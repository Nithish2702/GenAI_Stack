"""
Workflow Service Module

This module orchestrates the execution of user-defined workflows by coordinating
between different components (User Query, Knowledge Base, LLM Engine, Output).

Key Features:
- Workflow validation
- Component execution orchestration
- Topological sorting for execution order
- Chat session management
- Error handling and logging

Usage:
    workflow_service = WorkflowService()
    result = await workflow_service.execute_workflow(
        workflow_id=1,
        query="What is in the document?",
        session_id=None,
        db=db_session
    )
"""

import time
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.database.models import Workflow, ChatSession, ChatMessage, Document
from app.services.vector_service import VectorService
from app.services.llm_service import LLMService
from app.schemas.workflow import WorkflowCreate, WorkflowUpdate

class WorkflowService:
    def __init__(self):
        self.vector_service = VectorService()
        self.llm_service = LLMService()

    def create_workflow(self, workflow_data: WorkflowCreate, db: Session) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(
            name=workflow_data.name,
            description=workflow_data.description,
            components=[comp.dict() for comp in workflow_data.components],
            connections=[{
                'source_id': conn.source,
                'target_id': conn.target
            } for conn in workflow_data.connections]
        )
        
        db.add(workflow)
        db.commit()
        db.refresh(workflow)
        return workflow

    def get_workflow(self, workflow_id: int, db: Session) -> Optional[Workflow]:
        """Get workflow by ID"""
        return db.query(Workflow).filter(Workflow.id == workflow_id).first()

    def get_workflows(self, db: Session, skip: int = 0, limit: int = 100) -> List[Workflow]:
        """Get all workflows"""
        return db.query(Workflow).offset(skip).limit(limit).all()

    def update_workflow(self, workflow_id: int, workflow_data: WorkflowUpdate, db: Session) -> Optional[Workflow]:
        """Update workflow"""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return None

        update_data = workflow_data.dict(exclude_unset=True)
        
        # Convert components and connections to dict format if provided
        if 'components' in update_data and update_data['components']:
            update_data['components'] = [comp.dict() if hasattr(comp, 'dict') else comp for comp in update_data['components']]
        if 'connections' in update_data and update_data['connections']:
            update_data['connections'] = [{
                'source_id': conn.source if hasattr(conn, 'source') else conn.get('source'),
                'target_id': conn.target if hasattr(conn, 'target') else conn.get('target')
            } for conn in update_data['connections']]

        for field, value in update_data.items():
            setattr(workflow, field, value)

        db.commit()
        db.refresh(workflow)
        return workflow

    def delete_workflow(self, workflow_id: int, db: Session) -> bool:
        """Delete workflow and all associated chat sessions"""
        workflow = db.query(Workflow).filter(Workflow.id == workflow_id).first()
        if not workflow:
            return False

        # Delete all chat sessions and their messages for this workflow
        # This is done automatically by cascade delete if configured in the model
        # But we'll do it explicitly to be safe
        chat_sessions = db.query(ChatSession).filter(ChatSession.workflow_id == workflow_id).all()
        for session in chat_sessions:
            # Delete all messages in this session
            db.query(ChatMessage).filter(ChatMessage.session_id == session.id).delete()
            # Delete the session
            db.delete(session)
        
        # Now delete the workflow
        db.delete(workflow)
        db.commit()
        return True

    def validate_workflow(self, components: List[Dict], connections: List[Dict]) -> Dict[str, Any]:
        """Validate workflow structure"""
        errors = []
        warnings = []

        # Check for required components
        component_types = [comp.get('type') for comp in components]
        
        if 'user_query' not in component_types:
            errors.append("Workflow must have a User Query component")
        
        if 'output' not in component_types:
            errors.append("Workflow must have an Output component")

        if 'llm_engine' not in component_types:
            warnings.append("Workflow should have an LLM Engine component for processing")

        # Check connections
        component_ids = [comp.get('id') for comp in components]
        
        for connection in connections:
            source = connection.get('source_id') or connection.get('source')
            target = connection.get('target_id') or connection.get('target')
            
            if source not in component_ids:
                errors.append(f"Connection source '{source}' not found in components")
            
            if target not in component_ids:
                errors.append(f"Connection target '{target}' not found in components")

        # Check for disconnected components
        connected_components = set()
        for connection in connections:
            source = connection.get('source_id') or connection.get('source')
            target = connection.get('target_id') or connection.get('target')
            connected_components.add(source)
            connected_components.add(target)
        
        disconnected = set(component_ids) - connected_components
        if disconnected:
            warnings.append(f"Disconnected components: {list(disconnected)}")

        return {
            "is_valid": len(errors) == 0,
            "errors": errors,
            "warnings": warnings
        }

    async def execute_workflow(
        self, 
        workflow_id: int, 
        query: str, 
        session_id: Optional[int], 
        db: Session
    ) -> Dict[str, Any]:
        """Execute workflow with given query"""
        start_time = time.time()
        
        # Get workflow
        workflow = self.get_workflow(workflow_id, db)
        if not workflow:
            raise ValueError("Workflow not found")

        # Validate workflow
        validation = self.validate_workflow(workflow.components, workflow.connections)
        if not validation['is_valid']:
            raise ValueError(f"Invalid workflow: {validation['errors']}")

        # Create or get chat session
        if not session_id:
            session = ChatSession(workflow_id=workflow_id)
            db.add(session)
            db.commit()
            db.refresh(session)
            session_id = session.id
        else:
            session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
            if not session:
                raise ValueError("Chat session not found")

        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            message_type="user",
            content=query
        )
        db.add(user_message)
        db.commit()

        try:
            # Execute workflow logic
            result = await self._execute_workflow_logic(workflow, query, db)
            
            # Save assistant response
            assistant_message = ChatMessage(
                session_id=session_id,
                message_type="assistant",
                content=result['response'],
                message_metadata=result.get('metadata', {})
            )
            db.add(assistant_message)
            db.commit()

            execution_time = time.time() - start_time

            return {
                "response": result['response'],
                "session_id": session_id,
                "execution_time": execution_time,
                "metadata": result.get('metadata', {})
            }

        except Exception as e:
            # Save error message
            error_message = ChatMessage(
                session_id=session_id,
                message_type="assistant",
                content=f"Error: {str(e)}",
                message_metadata={"error": True}
            )
            db.add(error_message)
            db.commit()
            
            raise e

    async def _execute_workflow_logic(self, workflow: Workflow, query: str, db: Session) -> Dict[str, Any]:
        """Execute the actual workflow logic"""
        components = {comp['id']: comp for comp in workflow.components}
        connections = workflow.connections

        # Find execution order
        execution_order = self._get_execution_order(components, connections)
        
        # Execute components in order
        context = {"query": query}
        
        for component_id in execution_order:
            component = components[component_id]
            component_type = component['type']
            
            if component_type == 'user_query':
                # User query component just passes the query forward
                context['user_query'] = query
                
            elif component_type == 'knowledge_base':
                # Knowledge base component retrieves relevant context
                config = component.get('data', {})
                n_results = config.get('n_results', 3)
                pass_to_llm = config.get('pass_to_llm', True)
                
                if pass_to_llm:
                    # Get document IDs for this workflow
                    workflow_documents = db.query(Document).filter(
                        Document.workflow_id == workflow.id
                    ).all()
                    
                    if not workflow_documents:
                        context['knowledge_base_context'] = ""
                        context['sources'] = []
                    else:
                        # Search for relevant chunks only in this workflow's documents
                        all_relevant_chunks = []
                        
                        for doc in workflow_documents:
                            doc_chunks = await self.vector_service.search_similar(
                                query=query,
                                n_results=n_results,
                                document_id=doc.id
                            )
                            all_relevant_chunks.extend(doc_chunks)
                        
                        # Sort by score and take top n_results
                        all_relevant_chunks.sort(key=lambda x: x['score'], reverse=True)
                        relevant_chunks = all_relevant_chunks[:n_results]
                        
                        # Combine chunks into context
                        if relevant_chunks:
                            kb_context = "\n\n".join([chunk['text'] for chunk in relevant_chunks])
                            context['knowledge_base_context'] = kb_context
                            
                            # Extract unique sources
                            sources = []
                            for doc in workflow_documents:
                                if doc.original_filename not in sources:
                                    sources.append(doc.original_filename)
                            context['sources'] = sources
                
            elif component_type == 'llm_engine':
                # LLM Engine component generates the response
                config = component.get('data', {})
                
                model_provider = 'gemini'  # Always use Gemini
                model_name = config.get('model_name', 'gemini-pro')
                custom_prompt = config.get('custom_prompt')
                use_web_search = config.get('use_web_search', False)
                temperature = config.get('temperature', 0.7)
                
                # Generate response
                llm_response = await self.llm_service.generate_response(
                    query=context['query'],
                    context=context.get('knowledge_base_context'),
                    custom_prompt=custom_prompt,
                    model=model_provider,
                    model_name=model_name,
                    use_web_search=use_web_search,
                    temperature=temperature
                )
                
                context['llm_response'] = llm_response
                
            elif component_type == 'output':
                # Output component formats the final response
                config = component.get('data', {})
                show_sources = config.get('show_sources', True)
                
                if 'llm_response' in context:
                    final_response = context['llm_response']['response']
                    metadata = {
                        "model_info": {
                            "provider": context['llm_response'].get('provider'),
                            "model": context['llm_response'].get('model'),
                            "tokens_used": context['llm_response'].get('tokens_used')
                        }
                    }
                    
                    if show_sources and 'sources' in context:
                        metadata['sources'] = list(set(context['sources']))
                    
                    return {
                        "response": final_response,
                        "metadata": metadata,
                        "sources": metadata.get('sources', [])
                    }

        # Fallback response
        return {
            "response": "Workflow executed but no response generated",
            "metadata": {}
        }

    def _get_execution_order(self, components: Dict, connections: List[Dict]) -> List[str]:
        """Determine the execution order of components based on connections"""
        # Simple topological sort
        in_degree = {comp_id: 0 for comp_id in components.keys()}
        graph = {comp_id: [] for comp_id in components.keys()}
        
        # Build graph - handle both source/target and source_id/target_id
        for connection in connections:
            source = connection.get('source_id') or connection.get('source')
            target = connection.get('target_id') or connection.get('target')
            if source and target:
                graph[source].append(target)
                in_degree[target] += 1
        
        # Find starting nodes (no incoming edges)
        queue = [comp_id for comp_id, degree in in_degree.items() if degree == 0]
        result = []
        
        while queue:
            current = queue.pop(0)
            result.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        return result