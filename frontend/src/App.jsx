import React from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import StacksList from './pages/StacksList'
import StackBuilder from './pages/StackBuilder'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Navigate to="/stacks" replace />} />
        <Route path="/stacks" element={<StacksList />} />
        <Route path="/stacks/:id" element={<StackBuilder />} />
        <Route path="/stacks/new" element={<StackBuilder />} />
      </Routes>
    </Router>
  )
}

export default App
