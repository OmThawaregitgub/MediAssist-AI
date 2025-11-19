# rag.py - UPDATED FOR STREAMLIT CLOUD
import chromadb
from llm import GeminiLLM

class RAGPipeline:
    def __init__(self, collection_name="medical_rag"):
        # Use in-memory client for Streamlit Cloud
        self.client = chromadb.Client()
        
        # Let ChromaDB handle embeddings automatically
        self.collection = self.client.get_or_create_collection(
            name=collection_name
        )

        self.llm = GeminiLLM()
        
        # Initialize with sample medical data
        self._initialize_sample_data()

    def _initialize_sample_data(self):
        """Add sample medical data for demonstration"""
        sample_docs = [
            {
                "id": "doc1",
                "text": "Intermittent fasting (IF) involves cycling between periods of eating and fasting. Common methods include 16:8 (16 hours fasting, 8 hours eating) and 5:2 (5 days normal eating, 2 days restricted calories). Studies show benefits for weight loss and metabolic health.",
                "metadata": {"source": "medical_guide", "topic": "definition"}
            },
            {
                "id": "doc2", 
                "text": "Research indicates intermittent fasting can improve insulin sensitivity and aid weight loss. Participants in clinical trials showed 3-8% body weight reduction over 8-12 weeks with improved metabolic markers including blood sugar control.",
                "metadata": {"source": "clinical_study", "topic": "benefits"}
            },
            {
                "id": "doc3",
                "text": "Intermittent fasting may benefit Type 2 diabetes patients by improving glycemic control. However, patients on insulin or sulfonylureas should be closely monitored for hypoglycemia risks during fasting periods. Medical supervision is recommended.",
                "metadata": {"source": "diabetes_journal", "topic": "diabetes"}
            },
            {
                "id": "doc4",
                "text": "Breast cancer risk factors include age, family history, genetic mutations (BRCA1/BRCA2), hormonal factors, obesity, alcohol consumption, and radiation exposure. Regular screening through mammography is recommended for early detection.",
                "metadata": {"source": "oncology_guide", "topic": "cancer"}
            },
            {
                "id": "doc5",
                "text": "Common intermittent fasting protocols: 16:8 method (daily 16-hour fast), 5:2 diet (2 days of severe calorie restriction per week), alternate-day fasting, and eat-stop-eat (24-hour fasts 1-2 times per week). Each has different adherence rates and health outcomes.",
                "metadata": {"source": "nutrition_review", "topic": "methods"}
            }
        ]
        
        # Add documents - ChromaDB will handle embeddings automatically
        for doc in sample_docs:
            self.collection.add(
                ids=[doc["id"]],
                documents=[doc["text"]],
                metadatas=[doc["metadata"]]
            )

    def ask(self, query: str) -> str:
        try:
            # Use ChromaDB's automatic embedding generation
            results = self.collection.query(
                query_texts=[query],  # ChromaDB handles the embedding
                n_results=3
            )

            retrieved_docs = results["documents"][0] if results["documents"] else []

            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
                final_prompt = f"""
You are MediAssist AI, a medical research assistant. Use the context below to answer accurately.

Context:
{context}

Question: {query}

Provide a clear, evidence-based answer:
"""
                return self.llm.generate(final_prompt)
            else:
                # Fallback to general medical knowledge
                general_prompt = f"""
You are MediAssist AI, a helpful medical assistant. Answer this question based on your medical knowledge:

Question: {query}

Provide a helpful and accurate response:
"""
                return self.llm.generate(general_prompt)
                
        except Exception as e:
            return f"Error retrieving information: {str(e)}"
