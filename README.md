. Architecture

```text
User
  |
  v
Streamlit Frontend (app.py)
  |
  v
FastAPI Backend (backend/main.py)
  |
  +--> API Routes (backend/api/routes.py)
  |
  +--> EcoService (backend/services/eco_service.py)
          |
          +--> RAG Retriever (rag/retriever.py)
          |      |
          |      +--> Sentence Transformers embeddings
          |      +--> FAISS vector index
          |      +--> Knowledge Base (*.txt)
          |
          +--> Environmental Reasoning Engine
          |      (reasoning/environmental_engine.py)
          |
          +--> AI Reasoner
                 (backend/services/ai_reasoner.py, when enabled)
```

The system extracts environmental information from natural-language input, stores metrics in session memory, retrieves relevant knowledge, applies environmental reasoning rules, and can pass metrics plus retrieved evidence to an AI reasoning layer for structured analysis.

## 2. Knowledge Base and Schema

EcoRAG does not currently use a relational database. The knowledge layer consists of local text documents indexed as embeddings in FAISS, with document metadata stored in `documents.pkl`. Structured environmental metrics are represented in JSON.

### Environmental metrics schema

```json
{
  "soil": {
    "ph": 6.5,
    "organic_carbon": 1.2,
    "moisture": 24
  },
  "land": {
    "land_use": "mixed agriculture",
    "crop": "wheat",
    "tree_cover": 8,
    "vegetation_diversity": 2
  },
  "biodiversity": {
    "species_richness": 12,
    "habitat_diversity": 2,
    "pollinator_abundance": 40
  },
  "climate": {
    "annual_rainfall": 650,
    "mean_temperature": 27,
    "rainfall_category": "low",
    "region_type": "semi-arid"
  },
  "human_impact": {
    "pollution": "medium",
    "deforestation": "low",
    "pesticide_use": "medium"
  }
}
```

### Knowledge-base documents

- `knowledge_base/soil_health.txt`
- `knowledge_base/biodiversity.txt`
- `knowledge_base/climate.txt`
- `knowledge_base/agroforestry.txt`
- `knowledge_base/environmental_impacts.txt`

## 3. Local Setup

### Requirements

- Python 3.10+ recommended
- Git
- Internet access for Python package installation and model download
- An OpenAI API key only when the optional AI reasoning layer is enabled

### Installation

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Build the RAG index

```powershell
python rag/ingest.py
```

This creates the local FAISS index and document metadata files:

- `rag/faiss.index`
- `rag/documents.pkl`

These generated files are excluded from Git via `.gitignore` and can be regenerated locally.

### Configure the AI API key

Do not commit an API key to GitHub. In PowerShell, for the current terminal session:

```powershell
$env:OPENAI_API_KEY="YOUR_KEY_HERE"
```

### Run the backend

```powershell
uvicorn backend.main:app --reload
```

Backend URLs:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

### Run the Streamlit frontend

Open a second terminal and run:

```powershell
streamlit run app.py
```

The Streamlit UI normally opens at the local Streamlit URL shown by the command.

## 4. API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Backend status |
| GET | `/health` | Health check |
| GET | `/api/status` | API status |
| POST | `/api/analyze` | Analyze structured environmental metrics and return recommendations/evidence |

### Example request

```json
{
  "soil": {
    "organic_carbon": 0.3
  },
  "land": {
    "crop": "wheat",
    "land_use": "monoculture"
  },
  "climate": {
    "rainfall_category": "low",
    "region_type": "semi-arid"
  },
  "biodiversity": {},
  "human_impact": {}
}
```

## 5. CI/CD

Current status: the project is hosted in GitHub, but an automated CI/CD workflow is not yet configured in the repository.

For review, the current source-of-truth workflow is:

```text
Git commit -> git push -> GitHub repository
```

A production deployment would typically add GitHub Actions for automated syntax/tests and a deployment target for the FastAPI/Streamlit services.

## 6. Reviewer Notes

- GitHub repository: https://github.com/Tsupritha34/EcoRAG.git
- Live demo: Not deployed yet.
- API documentation (local): http://127.0.0.1:8000/docs
- No credentials are embedded in the repository.
- Reviewers who enable the AI reasoning layer must supply their own OpenAI API key through an environment variable.
- Run `python rag/ingest.py` after cloning to recreate excluded FAISS artifacts.
- The project currently combines deterministic environmental rules with RAG retrieval; the AI reasoning layer can further interpret retrieved evidence when configured.

## 7. Test Scenario

Example natural-language input:

> Soil organic carbon is 0.3%. Rainfall is low. The crop is monoculture wheat, and the region is semi-arid.

Expected system behavior:

1. Extract SOC, rainfall category, crop, land-use, and region context.
2. Identify low-SOC and dry-climate conditions.
3. Retrieve related soil, biodiversity, climate, and agroforestry knowledge.
4. Generate management actions such as crop diversification, suitable cover/legume systems, and habitat-supporting vegetation where appropriate.
5. Report impacted environmental metrics, time horizon, confidence, measurable indicators, and supporting evidence.

## 8. Demo Video
https://www.image2url.com/r2/default/videos/1789805884322-e2499712-45ae-4738-9b44-7d6ed5d53653.mp4

