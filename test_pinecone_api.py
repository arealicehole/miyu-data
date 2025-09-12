#!/usr/bin/env python3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('PINECONE_API_KEY')
print(f"Testing API key: {api_key[:10]}...{api_key[-10:]}")

# Test with direct API call
headers = {
    'Api-Key': api_key,
    'X-Pinecone-API-Version': '2024-07'
}

# Try listing indexes
response = requests.get('https://api.pinecone.io/indexes', headers=headers)
print(f"\nList indexes response: {response.status_code}")
if response.status_code == 200:
    print("Success! Indexes:", response.json())
else:
    print("Error:", response.text)

# Try the specific index endpoint
index_host = 'https://miyu-testa-6875460.svc.aped-4627-b74a.pinecone.io'
stats_response = requests.get(f'{index_host}/describe_index_stats', headers={'Api-Key': api_key})
print(f"\nIndex stats response: {stats_response.status_code}")
if stats_response.status_code == 200:
    print("Index stats:", stats_response.json())
else:
    print("Error:", stats_response.text)