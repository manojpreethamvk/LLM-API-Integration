
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

try:
    for model in client.models.list():
        if "generateContent" in (model.supported_actions or []):
            print(model.name)

except Exception as error:
    print(f"Could not list models: {error}")
