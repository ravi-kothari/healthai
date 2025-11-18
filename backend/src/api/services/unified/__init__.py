"""
Unified PreVisit + Appoint-Ready services.

This package provides the data transformation layer that creates
a seamless patient experience by combining PreVisit.ai and Appoint-Ready
data into patient-friendly summaries.
"""

from src.api.services.unified.data_transformer import data_transformer

__all__ = ["data_transformer"]
