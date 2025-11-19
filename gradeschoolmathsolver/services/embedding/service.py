"""
Embedding Service
Generates embeddings using Docker Model Runner for RAG capabilities
"""
import requests
from typing import Optional, List
from gradeschoolmathsolver.config import Config


class EmbeddingService:
    """Service for generating text embeddings using Docker Model Runner"""

    def __init__(self):
        self.config = Config()
        self.enabled = self.config.EMBEDDING_SERVICE_ENABLED
        self.model_url = self.config.EMBEDDING_MODEL_URL
        self.model_name = self.config.EMBEDDING_MODEL_NAME
        self.engine = self.config.EMBEDDING_ENGINE

    def generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding for a single text input

        Args:
            text: Text to generate embedding for

        Returns:
            List of floats representing the embedding vector, or None if service is disabled or fails
        """
        if not self.enabled:
            return None

        if not text or not text.strip():
            return None

        try:
            # Use OpenAI-compatible embeddings API format
            response = requests.post(
                f"{self.model_url}/engines/{self.engine}/v1/embeddings",
                json={
                    "model": self.model_name,
                    "input": text
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                # Extract embedding from OpenAI-compatible response
                data = result.get('data', [])
                if data and len(data) > 0:
                    embedding = data[0].get('embedding', [])
                    if embedding:
                        return embedding

        except requests.exceptions.Timeout:
            print(f"Timeout generating embedding for text: {text[:50]}...")
        except requests.exceptions.ConnectionError:
            print(f"Connection error: Unable to reach embedding service at {self.model_url}")
        except Exception as e:
            print(f"Error generating embedding: {e}")

        return None

    def generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        Generate embeddings for multiple text inputs

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors, or None if service is disabled or fails
        """
        if not self.enabled:
            return None

        if not texts or len(texts) == 0:
            return None

        try:
            # Use OpenAI-compatible embeddings API format with batch input
            response = requests.post(
                f"{self.model_url}/engines/{self.engine}/v1/embeddings",
                json={
                    "model": self.model_name,
                    "input": texts
                },
                timeout=60  # Longer timeout for batch processing
            )

            if response.status_code == 200:
                result = response.json()
                # Extract embeddings from OpenAI-compatible response
                data = result.get('data', [])
                if data and len(data) > 0:
                    embeddings = [item.get('embedding', []) for item in data]
                    if all(embeddings):  # Check all embeddings are valid
                        return embeddings

        except requests.exceptions.Timeout:
            print(f"Timeout generating embeddings for {len(texts)} texts")
        except requests.exceptions.ConnectionError:
            print(f"Connection error: Unable to reach embedding service at {self.model_url}")
        except Exception as e:
            print(f"Error generating embeddings: {e}")

        return None

    def get_embedding_dimension(self) -> Optional[int]:
        """
        Get the dimension of embeddings produced by the model

        Returns:
            Embedding dimension, or None if unable to determine
        """
        # Try to generate a test embedding to determine dimension
        test_embedding = self.generate_embedding("test")
        if test_embedding:
            return len(test_embedding)
        return None

    def is_available(self) -> bool:
        """
        Check if the embedding service is available and working

        Returns:
            True if service is enabled and accessible, False otherwise
        """
        if not self.enabled:
            return False

        try:
            # Try to generate a simple test embedding
            test_embedding = self.generate_embedding("test")
            return test_embedding is not None
        except Exception:
            return False


if __name__ == "__main__":
    # Test the service
    service = EmbeddingService()

    print("=" * 60)
    print("Embedding Service Test")
    print("=" * 60)
    print(f"Service Enabled: {service.enabled}")
    print(f"Model URL: {service.model_url}")
    print(f"Model Name: {service.model_name}")
    print(f"Engine: {service.engine}")
    print()

    if not service.enabled:
        print("Embedding service is disabled. Enable it in .env to test.")
    else:
        # Test single embedding generation
        print("\nTest 1: Single Embedding Generation")
        print("-" * 60)
        test_text = "What is five plus three?"
        print(f"Input: {test_text}")

        embedding = service.generate_embedding(test_text)
        if embedding:
            print("✅ Embedding generated successfully")
            print(f"   Dimension: {len(embedding)}")
            print(f"   First 5 values: {embedding[:5]}")
        else:
            print("❌ Failed to generate embedding")

        # Test batch embedding generation
        print("\n\nTest 2: Batch Embedding Generation")
        print("-" * 60)
        test_texts = [
            "What is five plus three?",
            "Calculate ten minus four",
            "What is six times seven?"
        ]
        print(f"Input: {len(test_texts)} texts")

        embeddings = service.generate_embeddings(test_texts)
        if embeddings:
            print("✅ Embeddings generated successfully")
            print(f"   Count: {len(embeddings)}")
            print(f"   Dimensions: {[len(emb) for emb in embeddings]}")
        else:
            print("❌ Failed to generate embeddings")

        # Test service availability
        print("\n\nTest 3: Service Availability")
        print("-" * 60)
        is_available = service.is_available()
        if is_available:
            print("✅ Embedding service is available")
            dimension = service.get_embedding_dimension()
            if dimension:
                print(f"   Embedding dimension: {dimension}")
        else:
            print("❌ Embedding service is not available")

    print("\n" + "=" * 60)
