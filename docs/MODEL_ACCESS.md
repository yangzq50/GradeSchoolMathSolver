# Model Access Module

The Model Access module (`model_access.py`) provides a centralized interface for all AI model interactions in the GradeSchoolMathSolver system. It consolidates HTTP calls to both embedding and text generation services, providing a single point of configuration and maintenance.

## Overview

All business logic should call into this module rather than directly accessing model endpoints. This design provides:

- **Centralized configuration**: All model endpoints and model names are configured in one place
- **Consistent error handling**: Retry logic and error handling are standardized
- **Easy maintenance**: Changes to model APIs require updates in only one file
- **Better testing**: Mock the model_access module instead of HTTP calls throughout the codebase

## Configuration

Model endpoints and names are configured via environment variables:

### Environment Variables

```bash
# Text Generation Service
GENERATION_SERVICE_URL=http://localhost:12434/engines/llama.cpp/v1/chat/completions
GENERATION_MODEL_NAME=ai/llama3.2:1B-Q4_0

# Embedding Service
EMBEDDING_SERVICE_URL=http://localhost:12434/engines/llama.cpp/v1/embeddings
EMBEDDING_MODEL_NAME=ai/embeddinggemma:300M-Q8_0
```

### Legacy Configuration (Backward Compatible)

The system also supports legacy configuration variables for backward compatibility:

```bash
# These are used to construct service URLs if the new variables are not set
AI_MODEL_URL=http://localhost:12434
AI_MODEL_NAME=ai/llama3.2:1B-Q4_0
LLM_ENGINE=llama.cpp
EMBEDDING_MODEL_URL=http://localhost:12434
EMBEDDING_MODEL_NAME=ai/embeddinggemma:300M-Q8_0
```

## API Functions

### Text Generation

#### `generate_text_completion(messages, max_retries=3, timeout=30, **kwargs)`

Generate text completion using the configured LLM service.

**Parameters:**
- `messages` (List[Dict[str, str]]): List of message dicts with 'role' and 'content' keys following OpenAI chat format
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 30)
- `**kwargs`: Additional parameters to pass to the model API

**Returns:**
- `str`: Generated text content, or `None` if generation fails after all retries

**Example:**
```python
from gradeschoolmathsolver import model_access

messages = [
    {"role": "system", "content": "You are a math teacher."},
    {"role": "user", "content": "What is 5 + 3?"}
]
response = model_access.generate_text_completion(messages)
print(response)  # "5 + 3 equals 8"
```

### Embedding Generation

#### `generate_embedding(text, max_retries=3, timeout=30)`

Generate embedding vector for a single text input.

**Parameters:**
- `text` (str): Text string to embed
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 30)

**Returns:**
- `List[float]`: Embedding vector (list of floats), or `None` if generation fails

**Example:**
```python
from gradeschoolmathsolver import model_access

embedding = model_access.generate_embedding("What is 5 + 3?")
print(len(embedding))  # 768 (or whatever dimension the model uses)
print(embedding[:5])   # [0.1234, -0.5678, 0.9012, ...]
```

#### `generate_embeddings_batch(texts, max_retries=3, timeout=30)`

Generate embeddings for multiple texts in a single API call.

**Parameters:**
- `texts` (List[str]): List of text strings to embed
- `max_retries` (int): Maximum number of retry attempts (default: 3)
- `timeout` (int): Request timeout in seconds (default: 30)

**Returns:**
- `List[Optional[List[float]]]`: List of embedding vectors. Returns `None` for any text that is empty, invalid, or failed to embed. The output list length matches the input list length.

**Example:**
```python
from gradeschoolmathsolver import model_access

texts = ["What is 5 + 3?", "", "Calculate 10 - 4"]
embeddings = model_access.generate_embeddings_batch(texts)

print(len(embeddings))      # 3 - same as input
print(embeddings[0])        # [0.1, 0.2, 0.3, ...]
print(embeddings[1])        # None - empty string
print(embeddings[2])        # [0.4, 0.5, 0.6, ...]
```

### Service Availability

#### `is_embedding_service_available()`

Check if the embedding service is available.

**Returns:**
- `bool`: `True` if service is available, `False` otherwise

**Example:**
```python
from gradeschoolmathsolver import model_access

if model_access.is_embedding_service_available():
    embedding = model_access.generate_embedding("test")
else:
    print("Embedding service unavailable")
```

#### `is_generation_service_available()`

Check if the text generation service is available.

**Returns:**
- `bool`: `True` if service is available, `False` otherwise

**Example:**
```python
from gradeschoolmathsolver import model_access

if model_access.is_generation_service_available():
    messages = [{"role": "user", "content": "test"}]
    response = model_access.generate_text_completion(messages)
else:
    print("Generation service unavailable")
```

## Example Endpoint Usage

