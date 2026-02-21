import asyncio
import os
import sys
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")

# Add backend to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "backend")))

from app.rag_service import RAGService

async def test_rag():
    print("Starting RAG Verification...")
    rag = RAGService()
    await rag.initialize()
    
    questions = [
        "How to control aphids in mustard crop?",
        "Yellow leaves on coconut tree in Kerala",
        "What is the solution for Sigatoka Leaf Spot in banana?"
    ]
    
    for q in questions:
        print(f"\nQuestion: {q}")
        answer = await rag.generate_answer(q)
        print(f"Answer:\n{answer}")
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_rag())
