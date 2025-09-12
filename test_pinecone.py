#!/usr/bin/env python3
"""
Test Pinecone connection
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

api_key = os.getenv('PINECONE_API_KEY')
print(f"API Key length: {len(api_key) if api_key else 0}")

try:
    # Initialize Pinecone
    pc = Pinecone(api_key=api_key)
    
    # List indexes
    print("\nListing indexes...")
    indexes = pc.list_indexes()
    for idx in indexes:
        print(f"  - {idx.name} (host: {idx.host})")
    
    # Connect to specific index
    print("\nConnecting to miyu-testa...")
    index = pc.Index(
        name='miyu-testa',
        host='https://miyu-testa-6875460.svc.aped-4627-b74a.pinecone.io'
    )
    
    # Test query
    print("Testing query...")
    result = index.query(
        vector=[0.1] * 3072,
        top_k=1,
        include_metadata=True
    )
    print(f"Query successful! Returned {len(result.matches)} matches")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()