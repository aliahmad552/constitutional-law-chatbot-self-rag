from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

import uuid
import asyncio
import sqlite3

from src.helper import rag_app

app = FastAPI()

# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================================================
# SQLITE
# =========================================================

DB_PATH = "chat_threads.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS threads(
        thread_id TEXT PRIMARY KEY,
        title TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS messages(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT,
        role TEXT,
        content TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


init_db()

# =========================================================
# DB HELPERS
# =========================================================


def create_thread_if_not_exists(thread_id: str, first_message: str):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        "SELECT thread_id FROM threads WHERE thread_id=?",
        (thread_id,)
    )

    exists = cur.fetchone()

    if not exists:
        title = first_message[:50]

        cur.execute(
            """
            INSERT INTO threads(thread_id,title)
            VALUES(?,?)
            """,
            (thread_id, title)
        )

    conn.commit()
    conn.close()

@app.post("/login")
async def login(user: dict):
    return {"message": "Login successful"}

@app.post("/register")
async def register(user: dict):
    return {"message": "User registered"}


def save_message(
    thread_id: str,
    role: str,
    content: str
):
    conn = sqlite3.connect(DB_PATH)

    conn.execute(
        """
        INSERT INTO messages(
            thread_id,
            role,
            content
        )
        VALUES(?,?,?)
        """,
        (thread_id, role, content)
    )

    conn.commit()
    conn.close()


def get_threads():
    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        SELECT thread_id,title,created_at
        FROM threads
        ORDER BY created_at DESC
    """)

    rows = cur.fetchall()

    conn.close()

    return [
        {
            "thread_id": r[0],
            "title": r[1],
            "created_at": r[2]
        }
        for r in rows
    ]


def get_messages(thread_id: str):
    conn = sqlite3.connect(DB_PATH)

    cur = conn.cursor()

    cur.execute("""
        SELECT role,content
        FROM messages
        WHERE thread_id=?
        ORDER BY id ASC
    """, (thread_id,))

    rows = cur.fetchall()

    conn.close()

    return [
        {
            "role": r[0],
            "content": r[1]
        }
        for r in rows
    ]


# =========================================================
# REST APIs
# =========================================================

@app.get("/")
def root():
    return {"status": "running"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/threads")
def list_threads():
    return {
        "threads": get_threads()
    }


@app.get("/threads/{thread_id}")
def thread_history(thread_id: str):
    return {
        "thread_id": thread_id,
        "messages": get_messages(thread_id)
    }


# =========================================================
# CHATGPT STYLE STREAM
# =========================================================

async def stream_response(
    ws: WebSocket,
    answer: str
):
    """
    Sends ONE token/character at a time.

    Frontend appends content.
    No duplication issue.
    """

    for ch in answer:

        await ws.send_json({
            "type": "token",
            "content": ch
        })

        await asyncio.sleep(0.005)


# =========================================================
# WEBSOCKET
# =========================================================

@app.websocket("/ws/chat")
async def websocket_chat(ws: WebSocket):

    await ws.accept()

    try:

        while True:

            payload = await ws.receive_json()

            user_msg = payload.get("message", "").strip()

            thread_id = payload.get("thread_id")

            if not user_msg:
                continue

            # =====================================
            # NEW CHAT
            # =====================================

            if not thread_id:
                thread_id = str(uuid.uuid4())

            create_thread_if_not_exists(
                thread_id,
                user_msg
            )

            save_message(
                thread_id,
                "user",
                user_msg
            )

            # =====================================
            # SEND THREAD ID
            # =====================================

            await ws.send_json({
                "type": "thread_id",
                "thread_id": thread_id
            })

            # =====================================
            # LANGGRAPH CONFIG
            # =====================================

            config = {
                "configurable": {
                    "thread_id": thread_id
                }
            }

            state = {
                "question": user_msg,

                "retrieval_query": "",
                "rewrite_tries": 0,

                "docs": [],
                "relevant_docs": [],

                "context": "",
                "answer": "",

                "need_retrieval": False,

                "issup": "no_support",
                "evidence": [],

                "retries": 0,

                "isuse": "not_useful",
                "use_reason": ""
            }

            # =====================================
            # EXECUTE GRAPH
            # =====================================

            result = rag_app.invoke(
                state,
                config=config
            )

            final_answer = result.get(
                "answer",
                "No answer generated."
            )

            # =====================================
            # SAVE BOT RESPONSE
            # =====================================

            save_message(
                thread_id,
                "assistant",
                final_answer
            )

            # =====================================
            # STREAM ANSWER
            # =====================================

            await stream_response(
                ws,
                final_answer
            )

            # =====================================
            # END EVENT
            # =====================================

            await ws.send_json({
                "type": "end",
                "thread_id": thread_id
            })

    except WebSocketDisconnect:
        print("Client disconnected")

    except Exception as e:

        print("ERROR:", str(e))

        try:

            await ws.send_json({
                "type": "error",
                "message": str(e)
            })

        except:
            pass