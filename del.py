from google.genai import Client
# For checking ehich model is supported by your API key.

client = Client(api_key="Your_API_KEY")

models = client.models.list()

for m in models:
    print(m.name)
