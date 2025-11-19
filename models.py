"""
Data models for the GradeSchoolMathSolver-RAG system

DEPRECATED: This module has been moved to gradeschoolmathsolver.models
Please update your imports to use: from gradeschoolmathsolver.models import Question, UserAnswer, etc.
"""
import warnings
warnings.warn(
    "Importing from 'models' is deprecated. Use 'from gradeschoolmathsolver.models import ...' instead.",
    DeprecationWarning,
    stacklevel=2
)

from gradeschoolmathsolver.models import *  # noqa: F401, F403
