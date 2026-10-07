"""
The onboarding diagnostic assessment. One question set covering every
top-level skill category so a brand-new student's initial skill profile can
be estimated across the whole curriculum in a single sitting (~20-25 min).
"""

DIAGNOSTIC_ASSESSMENT = {
    "title": "Agentic AI LMS Diagnostic Assessment",
    "description": (
        "A short diagnostic covering Python, AI/ML, LLMs, Prompt Engineering, Embeddings, RAG, "
        "Agents, Tool Calling, Memory, LangChain, and LangGraph. There's no passing/failing grade — "
        "it builds your starting skill profile so the AI planner can personalize your path through the curriculum."
    ),
    "assessment_type": "diagnostic",
    "passing_score": 0.0,
    "time_limit_minutes": 30,
    "questions": [
        # --- Python (3) ---
        {
            "question_type": "mcq", "skill_slug": "python", "difficulty": "easy", "points": 1.0,
            "prompt": "Which data structure would you use to store unique items with no guaranteed order in Python?",
            "options": [{"id": "a", "text": "list"}, {"id": "b", "text": "set"}, {"id": "c", "text": "tuple"}, {"id": "d", "text": "str"}],
            "correct_answer": {"choice": "b"},
            "explanation": "A `set` stores unique, unordered items and provides O(1) average membership checks.",
        },
        {
            "question_type": "mcq", "skill_slug": "python", "difficulty": "medium", "points": 1.0,
            "prompt": "What does the `async`/`await` pair primarily let a Python program do?",
            "options": [
                {"id": "a", "text": "Run CPU-bound code faster using multiple cores"},
                {"id": "b", "text": "Pause a coroutine at I/O-bound points so other work can run concurrently"},
                {"id": "c", "text": "Automatically parallelize loops"},
                {"id": "d", "text": "Prevent all exceptions from propagating"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "`async`/`await` enables cooperative concurrency for I/O-bound work (like calling an LLM API), not CPU parallelism.",
        },
        {
            "question_type": "coding", "skill_slug": "python", "difficulty": "medium", "points": 1.0,
            "prompt": "Write a Python function `chunk(items, size)` that yields successive lists of at most `size` items from `items`.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "A generator/function that splits a list into consecutive sublists of length <= size, covering all input items in order.",
                "sample_solution": "def chunk(items, size):\n    for i in range(0, len(items), size):\n        yield items[i:i + size]",
            },
            "explanation": "Slicing with a step of `size` is the idiomatic way to batch a sequence — this pattern shows up constantly when chunking documents for RAG.",
        },

        # --- AI/ML (3) ---
        {
            "question_type": "mcq", "skill_slug": "ai-ml", "difficulty": "easy", "points": 1.0,
            "prompt": "In supervised learning, what does the model learn from during training?",
            "options": [
                {"id": "a", "text": "Labeled input-output pairs"},
                {"id": "b", "text": "Only unlabeled inputs"},
                {"id": "c", "text": "Random noise"},
                {"id": "d", "text": "Rewards from an environment"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Supervised learning fits a model to labeled examples so it can predict labels for new inputs.",
        },
        {
            "question_type": "multi_select", "skill_slug": "ai-ml", "difficulty": "medium", "points": 1.0,
            "prompt": "Which of the following are common causes of overfitting? (Select all that apply)",
            "options": [
                {"id": "a", "text": "Too few training examples relative to model complexity"},
                {"id": "b", "text": "Training for too many epochs without regularization"},
                {"id": "c", "text": "Using a validation set"},
                {"id": "d", "text": "A model with excessive capacity for the problem size"},
            ],
            "correct_answer": {"choices": ["a", "b", "d"]},
            "explanation": "Overfitting comes from a model memorizing training data instead of generalizing — small datasets, too much capacity, and excessive training all contribute; a validation set is a tool to *detect* it, not a cause.",
        },
        {
            "question_type": "short_answer", "skill_slug": "ai-ml", "difficulty": "medium", "points": 1.0,
            "prompt": "In one or two sentences, explain why you'd hold out a separate test set instead of evaluating a model only on its training data.",
            "options": [],
            "correct_answer": {
                "expected": "A held-out test set measures how well the model generalizes to unseen data, since training accuracy alone can hide overfitting.",
                "keywords": ["generalize", "unseen", "overfit", "test set", "held out"],
            },
            "explanation": "Training performance reflects memorization risk; a held-out set approximates real-world performance on new data.",
        },

        # --- LLMs (3) ---
        {
            "question_type": "mcq", "skill_slug": "llm", "difficulty": "easy", "points": 1.0,
            "prompt": "A model's 'context window' refers to:",
            "options": [
                {"id": "a", "text": "The maximum number of tokens it can consider at once (input + output)"},
                {"id": "b", "text": "The number of GPUs used to train it"},
                {"id": "c", "text": "The size of its training dataset"},
                {"id": "d", "text": "The number of layers in the network"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "The context window bounds how much text (in tokens) the model can attend to in a single call.",
        },
        {
            "question_type": "mcq", "skill_slug": "llm", "difficulty": "medium", "points": 1.0,
            "prompt": "Raising the `temperature` parameter when sampling from an LLM generally:",
            "options": [
                {"id": "a", "text": "Makes output more deterministic and repetitive"},
                {"id": "b", "text": "Increases randomness/diversity in the generated tokens"},
                {"id": "c", "text": "Increases the context window size"},
                {"id": "d", "text": "Has no effect on generation"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Temperature scales the probability distribution before sampling; higher values flatten it, increasing diversity (and risk of incoherence).",
        },
        {
            "question_type": "scenario", "skill_slug": "llm", "difficulty": "hard", "points": 1.0,
            "prompt": "An LLM confidently states a fact that turns out to be false, with no indication of uncertainty. What is this behavior called, and what's one practical mitigation?",
            "options": [],
            "correct_answer": {
                "expected": "This is a hallucination. Mitigations include grounding responses in retrieved/verified sources (RAG), lowering temperature, and asking the model to cite sources or express uncertainty.",
            },
            "explanation": "Hallucination is a core LLM limitation; grounding generation in retrieved evidence (RAG) is the most reliable production mitigation.",
        },

        # --- Prompt Engineering (2) ---
        {
            "question_type": "mcq", "skill_slug": "prompt-engineering", "difficulty": "easy", "points": 1.0,
            "prompt": "Providing a few labeled input/output examples inside the prompt before the real task is called:",
            "options": [{"id": "a", "text": "Zero-shot prompting"}, {"id": "b", "text": "Few-shot prompting"}, {"id": "c", "text": "Fine-tuning"}, {"id": "d", "text": "Chunking"}],
            "correct_answer": {"choice": "b"},
            "explanation": "Few-shot prompting demonstrates the desired pattern with examples directly in-context.",
        },
        {
            "question_type": "short_answer", "skill_slug": "prompt-engineering", "difficulty": "medium", "points": 1.0,
            "prompt": "Why does explicitly asking a model to 'respond with valid JSON matching this schema: {...}' tend to produce more reliable structured output than just asking for 'a JSON response'?",
            "options": [],
            "correct_answer": {
                "expected": "Giving an explicit schema/example constrains the model's output format and reduces ambiguity, making downstream parsing more reliable.",
                "keywords": ["schema", "constrain", "format", "parse", "ambiguity"],
            },
            "explanation": "Explicit schemas and examples reduce the space of plausible outputs, which is exactly what structured-output prompting relies on.",
        },

        # --- Embeddings (2) ---
        {
            "question_type": "mcq", "skill_slug": "embeddings", "difficulty": "easy", "points": 1.0,
            "prompt": "Cosine similarity between two embedding vectors measures:",
            "options": [
                {"id": "a", "text": "The angle between them, indicating semantic closeness regardless of magnitude"},
                {"id": "b", "text": "Their exact numeric difference"},
                {"id": "c", "text": "How many dimensions they share"},
                {"id": "d", "text": "Which vector was created first"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Cosine similarity is the cosine of the angle between vectors — high similarity means they point in a similar direction (semantically close), independent of length.",
        },
        {
            "question_type": "mcq", "skill_slug": "embeddings", "difficulty": "medium", "points": 1.0,
            "prompt": "Two sentences with very different wording but the same meaning should generally have embeddings that are:",
            "options": [
                {"id": "a", "text": "Identical"}, {"id": "b", "text": "Close together in vector space"},
                {"id": "c", "text": "Maximally far apart"}, {"id": "d", "text": "Unrelated"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A good embedding model captures semantic meaning, not surface wording, so paraphrases land close together.",
        },

        # --- RAG (3) ---
        {
            "question_type": "mcq", "skill_slug": "rag", "difficulty": "easy", "points": 1.0,
            "prompt": "RAG stands for:",
            "options": [
                {"id": "a", "text": "Retrieval Augmented Generation"}, {"id": "b", "text": "Random Access Generation"},
                {"id": "c", "text": "Recursive Agent Graph"}, {"id": "d", "text": "Ranked Answer Grouping"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "RAG grounds an LLM's generation step in content retrieved from an external knowledge source.",
        },
        {
            "question_type": "mcq", "skill_slug": "rag", "difficulty": "medium", "points": 1.0,
            "prompt": "Why do RAG pipelines typically chunk documents before embedding them?",
            "options": [
                {"id": "a", "text": "Chunking is required by law for AI systems"},
                {"id": "b", "text": "Smaller, focused chunks retrieve more precisely and fit within context limits"},
                {"id": "c", "text": "It makes embeddings faster to compute regardless of retrieval quality"},
                {"id": "d", "text": "It removes the need for a vector database"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Chunking balances retrieval precision (smaller, focused units) against needing enough context to be meaningful, and keeps retrieved content within the model's context window.",
        },
        {
            "question_type": "scenario", "skill_slug": "rag", "difficulty": "hard", "points": 1.0,
            "prompt": "Your RAG system retrieves technically relevant chunks, but the generated answer still misses the point of the question. Name one technique that could improve result quality between retrieval and generation.",
            "options": [],
            "correct_answer": {"expected": "Reranking the retrieved candidates with a cross-encoder (or similar) before passing the top results to the generator, or using hybrid search to improve the initial candidate set."},
            "explanation": "Reranking re-scores retrieved candidates with a more expensive, more accurate model, improving precision beyond the initial (often approximate) vector search.",
        },

        # --- Agents (3) ---
        {
            "question_type": "mcq", "skill_slug": "agents", "difficulty": "easy", "points": 1.0,
            "prompt": "What most distinguishes an AI agent from a simple single-turn chatbot?",
            "options": [
                {"id": "a", "text": "Agents can reason, plan, and take multi-step actions using tools"},
                {"id": "b", "text": "Agents always use a larger model"},
                {"id": "c", "text": "Chatbots cannot use natural language"},
                {"id": "d", "text": "There is no meaningful difference"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Agents loop through reasoning and action steps, often invoking tools, rather than producing one response and stopping.",
        },
        {
            "question_type": "mcq", "skill_slug": "agents", "difficulty": "medium", "points": 1.0,
            "prompt": "In a typical agent loop, what usually happens right after the model decides to call a tool?",
            "options": [
                {"id": "a", "text": "The conversation ends immediately"},
                {"id": "b", "text": "The tool executes and its result is fed back into the model's context for the next reasoning step"},
                {"id": "c", "text": "The model is retrained"},
                {"id": "d", "text": "The user must manually restart the session"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "This observe-act-observe cycle (often called ReAct) is the core of the agent loop.",
        },
        {
            "question_type": "mcq", "skill_slug": "agents", "difficulty": "medium", "points": 1.0,
            "prompt": "'Reflection' in an agent architecture refers to:",
            "options": [
                {"id": "a", "text": "The agent critiquing/evaluating its own prior output to improve the next step"},
                {"id": "b", "text": "Mirroring the user's tone exactly"},
                {"id": "c", "text": "Logging every API call"},
                {"id": "d", "text": "Rendering UI components"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Reflection loops let an agent self-correct, often substantially improving output quality on harder tasks.",
        },

        # --- Tool Calling (2) ---
        {
            "question_type": "mcq", "skill_slug": "tool-calling", "difficulty": "easy", "points": 1.0,
            "prompt": "Structured tool/function calling lets a model:",
            "options": [
                {"id": "a", "text": "Directly execute arbitrary code on the host machine"},
                {"id": "b", "text": "Request a specific function be called with typed arguments, which the calling application then executes"},
                {"id": "c", "text": "Bypass all safety filters"},
                {"id": "d", "text": "Train itself further"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The model only proposes a structured call; the application decides whether and how to actually execute it — this separation is central to agent safety.",
        },
        {
            "question_type": "mcq", "skill_slug": "tool-calling", "difficulty": "medium", "points": 1.0,
            "prompt": "Why should a production agent's available tools be an explicit, narrow allowlist rather than 'anything the model wants to run'?",
            "options": [
                {"id": "a", "text": "It has no real benefit"},
                {"id": "b", "text": "It bounds what actions the agent can actually take, limiting blast radius from mistakes or prompt injection"},
                {"id": "c", "text": "It makes the model larger"},
                {"id": "d", "text": "It's required to reduce token usage only"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Explicit, permissioned tools are a core AI-safety control against both bugs and adversarial prompt injection.",
        },

        # --- Memory (2) ---
        {
            "question_type": "mcq", "skill_slug": "memory", "difficulty": "easy", "points": 1.0,
            "prompt": "Short-term (working) memory in an agent typically holds:",
            "options": [
                {"id": "a", "text": "The current conversation/task context that fits in the active window"},
                {"id": "b", "text": "A permanent record of every user who ever used the system"},
                {"id": "c", "text": "The model's training weights"},
                {"id": "d", "text": "Nothing — agents have no memory"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Short-term memory is scoped to the current session/task; long-term memory persists across sessions (e.g. in a database or vector store).",
        },
        {
            "question_type": "mcq", "skill_slug": "memory", "difficulty": "medium", "points": 1.0,
            "prompt": "A reasonable way to give an agent long-term memory across sessions is to:",
            "options": [
                {"id": "a", "text": "Store durable facts/summaries externally (e.g. a database) and retrieve relevant ones into context when needed"},
                {"id": "b", "text": "Increase the context window infinitely"},
                {"id": "c", "text": "Retrain the base model after every conversation"},
                {"id": "d", "text": "Long-term memory is not possible for LLM agents"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Persisting and selectively retrieving external memory is the standard, scalable approach to long-term agent memory.",
        },

        # --- LangChain (2) ---
        {
            "question_type": "mcq", "skill_slug": "langchain", "difficulty": "easy", "points": 1.0,
            "prompt": "LangChain is primarily used to:",
            "options": [
                {"id": "a", "text": "Train new foundation models from scratch"},
                {"id": "b", "text": "Compose LLM applications from reusable building blocks (models, prompts, tools, retrieval, memory)"},
                {"id": "c", "text": "Host a vector database"},
                {"id": "d", "text": "Replace Python entirely"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "LangChain provides standardized abstractions for the recurring pieces of LLM applications.",
        },
        {
            "question_type": "short_answer", "skill_slug": "langchain", "difficulty": "medium", "points": 1.0,
            "prompt": "What's the benefit of using LangChain's standard model/tool interfaces instead of writing custom code directly against one provider's SDK?",
            "options": [],
            "correct_answer": {
                "expected": "Standard interfaces make it easier to swap providers/models, reuse chains and tools across projects, and compose components consistently.",
                "keywords": ["swap", "portable", "reuse", "consistent", "provider"],
            },
            "explanation": "A common interface reduces vendor lock-in and lets the same chain/tool logic work across different underlying models.",
        },

        # --- LangGraph (3) ---
        {
            "question_type": "mcq", "skill_slug": "langgraph", "difficulty": "easy", "points": 1.0,
            "prompt": "LangGraph primarily adds to LangChain the ability to:",
            "options": [
                {"id": "a", "text": "Model agent workflows as a stateful graph with branching, loops, and checkpoints"},
                {"id": "b", "text": "Train embeddings"},
                {"id": "c", "text": "Replace vector databases"},
                {"id": "d", "text": "Render frontend UI"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "LangGraph is built for explicit, stateful orchestration of multi-step (and often multi-agent) workflows.",
        },
        {
            "question_type": "mcq", "skill_slug": "langgraph", "difficulty": "medium", "points": 1.0,
            "prompt": "A 'checkpoint' in LangGraph is best described as:",
            "options": [
                {"id": "a", "text": "A saved snapshot of graph state that lets execution be paused, inspected, or resumed"},
                {"id": "b", "text": "A syntax error in the graph definition"},
                {"id": "c", "text": "A type of embedding model"},
                {"id": "d", "text": "A billing milestone"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Checkpoints persist graph state, which is what enables human-in-the-loop review and durable long-running workflows.",
        },
        {
            "question_type": "mcq", "skill_slug": "langgraph", "difficulty": "hard", "points": 1.0,
            "prompt": "For a workflow where a supervisor agent must route a task to one of several specialist agents based on the task's content, which LangGraph feature is most directly relevant?",
            "options": [
                {"id": "a", "text": "Conditional edges (routing logic between nodes based on state)"},
                {"id": "b", "text": "Static, fixed edges only"},
                {"id": "c", "text": "Removing all state from the graph"},
                {"id": "d", "text": "Disabling checkpoints"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Conditional edges let the graph branch to different nodes (specialist agents) based on the current state, which is exactly the supervisor/delegation pattern.",
        },
    ],
}
