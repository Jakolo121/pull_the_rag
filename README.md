# RAG Pipeline with FastAPI

A production-ready Retrieval-Augmented Generation (RAG) pipeline implementation using FastAPI, LangChain, and Pinecone. This service processes PDF documents and provides a question-answering interface using state-of-the-art language models.

## 🚀 Features

- PDF document processing and embedding
- Async FastAPI endpoints for document upload and querying
- Serverless Pinecone vector store integration
- LLM integration with Groq (llama3-70b-8192)
- NeMo Guardrails for safe and controlled responses
- Docker support for easy deployment
- Comprehensive logging and error handling

## 🛠️ Tech Stack

- **FastAPI**: Modern web framework for building APIs
- **LangChain**: Framework for developing LLM applications
- **Pinecone**: Vector database for efficient similarity search
- **Groq**: High-performance LLM provider
- **PyMuPDF**: PDF processing library
- **Docker**: Containerization platform

## 📋 Prerequisites

- Python 3.12+
- Docker (optional)
- API keys for:
  - OpenAI (embeddings)
  - Pinecone
  - Groq
  - LangSmith (optional)

## 🔧 Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rag-pipeline.git
cd rag-pipeline
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
GROQ_API_KEY=your_groq_api_key
LANGSMITH_API_KEY=your_langsmith_api_key
```

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t rag-pipeline .
```

2. Run the container:
```bash
docker run -p 8000:8000 --env-file .env rag-pipeline
```

## 📚 API Documentation

### Endpoints

#### POST /upload/
Upload and process a PDF document.
```bash
curl -X POST -F "file=@/path/to/your/document.pdf" http://localhost:8000/upload/
```

#### POST /query/
Query the RAG pipeline with a question.
```bash
curl -X POST -H "Content-Type: application/json" \
     -d '{"question": "Your question here", "index_name": "your_index_name"}' \
     http://localhost:8000/query/
```

#### GET /health/
Check the API health status.
```bash
curl http://localhost:8000/health/
```

## 🏗️ Project Structure

```
rag-pipeline/
├── api.py              # FastAPI application
├── loader.py           # Document processing and embedding
├── rag_chain.py        # RAG implementation
├── config/             # NeMo Guardrails configuration
├── requirements.txt    # Project dependencies
├── Dockerfile         # Docker configuration
└── .env               # Environment variables
```

## 🔒 Security Considerations

- Always use environment variables for sensitive information
- Never commit `.env` files to version control
- Implement rate limiting for production deployments
- Consider adding authentication for the API endpoints

## 🚀 Deployment

### Cloud Deployment Options

#### Google Cloud Run
```bash
gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/rag-pipeline
gcloud run deploy rag-pipeline --image gcr.io/YOUR_PROJECT_ID/rag-pipeline
```

#### AWS ECS
```bash
aws ecr get-login-password --region YOUR_REGION | docker login --username AWS --password-stdin
docker tag rag-pipeline:latest YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/rag-pipeline
docker push YOUR_ACCOUNT_ID.dkr.ecr.YOUR_REGION.amazonaws.com/rag-pipeline
```

## 📈 Performance Optimization

- Uses lazy loading for document processing
- Implements async/await for better concurrency
- Employs efficient chunking strategies
- Utilizes serverless vector storage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Isabella Reichardt (@reichardtit)

## 🙏 Acknowledgments

- LangChain team for the excellent framework
- Pinecone team for vector storage solutions
- FastAPI team for the amazing web framework

## 📞 Support

For support, open an issue in the repository.

---

Remember to replace placeholder values (API keys, email addresses, etc.) with your actual information before deploying.