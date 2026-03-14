🧠 Incident Extraction API with Local LLM (Ollama)
API that receives free-text descriptions of incidents and returns structured JSON data, using a local LLM via Ollama.

🎯 Goal
Demonstrate a complete information extraction pipeline featuring:

Deterministic text preprocessing
Semantic extraction with a local LLM
Structural validation with Pydantic
A simple, documented HTTP API

All without relying on external services.

🏗️ Architecture
User → FastAPI → Preprocessing → Ollama (LLM) → Pydantic → Structured JSON

User sends text via API
Text goes through deterministic preprocessing
Processed text is sent to the local LLM (Ollama)
LLM output is validated with Pydantic
API returns structured JSON


🧹 Text Preprocessing
Before any LLM call, the text goes through fixed, predictable, and testable rules:

Normalization — lowercase and general cleanup
Accent removal
Date and time standardization
Temporal hint extraction
Fuzzy matching with Levenshtein distance — corrects minor word variations and reduces LLM dependency

This ensures greater consistency, reproducibility, and testability throughout the pipeline.

📁 Project Structure
.
├── api.py                        # FastAPI entry point
│
├── core/
│   ├── incident_extractor.py     # Orchestrates the pipeline (prompt + LLM + parsing)
│   └── text_preprocessor.py     # Deterministic text preprocessing
│
├── model/
│   ├── incident.py               # Pydantic incident model
│   └── incident_prompt.py        # Prompt used by the LLM
│
├── tests/
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   └── conftest.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md

🛠️ Prerequisites
Before getting started, make sure you have the following installed:

Docker Desktop
Git or GitHub CLI (to clone the repository)


🚀 Installation & Setup
1. Install Docker Desktop and Git
Visit the links below and follow the installer instructions for your operating system:
👉 https://git-scm.com/install/windows
👉 https://docs.docker.com/get-started/introduction/get-docker-desktop/
After installation, open Docker Desktop and wait for it to fully initialize (the system tray icon should turn green/stable).
2. Clone the repository
Option A — GitHub CLI (recommended):
bashgh repo clone Rodrigo-K-Fuchs/API-de-Extracao-de-Incidentes-com-LLM-Local
Option B — Standard Git:
bashgit clone https://github.com/Rodrigo-K-Fuchs/API-de-Extracao-de-Incidentes-com-LLM-Local.git
Option C — Download ZIP:
On the GitHub repository page, click Code → Download ZIP and extract the contents.

3. Navigate to the project folder
After cloning or extracting the ZIP, go to the project root:
bashcd API-de-Extracao-de-Incidentes-com-LLM-Local

⚠️ All subsequent commands must be run from this folder.


🐳 Running with Docker
Build the image
bashdocker build -t incident-api .
Start the application
bashdocker compose up
```

To stop:  
`CTRL + C`

---

## 🌐 Interactive Documentation

With the application running, access the Swagger UI to test the API directly in your browser:
```
http://localhost:8000/docs

🧪 Tests
The project includes unit tests (preprocessing, validations, and deterministic rules) and integration tests (full pipeline with a mocked LLM).
To run the tests, open the project in your IDE or text editor and, from the terminal at the project root, run:
bashpytest

Integration tests use a mocked LLM and do not require Ollama to be running.


⚠️ System Rules

Fields that cannot be inferred return null
Impossible timestamps return "INVALID"
The LLM never fabricates information
All output goes through Pydantic validation
The LLM does not decide alone — the code is in charge


📖 Code Documentation
All main classes have docstrings describing their responsibility, inputs, outputs, and expected behavior.
