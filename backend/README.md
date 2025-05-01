# Backend - IDIS (Document Intelligence Suite)

This is the backend service for IDIS (Document Intelligence Suite). It provides APIs for document ingestion, OCR, semantic chunking, vector storage, and interactive Q&A. Built with FastAPI, it integrates various tools like Tesseract, PaddleOCR, FAISS, and SentenceTransformers to process and analyze documents efficiently.

---

## 🚀 Features

1. **Document Ingestion**: Upload PDFs, images, and Word documents via API endpoints.
2. **OCR Support**: Extract text from scanned documents using Tesseract or PaddleOCR.
3. **Semantic Chunking**: Break down documents into meaningful sections and generate embeddings.
4. **Vector Storage**: Store embeddings locally in FAISS for fast similarity searches.
5. **Interactive Q&A**: Query documents using local LLMs (via Groq/Ollama) or OpenAI APIs.
6. **Entity Extraction**: Extract structured data like names, dates, and invoice numbers using spaCy.
7. **Multiple Output Formats**: Export processed data as JSON, CSV, or Excel.
8. **Cloud-Ready**: Fully containerized with Docker for local development and Kubernetes manifests for deployment.

---

## 🛠️ Installation & Setup

### Prerequisites

- Python 3.10+
- Docker (optional for containerized development)
- Tesseract OCR installed on the system

### Local Development

1. **Clone the Repository**

   ```bash
   git clone https://github.com/your-username/IDIS.git
   cd IDIS/backend
   ```

2. **Set Up Environment Variables**

   - Copy `.env.example` to `.env`:

     ```bash
     cp .env.example .env
     ```

   - Update the `.env` file with your configuration (e.g., API keys, file paths).

3. **Install Dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**

   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Access the API**

   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Using Docker

1. **Build and Run the Docker Container**

   ```bash
   docker build -t idis-backend .
   docker run -p 8000:8000 --env-file .env idis-backend
   ```

2. **Access the API**

   - API Documentation: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 📂 Folder Structure

```
backend/
├── app/                # FastAPI application code
│   ├── main.py         # Entry point for the application
|   ├── config.py       # Application configuration settings
│   ├── routers/        # API route definitions
│   ├── services/       # Business logic and helper functions
│   ├── models/         # Pydantic models for request/response 
|   ├── core/               # Core configurations and utilities
├── data/               # Storage for uploaded and processed files
├── requirements.txt    # Python dependencies
├── Dockerfile          # Docker configuration
├── .env                # Environment variables (not committed to version control)
└── .env.example        # Example environment variables
```

---

## 💡 API Usage Examples

### Upload a Document

```bash
curl -F "file=@/path/to/document.pdf" http://localhost:8000/upload
```

### Perform Q&A on a Document

```bash
curl -X POST http://localhost:8000/chat \
     -H 'Content-Type: application/json' \
     -d '{"question":"What is the total amount on invoice #123?"}'
```

### Export Processed Data

```bash
curl http://localhost:8000/export?format=csv -o data.csv
```

---

## 🛠️ Environment Variables

The application uses the following environment variables:

| Variable              | Description                                      | Default Value                |
|-----------------------|--------------------------------------------------|------------------------------|
| `ENVIRONMENT`         | Application environment (`development`/`prod`)  | `development`               |
| `DEBUG`               | Enable debug mode (`true`/`false`)              | `true`                      |
| `GROQ_API_KEY`        | API key for Groq LLM                            |                              |
| `LLM_PROVIDER`        | LLM provider (`groq`, `openai`, etc.)           | `groq`                      |
| `GROQ_MODEL`          | Model name for Groq                             | `llama3-8b-8192`            |
| `UPLOAD_FOLDER`       | Path for uploaded files                         | `./data/documents`          |
| `PROCESSED_FOLDER`    | Path for processed files                        | `./data/processed`          |
| `VECTOR_FOLDER`       | Path for vector storage                         | `./data/vectors`            |
| `OCR_ENGINE`          | OCR engine to use (`tesseract`, `paddleocr`)    | `tesseract`                 |
| `EMBEDDING_MODEL`     | SentenceTransformers model for embeddings       | `sentence-transformers/all-MiniLM-L6-v2` |
| `VECTOR_DIMENSION`    | Dimension of the embedding vectors              | `384`                       |

---