# DrNiceFellow's Simple Chat WebUI

![Screenshot](/assets/screenshot.png)

This is a simple chat WebUI developed by Dr. Nicefellow. It is designed to provide a user-friendly interface for interacting with a chatbot. The backend engine is powered by OpenAI API, and the backend LLM should support chat template. It is tested with OpenAI API extension of text-generation-web-ui.

## Features

- User-friendly chat interface
- Backend engine powered by OpenAI API
- Tool usage support for Python interpreter and search engine and RAG

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

## Usage

Open your web browser and navigate to `http://localhost:7860`. You can start chatting with the bot by typing your message in the chat input field and pressing the "Send" button.


## Tool Usage

This project supports the use of the Python interpreter and search engine. The Python interpreter is used for executing Python code, while the search engine is used for retrieving web data based on automatically generated search terms.

To update the `README.md` file, you can add a new section that describes the RAG feature and its interaction with the PostgreSQL database. Here's a suggestion:

## RAG and PostgreSQL Integration

The software now includes a feature for automatic saving of important chat information to a PostgreSQL database using the RAG (Retrieval-Augmented Generation) model. This information can be automatically fetched for future chats, enhancing the chatbot's ability to provide context-aware responses abd achieving a persistent chatbot.

To use this feature, you need to provide the necessary database configuration in the `config.yml` file. The required parameters include the database name, host, password, port, user, and table name.

Please note that this feature requires additional dependencies. These dependencies are listed in the `requirements_rag.txt` file.


For the `requirements_rag.txt` file, you can list the dependencies as follows:

```plaintext
psycopg2-binary==2.9.1
llama_index==0.1.0
```

Please note that the versions of the dependencies are hypothetical and you should use the versions that are compatible with your project.

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