from groq import Groq
import os
import re
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

# Common phishing typologies
PHISHING_TYPOLOGIES = {
    "Urgency": ["urgent", "immediate", "action required", "deadline"],
    "Authority": ["ceo", "manager", "director", "executive"],
    "Fear": ["suspended", "locked", "compromised", "security"],
    "Greed": ["reward", "bonus", "prize", "win"],
    "Curiosity": ["click here", "see attached", "check this"]
}

def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def sanitize_input(text):
    """Sanitize user input to prevent XSS and injection attacks."""
    # Remove potentially dangerous characters
    text = re.sub(r'[<>]', '', text)
    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def analyze_phishing_typology(prompt):
    """Analyze the prompt for common phishing typologies."""
    typologies_found = []
    prompt_lower = prompt.lower()
    
    for typology, keywords in PHISHING_TYPOLOGIES.items():
        if any(keyword in prompt_lower for keyword in keywords):
            typologies_found.append(typology)
    
    return typologies_found

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


@app.route('/generate_email', methods=['POST'])
def generate_email():
    """
        Generate an email based on the provided data.
    """
    try:
        data = request.json
        prompt = data.get('prompt', '').strip()
        
        # Input validation
        if not prompt:
            return jsonify({"error": "Prompt is required"}), 400
        
        if len(prompt) > 500:
            return jsonify({"error": "Prompt is too long. Maximum 500 characters allowed."}), 400
        
        # Sanitize input
        prompt = sanitize_input(prompt)
        
        # Analyze phishing typology
        typologies = analyze_phishing_typology(prompt)
        
        # Generate email with typology analysis
        email = groq_client(
            f"Generate a simulated phishing email for educational purposes. "
            f"Detected typologies: {', '.join(typologies)}. "
            f"Format: 'Subject: ', 'To: ', 'Content: '. "
            f"Prompt: {prompt}"
        )
        
        # Parse email components
        email = email.replace("*", "")
        
        try:
            subject = email.split("Subject:")[1].split("To:")[0].strip()
            to = email.split("To:")[1].split("\n")[0].strip()
            content = email.split("Content:")[1].strip()
            
            # Validate email format
            if not validate_email(to):
                return jsonify({"error": "Invalid email format generated"}), 400
            print(f"Typologies:{typologies}")
            return jsonify({
                "subject": subject,
                "to": to,
                "content": content,
                "typologies": typologies
            })
            
        except IndexError:
            return jsonify({"error": "Failed to parse generated email"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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
    app.run(debug=False, host='127.0.0.1', port=8000)
    print("Done.")
