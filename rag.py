from pathlib import Path
import shutil

from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    TextLoader,
)

from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_ollama import (
    OllamaEmbeddings,
    ChatOllama,
)

from langchain_chroma import Chroma

from langchain_core.prompts import ChatPromptTemplate


# -----------------------------
# Configuration
# -----------------------------

DB_DIR = "./chroma_db"

EMBEDDING_MODEL = "qwen3-embedding:0.6b"

LLM_MODEL = "qwen3:4b"


# -----------------------------
# Load Document
# -----------------------------

def load_document(file_path):

    path = Path(file_path)

    extension = path.suffix.lower()

    if extension == ".pdf":

        loader = PyPDFLoader(str(path))

    elif extension == ".docx":

        loader = Docx2txtLoader(str(path))

    elif extension == ".txt":

        loader = TextLoader(
            str(path),
            encoding="utf-8"
        )

    else:

        raise ValueError(
            "Only PDF, DOCX and TXT files are supported."
        )

    documents = loader.load()

    if not documents:

        raise ValueError(
            "The document is empty."
        )

    return documents


# -----------------------------
# Split Document
# -----------------------------

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(

        chunk_size=800,

        chunk_overlap=120,

        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            ""
        ]
    )

    chunks = splitter.split_documents(documents)

    return chunks


# -----------------------------
# Create Vector Database
# -----------------------------

def build_vector_store(chunks):

    db_path = Path(DB_DIR)

    if db_path.exists():

        shutil.rmtree(db_path)

    embeddings = OllamaEmbeddings(

        model=EMBEDDING_MODEL
    )

    vector_store = Chroma(

        collection_name="incident_knowledge",

        embedding_function=embeddings,

        persist_directory=DB_DIR
    )

    vector_store.add_documents(chunks)

    return vector_store


# -----------------------------
# Open Existing Vector Database
# -----------------------------

def get_vector_store():

    embeddings = OllamaEmbeddings(

        model=EMBEDDING_MODEL
    )

    vector_store = Chroma(

        collection_name="incident_knowledge",

        embedding_function=embeddings,

        persist_directory=DB_DIR
    )

    return vector_store


# -----------------------------
# Prompt
# -----------------------------

def create_prompt():

    prompt = ChatPromptTemplate.from_messages(

        [

            (
                "system",

                """
You are an IT incident and troubleshooting assistant.

Answer the user's question using ONLY the
provided incident knowledge base.

Identify:

1. Problem
2. Possible Cause
3. Recommended Troubleshooting Steps

Do not invent information.

If the answer is not available in the
knowledge base, say:

"I could not find a relevant solution
in the incident knowledge base."

Keep the answer clear and practical.

Context:

{context}
"""
            ),

            (
                "human",

                "{question}"
            )

        ]
    )

    return prompt


# -----------------------------
# Ask Question
# -----------------------------

def answer_question(question):

    vector_store = get_vector_store()

    # Retrieve relevant chunks
    results = vector_store.similarity_search(

        question,

        k=4
    )

    if not results:

        return (
            "I could not find a relevant solution "
            "in the incident knowledge base.",
            []
        )

    context_parts = []

    sources = []

    for document in results:

        context_parts.append(
            document.page_content
        )

        source = Path(
            document.metadata.get(
                "source",
                "Unknown"
            )
        ).name

        page = document.metadata.get("page")

        if page is not None:

            source_name = (
                f"{source} "
                f"(page {page + 1})"
            )

        else:

            source_name = source

        if source_name not in sources:

            sources.append(source_name)

    context = "\n\n---\n\n".join(
        context_parts
    )

    # Create prompt
    prompt = create_prompt()

    messages = prompt.format_messages(

        context=context,

        question=question
    )

    # Ollama LLM
    llm = ChatOllama(

        model=LLM_MODEL,

        temperature=0
    )

    # Generate answer
    response = llm.invoke(messages)

    return response.content, sources