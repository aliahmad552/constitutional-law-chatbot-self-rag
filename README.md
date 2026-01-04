# 🧠 AI-Powered Constitutional Law Chatbot for Pakistan

**AI-Powered Constitutional Law Chatbot for Pakistan** is an advanced, multilingual chat application that enables users to interact with the **Constitution of Pakistan (1973)**—including its **Articles, Schedules, and Amendments**—in natural language.  
Built using a Retrieval-Augmented Generation (RAG) pipeline, this chatbot provides **source-grounded answers** backed by actual constitutional text, with real-time streaming and persistent conversational memory.

---

## 🚀 Project Overview

This project is part of the **Final Year Project (FYP)** for the **Bachelor of Science in Software Engineering** at **The Islamia University of Bahawalpur**, supervised by **Dr. Nadia Khan**.

The core idea is to leverage cutting-edge AI technology to make constitutional knowledge accessible and understandable to:

- **Law Students**
- **Lawyers**
- **General Public**
- **Researchers**

It supports **multilingual interaction** including:
🌐 English, Urdu, French, and Arabic.

---

## 📌 Features

### 🔹 AI-Driven Knowledge Retrieval
- Uses **Retrieval-Augmented Generation (RAG)** for accurate, context-aware responses.
- Embedding generation and semantic search using **HuggingFace Sentence Transformers**.
- Vector store powered by **Pinecone** for high-quality similarity matching.

### 🔹 Multilingual Support
- Query and response support for:
  - 🇬🇧 English
  - 🇵🇰 Urdu
  - 🇫🇷 French
  - 🇸🇦 Arabic

### 🔹 Real-Time Streaming
- FastAPI backend with **WebSocket support** for streaming answers as they are generated.

### 🔹 Persistent Memory & Chat History
- **Long-term conversational memory** for each registered user.
- Users can **view or delete their chat history**.
- Memory saves context to improve future responses.

### 🔹 Authentication & Access Control
- User roles:
  - 👤 **Guest**
  - ✅ **Registered User**
  - 🛠 **Admin**
- Admin dashboard includes system monitoring and logs access.

### 🔹 Observability & Monitoring
- Integrated with **LangSmith** for trace and observability management.

### 🔹 Legal Safety & Disclaimer
- All answers are **informational only**, not legal advice.
- Responses are grounded directly in constitutional text with source traceability.

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI |
| Frontend | HTML/CSS/JavaScript |
| Real-Time | WebSockets |
| Vector Database | Pinecone |
| Embeddings | HuggingFace Sentence Transformers |
| LLM Integration | OpenAI (ChatOpenAI model) |
| Persistence DB | PostgreSQL (chat + memory) |
| Auth DB | MySQL (user accounts) |
| Monitoring | LangSmith |
| Deployment | Docker |

---

## 📁 Repository Structure
```bash
constitutional_chatbot/
│
├── src/
│   ├── __init__.py
│   └── helper.py             # RAG agent creation
│
├── research/
│   └── trials.py             # trials notebook jupyter
│
├── src/
│   └── prompt.py             # System prompts
│
├── data/
│   └── constitutional.pdf    # knowledge base
│
├── static/                   # Frontend assets
├── templates/                # HTML templates
│
├── app.py                    # FastAPI applicatio                  
├── Dockerfile                # Docker file
├── setup.py                  # Readme.md
├── template.sh               # Text chunking
├── vector_store.py           # Pinecone integration
├── store_index.py            # Embedding model
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables
└── README.md                 # This file
```


## 🧠 How It Works

1. **Document Processing**
   - PDFs of the Constitution are cleaned and split using a recursive text splitter.
   - Text chunks are embedded and stored in Pinecone.

2. **User Query Submission**
   - Query sent to FastAPI backend via WebSocket.
   - Backend generates embeddings and does a semantic similarity search.

3. **Context Retrieval & Response Generation**
   - Relevant chunks are retrieved.
   - AI model (ChatOpenAI) generates a response grounded on the retrieved text.

4. **Real-Time Response Streaming**
   - Backend streams answers through WebSockets.
   - Conversations are saved in PostgreSQL with memory context.

---

## 🧪 Setup & Installation

## 1️⃣ Clone the Repository

```bash
git clone https://github.com/aliahmad552/constitutional-law-chatbot.git
cd constitutional-law-chatbot
```
## 2️⃣ Create & Activate Virtual Environment
```bash
Copy code
python -m venv venv
source venv/bin/activate
```
## 3️⃣ Install Dependencies
```bash
Copy code
pip install -r requirements.txt
```
## 4️⃣ Environment Setup
Copy .env.example to .env and set:

ini
## Copy code
```bash
OPENAI_API_KEY=your_openai_key
PINECONE_API_KEY=your_pinecone_key
MY_SQL_URL=your_mysql_connection
POSTGRES_URL=your_postgresql_connection
LANGSMITH_KEY=your_langsmith_key
```
## 5️⃣ Build Vector Index
```bash
Copy code
python store_index.py
```
## 6️⃣ Run the Backend
```bash
Copy code
uvicorn app:app --reload
```
## 7️⃣ Open the Frontend
Go to:

arduino
Copy code
http://localhost:8000
## 🚧 Admin Dashboard
Admins can:

Review logs

Observe AI traces

Monitor usage metrics

## 👤 Admin access requires set credentials in MySQL.

### 📜 Disclaimer
⚖️ This chatbot provides educational and informational information only.
It does not replace professional legal advice and should not be used when legal judgment is required.

## 🧾 Related Work
There are similar AI legal assistants worldwide, including:

LawGPT: an AI model designed to answer legal questions in the context of Pakistani law. 
GitHub

## ❤️ Contributing
Contributions are welcome!
Please raise issues, submit PRs, or suggest improvements.

## 📄 License
This project is licensed under the Apache-2.0 License.

## 👨‍💻 Author

**Ali Ahmad**

- GitHub: https://github.com/aliahmad552
- LinkedIn: https://www.linkedin.com/in/ali-ahmad-dawana
- Email: aliahmaddawana@gmail.com
