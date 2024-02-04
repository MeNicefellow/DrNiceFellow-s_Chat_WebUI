from flask import Flask, render_template, request, jsonify, session
from flask_session import Session  # You may need to install this with pip
import requests
from flask import request, send_from_directory
import random

app = Flask(__name__)
import yaml
import os

# Load keys from config.yml
with open("config.yml", 'r') as ymlfile:
    cfg = yaml.safe_load(ymlfile)
app.secret_key = cfg['secret_key']
OPENAI_API_KEY = cfg['openai_api_key']
user = cfg['user_name']
host = cfg['host']

# Configure server-side session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from flask import make_response

@app.route('/assets/backgrounds/<path:filename>')
def custom_static(filename):
    return send_from_directory('assets/backgrounds', filename)
@app.route('/next_background_image')
def next_background_image():
    current_image = request.args.get('current_image')
    images = os.listdir('assets/backgrounds')
    current_index = images.index(current_image)
    next_index = (current_index + 1) % len(images)  # Loop back to the first image
    next_image = images[next_index]
    return jsonify({'image_name': next_image})
@app.route('/background_image')
def background_image():
    # Assuming the first image is the default background
    image_name = os.listdir('assets/backgrounds')[0]
    return send_from_directory('assets/backgrounds', image_name)

@app.route('/download_chat_history', methods=['GET'])
def download_chat_history():
    chat_history = '\n'.join(session.get('chat_history', [])).replace('[INST]', 'User: ').replace('[/INST]', '\nBot: ')
    response = make_response(chat_history)
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
    return response

@app.route('/')
def home():
    # Initialize chat history for new session
    if 'chat_history' not in session:
        session['chat_history'] = []
    if 'user' not in session:
        session['user'] = []
    if 'assistant' not in session:
        session['assistant'] = []
    title = user+"'s Personal Assistant"  # Replace 'xx' with the desired name
    return render_template('index.html', title=title)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']

    if question == 'clear':
        session['chat_history'] = []
        session['user'] = []
        session['assistant'] = []
        return jsonify({'answer': 'Chat history cleared!'})


    max_tokens = 1024
    min_p = 0.9
    top_k = 1
    top_p = 0.9
    temperature=0.8
    inst_beg = "[INST]"
    inst_end = "[/INST]"
    prompt = ''.join(session['chat_history'])+'[INST]'+question+'[/INST]'
    print("prompt:",prompt)
    
    payload = {
        "prompt": prompt,
        "model": "gpt-3.5-turbo-instruct",
        "max_tokens": max_tokens,
        "n_predict": max_tokens,
        "min_p": min_p,
        "stream": False,
        "seed": random.randint(
            1000002406736107, 3778562406736107
        ),  # Was acting weird without this
        "top_k": top_k,
        "top_p": top_p,
        "stop": ["</s>", inst_beg, inst_end],
        "temperature": temperature,
    }
    
    
    response = requests.post(
        host,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {OPENAI_API_KEY}",
        },
        json=payload,
        timeout=360,
        stream=False,
    )

    if response.status_code == 200:
        answer = response.json()['choices'][0]['text']
        # Append bot's response to the chat history
        session['chat_history'].append(prompt+answer)
        session['user'].append(question)
        session['assistant'].append(answer)
        return jsonify({'answer': answer})
    else:
        return jsonify({'error': 'Failed to fetch response from OpenAI'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=7860,debug=True)