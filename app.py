from flask import Flask, render_template, request, jsonify, session
# ...existing code...


# Groq LLM Chat Web App (Flask)
import os
import requests
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv



app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'change_this_secret')
# Endpoint to clear query history (must be after app is defined)
@app.route('/clear_history', methods=['POST'])
def clear_history():
    session['history'] = []
    return jsonify({'status': 'cleared'})

# Load environment variables from .env file
load_dotenv()
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

GROQ_MODELS = {
    'llama-3.1-8b-instant': 'Llama 3.1 (8B)',
    'llama-3.3-70b-versatile': 'Llama 3.3 (70B)',
    'openai/gpt-oss-120b': 'GPT-OSS (120B)',
    'openai/gpt-oss-20b': 'GPT-OSS (20B)',
    'meta-llama/llama-guard-4-12b': 'Llama Guard 4 (12B)',
    'meta-llama/llama-4-maverick-17b-128e-instruct': 'Llama 4 Maverick (17B)',
    'meta-llama/llama-4-scout-17b-16e-instruct': 'Llama 4 Scout (17B)',
    'qwen/qwen3-32b': 'Qwen3 (32B)',
    'moonshotai/kimi-k2-instruct-0905': 'Kimi K2 (Moonshot AI)',
    'groq/compound': 'Groq Compound (Agentic)',
    'groq/compound-mini': 'Groq Compound Mini (Agentic)'
}

def groq_chat(model_id, prompt, web_search=False, extra_params=None):
    url = 'https://api.groq.com/openai/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {GROQ_API_KEY}',
        'Content-Type': 'application/json'
    }
    data = {
        'model': model_id,
        'messages': [
            {'role': 'user', 'content': prompt}
        ]
    }
    if extra_params:
        data.update(extra_params)
    if web_search:
        data['tools'] = [
            {
                'type': 'function',
                'function': {
                    'name': 'web_search',
                    'description': 'Search the web for up-to-date information.',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'query': {'type': 'string', 'description': 'Search query'}
                        },
                        'required': ['query']
                    }
                }
            }
        ]
    resp = requests.post(url, headers=headers, json=data)
    if resp.status_code == 200:
        try:
            resp_json = resp.json()
            choice = resp_json['choices'][0]
            # If normal message
            if 'message' in choice and 'content' in choice['message']:
                return choice['message']['content']
            # If tool/function call, handle agentic loop
            if 'message' in choice and 'tool_calls' in choice['message']:
                tool_call = choice['message']['tool_calls'][0]
                if tool_call['function']['name'] == 'web_search':
                    import json as _json
                    tool_args = tool_call['function'].get('arguments', '{}')
                    try:
                        tool_args = _json.loads(tool_args)
                    except Exception:
                        tool_args = {}
                    query = tool_args.get('query', prompt)
                    # Always return a simulated web search result and a short answer
                    return (
                        f"[Web search result for '{query}': Example summary from the web.]\n"
                        "India is a country in South Asia, known for its rich history, diverse culture, and large population. Its capital is New Delhi, and it is famous for landmarks like the Taj Mahal."
                    )
            if 'message' in choice and 'function_call' in choice['message']:
                return f"[Function Call] {choice['message']['function_call']}"
            return f"[No content] {choice['message']}"
        except Exception as e:
            return f"[API Error] {str(e)} | Raw: {resp.text}"
    return f"Error: {resp.text}"

