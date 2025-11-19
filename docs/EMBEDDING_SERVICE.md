# Embedding Service Documentation

## Overview

The Embedding Service generates vector embeddings from text using the `ai/embeddinggemma:300M-Q8_0` model via Docker Model Runner. This service is a foundational component for enabling Retrieval-Augmented Generation (RAG) capabilities, allowing efficient vector-based similarity search for questions and answers.

## Features

- **Single Text Embedding**: Generate embedding for a single text input
- **Batch Embedding**: Generate embeddings for multiple texts in one request
- **OpenAI-Compatible API**: Uses standard embeddings API format
- **Graceful Degradation**: Handles service unavailability gracefully
- **Configurable**: Easy to enable/disable and configure via environment variables
- **Docker Model Runner Integration**: Runs locally with Docker Desktop

## Architecture

### Service Design

The `EmbeddingService` class provides a clean API for generating text embeddings:

```python
from gradeschoolmathsolver.services.embedding import EmbeddingService

service = EmbeddingService()

# Generate single embedding
embedding = service.generate_embedding("What is five plus three?")

# Generate batch embeddings
embeddings = service.generate_embeddings([
    "What is five plus three?",
    "Calculate ten minus four"
])
```

### API Integration

The service uses the OpenAI-compatible embeddings API format:

**Endpoint**: `{EMBEDDING_MODEL_URL}/engines/{EMBEDDING_ENGINE}/v1/embeddings`

**Request Format**:
```json
{
  "model": "ai/embeddinggemma:300M-Q8_0",
  "input": "text to embed"
}
```

**Response Format**:
```json
{
  "data": [
    {
      "embedding": [0.1, 0.2, ...],
      "index": 0
    }
  ]
}
```

## Configuration

### Environment Variables

Add these settings to your `.env` file:

```bash
# Embedding Service Configuration
EMBEDDING_MODEL_URL=http://localhost:12434
EMBEDDING_MODEL_NAME=ai/embeddinggemma:300M-Q8_0
EMBEDDING_ENGINE=llama.cpp
EMBEDDING_SERVICE_ENABLED=True
```

### Configuration Options

- **EMBEDDING_MODEL_URL**: URL of the embedding model service endpoint
  - Default: `http://localhost:12434`
  - Use `http://host.docker.internal:12434` when running in Docker
  
- **EMBEDDING_MODEL_NAME**: Name/identifier of the embedding model
  - Default: `ai/embeddinggemma:300M-Q8_0`
  - Must match the model downloaded in Docker Model Runner
  
- **EMBEDDING_ENGINE**: Engine type for API path
  - Default: `llama.cpp`
  - Docker Model Runner uses `llama.cpp` engine
  
- **EMBEDDING_SERVICE_ENABLED**: Enable/disable the service
  - Default: `True`
  - Set to `False` to disable embedding generation

## Setup Instructions

### Prerequisites

- Docker Desktop 4.32 or later
- Docker Model Runner enabled
- 8GB+ RAM recommended

### Step 1: Enable Docker Model Runner

1. Open Docker Desktop
2. Navigate to **Settings** → **Features in development**
3. Enable **"Enable Docker AI Model Runner"**
4. Click **Apply & Restart**

### Step 2: Download the Embedding Model

1. In Docker Desktop, navigate to the **AI Models** or **Models** section
2. Search for `embeddinggemma:300M-Q8_0`
3. Click to download/pull the model
4. Wait for the download to complete
5. Verify the model appears in the downloaded models list

**Model Details**:
- Name: `ai/embeddinggemma:300M-Q8_0`
- Size: ~300M parameters
- Quantization: Q8_0 (8-bit quantization)
- Purpose: Text embedding generation for RAG

### Step 3: Verify Installation

Test the embedding service:

```bash
# Verify model is available
curl http://localhost:12434/engines/llama.cpp/v1/models

# Test embedding generation
curl http://localhost:12434/engines/llama.cpp/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/embeddinggemma:300M-Q8_0",
    "input": "What is five plus three?"
  }'
```

Expected response should include:
```json
{
  "data": [
    {
      "embedding": [...],
      "index": 0
    }
  ]
}
```

### Step 4: Configure the Application

