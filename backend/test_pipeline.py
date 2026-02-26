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
        
        # Mock message history
        conversation_messages = []
        
        # The user's query
        query_text = "I am growing cassava in my field. After about one to two months of growth, many plants started showing pale yellow and light-green patches on the leaves. The leaves look mottled and uneven in color. Some leaves are smaller than normal and slightly twisted. A few plants are not growing properly and appear stunted compared to healthy ones nearby. I also noticed a lot of tiny white insects sitting under the leaves, especially during warm days. The problem seems to be spreading slowly across the field. What disease could this be? How can I confirm it and what treatment (organic and chemical) should I apply?"
        
        # 1. Simulate disease_engine logic
        features = diagnostic_engine.extract_features(query_text.lower())
        print(f"Extracted Features: {features}")
        
        hybrid_query = f"{features.get('crop', '')} {features.get('position', '')} {features.get('pattern', '')} {features.get('weather', '')} {query_text}".strip()
        print(f"Hybrid Query: {hybrid_query}")
        
        rag_match = await rag_service.identify_disease(hybrid_query)
        
        if rag_match:
            print(f"✅ FOUND MATCH: {rag_match['disease_name']}")
        else:
            print("❌ NO MATCH FOUND within threshold")

if __name__ == "__main__":
    asyncio.run(main())
