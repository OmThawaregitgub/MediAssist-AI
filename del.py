from google.genai import Client

client = Client(api_key="AIzaSyDg9894NJHZEmcwiLuj5Nt0CttuUuFdKX0")

models = client.models.list()

for m in models:
    print(m.name)
