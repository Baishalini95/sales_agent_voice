from rag_engine import RAGEngine

# Test the RAG engine
rag = RAGEngine()

# Test queries
test_queries = [
    "how to authorize Managing Electronic Service Agent",
    "Managing Electronic Service Agent",
    "electronic service agent",
    "service account",
    "email configuration"
]

print("Testing RAG Engine:")
print("=" * 50)

for query in test_queries:
    print(f"\nQuery: {query}")
    print("-" * 30)
    response = rag.generate_response(query)
    print(f"Response: {response}")
    print("=" * 50)