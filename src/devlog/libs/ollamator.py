import requests
import json
import logging

logger = logging.getLogger(__name__)

class Ollamator:
    def __init__(self, ollama_url, model="llama3.1:8b"):
        self.ollama_url = ollama_url
        self.model = model

    def process_text(self, text):
        system_prompt =  """
        You are a professional social manager for a development team.
        Your one and only goal is to review all the commits and their messages on the given repository and transform them into multiple coherent blog post.
        You will be given a list of commits and their messages, and you will need to transform them into a single coherent blog post.
        Use the date given at the beginning of the prompt to format the date in the blog post and to create a title.
        """
        try:
            # Combine the instruction prompt and the input text
            full_prompt = f"{system_prompt}\n\n{text}"

            # Prepare the payload for the Ollama API
            payload = {
                "model": self.model,
                "prompt": full_prompt,
                "stream": False
            }

            # Send the request to the Ollama instance
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload)
            response.raise_for_status()  # Raise an exception for bad status codes

            # Parse the JSON response
            result = response.json()

            return result['response']

        except requests.RequestException as e:
            logger.error(f"Error communicating with Ollama instance: {e}")
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error decoding JSON response: {e}")
            return None
        except KeyError as e:
            logger.error(f"Unexpected response format: {e}")
            return None

    def process_file(self, file_path):
        try:
            with open(file_path, 'r') as file:
                text = file.read()
            return self.process_text(text)
        except IOError as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return None