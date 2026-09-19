from pathlib import Path
import pickle

import faiss
from sentence_transformers import SentenceTransformer


# --------------------------------------------------
# PATH CONFIGURATION
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE_DIR / "rag"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


# --------------------------------------------------
# RETRIEVER CLASS
# --------------------------------------------------

class Retriever:

    def __init__(self):

        index_path = INDEX_DIR / "faiss.index"
        documents_path = INDEX_DIR / "documents.pkl"

        if not index_path.exists():
            raise FileNotFoundError(
                f"FAISS index not found: {index_path}\n"
                "Run rag/ingest.py first."
            )

        if not documents_path.exists():
            raise FileNotFoundError(
                f"Documents file not found: {documents_path}\n"
                "Run rag/ingest.py first."
            )

        print("Loading FAISS index...")

        self.index = faiss.read_index(str(index_path))

        print("Loading documents...")

        with open(documents_path, "rb") as file:
            self.documents = pickle.load(file)

        print("Loading embedding model...")

        self.model = SentenceTransformer(MODEL_NAME)

        print("Retriever initialized successfully.")
        print(f"Documents available: {len(self.documents)}")


    # --------------------------------------------------
    # SEARCH
    # --------------------------------------------------

    def search(self, query, top_k=3):

        if not query or not query.strip():
            return []

        # Make sure top_k does not exceed document count
        top_k = min(top_k, len(self.documents))

        print("\n" + "=" * 60)
        print("RAG QUERY:")
        print(query)
        print("=" * 60)

        # Create embedding for current user query
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            normalize_embeddings=True
        )

        # Search FAISS
        scores, indices = self.index.search(
            query_embedding,
            top_k
        )

        results = []

        print("\nRetrieved documents:")

        for rank, (score, index) in enumerate(
            zip(scores[0], indices[0]),
            start=1
        ):

            if index == -1:
                continue

            document = self.documents[index]

            result = {
                "rank": rank,
                "text": document.get("text", ""),
                "source": document.get("source", "Unknown"),
                "score": float(score)
            }

            results.append(result)

            print(
                f"\n#{rank}"
                f"\nScore: {score:.4f}"
                f"\nSource: {result['source']}"
                f"\nText: {result['text'][:300]}"
            )

        return results


# --------------------------------------------------
# HELPER FUNCTION
# --------------------------------------------------

def build_environment_query(
    soil_carbon,
    rainfall,
    crop,
    region,
    land_use=None,
    biodiversity=None,
    moisture=None
):
    """
    Creates a dynamic RAG query from the user's
    environmental metrics.
    """

    query_parts = [
        f"Soil organic carbon: {soil_carbon}",
        f"Rainfall: {rainfall}",
        f"Crop: {crop}",
        f"Region: {region}",
    ]

    if land_use:
        query_parts.append(
            f"Land use: {land_use}"
        )

    if biodiversity:
        query_parts.append(
            f"Biodiversity: {biodiversity}"
        )

    if moisture:
        query_parts.append(
            f"Soil moisture: {moisture}"
        )

    query_parts.append(
        """
Provide environmental management recommendations
appropriate for these conditions.

Consider:
- soil organic carbon improvement
- biodiversity improvement
- agroforestry
- intercropping
- cover crops
- crop rotation
- soil health
- water conservation
- measurable environmental improvements
- credible environmental evidence
"""
    )

    return "\n".join(query_parts)


# --------------------------------------------------
# TEST
# --------------------------------------------------

if __name__ == "__main__":

    retriever = Retriever()

    # Test input
    query = build_environment_query(
        soil_carbon="0.3%",
        rainfall="low",
        crop="monoculture wheat",
        region="semi-arid",
        land_use="monoculture",
        biodiversity="low",
        moisture="24%"
    )

    results = retriever.search(
        query,
        top_k=3
    )

    print("\n")
    print("=" * 60)
    print("FINAL RETRIEVAL RESULT")
    print("=" * 60)

    for result in results:

        print("\nRecommendation Source:")
        print(result["source"])

        print("\nScore:")
        print(result["score"])

        print("\nContent:")
        print(result["text"])