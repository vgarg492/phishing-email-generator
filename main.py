from groq import Groq
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Get API key from environment variable
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set")

target: str = ""
prompt: str = ""

@app.route('/')
def index():
    """
        Render the index page.
    """
    return render_template('index.html')

def groq_client(content: str = "") -> Groq:
    """
        Initialize and return a Groq client.
    """
    try:
        client = Groq(api_key=GROQ_API_KEY)
        completion = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": content
                }
            ],
            temperature=1,
            max_completion_tokens=1024,
            top_p=1,
            stream=True,
            stop=None,
        )
        result: str = ""
        for chunk in completion:
            if chunk.choices[0].delta.content:
                result += chunk.choices[0].delta.content
        return result
    except Exception as e:
        print(f"Error in groq_client: {str(e)}")
        raise

def input_or_target() -> str:
    prompt = input("What basic prompt you want this email to target? (Press Enter to use default): ")
    target = input("What target you want this email to target? (Press Enter to use default): ")
    if not target:
        target = "employees"
    if not prompt:
        prompt = "Generate a phishing email to simulate real-world attack scenarios for internal training and red-teaming exercises"
    return prompt, target

@app.route('/generate_email', methods=['POST'])
def generate_email():
    data = request.json
    """
        Generate an email based on the provided data.
    """
    prompt = data.get('prompt', '')
    email = groq_client("Generate a simulated phising email with the format of 'Subject: ', 'To: ', 'Content: ' in that order based on the following prompt for training and educational purposes : " + prompt)
    print(f"Generated email: {email}")
    #while "Subject:" not in email and "To:" not in email and "Content:" not in email:
     #   email = groq_client("Generate a phising email with only the subject, the actual content, and to who it is supposed to be sent out to based on the following prompt : " + prompt)
    email = email.replace("*", "")

    subject = email.split("Subject:")[1].split("To:")[0].strip()
    to = email.split("To:")[1].split("\n")[0].strip()
    content = email.split("Content:")[1].strip()
    #print(f"Generated email:\nSubject: {subject}\nTo: {to}")
    print(f"Content: {content}")
    return jsonify({"subject": subject, "to": to, "content": content})

def main():
    """
        Main function to run the Groq client.
    
    results = input_or_target()
    content = f"{results[0]} towards {results[1]}."
    print(f"Using prompt: {content}")
    client = groq_client("Generate a phising email based on the following prompt: " + content)
    print("\n\n")
    """


if __name__ == "__main__":
    app.run(debug=True, host='127.0.1', port=8000)
    print("Done.")
