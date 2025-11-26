"""
Quiz History Service
Manages quiz history using centralized database service for RAG (Retrieval-Augmented Generation)

This service provides:
- Storage of question-answer pairs with vector embeddings
- Similarity-based search for relevant historical questions
- User history retrieval
- Graceful degradation when database is unavailable

Embedding Generation:
The service generates embeddings for configured source columns (e.g., 'question', 'equation')
and stores them in corresponding embedding columns for vector similarity search.

For MariaDB: Embeddings are stored in separate tables (one per embedding column) because
MariaDB doesn't support multiple VECTOR indexes on the same table.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from gradeschoolmathsolver.config import Config
from gradeschoolmathsolver.models import QuizHistory
from gradeschoolmathsolver.services.database import get_database_service
from gradeschoolmathsolver.services.database.schemas import (
    get_answer_history_schema_for_backend,
    get_embedding_source_mapping,
    get_embedding_config,
    get_embedding_table_schemas_mariadb,
    get_embedding_table_name
)


class QuizHistoryService:
    """
    Service for managing quiz history with centralized database service

    This service handles quiz history storage and retrieval for RAG functionality.
    It gracefully degrades to limited mode when database is unavailable.

    Embedding Support:
    The service automatically generates embeddings for source text columns
    (configured via EMBEDDING_SOURCE_COLUMNS) when adding history records.
    These embeddings enable vector similarity search for RAG.

    For MariaDB, embeddings are stored in separate tables (one per embedding column)
    because MariaDB doesn't support multiple VECTOR indexes on the same table.

    Attributes:
        config: Configuration object
        index_name: Name of the database index
        db: DatabaseService instance for data operations
        embedding_service: EmbeddingService for generating vector embeddings
        source_to_embedding_map: Mapping from source columns to embedding columns
    """

    def __init__(self):
        self.config = Config()
        self.index_name = self.config.ELASTICSEARCH_INDEX
        self.db = get_database_service()
        self.embedding_service = None
        self.source_to_embedding_map = get_embedding_source_mapping()
        self._create_index()

    def _get_embedding_service(self):
        """
        Lazy-load the embedding service to avoid circular imports
        and allow graceful degradation when service is unavailable.

        Returns:
            EmbeddingService instance or None if unavailable
        """
        if self.embedding_service is None:
            try:
                from gradeschoolmathsolver.services.embedding import EmbeddingService
                self.embedding_service = EmbeddingService()
            except Exception as e:
                print(f"Warning: Could not initialize embedding service: {e}")
                return None
        return self.embedding_service

    def _create_index(self):
        """
        Create database index with appropriate mappings including embedding columns

        Uses the centralized schema definition from schemas.py which includes
        both standard fields and embedding columns for vector search.

        For MariaDB: Creates separate tables for each embedding column because
        MariaDB doesn't support multiple VECTOR indexes on the same table.
        """
        # Get the full schema with embeddings for the configured backend
        schema = get_answer_history_schema_for_backend(
            self.config.DATABASE_BACKEND,
            include_embeddings=True
        )

        # Create the main collection
        self.db.create_collection(self.index_name, schema)

        # For MariaDB, also create separate embedding tables
        if self.config.DATABASE_BACKEND == 'mariadb':
            embedding_config = get_embedding_config()
            embedding_tables = get_embedding_table_schemas_mariadb(
                self.index_name,
                embedding_config
            )
            for table_name, table_schema in embedding_tables.items():
                self.db.create_collection(table_name, table_schema)

    def add_history(self, history: QuizHistory) -> bool:
        """
        Add a quiz history record to database with vector embeddings

        This method generates embeddings from configured source text columns
        (e.g., 'question' and 'equation') and stores them in the corresponding
        embedding columns for vector similarity search.

        The source-to-embedding mapping is configured via:
        - EMBEDDING_SOURCE_COLUMNS: Source text columns (default: 'question,equation')
        - EMBEDDING_COLUMN_NAMES: Embedding columns (default: 'question_embedding,equation_embedding')

        For MariaDB: Embeddings are stored in separate tables (one per embedding column).

        Args:
            history: QuizHistory object to store

        Returns:
            True if successful, False if database unavailable or error occurs
        """
        if not self.db.is_connected():
            return False

        try:
            # Build the base document
            doc: Dict[str, Any] = {
                "username": history.username,
                "question": history.question,
                "equation": history.user_equation,  # Store as equation
                "user_equation": history.user_equation,  # Keep for backward compatibility
                "user_answer": history.user_answer,
                "correct_answer": history.correct_answer,
                "is_correct": history.is_correct,
                "category": history.category,
                "timestamp": history.timestamp.isoformat(),
                "reviewed": False  # Default value for new records
            }

            # Generate embeddings
            embeddings = self._generate_embeddings(history)

            if self.config.DATABASE_BACKEND == 'mariadb':
                # For MariaDB: Insert main record first, then embeddings in separate tables
                doc_id = self.db.insert_record(self.index_name, doc)
                if doc_id is None:
                    return False

                # Insert embeddings into separate tables
                for embedding_col, embedding in embeddings.items():
                    table_name = get_embedding_table_name(self.index_name, embedding_col)
                    embedding_doc = {
                        "record_id": doc_id,
                        "embedding": embedding
                    }
                    self.db.insert_record(table_name, embedding_doc)
            else:
                # For Elasticsearch: Add embeddings to main document
                doc.update(embeddings)
                doc_id = self.db.insert_record(self.index_name, doc)

            return doc_id is not None
        except Exception as e:
            print(f"Error adding history: {e}")
            return False

    def _generate_embeddings(self, history: QuizHistory) -> Dict[str, List[float]]:
        """
        Generate embeddings for all configured source columns.

        Args:
            history: QuizHistory object containing source text data

        Returns:
            Dict mapping embedding column name to embedding vector

        Raises:
            RuntimeError: If embedding service is unavailable or embedding generation fails.
        """
        embedding_service = self._get_embedding_service()
        if embedding_service is None:
            raise RuntimeError(
                "Embedding service is unavailable. Cannot add quiz history without authentic embeddings. "
                "Please ensure the embedding service is running and accessible."
            )

        # Map source column names to their values from the history object
        source_values = {
            'question': history.question,
            'equation': history.user_equation,
        }

        embeddings = {}
        for source_col, embedding_col in self.source_to_embedding_map.items():
            source_text = source_values.get(source_col, '')
            if not source_text:
                raise RuntimeError(
                    f"Cannot generate embedding for column '{embedding_col}': "
                    f"source column '{source_col}' is empty or not found."
                )

            embedding = self._generate_single_embedding(embedding_service, source_col, embedding_col, source_text)
            embeddings[embedding_col] = embedding

        return embeddings

    def _generate_single_embedding(
        self,
        embedding_service: Any,
        source_col: str,
        embedding_col: str,
        source_text: str
    ) -> List[float]:
        """
        Generate a single embedding for a source text.

        Args:
            embedding_service: The embedding service instance
            source_col: Name of the source column
            embedding_col: Name of the embedding column
            source_text: Text to generate embedding for

        Returns:
            Embedding vector as list of floats

        Raises:
            RuntimeError: If embedding generation fails
        """
        try:
            embedding = embedding_service.generate_embedding(source_text)
        except Exception as e:
            raise RuntimeError(
                f"Failed to generate embedding for column '{embedding_col}' "
                f"from source column '{source_col}': {e}"
            ) from e

        if embedding is None:
            raise RuntimeError(
                f"Embedding service returned None for column '{embedding_col}' "
                f"from source column '{source_col}'."
            )

        return list(embedding)

    def search_relevant_history(self, username: str, question: str,
                                category: Optional[str] = None,
                                top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for relevant quiz history using semantic similarity

        Uses database text matching to find similar questions from
        the user's history, optionally filtered by category.

        Args:
            username: Username to search for
            question: Question text for similarity search
            category: Optional category filter
            top_k: Number of results to return (1-20)

        Returns:
            List of relevant history records with scores, empty if unavailable
        """
        if not self.db.is_connected():
            return []

        # Validate and clamp top_k
        top_k = max(1, min(top_k, 20))

        try:
            # Build query - this is Elasticsearch-specific but abstracted in the future
            must_clauses = [
                {"match": {"username": username}}
            ]

            should_clauses = [
                {"match": {"question": {"query": question, "boost": 2}}},
                {"match": {"user_equation": question}}
            ]

            if category:
                must_clauses.append({"term": {"category": category}})

            query = {
                "bool": {
                    "must": must_clauses,
                    "should": should_clauses
                }
            }

            sort = [
                {"_score": {"order": "desc"}},
                {"timestamp": {"order": "desc"}}
            ]

            # Use database service search
            hits = self.db.search_records(
                collection_name=self.index_name,
                query=query,
                sort=sort,
                limit=top_k
            )

            return self._format_search_results(hits)
        except Exception as e:
            print(f"Error searching history: {e}")
            return []

    def _format_search_results(self, hits: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Format search hits into result dictionaries."""
        results = []
        for hit in hits:
            source = hit['_source']
            results.append({
                'question': source.get('question'),
                'user_equation': source.get('user_equation'),
                'user_answer': source.get('user_answer'),
                'correct_answer': source.get('correct_answer'),
                'is_correct': source.get('is_correct'),
                'category': source.get('category'),
                'timestamp': source.get('timestamp'),
                'score': hit.get('_score', 0)
            })
        return results

    def get_user_history(self, username: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get all history for a user

        Args:
            username: Username to retrieve history for
            limit: Maximum number of records (1-1000)

        Returns:
            List of history records sorted by timestamp, empty if unavailable
        """
        if not self.db.is_connected():
            return []

        # Validate and clamp limit
        limit = max(1, min(limit, 1000))

        try:
            query = {"match": {"username": username}}
            sort = [{"timestamp": {"order": "desc"}}]

            hits = self.db.search_records(
                collection_name=self.index_name,
                query=query,
                sort=sort,
                limit=limit
            )

            results = []
            for hit in hits:
                source = hit['_source']
                results.append(source)

            return results
        except Exception as e:
            print(f"Error getting user history: {e}")
            return []

    def is_connected(self) -> bool:
        """
        Check if database is connected and responsive

        Returns:
            True if connected and responsive, False otherwise
        """
        return bool(self.db.is_connected())


if __name__ == "__main__":
    # Test the service
    service = QuizHistoryService()

    if service.is_connected():
        print("Connected to Elasticsearch")

        # Add test history
        history = QuizHistory(
            username="test_user",
            question="What is 5 + 3?",
            user_equation="5 + 3",
            user_answer=8,
            correct_answer=8,
            is_correct=True,
            category="addition",
            timestamp=datetime.now()
        )

        service.add_history(history)
        print("Added test history")

        # Search
        results = service.search_relevant_history(
            "test_user",
            "What is 6 + 2?",
            top_k=3
        )
        print(f"Found {len(results)} relevant records")
    else:
        print("Not connected to Elasticsearch - service in limited mode")
