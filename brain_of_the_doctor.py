import os
import base64
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

def encode_image(image_path):
    """
    Converts an image to base64 encoding
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def analyze_image_with_query(query, model, encoded_image):
    """
    Sends a prompt and image to Groq vision model and returns the response
    """
    print("Initializing Groq Client...")
    client = Groq(api_key=GROQ_API_KEY)

    try:
        # Send a simple text query + image URL (as base64)
        chat_completion = client.chat.completions.create(
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": query
                }
            ],
            image_url={"url": f"data:image/jpeg;base64,{encoded_image}"}
        )
        print("Response received!")

        # Extract and return the AI response text
        response_text = chat_completion.choices[0].message.content
        print("AI Response:", response_text)
        return response_text

    except Exception as e:
        print(f"Error during Groq API call: {e}")
        return "Sorry, I couldn't analyze the image."
