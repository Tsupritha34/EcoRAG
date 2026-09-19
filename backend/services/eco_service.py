from rag.retriever import Retriever
from reasoning.environmental_engine import generate_recommendations
from backend.services.ai_reasoner import AIReasoner


class EcoService:

    def __init__(self):
        self.retriever = None
        self.ai_reasoner = None

    def get_retriever(self):
        if self.retriever is None:
            self.retriever = Retriever()

        return self.retriever

    def get_ai_reasoner(self):
        if self.ai_reasoner is None:
            self.ai_reasoner = AIReasoner()

        return self.ai_reasoner

    def retrieve_evidence(self, query, top_k=5):
        retriever = self.get_retriever()

        return retriever.search(
            query,
            top_k=top_k
        )

    def analyze(self, metrics):

        # ---------------------------------------------
        # Step 1: Create a retrieval query
        # ---------------------------------------------

        query_parts = []

        for category, values in metrics.items():

            if not values:
                continue

            query_parts.append(
                f"{category}: {values}"
            )

        rag_query = (
            "environmental science biodiversity "
            "soil health climate land use "
            + " ".join(query_parts)
        )

        # ---------------------------------------------
        # Step 2: Retrieve scientific evidence
        # ---------------------------------------------

        evidence = self.retrieve_evidence(
            rag_query,
            top_k=5
        )

        # ---------------------------------------------
        # Step 3: Run existing rule-based reasoning
        # ---------------------------------------------

        rule_recommendations = generate_recommendations(
            metrics
        )

        # ---------------------------------------------
        # Step 4: AI scientist reasoning
        # ---------------------------------------------

        ai_reasoner = self.get_ai_reasoner()

        ai_result = ai_reasoner.analyze(
            metrics=metrics,
            evidence=evidence
        )

        # ---------------------------------------------
        # Step 5: Return complete result
        # ---------------------------------------------

        return {
            "environmental_assessment": ai_result,
            "rule_based_recommendations": rule_recommendations,
            "retrieved_evidence": evidence
        }