1. Copy `.env.example` to `.env` if you haven't already:
   ```bash
   cp .env.example .env
   ```

2. Update the embedding configuration in `.env`:
   ```bash
   EMBEDDING_SERVICE_ENABLED=True
   EMBEDDING_MODEL_URL=http://localhost:12434
   EMBEDDING_MODEL_NAME=ai/embeddinggemma:300M-Q8_0
   EMBEDDING_ENGINE=llama.cpp
   ```

3. If running in Docker, use `host.docker.internal` instead of `localhost`:
   ```bash
   EMBEDDING_MODEL_URL=http://host.docker.internal:12434
   ```

### Step 5: Test the Service

Run the service test script:

```bash
# Direct service test
python gradeschoolmathsolver/services/embedding/service.py

# Unit tests
python tests/test_embedding_service.py

# Or with pytest
pytest tests/test_embedding_service.py -v
```

## Usage

### Basic Usage

```python
from gradeschoolmathsolver.services.embedding import EmbeddingService

# Initialize service
service = EmbeddingService()

# Check if service is available
if service.is_available():
    # Generate embedding for single text
    text = "What is the sum of five and three?"
    embedding = service.generate_embedding(text)
    
    if embedding:
        print(f"Embedding dimension: {len(embedding)}")
        print(f"First 5 values: {embedding[:5]}")
```

### Batch Processing

```python
# Generate embeddings for multiple texts
texts = [
    "What is five plus three?",
    "Calculate ten minus four",
    "What is six times seven?"
]

embeddings = service.generate_embeddings(texts)

if embeddings:
    for i, emb in enumerate(embeddings):
        print(f"Text {i+1}: Dimension {len(emb)}")
```

### Check Embedding Dimension

```python
# Get the embedding dimension
dimension = service.get_embedding_dimension()
print(f"Embedding dimension: {dimension}")
```

## Integration with RAG

The embedding service is designed to support vector-based retrieval in RAG workflows:

### 1. Embedding Questions

```python
# When storing a question-answer pair
question = "What is five plus three?"
question_embedding = service.generate_embedding(question)

# Store in vector database with embedding
store_to_database(question, answer, question_embedding)
```

### 2. Similarity Search

```python
# When searching for similar questions
query = "What is the sum of 5 and 3?"
query_embedding = service.generate_embedding(query)

# Search for similar embeddings
similar_items = vector_search(query_embedding, top_k=5)
```

### 3. Context Retrieval for RAG

```python
# Retrieve relevant context for RAG
def get_rag_context(question, top_k=3):
    # Generate embedding for the question
    question_embedding = service.generate_embedding(question)
    
    # Find similar questions from history
    similar_questions = search_similar(question_embedding, top_k)
    
    # Return context for the AI model
    return format_context(similar_questions)
```

## Error Handling

The service includes comprehensive error handling:

### Service Disabled

```python
if not service.enabled:
    print("Embedding service is disabled")
    # Handle accordingly
```

### Connection Errors

```python
embedding = service.generate_embedding(text)
if embedding is None:
    # Service unavailable or error occurred
    print("Failed to generate embedding")
    # Fall back to alternative approach
```

### Empty Input

```python
# Empty inputs return None
embedding = service.generate_embedding("")  # Returns None
embedding = service.generate_embedding("   ")  # Returns None
embeddings = service.generate_embeddings([])  # Returns None
```

## Performance Considerations

### Model Size

- **ai/embeddinggemma:300M-Q8_0**: ~300M parameters
- **Quantization**: Q8_0 (8-bit) for reduced size and faster inference
- **Memory**: ~500MB RAM recommended
- **Speed**: Fast inference suitable for real-time applications

### Optimization Tips

1. **Batch Processing**: Use `generate_embeddings()` for multiple texts to reduce API calls
2. **Caching**: Cache embeddings for frequently used texts
3. **Timeout Settings**: Default 30s for single, 60s for batch - adjust if needed
4. **Connection Pooling**: Requests library handles connection reuse automatically

### Resource Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4 GB
- Disk: 2 GB (for model storage)

**Recommended**:
- CPU: 4 cores
- RAM: 8 GB
- GPU: Optional, for faster inference

## Troubleshooting

### Issue: "Connection error: Unable to reach embedding service"

