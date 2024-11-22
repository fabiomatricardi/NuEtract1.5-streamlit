import requests
import json
from typing import List, Dict

# Function to send a request to the server and get a response
def get_response(
    server_url: str,
    messages: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 2048,
    stream: bool = True,
) -> str:
    headers = {"Content-Type": "application/json"}
    data = {
        "prompt": messages,
        "temperature": temperature,
        "top_p": top_p,
        "max_tokens": max_tokens,
        "stream": stream,
        "stop":['<|im_end|>'],
    }
    # Send POST request to the server
    response = requests.post(
        f"{server_url}/v1/completions",
        headers=headers,
        data=json.dumps(data),
        stream=stream,
    )
    response.raise_for_status()  # Ensure the request was successful
    if stream:  #THIS PART IS TO BE FIXED
        content = ""
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode("utf-8").lstrip("data: ")
                try:
                    json_line = json.loads(decoded_line)
                    if "choices" in json_line and len(json_line["choices"]) > 0:
                        delta = json_line["choices"][0].get("delta", {})
                        content_piece = delta.get("content", "")
                        content += content_piece
                        print(content_piece, end="", flush=True)
                except json.JSONDecodeError:
                    continue
        print()  # Ensure the next prompt starts on a new line
        return content
    else:
        result = response.json()
        print(result['content'])
        if "choices" in result and len(result["choices"]) > 0:
            return result["choices"][0]["message"]["content"]
        else:
            return ""
# Function to run the chatbot
def chatbot(
    server_url: str,
    temperature: float = 0.7,
    top_p: float = 0.9,
    max_tokens: int = 4096,
    stream: bool = False,
):
    while True:
        prompt = input("User: ")
        if prompt.lower() in ["exit", "quit"]:
            break
        template = f"""<|im_start|>user
{prompt}<|im_end|>
<|im_start|>assistant"""
    #while True:
        print("Assistant: ", end="")
        response = get_response(
            server_url, template, temperature, top_p, max_tokens, stream
        )
        print(response)
if __name__ == "__main__":
    server_url = "http://localhost:8001"
    chatbot(server_url=server_url)