"""
Course 14: Capstone Projects

Seven end-to-end projects that apply the full curriculum (Python through
multi-agent systems, evaluation, and production engineering) to build real,
portfolio-worthy agentic AI systems.
"""

PROJECTS = [
    {
        "slug": "rag-knowledge-assistant",
        "title": "RAG Knowledge Assistant",
        "overview": (
            "Build a retrieval-augmented question-answering system over a real document set "
            "(technical docs, a knowledge base, or a set of PDFs you choose), with citation "
            "verification and a faithfulness check so it refuses to answer confidently beyond "
            "what its sources actually support."
        ),
        "objective": (
            "Ship a working RAG assistant that ingests a document collection, retrieves relevant "
            "passages for a user question, generates a grounded answer with citations, and "
            "measurably reduces hallucination compared to an ungrounded baseline — backed by an "
            "evaluation harness that proves it, not just a demo that looks convincing."
        ),
        "prerequisites": [
            "Completed the Embeddings and RAG courses",
            "Comfortable writing Python and using a vector database client",
            "Completed the Agent Evaluation & Safety course's hallucination and grounding modules",
        ],
        "learning_outcomes": [
            "Design a chunking strategy appropriate to a real document collection",
            "Build an end-to-end retrieval pipeline with a vector database and a reranking step",
            "Implement a grounded generation prompt with explicit citation formatting",
            "Build and run an evaluation harness measuring faithfulness, answer relevance, and retrieval precision",
            "Ship the assistant behind a simple API with a working refuse-when-insufficient-evidence path",
        ],
        "requirements": [
            "Ingest at least 50 real documents (or an equivalent volume of text) into a vector store",
            "Implement chunking with configurable chunk size and overlap",
            "Implement retrieval with top-k similarity search and at least one reranking pass",
            "Generate answers using a grounded prompt that cites specific source passages",
            "Implement a citation verification step that checks each cited claim against its source",
            "Implement an 'insufficient evidence' refusal path when retrieval quality is low",
            "Build an evaluation harness with at least 20 labeled test questions and faithfulness/relevance scoring",
            "Expose the assistant through a simple HTTP API (FastAPI is recommended but not required)",
        ],
        "architecture": (
            "The system has three pipelines: an offline ingestion pipeline that chunks and embeds "
            "documents into a vector store; an online query pipeline that retrieves, reranks, "
            "grounds, and generates an answer with citations; and an evaluation pipeline that runs "
            "independently against a labeled test set to score faithfulness and relevance.\n\n"
            "```\n"
            "  Documents            User Question\n"
            "     |                      |\n"
            "     v                      v\n"
            "  [Chunker]            [Embed Query]\n"
            "     |                      |\n"
            "     v                      v\n"
            "  [Embedder]  --->   [Vector Store] ---> top-k passages\n"
            "                            |\n"
            "                            v\n"
            "                       [Reranker]\n"
            "                            |\n"
            "                            v\n"
            "                  [Grounded Generator] ---> answer + citations\n"
            "                            |\n"
            "                            v\n"
            "                  [Citation Verifier] ---> final answer or refusal\n"
            "\n"
            "  [Eval Harness] ---(runs independently against)---> [Query Pipeline]\n"
            "```"
        ),
        "milestones": [
            {"title": "Ingestion pipeline working end to end", "description": "Documents are chunked, embedded, and queryable in the vector store; a manual similarity search returns sensible results."},
            {"title": "Grounded generation with citations", "description": "The query pipeline retrieves, reranks, and generates an answer that cites specific source passages using the structured citation format."},
            {"title": "Verification and refusal paths implemented", "description": "Citation verification catches unsupported claims, and the system refuses gracefully when retrieval quality is too low."},
            {"title": "Evaluation harness passing a defined bar", "description": "The labeled test set runs end to end and the system clears a defined faithfulness and answer-relevance threshold."},
            {"title": "API deployed and documented", "description": "The assistant is reachable over HTTP with a documented request/response contract and basic error handling."},
        ],
        "tasks": [
            {"title": "Select and prepare a document collection", "description": "Choose a real, coherent document set (product docs, a textbook, policy documents) and convert it to clean plain text."},
            {"title": "Implement chunking", "description": "Split documents into overlapping chunks sized appropriately for your embedding model, preserving enough context per chunk to stand alone."},
            {"title": "Build the ingestion pipeline", "description": "Embed each chunk and upsert into a vector store with metadata (source title, section, chunk index)."},
            {"title": "Implement retrieval and reranking", "description": "Given a query, retrieve top-k candidates by similarity and apply a reranking pass to improve precision at the top of the list."},
            {"title": "Implement grounded generation", "description": "Write a prompt that answers only from retrieved passages, using the structured source-index citation pattern from the evaluation course."},
            {"title": "Implement citation verification", "description": "Check each cited claim against its source passage using an LLM-as-judge faithfulness check, and drop or flag unsupported claims."},
            {"title": "Implement the insufficient-evidence refusal path", "description": "Gate generation on a minimum retrieval similarity score, returning an honest 'I don't have enough information' response below threshold."},
            {"title": "Build the evaluation harness", "description": "Write at least 20 labeled test questions with expected answer content, and score faithfulness, answer relevance, and retrieval precision@k."},
            {"title": "Expose the assistant via an API", "description": "Wrap the query pipeline in a FastAPI (or equivalent) endpoint with typed request/response models."},
            {"title": "Write up results and known limitations", "description": "Document your evaluation scores, what document types the system handles well or poorly, and what you'd improve with more time."},
        ],
        "expected_output": (
            "A running API endpoint that accepts a question and returns a grounded answer with "
            "citations back to specific source passages, or an honest refusal when evidence is "
            "insufficient. An evaluation report showing faithfulness, answer relevance, and "
            "retrieval precision scores against your labeled test set, with before/after numbers "
            "if you compare against an ungrounded baseline."
        ),
        "evaluation_criteria": [
            {"criterion": "Retrieval quality: relevant passages are reliably retrieved for the test question set", "weight": 0.2},
            {"criterion": "Grounding and faithfulness: generated answers are measurably well-supported by retrieved context", "weight": 0.25},
            {"criterion": "Citation correctness: citations point to passages that actually support the cited claim", "weight": 0.2},
            {"criterion": "Refusal behavior: the system reliably declines to answer when evidence is insufficient, rather than guessing", "weight": 0.15},
            {"criterion": "Evaluation rigor: the harness is real, labeled, and its results are reported honestly, including weaknesses", "weight": 0.1},
            {"criterion": "Engineering quality: clean pipeline structure, typed API, and reasonable error handling", "weight": 0.1},
        ],
        "resources": [
            {"title": "Ragas: Evaluation framework for RAG", "url": "https://docs.ragas.io/en/stable/", "resource_type": "docs"},
            {"title": "Anthropic: Citations with the Messages API", "url": "https://docs.anthropic.com/en/docs/build-with-claude/citations", "resource_type": "docs"},
            {"title": "Pinecone: RAG pipeline guide", "url": "https://www.pinecone.io/learn/retrieval-augmented-generation/", "resource_type": "article"},
        ],
        "order_index": 1,
        "estimated_hours": 14,
        "difficulty": "intermediate",
        "skills": [
            {"slug": "rag", "weight": 1.0},
            {"slug": "vector-db", "weight": 0.7},
            {"slug": "embeddings", "weight": 0.6},
        ],
    },
    {
        "slug": "research-agent",
        "title": "Research Agent",
        "overview": (
            "Build an autonomous research agent that takes an open-ended question, plans a "
            "multi-step research strategy, calls web search and page-fetching tools to gather "
            "evidence, and synthesizes a cited report — with explicit planning and re-planning as "
            "it discovers what it doesn't yet know."
        ),
        "objective": (
            "Ship an agent that decomposes a research question into sub-questions, executes tool "
            "calls to gather evidence for each, adapts its plan based on what it finds, and "
            "produces a coherent, cited final report, bounded by clear stopping conditions so it "
            "doesn't loop indefinitely."
        ),
        "prerequisites": [
            "Completed the AI Agents and Planning modules",
            "Completed the Tool Calling module",
            "Comfortable implementing tool-calling loops in Python",
        ],
        "learning_outcomes": [
            "Implement a plan-and-execute agent loop that decomposes a goal into sub-tasks",
            "Integrate real web search and page-fetching tools with proper error handling",
            "Implement re-planning logic that adapts the research plan based on intermediate findings",
            "Implement loop detection and step limits to bound agent execution",
            "Synthesize multi-source findings into a coherent, cited final report",
        ],
        "requirements": [
            "Implement an explicit planning step that decomposes the research question into sub-questions before executing",
            "Integrate at least one real web search tool and one page-fetching/summarization tool",
            "Implement re-planning: the agent must be able to revise its plan based on findings, not just execute a fixed plan",
            "Implement a step cap and loop detector so the agent cannot run unbounded",
            "Track and cite every source used in the final report",
            "Handle tool failures (search timeout, unreachable page) without crashing the whole run",
            "Produce a final report with a clear structure: summary, findings per sub-question, and a source list",
        ],
        "architecture": (
            "A planner produces an initial set of sub-questions. An executor loop processes each "
            "sub-question with a research tool set (search, fetch, summarize), feeding findings "
            "back to the planner, which can add, remove, or reprioritize sub-questions before the "
            "loop continues. A synthesis step runs once the planner signals the research is "
            "sufficient or a step cap is reached.\n\n"
            "```\n"
            "  Research Question\n"
            "        |\n"
            "        v\n"
            "    [Planner] <-------------------+\n"
            "        |                         |\n"
            "        v                         |\n"
            "  sub-questions queue              |\n"
            "        |                         |\n"
            "        v                         |\n"
            "   [Executor loop]                |\n"
            "     |     |     |                |\n"
            "  [search][fetch][summarize]       |\n"
            "     |     |     |                |\n"
            "     +-----+-----+                |\n"
            "           |                      |\n"
            "     findings ---------------------+   (re-plan)\n"
            "           |\n"
            "     (loop until planner signals done, or step cap / loop detector triggers)\n"
            "           |\n"
            "           v\n"
            "     [Synthesizer] ---> cited final report\n"
            "```"
        ),
        "milestones": [
            {"title": "Planning step producing sensible sub-questions", "description": "Given a research question, the planner reliably decomposes it into 3-6 concrete, answerable sub-questions."},
            {"title": "Tool-calling executor loop working", "description": "The agent can search, fetch, and summarize for a single sub-question end to end, handling tool failures gracefully."},
            {"title": "Re-planning implemented", "description": "The agent revises its sub-question list based on findings at least once during a typical run, demonstrated with a concrete example."},
            {"title": "Bounded execution", "description": "Step cap and loop detection are implemented and verified to actually stop a deliberately-triggered runaway case."},
            {"title": "Synthesized, cited final report", "description": "The agent produces a complete report with per-sub-question findings and a full source list for a real research question."},
        ],
        "tasks": [
            {"title": "Design the planner's output schema", "description": "Define a typed sub-question list structure the planner produces and the executor consumes."},
            {"title": "Implement the planner prompt", "description": "Write and test a prompt that decomposes a research question into concrete, independently-researchable sub-questions."},
            {"title": "Implement the search tool", "description": "Wrap a real web search API as a typed tool with timeout and error handling."},
            {"title": "Implement the fetch and summarize tool", "description": "Wrap a page-fetching tool that retrieves and condenses a webpage's content for a given sub-question."},
            {"title": "Implement the executor loop", "description": "For each sub-question, call search then fetch/summarize, accumulating findings with source attribution."},
            {"title": "Implement re-planning logic", "description": "After each round of findings, let the planner revise the sub-question queue — add follow-ups, drop resolved questions, reprioritize."},
            {"title": "Implement step cap and loop detection", "description": "Add a maximum step count and a repeated-action detector, and write a test that deliberately triggers each to confirm they work."},
            {"title": "Implement the synthesis step", "description": "Combine all findings into a structured final report with inline citations and a source list."},
            {"title": "Run and evaluate on 5 real research questions", "description": "Execute the full agent on varied research questions and review report quality, citation accuracy, and step efficiency."},
        ],
        "expected_output": (
            "A working research agent that, given an open-ended question, produces a structured, "
            "cited report within a bounded number of steps, along with a log/trace of its planning "
            "decisions and tool calls for at least one full example run, demonstrating at least one "
            "instance of re-planning based on intermediate findings."
        ),
        "evaluation_criteria": [
            {"criterion": "Planning quality: sub-questions are concrete, relevant, and cover the research question well", "weight": 0.2},
            {"criterion": "Tool integration robustness: search/fetch failures are handled without crashing the run", "weight": 0.2},
            {"criterion": "Re-planning: demonstrated adaptation of the plan based on findings, not a fixed static plan", "weight": 0.2},
            {"criterion": "Bounded execution: step cap and loop detection verifiably prevent runaway execution", "weight": 0.15},
            {"criterion": "Report quality: the final synthesis is coherent, well-organized, and accurately cited", "weight": 0.15},
            {"criterion": "Engineering quality: clean separation between planner, executor, and synthesizer components", "weight": 0.1},
        ],
        "resources": [
            {"title": "LangGraph: Plan-and-execute tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/", "resource_type": "tutorial"},
            {"title": "Anthropic: Building effective agents", "url": "https://www.anthropic.com/research/building-effective-agents", "resource_type": "article"},
        ],
        "order_index": 2,
        "estimated_hours": 14,
        "difficulty": "intermediate",
        "skills": [
            {"slug": "agents", "weight": 1.0},
            {"slug": "planning", "weight": 0.8},
            {"slug": "tool-calling", "weight": 0.7},
        ],
    },
    {
        "slug": "customer-support-agent",
        "title": "Customer Support Agent",
        "overview": (
            "Build a customer support agent that answers product questions grounded in a "
            "knowledge base, remembers context across a multi-turn conversation, and knows when "
            "to escalate to a human rather than guessing."
        ),
        "objective": (
            "Ship a support agent combining RAG (for grounded product answers) with conversation "
            "memory (for coherent multi-turn interactions) and a clear escalation policy, "
            "evaluated against realistic support scenarios including ones it should refuse or "
            "escalate rather than answer directly."
        ),
        "prerequisites": [
            "Completed the RAG Knowledge Assistant project or equivalent RAG experience",
            "Completed the Agent Memory module",
            "Completed the Guardrails module from the Agent Evaluation & Safety course",
        ],
        "learning_outcomes": [
            "Combine RAG grounding with short- and long-term conversation memory in one agent",
            "Design an escalation policy that routes appropriately-scoped requests to a human",
            "Implement conversation-level guardrails for tone, scope, and policy compliance",
            "Persist and retrieve multi-turn conversation state correctly across sessions",
            "Evaluate a support agent against realistic, varied support scenarios",
        ],
        "requirements": [
            "Ground product/policy answers in a real knowledge base using retrieval",
            "Persist conversation history so the agent maintains context across multiple turns in a session",
            "Implement short-term memory (recent turns) and at least a simple long-term memory (e.g., remembered customer preferences or prior issues across sessions)",
            "Implement an explicit escalation policy: define at least 4 concrete conditions that trigger escalation to a human",
            "Implement input and output guardrails appropriate to a support context (tone, scope, no unauthorized promises)",
            "Handle at least one multi-turn scenario where later turns depend on earlier context",
            "Build a test set of at least 15 scenarios, including some that should be escalated rather than answered",
        ],
        "architecture": (
            "A conversation manager loads short-term (recent turns) and long-term (persisted "
            "customer facts) memory before each turn. The agent grounds its answer in retrieved "
            "knowledge-base content, checks the request against escalation rules, and either "
            "responds directly or hands off to a human queue with full context attached.\n\n"
            "```\n"
            "  Incoming message\n"
            "        |\n"
            "        v\n"
            "  [Input guardrails] ---(blocked)---> safe refusal\n"
            "        |\n"
            "        v\n"
            "  [Memory loader] <---> [Long-term store] (customer facts, prior issues)\n"
            "        |         <---> [Conversation history] (recent turns)\n"
            "        v\n"
            "  [Escalation check] ---(escalate)---> [Human queue] (+ full context)\n"
            "        |\n"
            "        v\n"
            "  [RAG retrieval] ---> [Grounded generation]\n"
            "        |\n"
            "        v\n"
            "  [Output guardrails] ---> response to customer\n"
            "        |\n"
            "        v\n"
            "  [Persist turn + update long-term memory]\n"
            "```"
        ),
        "milestones": [
            {"title": "Grounded single-turn Q&A working", "description": "The agent answers product questions correctly, citing the knowledge base, for isolated single-turn queries."},
            {"title": "Multi-turn memory working", "description": "A conversation where turn 3 depends on context established in turn 1 is handled correctly, verified with a concrete transcript."},
            {"title": "Escalation policy implemented and tested", "description": "At least 4 escalation conditions are implemented and each is verified to trigger correctly on a matching test scenario."},
            {"title": "Guardrails implemented", "description": "Input and output guardrails block at least one deliberately crafted bad-input test case each."},
            {"title": "Full evaluation suite passing", "description": "All 15+ test scenarios run end to end with documented pass/fail results and explanations for any failures."},
        ],
        "tasks": [
            {"title": "Build or select a support knowledge base", "description": "Assemble a realistic product/policy knowledge base (FAQ, docs, policy pages) to ground answers in."},
            {"title": "Implement the RAG grounding pipeline", "description": "Reuse or adapt retrieval and grounded generation from the RAG project for the support domain."},
            {"title": "Implement conversation persistence", "description": "Store and load conversation history per session using a database, following the schema patterns from the production course."},
            {"title": "Implement long-term memory", "description": "Design and implement a simple persisted-fact store (e.g., customer's product tier, prior reported issues) referenced across sessions."},
            {"title": "Define and implement the escalation policy", "description": "Write explicit, checkable rules for when to escalate (e.g., refund above a threshold, expressed frustration, request outside product scope) and wire them into the flow before generation."},
            {"title": "Implement input and output guardrails", "description": "Add guardrail checks appropriate to support: tone/abuse detection on input, unauthorized-promise detection on output."},
            {"title": "Build the test scenario suite", "description": "Write 15+ realistic scenarios covering direct answers, multi-turn context dependency, and required escalations."},
            {"title": "Run the evaluation suite and fix failures", "description": "Execute all scenarios, document results, and iterate on prompts/policy until the suite passes your defined bar."},
        ],
        "expected_output": (
            "A working support agent reachable through a simple interface (CLI or API) that "
            "correctly handles grounded single-turn questions, multi-turn conversations with "
            "context dependency, and reliably escalates the scenarios your policy defines as "
            "needing a human — with an evaluation report showing pass/fail results across your "
            "full test scenario suite."
        ),
        "evaluation_criteria": [
            {"criterion": "Grounding quality: product/policy answers are accurate and cite the knowledge base correctly", "weight": 0.2},
            {"criterion": "Memory correctness: multi-turn context is correctly maintained and used across a session", "weight": 0.2},
            {"criterion": "Escalation reliability: defined escalation conditions trigger consistently and appropriately", "weight": 0.25},
            {"criterion": "Guardrail effectiveness: input/output guardrails correctly catch their targeted test cases", "weight": 0.15},
            {"criterion": "Evaluation coverage: the test scenario suite is realistic and covers edge cases, not just happy paths", "weight": 0.1},
            {"criterion": "Engineering quality: clean separation of memory, retrieval, escalation, and guardrail components", "weight": 0.1},
        ],
        "resources": [
            {"title": "LangGraph: Memory concepts", "url": "https://langchain-ai.github.io/langgraph/concepts/memory/", "resource_type": "docs"},
            {"title": "NVIDIA NeMo Guardrails", "url": "https://docs.nvidia.com/nemo/guardrails/", "resource_type": "docs"},
        ],
        "order_index": 3,
        "estimated_hours": 16,
        "difficulty": "intermediate",
        "skills": [
            {"slug": "agents", "weight": 0.9},
            {"slug": "memory", "weight": 0.9},
            {"slug": "rag", "weight": 0.7},
        ],
    },
    {
        "slug": "data-analyst-agent",
        "title": "Data Analyst Agent",
        "overview": (
            "Build an agent that answers natural-language questions about a tabular dataset by "
            "writing and executing real analysis code — generating pandas/SQL queries, running "
            "them in a sandboxed environment, and explaining the results — rather than guessing "
            "numbers from context."
        ),
        "objective": (
            "Ship an agent that takes a natural-language data question, translates it into "
            "executable analysis code, runs it safely, verifies the result makes sense, and "
            "returns both the answer and the code/query that produced it so the result is fully "
            "auditable."
        ),
        "prerequisites": [
            "Completed the Python for AI and Tool Calling courses",
            "Comfortable with pandas or SQL",
            "Completed the Security module (sandboxing) from the Agent Evaluation & Safety course",
        ],
        "learning_outcomes": [
            "Design a tool that lets an agent generate and execute real analysis code safely",
            "Implement a sandboxed code execution environment with resource limits",
            "Implement a self-check step that verifies generated code's output is plausible before returning it",
            "Handle ambiguous data questions by asking clarifying questions or stating assumptions explicitly",
            "Produce auditable answers that always show the exact code or query used",
        ],
        "requirements": [
            "Accept a natural-language question about a provided tabular dataset (CSV or SQL database)",
            "Generate executable pandas or SQL code to answer the question",
            "Execute the generated code in a sandboxed environment with CPU, memory, and time limits",
            "Never execute generated code with full host privileges or unrestricted file/network access",
            "Implement a result sanity-check step (e.g., type checking, range checking, re-deriving via a second method) before returning an answer",
            "Handle at least one ambiguous question by stating explicit assumptions rather than guessing silently",
            "Always return the exact code/query used alongside the natural-language answer, for auditability",
            "Handle code execution errors (syntax errors, runtime exceptions) by retrying or reporting clearly, not crashing",
        ],
        "architecture": (
            "A planner interprets the natural-language question against the dataset's schema and "
            "generates candidate analysis code. A sandbox executor runs the code in an isolated "
            "environment. A verifier checks the result for plausibility before a final synthesis "
            "step explains the answer in plain language alongside the exact code used.\n\n"
            "```\n"
            "  Natural-language question + dataset schema\n"
            "        |\n"
            "        v\n"
            "  [Code Generator] ---> pandas/SQL code\n"
            "        |\n"
            "        v\n"
            "  [Sandboxed Executor] (CPU/mem/time limits, no network, no host FS)\n"
            "        |\n"
            "        +---(error)---> [Retry with error feedback] (bounded attempts)\n"
            "        |\n"
            "        v\n"
            "  [Result Verifier] ---(implausible)---> retry or flag uncertainty\n"
            "        |\n"
            "        v\n"
            "  [Synthesizer] ---> plain-language answer + exact code used\n"
            "```"
        ),
        "milestones": [
            {"title": "Code generation working for simple questions", "description": "The agent correctly generates and executes code for straightforward aggregate questions (counts, sums, averages) against the dataset."},
            {"title": "Sandboxed execution verified secure", "description": "The execution environment is demonstrated to block a deliberately malicious or resource-exhausting test snippet."},
            {"title": "Error handling and retry implemented", "description": "A deliberately buggy generated query triggers a bounded retry with error feedback rather than crashing the run."},
            {"title": "Result verification implemented", "description": "The verifier catches at least one deliberately implausible result in a test case (e.g., a negative count) before it's returned."},
            {"title": "Ambiguity handling demonstrated", "description": "At least one genuinely ambiguous question is handled by stating explicit assumptions, verified against a written test case."},
        ],
        "tasks": [
            {"title": "Select and prepare a dataset", "description": "Choose a real, moderately complex tabular dataset (CSV or a small SQL database) with enough columns and rows to support varied questions."},
            {"title": "Implement schema introspection", "description": "Build a function that summarizes the dataset's schema (columns, types, sample values) for the code generator's context."},
            {"title": "Implement the code generator", "description": "Write a prompt and structured-output schema that turns a natural-language question plus schema into executable pandas or SQL code."},
            {"title": "Build the sandboxed executor", "description": "Implement code execution with network isolation and resource limits, following the sandboxing patterns from the security module."},
            {"title": "Implement retry-with-error-feedback", "description": "On execution failure, feed the error back to the code generator for a bounded number of correction attempts."},
            {"title": "Implement the result verifier", "description": "Add sanity checks (type/range checks, or a second independent derivation) that flag implausible results before they're returned."},
            {"title": "Implement ambiguity handling", "description": "Detect underspecified questions and have the agent state its interpretation/assumptions explicitly rather than guessing silently."},
            {"title": "Build the synthesis and audit-trail output", "description": "Return a plain-language answer alongside the exact executed code, for every response."},
            {"title": "Test against 10+ varied questions", "description": "Run the agent against a range of question types (simple aggregates, filters, joins/multi-step, ambiguous phrasing) and document results."},
        ],
        "expected_output": (
            "A working agent that answers natural-language questions about a real dataset by "
            "generating and safely executing real analysis code, returning both the plain-language "
            "answer and the exact code used for every response, with documented results across a "
            "range of question types including at least one handled ambiguous case and one caught "
            "sandbox violation attempt."
        ),
        "evaluation_criteria": [
            {"criterion": "Code generation correctness: generated code correctly answers the range of tested questions", "weight": 0.25},
            {"criterion": "Sandbox security: execution environment is verifiably isolated and resource-limited", "weight": 0.2},
            {"criterion": "Error handling: execution failures are retried with feedback or reported clearly, never crash silently", "weight": 0.15},
            {"criterion": "Result verification: implausible results are caught before being returned as final answers", "weight": 0.15},
            {"criterion": "Auditability: every answer is accompanied by the exact code/query used", "weight": 0.15},
            {"criterion": "Ambiguity handling: underspecified questions are handled with explicit stated assumptions", "weight": 0.1},
        ],
        "resources": [
            {"title": "Docker: Runtime resource constraints", "url": "https://docs.docker.com/config/containers/resource_constraints/", "resource_type": "docs"},
            {"title": "pandas documentation", "url": "https://pandas.pydata.org/docs/", "resource_type": "docs"},
        ],
        "order_index": 4,
        "estimated_hours": 14,
        "difficulty": "intermediate",
        "skills": [
            {"slug": "agents", "weight": 0.8},
            {"slug": "tool-calling", "weight": 0.9},
            {"slug": "python", "weight": 0.8},
        ],
    },
    {
        "slug": "ai-interview-agent",
        "title": "AI Interview Agent",
        "overview": (
            "Build an agent that conducts a structured technical or behavioral interview: asking "
            "adaptive follow-up questions based on the candidate's answers, maintaining a coherent "
            "line of questioning across the full session, and producing a structured evaluation "
            "at the end grounded in what was actually said."
        ),
        "objective": (
            "Ship an interview agent that runs a full multi-turn interview session using a defined "
            "question bank and adaptive follow-up logic, tracks what's been covered via memory, "
            "and generates a structured, evidence-grounded candidate evaluation — designed "
            "carefully to avoid leading or biased questioning."
        ),
        "prerequisites": [
            "Completed the Agent Memory and Prompt Engineering modules",
            "Completed the Agent Evaluation & Safety course",
            "Comfortable designing multi-turn conversational flows",
        ],
        "learning_outcomes": [
            "Design an adaptive multi-turn conversation flow driven by prior answers",
            "Implement session memory that tracks topic coverage across an interview",
            "Apply careful prompt engineering to avoid leading questions and scoring bias",
            "Generate a structured, evidence-grounded evaluation tied to specific things the candidate said",
            "Design guardrails appropriate to a sensitive, evaluative use case",
        ],
        "requirements": [
            "Define a structured question bank (at least 8 questions) covering a specific role/skill area",
            "Implement adaptive follow-up: the agent must generate at least one genuine follow-up question based on a candidate's specific answer, not just proceed down a fixed script",
            "Track topic/question coverage across the session using memory, avoiding repeated or redundant questions",
            "Implement a defined interview closing condition (all core topics covered, or a turn/time limit)",
            "Generate a structured final evaluation with per-topic assessment, each backed by a specific quote or paraphrase from the transcript",
            "Implement guardrails against leading questions and against generating evaluative bias unrelated to job-relevant criteria",
            "Handle an off-topic or evasive candidate response without breaking the interview flow",
        ],
        "architecture": (
            "A session controller drives the interview loop: it selects the next question (from "
            "the bank or as an adaptive follow-up), tracks coverage state, and detects when to "
            "close the interview. A separate evaluation stage runs only after the session ends, "
            "reading the full transcript to produce a structured, evidence-grounded assessment — "
            "kept separate from the live interview flow so evaluation never leaks into how "
            "questions are asked.\n\n"
            "```\n"
            "  Question bank                  Candidate response\n"
            "       |                                |\n"
            "       v                                v\n"
            "  [Session Controller] <---> [Coverage Memory] (topics asked/covered)\n"
            "       |\n"
            "       +--(needs follow-up?)--> [Follow-up Generator] ---> adaptive question\n"
            "       |\n"
            "       +--(coverage complete or limit hit)--> [Close Session]\n"
            "                                                    |\n"
            "                                                    v\n"
            "                                          [Evaluator] (reads full transcript)\n"
            "                                                    |\n"
            "                                                    v\n"
            "                                     structured, evidence-grounded evaluation\n"
            "```"
        ),
        "milestones": [
            {"title": "Fixed-script interview flow working", "description": "The agent can run through the full question bank in order, collecting responses, without adaptive logic yet."},
            {"title": "Adaptive follow-up implemented", "description": "At least one real session demonstrates a follow-up question generated specifically from a candidate's prior answer, not from the fixed bank."},
            {"title": "Coverage tracking and closing condition working", "description": "The session correctly avoids redundant questions and closes when coverage criteria are met or a limit is reached."},
            {"title": "Structured evaluation generation working", "description": "The evaluator produces a per-topic assessment for a full test transcript, each claim backed by a specific quote or paraphrase."},
            {"title": "Bias and leading-question guardrails verified", "description": "At least one deliberately leading draft question is caught and rewritten by the guardrail before being asked."},
        ],
        "tasks": [
            {"title": "Define the question bank and topic taxonomy", "description": "Write at least 8 structured questions mapped to specific topics/skills for a chosen role."},
            {"title": "Implement the session controller loop", "description": "Build the turn-by-turn loop that asks a question, receives a response, and decides the next action."},
            {"title": "Implement coverage memory", "description": "Track which topics have been asked and to what depth, so the controller can avoid redundancy and detect completion."},
            {"title": "Implement the follow-up generator", "description": "Write a prompt that generates a genuine, specific follow-up question grounded in the candidate's actual prior answer."},
            {"title": "Implement leading-question and bias guardrails", "description": "Add a check that reviews generated questions for leading phrasing or irrelevant bias before they're asked."},
            {"title": "Implement the session closing logic", "description": "Define and implement the condition(s) under which the interview ends."},
            {"title": "Implement the evaluator", "description": "Write a post-session evaluation step that reads the full transcript and produces a structured, per-topic, evidence-grounded assessment."},
            {"title": "Handle off-topic/evasive responses", "description": "Add handling so a non-answer or deflection doesn't break the flow — the agent should redirect or note the gap, not crash or loop."},
            {"title": "Run and review 3 full mock interview sessions", "description": "Conduct full sessions (real or simulated candidate answers) and review transcripts and evaluations for quality and fairness."},
        ],
        "expected_output": (
            "A working interview agent that conducts a complete, multi-turn interview session "
            "using a defined question bank with at least one genuine adaptive follow-up, and "
            "produces a structured final evaluation for that session where every assessment claim "
            "is backed by a specific piece of the transcript — demonstrated across at least 3 full "
            "mock sessions."
        ),
        "evaluation_criteria": [
            {"criterion": "Adaptive questioning: follow-ups are genuinely grounded in the candidate's specific prior answers", "weight": 0.2},
            {"criterion": "Coverage tracking: the session avoids redundant questions and reliably reaches a sensible closing point", "weight": 0.15},
            {"criterion": "Evaluation quality: the final assessment is structured, specific, and every claim is evidence-backed", "weight": 0.25},
            {"criterion": "Bias mitigation: leading questions and irrelevant bias are demonstrably caught and corrected", "weight": 0.2},
            {"criterion": "Robustness: off-topic or evasive responses are handled gracefully without breaking the flow", "weight": 0.1},
            {"criterion": "Engineering quality: clean separation between the live session flow and the post-session evaluator", "weight": 0.1},
        ],
        "resources": [
            {"title": "Anthropic: Prompt engineering overview", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "resource_type": "docs"},
            {"title": "LangGraph: Memory concepts", "url": "https://langchain-ai.github.io/langgraph/concepts/memory/", "resource_type": "docs"},
        ],
        "order_index": 5,
        "estimated_hours": 16,
        "difficulty": "advanced",
        "skills": [
            {"slug": "agents", "weight": 0.8},
            {"slug": "memory", "weight": 0.8},
            {"slug": "prompt-engineering", "weight": 0.9},
        ],
    },
    {
        "slug": "multi-agent-research-system",
        "title": "Multi-Agent Research System",
        "overview": (
            "Build a supervisor-worker multi-agent system in LangGraph where a supervisor "
            "decomposes a complex research task, delegates to specialist agents (research, "
            "analysis, writing) running in a coordinated graph, and resolves conflicts between "
            "their outputs before producing a final synthesized report."
        ),
        "objective": (
            "Ship a working LangGraph multi-agent system with at least three distinct specialist "
            "agents coordinated by a supervisor, using shared state with correct reducers, that "
            "produces a synthesized, conflict-checked final report for a complex research "
            "question no single specialist could handle well alone."
        ),
        "prerequisites": [
            "Completed the Multi-Agent Systems and LangGraph courses",
            "Completed the Research Agent project or equivalent experience with tool-calling agents",
            "Comfortable with LangGraph's StateGraph and Send APIs",
        ],
        "learning_outcomes": [
            "Design and implement a supervisor-worker topology in LangGraph with conditional routing",
            "Implement a shared state schema with correct reducers for concurrent specialist writes",
            "Implement at least one parallel fan-out step for independent sub-tasks",
            "Detect and resolve conflicting outputs between specialist agents",
            "Produce a coherent final synthesis from multiple independent specialist contributions",
        ],
        "requirements": [
            "Implement at least 3 distinct specialist agents (e.g., research, data-analysis, writing) each with its own scoped tool set",
            "Implement a supervisor agent that routes tasks to specialists using LangGraph conditional edges",
            "Implement a shared state schema (TypedDict/Pydantic) with explicit reducers for any concurrently-written field",
            "Implement at least one parallel fan-out step using the Send API for independent sub-tasks",
            "Implement conflict detection between specialist outputs and at least one resolution strategy (precedence rule or arbitrator)",
            "Implement a step/depth limit to bound the graph's total execution",
            "Produce a final synthesized report combining multiple specialists' contributions coherently",
            "Visualize and include the compiled graph structure (e.g., via draw_mermaid) in your submission",
        ],
        "architecture": (
            "A supervisor node routes an incoming research task to specialist nodes via conditional "
            "edges, fanning out to parallel research sub-tasks where independent, and fanning back "
            "in through shared state. A conflict-check node inspects specialist outputs before a "
            "synthesis node produces the final report.\n\n"
            "```\n"
            "                     Research Task\n"
            "                          |\n"
            "                          v\n"
            "                     [Supervisor] ------------------+\n"
            "                    /      |      \\                 |\n"
            "                   v       v       v                |\n"
            "            [Research]  [Analysis] [Writing]         |\n"
            "              |    (parallel Send fan-out            |\n"
            "              |     for independent sub-questions)   |\n"
            "              v                                      |\n"
            "        [Shared State] (reducers merge concurrent writes)\n"
            "              |                                      |\n"
            "              v                                      |\n"
            "        [Conflict Check] ---(conflict)---> [Arbitrator] --+\n"
            "              |\n"
            "              v\n"
            "        [Synthesizer] ---> final cited report\n"
            "```"
        ),
        "milestones": [
            {"title": "Graph compiles and routes correctly", "description": "The StateGraph compiles, and a manual test confirms the supervisor correctly routes to each specialist for a matching task type."},
            {"title": "Specialists working independently", "description": "Each specialist agent is verified to work correctly in isolation via a direct unit-style test, before wiring into the full graph."},
            {"title": "Shared state and reducers correct", "description": "A test demonstrates that concurrent parallel writes to a shared state field merge correctly rather than one overwriting another."},
            {"title": "Parallel fan-out working", "description": "At least one real run demonstrates the Send API fanning out to multiple parallel specialist invocations for independent sub-tasks."},
            {"title": "Conflict detection and synthesis working end to end", "description": "A deliberately conflicting pair of specialist outputs is correctly detected and resolved, and the final synthesis reads as coherent, not just concatenated."},
        ],
        "tasks": [
            {"title": "Design the shared state schema", "description": "Define the TypedDict/Pydantic state schema for the graph, identifying which fields need reducers for concurrent writes."},
            {"title": "Implement the research specialist", "description": "Build a research specialist agent with search/fetch tools, following the tool-scoping principles from the multi-agent course."},
            {"title": "Implement the analysis specialist", "description": "Build a specialist that processes research findings into structured analysis or comparisons."},
            {"title": "Implement the writing specialist", "description": "Build a specialist that turns analysis into polished narrative report sections."},
            {"title": "Implement the supervisor and routing", "description": "Build the supervisor node and its conditional edges routing tasks to the correct specialist(s)."},
            {"title": "Implement parallel fan-out for independent sub-tasks", "description": "Identify a genuinely parallelizable step (e.g., researching multiple independent sub-questions) and implement it with the Send API."},
            {"title": "Implement conflict detection and resolution", "description": "Add a synthesis-time check for contradictions between specialist outputs, with a precedence rule or arbitrator agent to resolve them."},
            {"title": "Implement step/depth limits", "description": "Add bounded execution to prevent runaway delegation or looping between supervisor and specialists."},
            {"title": "Implement the final synthesizer", "description": "Combine all specialist contributions into one coherent, cited final report."},
            {"title": "Test end to end and visualize the graph", "description": "Run the full system on a real complex research task, capture the compiled graph diagram, and document a full example trace."},
        ],
        "expected_output": (
            "A working LangGraph multi-agent system, runnable end to end on a real complex "
            "research question, producing a synthesized final report from at least 3 specialists "
            "with at least one demonstrated parallel fan-out and one demonstrated conflict "
            "resolution, along with a graph visualization and a full execution trace for one "
            "example run."
        ),
        "evaluation_criteria": [
            {"criterion": "Graph correctness: routing, state, and reducers all behave correctly, verified with targeted tests", "weight": 0.2},
            {"criterion": "Specialist quality: each specialist produces useful, correctly-scoped output within its domain", "weight": 0.2},
            {"criterion": "Parallel fan-out: independent sub-tasks are genuinely executed in parallel via the Send API", "weight": 0.15},
            {"criterion": "Conflict handling: conflicting specialist outputs are detected and resolved sensibly, not silently ignored", "weight": 0.2},
            {"criterion": "Synthesis quality: the final report reads as coherent and integrated, not a concatenation of parts", "weight": 0.15},
            {"criterion": "Engineering quality: clean graph structure with documented state schema and a working visualization", "weight": 0.1},
        ],
        "resources": [
            {"title": "LangGraph: Multi-agent systems", "url": "https://langchain-ai.github.io/langgraph/concepts/multi_agent/", "resource_type": "docs"},
            {"title": "LangGraph: Multi-agent collaboration tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/", "resource_type": "tutorial"},
            {"title": "LangGraph: Map-reduce and the Send API", "url": "https://langchain-ai.github.io/langgraph/how-tos/graph-api/#map-reduce-and-the-send-api", "resource_type": "docs"},
        ],
        "order_index": 6,
        "estimated_hours": 20,
        "difficulty": "advanced",
        "skills": [
            {"slug": "multi-agent-systems", "weight": 1.0},
            {"slug": "langgraph", "weight": 0.9},
            {"slug": "planning", "weight": 0.6},
        ],
    },
    {
        "slug": "production-agentic-ai-capstone",
        "title": "Production Agentic AI Capstone",
        "overview": (
            "Take an agent system (your own from an earlier project, or a new one) and ship it as "
            "a real production service: a FastAPI backend with authentication, persistence, "
            "caching, monitoring, cost controls, and a deployment pipeline — the full production "
            "engineering stack applied to an actual agentic system, not a toy example."
        ),
        "objective": (
            "Ship a deployed, monitored, cost-controlled agent service that could plausibly handle "
            "real traffic: authenticated endpoints, persisted conversation/run state, an "
            "evaluation harness gating changes, observability into what the agent is doing, and "
            "documented rate limits and cost budgets."
        ),
        "prerequisites": [
            "Completed the Production AI Agents course",
            "Completed at least one prior agent-building project (Research Agent, Customer Support Agent, or Multi-Agent Research System)",
            "Comfortable with Docker and a relational database",
        ],
        "learning_outcomes": [
            "Expose an existing or new agent system as a production-grade FastAPI service",
            "Implement authentication, persistence, and rate limiting for the service",
            "Instrument the service with structured logging, metrics, and tracing",
            "Implement cost controls (token budgets, model routing) and verify them under a load test",
            "Deploy the service in a container with a documented rollout and rollback strategy",
        ],
        "requirements": [
            "Expose the agent through a FastAPI service with typed request/response models and at least one streaming endpoint",
            "Implement authentication (API key or JWT) with at least one scoped permission distinction",
            "Persist conversations/runs to a database with a schema supporting multi-tenant isolation",
            "Implement caching for at least one expensive, cacheable operation",
            "Implement rate limiting per caller using a token-bucket or equivalent algorithm",
            "Instrument the service with structured logs, Prometheus-style metrics, and request tracing with correlation IDs",
            "Implement a token budget and at least one cost-based model-routing decision",
            "Containerize the service with a multi-stage Dockerfile and working health/readiness checks",
            "Run the evaluation harness from an earlier course/project against the service and report results",
            "Document your rollout strategy (blue-green or canary) and rollback triggers, even if only run locally/staged",
        ],
        "architecture": (
            "The agent system from an earlier project sits behind a FastAPI service layer adding "
            "auth, persistence, caching, rate limiting, and observability, all instrumented and "
            "containerized, with an evaluation harness gating changes before they'd reach "
            "production traffic.\n\n"
            "```\n"
            "        Client\n"
            "          |\n"
            "          v\n"
            "  [Rate Limiter] --(429 if exceeded)-->\n"
            "          |\n"
            "          v\n"
            "  [Auth: API key / JWT + scopes]\n"
            "          |\n"
            "          v\n"
            "  [FastAPI routes] ---> [Cache check] ---(hit)---> cached response\n"
            "          |                                  |\n"
            "          v                                  v (miss)\n"
            "  [Agent System] <---> [Database: conversations, runs, tenant-isolated]\n"
            "          |\n"
            "          v\n"
            "  [Structured Logs] + [Metrics] + [Traces] ---> dashboards / alerts\n"
            "          |\n"
            "          v\n"
            "  response (+ cost recorded against token budget)\n"
            "\n"
            "  [Docker image] ---deployed with---> [health/readiness checks] + [rollout strategy]\n"
            "  [Eval harness] ---gates---> changes before rollout\n"
            "```"
        ),
        "milestones": [
            {"title": "Service skeleton with auth and persistence", "description": "The agent is reachable through authenticated FastAPI endpoints, with conversations/runs correctly persisted and tenant-isolated."},
            {"title": "Caching and rate limiting working", "description": "At least one operation is verifiably served from cache on a repeat request, and rate limiting correctly returns 429s beyond the configured limit."},
            {"title": "Observability instrumented", "description": "Structured logs, metrics, and correlation-id tracing are in place, demonstrated by reconstructing one full request's trace from logs alone."},
            {"title": "Cost controls verified", "description": "Token budget enforcement and model routing are demonstrated with a test that would exceed budget without them, and succeeds with them."},
            {"title": "Containerized, deployed, and evaluated", "description": "The service runs in a container with working health checks, and the evaluation harness runs against it with documented results."},
        ],
        "tasks": [
            {"title": "Choose and prepare the base agent system", "description": "Select an agent system from an earlier project (or build a focused new one) to serve as the capstone's core."},
            {"title": "Build the FastAPI service layer", "description": "Implement typed routes, including at least one streaming endpoint, wrapping the agent system."},
            {"title": "Implement authentication and scopes", "description": "Add API key or JWT authentication with at least one scoped permission distinction enforced at the tool-dispatch layer."},
            {"title": "Implement persistence with tenant isolation", "description": "Design and implement the database schema for conversations/runs, enforcing tenant isolation at the query or RLS layer."},
            {"title": "Implement caching", "description": "Add exact-match (and optionally semantic) caching for at least one expensive, safely-cacheable operation."},
            {"title": "Implement rate limiting", "description": "Add per-caller token-bucket rate limiting with informative rate-limit response headers."},
            {"title": "Instrument logging, metrics, and tracing", "description": "Add structured logging with bound correlation ids, Prometheus-style metrics, and span-based tracing for agent runs."},
            {"title": "Implement cost controls", "description": "Add a per-request token budget and at least one cost-aware model-routing decision, verified under a deliberate stress test."},
            {"title": "Containerize and add health checks", "description": "Write a multi-stage Dockerfile with a non-root user and working liveness/readiness endpoints reflecting real dependency health."},
            {"title": "Run the evaluation harness and document rollout strategy", "description": "Run an evaluation suite against the deployed service, and write up your rollout strategy (blue-green or canary) with specific rollback triggers."},
        ],
        "expected_output": (
            "A deployed (locally containerized at minimum) agent service with authentication, "
            "tenant-isolated persistence, caching, rate limiting, full observability "
            "instrumentation, and enforced cost controls — accompanied by an evaluation report "
            "run against the live service, a documented rollout/rollback strategy, and a full "
            "request trace reconstructed from logs for at least one example run."
        ),
        "evaluation_criteria": [
            {"criterion": "Service correctness: auth, persistence, caching, and rate limiting all function correctly under test", "weight": 0.2},
            {"criterion": "Observability: a full request can be traced end to end from structured logs and metrics alone", "weight": 0.2},
            {"criterion": "Cost control: token budgets and model routing demonstrably prevent runaway spend under a stress scenario", "weight": 0.2},
            {"criterion": "Security and isolation: tenant isolation and scoped permissions are verified with explicit tests, not just assumed", "weight": 0.15},
            {"criterion": "Deployment readiness: the service is containerized with working health checks and a documented, justified rollout strategy", "weight": 0.15},
            {"criterion": "Evaluation rigor: the evaluation harness runs against the real service and results are reported honestly", "weight": 0.1},
        ],
        "resources": [
            {"title": "FastAPI: Official documentation", "url": "https://fastapi.tiangolo.com/", "resource_type": "docs"},
            {"title": "Google SRE Book: Implementing SLOs", "url": "https://sre.google/workbook/implementing-slos/", "resource_type": "article"},
            {"title": "OpenTelemetry: Traces specification", "url": "https://opentelemetry.io/docs/specs/otel/trace/", "resource_type": "docs"},
        ],
        "order_index": 7,
        "estimated_hours": 24,
        "difficulty": "advanced",
        "skills": [
            {"slug": "production-ai", "weight": 1.0},
            {"slug": "langgraph", "weight": 0.5},
            {"slug": "evaluation", "weight": 0.7},
        ],
    },
]
