from dotenv import load_dotenv
import os
import streamlit as st
from google import genai
from reg import Reg_pipline as RP

# Load environment variables from a .env file.
load_dotenv()

class LargeLanguageModel:
    def __init__(self) -> None:
        # Extract the Gemini API key from environment variables.
        self.API_key = os.getenv("Gemini_Api_Key") or st.secrets["Gemini_Api_Key"]

    @staticmethod
    def Remove_extre_space(prompt:str) -> str:
        # Remove the extra space from the propmt.
        return prompt.strip()
    
    def config_llm(self,model: str = "gemini-robotics-er-1.5-preview") -> bool:
        """
        Initilize the model with approprate model and return boolean value.
        As th e model is initilized correctly or not.

        :param model: By default it have "gemini-robotics-er-1.5-preview" you can change it.
        :type model: Model must have the string data type.
        :return: Boolean value indicating success or failure of model initialization.
        """
        # Configure the Gemini API with the provided API key.
        self.client = genai.Client(api_key=self.API_key)

        responce = self.client.models.generate_content(
                              
                                        model="gemini-robotics-er-1.5-preview",
                                        contents="Hello, this is a test."
                                        )
        
        if(responce != None):
            return True
        
        else:
            return False
        
        return False
    
    @staticmethod
    def gather_information_from_reg(query: str, top_k: int = 5) -> list:
        """
        Gather relevant information from the Reg_pipline based on the query.

        :param query: The search query string.
        :param top_k: The number of top similar documents to retrieve.
        :return: List of relevant documents from the Reg_pipline.
        """
        try:
            # Initialize the Reg_pipline instance.
            reg_pipeline = RP()

            # Search for similar documents in the Reg_pipline collection.
            results = reg_pipeline.search_all(query=query, top_k=top_k)

            return results

        except Exception as e:
            print(f"An error occurred while gathering information from Reg_pipline: {e}")
            return []
        
    def generate_response(self,prompt: str,model: str = "gemini-robotics-er-1.5-preview") -> str:
        # Generate a response from the LLM based on the provided prompt.

        Vector_data_result = LargeLanguageModel.gather_information_from_reg(query=prompt)
        context = "No relevant context found."
        if(len(Vector_data_result) > 0):
            context = "\n".join([doc['document'] for doc in Vector_data_result])

        prompt = f"""
                     You are a helpful medical assistant. That give research information
                     related to the health care domain specially in ["Cancer","Diabetes","Cardiology"]
                     based on the context provided. Used contex to answer the given question and
                     represent the answer in detail manner. An respond in markdown format.If user want 
                     resopnce in bullet points then provide the response in bullet points. According
                     to user query manage that ant act as the expert in the medical domain. And do not give
                     any response if the context is not related to medical field. And do not
                     give any sensetive information relaed to medicine if any one ask drug name 
                     or treatment plan. Always suggest to consult a medical professional for such
                     information. And do not get hallucination. Use the below context to answer the question. And present
                     it as the user want it(If customer want in tabular form do it like-wise as specify in prompt). If customer not specify anything then present in standard format.


                     Context: {self.Remove_extre_space(context)}
                     Question: {self.Remove_extre_space(prompt)}
                  """
        

        if(context != "No relevant context found."):
            try:
                if(self.config_llm(model=model)):
                    response = self.client.models.generate_content(
                        model=model,
                        contents=prompt
                    )
                    return response.text
                
                else:
                    return "Error: LLM model configuration failed."

            except Exception as e:
                print(f"An error occurred while generating response from LLM: {e}")
                return "Error: An exception occurred while generating the response."
        else:
            return "No relevant context found to answer the question."
            
    
    

