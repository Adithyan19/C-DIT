import asyncio
import uuid
import datetime
from app.database import AsyncSessionLocal
from app.rag_service import RAGService
from app.disease_engine import diagnostic_engine, analyze_message
from app.models import Message, MessageSender, ContentType

async def test_chat(query_text):
    rag_service = RAGService()
    await rag_service.initialize()
    
    async with AsyncSessionLocal() as db:
        await rag_service.rebuild_index(db)
        
        class MockApp:
            state = type('obj', (object,), {'rag_service': rag_service})
        class MockRequest:
            app = MockApp()
        request = MockRequest()
        
        print(f"\n--- USER: {query_text} ---")
        response = await analyze_message(
            db=db,
            text=query_text,
            image_url=None,
            conversation_messages=[],
            request=request
        )
        print(f"BOT: {response['response_text']}")

async def main():
    await test_chat("Hello, good morning!")
    await test_chat("Thank you for your help yesterday.")
    await test_chat("How does the weather affect my crops?")

if __name__ == "__main__":
    asyncio.run(main())
