import asyncio
from sentence_transformers import SentenceTransformer
import numpy as np

async def main():
    embedder = SentenceTransformer("all-MiniLM-L6-v2")
    
    knowledge_text = "tapioca mosaic leaves mottling dry"
    user_query = "I am growing cassava in my field. After about one to two months of growth, many plants started showing pale yellow and light-green patches on the leaves. The leaves look mottled and uneven in color. Some leaves are smaller than normal and slightly twisted. A few plants are not growing properly and appear stunted compared to healthy ones nearby. I also noticed a lot of tiny white insects sitting under the leaves, especially during warm days. The problem seems to be spreading slowly across the field. What disease could this be? How can I confirm it and what treatment (organic and chemical) should I apply?"
    
    extracted_features_query = "tapioca mosaic leaves mottling summer"
    extracted_features_bare = "tapioca leaves mottling summer"
    
    knowledge_emb = embedder.encode([knowledge_text])[0]
    user_emb = embedder.encode([user_query])[0]
    bare_emb = embedder.encode([extracted_features_bare])[0]
    
    hybrid_query_1 = f"{extracted_features_bare} {user_query}"
    hybrid_emb_1 = embedder.encode([hybrid_query_1])[0]
    
    hybrid_query_2 = f"Crop: tapioca. Symptoms: {extracted_features_bare}. Description: {user_query}"
    hybrid_emb_2 = embedder.encode([hybrid_query_2])[0]
    
    dist_user = np.sum((knowledge_emb - user_emb) ** 2)
    dist_bare = np.sum((knowledge_emb - bare_emb) ** 2)
    dist_hybrid_1 = np.sum((knowledge_emb - hybrid_emb_1) ** 2)
    dist_hybrid_2 = np.sum((knowledge_emb - hybrid_emb_2) ** 2)
    
    print(f"L2 Distance (knowledge vs full user query): {dist_user}")
    print(f"L2 Distance (knowledge vs bare extracted features): {dist_bare}")
    print(f"L2 Distance (knowledge vs hybrid 1 (bare + raw)): {dist_hybrid_1}")
    print(f"L2 Distance (knowledge vs hybrid 2 (structured)): {dist_hybrid_2}")

if __name__ == "__main__":
    asyncio.run(main())
