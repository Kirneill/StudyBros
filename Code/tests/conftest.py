"""
Pytest fixtures for Study Guide tests.
"""

import tempfile
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from study_guide.database.models import Base
from study_guide.database.operations import DatabaseOperations


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def test_db():
    """Create an in-memory test database."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


@pytest.fixture
def db_ops(test_db):
    """Create database operations instance."""
    return DatabaseOperations(test_db)


@pytest.fixture
def sample_text():
    """Sample text content for testing."""
    return """
# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Types of Machine Learning

### Supervised Learning

In supervised learning, the algorithm learns from labeled training data. The model makes predictions based on the input data and is corrected when predictions are wrong.

Examples include:
- Classification (spam detection, image recognition)
- Regression (price prediction, weather forecasting)

### Unsupervised Learning

Unsupervised learning works with unlabeled data. The algorithm tries to find patterns and structures in the data without prior knowledge of outcomes.

Examples include:
- Clustering (customer segmentation)
- Dimensionality reduction (PCA)

### Reinforcement Learning

In reinforcement learning, an agent learns to make decisions by performing actions and receiving rewards or penalties.

## Key Concepts

**Training Data**: The dataset used to train the model.

**Features**: The input variables used for prediction.

**Labels**: The output variables the model tries to predict.

**Model**: The mathematical representation learned from data.

**Overfitting**: When a model performs well on training data but poorly on new data.

**Underfitting**: When a model is too simple to capture the underlying pattern.
"""


@pytest.fixture
def sample_flashcards():
    """Sample flashcard content for testing."""
    return {
        "cards": [
            {
                "question": "What is machine learning?",
                "answer": "A subset of AI that enables systems to learn from experience.",
                "tags": ["ml", "basics"],
                "difficulty": "easy",
            },
            {
                "question": "What is supervised learning?",
                "answer": "Learning from labeled training data with known outcomes.",
                "tags": ["ml", "supervised"],
                "difficulty": "medium",
            },
        ]
    }


@pytest.fixture
def sample_quiz():
    """Sample quiz content for testing."""
    return {
        "questions": [
            {
                "prompt": "Which type of learning uses labeled data?",
                "options": [
                    {"label": "A", "text": "Unsupervised Learning"},
                    {"label": "B", "text": "Supervised Learning"},
                    {"label": "C", "text": "Reinforcement Learning"},
                    {"label": "D", "text": "Semi-supervised Learning"},
                ],
                "correct_index": 1,
                "explanation": "Supervised learning uses labeled training data.",
            }
        ]
    }


@pytest.fixture
def sample_audio_summary():
    """Sample audio summary content for testing."""
    return {
        "title": "Machine Learning Overview",
        "overview": "Machine learning is a subset of artificial intelligence that enables systems to learn from data. This summary covers the main types of machine learning and their applications.",
        "key_concepts": [
            {
                "concept": "Supervised Learning",
                "explanation": "Learning from labeled training data where the correct outputs are known.",
                "importance": "essential",
            },
            {
                "concept": "Unsupervised Learning",
                "explanation": "Finding patterns in unlabeled data without predefined outcomes.",
                "importance": "important",
            },
            {
                "concept": "Reinforcement Learning",
                "explanation": "Learning through interaction with an environment and receiving rewards.",
                "importance": "important",
            },
        ],
        "main_points": [
            "Machine learning enables computers to learn from experience.",
            "Supervised learning uses labeled data for training.",
            "Unsupervised learning discovers hidden patterns.",
            "Model evaluation is critical for success.",
        ],
        "conclusion": "Understanding the different types of machine learning helps you choose the right approach for your problem.",
        "estimated_read_time_seconds": 120,
    }


@pytest.fixture
def test_data_dir():
    """Path to test data directory."""
    return Path(__file__).parent / "test_data"