**Solutions**:
1. Verify Docker Desktop is running
2. Check Docker Model Runner is enabled
3. Confirm the embedding model is downloaded
4. Test the endpoint manually:
   ```bash
   curl http://localhost:12434/engines/llama.cpp/v1/models
   ```

### Issue: "Timeout generating embedding"

**Solutions**:
1. Increase timeout in service configuration
2. Check system resources (CPU/RAM usage)
3. Try smaller batch sizes
4. Verify model is loaded (check Docker Desktop models tab)

### Issue: Model not found

**Solutions**:
1. Pull the model in Docker Desktop:
   - Open Docker Desktop
   - Go to Models section
   - Search for and download `embeddinggemma:300M-Q8_0`
2. Verify model name in `.env` matches exactly
3. Check model name in Docker Desktop models list

### Issue: Empty or null embeddings

**Solutions**:
1. Check input text is not empty
2. Verify API response format matches expected structure
3. Test with simple text: `service.generate_embedding("test")`
4. Check Docker Desktop logs for model errors

### Issue: Docker container can't reach localhost:12434

**Solution**:
Use `host.docker.internal` instead of `localhost` in docker-compose.yml:
```yaml
environment:
  - EMBEDDING_MODEL_URL=http://host.docker.internal:12434
```

## Testing

### Run Tests

```bash
# Direct test script
python tests/test_embedding_service.py

# With pytest
pytest tests/test_embedding_service.py -v

# With coverage
pytest tests/test_embedding_service.py --cov=gradeschoolmathsolver.services.embedding
```

### Test Cases

1. **Initialization Test**: Verify service initializes correctly
2. **Single Generation**: Test single text embedding
3. **Batch Generation**: Test multiple text embeddings
4. **Empty Input**: Test handling of empty/invalid inputs
5. **Consistency**: Verify same input produces consistent output
6. **Dimension**: Test getting embedding dimension
7. **Availability**: Test service availability check

## API Reference

### EmbeddingService Class

#### Methods

##### `__init__()`
Initialize the embedding service with configuration from Config class.

##### `generate_embedding(text: str) -> Optional[List[float]]`
Generate embedding for a single text input.

**Parameters**:
- `text` (str): Text to generate embedding for

**Returns**:
- `List[float]`: Embedding vector, or `None` if failed

**Example**:
```python
embedding = service.generate_embedding("What is 5+3?")
```

##### `generate_embeddings(texts: List[str]) -> Optional[List[List[float]]]`
Generate embeddings for multiple text inputs.

**Parameters**:
- `texts` (List[str]): List of texts to generate embeddings for

**Returns**:
- `List[List[float]]`: List of embedding vectors, or `None` if failed

**Example**:
```python
embeddings = service.generate_embeddings(["text1", "text2"])
```

##### `get_embedding_dimension() -> Optional[int]`
Get the dimension of embeddings produced by the model.

**Returns**:
- `int`: Embedding dimension, or `None` if unable to determine

**Example**:
```python
dimension = service.get_embedding_dimension()
```

##### `is_available() -> bool`
Check if the embedding service is available and working.

**Returns**:
- `bool`: `True` if service is enabled and accessible, `False` otherwise

**Example**:
```python
if service.is_available():
    embedding = service.generate_embedding(text)
```

## Future Enhancements

Potential improvements for the embedding service:

1. **Vector Database Integration**: Direct integration with vector databases (Milvus, Pinecone, etc.)
2. **Caching Layer**: Redis/Memcached for embedding cache
3. **Async Support**: Async/await for non-blocking operations
4. **Batch Queue**: Queue system for high-volume batch processing
5. **Model Switching**: Support for multiple embedding models
6. **Fine-tuning**: Custom model fine-tuning for math-specific embeddings
7. **Similarity Search**: Built-in similarity search utilities
8. **Monitoring**: Prometheus metrics for service health

## Related Documentation

- [AI Model Service Documentation](AI_MODEL_SERVICE.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Database Service Documentation](DATABASE_SERVICE.md)
- [Main README](../README.md)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Verify Docker Model Runner is working correctly
3. Review Docker Desktop logs
4. Open an issue on GitHub with:
   - Error messages
   - Configuration details
   - Docker Desktop version
   - System information (OS, RAM, etc.)
