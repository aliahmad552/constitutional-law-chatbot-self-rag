from dotenv import load_dotenv
import os
from src.helper import load_pdf_files, download_embeddings, text_split, filter_to_minimal_docs
from pinecone import Pinecone
from pinecone import ServerlessSpec
from langchain_pinecone import PineconeVectorStore

load_dotenv()

extracted_docs = load_pdf_files('data')
filtered_docs = filter_to_minimal_docs(extracted_docs)
text_chunk = text_split(filtered_docs)
embedding = download_embeddings()

# Get API key
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
os.environ['PINECONE_API_KEY']=PINECONE_API_KEY

pinecone_api_key = PINECONE_API_KEY
pc = Pinecone(api_key=pinecone_api_key)
print(pinecone_api_key)
index_name='my-index-v1'
if not pc.has_index(index_name):
    pc.create_index(
        dimension=384,
        name = index_name,
        metric='cosine',
        spec=ServerlessSpec(cloud='aws',region='us-east-1')
    )

index = pc.Index(index_name)

vc = PineconeVectorStore.from_documents(
    text_chunk,
    index_name=index_name,
    embedding=embedding
)

