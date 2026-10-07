"""Agentic AI LMS - AI engine package.

Pure-Python/LangChain/LangGraph library consumed by the FastAPI backend as
plain function/class calls (no HTTP boundary). This package is mostly
DB-read-only (RAG retrieval) or fully DB-agnostic (agents take plain dicts
in, return plain dicts out). It never performs DB writes itself.
"""
