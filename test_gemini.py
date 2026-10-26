
import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing. Check your .env file.")

client = genai.Client(api_key=api_key)

for attempt in range(3):
    try:
        response = client.models.generate_content(
            model="gemini-flash-lite-latest",
            contents="Reply with exactly: Gemini API is working!"
        )

        print("Gemini response:")
        print(response.text)
        break

    except ServerError as error:
        if attempt == 2:
            print("Gemini is still unavailable. Try again later.")
            print(f"Error: {error}")
        else:
            delay = 5 * (2 ** attempt)
            print(f"Temporary server error. Retrying in {delay} seconds...")
            time.sleep(delay)

    except Exception as error:
        print(f"Request failed: {type(error).__name__}: {error}")
        break
