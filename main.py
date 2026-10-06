from pathlib import Path

from rag import (
    load_document,
    split_documents,
    build_vector_store,
    answer_question,
)

DOCUMENT_PATH = Path("documents/company_policy.docx")


def main():
    print("=" * 60)
    print("   Ask your Ml questions")
    print("=" * 60)

    document_path = Path(DOCUMENT_PATH)

    if not document_path.exists():
        print(f"\nDocument not found: {DOCUMENT_PATH}")
        return

    print("\n[1/3] Loading document...")

    documents = load_document(str(document_path))

    print(f"Loaded {len(documents)} document section(s).")

    print("\n[2/3] Creating chunks and vector database...")

    chunks = split_documents(documents)

    print(f"Created {len(chunks)} chunks.")

    build_vector_store(chunks)

    print("\n[3/3] RAG system is ready!")

    print("\n" + "=" * 60)
    print("Ask your question?.")
    print("Type 'exit' to stop.")
    print("=" * 60)

    while True:

        question = input("\nYou: ").strip()

        if question.lower() == "exit":
            print("\nGoodbye!")
            break

        if not question:
            print("Please enter a question.")
            continue

        try:
            print("\nSearching knowledge base...")

            answer, sources = answer_question(question)

            print("\nAI Assistant:")
            print("-" * 60)
            print(answer)

            print("\nSources:")
            for source in sources:
                print(f"  - {source}")

        except Exception as error:
            print(f"\nError: {error}")


if __name__ == "__main__":
    main()