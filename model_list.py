from google.genai import Client
# For checking ehich model is supported by your API key.

client = Client(api_key="AIzaSyDg9894NJHZEmcwiLuj5Nt0CttuUuFdKX0")

models = client.models.list()

def model_list(model_api_key: str = None) -> list:
    """List available models for the provided API key."""
    try:
        if not model_api_key:
            model_api_key = "AIzaSyDg9894NJHZEmcwiLuj5Nt0CttuUuFdKX0"
        client = Client(api_key=model_api_key)
        models = client.models.list()
        model_names = [model.name for model in models]
        return model_names
    
    except Exception as e:
        print(f"Error retrieving model list: {e}")
        return []
            

