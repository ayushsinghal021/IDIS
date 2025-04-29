# Document Intelligence Suite

Welcome! 👋 This is the Document Intelligence Suite, your one-stop solution for turning PDFs, images, and Word docs into searchable, structured data. I built it because—I don’t know about you—but wrestling with scattered invoices, reports, and scans drove me nuts. Now, everything gets ingested, parsed, chunked, and made queryable through a friendly API and dashboard.

---

## 🚀 Key Features

1. **Flexible Ingestion**: Drop in text-based PDFs, scanned images, and Word files via a FastAPI endpoint. No more manual copy-paste.
2. **Smart OCR & Parsing**: Scanned docs go through Tesseract (or PaddleOCR), while text-PDFs are handled by pdfplumber or PyMuPDF under the hood.
3. **Semantic Chunking**: We slice and dice content into meaningful sections, then generate embeddings using SentenceTransformers.
4. **Vector Store**: Embeddings live locally in a FAISS vector store today—and you can swap in Pinecone or Weaviate when you’re ready to scale.
5. **Interactive Q&A**: Fire up a chat endpoint that taps either a local LLM (LLaMA/Mistral via Ollama) or your OpenAI API key. Ask away!
6. **Structured Data Extraction**: Entities like names, dates, invoice numbers—pulled out via spaCy pipelines, with regex as a safety net.
7. **Multiple Output Formats**: Get your data as JSON, CSV/Excel, or push it out through REST callbacks.
8. **User Dashboard**: React + Tailwind gives you real-time upload status, extracted insights, and usage metrics in a sleek interface.
9. **Containerized & Cloud-Ready**: Docker for local dev, plus Kubernetes manifests and Terraform templates for spinning up in the cloud.

---

## 🛠️ Installation & Setup

1. **Clone the repo**

   ```bash
   git clone https://github.com/your-username/document-intel-suite.git
   cd document-intel-suite
   ```

2. **Environment Variables**

   - Copy `.env.example` to `.env`
   - Fill in your OpenAI API key (if using) and any other secrets.

3. **Local Development with Docker**

   ```bash
   docker-compose up --build
   ```

4. **Access the App**

   - FastAPI docs: `http://localhost:8000/docs`
   - Dashboard: `http://localhost:3000`

---

## 💡 Usage Examples

- **Ingest a file**:

  ```bash
  curl -F "file=@/path/to/invoice.pdf" http://localhost:8000/upload
  ```

- **Chat Q&A**:

  ```bash
  curl -X POST http://localhost:8000/chat \
       -H 'Content-Type: application/json' \
       -d '{"question":"What’s the total due on invoice #123?"}'
  ```

- **Export as CSV**:

  ```bash
  curl http://localhost:8000/export?format=csv -o data.csv
  ```

---

## 📐 Architecture Overview

```mermaid
flowchart LR
  A[Upload Endpoint] --> B{File Type?}
  B -->|Scanned| C[OCR (Tesseract/PaddleOCR)]
  B -->|Text-PDF| D[PDF Parser (pdfplumber/PyMuPDF)]
  C & D --> E[Semantic Chunking + Embeddings]
  E --> F[FAISS Vector Store]
  F --> G[Q&A Chat (LLM/OpenAI)]
  F --> H[Data Extraction (spaCy/Regex)]
  H --> I[Output (JSON/CSV/Callback)]
  G & I --> J[React Dashboard]
```

---

## 🤝 Contributing

Feel free to open issues or submit PRs. Whether it’s swapping in a new OCR engine or polishing the UI, all contributions are welcome.

---

## 📝 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

*Last updated: April 29, 2025*

