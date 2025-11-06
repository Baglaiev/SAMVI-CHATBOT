"""
IT Support Chatbot Application
Healthcare IT Support Chatbot using Claude API and RAG
"""

import os
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage, HumanMessage
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="IT Support 🏥",
    page_icon="🏥",
    layout="wide"
)

# Title and branding
st.title("🏥 Healthcare IT Support Chatbot")
st.markdown("*Powered by Claude AI*")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    
    # API Key input (if not in environment)
    if not os.getenv("ANTHROPIC_API_KEY"):
        api_key = st.text_input("Anthropic API Key", type="password")
        if api_key:
            os.environ["ANTHROPIC_API_KEY"] = api_key
    
    # Model parameters
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, 0.1)
    max_tokens = st.slider("Max Tokens", 1024, 8192, 4096, 512)
    
    # Retrieval parameters
    st.subheader("Retrieval Settings")
    search_k = st.slider("Number of documents to retrieve", 1, 10, 3)
    
    st.divider()
    st.caption("Version 1.0.0")


@st.cache_resource
def initialize_rag_chain(temperature, max_tokens, search_k):
    """Initialize the RAG chain with given parameters"""
    
    # Initialize Claude LLM
    llm = ChatAnthropic(
        model="claude-sonnet-4-20250514",
        temperature=temperature,
        max_tokens=max_tokens,
        timeout=None,
        max_retries=2
    )
    
    # Load embeddings and vector store
    embedding_model = "BAAI/bge-large-en-v1.5"
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model)
    
    # Load FAISS index
    vectorstore = FAISS.load_local(
        "index_faiss", 
        embeddings, 
        allow_dangerous_deserialization=True
    )
    
    # Create retriever
    retriever = vectorstore.as_retriever(
        search_type='mmr',
        search_kwargs={'k': search_k, 'fetch_k': search_k + 1}
    )
    
    # Contextualization prompt
    context_q_system_prompt = """Given the following chat history and the follow-up question
    which might reference context in the chat history, formulate a standalone question which
    can be understood without the chat history. Do NOT answer the question, just reformulate
    it if needed and otherwise return it as is."""
    
    context_q_prompt = ChatPromptTemplate.from_messages([
        ("system", context_q_system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "Question: {input}"),
    ])
    
    # History-aware retriever
    history_aware_retriever = create_history_aware_retriever(
        llm=llm,
        retriever=retriever,
        prompt=context_q_prompt
    )
    
    # Q&A system prompt
    system_prompt = """You are a helpful IT Support virtual assistant for a healthcare organization.
    You provide accurate, concise answers to IT support questions.
    
    Use the following context to answer questions:
    - If the answer is in the context, provide a clear and helpful response
    - If you don't know the answer, say so honestly and suggest contacting IT support directly
    - Keep your answers professional, concise, and actionable
    - For healthcare IT systems, prioritize security and compliance in your guidance
    
    Context: {context}
    """
    
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder("chat_history"),
        ("human", "Question: {input}"),
    ])
    
    # Q&A chain
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    
    # Final RAG chain
    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        qa_chain,
    )
    
    return rag_chain


# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hi! I'm your IT Support assistant. How can I help you today?")
    ]

if "rag_chain" not in st.session_state:
    if os.getenv("ANTHROPIC_API_KEY"):
        with st.spinner("Initializing chatbot..."):
            st.session_state.rag_chain = initialize_rag_chain(
                temperature, max_tokens, search_k
            )

# Display chat history
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)

# Chat input
if prompt := st.chat_input("Ask your IT support question..."):
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.error("Please provide your Anthropic API Key in the sidebar.")
        st.stop()
    
    # Display user message
    with st.chat_message("user"):
        st.write(prompt)
    
    # Add to chat history
    st.session_state.chat_history.append(HumanMessage(content=prompt))
    
    # Get response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.rag_chain.invoke({
                "input": prompt,
                "chat_history": st.session_state.chat_history
            })
            
            answer = response["answer"]
            st.write(answer)
    
    # Add assistant response to chat history
    st.session_state.chat_history.append(AIMessage(content=answer))

# Clear chat button
if st.sidebar.button("Clear Chat History"):
    st.session_state.chat_history = [
        AIMessage(content="Hi! I'm your IT Support assistant. How can I help you today?")
    ]
    st.rerun()
