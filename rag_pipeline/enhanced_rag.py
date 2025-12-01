import os
import logging
from typing import List, Dict, Any, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.llms.base import BaseLLM
from llm import LLMClient
from .query_transformer import QueryTransformer
from .reranker import RAGReranker
from .hallucination_checker import HallucinationChecker
from .memory import ConversationMemory
from .document_processor import DocumentProcessor
from .agents import QueryAgent

logger = logging.getLogger(__name__)

class EnhancedRAGPipeline:
    """
    Enhanced RAG Pipeline with advanced features:
    - Query transformation/expansion
    - RAG Fusion/reranking
    - Hallucination checking
    - Conversation memory
    - Multi-document support
    - Agent-based query processing
    """
    
    def __init__(self, user_id: str = None):
        """
        Initialize enhanced RAG pipeline
        
        Args:
            user_id: Unique user identifier for personalized memory
        """
        try:
            # Initialize embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            
            # Initialize ChromaDB with persistence
            persist_directory = "./chroma_db"
            os.makedirs(persist_directory, exist_ok=True)
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Create or get collection
            collection_name = "medical_documents"
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            
            # Initialize components
            self.llm = LLMClient()
            self.query_transformer = QueryTransformer()
            self.reranker = RAGReranker()
            self.hallucination_checker = HallucinationChecker()
            self.document_processor = DocumentProcessor()
            
            # Initialize memory if user_id provided
            self.memory = ConversationMemory(user_id) if user_id else None
            
            # Initialize query agent
            self.query_agent = QueryAgent(
                llm=self.llm,
                memory=self.memory,
                hallucination_checker=self.hallucination_checker
            )
            
            # Initialize text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
                separators=["\n\n", "\n", " ", ""]
            )
            
            logger.info("✅ Enhanced RAG Pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Error initializing Enhanced RAG Pipeline: {e}")
            raise e
    
    def add_documents(self, documents: List[Dict[str, Any]], metadata: Dict = None):
        """
        Add documents to the vector store
        
        Args:
            documents: List of documents with 'text' and optional 'metadata'
            metadata: Additional metadata for all documents
        """
        try:
            all_chunks = []
            all_metadatas = []
            all_ids = []
            
            for i, doc in enumerate(documents):
                # Split document into chunks
                chunks = self.text_splitter.split_text(doc.get('text', ''))
                
                for j, chunk in enumerate(chunks):
                    chunk_id = f"doc_{i}_chunk_{j}"
                    all_chunks.append(chunk)
                    
                    # Combine document metadata with chunk metadata
                    chunk_metadata = doc.get('metadata', {}).copy()
                    if metadata:
                        chunk_metadata.update(metadata)
                    chunk_metadata['chunk_index'] = j
                    chunk_metadata['document_index'] = i
                    
                    all_metadatas.append(chunk_metadata)
                    all_ids.append(chunk_id)
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(all_chunks).tolist()
            
            # Add to collection
            self.collection.add(
                documents=all_chunks,
                embeddings=embeddings,
                metadatas=all_metadatas,
                ids=all_ids
            )
            
            logger.info(f"✅ Added {len(all_chunks)} chunks to vector store")
            
        except Exception as e:
            logger.error(f"❌ Error adding documents: {e}")
            raise e
    
    def search(self, query: str, top_k: int = 10, use_reranking: bool = True):
        """
        Enhanced search with query transformation and reranking
        
        Args:
            query: Original user query
            top_k: Number of results to return
            use_reranking: Whether to use reranking
            
        Returns:
            List of relevant documents with scores
        """
        try:
            # Step 1: Transform/expand query
            expanded_queries = self.query_transformer.transform(query)
            
            # Step 2: Search for each query variation
            all_results = []
            for i, q in enumerate(expanded_queries):
                # Generate query embedding
                query_embedding = self.embedding_model.encode(q).tolist()
                
                # Search in vector store
                results = self.collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k * 2  # Get more results for reranking
                )
                
                # Combine results
                for j, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    all_results.append({
                        'text': doc,
                        'metadata': metadata,
                        'score': 1 - distance,  # Convert distance to similarity
                        'query_variation': i,
                        'original_rank': j
                    })
            
            # Step 3: Rerank results if enabled
            if use_reranking and len(all_results) > 1:
                reranked_results = self.reranker.rerank(
                    query=query,
                    documents=[r['text'] for r in all_results],
                    scores=[r['score'] for r in all_results]
                )
                
                # Update scores and sort
                for i, new_score in enumerate(reranked_results):
                    all_results[i]['reranked_score'] = new_score
                
                all_results.sort(key=lambda x: x.get('reranked_score', x['score']), reverse=True)
            else:
                all_results.sort(key=lambda x: x['score'], reverse=True)
            
            # Return top_k results
            return all_results[:top_k]
            
        except Exception as e:
            logger.error(f"❌ Error in enhanced search: {e}")
            return []
    
    def ask(self, query: str, conversation_id: str = None) -> Dict[str, Any]:
        """
        Process query with full RAG pipeline
        
        Args:
            query: User query
            conversation_id: ID for conversation context
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Add to conversation memory if available
            if self.memory and conversation_id:
                self.memory.add_message(conversation_id, "user", query)
            
            # Get relevant context
            relevant_docs = self.search(query)
            
            # Format context for LLM
            context = "\n\n".join([f"[Source {i+1}]: {doc['text']}" 
                                  for i, doc in enumerate(relevant_docs[:5])])
            
            # Generate answer using agent
            result = self.query_agent.process_query(
                query=query,
                context=context,
                relevant_docs=relevant_docs
            )
            
            # Check for hallucinations
            hallucination_check = self.hallucination_checker.check(
                answer=result['answer'],
                sources=relevant_docs
            )
            
            # Add to memory if available
            if self.memory and conversation_id and result['answer']:
                self.memory.add_message(conversation_id, "assistant", result['answer'])
            
            # Prepare response
            response = {
                'answer': result['answer'],
                'sources': relevant_docs[:3],  # Top 3 sources
                'hallucination_check': hallucination_check,
                'confidence': result.get('confidence', 0.8),
                'suggested_questions': self._generate_follow_up_questions(query, result['answer'])
            }
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Error in RAG pipeline: {e}")
            return {
                'answer': f"I apologize, but I encountered an error: {str(e)}",
                'sources': [],
                'hallucination_check': {'is_hallucination': False, 'confidence': 0.0},
                'confidence': 0.0,
                'suggested_questions': []
            }
    
    def _generate_follow_up_questions(self, query: str, answer: str) -> List[str]:
        """Generate suggested follow-up questions"""
        prompt = f"""
        Based on the original question and answer below, suggest 3 relevant follow-up questions.
        
        Original Question: {query}
        Answer: {answer}
        
        Suggest 3 follow-up questions that would help the user learn more about this topic.
        Return only the questions as a bulleted list.
        """
        
        try:
            response = self.llm.generate(prompt)
            questions = [q.strip('-• ') for q in response.split('\n') if q.strip()]
            return questions[:3]
        except:
            return []
    
    def get_conversation_history(self, conversation_id: str) -> List[Dict]:
        """Get conversation history"""
        if self.memory:
            return self.memory.get_conversation(conversation_id)
        return []
    
    def clear_conversation(self, conversation_id: str):
        """Clear conversation history"""
        if self.memory:
            self.memory.clear_conversation(conversation_id)
