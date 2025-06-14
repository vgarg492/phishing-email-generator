# Phishing Email Generator

A web application that generates phishing emails using AI to help security professionals and researchers test their organization's security awareness and train employees to recognize potential threats.

## Features

- Modern, user-friendly interface
- AI-powered email generation
- Realistic email composition interface
- Secure API key management
- Responsive design

## Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Groq API key

## Installation

1. Clone the repository:
```bash
git clone https://github.com/vgarg492/phishing-email-generator.git
cd phishing-email-generator
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install the required dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root directory and add your Groq API key:
```
GROQ_API_KEY=your_api_key_here
```

## Usage

1. Start the Flask application:
```bash
python main.py
```

2. Open your web browser and navigate to `http://localhost:5000`

3. Enter your prompt in the text area and click "Generate Email" to create a phishing email

## Project Structure

```
phishing-email-generator/
├── main.py              # Flask application and API integration
├── static/
│   ├── script.js        # Frontend JavaScript
│   └── style.css        # CSS styles
├── templates/
│   └── index.html       # Main HTML template
├── .env                 # Environment variables (not tracked by git)
├── .gitignore          # Git ignore file
└── requirements.txt     # Python dependencies
```

## Security Considerations

- Never commit your `.env` file containing API keys
- Use this tool responsibly and only for legitimate security testing
- Ensure you have proper authorization before testing on any systems
- Follow ethical guidelines and local laws regarding security testing

## Contributing

1. Fork the repository
2. Create a new branch for your feature
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is intended for educational and legitimate security testing purposes only. Users are responsible for ensuring they have proper authorization before using this tool on any systems. The developers are not responsible for any misuse or damage caused by this tool. 