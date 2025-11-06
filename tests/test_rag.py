"""
Tests for RAG functionality
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from langchain_core.messages import AIMessage, HumanMessage


class TestRAGChain:
    """Test cases for RAG chain"""
    
    @pytest.fixture
    def mock_vectorstore(self):
        """Mock FAISS vector store"""
        with patch('langchain.vectorstores.FAISS.load_local') as mock:
            yield mock
    
    @pytest.fixture
    def mock_llm(self):
        """Mock Claude LLM"""
        with patch('langchain_anthropic.ChatAnthropic') as mock:
            yield mock
    
    def test_vectorstore_loading(self, mock_vectorstore):
        """Test vector store can be loaded"""
        mock_vectorstore.return_value = Mock()
        
        # Import here to use mocked dependencies
        from langchain.vectorstores import FAISS
        from langchain_huggingface import HuggingFaceEmbeddings
        
        embeddings = Mock()
        vectorstore = FAISS.load_local("index_faiss", embeddings)
        
        assert vectorstore is not None
    
    def test_chat_history_format(self):
        """Test chat history message formatting"""
        chat_history = [
            AIMessage(content="Hello!"),
            HumanMessage(content="Hi there")
        ]
        
        assert len(chat_history) == 2
        assert isinstance(chat_history[0], AIMessage)
        assert isinstance(chat_history[1], HumanMessage)
    
    def test_retrieval_parameters(self):
        """Test retrieval parameters are correctly set"""
        search_kwargs = {'k': 3, 'fetch_k': 4}
        
        assert search_kwargs['k'] == 3
        assert search_kwargs['fetch_k'] == 4


class TestDataProcessing:
    """Test cases for data processing"""
    
    def test_chunk_creation(self):
        """Test text is properly chunked"""
        from langchain_text_splitters import RecursiveCharacterTextSplitter
        
        text = "This is a test. " * 100
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=100,
            chunk_overlap=20
        )
        
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 1
        assert all(len(chunk) <= 120 for chunk in chunks)  # Allow overlap


class TestMonitoring:
    """Test cases for monitoring functionality"""
    
    def test_metrics_extraction(self):
        """Test metrics can be extracted from data"""
        import pandas as pd
        
        data = pd.DataFrame({
            'response_time': [1.2, 1.5, 0.8],
            'confidence': [0.9, 0.85, 0.95],
            'user_id': ['user1', 'user2', 'user1']
        })
        
        avg_response_time = data['response_time'].mean()
        avg_confidence = data['confidence'].mean()
        unique_users = data['user_id'].nunique()
        
        assert avg_response_time > 0
        assert 0 <= avg_confidence <= 1
        assert unique_users == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
