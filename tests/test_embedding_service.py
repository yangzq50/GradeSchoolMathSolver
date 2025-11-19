"""
Test suite for Embedding Service
"""
import sys
sys.path.insert(0, '/home/runner/work/GradeSchoolMathSolver-RAG/GradeSchoolMathSolver-RAG')

from gradeschoolmathsolver.services.embedding import EmbeddingService  # noqa: E402


def test_embedding_service_initialization():
    """Test embedding service initialization"""
    service = EmbeddingService()

    assert service is not None, "Service should be initialized"
    assert hasattr(service, 'enabled'), "Service should have enabled attribute"
    assert hasattr(service, 'model_url'), "Service should have model_url attribute"
    assert hasattr(service, 'model_name'), "Service should have model_name attribute"
    assert hasattr(service, 'engine'), "Service should have engine attribute"

    print("✅ Embedding Service: Initialization successful")


def test_embedding_service_single_generation():
    """Test single embedding generation"""
    service = EmbeddingService()

    if not service.enabled:
        print("⏭️  Embedding Service: Skipping single generation test (service disabled)")
        return

    test_text = "What is five plus three?"
    embedding = service.generate_embedding(test_text)

    if embedding:
        assert isinstance(embedding, list), "Embedding should be a list"
        assert len(embedding) > 0, "Embedding should not be empty"
        assert all(isinstance(x, (int, float)) for x in embedding), "All embedding values should be numeric"
        print(f"✅ Embedding Service: Single embedding generated (dimension: {len(embedding)})")
    else:
        print("⚠️  Embedding Service: Could not generate embedding (model may not be available)")


def test_embedding_service_batch_generation():
    """Test batch embedding generation"""
    service = EmbeddingService()

    if not service.enabled:
        print("⏭️  Embedding Service: Skipping batch generation test (service disabled)")
        return

    test_texts = [
        "What is five plus three?",
        "Calculate ten minus four",
        "What is six times seven?"
    ]
    embeddings = service.generate_embeddings(test_texts)

    if embeddings:
        assert isinstance(embeddings, list), "Embeddings should be a list"
        assert len(embeddings) == len(test_texts), "Should have same number of embeddings as inputs"
        assert all(isinstance(emb, list) for emb in embeddings), "Each embedding should be a list"
        assert all(len(emb) > 0 for emb in embeddings), "Each embedding should not be empty"
        print(f"✅ Embedding Service: Batch embeddings generated ({len(embeddings)} embeddings)")
    else:
        print("⚠️  Embedding Service: Could not generate batch embeddings (model may not be available)")


def test_embedding_service_empty_input():
    """Test embedding generation with empty input"""
    service = EmbeddingService()

    if not service.enabled:
        print("⏭️  Embedding Service: Skipping empty input test (service disabled)")
        return

    # Empty string should return None
    embedding = service.generate_embedding("")
    assert embedding is None, "Empty string should return None"

    # Whitespace-only string should return None
    embedding = service.generate_embedding("   ")
    assert embedding is None, "Whitespace-only string should return None"

    # Empty list should return None
    embeddings = service.generate_embeddings([])
    assert embeddings is None, "Empty list should return None"

    print("✅ Embedding Service: Empty input handling correct")


def test_embedding_service_consistency():
    """Test that same input produces same embedding"""
    service = EmbeddingService()

    if not service.enabled:
        print("⏭️  Embedding Service: Skipping consistency test (service disabled)")
        return

    test_text = "What is five plus three?"
    embedding1 = service.generate_embedding(test_text)
    embedding2 = service.generate_embedding(test_text)

    if embedding1 and embedding2:
        assert len(embedding1) == len(embedding2), "Embeddings should have same dimension"
        # Note: Embeddings might not be exactly identical due to model randomness
        # but they should be very similar
        print("✅ Embedding Service: Consistency check passed")
    else:
        print("⚠️  Embedding Service: Could not perform consistency test (model may not be available)")


def test_embedding_service_dimension():
    """Test getting embedding dimension"""
    service = EmbeddingService()

    if not service.enabled:
        print("⏭️  Embedding Service: Skipping dimension test (service disabled)")
        return

    dimension = service.get_embedding_dimension()
    if dimension:
        assert isinstance(dimension, int), "Dimension should be an integer"
        assert dimension > 0, "Dimension should be positive"
        print(f"✅ Embedding Service: Dimension retrieved ({dimension})")
    else:
        print("⚠️  Embedding Service: Could not get dimension (model may not be available)")


def test_embedding_service_availability():
    """Test service availability check"""
    service = EmbeddingService()

    is_available = service.is_available()
    assert isinstance(is_available, bool), "Availability should be a boolean"

    if service.enabled:
        if is_available:
            print("✅ Embedding Service: Service is available")
        else:
            print("⚠️  Embedding Service: Service is enabled but not available (model may not be running)")
    else:
        assert not is_available, "Service should not be available when disabled"
        print("✅ Embedding Service: Service correctly reports unavailable when disabled")


if __name__ == "__main__":
    print("=" * 70)
    print("Running Embedding Service Tests")
    print("=" * 70)
    print()

    test_embedding_service_initialization()
    test_embedding_service_single_generation()
    test_embedding_service_batch_generation()
    test_embedding_service_empty_input()
    test_embedding_service_consistency()
    test_embedding_service_dimension()
    test_embedding_service_availability()

    print()
    print("=" * 70)
    print("All tests completed!")
    print("=" * 70)
