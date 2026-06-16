Forked from https://github.com/ritun16/openai-compatible-fastapi

# 🚀 Building an OpenAI-Compatible API with Open-Source LLM: Rate-Limiting, Custom API Keys 🔐, and Streamlit Authentication 🌐

Welcome to the **OpenAI-Compatible API with Open-Source LLMs** repository! This project provides a comprehensive guide and implementation for building your own API service using open-source Large Language Models (LLMs). The API is designed to be compatible with the OpenAI API, and includes features such as **rate limiting**, **custom API keys** for authentication, and a **Streamlit-based** authentication system using local email and password.

---

## 🚀 Key Features

- **OpenAI-Compatible API**: Fully aligned with OpenAI’s `chat/completions` route for seamless integration.
- **Secure API Key Management**: Use the Streamlit app to create, manage, and delete API keys.
- **Rate Limiting**: Prevents abuse and ensures fair usage through a custom rate-limiting system.
- **Local Email Authentication**: Implements a simple email and password registration/login flow.
- **FastAPI for LLM Serving**: Serve open-source LLMs using `FastAPI`, with model serving by `vLLM` for efficient, paged attention mechanism.

---

## 📂 File Structure

- **.env**: Stores environment variables.
- **api_key_backend.py**: Manages API key creation, deletion, and database integration.
- **app.py**: Streamlit app for user login, logout, and API key management.
- **auths.py**: Implements email and password authentication, registration, and session management.
- **configs.py**: Configuration settings for the application, including database and API limits.
- **requirements.txt**: Python dependencies required to run the project.
- **serving.py**: FastAPI code to serve the LLM with support for paged attention mechanism.
- **testing_api.py**: To ensure the API functions as expected and compatible with OpenAI client.

---

## 🔧 Setup Instructions

### Prerequisites

- Python 3.9+
- Virtual environment

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/ritun16/openai-compatible-fastapi.git
   cd openai-compatible-fastapi
   ```
2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Up Environment Variables: Create a .env file in the root directory with the following keys**
   ```bash
   NGROK_AUTH_TOKEN=<ngrok_auth_token> # Optional
   ```
5. **Run the Streamlit App: Start the authentication and API key management app**
   ```bash
   streamlit run app.py
   ```
6. **Run the FastAPI Server: Start the LLM-serving API.**
   ```bash
   uvicorn serving:app --reload --port 8000
   ```
