from flask import Flask, render_template, request, jsonify#, session
from flask_session import Session  # You may need to install this with pip
import requests
from flask import request, send_from_directory
from utils import *
import subprocess
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

rag = cfg['rag']
if rag:
    from rag import DatabaseManager
    db_name = cfg['db_name']
    db_host = cfg['db_host']
    password = cfg['db_password']
    port = cfg['db_port']
    user = cfg['db_user']
    table_name = cfg['db_table_name']
    db = DatabaseManager(db_name, db_host, password, port, user, table_name)

# Configure server-side session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
#session_dir = os.path.join(app.instance_path, 'session')
#if not os.path.exists(session_dir):
#    os.makedirs(session_dir)
#app.config["SESSION_FILE_DIR"] = session_dir
Session(app)

from flask import make_response

session = {}

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
    chat_history = session.get('chat_history', '').replace('[INST]', 'User: ').replace('[/INST]', '\nBot: ')
    response = make_response(chat_history)
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
    return response

@app.route('/')
def home():
    # Initialize chat history for new session
    if 'chat_history' not in session:
        session['chat_history'] = ''
    if 'msg_history' not in session:
        session['msg_history'] = []
    title = user+"'s Personal Assistant"  # Replace 'xx' with the desired name
    return render_template('index.html', title=title)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']
    tool_usage = data.get('tool_usage', False)
    print("tool_usage:",tool_usage)

    if question == 'clear':
        session['chat_history'] = ''
        session['msg_history'] = []
        #session['user'] = []
        #session['assistant'] = []
        return jsonify({'answer': 'Chat history cleared!'})


    if 'chat_history' not in session:
        session['chat_history'] = ''
    if 'msg_history' not in session:
        session['msg_history'] = []
    if tool_usage:

        first_prompt = (
            f'Please provide the answer to the following question strictly in JSON format, '
            f'with no additional text or explanation. The JSON response should contain only two keys: '
            f'"method" and "content". The "method" key can have one of five values: "DirectAnswer", '
            f'"SearchEngine", "python", "SaveToDB", or "RetrieveFromDB". The "content" key should '
            f'contain the corresponding output based on the method chosen. For "DirectAnswer", it should '
            f'be the factual answer to the question posed. For "SearchEngine", it should be the exact '
            f'search query you would use. For "python", it should be the Python code that would generate '
            f'the answer. For "SaveToDB", use this method in two cases: when the user provides important '
            f'information that should be saved for future sessions, or to summarize the content of the '
            f'current chat session for future reference. The "content" should be the note in natural language you wish to save '
            f'to the database. For "RetrieveFromDB", use this method when the user asks about or refers to '
            f'something from a previous session. The "content" should be the query in natural language used to retrieve '
            f'data from the database. Here is the question: {question}'
        )
        # After performing a "SaveToDB" or "RetrieveFromDB" operation, you will be given a chance to '
        #    f'follow up with a "DirectAnswer" to provide the user with a response based on the newly '
        #    f'updated or retrieved information.

        session['msg_history'].append({"role": "user", "content": first_prompt})

        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "mode": "instruct",
            "messages": session['msg_history']
        }
        response = requests.post(host, headers=headers, json=data, verify=False)
        print("request sent:",data)
        i = 0
        tool_used = ''
        while i<5:
            if response.status_code == 200:
                print("response with 200")
                answer = response.json()['choices'][0]['message']['content']#response.json()['choices'][0]['text']
                print("answer:",answer)
                # Append bot's response to the chat history
                ###session['chat_history']=prompt+answer
                session['msg_history'].append({"role": "assistant", "content": answer})
                print("chat_history:",session['chat_history'])

                data = extract_json(answer)
                print("data:",data)
                print(data['method'] == 'RetrieveFromDB')
                if 'method' not in data or 'content' not in data:
                    return jsonify({'error': 'Invalid JSON format. Please provide the answer in the specified format.'}), 400
                elif data['method'] not in ['DirectAnswer', 'SearchEngine', 'python', 'SaveToDB', 'RetrieveFromDB']:
                    return jsonify({'error': 'Invalid method. Please choose one of the following: "DirectAnswer", "SearchEngine", or "python".'}), 400
                elif data['method'] == 'DirectAnswer':
                    return jsonify({'answer': data['content']+ f' (Tool used: {tool_used} for the answer)'})
                elif data['method'] == 'SearchEngine':
                    tool_used += 'SearchEngine '
                    output = retrieve_web_data(data['content'])
                    prompt = f'Here are the search results obtained using the keywords you provided: "{output}". Please review these results and determine if they sufficiently answer the original question. Respond in strict JSON format with two keys: "method" and "content". If the results are sufficient, use "DirectAnswer" for "method" and provide the answer in "content". If the results are not sufficient and you suggest conducting another search, use "SearchEngine" for "method" and provide the new keywords in "content". No other text or explanation should be provided outside of the JSON response.'
                elif data['method'] == 'python':
                    tool_used += 'python '
                    code = data['content']
                    output = subprocess.run(
                        ["python3", "-c", code],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        )
                    stdout = output.stdout.decode()
                    stderr = output.stderr.decode()
                    output = f"stdout: {stdout}, stderr: {stderr}"
                    print(f"Round {i} python output: {output}")
                    prompt = f'The Python code you provided has been executed, and the result is as follows: "{output}". Please review this output and determine if it correctly answers the original question. Respond in strict JSON format with two keys: "method" and "content". If the execution was successful and the result is correct, use "DirectAnswer" for "method" and provide the answer in "content". If there was an error and you need to provide corrected Python code, use "python" for "method" and include the revised code in "content". No other text or explanation should be provided outside of the JSON response.'
                elif data['method'] == 'SaveToDB':
                    tool_used += 'SaveToDB '
                    notes = [data['content']]
                    print("notes to save:",notes)
                    db.save_to_db(notes)
                    prompt = f'The chat history has been saved to the database. If you would like to follow up with a response based on this information, please provide a "DirectAnswer" in JSON format with the answer to the original question. If you would like to save additional information or perform another operation, please provide the corresponding JSON response with the "method" and "content" keys.'
                elif data['method'] == 'RetrieveFromDB':
                    tool_used += 'RetrieveFromDB '
                    query = data['content']
                    print("query to retrieve:",query)
                    output = db.query_db(query)
                    print("output from db:",output)
                    prompt = f'The information retrived from the database is as follows: "{output}". Please review this information and determine if it sufficiently answers the original question. Respond in strict JSON format with two keys: "method" and "content". If the retrieved information is sufficient, use "DirectAnswer" for "method" and provide the answer in "content". If the information is not sufficient and you need to perform another operation, use the corresponding method for "method" and provide the necessary "content". No other text or explanation should be provided outside of the JSON response.'
                else:
                    print("Invalid method:",data['method'])
                i += 1
                print(f"Round {i} prompt: {prompt}")
                session['msg_history'].append({"role": "user", "content": prompt})
                data = {
                    "mode": "instruct",
                    "messages": session['msg_history']
                }
                response = requests.post(host, headers=headers, json=data, verify=False)
            else:
                print("response with error")
                return jsonify({'error': 'Failed to fetch response from OpenAI'}), 500
    else:
        max_tokens = 1024
        min_p = 0.9
        top_k = 1
        top_p = 0.9
        temperature=0.8
        inst_beg = "[INST]"
        inst_end = "[/INST]"
        prompt = session['chat_history']+'[INST]'+question+'[/INST]'
        print("prompt:",prompt)
        #print("user:",session['user'])
        #print("assistant:",session['assistant'])

        #payload = {
        #    "prompt": prompt,
        #    "model": "gpt-3.5-turbo-instruct",
        #    "max_tokens": max_tokens,
        #    "n_predict": max_tokens,
        #    "min_p": min_p,
        #    "stream": False,
        #    "seed": random.randint(
        #        1000002406736107, 3778562406736107
        #    ),  # Was acting weird without this
        #    "top_k": top_k,
        #    "top_p": top_p,
        #    "stop": ["</s>", inst_beg, inst_end],
        #    "temperature": temperature,
        #}
        #
        #
        #response = requests.post(
        #    host,
        #    headers={
        #        "Accept": "application/json",
        #        "Content-Type": "application/json",
        #        "Authorization": f"Bearer {OPENAI_API_KEY}",
        #    },
        #    json=payload,
        #    timeout=360,
        #    stream=False,
        #)
        session['msg_history'].append({"role": "user", "content": question})

        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "mode": "instruct",
            "messages": session['msg_history']
        }
        response = requests.post(host, headers=headers, json=data, verify=False)
        print("request sent:",data)





        if response.status_code == 200:
            print("response with 200")
            answer = response.json()['choices'][0]['message']['content']#response.json()['choices'][0]['text']
            # Append bot's response to the chat history
            ###session['chat_history']=prompt+answer
            session['msg_history'].append({"role": "assistant", "content": answer})
            print("chat_history:",session['chat_history'])
            #session['user'].append(question)
            #session['assistant'].append(answer)
            return jsonify({'answer': answer})
        else:
            print("response with error")
            return jsonify({'error': 'Failed to fetch response from OpenAI'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=8000,debug=True)