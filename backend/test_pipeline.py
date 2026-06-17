import asyncio
from app.database import AsyncSessionLocal
from app.rag_service import RAGService
from app.disease_engine import diagnostic_engine, analyze_message
from app.models import Message, MessageSender, ContentType
import uuid
import datetime

async def main():
    rag_service = RAGService()
    await rag_service.initialize()
    
    async with AsyncSessionLocal() as db:
        await rag_service.rebuild_index(db)
        print("Index rebuilt with DB documents.")
        
        # The user's query
        query_text = "I’m growing bananas and something is wrong"
        
        # 1. Simulate disease_engine logic via full analyze_message
        msg = Message(id=uuid.uuid4(), conversation_id=uuid.uuid4(), sender=MessageSender.user, content_type=ContentType.text, text_content=query_text, created_at=datetime.datetime.utcnow())
        
        # Create a mock request to hold app.state.rag_service
        class MockApp:
            state = type('obj', (object,), {'rag_service': rag_service})
        class MockRequest:
            app = MockApp()
            
        request = MockRequest()
        
        response = await analyze_message(
            db=db,
            text=query_text,
            image_url=None,
            conversation_messages=[],
            request=request
        )
        
        print("--- FULL PIPELINE RESPONSE ---")
        print(f"Is Diagnosis: {response['is_diagnosis']}")
        print(f"Is Unknown: {response['is_unknown']}")
        print(f"Is Follow Up: {response['follow_up']}")
        print(f"Disease Name: {response['disease_name']}")
        print(f"Response Text: {response['response_text']}")

if __name__ == "__main__":
    asyncio.run(main())
