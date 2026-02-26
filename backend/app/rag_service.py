import logging
import os
import pickle
import asyncio

logger = logging.getLogger(__name__)


class RAGService:
    def __init__(self):
        self.model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
        self.embedder_name = "all-MiniLM-L6-v2"

        self.tokenizer = None
        self.model = None
        self.embedder = None
        self.index = None
        self.documents = []

        self.is_initialized = False
        self.is_loading = False

    async def initialize(self):
        """Initialize embedder. FAISS index will be built later from DB data."""
        if self.is_initialized or self.is_loading:
            return

        try:
            self.is_loading = True
            from sentence_transformers import SentenceTransformer
            
            logger.info("Starting RAG Service initialization...")
            # Load embedder first (memory-light)
            logger.info(f"Loading embedder: {self.embedder_name}")
            self.embedder = await asyncio.to_thread(SentenceTransformer, self.embedder_name)
            logger.info("Embedder loaded")
            
            self.is_initialized = True
            logger.info("RAG Service initialized (waiting for knowledge load)")
        except Exception as e:
            logger.error(f"Error during RAG initialization: {e}", exc_info=True)
        finally:
            self.is_loading = False

    async def build_index_from_knowledge(self, knowledge_list: list):
        """Build FAISS index from local database knowledge."""
        if not self.embedder:
            await self.initialize()
            
        import faiss
        import numpy as np
        import asyncio

        if not knowledge_list:
            logger.warning("No knowledge found to build index.")
            self.index = None # Ensure index is cleared if no knowledge
            self.documents = []
            return

        logger.info(f"Building RAG index from {len(knowledge_list)} local items...")
        
        self.documents = []
        texts_to_embed = []
        
        for item in knowledge_list:
            # Create a rich text representation for embedding
            # This helps the retriever find the right treatment
            context_text = (
                f"Crop: {item.crop}\n"
                f"Disease: {item.disease_name}\n"
                f"Symptoms: {item.symptom} at {item.position} with {item.pattern}\n"
                f"Weather: {item.weather}\n"
                f"Treatment: {item.treatment_summary}"
            )
            # Store metadata along with the rich text context
            self.documents.append({
                "context": context_text,
                "crop": item.crop,
                "disease_name": item.disease_name,
                "symptom": item.symptom,
                "position": item.position,
                "pattern": item.pattern,
                "weather": item.weather,
                "treatment_summary": item.treatment_summary
            })
            # Embed the disease and symptoms for retrieval
            # Focusing heavily on symptoms, position, pattern and weather for identification
            texts_to_embed.append(f"{item.crop} {item.symptom} {item.position} {item.pattern} {item.weather}")

        # Build index in batches
        batch_size = 128
        embeddings = []
        for i in range(0, len(texts_to_embed), batch_size):
            batch = texts_to_embed[i:i + batch_size]
            batch_embeddings = await asyncio.to_thread(self.embedder.encode, batch)
            embeddings.append(batch_embeddings)

        embeddings = np.vstack(embeddings)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings.astype('float32'))
        
        logger.info("Local knowledge base index built successfully")
        logger.info(f"FAISS index created with {self.index.ntotal} documents")

    async def rebuild_index(self, db_session):
        """Rebuild the index by fetching all knowledge from the database."""
        from sqlalchemy import select
        from app.models import DiseaseKnowledge
        result = await db_session.execute(select(DiseaseKnowledge))
        knowledge_list = result.scalars().all()
        await self.build_index_from_knowledge(knowledge_list)

    async def identify_disease(self, query_text: str, threshold: float = 1.25):
        """Identify a disease from a symptom description using FAISS."""
        if not self.index or not self.embedder:
            return None
            
        import numpy as np
        import asyncio
        
        # Embed the farmer's query
        query_embedding = await asyncio.to_thread(self.embedder.encode, [query_text])
        
        # Search for the top 1 match
        distances, indices = await asyncio.to_thread(
            self.index.search, np.array(query_embedding).astype('float32'), 1
        )
        
        if len(distances) > 0 and len(distances[0]) > 0:
            distance = distances[0][0]
            index = indices[0][0]
            
            logger.info(f"RAG Identify FAISS Distance: {distance} (Threshold: {threshold})")
            
            # Lower distance means better match in L2 space
            if distance < threshold and index < len(self.documents):
                return self.documents[index]
                
        return None

    async def load_model(self):
        """Lazy-load LLM only when needed."""
        if self.model is not None and self.tokenizer is not None:
            return

        import torch
        from transformers import AutoTokenizer, AutoModelForCausalLM

        logger.info(f"Loading LLM: {self.model_name}")
        self.tokenizer = await asyncio.to_thread(AutoTokenizer.from_pretrained, self.model_name)
        self.model = await asyncio.to_thread(
            AutoModelForCausalLM.from_pretrained,
            self.model_name,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="auto",
            low_cpu_mem_usage=True
        )
        self.model.eval()
        logger.info("TinyLlama model loaded")

    def retrieve_context(self, query, top_k=5):
        """Retrieve relevant context for a query."""
        if not self.index or not self.embedder:
            return ""

        import numpy as np
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(np.array(query_embedding).astype('float32'), top_k)
        
        retrieved_docs = []
        for i in indices[0]:
            if i < len(self.documents):
                retrieved_docs.append(self.documents[i]["context"])
                
        return "\n\n".join(retrieved_docs)

    async def generate_answer(self, disease_name: str, crop_name: str, top_k=5):
        """Generate a detailed treatment explanation for a diagnosed disease."""
        if not self.is_initialized:
            return "Treatment service is not initialized."

        import torch

        query = f"How to treat {disease_name} in {crop_name} crops?"
        
        # CPU Fallback - Too slow to run full LLM, just format the context nicely
        if not torch.cuda.is_available():
            logger.info("CPU detected. Skipping LLM generation for speed and returning formatted context.")
            # For direct output (no LLM synthesis), just get the 1 most relevant document
            best_context = await asyncio.to_thread(self.retrieve_context, query, top_k=1)
            return f"{best_context}\n\n*(Note: Detailed AI explanation skipped because no GPU is available on this server to synthesize the answer quickly.)*"

        context = await asyncio.to_thread(self.retrieve_context, query, top_k=top_k)

        await self.load_model()  # lazy-load model

        prompt = f"""<|system|>
You are an expert plant pathologist. Your task is to provide a detailed, scientific treatment guide for a SPECIFIC disease.
Do not diagnose. The diagnosis has already been confirmed as: {disease_name} in {crop_name}.
Use the provided scientific context to explain:
1. Chemical control (if applicable and safe according to context).
2. Organic/Cultural management (Bordeaux mixture, fertilization, drainage).
3. Preventive measures to stop the spread.

Context:
{context}</s>
<|user|>
Explain the treatment for {disease_name} in {crop_name}.</s>
<|assistant|>
Treatment Guide:"""

        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        outputs = await asyncio.to_thread(
            self.model.generate,
            **inputs,
            max_new_tokens=300,
            temperature=0.7,
            do_sample=True,
            pad_token_id=self.tokenizer.eos_token_id
        )

        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's answer
        if "Treatment Guide:" in response:
            answer = response.split("Treatment Guide:")[-1].strip()
        elif "Expert Answer:" in response:
             answer = response.split("Expert Answer:")[-1].strip()
        else:
            answer = response.strip()

        return answer