# rag.py
import chromadb
from llm import GeminiLLM
from pubmed_data import RECORDS

class RAGPipeline:
    def __init__(self, collection_name="medical_rag"):
        # Use in-memory client for Streamlit Cloud
        self.client = chromadb.EphemeralClient()
        
        # Let ChromaDB handle embeddings automatically
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "Cancer research database"}
        )

        self.llm = GeminiLLM()
        
        # Initialize with PubMed data
        self._initialize_pubmed_data()

    def _initialize_pubmed_data(self):
        """Add PubMed cancer research data to ChromaDB"""
        try:
            if self.collection.count() == 0:
                documents = []
                metadatas = []
                ids = []
                
                for record in RECORDS:
                    # Create document text from title and abstract
                    abstract_text = ""
                    if isinstance(record['abstract'], dict):
                        abstract_text = " ".join(record['abstract'].values())
                    elif isinstance(record['abstract'], str):
                        abstract_text = record['abstract']
                    
                    document_text = f"Title: {record['title']}\nAbstract: {abstract_text}"
                    
                    documents.append(document_text)
                    metadatas.append({
                        "pmid": record['pmid'],
                        "title": record['title'],
                        "journal": record['journal'], 
                        "authors": record['authors'],
                        "publication_date": record['publication_date'],
                        "source": "pubmed"
                    })
                    ids.append(f"pubmed_{record['pmid']}")
                
                # Add all documents at once
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    metadatas=metadatas
                )
        except Exception as e:
            print(f"Note: {e}")

    def ask(self, query: str) -> str:
        try:
            # Handle greetings directly
            query_lower = query.lower().strip()
            if query_lower in ['hi', 'hello', 'hey', 'hola', 'hi!', 'hello!']:
                return "Hello! 👋 I'm MediAssist AI, your medical research assistant. I specialize in cancer research and can help answer questions using our database of medical studies. What would you like to know about cancer types, treatments, or research?"
            
            # Check if user wants tabular format information
            if 'tabular' in query_lower or 'table' in query_lower or 'format' in query_lower:
                if 'cancer' in query_lower and 'type' in query_lower:
                    return self._generate_cancer_types_table()
            
            # Use ChromaDB's built-in embeddings
            results = self.collection.query(
                query_texts=[query],
                n_results=5  # Get more results for comprehensive questions
            )

            retrieved_docs = results["documents"][0] if results["documents"] else []
            retrieved_metadatas = results["metadatas"][0] if results["metadatas"] else []

            if retrieved_docs:
                context = "\n\n".join(retrieved_docs)
                
                # Create sources information
                sources_info = "\n\n📚 **Research Sources:**\n"
                for meta in retrieved_metadatas:
                    title = meta.get('title', 'Unknown')
                    journal = meta.get('journal', 'Unknown journal')
                    year = meta.get('publication_date', 'Unknown year')
                    sources_info += f"• {title} ({journal}, {year})\n"

                # Special prompt for comprehensive cancer information
                if 'all type' in query_lower and 'cancer' in query_lower:
                    final_prompt = f"""You are MediAssist AI, a comprehensive cancer research assistant. 

Based on the research context below AND your general medical knowledge, provide detailed information about major cancer types and their treatments in a structured tabular format.

RESEARCH CONTEXT:
{context}

QUESTION: {query}

Please provide a comprehensive table showing:
1. Cancer Type
2. Common Locations
3. Main Treatment Approaches
4. Recent Advances
5. Survival Rates (if available)

Format as a clear, readable table with proper headers. Include at least 10-15 major cancer types:"""
                else:
                    final_prompt = f"""You are MediAssist AI, a medical research assistant. 

Based on the following research context, provide a clear, evidence-based answer to the question.

RESEARCH CONTEXT:
{context}

QUESTION: {query}

Please provide a helpful, accurate answer based on the research above:"""

                answer = self.llm.generate(final_prompt)
                return answer + sources_info
            else:
                # No relevant documents found - use general knowledge for comprehensive requests
                if 'all type' in query_lower and 'cancer' in query_lower:
                    return self._generate_cancer_types_table()
                return self.llm.generate(f"Please answer this question about cancer research: {query}")
                
        except Exception as e:
            # Fallback response for comprehensive cancer queries
            if 'cancer' in query.lower() and 'type' in query.lower():
                return self._generate_cancer_types_table()
            return "I can help you with cancer research information. Please ask specific questions about cancer types, treatments, or recent studies."

    def _generate_cancer_types_table(self):
        """Generate a comprehensive table of cancer types and treatments"""
        table_prompt = """Create a comprehensive table of major cancer types with their treatments. Format it as a clear, readable table with these columns:
- Cancer Type
- Common Locations
- Main Treatment Approaches  
- Recent Advances
- 5-Year Survival Range

Include these cancer types at minimum:
1. Breast Cancer
2. Lung Cancer
3. Prostate Cancer
4. Colorectal Cancer
5. Skin Cancer (Melanoma)
6. Bladder Cancer
7. Non-Hodgkin Lymphoma
8. Kidney Cancer
9. Leukemia
10. Pancreatic Cancer
11. Thyroid Cancer
12. Liver Cancer
13. Ovarian Cancer
14. Brain Cancer
15. Stomach Cancer

Make the table well-organized and easy to read. Include brief descriptions of treatment approaches."""

        response = self.llm.generate(table_prompt)
        return response + "\n\n💡 *Note: This is general medical information. Always consult healthcare professionals for specific medical advice.*"

    def get_collection_info(self):
        """Check how many documents are in the collection"""
        try:
            count = self.collection.count()
            return f"Medical database loaded with {count} research articles"
        except Exception as e:
            return "Medical research database is ready"
