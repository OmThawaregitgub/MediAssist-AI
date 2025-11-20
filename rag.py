import chromadb
from llm import LLMClient

class RAGPipeline:
    def __init__(self) -> None:
        """
        Initialize the RAGPipeline components.

        This method performs the following:
        1. Creates an in-memory ChromaDB client.
        2. Generates a unique collection name to avoid conflicts across instances.
        3. Initializes the LLM client used for generating responses.
        4. Wraps initialization in a try/except block to catch and surface errors.

        Returns:
            None
        Raises:
            Exception: If any component fails during initialization.
        """
        try:
            # Use in-memory client with unique collection name
            self.client = chromadb.Client()
            
            # Create unique collection name to avoid conflicts
            collection_name = f"medical_data_{id(self)}"
            self.collection = self.client.create_collection(collection_name)
            
            # Initialize LLM
            self.llm = LLMClient()
            
            print("✅ MediAssist AI Initialized Successfully")
                
        except Exception as e:
            print(f"❌ Error initializing RAGPipeline: {e}")
            raise e
    
    def ask(self, query: str) -> str:
        """
        Process and respond to user queries.

        Parameters:
            query (str): The user's input question or message.

        Returns:
            str: A generated response from the LLM or a predefined greeting.

        Behavior:
            - Detects greetings and returns friendly preset responses.
            - Identifies medical-related keywords to generate more focused prompts.
            - Uses general prompts for non-medical questions.
            - Handles unexpected errors gracefully by returning a user-friendly message.
        """
        
        try:
            query_lower = query.lower().strip()
            
            # Handle greetings
            if any(word in query_lower for word in ["hi", "hello", "hey"]):
                return "Hello! 👋 I'm MediAssist AI. How can I help you with medical questions today?"
            
            if "how are you" in query_lower:
                return "I'm doing well, thank you! Ready to assist you with medical information."
            
            # Handle medical questions
            if any(word in query_lower for word in ["cancer", "fasting", "diabetes", "treatment", "medical", "health"]):
                prompt = f"Please provide clear, helpful information about: {query}"
            else:
                prompt = f"Please answer this question: {query}"
            
            return self.llm.generate(prompt)
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}"
    
    def get_collection_info(self) -> str:
        """
        Return basic information about the medical AI assistant.

        Returns:
            str: A friendly description of the assistant's role.
        """
        return "🩺 Medical AI Assistant - Ready to Help"

