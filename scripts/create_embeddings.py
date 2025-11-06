"""
Create Embeddings Script
Generates vector embeddings and creates FAISS index
"""

import pickle
from pathlib import Path
from typing import List

import yaml
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS


def load_params():
    """Load parameters from params.yaml"""
    with open("params.yaml", 'r') as f:
        params = yaml.safe_load(f)
    return params


def load_processed_data(input_path: Path) -> List[str]:
    """Load processed document chunks"""
    with open(input_path, 'rb') as f:
        chunks = pickle.load(f)
    
    print(f"Loaded {len(chunks)} chunks")
    return chunks


def create_embeddings(chunks: List[str], params: dict) -> FAISS:
    """Create embeddings and FAISS vector store"""
    
    # Get parameters
    model_name = params['embeddings']['model_name']
    
    print(f"Creating embeddings using {model_name}...")
    
    # Initialize embedding model
    embeddings = HuggingFaceEmbeddings(model_name=model_name)
    
    # Create FAISS vector store
    vectorstore = FAISS.from_texts(chunks, embedding=embeddings)
    
    print("Embeddings created successfully!")
    
    return vectorstore


def save_vectorstore(vectorstore: FAISS, output_path: Path):
    """Save FAISS vector store to disk"""
    output_path.mkdir(parents=True, exist_ok=True)
    
    vectorstore.save_local(str(output_path))
    
    print(f"Vector store saved to {output_path}")


def main():
    print("Starting embeddings creation...")
    
    # Load parameters
    params = load_params()
    
    # Define paths
    input_path = Path("data/processed/documents.pkl")
    output_path = Path("index_faiss")
    
    # Load processed data
    chunks = load_processed_data(input_path)
    
    # Create embeddings
    vectorstore = create_embeddings(chunks, params)
    
    # Save vector store
    save_vectorstore(vectorstore, output_path)
    
    print("Embeddings creation complete!")


if __name__ == "__main__":
    main()
