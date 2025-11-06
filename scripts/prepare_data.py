"""
Data Preparation Script
Processes raw documentation and prepares it for embedding
"""

import pickle
from pathlib import Path
from typing import List

import yaml
from langchain_community.document_loaders import PyMuPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter


def load_params():
    """Load parameters from params.yaml"""
    with open("params.yaml", 'r') as f:
        params = yaml.safe_load(f)
    return params


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF file"""
    loader = PyMuPDFLoader(file_path)
    pages = loader.load()
    content = "\n".join([page.page_content for page in pages])
    return content


def process_documents(data_path: Path, params: dict) -> List[str]:
    """Process all documents in the data directory"""
    
    # Get parameters
    chunk_size = params['prepare']['chunk_size']
    chunk_overlap = params['prepare']['chunk_overlap']
    
    # Initialize text splitter
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    
    # Find all PDF files
    pdf_files = list(data_path.glob("*.pdf"))
    
    print(f"Found {len(pdf_files)} PDF files")
    
    # Process each file
    all_chunks = []
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}...")
        
        # Extract text
        text = extract_text_from_pdf(str(pdf_file))
        
        # Split into chunks
        chunks = text_splitter.split_text(text)
        all_chunks.extend(chunks)
        
        print(f"  Created {len(chunks)} chunks")
    
    print(f"\nTotal chunks created: {len(all_chunks)}")
    
    return all_chunks


def save_processed_data(chunks: List[str], output_path: Path):
    """Save processed chunks to file"""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'wb') as f:
        pickle.dump(chunks, f)
    
    print(f"Saved processed data to {output_path}")


def main():
    print("Starting data preparation...")
    
    # Load parameters
    params = load_params()
    
    # Define paths
    data_path = Path("data/raw")
    output_path = Path("data/processed/documents.pkl")
    
    # Process documents
    chunks = process_documents(data_path, params)
    
    # Save processed data
    save_processed_data(chunks, output_path)
    
    print("Data preparation complete!")


if __name__ == "__main__":
    main()
