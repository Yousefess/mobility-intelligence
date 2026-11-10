# Mobility Intelligence

A trajectory analysis copilot: natural-language Q&A over GPS trajectory data (GeoLife dataset),
combining a SQL/Geo agent (PostGIS) and a RAG agent (urban mobility documents) orchestrated
with LangGraph.

## Stack

FastAPI, PostgreSQL 16 + PostGIS + pgvector, SQLAlchemy, Alembic, LangGraph, LangChain (core),
OpenAI-compatible client (Groq primary, OpenRouter fallback), Docker.

## Status

Work in progress — see `docs/` for design notes.
