# DrNiceFellow's Virtual Assistant System

![Screenshot](/assets/screenshot.png)

This is a virtual assistant platform developed by Dr. Nicefellow. It provides a user-friendly interface for interacting with an AI assistant that can execute various tasks beyond simple chatting. Powered by OpenAI API and designed for seamless tool integration, this system supports functions such as Python code execution, web searches, event management, and Retrieval-Augmented Generation (RAG).

## Features

- User-friendly chat interface
- Backend engine powered by OpenAI API
- Multi-tool support, including:
  - Python interpreter for code execution
  - Search engine for real-time data retrieval
  - Calendar management for events and reminders
- RAG (Retrieval-Augmented Generation) for context-aware and persistent conversations
- PostgreSQL integration for saving important chat data and enabling future retrieval
- Automatic calendar updates and reminders

## Calendar Features

- Create events: The assistant can create new calendar events based on user requests.
- Event reminders: It can remind users of upcoming events.
- View upcoming events: Displays events for the next 7 days.
- Auto-refresh: The calendar updates automatically after each chat interaction.

## Requirements

- Python
- Flask
- Flask-session
- YAML

## Installation

1. Clone the repository
2. Start the backend server and obtain the API key and host address.
3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```
4. Optional: Install additional dependencies for RAG support:
   ```
   pip install -r requirements_rag.txt
   ```
5. Create a `config.yml` file from the provided `example.config.yml` and set the OpenAI API key.
6. Run the application:
   ```
   python app.py
   ```

## Database Setup

Before using the platform, prepare the PostgreSQL database:

1. Start the PostgreSQL service:
   ```
   service postgresql start
   ```
2. Switch to the `postgres` user:
   ```
   su - postgres
   ```
3. Access PostgreSQL:
   ```
   psql
   ```
4. Create a new user and database:
   ```sql
   CREATE USER chatbot WITH PASSWORD 'password';
   ALTER ROLE chatbot SUPERUSER;
   CREATE DATABASE chatbot;
   ```

## Usage

Once the server is running, open a web browser and navigate to `http://localhost:7860`. You can start interacting with the virtual assistant by typing commands or questions into the chat.

### Calendar Interaction

Users can interact with the assistant's calendar features through natural language commands, such as:

- "Set up a meeting with John on Friday at 2 PM."
- "Remind me to call Mom tomorrow at 6 PM."
- "What events do I have this week?"

The assistant will update the calendar and display the upcoming events for the next 7 days.

## Tool Integration

This platform offers:

- **Python Interpreter**: The assistant can execute Python code and return the results.
- **Search Engine**: Automatically retrieves relevant information from the web based on user queries.

## RAG and PostgreSQL Integration

The virtual assistant leverages RAG (Retrieval-Augmented Generation) to improve context-aware responses by storing key information in a PostgreSQL database. This allows the assistant to recall prior chats and provide more relevant, persistent interactions.

To enable this, configure your PostgreSQL database settings in the `config.yml` file. Ensure you provide details such as database name, user, password, host, and port.

## Database Visualization

To visualize the database, consider using a tool like [pgweb](https://github.com/sosedoff/pgweb):

```bash
./pgweb_linux_amd64  --bind=0.0.0.0 --listen=7861 --url="postgresql://chatbot:password@localhost:5432/chatbot"
```

## Future Plans

- [x] Add support for multiple chat formats
- [x] Add function calling capabilities
- [x] Implement full RAG support

## Disclaimer

This project is intended for personal use. Because the assistant can execute Python code, be aware of the potential security risks involved. Users should exercise caution when interacting with the assistant, particularly when running code. The developers take no responsibility for any damages or security breaches arising from the use of this software.

## License

This project is licensed under the Apache 2.0 License.

## Discord Community

Join our Discord server [here](https://discord.gg/xhcBDEM3) to ask questions, share feedback, and contribute to the project.

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.
