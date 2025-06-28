from groq import Groq
import os
import re
from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from dotenv import load_dotenv
import sqlite3
import bcrypt
import secrets
# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = secrets.token_hex(16)  # Generate a random secret key

def get_db_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with required tables."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE, password BLOB)''')
    conn.commit()
    conn.close()

# Initialize database
init_db()

def sign_up(username, password):
    try:
        """Register a new user."""
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()
        
        #create a new email databse for the user
        user_email_db = f"{username}_emails.db"
        user_conn = sqlite3.connect(user_email_db)
        user_cursor = user_conn.cursor()
        user_cursor.execute('''CREATE TABLE IF NOT EXISTS emails (id INTEGER PRIMARY KEY AUTOINCREMENT, subject TEXT, \"to\" TEXT, content TEXT, typologies TEXT, aggression TEXT, prompt TEXT)''')
        user_conn.commit()
        user_conn.close()
        
    except sqlite3.IntegrityError:
        print(f"User already exists")
        
    except Exception as e:
        print(f"Error in sign_up: {str(e)}")
        
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user[2]):
            print(f"User {username} signed in successfully")
            session['username'] = username  # Store username in session
            return redirect(url_for('index'))
        else:
            print(f"Invalid username or password")
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')




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

@app.route('/email')
def index():
    """
        Render the index page.
    """
    return render_template('index.html')

@app.route('/')
def login():
    """
        Render the login page.
    """
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        sign_up(username, password)
        return redirect(url_for('login'))
    return render_template('signup.html')

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
        # Get username from session
        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 401
        
        data = request.json
        prompt = data.get('prompt', '').strip()
        aggression = data.get('aggression', '').strip()
        
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
            f"Generate a simulated phishing email for educational purposes. In the email, you should be as aggressive as the aggression level. Also in the 'To' section, you must put an email that is valid and not a fake email."
            f"Detected typologies: {', '.join(typologies)}. "
            f"Aggression: {aggression}%"
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
            print(f"Aggression percentage: {aggression}")

            # Save the email to the user's database
            user_email_db = f"{username}_emails.db"
            user_conn = sqlite3.connect(user_email_db)
            user_cursor = user_conn.cursor()
            
            # Create table if it doesn't exist (with proper quoted column name)
            user_cursor.execute('''CREATE TABLE IF NOT EXISTS emails 
                                  (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                                   subject TEXT, 
                                   "to" TEXT, 
                                   content TEXT, 
                                   typologies TEXT, 
                                   aggression TEXT, 
                                   prompt TEXT)''')
            
            # Insert the email data
            user_cursor.execute('INSERT INTO emails (subject, "to", content, typologies, aggression, prompt) VALUES (?, ?, ?, ?, ?, ?)', 
                               (subject, to, content, str(typologies), aggression, prompt))
            user_conn.commit()
            user_conn.close()

            return jsonify({
                "subject": subject,
                "to": to,
                "content": content,
                "typologies": typologies,
                "aggression": aggression,
                "prompt": prompt
            })  
            
        except IndexError:
            return jsonify({"error": "Failed to parse generated email"}), 500
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_emails', methods=['GET'])
def get_emails():
    """
    Get all emails for the current user.
    """
    try:
        # Get username from session
        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 401
        
        # Connect to user's email database
        user_email_db = f"{username}_emails.db"
        user_conn = sqlite3.connect(user_email_db)
        user_cursor = user_conn.cursor()
        
        # Get all emails for the user
        user_cursor.execute('SELECT id, subject, "to", content, typologies, aggression, prompt FROM emails ORDER BY id DESC')
        emails = user_cursor.fetchall()
        
        # Convert to list of dictionaries
        email_list = []
        for email in emails:
            email_list.append({
                'id': email[0],
                'subject': email[1],
                'to': email[2],
                'content': email[3],
                'typologies': email[4],
                'aggression': email[5],
                'prompt': email[6]
            })
        
        user_conn.close()
        
        return jsonify({"emails": email_list})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/get_email/<int:email_id>', methods=['GET'])
def get_email(email_id):
    """
    Get a specific email by ID for the current user.
    """
    try:
        # Get username from session
        username = session.get('username')
        if not username:
            return jsonify({"error": "User not logged in"}), 401
        
        # Connect to user's email database
        user_email_db = f"{username}_emails.db"
        user_conn = sqlite3.connect(user_email_db)
        user_cursor = user_conn.cursor()
        
        # Get the specific email
        user_cursor.execute('SELECT id, subject, "to", content, typologies, aggression, prompt FROM emails WHERE id = ?', (email_id,))
        email = user_cursor.fetchone()
        
        if not email:
            user_conn.close()
            return jsonify({"error": "Email not found"}), 404
        
        # Convert to dictionary
        email_data = {
            'id': email[0],
            'subject': email[1],
            'to': email[2],
            'content': email[3],
            'typologies': email[4],
            'aggression': email[5],
            'prompt': email[6]
        }
        
        user_conn.close()
        
        return jsonify({"email": email_data})
        
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
