"""
Configuration settings for the GradeSchoolMathSolver-RAG system

DEPRECATED: This module has been moved to gradeschoolmathsolver.config
Please update your imports to use: from gradeschoolmathsolver.config import Config
"""
import warnings
warnings.warn(
    "Importing from 'config' is deprecated. Use 'from gradeschoolmathsolver.config import Config' instead.",
    DeprecationWarning,
    stacklevel=2
)

from gradeschoolmathsolver.config import *  # noqa: F401, F403
