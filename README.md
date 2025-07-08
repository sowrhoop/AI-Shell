# OpenAI CLI Chat Application

A simple and elegant command-line interface (CLI) application built with Python that allows you to interact with OpenAI's powerful language models (like gpt-3.5-turbo).

## Table of Contents

-   [Features](#features)
-   [Prerequisites](#prerequisites)
-   [Installation](#installation)
-   [API Key Setup](#api-key-setup)
-   [Usage](#usage)
-   [Converting to a Standalone Executable (.exe)](#converting-to-a-standalone-executable-exe)
-   [Error Handling](#error-handling)
-   [Future Development](#future-development)
-   [Author](#author)
-   [License](#license)

## Features

* **Interactive Chat:** Engage in continuous conversations with the AI model directly from your terminal.
* **OpenAI Integration:** Utilizes the official OpenAI Python library.
* **Simple Interface:** Clean and straightforward command-line interaction.
* **Error Handling:** Basic error management for API issues or missing configurations.
* **Executable Ready:** Can be easily converted into a standalone `.exe` file for Windows users.

## Prerequisites

Before you begin, ensure you have the following installed on your Windows system:

* **Python 3.8+:** You can download it from [python.org](https://www.python.org/downloads/windows/). Make sure to check "Add Python to PATH" during installation.
* **pip:** Python's package installer (usually comes with Python).

## Installation

1.  **Clone the repository (or download the script):**

    If you're using Git:
    ```bash
    git clone [https://github.com/sowrhoop/AI-Shell.git](https://github.com/sowrhoop/AI-Shell.git)
    cd AI-Shell
    ```

    If you're just downloading the script, save the Python code in a folder of your choice.

2.  **Create a Virtual Environment (Recommended):**
    Create a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **Command Prompt:**
        ```bash
        .\venv\Scripts\activate
        ```
    * **PowerShell:**
        ```bash
        .\venv\Scripts\Activate.ps1
        ```

4.  **Install Dependencies:**
    ```bash
    pip install openai
    ```

## API Key Setup

**This is a crucial step!** The application requires your OpenAI API key to function. For security, it's highly recommended to set it as an environment variable rather than embedding it directly in the code.

1.  **Obtain your OpenAI API Key:**
    * Go to the [OpenAI Platform](https://platform.openai.com/).
    * Sign up or log in.
    * Navigate to "API keys" (usually under your user icon or in the left sidebar).
    * Click "Create new secret key" and **copy the key immediately**. You won't see it again.

2.  **Set the API Key as an Environment Variable (Windows):**
    Open **Command Prompt as an Administrator** and run the following command. Replace `"your_openai_api_key_here"` with the actual key you copied.

    ```cmd
    setx OPENAI_API_KEY "your_openai_api_key_here"
    ```
    After running this, close the current Command Prompt/PowerShell window and open a new one for the change to take effect.

    You can verify it by typing `echo %OPENAI_API_KEY%` in a new Command Prompt.

## Usage

### Running the Python Script for other Operating Systems(Linux, Mac OS):

1.  Ensure your virtual environment is activated (if you created one).
2.  Navigate to the directory containing `AI-Shell.py`.
3.  Run the script:
    ```bash
    python AI-Shell.py
    ```
4.  The application will prompt you to "Enter your prompt:". Type your question or statement and press `Enter`.
5.  To exit the application, type `exit` and press `Enter`.

## Converting to a Standalone Executable (.exe)

You can convert this Python script into a single executable file for Windows using `PyInstaller`. This allows users to run the application without installing Python or its dependencies.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```

2.  **Generate the .exe:**
    Navigate to the directory containing `AI-Shell.py` in your Command Prompt/PowerShell (with the virtual environment activated or PyInstaller installed globally), and run:
    ```bash
    pyinstaller --onefile AI-Shell.py
    ```
    This will create a `dist` folder in your current directory.

3.  **Run the .exe:**
    Inside the `dist` folder, you will find `AI-Shell.exe`. You can double-click it or run it from the command line.

    **Note:** Users running the `.exe` will still need to have the `OPENAI_API_KEY` environment variable set on their system.

## Error Handling

* **`Error initializing OpenAI client: ...`**: This usually means your `OPENAI_API_KEY` environment variable is not set correctly or is missing. Please review the [API Key Setup](#api-key-setup) section.
* **`An error occurred: ...`**: This could indicate a network issue preventing connection to OpenAI, a problem with your API key (e.g., expired or invalid during a call), or an issue with the request itself.
* **Model Name:** The code currently uses `model="gpt-3.5-turbo"`.

---

## Future Development

This project is planned for continuous improvement! Future features may include:

* **Model Selection:** Allow users to choose different OpenAI models directly from the command line.
* **Conversation History:** Implement saving and loading of chat history.
* **Improved Error Messages:** More detailed and user-friendly error feedback.
* **Configuration File:** Option to manage settings (like default model, temperature) via a configuration file.

## Author

**Sowrhoop Raaj B**

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)**. See the [LICENSE](LICENSE) file for more details.
