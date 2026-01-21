# Groq LLM Chat Web App Setup Instructions

1. Create and activate your Python environment:
   - python -m venv groqenv
   - On PowerShell: & C:\DataScience\groq_experiments\groqenv\Scripts\Activate.ps1

2. Install dependencies:
   - C:\DataScience\groq_experiments\groqenv\Scripts\python.exe -m pip install -r requirements.txt

3. Set your Groq API key:
   - Copy .env.example to .env
   - Edit .env and set GROQ_API_KEY=your_groq_api_key_here

4. Run the app:
   - C:\DataScience\groq_experiments\groqenv\Scripts\python.exe app.py

5. Open http://localhost:5000 in your browser to use the chat app.

If you rename your environment, update all paths above accordingly.
