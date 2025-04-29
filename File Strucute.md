```
idis-project/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI entrypoint
│   │   ├── config.py                 # Configuration management
│   │   ├── core/                     # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── ocr.py                # OCR processing
│   │   │   ├── parser.py             # Document parsing
│   │   │   ├── chunking.py           # Semantic chunking
│   │   │   ├── embedding.py          # Vector embedding generation
│   │   │   ├── vector_store.py       # FAISS interface
│   │   │   ├── entity_extraction.py  # Named entity recognition
│   │   │   └── llm.py                # LLM orchestration
│   │   ├── routers/                  # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── documents.py          # Document upload/processing
│   │   │   ├── qa.py                 # Q&A endpoints
│   │   │   ├── entities.py           # Entity extraction endpoints
│   │   │   └── export.py             # Data export endpoints
│   │   ├── models/                   # Data models
│   │   │   ├── __init__.py
│   │   │   ├── document.py           # Document models
│   │   │   ├── query.py              # Query models
│   │   │   └── response.py           # Response models
│   │   ├── services/                 # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── document_service.py   # Document processing pipeline
│   │   │   ├── qa_service.py         # Q&A pipeline
│   │   │   └── analytics_service.py  # Usage metrics
│   │   └── utils/                    # Utilities
│   │       ├── __init__.py
│   │       ├── file_utils.py         # File handling
│   │       └── metrics.py            # Performance metrics
│   ├── tests/                        # Backend tests
│   │   ├── __init__.py
│   │   ├── test_ocr.py
│   │   ├── test_parser.py
│   │   └── test_qa.py
│   ├── data/                         # Data storage
│   │   ├── vectors/                  # FAISS indexes
│   │   ├── documents/                # Original documents
│   │   └── processed/                # Processed results
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/               # React components
│   │   │   ├── Dashboard.jsx
│   │   │   ├── DocumentUploader.jsx
│   │   │   ├── ChatInterface.jsx
│   │   │   ├── EntityViewer.jsx
│   │   │   └── AnalyticsPanel.jsx
│   │   ├── services/                 # API clients
│   │   │   ├── api.js
│   │   │   └── auth.js
│   │   ├── hooks/                    # Custom React hooks
│   │   │   └── useDocuments.js
│   │   ├── App.jsx
│   │   ├── index.jsx
│   │   └── tailwind.css
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml                # Local development setup
├── .env.example                      # Environment variable template
├── k8s/                              # Kubernetes manifests
│   ├── backend-deployment.yaml
│   ├── frontend-deployment.yaml
│   ├── ingress.yaml
│   └── persistent-volume.yaml
├── terraform/                        # IaC for cloud deployment
│   ├── main.tf
│   ├── variables.tf
│   └── outputs.tf
├── .github/
│   └── workflows/
│       ├── ci.yml                    # Continuous Integration
│       └── cd.yml                    # Continuous Deployment
├── README.md
└── LICENSE
```
