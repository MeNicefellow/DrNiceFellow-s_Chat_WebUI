from flask import Flask, render_template, request, jsonify
from flask_session import Session
import requests
from flask import request, send_from_directory
from utils import *
import subprocess
import random
import threading
import time
from datetime import datetime, timedelta
from dateutil.parser import parse as parse_datetime
import traceback
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
system_prompt = {"role": "system", "content": f"You are a friend of {user}"}
rag = cfg['rag']
if rag:
    from rag import DatabaseManager
    db_name = cfg['db_name']
    db_host = cfg['db_host']
    password = cfg['db_password']
    port = cfg['db_port']
    db_user = cfg['db_user']
    table_name = cfg['db_table_name']
    db = DatabaseManager(db_name, db_host, password, port, db_user, table_name)

# Configure server-side session
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

from flask import make_response

pending_messages = []  # Global list to store pending assistant messages
session = {}
pending_reminders = []  # Global list to store pending reminders


@app.route('/get_calendar_events', methods=['GET'])
def get_calendar_events():
    try:
        # Get the current time
        now = datetime.now()
        # Get events for the next 7 days
        end_date = now + timedelta(days=7)
        events = db.get_upcoming_events(now, end_date)
        
        # Format events for JSON response
        formatted_events = []
        for event in events:
            event_id, event_content, event_datetime = event
            formatted_events.append({
                'id': event_id,
                'title': event_content,
                'date': event_datetime.isoformat()
            })
        
        return jsonify(formatted_events)
    except Exception as e:
        print(f"Error fetching calendar events: {e}")
        return jsonify({'error': 'Failed to fetch calendar events'}), 500



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
    chat_history = session.get('chat_history', '').replace('</s>', 'User: ').replace('</s>', '\nBot: ')
    response = make_response(chat_history)
    response.headers["Content-Disposition"] = "attachment; filename=chat_history.txt"
    return response

@app.route('/')
def home():
    # Initialize chat history for new session
    if 'chat_history' not in session:
        session['chat_history'] = ''
    if 'msg_history' not in session:
        session['msg_history'] = [system_prompt]
    title = user + "'s Personal Assistant"  # Replace 'xx' with the desired name
    return render_template('index.html', title=title)

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data['question']
    tool_usage = data.get('tool_usage', False)
    print("tool_usage:", tool_usage)

    if question == 'clear':
        session['chat_history'] = ''
        session['msg_history'] = [system_prompt]
        return jsonify({'answer': 'Chat history cleared!'})

    if 'chat_history' not in session:
        session['chat_history'] = ''
    if 'msg_history' not in session:
        session['msg_history'] = [system_prompt]
    if tool_usage:
        if rag:
            now = datetime.now()
            first_prompt = (
                f'Current time: {str(now)}. '
                f'Please provide the answer to the following question strictly in JSON format, '
                f'with no additional text or explanation. The JSON response should contain only two keys: '
                f'"method" and "content". The "method" key can have one of six values: "DirectAnswer", '
                f'"SearchEngine", "python", "SaveToDB", "RetrieveFromDB", or "AddToCalendar". The "content" key should '
                f'contain the corresponding output based on the method chosen. For "DirectAnswer", it should '
                f'be the factual answer to the question posed. For "SearchEngine", it should be the exact '
                f'search query you would use. For "python", it should be the Python code that would generate '
                f'the answer. For "SaveToDB", use this method in two cases: when the user provides important '
                f'information that should be saved for future sessions, or to summarize the content of the '
                f'current chat session for future reference. The "content" should be the note in natural language you wish to save '
                f'to the database. For "RetrieveFromDB", use this method when the user asks about or refers to '
                f'something from a previous session. The "content" should be the query in natural language used to retrieve '
                f'data from the database. For "AddToCalendar", use this method when the user wants to add an event to the calendar. '
                f'The "content" should be a JSON object with "event_content" and "event_datetime" keys, '
                f'where "event_datetime" should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). '
                f'Here is the question: {question}'
            )
        else:
            first_prompt = f'Please provide the answer to the following question strictly in JSON format, with no additional text or explanation. The JSON response should contain only two keys: "method" and "content". The "method" key can have one of four values: "DirectAnswer", "SearchEngine", "python", or "AddToCalendar". The "content" key should contain the corresponding output based on the method chosen. For "DirectAnswer", it should be the factual answer to the question posed. For "SearchEngine", it should be the exact search query you would use. For "python", it should be the Python code that would generate the answer. For "AddToCalendar", use this method when the user wants to add an event to the calendar. The "content" should be a JSON object with "event_content" and "event_datetime" keys, where "event_datetime" should be in ISO 8601 format (YYYY-MM-DDTHH:MM:SS). Here is the question: {question}'

        session['msg_history'].append({"role": "user", "content": first_prompt})

        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "mode": "instruct",
            "messages": session['msg_history']
        }
        response = requests.post(host, headers=headers, json=data, verify=False)
        print("request sent:", data)
        i = 0
        tool_used = ''
        while i < 5:
            print("=====================================")
            if response.status_code == 200:
                print("response with 200")
                answer = response.json()['choices'][0]['message']['content']
                print("answer:", answer)
                session['msg_history'].append({"role": "assistant", "content": answer})
                print("chat_history:", session['chat_history'])

                data = extract_json(answer)
                print("data:", data)
                if 'method' not in data or 'content' not in data:
                    return jsonify({'error': 'Invalid JSON format. Please provide the answer in the specified format.'}), 400
                elif data['method'] not in ['DirectAnswer', 'SearchEngine', 'python', 'SaveToDB', 'RetrieveFromDB', 'AddToCalendar']:
                    return jsonify({'error': 'Invalid method. Please choose one of the allowed methods.'}), 400
                elif data['method'] == 'DirectAnswer':
                    return jsonify({'answer': data['content'] + f' (Tool used: {tool_used} for the answer)'})
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
                    print("notes to save:", notes)
                    db.save_to_db(notes)
                    prompt = f'The chat history has been saved to the database. If you would like to follow up with a response based on this information, please provide a "DirectAnswer" in JSON format with the answer to the original question. If you would like to save additional information or perform another operation, please provide the corresponding JSON response with the "method" and "content" keys.'
                elif data['method'] == 'RetrieveFromDB':
                    tool_used += 'RetrieveFromDB '
                    query = data['content']
                    print("query to retrieve:", query)
                    output = db.query_db(query)
                    print("output from db:", output)
                    prompt = f'The information retrieved from the database is as follows: "{output}". Please review this information and determine if it sufficiently answers the original question. Respond in strict JSON format with two keys: "method" and "content". If the retrieved information is sufficient, use "DirectAnswer" for "method" and provide the answer in "content". If the information is not sufficient and you need to perform another operation, use the corresponding method for "method" and provide the necessary "content". No other text or explanation should be provided outside of the JSON response.'
                elif data['method'] == 'AddToCalendar':
                    tool_used += 'AddToCalendar '
                    content = data['content']
                    try:
                        if type(content) is str:
                            event_data = json.loads(content)
                        else:
                            event_data = content
                        print("event_data:", type(event_data), event_data)
                        event_content = event_data['event_content']
                        event_datetime_str = event_data['event_datetime']
                        event_datetime = parse_datetime(event_datetime_str)
                        db.add_calendar_event(event_content, event_datetime)
                        prompt = f'The event "{event_content}" has been added to the calendar on {event_datetime_str}. If you would like to follow up with a response, please provide a "DirectAnswer" in JSON format. No other text or explanation should be provided outside of the JSON response.'
                    except Exception as e:
                        print(f"Error parsing event data: {e}")
                        traceback.print_exc()
                        prompt = f'There was an error adding the event to the calendar. Please ensure the "content" contains a JSON object with "event_content" and "event_datetime" in ISO 8601 format. Respond in JSON format with a "DirectAnswer" explaining the error.'
                else:
                    print("Invalid method:", data['method'])
                i += 1
                print(f"Round {i} prompt: {prompt}")
                session['msg_history'].append({"role": "user", "content": prompt})
                data = {
                    "mode": "instruct",
                    "messages": session['msg_history']
                }
                response = requests.post(host, headers=headers, json=data, verify=False)
                print('------')
                print("response:", response)
                print('------')
            else:
                print("response with error")
                return jsonify({'error': 'Failed to fetch response from OpenAI'}), 500
    else:
        session['msg_history'].append({"role": "user", "content": question})

        headers = {
            "Content-Type": "application/json"
        }
        data = {
            "mode": "instruct",
            "messages": session['msg_history']
        }
        response = requests.post(host, headers=headers, json=data, verify=False)
        print("request sent:", data)

        if response.status_code == 200:
            print("response with 200")
            answer = response.json()['choices'][0]['message']['content']
            session['msg_history'].append({"role": "assistant", "content": answer})
            print("chat_history:", session['chat_history'])
            return jsonify({'answer': answer})
        else:
            print("response with error")
            return jsonify({'error': 'Failed to fetch response from OpenAI'}), 500

