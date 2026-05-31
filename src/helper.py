from typing import List, Literal
import os
from dotenv import load_dotenv
import sqlite3

from langchain_core.documents import Document
from langchain_core.output_parsers import PydanticOutputParser

from langchain_huggingface import (
    HuggingFaceEmbeddings,
    ChatHuggingFace,
    HuggingFaceEndpoint,
)

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.sqlite import SqliteSaver

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore

from src.state import State
from src.schema import RetrieveDecision, RelevanceDecision
from src.prompt import (
    decide_retrieval_prompt,
    direct_generation_prompt,
    is_relevant_prompt,
    rag_generation_prompt,
)

load_dotenv()

# =========================================================
# EMBEDDINGS
# =========================================================
embedding = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# =========================================================
# PINECONE
# =========================================================
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_name = "my-index-v2"

vc = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embedding,
)

retriever = vc.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 4},
)

# =========================================================
# LLM (NO STREAM HERE → prevents duplication bug)
# =========================================================
llm = ChatHuggingFace(
    llm=HuggingFaceEndpoint(
        repo_id="Qwen/Qwen2.5-72B-Instruct",
        temperature=0.0,
        max_new_tokens=1024,
    )
)

# =========================================================
# STRUCTURED OUTPUT HELPER
# =========================================================
def invoke_structured(prompt, parser, **kwargs):
    format_instructions = parser.get_format_instructions()
    messages = prompt.format_messages(**kwargs)

    messages[0].content += (
        "\n\nReturn ONLY valid JSON.\n\n" + format_instructions
    )

    response = llm.invoke(messages)
    return parser.parse(response.content)


# =========================================================
# 1. DECIDE RETRIEVAL
# =========================================================
retrieve_parser = PydanticOutputParser(
    pydantic_object=RetrieveDecision
)

def decide_retrieval(state: State):
    decision = invoke_structured(
        decide_retrieval_prompt,
        retrieve_parser,
        question=state["question"],
    )

    return {"need_retrieval": decision.should_retrieve}


def route_after_decide(state: State) -> Literal["direct", "retrieve"]:
    return "retrieve" if state.get("need_retrieval") else "direct"


# =========================================================
# 2. DIRECT ANSWER
# =========================================================
def generate_direct(state: State):
    out = llm.invoke(
        direct_generation_prompt.format_messages(
            question=state["question"]
        )
    )

    return {"answer": out.content}


# =========================================================
# 3. RETRIEVE
# =========================================================
def retrieve(state: State):
    query = state.get("retrieval_query") or state["question"]
    docs = retriever.invoke(query)

    return {"docs": docs}


# =========================================================
# 4. RELEVANCE FILTER
# =========================================================
relevance_parser = PydanticOutputParser(
    pydantic_object=RelevanceDecision
)

def is_relevant(state: State):
    relevant_docs = []

    for doc in state.get("docs", []):
        decision = invoke_structured(
            is_relevant_prompt,
            relevance_parser,
            question=state["question"],
            document=doc.page_content,
        )

        if decision.is_relevant:
            relevant_docs.append(doc)

    return {"relevant_docs": relevant_docs}


def route_after_relevance(state: State) -> Literal["generate", "no_answer"]:
    if state.get("relevant_docs"):
        return "generate"
    return "no_answer"


# =========================================================
# 5. GENERATE FROM CONTEXT
# =========================================================
def generate_from_context(state: State):
    context = "\n\n---\n\n".join(
        d.page_content for d in state.get("relevant_docs", [])
    ).strip()

    if not context:
        return {
            "answer": "Not found in provided documents.",
            "context": "",
        }

    out = llm.invoke(
        rag_generation_prompt.format_messages(
            question=state["question"],
            context=context,
        )
    )

    return {
        "answer": out.content,
        "context": context,
    }


# =========================================================
# 6. NO ANSWER
# =========================================================
def no_answer_found(state: State):
    return {
        "answer": "No relevant information found.",
        "context": "",
    }


# =========================================================
# GRAPH BUILD
# =========================================================
g = StateGraph(State)

g.add_node("decide_retrieval", decide_retrieval)
g.add_node("generate_direct", generate_direct)
g.add_node("retrieve", retrieve)
g.add_node("is_relevant", is_relevant)
g.add_node("generate_from_context", generate_from_context)
g.add_node("no_answer_found", no_answer_found)

# FLOW
g.add_edge(START, "decide_retrieval")

g.add_conditional_edges(
    "decide_retrieval",
    route_after_decide,
    {
        "direct": "generate_direct",
        "retrieve": "retrieve",
    },
)

g.add_edge("generate_direct", END)

g.add_edge("retrieve", "is_relevant")

g.add_conditional_edges(
    "is_relevant",
    route_after_relevance,
    {
        "generate": "generate_from_context",
        "no_answer": "no_answer_found",
    },
)

g.add_edge("generate_from_context", END)
g.add_edge("no_answer_found", END)


# =========================================================
# MEMORY (SQLite persistence)
# =========================================================
conn = sqlite3.connect(
    "chatbot_memory.db",
    check_same_thread=False
)

memory = SqliteSaver(conn)

rag_app = g.compile(
    checkpointer=memory
)