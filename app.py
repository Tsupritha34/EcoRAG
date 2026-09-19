import json
import re
from pathlib import Path

import streamlit as st

from rag.retriever import Retriever
from reasoning.environmental_engine import generate_recommendations


BASE_DIR = Path(__file__).resolve().parent
METRICS_FILE = BASE_DIR / "data" / "environmental_metrics.json"


st.set_page_config(
    page_title="EcoRAG - Biodiversity AI",
    page_icon="🌱",
    layout="wide",
)


# ---------------------------------------------------------
# Session state
# ---------------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "metrics" not in st.session_state:
    st.session_state.metrics = {
        "soil": {},
        "land": {},
        "biodiversity": {},
        "climate": {},
        "human_impact": {},
    }

if "retriever" not in st.session_state:
    st.session_state.retriever = None


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def initialize_retriever():
    """Load the FAISS retriever."""
    if st.session_state.retriever is not None:
        return st.session_state.retriever

    try:
        st.session_state.retriever = Retriever()
        return st.session_state.retriever
    except FileNotFoundError:
        return None
    except Exception:
        return None


def load_sample_metrics():
    """Load metrics from the JSON sample file."""
    if not METRICS_FILE.exists():
        return {}

    try:
        with open(METRICS_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return {}


def merge_metrics(new_metrics):
    """Merge newly extracted metrics into session memory."""
    for category, values in new_metrics.items():
        if category not in st.session_state.metrics:
            st.session_state.metrics[category] = {}

        if isinstance(values, dict):
            st.session_state.metrics[category].update(values)


def extract_metrics(text):
    """
    Extract environmental values from natural-language user input.
    Example:
    SOC 0.3%, rainfall 500 mm, wheat monoculture, moisture 15%
    """

    text_lower = text.lower()

    metrics = {
        "soil": {},
        "land": {},
        "biodiversity": {},
        "climate": {},
        "human_impact": {},
    }

    # Soil Organic Carbon
    soc_patterns = [
        r"(?:soc|soil organic carbon|organic carbon)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*%?",
    ]

    for pattern in soc_patterns:
        match = re.search(pattern, text_lower)
        if match:
            metrics["soil"]["organic_carbon"] = float(match.group(1))
            break

    # Soil pH
    ph_match = re.search(
        r"(?:soil\s*)?ph\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)",
        text_lower,
    )

    if ph_match:
        metrics["soil"]["ph"] = float(ph_match.group(1))

    # Soil moisture
    moisture_match = re.search(
        r"(?:soil\s*)?moisture\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*%?",
        text_lower,
    )

    if moisture_match:
        metrics["soil"]["moisture"] = float(moisture_match.group(1))

    # Rainfall
    rainfall_match = re.search(
        r"(?:annual\s*)?rainfall\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*(?:mm)?",
        text_lower,
    )

    if rainfall_match:
        metrics["climate"]["annual_rainfall"] = float(rainfall_match.group(1))

    # Temperature
    temperature_match = re.search(
        r"(?:temperature|temp)\s*(?:is|=|:)?\s*(-?\d+(?:\.\d+)?)\s*(?:°c|c)?",
        text_lower,
    )

    if temperature_match:
        metrics["climate"]["mean_temperature"] = float(
            temperature_match.group(1)
        )

    # Species richness
    species_match = re.search(
        r"(?:species richness|species)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)",
        text_lower,
    )

    if species_match:
        metrics["biodiversity"]["species_richness"] = float(
            species_match.group(1)
        )

    # Tree cover
    tree_match = re.search(
        r"(?:tree cover|tree coverage)\s*(?:is|=|:)?\s*(\d+(?:\.\d+)?)\s*%?",
        text_lower,
    )

    if tree_match:
        metrics["land"]["tree_cover"] = float(tree_match.group(1))

    # Crop detection
    common_crops = [
        "wheat",
        "rice",
        "maize",
        "corn",
        "millet",
        "sorghum",
        "soybean",
        "cotton",
        "sugarcane",
        "barley",
        "groundnut",
    ]

    for crop in common_crops:
        if crop in text_lower:
            metrics["land"]["crop"] = crop
            break

    # Monoculture
    if "monoculture" in text_lower:
        metrics["land"]["land_use"] = "monoculture"

    # Land use
    if "mixed agriculture" in text_lower:
        metrics["land"]["land_use"] = "mixed agriculture"

    if "agriculture" in text_lower and "land_use" not in metrics["land"]:
        metrics["land"]["land_use"] = "agriculture"

    # Pollution
    for level in ["low", "medium", "high"]:
        if f"pollution {level}" in text_lower:
            metrics["human_impact"]["pollution"] = level

    pollution_match = re.search(
        r"pollution\s*(?:is|=|:)?\s*(low|medium|high)",
        text_lower,
    )

    if pollution_match:
        metrics["human_impact"]["pollution"] = pollution_match.group(1)

    # Pesticide use
    pesticide_match = re.search(
        r"(?:pesticide use|pesticides?)\s*(?:is|=|:)?\s*(low|medium|high)",
        text_lower,
    )

    if pesticide_match:
        metrics["human_impact"]["pesticide_use"] = pesticide_match.group(1)

    # Deforestation
    deforestation_match = re.search(
        r"deforestation\s*(?:is|=|:)?\s*(low|medium|high)",
        text_lower,
    )

    if deforestation_match:
        metrics["human_impact"]["deforestation"] = (
            deforestation_match.group(1)
        )

    return metrics


def format_metric_name(name):
    """Convert snake_case names into readable names."""
    return name.replace("_", " ").title()


def format_metrics(metrics):
    """Create a readable environmental metrics summary."""
    lines = []

    for category, values in metrics.items():
        if not values:
            continue

        lines.append(f"**{category.replace('_', ' ').title()}**")

        for key, value in values.items():
            unit = ""

            if key in ["organic_carbon", "moisture", "tree_cover"]:
                unit = "%"

            elif key in ["annual_rainfall"]:
                unit = " mm"

            elif key in ["mean_temperature"]:
                unit = " °C"

            lines.append(
                f"- {format_metric_name(key)}: {value}{unit}"
            )

    return "\n".join(lines)


def find_missing_information(metrics):
    """
    Determine whether enough information exists to make
    a targeted environmental recommendation.
    """

    missing = []

    soil = metrics.get("soil", {})
    land = metrics.get("land", {})
    climate = metrics.get("climate", {})
    biodiversity = metrics.get("biodiversity", {})

    if "organic_carbon" not in soil:
        missing.append("soil organic carbon (SOC)")

    if "annual_rainfall" not in climate:
        missing.append("annual rainfall")

    if "crop" not in land:
        missing.append("main crop")

    if (
        "tree_cover" not in land
        and "species_richness" not in biodiversity
    ):
        missing.append("tree cover or species richness")

    return missing


def retrieve_evidence(retriever, query, top_k=3):
    """Retrieve scientific knowledge chunks from FAISS."""
    try:
        return retriever.search(query, top_k=top_k)
    except Exception:
        return []


def render_recommendation(rec, evidence):
    """Display one recommendation and supporting evidence."""

    st.markdown(f"### 🌿 {rec['action']}")

    st.markdown("**Scientific reasoning**")
    st.write(rec["reasoning"])

    st.markdown("**Impacted environmental metrics**")
    st.write(", ".join(rec["metrics"]))

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("**Time horizon**")
        st.write(rec["time_horizon"])

    with col2:
        st.markdown("**Confidence**")
        st.write(rec["confidence"])

    st.markdown("**Retrieved scientific evidence**")

    if not evidence:
        st.info("No indexed evidence was retrieved.")
        return

    for item in evidence:
        with st.expander(
            f"{item['source']} | similarity {item['score']:.3f}"
        ):
            st.write(item["text"])


# ---------------------------------------------------------
# Page header
# ---------------------------------------------------------

st.title("🌱 EcoRAG")
st.subheader("AI-Powered Biodiversity and Environmental Recommendation System")

st.write(
    "Describe your soil, land-use, biodiversity, climate, or human-impact "
    "conditions. EcoRAG retrieves relevant knowledge and combines it with "
    "environmental reasoning rules to produce measurable recommendations."
)


# ---------------------------------------------------------
# Sidebar
# ---------------------------------------------------------

with st.sidebar:
    st.header("📊 Environmental Metrics")

    if st.button("Load Sample Dataset"):
        sample = load_sample_metrics()

        if sample:
            merge_metrics(sample)
            st.success("Sample environmental metrics loaded.")
        else:
            st.warning("Sample dataset could not be loaded.")

    if st.button("Clear Conversation"):
        st.session_state.messages = []
        st.session_state.metrics = {
            "soil": {},
            "land": {},
            "biodiversity": {},
            "climate": {},
            "human_impact": {},
        }
        st.rerun()

    st.divider()

    st.markdown("### Current Metrics")

    current_metrics = format_metrics(st.session_state.metrics)

    if current_metrics:
        st.markdown(current_metrics)
    else:
        st.info("No environmental metrics entered yet.")


# ---------------------------------------------------------
# Knowledge system status
# ---------------------------------------------------------

retriever = initialize_retriever()

if retriever is None:
    st.warning(
        "The RAG index has not been created yet. "
        "After completing the project files, run `python rag/ingest.py` "
        "in the VS Code terminal."
    )


# ---------------------------------------------------------
# Previous conversation
# ---------------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant":

            recommendations = message.get("recommendations", [])
            evidence = message.get("evidence", [])

            for index, recommendation in enumerate(recommendations):

                current_evidence = []

                if index < len(evidence):
                    current_evidence = evidence[index]

                render_recommendation(
                    recommendation,
                    current_evidence,
                )


# ---------------------------------------------------------
# User input
# ---------------------------------------------------------

user_prompt = st.chat_input(
    "Example: SOC 0.3%, rainfall 500 mm, wheat monoculture, moisture 15%"
)


if user_prompt:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_prompt,
        }
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    extracted = extract_metrics(user_prompt)
    merge_metrics(extracted)

    missing = find_missing_information(
        st.session_state.metrics
    )

    # -----------------------------------------------------
    # Ask clarification when information is missing
    # -----------------------------------------------------

    if missing:

        missing_text = ", ".join(missing)

        assistant_text = (
            "I have captured the information you provided. "
            "To make a more targeted biodiversity recommendation, "
            f"please provide: **{missing_text}**."
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": assistant_text,
                "recommendations": [],
                "evidence": [],
            }
        )

        with st.chat_message("assistant"):
            st.markdown(assistant_text)

        st.stop()

    # -----------------------------------------------------
    # Generate RAG query
    # -----------------------------------------------------

    metrics_text = format_metrics(
        st.session_state.metrics
    )

    rag_query = (
        "environmental recommendation biodiversity soil climate "
        "land use species habitat "
        + metrics_text
    )

    evidence_results = []

    if retriever is not None:
        evidence_results = retrieve_evidence(
            retriever,
            rag_query,
            top_k=5,
        )

    # -----------------------------------------------------
    # Run environmental reasoning engine
    # -----------------------------------------------------

    recommendations = generate_recommendations(
        st.session_state.metrics
    )

    # -----------------------------------------------------
    # Match evidence to each recommendation
    # -----------------------------------------------------

    recommendation_evidence = []

    for recommendation in recommendations:

        query = (
            recommendation["action"]
            + " "
            + recommendation["reasoning"]
        )

        if retriever is not None:
            rec_evidence = retrieve_evidence(
                retriever,
                query,
                top_k=3,
            )
        else:
            rec_evidence = []

        recommendation_evidence.append(rec_evidence)

    assistant_intro = (
        "Based on the environmental metrics provided, "
        f"I identified **{len(recommendations)} recommendation(s)**."
    )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": assistant_intro,
            "recommendations": recommendations,
            "evidence": recommendation_evidence,
        }
    )

    # -----------------------------------------------------
    # Display response
    # -----------------------------------------------------

    with st.chat_message("assistant"):

        st.markdown(assistant_intro)

        for index, recommendation in enumerate(recommendations):

            render_recommendation(
                recommendation,
                recommendation_evidence[index],
            )

        if evidence_results:
            with st.expander("🔎 Overall RAG Retrieval"):

                for item in evidence_results:
                    st.markdown(
                        f"**Source:** {item['source']}  \n"
                        f"**Similarity:** {item['score']:.3f}"
                    )

                    st.write(item["text"])