### Text Generation Endpoint

```bash
curl http://localhost:12434/engines/llama.cpp/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/llama3.2:1B-Q4_0",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Please write 500 words about the fall of Rome."
      }
    ]
  }'
```

### Embedding Endpoint

```bash
curl http://localhost:12434/engines/llama.cpp/v1/embeddings \
  -H "Content-Type: application/json" \
  -d '{
    "model": "ai/embeddinggemma:300M-Q8_0",
    "input": "Your text to embed here"
  }'
```

## Configuration Examples

### Using Docker Desktop Model Runner (Default)

Docker Desktop's Model Runner provides an OpenAI-compatible API at localhost:12434.

```bash
# .env file
GENERATION_SERVICE_URL=http://localhost:12434/engines/llama.cpp/v1/chat/completions
GENERATION_MODEL_NAME=ai/llama3.2:1B-Q4_0
EMBEDDING_SERVICE_URL=http://localhost:12434/engines/llama.cpp/v1/embeddings
EMBEDDING_MODEL_NAME=ai/embeddinggemma:300M-Q8_0
```

### Using Custom Model Service

If you're using a different model service or deployment:

```bash
# .env file
GENERATION_SERVICE_URL=http://custom-llm-server:8080/v1/completions
GENERATION_MODEL_NAME=custom-model-name
EMBEDDING_SERVICE_URL=http://custom-embedding-server:8080/v1/embeddings
EMBEDDING_MODEL_NAME=custom-embedding-model
```

### Using Ollama

If you're using Ollama for model hosting:

```bash
# .env file
GENERATION_SERVICE_URL=http://localhost:11434/v1/chat/completions
GENERATION_MODEL_NAME=llama3.2:1b
EMBEDDING_SERVICE_URL=http://localhost:11434/v1/embeddings
EMBEDDING_MODEL_NAME=nomic-embed-text
```

### Using OpenAI API

If you're using OpenAI's API directly:

```bash
# .env file
GENERATION_SERVICE_URL=https://api.openai.com/v1/chat/completions
GENERATION_MODEL_NAME=gpt-4
EMBEDDING_SERVICE_URL=https://api.openai.com/v1/embeddings
EMBEDDING_MODEL_NAME=text-embedding-3-small

# Note: You'll need to add authentication handling for OpenAI API
# This may require modifications to model_access.py to include API keys
```

## Error Handling

The model_access module includes robust error handling:

- **Automatic retries**: Failed requests are automatically retried up to `max_retries` times
- **Timeout handling**: Requests that take too long are aborted
- **Validation**: Input parameters are validated before making API calls
- **Logging**: Errors and retries are logged for debugging

## Integration with Existing Services

All existing services have been refactored to use the model_access module:

- **QA Generation Service**: Uses `generate_text_completion()` for generating word problems
- **Agent Service**: Uses `generate_text_completion()` for RAG bot answers
- **Teacher Service**: Uses `generate_text_completion()` for educational feedback
- **Classification Service**: Uses `generate_text_completion()` for AI-based classification
- **Embedding Service**: Uses `generate_embedding()` and `generate_embeddings_batch()` for vector generation

## Testing

The model_access module includes comprehensive tests. Run them with:

```bash
pytest tests/test_model_access.py -v
```

## Troubleshooting

### Service Unavailable

If you get errors about the service being unavailable:

1. Check that the model service is running:
   ```bash
   curl http://localhost:12434/engines/llama.cpp/v1/models
   ```

2. Verify your configuration in `.env`

3. Check service availability:
   ```python
   from gradeschoolmathsolver import model_access
   print(model_access.is_generation_service_available())
   print(model_access.is_embedding_service_available())
   ```

### Timeout Errors

If requests are timing out:

1. Increase the timeout parameter:
   ```python
   model_access.generate_text_completion(messages, timeout=60)
   ```

2. Check your model service performance

3. Consider using a smaller model if the current one is too slow

### Invalid Responses

If you're getting `None` responses:

1. Check the logs for error messages
2. Verify the model service is returning valid OpenAI-compatible responses
3. Test the endpoint directly with curl to see the raw response

## Migration Guide

If you have existing code that makes direct HTTP calls to model endpoints, here's how to migrate:

### Before (Direct HTTP calls)

```python
import requests

response = requests.post(
    f"{config.AI_MODEL_URL}/engines/{config.LLM_ENGINE}/v1/chat/completions",
    json={
        "model": config.AI_MODEL_NAME,
        "messages": messages
    },
    timeout=30
)
result = response.json()
content = result['choices'][0]['message']['content']
```

### After (Using model_access)

```python
from gradeschoolmathsolver import model_access

content = model_access.generate_text_completion(messages)
```

The new approach is:
- More concise
- Includes automatic retry logic
- Centrally configured
- Easier to test
- More maintainable
