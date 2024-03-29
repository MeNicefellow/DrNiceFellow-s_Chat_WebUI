# DrNiceFellow's Simple Chat WebUI

![Screenshot](/assets/screenshot.png)

This is a simple chat WebUI developed by Dr. Nicefellow. It is designed to provide a user-friendly interface for interacting with a chatbot. The backend engine is powered by OpenAI API, and the backend LLM should support the Llama Chat/Mistral Instruct prompt template. It is tested with OpenAI API extension of text-generation-web-ui.

## Features

- User-friendly chat interface
- Backend engine powered by OpenAI API
- Support for Llama Chat/Mistral Instruct prompt template
- Tool usage support for Python interpreter and search engine

## Requirements

- Python
- Flask
- Flask-session
- YAML

## Installation

1. Clone the repository
2. Start the backend server and obtain the API key and host address.
2. Install the required packages using pip.
3. Create a `config.yml` file with the example example.config.yml and set the OpenAI API key.
4. Set your OpenAI API key in the `config.yml` file
5. Run the application:
   ```
   python app.py
   ```

## Usage

Open your web browser and navigate to `http://localhost:7860`. You can start chatting with the bot by typing your message in the chat input field and pressing the "Send" button.


## Tool Usage

This project supports the use of the Python interpreter and search engine. The Python interpreter is used for executing Python code, while the search engine is used for retrieving web data based on automatically generated search terms.

## TODO

- [x] Add support for other chat formats
- [x] Add function calling
- [ ] Add RAG support

## Disclaimer

This project is intended for personal use. It may contain vulnerabilities and security concerns. Users should use this project at their own risk. The developers of this project will not be responsible for any damage or issues that may arise from using this project.

## License

This project is licensed under the terms of the Apache 2.0 License.

## Discord Server

Join our Discord server [here](https://discord.gg/xhcBDEM3).

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.