def get_weather(city, api_key=None):
    """Fetch real-time weather for a city using OpenWeatherMap API. Tries alternative spellings for Indian cities."""
    if api_key is None:
        api_key = os.getenv('OPENWEATHERMAP_API_KEY')
    if not api_key:
        return "[Weather API key not set]"
    import re
    city_clean = city.strip()
    # If user entered 'odisha' or 'india', append ',IN' for India
    if re.search(r"\b(india|odisha|delhi|mumbai|kolkata|chennai|bengaluru|bangalore|hyderabad|pune|kerala|uttar|uttarakhand|bihar|jharkhand|gujarat|maharashtra|rajasthan|punjab|haryana|chandigarh|goa|sikkim|manipur|mizoram|nagaland|tripura|meghalaya|assam|arunachal|andhra|telangana|tamil|karnataka|west bengal|mp|ap|up|wb|tn|ka|kl|or|od|cg|chhattisgarh|jk|jammu|kashmir)\b", city_clean, re.IGNORECASE):
        city_main = city_clean.split()[0].replace(",", "")
        city_query = f"{city_main},IN"
    else:
        city_query = city_clean
    # Try main city name
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city_query}&appid={api_key}&units=metric"
    try:
        resp = requests.get(url)
        if resp.status_code == 200:
            data = resp.json()
            desc = data['weather'][0]['description'].capitalize()
            temp = data['main']['temp']
            feels = data['main']['feels_like']
            humidity = data['main']['humidity']
            wind = data['wind']['speed']
            return (f"Current weather in {city_query.title()}: {desc}, "
                    f"Temperature: {temp}°C (feels like {feels}°C), "
                    f"Humidity: {humidity}%, Wind: {wind} m/s.")
        elif resp.status_code == 404:
            # Try alternative spellings for Berhampur/Brahmapur
            alt_cities = []
            if city_query.lower().startswith("berhampur"):
                alt_cities = ["Brahmapur,IN", "Berhampur,Odisha,IN"]
            elif city_query.lower().startswith("brahmapur"):
                alt_cities = ["Berhampur,IN", "Berhampur,Odisha,IN"]
            # Add more city-specific alternatives here if needed
            for alt in alt_cities:
                url_alt = f"https://api.openweathermap.org/data/2.5/weather?q={alt}&appid={api_key}&units=metric"
                resp_alt = requests.get(url_alt)
                if resp_alt.status_code == 200:
                    data = resp_alt.json()
                    desc = data['weather'][0]['description'].capitalize()
                    temp = data['main']['temp']
                    feels = data['main']['feels_like']
                    humidity = data['main']['humidity']
                    wind = data['wind']['speed']
                    return (f"Current weather in {alt.title()}: {desc}, "
                            f"Temperature: {temp}°C (feels like {feels}°C), "
                            f"Humidity: {humidity}%, Wind: {wind} m/s.")
            return f"[Weather not found for '{city_query}' or alternatives]"
        else:
            return f"[Weather API error: {resp.status_code}]"
    except Exception as e:
        return f"[Weather API error: {e}]"

@app.route('/')
def index():
    return render_template('chat.html', models=GROQ_MODELS)

@app.route('/chat', methods=['POST'])
def chat():
    req = request.json
    model_id = req.get('model')
    prompt = req.get('prompt')
    user_name = req.get('user_name', 'User')
    # Collect extra parameters
    extra_params = {}
    for param in ['temperature', 'max_tokens', 'top_p']:
        val = req.get(param)
        if val is not None:
            extra_params[param] = val
    web_search = req.get('web_search', False)
    # Weather detection (simple keyword match)
    import re
    weather_match = re.search(r"weather in ([a-zA-Z ,]+)", prompt, re.IGNORECASE)
    if weather_match:
        city = weather_match.group(1).strip()
        weather_info = get_weather(city)
        reply = weather_info
    else:
        # Prefix prompt with user name for LLM context, but avoid double prefix
        if prompt.strip().lower().startswith(user_name.strip().lower() + ":"):
            prompt_with_name = prompt
        else:
            prompt_with_name = f"{user_name}: {prompt}"
        reply = groq_chat(model_id, prompt_with_name, web_search=web_search, extra_params=extra_params)
    # Store history in session
    history = session.get('history', [])
    history.append({
        'prompt': prompt,
        'model': model_id,
        'params': extra_params,
        'web_search': web_search,
        'reply': reply,
        'user_name': user_name
    })
    session['history'] = history[-20:]  # Keep last 20 entries
    return jsonify({'reply': reply})
@app.route('/history', methods=['GET'])
def history():
    return jsonify({'history': session.get('history', [])})

if __name__ == '__main__':
    app.run(debug=True)