@app.route('/get_pending_messages', methods=['GET'])
def get_pending_messages():
    global pending_messages
    messages = pending_messages.copy()
    pending_messages.clear()
    # Append the messages to the session's message history
    if 'msg_history' not in session:
        session['msg_history'] = [system_prompt]
    for msg in messages:
        session['msg_history'].append(msg)
    return jsonify({'messages': messages})

def background_calendar_checker():
    global pending_reminders
    reminded_events = set()
    while True:
        try:
            # Get the current time and time 15 minutes from now
            now = datetime.now()
            reminder_time = now + timedelta(minutes=15)
            # Get events happening between now and reminder_time
            events = db.get_upcoming_events(now, reminder_time)
            print("events:",events)
            for event in events:
                event_id, event_content, event_datetime = event
                # Check if we have already reminded the user about this event
                if event_id not in reminded_events:
                    # Prompt the LLM to generate the reminder message
                    llm_prompt = f'You have an upcoming event: "{event_content}" at {event_datetime}. The current time is {now}. You usually remind the user 15 minutes in advance. Please generate a reminder message to send to the user. Respond in strict JSON format with one key: "content". And the content is the reminder message you want to send to the user.'
                    # Send this prompt to the LLM
                    headers = {
                        "Content-Type": "application/json"
                    }
                    data = {
                        "mode": "instruct",
                        "messages": [
                            {"role": "system", "content": system_prompt['content']},
                            {"role": "user", "content": llm_prompt}
                        ]
                    }
                    response = requests.post(host, headers=headers, json=data, verify=False)
                    if response.status_code == 200:
                        llm_response = response.json()['choices'][0]['message']['content']
                        llm_response = json.loads(llm_response)
                        llm_response = llm_response['content']
                        # Add the reminder message to the pending messages
                        pending_messages.append({"role": "assistant", "content": llm_response})
                        # Mark this event as reminded
                        reminded_events.add(event_id)
                    else:
                        print("Failed to get response from LLM for event reminder")
            # Sleep for 60 seconds
            time.sleep(20)
        except Exception as e:
            print(f"Error in background_calendar_checker: {e}")
            time.sleep(60)

if __name__ == '__main__':
    # Start the background thread
    threading.Thread(target=background_calendar_checker, daemon=True).start()
    app.run(host='0.0.0.0', port=8000, debug=False)
