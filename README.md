# DrNiceFellow's Chat WebUI

![Screenshot](/assets/screenshot.png)

This is a chat WebUI developed by Dr. Nicefellow. It is designed to provide a user-friendly interface for interacting with a chatbot. The backend engine is powered by OpenAI API, and the backend LLM should support chat template. It is tested with OpenAI API extension of text-generation-web-ui.

## Features

- User-friendly chat interface
- Backend engine powered by OpenAI API
- Tool usage support for Python interpreter and search engine
- RAG (Retrieval-Augmented Generation) support
- Calendar integration with event management and reminders

## Calendar Features

- Set up events: The assistant can create new calendar events based on user requests.
- Reminders: The system can remind users of upcoming events.
- Display upcoming events: The web interface shows events for the next 7 days.
- Update calendar: The calendar automatically refreshes after each chat interaction.

## Requirements

- Python
- Flask
- Flask-session
- YAML

## Installation

1. Clone the repository
2. Start the backend server and obtain the API key and host address.
3. Install the required packages using pip. 
   ```
   pip install -r requirements.txt
   ```
4. Optional: Install the required packages for RAG support using pip.
   ```
   pip install -r requirements_rag.txt
   ```
5. Create a `config.yml` file with the example example.config.yml and set the OpenAI API key.
6. Set your OpenAI API key in the `config.yml` file
7. Run the application:
   ```
   python app.py
   ```

## Database Preparation

Before running the application, you need to prepare the PostgreSQL database. Follow these steps:

1. Start the PostgreSQL service:
   ```
   service postgresql start
   ```
2. Switch to the `postgres` user:
   ```
   su - postgres
   ```
3. Enter the PostgreSQL command line:
   ```
   psql
   ```
4. Create a new user named `chatbot` with the password `password`:
   ```
   CREATE USER chatbot WITH PASSWORD 'password';
   ```
5. Grant superuser privileges to the `chatbot` user:
   ```
   ALTER ROLE chatbot SUPERUSER;
   ```
6. Create a new database named `chatbot`:
   ```
   CREATE DATABASE chatbot;
   ```

After these steps, your PostgreSQL database is ready for the application.

## Usage

Open your web browser and navigate to `http://localhost:7860`. You can start chatting with the bot by typing your message in the chat input field and pressing the "Send" button.

### Calendar Interaction

You can interact with the calendar feature through natural language commands in the chat. For example:

- "Set up a meeting with John on Friday at 2 PM"
- "Remind me to call Mom tomorrow at 6 PM"
- "What events do I have this week?"

The assistant will interpret these commands and update the calendar accordingly. The upcoming events for the next 7 days will be displayed on the web interface, automatically updating after each interaction.

## Tool Usage

This project supports the use of the Python interpreter and search engine. The Python interpreter is used for executing Python code, while the search engine is used for retrieving web data based on automatically generated search terms.

## RAG and PostgreSQL Integration

The software now includes a feature for automatic saving of important chat information to a PostgreSQL database using the RAG (Retrieval-Augmented Generation) model. This information can be automatically fetched for future chats, enhancing the chatbot's ability to provide context-aware responses abd achieving a persistent chatbot.

To use this feature, you need to provide the necessary database configuration in the `config.yml` file. The required parameters include the database name, host, password, port, user, and table name.

Please note that this feature requires additional dependencies. These dependencies are listed in the `requirements_rag.txt` file.

## Database Visualization

To visualize the database, I recommend using a tool like [pgweb](https://github.com/sosedoff/pgweb). Below is a command to use it:
    
    ```bash
    ./pgweb_linux_amd64  --bind=0.0.0.0 --listen=7861 --url="postgresql://chatbot:password@localhost:5432/chatbot"
    
    ```

## TODO

- [x] Add support for other chat formats
- [x] Add function calling
- [x] Add RAG support

## Disclaimer

This project is intended for personal use. Given that this chatbot has the ability to write Python code, it's important to be aware of potential security risks. Users should be cautious when interacting with the bot, especially when executing generated code. The bot's code generation capability could potentially be exploited by malicious users to execute harmful commands or scripts. Users should use this project at their own risk. The developers of this project will not be responsible for any damage or issues that may arise from using this project.

## License

This project is licensed under the terms of the Apache 2.0 License.

## Discord Server

Join our Discord server [here](https://discord.gg/xhcBDEM3).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.