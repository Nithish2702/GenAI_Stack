"""
Vector Service Module - Pinecone Implementation

This module handles all vector database operations using Pinecone for semantic search.
It manages document embeddings, storage, and similarity-based retrieval.

Key Features:
- Document embedding generation using Google Gemini
- Vector storage in Pinecone (cloud-based, persistent)
- Semantic similarity search
- Metadata filtering
- Automatic index management

Usage:
    vector_service = VectorService()
    await vector_service.add_document_chunks(doc_id, chunks, metadata)
    results = await vector_service.search_similar(query, n_results=5)
"""

import pinecone
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.core.config import settings as app_settings
import time

class VectorService:
    def __init__(self):
        """Initialize Pinecone client and index"""
        if not app_settings.PINECONE_API_KEY:
            raise ValueError("PINECONE_API_KEY is required. Get free API key at https://www.pinecone.io")
        
        if not app_settings.GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY is required")
        
        # Initialize Pinecone (v2 API)
        import pinecone
        pinecone.init(api_key=app_settings.PINECONE_API_KEY, environment="us-east-1-aws")
        self.index_name = "genai-stack"
        
        # Create index if it doesn't exist
        self._ensure_index_exists()
        
        # Connect to index
        self.index = pinecone.Index(self.index_name)
        
        # Initialize Google Gemini
        genai.configure(api_key=app_settings.GOOGLE_API_KEY)
        
        print(f"✅ Pinecone VectorService initialized with index: {self.index_name}")

    def _ensure_index_exists(self):
        """Create Pinecone index if it doesn't exist"""
        try:
            import pinecone
            existing_indexes = pinecone.list_indexes()
            
            if self.index_name not in existing_indexes:
                print(f"⚠️  Index {self.index_name} doesn't exist. Please create it manually in Pinecone dashboard as a serverless index.")
                print(f"   Go to: https://app.pinecone.io/")
                print(f"   Create index with name: {self.index_name}, dimension: 768, metric: cosine")
            else:
                print(f"✅ Using existing index: {self.index_name}")
                
        except Exception as e:
            print(f"⚠️  Error checking index: {e}")
            print(f"   Assuming index exists and continuing...")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings using Google Gemini"""
        try:
            print(f"Creating embeddings for {len(texts)} texts using Google Gemini...")
            embeddings = []
            for text in texts:
                result = genai.embed_content(
                    model="models/embedding-001",
                    content=text,
                    task_type="retrieval_document"
                )
                embeddings.append(result['embedding'])
            print("✅ Google Gemini embeddings successful")
            return embeddings
        except Exception as e:
            print(f"❌ Google Gemini embeddings failed: {e}")
            raise Exception(f"Embedding generation failed: {str(e)}")

    async def add_document_chunks(
        self, 
        document_id: int, 
        chunks: List[str], 
        metadata: Dict[str, Any] = None
    ) -> int:
        """Add document chunks to Pinecone vector store"""
        if not chunks:
            return 0

        # First, delete any existing chunks for this document
        print(f"Cleaning up existing chunks for document {document_id}...")
        self.delete_document(document_id)

        # Create embeddings
        print(f"Creating embeddings for {len(chunks)} chunks...")
        embeddings = await self.create_embeddings(chunks)
        
        # Prepare vectors for Pinecone
        vectors = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            vector_id = f"doc_{document_id}_chunk_{i}"
            
            # Prepare metadata
            chunk_metadata = {
                "document_id": str(document_id),  # Pinecone requires string values
                "chunk_index": i,
                "text": chunk[:1000],  # Store first 1000 chars in metadata
                "text_length": len(chunk)
            }
            if metadata:
                # Convert all metadata values to strings for Pinecone
                for key, value in metadata.items():
                    chunk_metadata[key] = str(value)
            
            vectors.append({
                "id": vector_id,
                "values": embedding,
                "metadata": chunk_metadata
            })

        # Upsert to Pinecone in batches (Pinecone recommends batch size of 100)
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            print(f"Upserted batch {i//batch_size + 1}/{(len(vectors)-1)//batch_size + 1}")
        
        print(f"✅ Successfully added {len(chunks)} chunks for document {document_id}")
        return len(chunks)

    async def search_similar(
        self, 
        query: str, 
        n_results: int = 5,
        document_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Search for similar chunks in Pinecone"""
        try:
            # Create query embedding
            query_embeddings = await self.create_embeddings([query])
            query_embedding = query_embeddings[0]
            
            # Prepare filter for specific document
            filter_dict = None
            if document_id:
                filter_dict = {"document_id": {"$eq": str(document_id)}}
            
            # Search in Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=n_results,
                include_metadata=True,
                filter=filter_dict
            )
            
            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    "text": match['metadata'].get('text', ''),
                    "metadata": {
                        "document_id": int(match['metadata'].get('document_id', 0)),
                        "chunk_index": match['metadata'].get('chunk_index', 0),
                        "text_length": match['metadata'].get('text_length', 0)
                    },
                    "score": match['score'],  # Pinecone returns similarity score
                    "distance": 1 - match['score']  # Convert to distance for compatibility
                })
            
            print(f"✅ Found {len(formatted_results)} similar chunks")
            return formatted_results
            
        except Exception as e:
            print(f"❌ Search failed: {e}")
            return []

    def delete_document(self, document_id: int):
        """Delete all chunks for a document from Pinecone"""
        try:
            # Pinecone delete by filter
            self.index.delete(filter={"document_id": {"$eq": str(document_id)}})
            print(f"✅ Deleted all chunks for document {document_id}")
        except Exception as e:
            print(f"⚠️  Error deleting document chunks: {str(e)}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get Pinecone index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                "total_vectors": stats.get('total_vector_count', 0),
                "index_name": self.index_name,
                "dimension": 768,
                "metric": "cosine"
            }
        except Exception as e:
            return {"error": str(e)}
