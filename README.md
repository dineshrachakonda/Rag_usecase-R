# RAG Use Case

A local command-line retrieval-augmented generation (RAG) assistant for asking questions about company policy and other reference documents. It retrieves relevant document chunks from a Chroma vector store and uses a local Ollama model to generate answers with source references.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/) installed and running
- The Ollama models used by this project:
	- `qwen3:4b` for answer generation
	- `qwen3-embedding:0.6b` for document and query embeddings

Download the models once:

```powershell
ollama pull qwen3:4b
ollama pull qwen3-embedding:0.6b
```

## Setup

Create and activate a virtual environment, then install the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r req.txt
```

If PowerShell prevents activating the virtual environment, run the commands from Command Prompt instead:

```bat
py -m venv .venv
.venv\Scripts\activate.bat
python -m pip install -r req.txt
```

## Run

From the project root, run:

```powershell
python main.py
```

The program loads `documents/company_policy.docx`, creates document chunks and a local vector index in `chroma_db/`, then prompts for questions. Type `exit` to quit. Answers include the source document and, when available, its page number.

## Documents

The document loader supports PDF, DOCX, and TXT files. The current command-line app is configured to load `documents/company_policy.docx`; to use another file, change `DOCUMENT_PATH` in `main.py`.

The vector index is deleted and rebuilt each time the application starts. Keep the source document in place; `chroma_db/` is generated locally and does not need to be committed.

## Project Files

- `main.py` — command-line application and interactive question loop
- `rag.py` — document loading, chunking, vector storage, retrieval, and answer generation
- `documents/company_policy.docx` — sample knowledge-base document
- `req.txt` — Python package dependencies
"# Rag_usecase-R" 
