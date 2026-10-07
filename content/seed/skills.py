"""
Canonical skill graph for the Agentic AI LMS.

Every lesson / question / project in content/seed/** must reference skills by
`slug` from this file ONLY. Do not invent new skill slugs in course content —
if a new skill is genuinely needed, add it here first so the graph stays
consistent across courses.

Each entry: slug, name, description, category, parent (slug or None),
prerequisites: list of (slug, required_mastery) that must be met before this
skill is considered "unlocked" for a student.
"""

SKILLS = [
    # --- Foundations ---
    {"slug": "python", "name": "Python", "category": "foundations",
     "description": "Core Python programming: syntax, data structures, functions, OOP, and the language features used to build AI applications.",
     "parent": None, "prerequisites": []},
    {"slug": "ai-ml", "name": "AI & Machine Learning", "category": "foundations",
     "description": "Foundational machine learning concepts: supervised/unsupervised learning, model evaluation, and feature engineering.",
     "parent": None, "prerequisites": [("python", 0.5)]},

    # --- LLM branch ---
    {"slug": "llm", "name": "Large Language Models", "category": "llm",
     "description": "How LLMs work: tokens, context windows, transformers, inference, and their practical limitations.",
     "parent": None, "prerequisites": [("ai-ml", 0.4)]},
    {"slug": "tokens", "name": "Tokens & Tokenization", "category": "llm",
     "description": "How text is broken into tokens and why this matters for cost, context limits, and model behavior.",
     "parent": "llm", "prerequisites": []},
    {"slug": "transformers", "name": "Transformer Architecture", "category": "llm",
     "description": "Attention mechanisms and the transformer architecture underlying modern LLMs.",
     "parent": "llm", "prerequisites": [("tokens", 0.3)]},
    {"slug": "prompt-engineering", "name": "Prompt Engineering", "category": "llm",
     "description": "Designing prompts that reliably elicit correct, structured, and safe model behavior.",
     "parent": "llm", "prerequisites": [("llm", 0.4)]},

    # --- RAG branch ---
    {"slug": "embeddings", "name": "Embeddings", "category": "rag",
     "description": "Vector representations of text and how semantic similarity is computed and used.",
     "parent": None, "prerequisites": [("ai-ml", 0.3)]},
    {"slug": "chunking", "name": "Chunking", "category": "rag",
     "description": "Splitting documents into retrieval-friendly units without losing meaning.",
     "parent": "embeddings", "prerequisites": []},
    {"slug": "retrieval", "name": "Retrieval", "category": "rag",
     "description": "Finding the most relevant pieces of content for a query using vector and hybrid search.",
     "parent": "embeddings", "prerequisites": [("embeddings", 0.4)]},
    {"slug": "vector-db", "name": "Vector Databases", "category": "rag",
     "description": "Storing, indexing, and filtering embeddings at scale (FAISS, Chroma, Pinecone-style systems).",
     "parent": "embeddings", "prerequisites": [("embeddings", 0.4)]},
    {"slug": "reranking", "name": "Reranking", "category": "rag",
     "description": "Improving retrieval precision by re-scoring candidate results before generation.",
     "parent": "retrieval", "prerequisites": [("retrieval", 0.5)]},
    {"slug": "rag", "name": "Retrieval Augmented Generation", "category": "rag",
     "description": "The end-to-end pipeline that grounds LLM generation in retrieved, trustworthy content.",
     "parent": None, "prerequisites": [("retrieval", 0.5), ("vector-db", 0.4), ("prompt-engineering", 0.4)]},

    # --- Agents branch ---
    {"slug": "agents", "name": "AI Agents", "category": "agents",
     "description": "Systems that reason, plan, and take actions using tools rather than just answering in one shot.",
     "parent": None, "prerequisites": [("prompt-engineering", 0.5)]},
    {"slug": "tools", "name": "Tools", "category": "agents",
     "description": "Defining external capabilities (functions, APIs) that an agent can invoke.",
     "parent": "agents", "prerequisites": []},
    {"slug": "tool-calling", "name": "Tool Calling", "category": "agents",
     "description": "Structured function/tool calling so a model can request actions with typed arguments.",
     "parent": "tools", "prerequisites": [("tools", 0.4)]},
    {"slug": "memory", "name": "Agent Memory", "category": "agents",
     "description": "Short-term and long-term memory architectures that let agents retain and reuse context.",
     "parent": "agents", "prerequisites": [("agents", 0.3)]},
    {"slug": "planning", "name": "Planning", "category": "agents",
     "description": "Decomposing goals into ordered steps and adapting plans as new information arrives.",
     "parent": "agents", "prerequisites": [("agents", 0.3)]},
    {"slug": "reflection", "name": "Reflection", "category": "agents",
     "description": "Self-critique and self-correction loops that improve agent output quality.",
     "parent": "agents", "prerequisites": [("planning", 0.3)]},
    {"slug": "state", "name": "Agent State", "category": "agents",
     "description": "Modeling and persisting the evolving state of a multi-step agent workflow.",
     "parent": "agents", "prerequisites": [("agents", 0.3)]},

    # --- Frameworks ---
    {"slug": "langchain", "name": "LangChain", "category": "frameworks",
     "description": "Building LLM applications with LangChain's models, prompts, tools, retrieval, and memory abstractions.",
     "parent": None, "prerequisites": [("tool-calling", 0.4), ("prompt-engineering", 0.4)]},
    {"slug": "langgraph", "name": "LangGraph", "category": "frameworks",
     "description": "Stateful, graph-based orchestration of agent workflows with branching, loops, and checkpoints.",
     "parent": None, "prerequisites": [("langchain", 0.4), ("state", 0.4)]},

    # --- Systems ---
    {"slug": "multi-agent-systems", "name": "Multi-Agent Systems", "category": "systems",
     "description": "Coordinating multiple specialized agents through supervision, delegation, and shared state.",
     "parent": None, "prerequisites": [("langgraph", 0.4), ("memory", 0.3)]},
    {"slug": "evaluation", "name": "Agent Evaluation & Safety", "category": "systems",
     "description": "Measuring reliability, grounding, and safety of AI agents, and defending against misuse.",
     "parent": None, "prerequisites": [("rag", 0.3), ("agents", 0.4)]},
    {"slug": "production-ai", "name": "Production AI", "category": "systems",
     "description": "Shipping AI agents as reliable services: APIs, auth, caching, monitoring, and cost control.",
     "parent": None, "prerequisites": [("python", 0.5), ("agents", 0.4)]},
]

SKILL_SLUGS = {s["slug"] for s in SKILLS}
