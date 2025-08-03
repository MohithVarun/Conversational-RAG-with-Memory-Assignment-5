# 🏗️ Healthcare RAG Chatbot Architecture

## System Architecture Overview

The Healthcare RAG Chatbot is built on a modular architecture that combines retrieval-augmented generation with advanced memory management and knowledge processing.

```
┌─────────────────────────────────────────────────────────────────┐
│                        Streamlit UI (app.py)                     │
└───────────────────────────────┬─────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                 Advanced RAG System (advanced_rag_system.py)     │
│                                                                 │
│  ┌─────────────────────┐           ┌──────────────────────────┐ │
│  │   Memory Manager    │◄─────────►│      Knowledge Base      │ │
│  │(advanced_memory_    │           │  (advanced_knowledge_    │ │
│  │     manager.py)     │           │        base.py)          │ │
│  └─────────────────────┘           └──────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────┐           ┌──────────────────────────┐ │
│  │  Response Generator │◄─────────►│    Evaluation System     │ │
│  │   (OpenAI API)      │           │  (evaluation_system.py)  │ │
│  └─────────────────────┘           └──────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. User Interface (app.py)

The Streamlit-based user interface handles:
- User input collection
- Message display and formatting
- Session management
- Analytics and metrics display
- Dynamic response rendering

### 2. Advanced RAG System (advanced_rag_system.py)

The central orchestration layer that:
- Coordinates between memory and knowledge components
- Manages the response generation pipeline
- Handles context building and processing
- Implements different response styles based on context
- Manages API interactions with OpenAI

### 3. Memory Manager (advanced_memory_manager.py)

Responsible for:
- Multi-session memory storage and retrieval
- Long-term memory persistence
- User profile management
- Memory relevance scoring
- Context window management

### 4. Knowledge Base (advanced_knowledge_base.py)

Handles:
- Document storage and processing
- Text chunking strategies
- Embedding generation and storage
- Semantic search functionality
- Relevance scoring for knowledge retrieval

### 5. Evaluation System (evaluation_system.py)

Provides:
- RAGAS-like evaluation metrics
- Performance monitoring
- Response quality assessment
- System diagnostics

## Data Flow

1. **User Input** → The user submits a query through the Streamlit interface
2. **Context Building** → The system retrieves relevant memories and knowledge
3. **Response Generation** → The RAG system generates a contextual response
4. **Memory Storage** → The interaction is stored in the memory system
5. **Response Delivery** → The formatted response is displayed to the user

## Technical Implementation Details

### Embedding Models

The system uses two embedding approaches:
- Primary: OpenAI embeddings (when API key is available)
- Fallback: Sentence Transformers (local embedding generation)

### Vector Storage

- ChromaDB integration for vector storage and retrieval
- Custom similarity search implementation
- Metadata-enhanced retrieval

### Memory Persistence

- Pickle-based storage for memory persistence
- Session-based organization
- Long-term and short-term memory separation

### Response Generation

Multiple response styles implemented:
- Urgent responses for critical health issues
- Friendly responses for general queries
- Detailed responses for in-depth medical questions
- Professional responses for technical medical inquiries

## Deployment Architecture

The application is designed for deployment on:
- Streamlit Cloud (primary recommended platform)
- Hugging Face Spaces
- Custom server deployments

## Security Considerations

- API keys stored as environment variables
- No sensitive data stored in the repository
- Memory persistence with privacy controls
- User data handling with consideration for medical privacy

## Performance Optimization

- Caching for frequently accessed data
- Efficient context window management
- Optimized embedding generation
- Response time monitoring and optimization

---

This architecture provides a comprehensive framework for a healthcare-focused RAG system with advanced memory capabilities, ensuring contextual, personalized responses across multiple user sessions.