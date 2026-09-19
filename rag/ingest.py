from pathlib import Path
import pickle

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer


BASE_DIR = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_base"
INDEX_DIR = BASE_DIR / "rag"


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def load_documents():
    documents = []

    for file_path in KNOWLEDGE_DIR.glob("*.txt"):
        text = file_path.read_text(encoding="utf-8")

        chunks = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

        for chunk in chunks:
            documents.append(
                {
                    "text": chunk,
                    "source": file_path.name,
                }
            )

    return documents


def build_index():
    documents = load_documents()

    if not documents:
        raise ValueError("No knowledge-base documents were found.")

    model = SentenceTransformer(MODEL_NAME)

    texts = [doc["text"] for doc in documents]

    embeddings = model.encode(
        texts,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )

    embeddings = np.asarray(embeddings, dtype="float32")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Correct FAISS syntax
    faiss.write_index(index, str(INDEX_DIR / "faiss.index"))

    with open(INDEX_DIR / "documents.pkl", "wb") as file:
        pickle.dump(documents, file)

    print(f"Created FAISS index with {len(documents)} knowledge chunks.")


if __name__ == "__main__":
    build_index()