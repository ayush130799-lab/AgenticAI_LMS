"""
Course 6: Retrieval Augmented Generation

Teaches the end-to-end RAG pipeline: ingesting and cleaning documents,
chunking them sensibly, embedding and indexing chunks, retrieving relevant
context, constructing prompts, generating grounded answers with citations,
and evaluating the whole system. Builds directly on Course 5's embeddings
and vector database foundations.
"""

COURSE = {
    "slug": "retrieval-augmented-generation",
    "title": "Retrieval Augmented Generation",
    "subtitle": "Ground LLM answers in your own data, from raw documents to cited responses.",
    "description": (
        "Retrieval Augmented Generation (RAG) is the pattern that turns a general-purpose LLM "
        "into a system that answers accurately from your organization's own documents instead "
        "of guessing from training data. This course walks the full pipeline end to end: "
        "ingesting and cleaning real documents, chunking them without destroying meaning, "
        "embedding and indexing at scale, retrieving with precision, constructing grounded "
        "prompts, generating cited answers, and rigorously evaluating the result. You'll build "
        "a working RAG system piece by piece rather than just calling a black-box library."
    ),
    "learning_outcomes": [
        "Explain why RAG exists and when it beats fine-tuning or a bigger context window",
        "Build an ingestion pipeline that loads, cleans, and normalizes real-world documents",
        "Apply chunking strategies that preserve meaning and tune chunk size for retrieval quality",
        "Embed and index document chunks for fast semantic retrieval",
        "Implement hybrid search and reranking to improve retrieval precision",
        "Construct grounded prompts with metadata filtering and inline citations",
        "Evaluate a RAG system's retrieval quality and generation faithfulness with real metrics",
        "Apply advanced RAG techniques like query transformation and agentic self-correction",
    ],
    "order_index": 6,
    "estimated_hours": 22,
    "level": "intermediate",
    "icon": "search",
    "modules": [
        # ---------------------------------------------------------------
        {
            "slug": "what-is-rag",
            "title": "What is RAG?",
            "description": "Why grounding LLM generation in retrieved documents solves problems that prompting and fine-tuning alone cannot.",
            "order_index": 1,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-llms-need-retrieval",
                    "title": "Why LLMs Need Retrieval",
                    "description": "Understand the hallucination and knowledge-cutoff problems that RAG was invented to solve.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why an LLM's parametric knowledge is incomplete and can go stale",
                        "Define hallucination and describe why it happens even in well-trained models",
                        "Contrast RAG with fine-tuning and long-context approaches to grounding",
                        "Identify the kinds of questions RAG is and isn't well suited to answer",
                    ],
                    "content_markdown": """
## Why this matters

Every LLM you'll build agents with has a hard ceiling: it only knows what was in its training
data, frozen at a cutoff date, compressed into billions of weights. Ask it about your
company's internal refund policy, a document uploaded yesterday, or last week's product
release, and it will either say it doesn't know or, worse, confidently make something up.
Retrieval Augmented Generation exists to close that gap without retraining the model.

## The two failure modes RAG addresses

**Knowledge cutoff.** A model trained through early 2025 has no idea what happened in
September 2026, no matter how you phrase the prompt. Retrieval fixes this by fetching current
information at query time and handing it to the model as context.

**Hallucination.** When an LLM doesn't know an answer, it doesn't reliably say "I don't know" —
it generates the statistically plausible next tokens, which can look exactly like a real,
confident answer while being entirely fabricated. This is especially dangerous for narrow,
factual, or internal-only information the model was never trained on in the first place.

```python
# Without retrieval: the model guesses from parametric memory
response = llm.generate("What is Acme Corp's 2026 return policy?")
# May confidently invent a plausible-sounding but wrong policy

# With retrieval: the model is grounded in an actual source document
context = retrieve("Acme Corp return policy")
response = llm.generate(f"Using only this context, answer the question.\\n\\nContext: {context}\\n\\nQuestion: What is Acme Corp's 2026 return policy?")
# Answer is traceable back to a real document
```

## RAG vs. fine-tuning vs. long context

Three approaches compete to solve the "the model doesn't know X" problem, and they are not
interchangeable:

- **Fine-tuning** bakes new knowledge or behavior into model weights. It's expensive to
  update, doesn't scale well to fast-changing facts, and still hallucinates on details it
  wasn't explicitly trained on.
- **Long context** stuffs entire documents into the prompt. It works for small, static
  corpora but gets expensive and less accurate as context grows — models attend less reliably
  to information buried in the middle of a huge context window.
- **RAG** retrieves only the relevant slice of a large, frequently changing corpus at query
  time, keeping prompts small, answers current, and — critically — traceable to a source
  document you can point to.

## What RAG is good at, and what it isn't

RAG shines for question-answering over private or fast-changing knowledge: internal wikis,
support docs, contracts, codebases. It's a poor fit for tasks that need reasoning across an
entire corpus at once (like "summarize every contract we signed this year") or tasks with no
underlying documents to retrieve from (like open-ended creative writing). Recognizing which
category a task falls into, before reaching for RAG, will save you from building the wrong
system.

## The pipeline, at a glance

RAG breaks into two phases you'll build across this course: an **offline** phase (ingest,
clean, chunk, embed, index documents once) and an **online** phase (retrieve, construct
context, generate, cite — run per user query). Keeping this split in mind will make every
later module click into place as one stage of a coherent pipeline rather than an isolated
trick.
""",
                    "examples": [
                        {
                            "title": "A hallucination you can reproduce",
                            "code": (
                                "prompt = \"What was Acme Corp's Q3 2026 revenue?\"\n"
                                "# Ask a model with no retrieval access this question about a\n"
                                "# fictional or very recent company. It will often produce a\n"
                                "# specific, confident-sounding number that is entirely made up,\n"
                                "# because 'a plausible number' is what next-token prediction\n"
                                "# rewards in the absence of real data."
                            ),
                            "explanation": "Hallucination isn't a bug that shows up rarely -- it's the expected behavior whenever a model is asked about something outside its training data, which is exactly the gap RAG closes.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List three questions about your own organization (or a hypothetical company) that an LLM could not answer correctly without retrieval, and explain why each one requires current or private information.",
                            "difficulty": "easy",
                            "hint": "Think about anything that changes over time or was never public: pricing, internal policies, recent announcements.",
                        },
                        {
                            "prompt": "For a customer support chatbot, decide whether fine-tuning, long context, or RAG is the best fit, and justify your answer using the tradeoffs from this lesson.",
                            "difficulty": "medium",
                            "hint": "Consider how often support documentation changes and how large the full documentation set is.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (original RAG paper)",
                            "url": "https://arxiv.org/abs/2005.11401",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "llm", "weight": 0.3}],
                },
                {
                    "slug": "anatomy-of-a-rag-pipeline",
                    "title": "Anatomy of a RAG Pipeline",
                    "description": "A map of every stage a RAG system passes through, from raw document to cited answer.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Name and order the stages of a complete RAG pipeline",
                        "Distinguish the offline indexing phase from the online query phase",
                        "Identify which module in this course covers each pipeline stage",
                        "Explain how a failure at an early stage propagates through later stages",
                    ],
                    "content_markdown": """
## Why this matters

RAG tutorials often jump straight to "embed and search," skipping everything before and
after. That produces systems that retrieve garbage or generate ungrounded answers, because
each stage of the pipeline depends on the ones before it. This lesson lays out the full map so
you know exactly what you're building toward for the rest of the course.

## The offline phase: build the index once

```python
# 1. Ingestion   -- load raw documents from files, APIs, databases
documents = load_documents("./knowledge_base")

# 2. Cleaning    -- strip boilerplate, normalize whitespace, dedupe
cleaned = [clean_document(d) for d in documents]

# 3. Chunking    -- split into retrieval-sized units
chunks = [chunk for doc in cleaned for chunk in chunk_document(doc)]

# 4. Embedding   -- convert each chunk to a vector
vectors = embed_texts([c.text for c in chunks])

# 5. Indexing    -- store vectors + metadata in a vector database
vector_db.upsert(ids=[c.id for c in chunks], vectors=vectors, metadata=[c.metadata for c in chunks])
```

This phase runs whenever your source documents change — nightly, on upload, or on a schedule
— not on every user query. Get any of these five steps wrong and everything downstream
suffers: bad chunking produces vectors that mix unrelated ideas, bad cleaning leaves navigation
menus polluting your context, and so on.

## The online phase: answer one query

```python
# 6. Retrieval          -- find the most relevant chunks for this query
query_vec = embed_texts([user_query])[0]
candidates = vector_db.query(vector=query_vec, top_k=20)

# 7. Reranking (optional) -- re-score candidates with a more precise model
reranked = reranker.rerank(user_query, candidates, top_k=5)

# 8. Context construction -- assemble retrieved chunks into a prompt
context = build_context(reranked)

# 9. Generation           -- call the LLM with the grounded prompt
answer = llm.generate(build_prompt(user_query, context))

# 10. Citations            -- attach source references to the answer
cited_answer = attach_citations(answer, reranked)
```

This phase runs on every single user request, so latency and cost matter here in a way they
don't in the offline phase — a good reason retrieval and reranking need to be fast, not just
accurate.

## Failures compound downstream

If ingestion misses a document, no amount of clever retrieval will ever find it. If chunking
splits a sentence containing the actual answer in half, embedding and retrieval will struggle
to match it. If retrieval returns the wrong chunks, generation will confidently answer from
irrelevant context — often *more* confidently than if it had no context at all, because the
prompt tells it to use what it was given. This is why debugging a broken RAG answer means
walking backward through the pipeline stage by stage, not just tweaking the final prompt.

## How this course is organized

Each remaining module in this course corresponds to one or more pipeline stages: Ingestion and
Cleaning (stages 1-2), Chunking (stage 3), Embeddings (stage 4), Retrieval and Hybrid Search
and Reranking (stages 5-7), Context Construction (stage 8), Generation and Citations (stages
9-10), Metadata Filtering (cuts across retrieval), and finally RAG Evaluation and Advanced RAG
tie the whole system together. Keep this map handy — when something goes wrong later, you'll
know exactly which module to revisit.
""",
                    "examples": [
                        {
                            "title": "Tracing one query through all ten stages",
                            "code": (
                                "# A user asks: 'What is the cancellation policy for enterprise plans?'\n"
                                "# 1-5 already happened offline: enterprise docs were ingested,\n"
                                "#    cleaned, chunked, embedded, and indexed last night.\n"
                                "# 6. Retrieval finds 20 chunks mentioning 'cancellation' or 'enterprise'\n"
                                "# 7. Reranking narrows to the 5 chunks most relevant to THIS query\n"
                                "# 8. Context construction assembles those 5 chunks into a prompt\n"
                                "# 9. Generation produces an answer grounded in that context\n"
                                "# 10. Citations attach links back to the source policy document"
                            ),
                            "explanation": "Walking through a concrete query like this makes the abstract ten-stage pipeline concrete and shows exactly where offline work ends and online work begins.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Draw or describe the ten-stage pipeline from memory, labeling which stages run offline and which run online.",
                            "difficulty": "easy",
                            "hint": "Offline stages build the index once; online stages run per query.",
                        },
                        {
                            "prompt": "A RAG system answers confidently but incorrectly about a policy that was updated last week. Walk through the pipeline stages and list the two most likely root causes.",
                            "difficulty": "medium",
                            "hint": "Consider whether ingestion re-ran after the update, and whether the old chunk was ever removed from the index.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain: RAG conceptual guide",
                            "url": "https://python.langchain.com/docs/concepts/rag/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "document-ingestion",
            "title": "Document Ingestion",
            "description": "Loading raw documents from the many formats and sources a real knowledge base is made of.",
            "order_index": 2,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "loading-documents-from-diverse-sources",
                    "title": "Loading Documents from Diverse Sources",
                    "description": "Write loaders that pull text out of PDFs, HTML, Markdown, and databases into a common document format.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Identify the common document formats a real ingestion pipeline must handle",
                        "Implement loaders that normalize different sources into one document schema",
                        "Preserve source metadata (URL, file path, timestamp) during loading",
                        "Explain why a unified document representation simplifies every later pipeline stage",
                    ],
                    "content_markdown": """
## Why this matters

Real knowledge bases are never one tidy format. A single company's documentation might live in
PDFs, Confluence HTML exports, Markdown READMEs, and rows in a support ticket database.
Ingestion is the stage that turns all of that chaos into one consistent shape so every later
stage (cleaning, chunking, embedding) can be written once instead of once per format.

## A common document schema

Before writing any loader, decide on a single representation every loader must produce. This
is the contract the rest of your pipeline relies on.

```python
from dataclasses import dataclass, field

@dataclass
class RawDocument:
    id: str
    text: str
    source: str          # file path or URL
    doc_type: str         # "pdf", "html", "markdown", "db_row"
    metadata: dict = field(default_factory=dict)
```

## Loaders per format

```python
import pypdf

def load_pdf(path: str) -> RawDocument:
    reader = pypdf.PdfReader(path)
    text = "\\n".join(page.extract_text() or "" for page in reader.pages)
    return RawDocument(id=path, text=text, source=path, doc_type="pdf")

from bs4 import BeautifulSoup

def load_html(path: str) -> RawDocument:
    with open(path, encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "html.parser")
    text = soup.get_text(separator="\\n")
    return RawDocument(id=path, text=text, source=path, doc_type="html")

def load_markdown(path: str) -> RawDocument:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return RawDocument(id=path, text=text, source=path, doc_type="markdown")
```

Each loader is deliberately small: extract text, wrap it in `RawDocument`, done. Format-specific
parsing (stripping tags, decoding PDF layout quirks) stays isolated in its own function so a
bug in the PDF loader can never affect the Markdown loader.

## Loading from a database

Not every document is a file. Support tickets, product catalogs, and CMS entries often live in
a database and need to be loaded row by row.

```python
def load_from_db(rows: list[dict]) -> list[RawDocument]:
    return [
        RawDocument(
            id=f"ticket-{row['id']}",
            text=row["body"],
            source=f"db://tickets/{row['id']}",
            doc_type="db_row",
            metadata={"created_at": row["created_at"], "status": row["status"]},
        )
        for row in rows
    ]
```

## Assembling a pipeline that dispatches by type

```python
import os

LOADERS = {".pdf": load_pdf, ".html": load_html, ".md": load_markdown}

def load_documents(folder: str) -> list[RawDocument]:
    docs = []
    for filename in os.listdir(folder):
        ext = os.path.splitext(filename)[1]
        loader = LOADERS.get(ext)
        if loader:
            docs.append(loader(os.path.join(folder, filename)))
    return docs
```

## Why metadata matters this early

Notice every loader captures `source` and sometimes extra `metadata` even though nothing
downstream needs it yet. Capture it now anyway — retrofitting metadata after documents have
already been chunked and embedded is far more painful than carrying it through from the start.
You'll use this metadata heavily in the Citations and Metadata Filtering modules later in this
course.
""",
                    "examples": [
                        {
                            "title": "Dispatch-by-extension pattern",
                            "code": (
                                "docs = load_documents(\"./knowledge_base\")\n"
                                "print(len(docs), \"documents loaded\")\n"
                                "print(docs[0].doc_type, docs[0].source)"
                            ),
                            "explanation": "A single entry point that dispatches to format-specific loaders keeps the rest of the ingestion pipeline blissfully unaware of file formats.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a loader for plain .txt files that follows the same RawDocument schema as the PDF and HTML loaders.",
                            "difficulty": "easy",
                            "hint": "This is the simplest loader -- just read the file and wrap it, no parsing library needed.",
                        },
                        {
                            "prompt": "Extend load_documents to log a warning (not crash) when it encounters a file extension with no registered loader.",
                            "difficulty": "medium",
                            "hint": "Check the LOADERS dict for a miss and print or log instead of silently skipping.",
                        },
                        {
                            "prompt": "Add a CSV loader that treats each row as a separate RawDocument, using one column as the text and the rest as metadata.",
                            "difficulty": "medium",
                            "hint": "Python's built-in csv.DictReader gives you each row as a dict already.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain document loaders overview",
                            "url": "https://python.langchain.com/docs/concepts/document_loaders/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "python", "weight": 0.4}],
                },
                {
                    "slug": "building-an-ingestion-pipeline",
                    "title": "Building an End-to-End Ingestion Pipeline",
                    "description": "Combine loaders into a single, re-runnable ingestion job with change detection and error handling.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Compose individual loaders into one orchestrated ingestion pipeline",
                        "Detect which documents changed since the last run to avoid reprocessing everything",
                        "Handle and log per-document failures without aborting the whole job",
                        "Explain why ingestion should be idempotent and safely re-runnable",
                    ],
                    "content_markdown": """
## Why this matters

A one-off script that loads documents once is easy. A pipeline that safely re-runs every night
against a knowledge base that's constantly changing — without duplicating unchanged documents
or crashing on one bad file — is what actually ships to production.

## Detecting what changed

Re-embedding every document on every run wastes money and time. Track a content hash per
document so you only reprocess what actually changed.

```python
import hashlib

def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def find_changed_documents(docs: list, previous_hashes: dict[str, str]) -> list:
    changed = []
    for doc in docs:
        current_hash = content_hash(doc.text)
        if previous_hashes.get(doc.id) != current_hash:
            changed.append(doc)
    return changed
```

## Handling per-document failures

One malformed PDF should not take down an ingestion job processing ten thousand documents.

```python
def load_documents_safely(folder: str) -> tuple[list, list]:
    successes, failures = [], []
    for filename in os.listdir(folder):
        try:
            loader = LOADERS.get(os.path.splitext(filename)[1])
            if loader:
                successes.append(loader(os.path.join(folder, filename)))
        except Exception as exc:
            failures.append({"file": filename, "error": str(exc)})
    return successes, failures
```

Logging failures instead of swallowing them silently is what lets you notice, a week later,
that an entire subfolder of documents was never indexed because of a recurring parsing bug.

## The full orchestration

```python
def run_ingestion_pipeline(folder: str, previous_hashes: dict[str, str]) -> dict:
    docs, failures = load_documents_safely(folder)
    changed = find_changed_documents(docs, previous_hashes)

    cleaned = [clean_document(d) for d in changed]
    chunks = [c for d in cleaned for c in chunk_document(d)]
    vectors = embed_texts([c.text for c in chunks])
    vector_db.upsert(ids=[c.id for c in chunks], vectors=vectors, metadata=[c.metadata for c in chunks])

    new_hashes = {d.id: content_hash(d.text) for d in docs}
    return {"processed": len(changed), "failed": len(failures), "hashes": new_hashes, "errors": failures}
```

## Idempotency: the property that lets you sleep at night

An ingestion job is **idempotent** if running it twice in a row with no source changes produces
the same index state as running it once. Using `upsert` (insert-or-update by ID) instead of
blind `insert`, and skipping documents whose hash hasn't changed, are both what make this
pipeline safe to re-run on a schedule, retry after a crash, or trigger manually without fear of
duplicating every chunk in your vector database.

## Deletions matter too

If a source document is removed, your pipeline also needs to remove its chunks from the index
— otherwise your RAG system keeps citing content that no longer exists. Track the full set of
current document IDs each run, diff it against what's in the vector database, and issue
deletes for anything missing.
""",
                    "examples": [
                        {
                            "title": "Skipping unchanged documents on a re-run",
                            "code": (
                                "previous_hashes = load_hash_cache(\"./hash_cache.json\")\n"
                                "result = run_ingestion_pipeline(\"./knowledge_base\", previous_hashes)\n"
                                "print(f\"Processed {result['processed']} changed docs, {result['failed']} failures\")\n"
                                "save_hash_cache(\"./hash_cache.json\", result[\"hashes\"])"
                            ),
                            "explanation": "On the second run with no source changes, 'processed' drops to 0 because every document's hash already matches -- exactly the idempotent behavior a nightly job needs.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement the deletion-detection step described at the end of this lesson: given the current set of document IDs and the vector database's existing IDs, return the list of IDs that should be deleted.",
                            "difficulty": "medium",
                            "hint": "This is a set difference: existing_ids - current_ids.",
                        },
                        {
                            "prompt": "Add retry-with-backoff around the embedding call in run_ingestion_pipeline so a transient API failure doesn't fail the whole batch.",
                            "difficulty": "medium",
                            "hint": "Reuse the retry pattern from the Embeddings course if you've taken it, or write a simple loop with exponential backoff.",
                        },
                        {
                            "prompt": "Explain in your own words why using upsert instead of insert is required for idempotency, with a concrete example of what would go wrong otherwise.",
                            "difficulty": "easy",
                            "hint": "Think about what happens to duplicate detection and search relevance if the same chunk gets inserted twice.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Chroma: updating and deleting data",
                            "url": "https://docs.trychroma.com/docs/collections/manage-data",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "document-cleaning",
            "title": "Document Cleaning",
            "description": "Turning noisy extracted text into clean, meaningful prose before it's chunked and embedded.",
            "order_index": 3,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-raw-text-needs-cleaning",
                    "title": "Why Raw Extracted Text Needs Cleaning",
                    "description": "See the kinds of noise that leak into text extracted from PDFs, HTML, and exports, and why they hurt retrieval.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify common noise patterns introduced by document extraction",
                        "Explain how boilerplate text degrades embedding quality and retrieval precision",
                        "Distinguish content worth keeping from content worth stripping",
                        "Recognize encoding and whitespace issues that silently corrupt text",
                    ],
                    "content_markdown": """
## Why this matters

Extracted text is rarely clean. A PDF loader might interleave page headers with body text; an
HTML export drags along navigation menus and cookie banners; a Markdown export might carry
broken link syntax. If you embed that noise directly, you're not embedding your content — you're
embedding your content plus a variable amount of garbage that dilutes the very meaning you want
retrieval to key on.

## Common sources of noise

**Boilerplate.** Headers, footers, page numbers, "Copyright 2026 Acme Corp," navigation links,
and cookie-consent text repeat across every page of a document but carry no unique
information. If ten chunks of your corpus all contain the same footer, retrieval will treat
"footer similarity" as meaningful when it isn't.

```python
BOILERPLATE_PATTERNS = [
    r"^Page \\d+ of \\d+$",
    r"^Copyright \\d{4}.*All rights reserved\\.?$",
    r"^Skip to (main )?content$",
]

import re

def strip_boilerplate(text: str) -> str:
    lines = text.split("\\n")
    kept = [line for line in lines if not any(re.match(p, line.strip()) for p in BOILERPLATE_PATTERNS)]
    return "\\n".join(kept)
```

**Whitespace chaos.** PDF extraction in particular tends to produce inconsistent spacing,
stray line breaks mid-sentence, and repeated blank lines. This doesn't just look ugly — it can
break sentence-boundary-aware chunking (covered in the next module) if a chunker can't reliably
find where one sentence ends and the next begins.

**Encoding artifacts.** Smart quotes, non-breaking spaces, and mis-decoded bytes (like
"donâ€™t" instead of "don't") are a classic sign of an encoding mismatch during extraction.
These break both readability and any exact-match keyword search you layer on top later in
Hybrid Search.

**Structural noise.** Tables extracted from PDFs often turn into a wall of misaligned numbers
with no column structure; a chunk built purely from that is nearly useless as retrieval
context, even though the answer may technically be present.

## What to keep, not just what to strip

Cleaning isn't only subtraction. Preserving genuine structure — headings, list markers,
paragraph breaks — helps later chunking respect natural document boundaries instead of cutting
mid-thought. The goal of cleaning is not "make it as short as possible" but "make what remains
maximally meaning-dense."

## The cost of skipping this step

Teams that skip cleaning and chunk raw extracted text often see retrieval that returns the
right document but the wrong chunk — a footer or a broken table fragment instead of the
sentence that actually answers the question. Because this failure looks like a retrieval
problem, it's commonly misdiagnosed and "fixed" by tuning top_k or switching embedding models,
when the real fix was upstream, in cleaning.
""",
                    "examples": [
                        {
                            "title": "Before and after cleaning",
                            "code": (
                                "raw = \"Page 3 of 12\\n\\n\\nOur   refund   policy allows\\nreturns within 30 days.\\n\\nCopyright 2026 Acme Corp. All rights reserved.\"\n"
                                "cleaned = strip_boilerplate(normalize_whitespace(raw))\n"
                                "print(cleaned)\n"
                                "# 'Our refund policy allows returns within 30 days.'"
                            ),
                            "explanation": "Stripping page numbers and copyright lines while normalizing spacing leaves exactly the sentence that matters for retrieval and generation.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Take a real PDF you have access to, extract its text with any library, and list five distinct types of noise you observe in the raw output.",
                            "difficulty": "easy",
                            "hint": "Look specifically at page boundaries, headers/footers, and any tables.",
                        },
                        {
                            "prompt": "Write a regex pattern that detects and strips a repeated email-signature block from a set of extracted support ticket texts.",
                            "difficulty": "medium",
                            "hint": "Look for a consistent structural marker like '--' or 'Best regards' that starts the signature block.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Unstructured.io: cleaning bricks reference",
                            "url": "https://docs.unstructured.io/open-source/core-functionality/cleaning",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}],
                },
                {
                    "slug": "normalizing-and-deduplicating-text",
                    "title": "Normalizing and Deduplicating Text",
                    "description": "Implement whitespace normalization, encoding fixes, and near-duplicate detection before chunking.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement whitespace and encoding normalization for extracted text",
                        "Detect and remove exact duplicate documents",
                        "Detect near-duplicate documents using similarity thresholds",
                        "Explain the retrieval-quality cost of leaving duplicates in an index",
                    ],
                    "content_markdown": """
## Why this matters

Two problems that look cosmetic actually damage retrieval quality directly: inconsistent
text formatting confuses downstream chunkers, and duplicate content wastes retrieval slots on
redundant chunks — pushing genuinely different, useful chunks out of your top-k results.

## Normalizing whitespace and encoding

```python
import re
import unicodedata

def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)          # fix encoding artifacts
    text = text.replace("\\u00a0", " ")                   # non-breaking space -> regular space
    text = re.sub(r"[ \\t]+", " ", text)                  # collapse repeated spaces/tabs
    text = re.sub(r"\\n{3,}", "\\n\\n", text)               # collapse 3+ blank lines to 1
    return text.strip()
```

`unicodedata.normalize("NFKC", ...)` handles a surprising number of encoding issues in one call
by converting visually-equivalent but differently-encoded characters (like curly vs. straight
quotes) into a consistent form.

## Exact duplicate detection

Exact duplicates are common when the same document gets exported to multiple formats, or a
support macro gets pasted into hundreds of tickets verbatim.

```python
import hashlib

def dedupe_exact(docs: list) -> list:
    seen_hashes = set()
    unique = []
    for doc in docs:
        h = hashlib.sha256(doc.text.encode("utf-8")).hexdigest()
        if h not in seen_hashes:
            seen_hashes.add(h)
            unique.append(doc)
    return unique
```

## Near-duplicate detection

Near-duplicates are trickier: two documents that are 95% identical (a policy doc with one
paragraph updated) will have different hashes but should often still be treated as
duplicates for retrieval purposes. Embedding similarity is one practical way to catch these.

```python
import numpy as np

def dedupe_near(docs: list, embeddings: list, threshold: float = 0.98) -> list:
    keep_indices = []
    kept_vectors = []
    for i, vec in enumerate(embeddings):
        v = np.array(vec)
        v_norm = v / np.linalg.norm(v)
        is_duplicate = any(
            float(np.dot(v_norm, kept)) > threshold for kept in kept_vectors
        )
        if not is_duplicate:
            keep_indices.append(i)
            kept_vectors.append(v_norm)
    return [docs[i] for i in keep_indices]
```

A high threshold like 0.98 catches only near-identical text, not merely related content —
setting it too low would incorrectly discard genuinely distinct documents that happen to share
a topic.

## Why duplicates hurt retrieval, concretely

If three near-identical chunks about your refund policy all make it into the index, a query
about refunds may return all three in the top-5 results, crowding out a fourth, genuinely
different chunk about *exceptions* to the refund policy that the user actually needed.
Deduplication isn't just about storage efficiency — it directly improves the diversity and
usefulness of what retrieval returns.

## Where this fits in the pipeline

Run normalization before chunking (so chunk boundaries land on clean text) and run
deduplication after chunking but before embedding — deduplicating at the chunk level, not just
the document level, catches repeated boilerplate sections that survive even after
document-level cleaning.
""",
                    "examples": [
                        {
                            "title": "Full cleaning pipeline for one document",
                            "code": (
                                "doc.text = strip_boilerplate(normalize_text(doc.text))\n"
                                "cleaned_docs = dedupe_exact([doc for doc in all_docs])\n"
                                "# Near-dedup runs later, after chunk-level embeddings exist"
                            ),
                            "explanation": "Normalization and exact dedup run cheaply at the document level; near-dedup is deferred to the chunk level once embeddings are available.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Given two strings that differ only in curly vs. straight quotes and spacing, write a test proving normalize_text makes them identical.",
                            "difficulty": "easy",
                            "hint": "Use assert normalize_text(a) == normalize_text(b).",
                        },
                        {
                            "prompt": "Extend dedupe_near to also return, for each removed near-duplicate, which kept document it was considered a duplicate of, for auditability.",
                            "difficulty": "medium",
                            "hint": "Track the index of the kept vector that triggered the duplicate match, not just a boolean.",
                        },
                        {
                            "prompt": "Explain why a 0.98 cosine similarity threshold for near-duplicate detection is safer than 0.85, using an example of two related-but-distinct documents that might wrongly be merged at the lower threshold.",
                            "difficulty": "medium",
                            "hint": "Think about two different FAQ answers on a closely related topic.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Python unicodedata documentation",
                            "url": "https://docs.python.org/3/library/unicodedata.html",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "python", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "chunking",
            "title": "Chunking",
            "description": "Splitting cleaned documents into retrieval-sized units without cutting meaning in half.",
            "order_index": 4,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "chunking-strategies-overview",
                    "title": "Chunking Strategies Overview",
                    "description": "Survey fixed-size, recursive, and semantic chunking, and understand when each is the right tool.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why documents must be chunked before embedding",
                        "Compare fixed-size, recursive, and semantic chunking strategies",
                        "Identify the failure modes of naive fixed-size chunking",
                        "Choose an appropriate chunking strategy given a document type",
                    ],
                    "content_markdown": """
## Why this matters

Embedding models compress a chunk of text into one vector. Feed them a whole 50-page document
and the vector becomes a blurry average of everything in it — useless for finding the one
paragraph that actually answers a specific question. Feed them a single word and there's no
context to embed meaningfully. Chunking is the art of finding the unit size in between that
preserves enough context to be meaningful while staying small enough to be precise.

## Fixed-size chunking

The simplest strategy: split text into chunks of N characters or tokens, often with some
overlap between consecutive chunks.

```python
def fixed_size_chunks(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

It's fast and predictable, but it has no awareness of sentence or paragraph boundaries — it
will happily cut a sentence in half at the exact character offset, splitting an answer across
two chunks and hurting both embedding quality and retrieval.

## Recursive character chunking

A smarter default: try to split on the largest natural boundary first (paragraph breaks), and
only fall back to smaller boundaries (sentences, then words, then characters) if a piece is
still too big.

```python
SEPARATORS = ["\\n\\n", "\\n", ". ", " ", ""]

def recursive_split(text: str, chunk_size: int, separators: list[str] = SEPARATORS) -> list[str]:
    separator = separators[0]
    parts = text.split(separator) if separator else list(text)
    chunks, current = [], ""
    for part in parts:
        candidate = current + separator + part if current else part
        if len(candidate) <= chunk_size:
            current = candidate
        else:
            if current:
                chunks.append(current)
            if len(part) > chunk_size and len(separators) > 1:
                chunks.extend(recursive_split(part, chunk_size, separators[1:]))
                current = ""
            else:
                current = part
    if current:
        chunks.append(current)
    return chunks
```

This respects paragraph and sentence boundaries whenever possible, which is why it's the
default chunking strategy in most production RAG libraries.

## Semantic chunking

The most advanced approach: embed consecutive sentences and split at points where semantic
similarity drops sharply, meaning the topic actually changed — rather than splitting at a fixed
character count that has no relationship to where ideas begin and end.

```python
# Conceptually:
# 1. Split text into sentences
# 2. Embed each sentence
# 3. Compute similarity between consecutive sentence embeddings
# 4. Insert a chunk boundary wherever similarity drops below a threshold
```

Semantic chunking produces chunks that align with actual topic shifts, at the cost of an
embedding call per sentence during chunking — meaningfully more expensive and slower than
fixed-size or recursive splitting.

## Choosing a strategy

| Document type | Recommended strategy |
|---|---|
| Well-structured Markdown/HTML with headings | Recursive, split on headings first |
| Long-form prose (reports, articles) | Recursive or semantic |
| Code files | Split on function/class boundaries, not characters |
| Chat transcripts / support tickets | Often chunk per-message or per-ticket, not by size at all |

Start with recursive character chunking as a strong default; reach for semantic chunking only
after you've measured that boundary quality is actually limiting your retrieval accuracy, since
it's the most expensive option of the three.
""",
                    "examples": [
                        {
                            "title": "Fixed-size chunking cutting a sentence in half",
                            "code": (
                                "text = \"Our refund policy allows returns within 30 days of purchase, no questions asked.\"\n"
                                "chunks = fixed_size_chunks(text, chunk_size=40, overlap=0)\n"
                                "print(chunks)\n"
                                "# ['Our refund policy allows returns within', ' 30 days of purchase, no questions ask', 'ed.']\n"
                                "# The key number '30 days' is split across two chunks"
                            ),
                            "explanation": "This is exactly the failure recursive chunking is designed to avoid -- it would keep 'within 30 days of purchase' together by splitting on sentence or word boundaries instead.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a 200-page legal contract, a Slack export, and a product FAQ page, propose a chunking strategy for each and justify your choice.",
                            "difficulty": "medium",
                            "hint": "Think about natural boundaries each document type already has: clauses, individual messages, Q&A pairs.",
                        },
                        {
                            "prompt": "Trace through fixed_size_chunks by hand on a 100-character string with chunk_size=30 and overlap=10, and list the resulting chunk boundaries.",
                            "difficulty": "easy",
                            "hint": "Track the start index across iterations: it advances by chunk_size - overlap each time.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain: text splitters conceptual guide",
                            "url": "https://python.langchain.com/docs/concepts/text_splitters/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "chunking", "weight": 1.0}],
                },
                {
                    "slug": "implementing-recursive-character-chunking",
                    "title": "Implementing Recursive Character Chunking",
                    "description": "Build and test a production-style recursive chunker that attaches metadata to every chunk it produces.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 35,
                    "learning_objectives": [
                        "Implement a recursive chunker that falls back through multiple separators",
                        "Attach source document metadata and position info to each chunk",
                        "Add configurable overlap between chunks to preserve cross-boundary context",
                        "Write tests that verify chunk boundaries respect sentence structure where possible",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson covered the theory; this one builds a chunker you could actually plug into
a real ingestion pipeline, complete with the metadata every chunk needs to be traceable back to
its source document for citations later in this course.

## Defining the chunk record

```python
from dataclasses import dataclass

@dataclass
class Chunk:
    id: str
    text: str
    doc_id: str
    chunk_index: int
    metadata: dict
```

Every chunk carries a reference back to its parent document (`doc_id`) and its position within
that document (`chunk_index`) — both essential once you build citations and need to say
"this answer came from paragraph 3 of the refund policy."

## The chunker with overlap

```python
def chunk_document(doc, chunk_size: int = 800, overlap: int = 100) -> list[Chunk]:
    pieces = recursive_split(doc.text, chunk_size)
    chunks = []
    for i, piece in enumerate(pieces):
        prefix = pieces[i - 1][-overlap:] if i > 0 and overlap else ""
        chunk_text = (prefix + piece).strip()
        chunks.append(Chunk(
            id=f"{doc.id}-chunk-{i}",
            text=chunk_text,
            doc_id=doc.id,
            chunk_index=i,
            metadata={**doc.metadata, "source": doc.source},
        ))
    return chunks
```

Adding the tail of the previous chunk as a prefix gives each chunk a bit of context from what
came right before it, so a chunk that starts mid-thought ("...which means the deadline
applies.") still carries the sentence that explains what "the deadline" refers to.

## Choosing chunk_size and overlap in practice

There's no universal right number — it depends on your embedding model's effective range and
your documents' structure. A reasonable starting point for prose is 500-1000 characters with
10-15% overlap; you'll tune this empirically in the next lesson using retrieval metrics rather
than guessing.

```python
chunks = chunk_document(doc, chunk_size=800, overlap=100)
print(len(chunks), "chunks produced")
print(chunks[0].text[:100])
print(chunks[0].metadata)
```

## Testing that boundaries make sense

Automated tests can't judge "does this read naturally," but they can catch regressions in
chunk count, overlap presence, and metadata propagation.

```python
def test_chunk_overlap_present():
    doc = RawDocument(id="d1", text="A" * 2000, source="test", doc_type="markdown")
    chunks = chunk_document(doc, chunk_size=500, overlap=100)
    assert len(chunks) > 1
    assert chunks[1].text[:100] == chunks[0].text[-100:]

def test_metadata_propagates():
    doc = RawDocument(id="d1", text="Some text.", source="policy.md", doc_type="markdown", metadata={"category": "billing"})
    chunks = chunk_document(doc, chunk_size=500)
    assert chunks[0].metadata["category"] == "billing"
    assert chunks[0].metadata["source"] == "policy.md"
```

## Why overlap has a cost too

Overlap isn't free: it means the same sentence sometimes appears in two chunks, which slightly
inflates your index size and can cause a retrieval result list to contain two near-duplicate
chunks for the same underlying content. This is a preview of a Metadata Filtering and
Reranking concern later in this course — overlap is a deliberate tradeoff, not a free win.
""",
                    "examples": [
                        {
                            "title": "Chunking a full document into indexable units",
                            "code": (
                                "doc = load_markdown(\"./docs/refund-policy.md\")\n"
                                "cleaned = clean_document(doc)\n"
                                "chunks = chunk_document(cleaned, chunk_size=600, overlap=80)\n"
                                "for c in chunks[:2]:\n"
                                "    print(c.id, len(c.text), c.metadata[\"source\"])"
                            ),
                            "explanation": "This is the exact function call the ingestion pipeline from Module 2 invokes between cleaning and embedding.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Modify chunk_document to skip creating a chunk if its resulting text (after stripping whitespace) is shorter than 20 characters, to avoid indexing near-empty fragments.",
                            "difficulty": "easy",
                            "hint": "Add a length check right before appending to the chunks list.",
                        },
                        {
                            "prompt": "Write a test that verifies chunk_index values are sequential starting from 0 for a document that produces 5 chunks.",
                            "difficulty": "easy",
                            "hint": "Assert [c.chunk_index for c in chunks] == list(range(5)).",
                        },
                        {
                            "prompt": "Extend the Chunk dataclass and chunker to also store char_start and char_end offsets into the original document text, and explain one use case this would enable.",
                            "difficulty": "hard",
                            "hint": "One use case: highlighting the exact retrieved passage in a source document viewer.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain RecursiveCharacterTextSplitter reference",
                            "url": "https://python.langchain.com/docs/how_to/recursive_text_splitter/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "chunking", "weight": 1.0}, {"slug": "python", "weight": 0.4}],
                },
                {
                    "slug": "chunk-size-and-overlap-tradeoffs",
                    "title": "Chunk Size and Overlap Tradeoffs",
                    "description": "Tune chunk_size and overlap empirically using retrieval quality signals instead of guessing.",
                    "lesson_type": "reading",
                    "order_index": 3,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain how chunk size affects embedding specificity and context completeness",
                        "Describe the precision/recall tradeoff introduced by chunk size",
                        "Design a simple experiment to compare chunk_size settings using retrieval metrics",
                        "Recognize symptoms in retrieved results that point to chunk size being misconfigured",
                    ],
                    "content_markdown": """
## Why this matters

Chunk size is one of the highest-leverage parameters in a RAG system, and yet it's often set
once, arbitrarily, and never revisited. A chunk size that's wrong in either direction produces
retrieval that looks broken even though every other part of the pipeline is correct.

## Too small: precise but incomplete

Very small chunks (a sentence or two) embed a narrow, specific idea, which can make similarity
matching sharper. But a chunk that's too small often lacks the surrounding context needed to
actually answer a question — "This applies only to orders placed after that date" means nothing
without the preceding sentence defining "that date."

## Too large: complete but diluted

Very large chunks (multiple pages) carry plenty of context but dilute the embedding: if a
5,000-character chunk contains one sentence relevant to the query and 4,900 characters of
unrelated content, the resulting vector represents an average that may not be close to the
query vector at all, even though the answer is technically present in the chunk.

```python
# A useful mental model: embedding quality roughly follows an inverted U
# as chunk size increases -- too small loses context, too large dilutes signal.
# The right size depends on your documents' natural "unit of thought":
# a paragraph, a Q&A pair, a function, a support ticket.
```

## Designing an experiment instead of guessing

The only reliable way to pick chunk_size is to measure retrieval quality across a few candidate
settings against a small labeled evaluation set — pairs of (query, chunk that should be
retrieved).

```python
def evaluate_chunk_size(chunk_size: int, overlap: int, eval_queries: list[dict]) -> float:
    chunks = [c for doc in documents for c in chunk_document(doc, chunk_size, overlap)]
    vectors = embed_texts([c.text for c in chunks])
    index = build_index(chunks, vectors)

    hits = 0
    for item in eval_queries:
        results = index.search(embed_texts([item["query"]])[0], top_k=5)
        if any(item["expected_doc_id"] == r.doc_id for r in results):
            hits += 1
    return hits / len(eval_queries)

for size in [300, 500, 800, 1200]:
    score = evaluate_chunk_size(size, overlap=int(size * 0.15), eval_queries=eval_set)
    print(f"chunk_size={size}: recall@5={score:.2f}")
```

This is a preview of the RAG Evaluation module later in this course — chunking decisions should
be driven by the same kind of measurement you'll formalize there, not by intuition alone.

## Reading the symptoms

- **Retrieved chunks are on-topic but never contain the specific answer** → chunks may be too
  large; the answer is diluted inside a big block of loosely related text.
- **Retrieved chunks are precise but miss surrounding context needed to answer fully** → chunks
  may be too small; consider increasing size or overlap.
- **The same information appears fragmented across multiple retrieved chunks** → overlap may be
  too low, or chunk boundaries are landing mid-thought.

## A practical starting point

For prose-heavy corpora, 500-1000 characters with 10-20% overlap is a reasonable starting
point used across many production systems — but treat it as a hypothesis to validate against
your own evaluation set, not a rule to follow blindly.
""",
                    "examples": [
                        {
                            "title": "Comparing recall@5 across chunk sizes",
                            "code": (
                                "results = {size: evaluate_chunk_size(size, int(size*0.15), eval_set) for size in [300, 500, 800, 1200]}\n"
                                "best_size = max(results, key=results.get)\n"
                                "print(f\"Best chunk_size: {best_size} with recall@5={results[best_size]:.2f}\")"
                            ),
                            "explanation": "Choosing chunk_size from measured recall rather than intuition turns a guess into an evidence-based configuration decision.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a 10-item evaluation set of (query, expected_doc_id) pairs for a small document collection you have access to, and describe how you'd use it to compare two chunk sizes.",
                            "difficulty": "medium",
                            "hint": "Pick questions you know the answer to and identify which source document should be retrieved for each.",
                        },
                        {
                            "prompt": "A retrieved chunk contains the phrase 'as mentioned above, this exception does not apply' with no earlier context in the same chunk. Diagnose the likely chunking issue and propose a fix.",
                            "difficulty": "medium",
                            "hint": "This is a classic symptom of chunk size or overlap being too small relative to how the document references earlier content.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Pinecone: chunking strategies for LLM applications",
                            "url": "https://www.pinecone.io/learn/chunking-strategies/",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "chunking", "weight": 1.0}, {"slug": "rag", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "embeddings-for-rag",
            "title": "Embeddings",
            "description": "Choosing and applying an embedding model specifically for retrieval quality inside a RAG pipeline.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "choosing-an-embedding-model-for-rag",
                    "title": "Choosing an Embedding Model for RAG",
                    "description": "Evaluate embedding models on the dimensions that actually matter for retrieval: quality, cost, latency, and context limits.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Identify the criteria that matter when choosing an embedding model for RAG",
                        "Explain why query-document asymmetry matters for some embedding models",
                        "Compare hosted API embedding models against self-hosted open-source alternatives",
                        "Recognize why re-embedding your whole corpus is required after switching models",
                    ],
                    "content_markdown": """
## Why this matters

Every chunk in your RAG system passes through an embedding model, so its quality sets a hard
ceiling on your retrieval quality no matter how good your chunking or reranking is. Choosing
the right one is a decision worth making deliberately, not defaulting to whatever example code
you copied.

## The criteria that actually matter

- **Retrieval quality (MTEB benchmark scores)** — the Massive Text Embedding Benchmark ranks
  models specifically on retrieval tasks, which is more relevant to RAG than general-purpose
  leaderboards.
- **Dimensionality** — higher dimensions can capture more nuance but cost more to store and
  search; 384-1536 dimensions covers most production use cases well.
- **Max input length** — if your chunks are 800 tokens and the model truncates at 512, you're
  silently losing information on every chunk.
- **Cost and latency** — hosted API models charge per token and add network latency; self-hosted
  open-source models (via sentence-transformers) trade an infrastructure cost for zero
  per-call fees.
- **Query-document asymmetry support** — some models (like `text-embedding-3` and many
  instruction-tuned open models) expect queries and documents to be embedded slightly
  differently for best results.

## Query-document asymmetry

A subtlety that catches people off guard: some embedding models were trained with an explicit
distinction between "this is a search query" and "this is a document to be searched," and
expect you to prefix text accordingly.

```python
# Some open-source models (e.g. certain E5/BGE variants) expect explicit prefixes:
query_text = "query: What is the refund window?"
doc_text = "passage: Refunds are accepted within 30 days of purchase."

query_vec = embed_texts([query_text])[0]
doc_vec = embed_texts([doc_text])[0]
```

Skipping this prefix on a model that expects it silently degrades retrieval quality with no
error message — always check a model's documentation for this requirement before adopting it.

## Hosted API vs. self-hosted

```python
# Hosted (OpenAI-style): simple, no infra, pay per token
from openai import OpenAI
client = OpenAI()
vectors = [d.embedding for d in client.embeddings.create(model="text-embedding-3-small", input=texts).data]

# Self-hosted (sentence-transformers): more setup, no per-call cost, full data control
from sentence_transformers import SentenceTransformer
model = SentenceTransformer("BAAI/bge-small-en-v1.5")
vectors = model.encode(texts, normalize_embeddings=True).tolist()
```

Self-hosting matters most when you have strict data residency requirements, extremely high
query volume where API costs add up, or need offline/air-gapped operation. Hosted APIs win for
speed of iteration and not having to manage GPU infrastructure.

## Switching models means re-indexing everything

Vectors from two different embedding models are **not comparable** — they live in unrelated
geometric spaces, even if they happen to have the same dimensionality. Switching embedding
models requires re-embedding and re-indexing your entire corpus from scratch; there's no
incremental migration path. Factor this cost into your initial model choice rather than
treating it as a trivial config change.

## A practical default

For most teams starting out, a strong hosted model like `text-embedding-3-small` or a strong
open model like `bge-small-en-v1.5` is a safe default — both rank well on MTEB retrieval tasks
and cover the majority of English-language RAG use cases without exotic tuning.
""",
                    "examples": [
                        {
                            "title": "Checking whether a chunk exceeds a model's input limit",
                            "code": (
                                "MAX_TOKENS = 512  # example limit for a given model\n"
                                "for chunk in chunks:\n"
                                "    approx_tokens = len(chunk.text) // 4  # rough estimate\n"
                                "    if approx_tokens > MAX_TOKENS:\n"
                                "        print(f\"Warning: chunk {chunk.id} may be truncated\")"
                            ),
                            "explanation": "A quick token-length sanity check catches silent truncation before it quietly degrades every embedding for oversized chunks.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Look up the MTEB retrieval leaderboard and pick two candidate embedding models for a customer support RAG system, comparing their retrieval score, dimensionality, and max input length.",
                            "difficulty": "medium",
                            "hint": "https://huggingface.co/spaces/mteb/leaderboard filters specifically by retrieval task.",
                        },
                        {
                            "prompt": "Explain why swapping from a 1536-dimension model to a different 1536-dimension model still requires a full re-index, even though the vector shape is unchanged.",
                            "difficulty": "easy",
                            "hint": "Dimensionality matching doesn't mean the two models place similar meanings at similar coordinates.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "MTEB: Massive Text Embedding Benchmark leaderboard",
                            "url": "https://huggingface.co/spaces/mteb/leaderboard",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.7}, {"slug": "embeddings", "weight": 0.8}],
                },
                {
                    "slug": "embedding-and-indexing-chunks",
                    "title": "Embedding and Indexing Chunks",
                    "description": "Wire the chunker into an embedding step and store results in a FAISS or Chroma-style vector index.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Batch-embed chunks produced by the chunking pipeline",
                        "Store vectors alongside chunk text and metadata in a vector index",
                        "Persist an index so it survives process restarts",
                        "Verify indexing correctness with a smoke-test query",
                    ],
                    "content_markdown": """
## Why this matters

This lesson closes the loop on the offline phase of the pipeline: chunks from the Chunking
module become vectors, and vectors land in a searchable index, ready for the Retrieval module
next.

## Batch embedding chunks

```python
def embed_chunks(chunks: list, batch_size: int = 100) -> list[list[float]]:
    vectors = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        response = embed_texts([c.text for c in batch])
        vectors.extend(response)
    return vectors
```

Reusing the batching pattern from ingestion keeps this consistent with how you'd embed
anything else in the pipeline, and avoids one HTTP round-trip per chunk.

## Indexing with FAISS

```python
import faiss
import numpy as np

def build_faiss_index(chunks: list, vectors: list[list[float]]):
    dim = len(vectors[0])
    index = faiss.IndexFlatIP(dim)  # inner product; normalize vectors for cosine behavior
    matrix = np.array(vectors, dtype="float32")
    faiss.normalize_L2(matrix)
    index.add(matrix)
    id_map = {i: chunks[i] for i in range(len(chunks))}
    return index, id_map

index, id_map = build_faiss_index(chunks, vectors)
faiss.write_index(index, "rag_index.faiss")
```

FAISS is fast but stores only vectors — the `id_map` dictionary (or a small database) is your
responsibility to persist separately so you can turn a returned vector index back into the
actual chunk text and metadata.

## Indexing with Chroma

```python
import chromadb

client = chromadb.PersistentClient(path="./chroma_store")
collection = client.get_or_create_collection("rag_chunks", metadata={"hnsw:space": "cosine"})

collection.add(
    ids=[c.id for c in chunks],
    embeddings=vectors,
    documents=[c.text for c in chunks],
    metadatas=[c.metadata for c in chunks],
)
```

Chroma handles persistence and metadata storage for you, which is why many teams prototype with
Chroma before considering whether they need FAISS's raw speed plus custom infrastructure, or a
managed service for larger scale.

## Persisting so the index survives a restart

```python
# FAISS: write index + id_map separately
faiss.write_index(index, "rag_index.faiss")
import pickle
with open("id_map.pkl", "wb") as f:
    pickle.dump(id_map, f)

# Chroma: PersistentClient already writes to disk automatically on every .add() call
```

## Smoke-testing the index

Before trusting an index in a pipeline, run one known query and eyeball the result — this
catches the majority of indexing bugs (wrong vectors, misaligned metadata, forgotten
normalization) in seconds.

```python
def smoke_test(collection, query: str, expected_keyword: str):
    query_vec = embed_texts([query])[0]
    results = collection.query(query_embeddings=[query_vec], n_results=3)
    found = any(expected_keyword.lower() in doc.lower() for doc in results["documents"][0])
    print("PASS" if found else "FAIL", "-- top result:", results["documents"][0][0][:80])

smoke_test(collection, "How long do I have to return an item?", "30 days")
```

If this smoke test fails on an index you just built, debug indexing before moving on to
Retrieval — a broken index will make every later module look like it's the one that's broken.
""",
                    "examples": [
                        {
                            "title": "End-to-end from chunks to a queryable index",
                            "code": (
                                "chunks = [c for doc in cleaned_docs for c in chunk_document(doc)]\n"
                                "vectors = embed_chunks(chunks)\n"
                                "index, id_map = build_faiss_index(chunks, vectors)\n"
                                "smoke_test_faiss(index, id_map, \"return window\", \"30 days\")"
                            ),
                            "explanation": "This is the exact sequence that turns the output of the Chunking module into a searchable structure the Retrieval module will query.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a Chroma collection from a small set of 10 chunks and confirm collection.count() returns 10 after adding them.",
                            "difficulty": "easy",
                            "hint": "collection.add() followed by collection.count() is the whole exercise.",
                        },
                        {
                            "prompt": "Write a function that re-embeds and re-indexes only chunks whose IDs are not already present in a Chroma collection, avoiding redundant embedding calls.",
                            "difficulty": "medium",
                            "hint": "collection.get(ids=[...]) tells you which IDs already exist.",
                        },
                        {
                            "prompt": "Load a persisted FAISS index and id_map from disk in a fresh Python process and run a query against it, confirming results match what you got before saving.",
                            "difficulty": "medium",
                            "hint": "faiss.read_index() and pickle.load() are the two calls you need.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "FAISS wiki: getting started",
                            "url": "https://github.com/facebookresearch/faiss/wiki/Getting-started",
                            "resource_type": "docs",
                        },
                        {
                            "title": "Chroma: usage guide",
                            "url": "https://docs.trychroma.com/docs/overview/getting-started",
                            "resource_type": "docs",
                        },
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "embeddings", "weight": 0.5}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "retrieval",
            "title": "Retrieval",
            "description": "Finding the most relevant chunks for a query, and tuning that search for real-world precision and recall.",
            "order_index": 6,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "top-k-retrieval-fundamentals",
                    "title": "Top-k Retrieval Fundamentals",
                    "description": "Understand what top-k retrieval actually returns and why k is a tuning knob, not an afterthought.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what top-k retrieval means and how k affects downstream generation",
                        "Describe the tradeoff between a small k (precision) and a large k (recall)",
                        "Identify how retrieval quality is distinct from generation quality when debugging",
                        "Connect top-k choice to context window and cost constraints",
                    ],
                    "content_markdown": """
## Why this matters

Retrieval's job is deceptively simple to describe — "find the k most similar chunks to this
query" — but the value of k shapes everything downstream: what context the LLM sees, how much
you pay per query in tokens, and whether the right answer is even present for generation to
use.

## What top-k retrieval returns

```python
query_vec = embed_texts([user_query])[0]
results = vector_db.query(vector=query_vec, top_k=5)
# results: the 5 chunks whose vectors are closest to query_vec, ranked by similarity
```

Top-k retrieval is a **recall mechanism**, not a correctness guarantee — it returns the k
closest chunks *by embedding similarity*, which is not the same as "the k chunks that actually
answer the question." A chunk can be topically similar without containing the specific fact the
user needs, and the true best-answering chunk can rank 6th if k=5.

## The k tradeoff

A small k (e.g., 3) keeps the context tight and focused, reducing the chance the LLM gets
distracted by irrelevant material — but if the right chunk didn't make the cut, generation has
no chance of answering correctly no matter how good the prompt is.

A large k (e.g., 20) improves the odds the right chunk is included, at the cost of a longer,
noisier context that costs more tokens and can dilute the LLM's attention across more
material, sometimes *decreasing* answer quality even when the right chunk is technically
present.

```python
# This is exactly why reranking (a later module) exists: retrieve a larger k
# cheaply and broadly, then use a more precise (but slower) model to cut
# back down to a small, high-confidence set before generation.
results = vector_db.query(vector=query_vec, top_k=20)  # cast a wide net
top_chunks = reranker.rerank(user_query, results, top_k=5)  # then narrow precisely
```

## Retrieval quality vs. generation quality

When a RAG answer is wrong, the bug could be in retrieval (the right chunk was never found) or
in generation (the right chunk was found but the LLM ignored or misread it). These require
completely different fixes, so always check retrieval in isolation first: print the top-k
chunks for a failing query and manually verify whether the answer is actually present *before*
touching your prompt or generation settings.

```python
def debug_retrieval(query: str, top_k: int = 10):
    results = vector_db.query(vector=embed_texts([query])[0], top_k=top_k)
    for r in results:
        print(f"{r.score:.3f}  {r.metadata['source']}  {r.text[:100]}")
```

## k and the context window budget

Every retrieved chunk consumes tokens in the prompt. If your chunk size is 800 characters
(~200 tokens) and you retrieve top_k=20, you're spending roughly 4,000 tokens on context alone
— fine for a large context window, wasteful or even truncation-inducing for a small one. Tune k
jointly with chunk size and your model's context budget, not in isolation.

## A practical starting point

Retrieve a moderately generous top_k (10-20) before reranking, then narrow to 3-5 chunks for
actual generation. This "retrieve broad, rerank narrow" pattern balances recall and precision
better than trying to get top_k exactly right in a single retrieval step.
""",
                    "examples": [
                        {
                            "title": "The right chunk ranked just outside top-k",
                            "code": (
                                "results = vector_db.query(vector=query_vec, top_k=3)\n"
                                "# Suppose the chunk that actually answers the question ranked 4th\n"
                                "# by similarity -- it's simply absent from these 3 results, and no\n"
                                "# prompt engineering on the generation side can recover it."
                            ),
                            "explanation": "This illustrates why debugging should always start by inspecting raw retrieval results, not the final generated answer.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a customer-facing chatbot with a 16K token context window and 200-token chunks, calculate a reasonable upper bound on top_k before context construction (system prompt, conversation history, query) starts crowding out room for an answer.",
                            "difficulty": "medium",
                            "hint": "Budget tokens for system prompt + history + generation headroom first, then see what's left for retrieved context.",
                        },
                        {
                            "prompt": "Write the debug_retrieval function from this lesson and run it against 3 queries you expect to succeed and 1 you expect to fail. Report what you observe.",
                            "difficulty": "medium",
                            "hint": "A 'failing' query is a good one to pick if you know the true source document should not exist in your corpus.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Pinecone: vector search and retrieval fundamentals",
                            "url": "https://www.pinecone.io/learn/vector-search-basics/",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}],
                },
                {
                    "slug": "implementing-retrieval-with-faiss",
                    "title": "Implementing Retrieval with FAISS and Chroma",
                    "description": "Write a retrieval function that wraps FAISS and Chroma behind a common interface for the rest of the pipeline.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a retrieval function against a FAISS index and a Chroma collection",
                        "Design a common retrieval interface that hides the underlying vector store",
                        "Return retrieval results with similarity scores and full metadata",
                        "Measure and log retrieval latency for later performance tuning",
                    ],
                    "content_markdown": """
## Why this matters

Every other module in this course calls "retrieve the top-k chunks for this query" without
caring which vector database is underneath. Building that abstraction once means you can swap
FAISS for Chroma, or Chroma for a managed service, without touching context construction,
generation, or citations code.

## A common retrieval result shape

```python
from dataclasses import dataclass

@dataclass
class RetrievalResult:
    chunk_id: str
    text: str
    score: float
    metadata: dict
```

## Retrieval against FAISS

```python
import faiss
import numpy as np

def retrieve_faiss(query: str, index, id_map: dict, top_k: int = 10) -> list[RetrievalResult]:
    query_vec = np.array([embed_texts([query])[0]], dtype="float32")
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, top_k)
    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = id_map[idx]
        results.append(RetrievalResult(chunk_id=chunk.id, text=chunk.text, score=float(score), metadata=chunk.metadata))
    return results
```

FAISS returns raw indices, so you always need the `id_map` you saved during indexing to
translate an integer position back into an actual chunk.

## Retrieval against Chroma

```python
def retrieve_chroma(query: str, collection, top_k: int = 10) -> list[RetrievalResult]:
    query_vec = embed_texts([query])[0]
    raw = collection.query(query_embeddings=[query_vec], n_results=top_k)
    results = []
    for text, meta, distance, chunk_id in zip(
        raw["documents"][0], raw["metadatas"][0], raw["distances"][0], raw["ids"][0]
    ):
        similarity = 1 - distance  # Chroma returns cosine distance, not similarity
        results.append(RetrievalResult(chunk_id=chunk_id, text=text, score=similarity, metadata=meta))
    return results
```

Note the `1 - distance` conversion — Chroma's default cosine *distance* metric is the inverse of
similarity, and mixing up distance and similarity is one of the most common bugs in retrieval
code (higher distance means less similar, the opposite of a similarity score).

## Unifying behind one interface

```python
class Retriever:
    def __init__(self, backend: str, **kwargs):
        self.backend = backend
        self.kwargs = kwargs

    def retrieve(self, query: str, top_k: int = 10) -> list[RetrievalResult]:
        if self.backend == "faiss":
            return retrieve_faiss(query, top_k=top_k, **self.kwargs)
        elif self.backend == "chroma":
            return retrieve_chroma(query, top_k=top_k, **self.kwargs)
        raise ValueError(f"Unknown backend: {self.backend}")
```

Everything built in later modules — context construction, citations, evaluation — should call
`retriever.retrieve(query, top_k)` and never touch FAISS or Chroma internals directly.

## Measuring latency

```python
import time

def retrieve_with_timing(retriever: Retriever, query: str, top_k: int = 10):
    start = time.perf_counter()
    results = retriever.retrieve(query, top_k)
    elapsed_ms = (time.perf_counter() - start) * 1000
    print(f"Retrieval took {elapsed_ms:.1f}ms for top_k={top_k}")
    return results
```

Logging retrieval latency early means that when your system feels slow later, you can tell in
seconds whether retrieval, reranking, or generation is the bottleneck — instead of guessing.
""",
                    "examples": [
                        {
                            "title": "Swapping backends without touching calling code",
                            "code": (
                                "retriever = Retriever(backend=\"chroma\", collection=collection)\n"
                                "results = retriever.retrieve(\"What is the refund window?\", top_k=5)\n"
                                "# Later: retriever = Retriever(backend=\"faiss\", index=index, id_map=id_map)\n"
                                "# Calling code above is completely unchanged"
                            ),
                            "explanation": "This is the entire point of the Retriever abstraction: the rest of the pipeline never needs to know which vector store is running underneath.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a Pinecone-style backend branch to the Retriever class, assuming a pinecone_index.query(vector=..., top_k=...) method that returns matches with .id, .score, and .metadata.",
                            "difficulty": "medium",
                            "hint": "Follow the same pattern as retrieve_faiss and retrieve_chroma -- normalize the response into RetrievalResult objects.",
                        },
                        {
                            "prompt": "Write a test that confirms retrieve_chroma correctly converts Chroma's cosine distance into a similarity score using a known distance value.",
                            "difficulty": "easy",
                            "hint": "assert result.score == 1 - known_distance.",
                        },
                        {
                            "prompt": "Instrument the Retriever class to log the p50 and p95 retrieval latency across 50 sample queries.",
                            "difficulty": "hard",
                            "hint": "Collect elapsed times into a list, then use statistics.quantiles() or sort-and-index for p50/p95.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "FAISS: searching wiki page",
                            "url": "https://github.com/facebookresearch/faiss/wiki/Getting-started#searching",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
                {
                    "slug": "tuning-retrieval-for-recall-vs-precision",
                    "title": "Tuning Retrieval for Recall vs. Precision",
                    "description": "Diagnose and fix common retrieval failure patterns using recall and precision as concrete, measurable targets.",
                    "lesson_type": "reading",
                    "order_index": 3,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define recall@k and precision@k in the context of chunk retrieval",
                        "Diagnose whether a retrieval failure is a recall problem or a precision problem",
                        "Apply query expansion as one technique for improving retrieval recall",
                        "Recognize the role of similarity thresholds in filtering out irrelevant matches",
                    ],
                    "content_markdown": """
## Why this matters

"Retrieval isn't working well" is not an actionable bug report. Recall and precision turn that
vague feeling into two distinct, measurable problems that call for different fixes — confusing
the two leads to tuning the wrong knob.

## Recall@k and precision@k, concretely

**Recall@k** asks: of all the chunks that are actually relevant to this query, what fraction
did we retrieve in our top k? Low recall means the right chunk exists in your corpus but
retrieval never found it.

**Precision@k** asks: of the k chunks we retrieved, what fraction are actually relevant? Low
precision means retrieval is returning a lot of noise alongside (or instead of) the right
answer.

```python
def recall_at_k(retrieved_ids: set, relevant_ids: set) -> float:
    if not relevant_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(relevant_ids)

def precision_at_k(retrieved_ids: set, relevant_ids: set) -> float:
    if not retrieved_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(retrieved_ids)
```

## Diagnosing which one you have

If you manually search your corpus and confirm the right chunk exists, then run your retriever
and it's absent from the top-k, that's a **recall** problem — increase k, improve chunking, or
reconsider your embedding model. If the right chunk *is* present but buried among several
irrelevant ones, that's a **precision** problem — this is exactly what reranking (a later
module) is built to fix.

## Query expansion for recall

A single embedding of the user's literal query sometimes misses relevant chunks phrased very
differently. Query expansion generates several phrasings of the same question and merges their
retrieval results.

```python
def expand_query(query: str, llm) -> list[str]:
    prompt = f"Generate 3 alternative phrasings of this question, one per line, no numbering:\\n{query}"
    response = llm.generate(prompt)
    return [query] + [line.strip() for line in response.split("\\n") if line.strip()]

def retrieve_with_expansion(query: str, retriever, llm, top_k: int = 10) -> list:
    variants = expand_query(query, llm)
    seen_ids, merged = set(), []
    for variant in variants:
        for result in retriever.retrieve(variant, top_k=top_k):
            if result.chunk_id not in seen_ids:
                seen_ids.add(result.chunk_id)
                merged.append(result)
    return sorted(merged, key=lambda r: r.score, reverse=True)[:top_k]
```

This trades extra LLM and embedding calls for meaningfully better recall on queries phrased
unusually compared to how the source documents are written.

## Similarity thresholds for precision

Rather than always returning exactly k results, filter out anything below a minimum similarity
score — this prevents genuinely irrelevant chunks from ever reaching generation just because
they happened to be the "least bad" among the top-k.

```python
def retrieve_above_threshold(query: str, retriever, top_k: int = 10, min_score: float = 0.7) -> list:
    results = retriever.retrieve(query, top_k=top_k)
    return [r for r in results if r.score >= min_score]
```

A query with no genuinely relevant chunks in the corpus should sometimes return an empty list —
and your generation prompt should be written to handle that gracefully by saying "I don't have
information about that" rather than generating from irrelevant context.

## The tuning loop

Retrieval tuning is iterative: build a small evaluation set, measure recall/precision, form a
hypothesis about what's wrong (chunking, embedding model, k, thresholds), change one thing,
re-measure. This loop is formalized fully in the RAG Evaluation module later in this course.
""",
                    "examples": [
                        {
                            "title": "Diagnosing a specific retrieval failure",
                            "code": (
                                "query = \"Can I return a product after it's been opened?\"\n"
                                "results = retriever.retrieve(query, top_k=5)\n"
                                "# Manual check: the true answer lives in chunk 'return-policy-chunk-2'\n"
                                "found = any(r.chunk_id == \"return-policy-chunk-2\" for r in results)\n"
                                "print(\"Recall issue\" if not found else \"Chunk present -- check precision/generation instead\")"
                            ),
                            "explanation": "A single manual check like this, run against a known query, is often enough to tell you which half of the pipeline to investigate next.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a labeled set of 10 (query, relevant_chunk_ids) pairs, compute average recall@5 and precision@5 for your retriever and report both numbers.",
                            "difficulty": "medium",
                            "hint": "Loop over the 10 pairs, compute each metric per query, then average.",
                        },
                        {
                            "prompt": "Implement retrieve_with_expansion and compare its recall@5 against plain retrieval on 5 queries phrased unusually compared to your source documents.",
                            "difficulty": "hard",
                            "hint": "Deliberately pick queries that use different vocabulary than the documents to see expansion's benefit clearly.",
                        },
                        {
                            "prompt": "Explain why setting min_score too high can silently turn a recall problem into what looks like a 'no results' bug, and how you'd distinguish the two.",
                            "difficulty": "medium",
                            "hint": "Consider what happens if a genuinely relevant chunk scores just below your threshold.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Weaviate: hybrid search and retrieval evaluation blog",
                            "url": "https://weaviate.io/blog/retrieval-evaluation-metrics",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}, {"slug": "rag", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "context-construction",
            "title": "Context Construction",
            "description": "Assembling retrieved chunks into a prompt that fits the token budget and helps the model use them correctly.",
            "order_index": 7,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "assembling-context-windows",
                    "title": "Assembling Context Windows",
                    "description": "Decide how to order, format, and budget retrieved chunks before they reach the prompt.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why chunk ordering within a prompt can affect generation quality",
                        "Budget tokens across system prompt, context, history, and generation headroom",
                        "Format retrieved chunks so sources stay distinguishable to the model",
                        "Handle the case where retrieved context exceeds the available token budget",
                    ],
                    "content_markdown": """
## Why this matters

Retrieval and reranking hand you a ranked list of chunks; context construction turns that list
into the actual text the LLM reads. Getting this step wrong — bad ordering, no source
separation, blown token budgets — can waste a perfectly good retrieval result.

## Chunk ordering matters

Research and practical experience both show LLMs pay more attention to information near the
start and end of a long context than what's buried in the middle — an effect often called
"lost in the middle." A common mitigation is to place your highest-relevance chunks either
first or last, not in the middle of a long context block.

```python
def order_for_context(results: list) -> list:
    # Highest-scored chunk first, keeps most relevant content
    # at the position models attend to most reliably
    return sorted(results, key=lambda r: r.score, reverse=True)
```

## Budgeting tokens across the whole prompt

A prompt isn't just retrieved context — it also includes a system prompt, possibly
conversation history, and the user's question, all competing for the same context window.

```python
def build_token_budget(total_context_window: int, reserved_for_generation: int = 1000) -> dict:
    system_prompt_tokens = 300
    history_tokens = 800
    available_for_retrieval = total_context_window - reserved_for_generation - system_prompt_tokens - history_tokens
    return {"retrieval_budget": max(available_for_retrieval, 0)}

budget = build_token_budget(total_context_window=16000)
print(budget["retrieval_budget"])  # tokens left over for retrieved chunks
```

Always reserve headroom for the model's own generated output — a prompt that fills the entire
context window leaves no room for the answer itself.

## Formatting chunks so sources stay distinguishable

```python
def format_context(results: list) -> str:
    blocks = []
    for i, r in enumerate(results, start=1):
        blocks.append(f"[Source {i}: {r.metadata.get('source', 'unknown')}]\\n{r.text}")
    return "\\n\\n".join(blocks)

context_text = format_context(reranked_results)
```

Labeling each chunk with a source identifier isn't just for citations later — it also helps the
model distinguish where one piece of retrieved evidence ends and the next begins, reducing the
chance it blends two unrelated chunks into one incorrect claim.

## Handling context that doesn't fit

```python
import tiktoken

def fit_to_budget(results: list, max_tokens: int, encoding_name: str = "cl100k_base") -> list:
    encoding = tiktoken.get_encoding(encoding_name)
    kept, used = [], 0
    for r in results:
        cost = len(encoding.encode(r.text))
        if used + cost > max_tokens:
            break
        kept.append(r)
        used += cost
    return kept
```

Rather than truncating mid-chunk (which can cut off the exact sentence that answers the
question), drop whole chunks from the end of the ranked list once the budget is exhausted —
this is another reason reranking to a small, high-confidence set before context construction
matters so much.

## Putting it together

```python
def build_context(results: list, max_tokens: int) -> str:
    fitted = fit_to_budget(order_for_context(results), max_tokens)
    return format_context(fitted)
```

This function is the direct bridge between the Retrieval/Reranking modules and the Generation
module next — everything the LLM will see about your documents flows through this one call.
""",
                    "examples": [
                        {
                            "title": "Context construction end to end",
                            "code": (
                                "results = retriever.retrieve(query, top_k=20)\n"
                                "reranked = reranker.rerank(query, results, top_k=5)\n"
                                "context = build_context(reranked, max_tokens=budget[\"retrieval_budget\"])\n"
                                "print(context[:200])"
                            ),
                            "explanation": "Notice reranking happens before context construction -- narrowing to a small, high-confidence set makes the token budgeting step in this lesson much simpler.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Given 8 retrieved chunks averaging 150 tokens each and a retrieval budget of 600 tokens, trace through fit_to_budget and determine which chunks survive.",
                            "difficulty": "easy",
                            "hint": "600 / 150 = 4, so roughly the top 4 chunks by the input ordering fit.",
                        },
                        {
                            "prompt": "Modify format_context to also include each chunk's similarity score in the source label, and explain one debugging scenario where this would help.",
                            "difficulty": "medium",
                            "hint": "Seeing low scores next to included chunks can reveal when context construction is including weak matches.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Lost in the Middle: How Language Models Use Long Contexts",
                            "url": "https://arxiv.org/abs/2307.03172",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}],
                },
                {
                    "slug": "prompt-templates-for-grounded-generation",
                    "title": "Prompt Templates for Grounded Generation",
                    "description": "Design a reusable prompt template that instructs the model to answer only from provided context.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Write a prompt template that clearly separates instructions, context, and the user question",
                        "Instruct the model to decline answering when context is insufficient",
                        "Parameterize the template for reuse across different RAG use cases",
                        "Recognize prompt patterns that reduce ungrounded generation",
                    ],
                    "content_markdown": """
## Why this matters

The same retrieved context can produce a tightly grounded answer or a hallucinated one
depending entirely on how the prompt around it is written. This lesson builds the template that
turns "here's some text and a question" into reliable, grounded generation.

## The core template

```python
RAG_PROMPT_TEMPLATE = (
    "You are a helpful assistant that answers questions using ONLY the provided context.\\n"
    "If the context does not contain enough information to answer, say so explicitly instead of guessing.\\n"
    "Always cite which source number supports each claim you make.\\n\\n"
    "Context:\\n{context}\\n\\n"
    "Question: {question}\\n\\n"
    "Answer:"
)

def build_prompt(question: str, context: str) -> str:
    return RAG_PROMPT_TEMPLATE.format(context=context, question=question)
```

Three instructions do most of the work here: restrict answers to the given context, explicitly
permit "I don't know," and require citations. Each one independently reduces the chance of a
confident, ungrounded answer.

## Why "say so explicitly" matters more than it looks

Without an explicit permission to decline, models tend to answer *something* even from weak or
irrelevant context, because refusing to answer is a less common pattern in their training data
than answering. Stating the decline option directly and clearly in the prompt measurably
reduces this behavior.

```python
context_text = "Source 1: Our office hours are 9am-5pm Monday through Friday."
question = "What is your refund policy?"
prompt = build_prompt(question, context_text)
# A well-grounded model should respond with something like:
# "The provided context does not contain information about the refund policy."
```

## Parameterizing for different use cases

```python
def build_prompt(
    question: str,
    context: str,
    tone: str = "helpful and concise",
    allow_partial_answers: bool = True,
) -> str:
    partial_instruction = (
        "If only part of the question can be answered from the context, answer that part and note what's missing."
        if allow_partial_answers
        else "Only answer if the context fully addresses the question."
    )
    return (
        f"You are a {tone} assistant that answers questions using ONLY the provided context.\\n"
        f"{partial_instruction}\\n"
        "Always cite which source number supports each claim you make.\\n\\n"
        f"Context:\\n{context}\\n\\n"
        f"Question: {question}\\n\\n"
        "Answer:"
    )
```

Different products need different failure behavior — a legal research tool probably wants
`allow_partial_answers=False` to avoid ever combining a real fact with a guessed one, while a
general FAQ bot benefits from partial answers plus a note about what's missing.

## Patterns that reduce ungrounded generation

- Put instructions *before* the context, and the question *after* it — models tend to treat
  text closer to the question as most relevant, so keep grounding instructions from getting
  visually buried.
- Use structural markers ("Context:", "Question:") so the model reliably distinguishes
  instructions from data, reducing the chance retrieved content is misread as an instruction
  (a mild form of prompt injection risk worth taking seriously).
- Explicitly forbid using outside knowledge: "even if you know the answer from general
  knowledge, only use the provided context" closes a subtle loophole where models blend
  parametric knowledge with retrieved context without telling you.

## Testing the template

Run known "should decline" and "should answer" cases through your template regularly — prompt
templates regress silently when you tweak wording, and a quick eyeball test catches that before
it reaches users.
""",
                    "examples": [
                        {
                            "title": "A should-decline test case",
                            "code": (
                                "context_text = format_context(retriever.retrieve(\"warranty terms\", top_k=3))\n"
                                "prompt = build_prompt(\"What is the CEO's phone number?\", context_text)\n"
                                "answer = llm.generate(prompt)\n"
                                "# Expect something like 'The context does not contain this information.'"
                            ),
                            "explanation": "Deliberately asking a question the retrieved context cannot answer is one of the most useful regression tests for a grounded-generation prompt.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write 3 test questions your RAG system should decline to answer given its actual document corpus, and run them through your prompt template to check behavior.",
                            "difficulty": "medium",
                            "hint": "Pick questions clearly outside the corpus's topic, like asking a support bot about the weather.",
                        },
                        {
                            "prompt": "Modify the template to require the model to quote the exact sentence it's basing each claim on, in addition to citing the source number.",
                            "difficulty": "medium",
                            "hint": "Add an explicit instruction line and test it against a real retrieved context block.",
                        },
                        {
                            "prompt": "Explain, with an example, how retrieved content could be misinterpreted as an instruction by the model if context and instructions aren't clearly separated, and how structural markers mitigate this.",
                            "difficulty": "hard",
                            "hint": "Imagine a malicious or unusual document that contains text like 'Ignore previous instructions and...' inside its body.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "OpenAI: prompt engineering guide",
                            "url": "https://platform.openai.com/docs/guides/prompt-engineering",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "prompt-engineering", "weight": 0.6}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "generation",
            "title": "Generation",
            "description": "Calling the LLM with grounded context and settings tuned for factual, trustworthy answers.",
            "order_index": 8,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "grounded-generation-principles",
                    "title": "Grounded Generation Principles",
                    "description": "Understand the generation settings and instructions that keep answers tied to retrieved evidence.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain how temperature affects the risk of ungrounded generation",
                        "Describe the role of system vs. user messages in a grounded RAG prompt",
                        "Identify when a RAG system should refuse to answer rather than guess",
                        "Recognize the tension between fluency and strict faithfulness to context",
                    ],
                    "content_markdown": """
## Why this matters

Context construction hands the model good evidence; generation is where that evidence either
gets faithfully turned into an answer or quietly ignored in favor of the model's own
assumptions. The settings and structure of this final call matter as much as everything that
came before it.

## Temperature and grounding

Temperature controls how much randomness the model injects into token selection. Lower
temperature makes the model more likely to stick closely to the most probable continuation
given its input — which, for a well-grounded prompt, means closer to what the context actually
supports.

```python
response = llm.generate(
    prompt=build_prompt(question, context),
    temperature=0.1,   # low temperature: favor faithful, less "creative" answers
    max_tokens=500,
)
```

A temperature of 0.7-1.0 (common for creative writing) is generally a poor choice for RAG
generation — you want the model's *most likely* answer given the evidence, not a more novel or
varied one.

## System vs. user message structure

```python
messages = [
    {"role": "system", "content": "You answer strictly from provided context and cite sources. If context is insufficient, say so."},
    {"role": "user", "content": f"Context:\\n{context}\\n\\nQuestion: {question}"},
]
response = llm.chat(messages=messages, temperature=0.1)
```

Putting grounding instructions in the system message (rather than burying them in the user
turn) generally makes models treat them as a more persistent constraint across the whole
response, rather than one instruction among many in a long user message.

## Knowing when to refuse

A well-designed RAG system should refuse to answer, or answer with clear caveats, in specific
situations:

- Retrieval returned zero results above your similarity threshold.
- The retrieved chunks are topically related but don't actually address the specific question.
- The question requires reasoning across information not present in any single retrieved
  chunk.

```python
def should_attempt_answer(results: list, min_score: float = 0.7) -> bool:
    return any(r.score >= min_score for r in results)

if not should_attempt_answer(reranked):
    answer = "I don't have enough information in my knowledge base to answer that confidently."
else:
    answer = llm.generate(build_prompt(question, format_context(reranked)))
```

Building this check in code, rather than relying entirely on the model to self-police via
prompt instructions, gives you a deterministic backstop against low-confidence generation.

## The fluency vs. faithfulness tension

Models are trained to produce fluent, confident-sounding prose — which is often at odds with
faithfully representing uncertain or incomplete evidence. A faithful answer to weak context
might be "the context suggests X, but doesn't confirm it directly," which is less satisfying to
read than a confident, fully-formed (and possibly wrong) claim. Explicitly rewarding hedged,
honest answers in your prompt instructions — and evaluating for this, a topic in the RAG
Evaluation module — is necessary because fluency alone will not get you there.

## A simple mental model

Think of generation as translation, not composition: the model's job is to translate the
retrieved evidence into a well-phrased answer, not to compose an answer from its own general
knowledge with the evidence as loose inspiration. Every prompt and setting choice in this
lesson pushes the model toward the former.
""",
                    "examples": [
                        {
                            "title": "Same context, different temperature",
                            "code": (
                                "# At temperature=0.1, repeated calls with the same context tend to\n"
                                "# produce nearly identical, tightly-grounded answers.\n"
                                "# At temperature=0.9, repeated calls may vary in phrasing and\n"
                                "# occasionally introduce claims not directly supported by the context."
                            ),
                            "explanation": "This is a useful experiment to actually run: generate the same RAG prompt 5 times at each temperature and compare consistency and faithfulness by eye.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Run the same grounded prompt through an LLM 3 times at temperature=0.1 and 3 times at temperature=0.9, and compare answer consistency across the two settings.",
                            "difficulty": "medium",
                            "hint": "Keep the prompt and context fixed, and only change temperature between calls.",
                        },
                        {
                            "prompt": "Implement should_attempt_answer and wire it into a full retrieve-rerank-generate pipeline so low-confidence queries short-circuit before an LLM call.",
                            "difficulty": "medium",
                            "hint": "This also saves cost -- an LLM call you skip is a call you don't pay for.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "OpenAI API reference: chat completions parameters",
                            "url": "https://platform.openai.com/docs/api-reference/chat/create",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "prompt-engineering", "weight": 0.4}],
                },
                {
                    "slug": "building-the-generation-step",
                    "title": "Building the Generation Step",
                    "description": "Wire retrieval, context construction, and the LLM call into one callable RAG answer function.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a complete answer function chaining retrieval through generation",
                        "Handle empty or low-confidence retrieval results gracefully",
                        "Return structured output including the answer and the chunks used",
                        "Add basic error handling for LLM call failures",
                    ],
                    "content_markdown": """
## Why this matters

This lesson assembles everything from Retrieval through Generation into one function you could
actually call from an API endpoint — the first time in this course the pipeline becomes
something a real application could use end to end.

## The RAG answer function

```python
from dataclasses import dataclass

@dataclass
class RagAnswer:
    answer: str
    sources: list
    confident: bool

def answer_question(question: str, retriever, reranker, llm, top_k: int = 20, rerank_k: int = 5) -> RagAnswer:
    candidates = retriever.retrieve(question, top_k=top_k)
    if not candidates:
        return RagAnswer(answer="I don't have any relevant information to answer that.", sources=[], confident=False)

    reranked = reranker.rerank(question, candidates, top_k=rerank_k)
    if not should_attempt_answer(reranked):
        return RagAnswer(answer="I don't have enough confident information to answer that.", sources=reranked, confident=False)

    context = build_context(reranked, max_tokens=3000)
    prompt = build_prompt(question, context)

    try:
        answer_text = llm.generate(prompt, temperature=0.1, max_tokens=500)
    except Exception as exc:
        return RagAnswer(answer=f"Sorry, something went wrong generating an answer: {exc}", sources=reranked, confident=False)

    return RagAnswer(answer=answer_text, sources=reranked, confident=True)
```

Notice the function never raises an unhandled exception up to the caller — every failure path
(no candidates, low confidence, LLM error) returns a structured `RagAnswer` the calling code can
render consistently.

## Why sources travel with the answer

Returning `sources` alongside `answer` isn't optional polish — it's the raw material the
Citations module will format into inline references, and it's what lets a UI show "based on
these 3 documents" so users can verify the answer themselves rather than trusting it blindly.

## Testing the full chain

```python
def test_answer_question_declines_when_no_context():
    fake_retriever = FakeRetriever(results=[])
    result = answer_question("Unrelated question", fake_retriever, reranker, llm)
    assert result.confident is False
    assert "don't have" in result.answer.lower()

def test_answer_question_returns_sources_on_success():
    result = answer_question("What is the refund window?", retriever, reranker, llm)
    assert result.confident is True
    assert len(result.sources) > 0
```

Using a `FakeRetriever` that always returns an empty list lets you test the decline path
without needing a real vector database or LLM call — a pattern worth reusing throughout this
course whenever you test pipeline logic rather than the underlying models.

## Wrapping it for an API

```python
def rag_endpoint(request_body: dict) -> dict:
    result = answer_question(request_body["question"], retriever, reranker, llm)
    return {
        "answer": result.answer,
        "confident": result.confident,
        "sources": [{"source": s.metadata.get("source"), "score": s.score} for s in result.sources],
    }
```

This is close to what you'd actually deploy behind a `/ask` endpoint — the Production AI course
later in this program covers hardening this further with caching, rate limiting, and
monitoring.
""",
                    "examples": [
                        {
                            "title": "A full call from question to structured answer",
                            "code": (
                                "result = answer_question(\"How long is the return window?\", retriever, reranker, llm)\n"
                                "print(result.answer)\n"
                                "print(result.confident)\n"
                                "for s in result.sources:\n"
                                "    print(\"-\", s.metadata.get(\"source\"), round(s.score, 3))"
                            ),
                            "explanation": "This single call now represents the entire pipeline built across Modules 2 through 8 of this course.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write FakeRetriever and FakeReranker test doubles and use them to test answer_question's low-confidence path without any real API calls.",
                            "difficulty": "medium",
                            "hint": "A FakeRetriever just needs a retrieve(query, top_k) method that returns a hardcoded list.",
                        },
                        {
                            "prompt": "Add a max_retries parameter to answer_question that retries the LLM call up to that many times on failure before returning the error RagAnswer.",
                            "difficulty": "medium",
                            "hint": "Wrap the try/except in a loop and only return the failure case after exhausting retries.",
                        },
                        {
                            "prompt": "Extend RagAnswer with a latency_ms field that captures total time from the start of retrieval to the end of generation.",
                            "difficulty": "easy",
                            "hint": "Use time.perf_counter() at the start and end of answer_question.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain: build a retrieval-augmented generation app tutorial",
                            "url": "https://python.langchain.com/docs/tutorials/rag/",
                            "resource_type": "tutorial",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "python", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "citations",
            "title": "Citations",
            "description": "Making RAG answers verifiable by tracing every claim back to the source chunk it came from.",
            "order_index": 9,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-citations-matter-in-rag",
                    "title": "Why Citations Matter in RAG",
                    "description": "Understand what citations actually provide beyond making answers look credible.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why citations are a trust and verification mechanism, not decoration",
                        "Distinguish document-level citations from precise inline citations",
                        "Identify the risk of a model fabricating a citation for a real-looking but wrong source",
                        "Describe how citations support debugging retrieval and generation failures",
                    ],
                    "content_markdown": """
## Why this matters

A RAG answer without citations asks the user to trust it blindly — exactly the problem RAG was
built to avoid in the first place. Citations turn "trust me" into "here's exactly where this
came from, go check it yourself," which matters enormously for high-stakes domains like legal,
medical, or financial question answering.

## Document-level vs. precise citations

**Document-level citations** point to the source document ("according to the Employee
Handbook") but not the specific passage — easy to implement, but still requires the user to
search the whole document to verify a claim.

**Precise citations** point to the exact chunk or even sentence a claim came from — much more
useful for verification, and directly enabled by the metadata you've been carrying through
every stage of this pipeline since the Document Ingestion module.

```python
# Document-level
"According to the Employee Handbook, remote work requires manager approval."

# Precise (chunk-level)
"Remote work requires manager approval [Source 1, employee-handbook.pdf, section 4.2]."
```

## The fabricated citation risk

A subtle and dangerous failure mode: a model can generate a citation that *looks* correct —
"[Source 2]" — while the claim it's attached to isn't actually supported by that source's
content. This happens because generating plausible-looking citation syntax is easy for an LLM;
generating a citation that's *actually accurate* requires the model to faithfully track which
claim came from which piece of context, which is not guaranteed just because you asked for it
in the prompt.

```python
def verify_citation(claim: str, cited_source_text: str, nli_model) -> bool:
    # A natural language inference model checks whether cited_source_text
    # actually entails (supports) the claim, rather than trusting the
    # citation number blindly
    result = nli_model.predict(premise=cited_source_text, hypothesis=claim)
    return result.label == "entailment"
```

Programmatic citation verification, covered hands-on in the next lesson and revisited in RAG
Evaluation, is how production systems catch this failure mode instead of trusting the model's
self-reported citations at face value.

## Citations as a debugging tool

When a user reports "this answer is wrong," citations let you immediately check: was the wrong
information actually in the cited source (a content problem), was the wrong source retrieved in
the first place (a retrieval problem), or did the model misread a correct source (a generation
problem)? Without citations, you're stuck reproducing the whole pipeline from scratch to
diagnose a single bad answer.

## Citations and user trust calibration

Research on human-AI trust shows that citations shift how much people verify AI-generated
content versus simply accepting it. This is a double-edged sword: citations that look authoritative
but are wrong can *increase* misplaced trust, which is exactly why verifying citations
programmatically, not just displaying them, matters as much as generating them in the first
place.
""",
                    "examples": [
                        {
                            "title": "A citation that fails verification",
                            "code": (
                                "claim = \"Refunds are processed within 24 hours.\"\n"
                                "cited_text = \"Our office is open Monday through Friday, 9am to 5pm.\"\n"
                                "# verify_citation(claim, cited_text, nli_model) -> False\n"
                                "# The cited source has nothing to do with refund timing --\n"
                                "# this is exactly the fabricated-citation pattern to catch."
                            ),
                            "explanation": "Catching this kind of mismatch programmatically before showing an answer to a user is far more reliable than hoping the model never makes this mistake.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a domain of your choice (legal, medical, internal support), explain why document-level citations would or would not be sufficient, versus needing precise chunk-level citations.",
                            "difficulty": "easy",
                            "hint": "Consider how costly it would be for a user to manually search an entire document to verify one claim.",
                        },
                        {
                            "prompt": "Describe a debugging workflow that uses citations to distinguish a retrieval failure from a generation failure, using a concrete example question.",
                            "difficulty": "medium",
                            "hint": "Walk through: was the cited source even relevant to begin with, versus was it relevant but misread?",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: building effective citations in RAG systems",
                            "url": "https://www.anthropic.com/news/introducing-citations-api",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}],
                },
                {
                    "slug": "implementing-inline-citations",
                    "title": "Implementing Inline Citations",
                    "description": "Track source metadata through generation and format verifiable, clickable inline citations in the final answer.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Number and label sources consistently between context construction and the prompt",
                        "Parse model output to extract and validate citation markers",
                        "Map citation markers back to full source metadata for display",
                        "Implement basic programmatic citation verification",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson made the case for citations; this one builds them. The key engineering
challenge is keeping source numbering consistent from context construction, through the LLM's
generated text, to the final rendered answer.

## Numbering sources consistently

```python
def build_context_with_labels(results: list) -> tuple[str, dict]:
    labeled_sources = {}
    blocks = []
    for i, r in enumerate(results, start=1):
        labeled_sources[i] = r
        blocks.append(f"[Source {i}]\\n{r.text}")
    return "\\n\\n".join(blocks), labeled_sources

context_text, source_map = build_context_with_labels(reranked)
```

`source_map` is the lookup table that turns "[Source 2]" in the model's generated text back
into the actual chunk, its document, and its metadata.

## Prompting for citation markers

```python
CITED_PROMPT = (
    "Answer the question using only the numbered sources below. "
    "After each claim, cite the source number in square brackets, like [1].\\n\\n"
    "{context}\\n\\nQuestion: {question}\\n\\nAnswer:"
)

prompt = CITED_PROMPT.format(context=context_text, question=question)
raw_answer = llm.generate(prompt, temperature=0.1)
```

## Parsing citation markers out of the answer

```python
import re

def extract_citations(answer_text: str, source_map: dict) -> list:
    marker_pattern = r"\\[(\\d+)\\]"
    cited_numbers = {int(n) for n in re.findall(marker_pattern, answer_text)}
    return [source_map[n] for n in cited_numbers if n in source_map]

cited_sources = extract_citations(raw_answer, source_map)
```

Filtering with `if n in source_map` guards against the model hallucinating a citation number
that was never actually in the context — for example `[7]` when only 5 sources were provided.

## Verifying citations against their claims

```python
def verify_answer_citations(answer_text: str, source_map: dict, nli_model) -> dict:
    sentences = [s.strip() for s in answer_text.split(".") if s.strip()]
    verified, flagged = [], []
    for sentence in sentences:
        numbers = [int(n) for n in re.findall(r"\\[(\\d+)\\]", sentence)]
        if not numbers:
            continue
        supported = any(
            nli_model.predict(premise=source_map[n].text, hypothesis=sentence).label == "entailment"
            for n in numbers if n in source_map
        )
        (verified if supported else flagged).append(sentence)
    return {"verified": verified, "flagged": flagged}
```

Sentences that land in `flagged` are candidates for removal or for showing a "this claim could
not be automatically verified" warning in the UI, rather than being displayed with the same
confidence as verified claims.

## Rendering the final cited answer

```python
def render_with_citations(answer_text: str, source_map: dict) -> dict:
    return {
        "text": answer_text,
        "citations": [
            {"marker": n, "source": s.metadata.get("source"), "excerpt": s.text[:150]}
            for n, s in source_map.items()
            if f"[{n}]" in answer_text
        ],
    }
```

This structured shape is what a frontend would use to render clickable citation markers that
expand to show the actual source excerpt — turning an abstract "trust me" answer into something
a user can verify in two clicks.
""",
                    "examples": [
                        {
                            "title": "From question to a fully cited, structured answer",
                            "code": (
                                "context_text, source_map = build_context_with_labels(reranked)\n"
                                "raw_answer = llm.generate(CITED_PROMPT.format(context=context_text, question=question), temperature=0.1)\n"
                                "cited = render_with_citations(raw_answer, source_map)\n"
                                "print(cited[\"text\"])\n"
                                "print(cited[\"citations\"])"
                            ),
                            "explanation": "This is the citation-aware version of the answer_question function from the Generation module, ready to hand to a frontend.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a test confirming extract_citations ignores a citation marker like [9] when source_map only contains keys 1 through 5.",
                            "difficulty": "easy",
                            "hint": "Construct a fake answer_text containing '[9]' and assert it's excluded from the result.",
                        },
                        {
                            "prompt": "Modify render_with_citations to flag an answer as needing review if it contains zero citation markers despite the prompt requiring them.",
                            "difficulty": "medium",
                            "hint": "Check whether the citations list ends up empty even though context sources were provided.",
                        },
                        {
                            "prompt": "Implement a simplified verify_answer_citations using keyword overlap instead of a full NLI model, and discuss one way it could give a false positive.",
                            "difficulty": "hard",
                            "hint": "Keyword overlap might mark a claim 'supported' just because it shares vocabulary with the source, even if the source contradicts the claim.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic Citations API documentation",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/citations",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "metadata-filtering",
            "title": "Metadata Filtering",
            "description": "Narrowing retrieval to the right subset of documents using structured attributes alongside vector similarity.",
            "order_index": 10,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "designing-metadata-schemas-for-filtering",
                    "title": "Designing Metadata Schemas for Filtering",
                    "description": "Decide what structured attributes to attach to chunks so retrieval can be scoped precisely.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify common metadata fields that support real-world filtering needs",
                        "Design a metadata schema that balances usefulness against index bloat",
                        "Explain how metadata enables multi-tenant and access-controlled retrieval",
                        "Recognize the difference between filtering before and after vector search",
                    ],
                    "content_markdown": """
## Why this matters

Vector similarity alone can't express constraints like "only search documents this user is
permitted to see" or "only search policies still in effect." Metadata filtering combines
structured, exact constraints with semantic similarity — and getting the schema right early
saves a painful re-indexing project later.

## Common metadata fields

```python
metadata = {
    "source": "employee-handbook.pdf",
    "category": "hr-policy",
    "tenant_id": "acme-corp",
    "access_level": "internal",
    "effective_date": "2026-01-01",
    "expiry_date": None,
    "language": "en",
    "doc_version": "3.2",
}
```

Not every use case needs all of these — the discipline is picking the fields that map to real
constraints your product needs to enforce, not attaching everything you can think of
speculatively.

## Filtering enables multi-tenancy and access control

```python
results = vector_db.query(
    vector=query_vec,
    top_k=10,
    filter={"tenant_id": "acme-corp", "access_level": {"$in": ["public", "internal"]}},
)
```

In a multi-tenant RAG product, this filter is not optional polish — without it, a query from
one customer could retrieve another customer's private documents purely because they're
semantically similar. Access control via metadata filtering is a security requirement, not a
feature.

## Filtering by recency and validity

```python
from datetime import date

results = vector_db.query(
    vector=query_vec,
    top_k=10,
    filter={"effective_date": {"$lte": str(date.today())}, "expiry_date": {"$gte": str(date.today())}},
)
```

This pattern matters enormously for policy documents: an outdated policy chunk that's
semantically similar to the query should never be retrieved once a newer version has superseded
it, even if the old chunk is still sitting in your index.

## Pre-filtering vs. post-filtering

**Pre-filtering** applies metadata constraints *before* the approximate nearest-neighbor search
runs, so the ANN index only searches within the allowed subset. **Post-filtering** runs the
vector search first, then discards results that don't match the filter afterward.

```python
# Post-filtering risk: if top_k=10 candidates come back and none match
# the filter, you get zero results even though matching documents exist
# elsewhere in the full index.
raw = vector_db.query(vector=query_vec, top_k=10)
filtered = [r for r in raw if r.metadata["tenant_id"] == "acme-corp"]
# filtered could easily be empty even with plenty of acme-corp docs indexed
```

Most modern vector databases (Chroma, Pinecone, Qdrant, Weaviate) support native pre-filtering,
which searches only within the filtered subset directly — always prefer this over manual
post-filtering when your database supports it, precisely because of the under-return risk shown
above.

## Schema design as a forward-looking decision

Adding a new metadata field later is usually straightforward — you can backfill it during
re-ingestion. Removing the *need* for a field you forgot (like access control) after a system
is already handling real user data is much more costly. When in doubt, include fields for
access control and tenancy from day one, even in a single-tenant prototype, since retrofitting
security boundaries into a system already in production is high-risk work.
""",
                    "examples": [
                        {
                            "title": "A filter that combines tenancy, access, and recency in one query",
                            "code": (
                                "results = vector_db.query(\n"
                                "    vector=query_vec,\n"
                                "    top_k=10,\n"
                                "    filter={\n"
                                "        \"tenant_id\": \"acme-corp\",\n"
                                "        \"access_level\": {\"$in\": [\"public\", \"internal\"]},\n"
                                "        \"effective_date\": {\"$lte\": \"2026-09-23\"},\n"
                                "    },\n"
                                ")"
                            ),
                            "explanation": "Combining multiple filter constraints in one native query is both more correct and more efficient than chaining several post-filter passes in application code.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a metadata schema for a RAG system over internal engineering documentation shared across multiple teams, listing each field and the filtering need it serves.",
                            "difficulty": "medium",
                            "hint": "Think about team ownership, document status (draft vs. published), and deprecation.",
                        },
                        {
                            "prompt": "Explain, with a concrete example, why post-filtering a top_k=5 result set can return fewer than 5 results even when 20 matching documents exist in the full index.",
                            "difficulty": "medium",
                            "hint": "Walk through what happens if none of the 5 nearest neighbors overall happen to satisfy the filter.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Pinecone: metadata filtering guide",
                            "url": "https://docs.pinecone.io/guides/data/filter-with-metadata",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "vector-db", "weight": 0.5}],
                },
                {
                    "slug": "filtered-retrieval-in-practice",
                    "title": "Filtered Retrieval in Practice",
                    "description": "Implement filtered retrieval across FAISS and Chroma, including the workarounds FAISS needs for native filtering.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement filtered queries against a Chroma collection",
                        "Implement filtering for FAISS, which lacks native metadata support",
                        "Write tests confirming filters correctly restrict result sets",
                        "Measure the recall cost of over-restrictive filtering",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson covered why filtering matters; this one covers the practical reality that
not every vector store supports it the same way. FAISS in particular has no built-in metadata
system at all, so filtering has to be layered on manually.

## Native filtering with Chroma

```python
def retrieve_filtered_chroma(query: str, collection, filters: dict, top_k: int = 10) -> list:
    query_vec = embed_texts([query])[0]
    raw = collection.query(query_embeddings=[query_vec], n_results=top_k, where=filters)
    return [
        RetrievalResult(chunk_id=cid, text=doc, score=1 - dist, metadata=meta)
        for cid, doc, dist, meta in zip(raw["ids"][0], raw["documents"][0], raw["distances"][0], raw["metadatas"][0])
    ]

results = retrieve_filtered_chroma(
    "vacation policy",
    collection,
    filters={"$and": [{"tenant_id": "acme-corp"}, {"category": "hr-policy"}]},
    top_k=5,
)
```

Chroma applies `where` filters natively during the search, avoiding the under-return problem
from the previous lesson.

## Filtering with FAISS: the manual approach

FAISS itself has no concept of metadata, so filtering requires either (a) over-fetching and
post-filtering, accepting the under-return risk, or (b) maintaining separate FAISS indexes per
filterable dimension.

```python
def retrieve_filtered_faiss(query: str, index, id_map: dict, filters: dict, top_k: int = 5, over_fetch: int = 50) -> list:
    query_vec = np.array([embed_texts([query])[0]], dtype="float32")
    faiss.normalize_L2(query_vec)
    scores, indices = index.search(query_vec, over_fetch)

    matched = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        chunk = id_map[idx]
        if all(chunk.metadata.get(k) == v for k, v in filters.items()):
            matched.append(RetrievalResult(chunk_id=chunk.id, text=chunk.text, score=float(score), metadata=chunk.metadata))
        if len(matched) >= top_k:
            break
    return matched
```

Over-fetching a larger candidate pool (`over_fetch=50`) before filtering down to `top_k`
mitigates, but does not eliminate, the under-return risk — if fewer than `top_k` of the 50
candidates match the filter, you still get a short result list. This is the direct, practical
cost of using a library without native metadata support.

## Maintaining per-tenant FAISS indexes as an alternative

For strict multi-tenant isolation with FAISS, some teams instead maintain one separate index
per tenant rather than filtering a shared index:

```python
tenant_indexes: dict[str, tuple] = {}  # tenant_id -> (faiss_index, id_map)

def retrieve_for_tenant(query: str, tenant_id: str, top_k: int = 5) -> list:
    index, id_map = tenant_indexes[tenant_id]
    return retrieve_faiss(query, index, id_map, top_k=top_k)
```

This guarantees structural isolation (like the namespace pattern from Course 5) at the cost of
managing many small indexes instead of one large filterable one — a reasonable tradeoff when
tenant isolation is a hard security requirement rather than a soft filtering preference.

## Testing filter correctness

```python
def test_filtered_retrieval_excludes_other_tenants():
    results = retrieve_filtered_chroma("policy", collection, filters={"tenant_id": "acme-corp"}, top_k=10)
    assert all(r.metadata["tenant_id"] == "acme-corp" for r in results)
```

A test like this belongs in any multi-tenant RAG system's test suite as a permanent regression
guard — a filtering bug here is a data leak, not just a quality issue.

## Measuring the recall cost of over-restrictive filters

If a filter is too narrow (e.g., filtering to a single document version when the answer exists
in multiple versions), recall drops even though the underlying retrieval is working correctly.
Always test filtered recall against the same evaluation set you'd use for unfiltered retrieval,
so filtering-induced recall loss doesn't get misattributed to embedding or chunking quality.
""",
                    "examples": [
                        {
                            "title": "Comparing filtered vs. unfiltered recall on the same query",
                            "code": (
                                "unfiltered = retriever.retrieve(\"vacation policy\", top_k=10)\n"
                                "filtered = retrieve_filtered_chroma(\"vacation policy\", collection, {\"tenant_id\": \"acme-corp\"}, top_k=10)\n"
                                "print(len(unfiltered), \"vs\", len(filtered), \"results\")"
                            ),
                            "explanation": "A large gap between filtered and unfiltered result counts is worth investigating -- it may indicate a filter that's more restrictive than intended.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement retrieve_filtered_faiss and test it against an index where only 2 of 50 over-fetched candidates match the filter, confirming it returns fewer than top_k results as expected.",
                            "difficulty": "medium",
                            "hint": "Construct a small test index where you control exactly which chunks have which metadata.",
                        },
                        {
                            "prompt": "Write the multi-tenant isolation test from this lesson and deliberately break the filter logic to confirm the test actually catches the regression.",
                            "difficulty": "medium",
                            "hint": "Comment out the filter application temporarily and confirm the test fails.",
                        },
                        {
                            "prompt": "Compare the per-tenant-index approach against shared-index-with-filtering for a product with 10,000 tenants, and discuss which scales better operationally.",
                            "difficulty": "hard",
                            "hint": "Consider index build time, memory overhead per empty or small tenant index, and operational complexity of managing thousands of indexes.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Chroma: filtering with 'where' clauses",
                            "url": "https://docs.trychroma.com/docs/querying-collections/metadata-filtering",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.7}, {"slug": "vector-db", "weight": 0.6}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "hybrid-search",
            "title": "Hybrid Search",
            "description": "Combining keyword and vector search so exact terms and semantic meaning are both covered.",
            "order_index": 11,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "combining-keyword-and-vector-search",
                    "title": "Combining Keyword and Vector Search",
                    "description": "Understand why hybrid search exists and how BM25 and vector search complement each other's blind spots.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what BM25 scoring captures that vector similarity does not",
                        "Describe the general architecture of a hybrid search system",
                        "Identify query types where hybrid search meaningfully outperforms either method alone",
                        "Recognize the score-scale mismatch problem between BM25 and cosine similarity",
                    ],
                    "content_markdown": """
## Why this matters

Course 5 introduced the idea that keyword and vector search have complementary weaknesses.
Hybrid search is where that idea becomes a concrete architectural pattern you can implement:
run both searches, then merge their results into a single, better-informed ranking.

## What BM25 captures that vectors miss

BM25 (Best Matching 25) is a keyword-scoring algorithm that rewards documents containing query
terms, weighted by term rarity (rare terms count more) and term frequency (with diminishing
returns for repetition). It excels precisely where embeddings struggle: exact identifiers,
codes, acronyms, and rare proper nouns that an embedding model may not have learned strong
representations for.

```python
from rank_bm25 import BM25Okapi

corpus_tokens = [chunk.text.lower().split() for chunk in chunks]
bm25 = BM25Okapi(corpus_tokens)

query_tokens = "error code E-4521".lower().split()
scores = bm25.get_scores(query_tokens)
top_indices = scores.argsort()[::-1][:10]
```

A query for "error code E-4521" will score chunks containing that exact string far higher with
BM25 than with embedding similarity, which might rank a chunk about generic "error handling"
almost as high — even though it never mentions this specific code.

## The basic hybrid architecture

```python
def hybrid_search(query: str, vector_retriever, bm25, chunks: list, top_k: int = 10) -> list:
    vector_results = vector_retriever.retrieve(query, top_k=top_k)
    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_top_indices = bm25_scores.argsort()[::-1][:top_k]
    bm25_results = [
        RetrievalResult(chunk_id=chunks[i].id, text=chunks[i].text, score=float(bm25_scores[i]), metadata=chunks[i].metadata)
        for i in bm25_top_indices
    ]
    return merge_results(vector_results, bm25_results, top_k=top_k)
```

The `merge_results` function is the interesting part — explored fully in the next lesson,
because the naive approach of just averaging the two scores runs into a real problem.

## Why you can't just average the scores

Cosine similarity scores typically range narrowly, often 0.6-0.95 for relevant results. BM25
scores are unbounded and depend on corpus size and term frequency statistics, easily ranging
from 0 to 30 or more. Averaging a 0.85 cosine score with a 12.3 BM25 score produces a
meaningless number — the BM25 score would completely dominate any naive average, defeating the
purpose of combining the two signals fairly.

```python
# This is broken -- BM25's larger scale swamps the vector score:
combined_score = 0.5 * cosine_score + 0.5 * bm25_score  # DON'T do this directly
```

## When hybrid search earns its complexity

Hybrid search adds real engineering cost: two search systems to maintain, index, and keep in
sync. It's worth that cost specifically when your corpus and query patterns include a
meaningful share of exact-match needs — product codes, legal citations, technical
identifiers — alongside natural-language questions. A corpus of purely conversational FAQ
content may see little benefit from the added complexity; a corpus of technical documentation
or legal text often benefits substantially.
""",
                    "examples": [
                        {
                            "title": "A query hybrid search handles better than either method alone",
                            "code": (
                                "query = \"how do I fix error E-4521 during checkout\"\n"
                                "# Vector search: strong on 'fix ... during checkout' (the intent)\n"
                                "# BM25: strong on 'E-4521' (the exact identifier)\n"
                                "# Neither alone reliably nails both halves of this query"
                            ),
                            "explanation": "This is the canonical hybrid search use case: one query with both a semantic intent component and an exact-match component.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For your own project's expected queries, estimate what percentage would benefit from exact-match (BM25) signal versus pure semantic matching, and use that estimate to justify whether hybrid search is worth building.",
                            "difficulty": "medium",
                            "hint": "Look for identifiers, codes, names, or numbers in likely queries.",
                        },
                        {
                            "prompt": "Explain, using the score ranges given in this lesson, exactly why 0.5 * cosine + 0.5 * bm25 produces a ranking dominated by BM25 rather than a balanced combination.",
                            "difficulty": "easy",
                            "hint": "Compare the relative magnitude each term contributes to the sum given typical score ranges.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Elastic: BM25 algorithm explained",
                            "url": "https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}],
                },
                {
                    "slug": "implementing-reciprocal-rank-fusion",
                    "title": "Implementing Reciprocal Rank Fusion",
                    "description": "Merge vector and keyword search results correctly using rank-based fusion instead of raw score averaging.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain how Reciprocal Rank Fusion avoids the score-scale mismatch problem",
                        "Implement RRF to merge two ranked result lists into one",
                        "Tune RRF's k constant and understand what it controls",
                        "Evaluate a hybrid search implementation against vector-only and keyword-only baselines",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson showed why averaging raw BM25 and cosine scores doesn't work. Reciprocal
Rank Fusion (RRF) sidesteps the whole problem by ignoring raw scores entirely and combining
results based on *rank position* instead — a simple idea that turns out to work remarkably well
in practice.

## The RRF formula

For each result, RRF computes a score based only on where it ranked in each result list:

```
RRF_score(document) = sum over each ranking list of  1 / (k + rank_in_that_list)
```

Where `k` is a small constant (commonly 60) that dampens the impact of very high ranks. A
document that ranks #1 in both lists gets a much higher combined score than one that ranks #1
in only one list and is absent from the other.

```python
def reciprocal_rank_fusion(result_lists: list[list], k: int = 60) -> list:
    scores: dict[str, float] = {}
    item_lookup: dict[str, object] = {}
    for results in result_lists:
        for rank, result in enumerate(results, start=1):
            scores[result.chunk_id] = scores.get(result.chunk_id, 0) + 1 / (k + rank)
            item_lookup[result.chunk_id] = result
    ranked_ids = sorted(scores, key=lambda cid: scores[cid], reverse=True)
    return [item_lookup[cid] for cid in ranked_ids]
```

Because RRF only ever looks at rank position (1st, 2nd, 3rd...), it works identically well
whether the underlying scores are cosine similarities in the 0.6-0.95 range or BM25 scores in
the 0-30 range — the scale mismatch problem simply disappears.

## Wiring it into hybrid search

```python
def hybrid_search(query: str, vector_retriever, bm25, chunks: list, top_k: int = 10) -> list:
    vector_results = vector_retriever.retrieve(query, top_k=20)

    bm25_scores = bm25.get_scores(query.lower().split())
    bm25_ranked_indices = bm25_scores.argsort()[::-1][:20]
    bm25_results = [
        RetrievalResult(chunk_id=chunks[i].id, text=chunks[i].text, score=float(bm25_scores[i]), metadata=chunks[i].metadata)
        for i in bm25_ranked_indices
    ]

    fused = reciprocal_rank_fusion([vector_results, bm25_results], k=60)
    return fused[:top_k]
```

Retrieving a generous 20 from each method before fusing gives RRF enough signal to work with —
fusing two very short lists (e.g., top_k=3 from each) leaves little room for rank position to
meaningfully differentiate results.

## What the k constant controls

A smaller k (e.g., 10) makes RRF weight top-ranked results much more heavily than lower-ranked
ones; a larger k (e.g., 100) flattens the differences between ranks, giving results further
down each list more relative influence. k=60 is a widely used default from the original RRF
paper and a reasonable starting point before tuning.

```python
# Illustrating the effect of k on a rank-1 vs rank-5 result:
for k in [10, 60, 100]:
    rank1_score = 1 / (k + 1)
    rank5_score = 1 / (k + 5)
    print(f"k={k}: rank1={rank1_score:.4f}, rank5={rank5_score:.4f}, ratio={rank1_score/rank5_score:.2f}")
```

## Evaluating hybrid vs. single-method search

```python
def compare_methods(eval_queries: list, vector_retriever, bm25, chunks: list) -> dict:
    results = {"vector_only": 0, "bm25_only": 0, "hybrid": 0}
    for item in eval_queries:
        vector_hit = any(r.chunk_id == item["expected_chunk_id"] for r in vector_retriever.retrieve(item["query"], top_k=5))
        hybrid_hit = any(r.chunk_id == item["expected_chunk_id"] for r in hybrid_search(item["query"], vector_retriever, bm25, chunks, top_k=5))
        results["vector_only"] += int(vector_hit)
        results["hybrid"] += int(hybrid_hit)
    return {k: v / len(eval_queries) for k, v in results.items()}
```

Running this kind of comparison on your own evaluation set — not just trusting that hybrid
search is theoretically better — is how you confirm the added complexity actually pays off for
your specific corpus and query patterns, consistent with the measurement-first approach from
the Chunking module.
""",
                    "examples": [
                        {
                            "title": "RRF favoring a document that ranks well in both lists",
                            "code": (
                                "# doc_a: rank 1 in vector results, rank 8 in BM25 results\n"
                                "# doc_b: rank 2 in vector results, rank 2 in BM25 results\n"
                                "# RRF(doc_a) = 1/(60+1) + 1/(60+8) = 0.0164 + 0.0147 = 0.0311\n"
                                "# RRF(doc_b) = 1/(60+2) + 1/(60+2) = 0.0161 + 0.0161 = 0.0323\n"
                                "# doc_b wins -- consistently good in both lists beats being\n"
                                "# great in one and mediocre in the other"
                            ),
                            "explanation": "This worked example shows RRF's key property: consistent relevance across both signals is rewarded over being a top hit in only one.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement reciprocal_rank_fusion and verify by hand-computed example (like the one above) that it produces the expected ranking.",
                            "difficulty": "medium",
                            "hint": "Construct two small fake result lists with known ranks and compare against a manual RRF calculation.",
                        },
                        {
                            "prompt": "Run compare_methods on a small evaluation set and report whether hybrid search outperforms vector-only retrieval for your specific corpus.",
                            "difficulty": "hard",
                            "hint": "You'll need labeled (query, expected_chunk_id) pairs, similar to earlier evaluation exercises in this course.",
                        },
                        {
                            "prompt": "Experiment with k=10 versus k=100 in reciprocal_rank_fusion on the same two result lists and describe how the final ranking changes.",
                            "difficulty": "medium",
                            "hint": "Focus on whether a result that's rank 1 in one list but rank 15 in the other moves up or down as k changes.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Reciprocal Rank Fusion outperforms Condorcet and individual rank learning methods (original paper)",
                            "url": "https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "reranking",
            "title": "Reranking",
            "description": "Improving precision on a retrieved candidate set with a more powerful, more expensive scoring model.",
            "order_index": 12,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-rerank-after-retrieval",
                    "title": "Why Rerank After Retrieval",
                    "description": "Understand what cross-encoder rerankers do differently from embedding similarity, and why that improves precision.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the architectural difference between bi-encoders and cross-encoders",
                        "Describe why cross-encoders are more accurate but too slow to run on an entire corpus",
                        "Identify the retrieve-then-rerank pattern as the standard way to combine both",
                        "Recognize the latency and cost tradeoff reranking introduces",
                    ],
                    "content_markdown": """
## Why this matters

Retrieval (even hybrid retrieval) is fundamentally a fast, approximate first pass — it has to
be, because it searches across potentially millions of chunks. Reranking is where you spend
more compute on a much smaller candidate set to get meaningfully better precision on the
results that actually reach the LLM.

## Bi-encoders vs. cross-encoders

The embedding models you've used throughout this course are **bi-encoders**: the query and each
document are encoded into vectors *independently*, and similarity is computed afterward with a
cheap dot product. This independence is exactly what makes vector search fast — document
vectors can be precomputed once and reused for every future query.

```python
# Bi-encoder: independent encoding, fast at scale
query_vec = embed(query)       # computed once per query
doc_vec = embed(document)      # precomputed once, reused for every query
score = cosine_similarity(query_vec, doc_vec)
```

A **cross-encoder** instead feeds the query and document *together* into one model in a single
forward pass, letting the model's attention directly compare specific words and phrases between
them. This produces meaningfully more accurate relevance scores, but it cannot be precomputed —
every query-document pair needs its own full model pass.

```python
# Cross-encoder: joint encoding, accurate but must run per query-document pair
score = cross_encoder.predict([(query, document)])
# Cannot precompute -- every new query requires re-scoring every candidate document
```

## Why cross-encoders can't replace vector search

Running a cross-encoder over your entire corpus for every query would mean thousands to
millions of full model forward passes per request — far too slow and expensive for interactive
use. Vector search's precomputed embeddings let it narrow millions of documents down to a
handful of candidates in milliseconds; cross-encoders can then afford to carefully re-score just
those few candidates.

## The retrieve-then-rerank pattern

```python
def retrieve_and_rerank(query: str, retriever, cross_encoder, retrieve_k: int = 30, final_k: int = 5) -> list:
    candidates = retriever.retrieve(query, top_k=retrieve_k)
    pairs = [(query, c.text) for c in candidates]
    scores = cross_encoder.predict(pairs)
    reranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
    return [c for c, score in reranked[:final_k]]
```

This two-stage pattern — cheap, broad retrieval followed by expensive, narrow reranking — is
the standard architecture in nearly every production RAG system that cares about precision, and
it's the same "retrieve broad, narrow precisely" idea introduced back in the Retrieval module,
now with a concrete implementation.

## The tradeoff reranking introduces

Reranking adds real latency (a model call scoring 20-30 candidates) and cost to every query.
It's worth that cost when retrieval precision is genuinely limiting answer quality — verify this
with the same recall/precision measurement approach from the Retrieval module before adding
reranking, rather than assuming it's always beneficial. For latency-sensitive applications with
already-strong retrieval, reranking's cost may not be justified.
""",
                    "examples": [
                        {
                            "title": "A case where reranking changes the top result",
                            "code": (
                                "query = \"Can I cancel my subscription during the trial period?\"\n"
                                "# Vector search top-1 (bi-encoder): a chunk generally about 'subscriptions'\n"
                                "# Cross-encoder reranking top-1: a chunk specifically about\n"
                                "# 'cancellation during trial' -- the cross-encoder's joint\n"
                                "# attention over both texts caught the specific match that\n"
                                "# independent embedding similarity slightly under-weighted"
                            ),
                            "explanation": "This is the concrete payoff of reranking: catching precise relevance that bi-encoder similarity alone sometimes misses.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Explain in your own words why a cross-encoder's document representations cannot be precomputed and cached the way bi-encoder embeddings can.",
                            "difficulty": "easy",
                            "hint": "Consider what input the cross-encoder actually needs to produce its score.",
                        },
                        {
                            "prompt": "For a system with 50ms retrieval latency budget and a cross-encoder that takes 8ms per candidate, calculate the maximum number of candidates you could rerank within a 200ms total budget.",
                            "difficulty": "medium",
                            "hint": "200ms total minus 50ms retrieval leaves 150ms for reranking; divide by per-candidate cost.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Sentence-Transformers: cross-encoders documentation",
                            "url": "https://www.sbert.net/examples/applications/cross-encoder/README.html",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "reranking", "weight": 1.0}],
                },
                {
                    "slug": "implementing-a-cross-encoder-reranker",
                    "title": "Implementing a Cross-Encoder Reranker",
                    "description": "Wire a cross-encoder reranking step into the retrieval pipeline and measure its impact on precision.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement reranking using an open-source cross-encoder model",
                        "Batch cross-encoder scoring for efficiency across many candidates",
                        "Combine reranking with the hybrid search results from the previous module",
                        "Measure precision@k before and after reranking on an evaluation set",
                    ],
                    "content_markdown": """
## Why this matters

This lesson turns the previous lesson's theory into a `Reranker` class that slots directly into
the `answer_question` pipeline built in the Generation module — the final piece that upgrades
retrieval from "roughly relevant" to "precisely relevant" before generation ever sees the
context.

## Using an open-source cross-encoder

```python
from sentence_transformers import CrossEncoder

class Reranker:
    def __init__(self, model_name: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        self.model = CrossEncoder(model_name)

    def rerank(self, query: str, candidates: list, top_k: int = 5) -> list:
        if not candidates:
            return []
        pairs = [(query, c.text) for c in candidates]
        scores = self.model.predict(pairs)
        ranked = sorted(zip(candidates, scores), key=lambda pair: pair[1], reverse=True)
        return [
            RetrievalResult(chunk_id=c.chunk_id, text=c.text, score=float(score), metadata=c.metadata)
            for c, score in ranked[:top_k]
        ]
```

`ms-marco-MiniLM-L-6-v2` is a small, fast cross-encoder trained specifically for passage
reranking — a strong default for getting started before evaluating whether a larger, slower
model is worth its extra latency for your use case.

## Batching for efficiency

`CrossEncoder.predict()` already batches internally, but being explicit about batch size
matters when reranking large candidate sets or running on constrained hardware.

```python
scores = self.model.predict(pairs, batch_size=32, show_progress_bar=False)
```

## Combining with hybrid search

```python
def full_retrieval_pipeline(query: str, vector_retriever, bm25, chunks: list, reranker: Reranker) -> list:
    hybrid_candidates = hybrid_search(query, vector_retriever, bm25, chunks, top_k=30)
    return reranker.rerank(query, hybrid_candidates, top_k=5)
```

This chains every retrieval technique from this course into one pipeline: hybrid search casts a
wide, high-recall net across both semantic and keyword signals, and reranking narrows that net
down to a small, high-precision set ready for context construction.

## Measuring the precision improvement

```python
def measure_precision_improvement(eval_queries: list, retriever, reranker) -> dict:
    before, after = [], []
    for item in eval_queries:
        candidates = retriever.retrieve(item["query"], top_k=20)
        before_hit = any(c.chunk_id == item["expected_chunk_id"] for c in candidates[:5])

        reranked = reranker.rerank(item["query"], candidates, top_k=5)
        after_hit = any(c.chunk_id == item["expected_chunk_id"] for c in reranked)

        before.append(before_hit)
        after.append(after_hit)
    return {"precision_before": sum(before) / len(before), "precision_after": sum(after) / len(after)}
```

Running this on a real evaluation set — not just trusting reranking is beneficial in theory —
tells you exactly how much precision@5 improved, and whether that improvement is worth the
added latency for your specific application.

## When NOT to rerank

If your evaluation shows retrieval precision@5 is already high (say, above 0.9) without
reranking, the added latency and cost may not be worth a marginal improvement. Reranking earns
its keep most clearly when precision@5 without it is noticeably weaker than recall@20 — meaning
the right chunks are being found, just not consistently ranked near the top.
""",
                    "examples": [
                        {
                            "title": "The full pipeline from query to reranked context",
                            "code": (
                                "reranker = Reranker()\n"
                                "final_results = full_retrieval_pipeline(\n"
                                "    \"Can I cancel during the trial period?\", vector_retriever, bm25, chunks, reranker\n"
                                ")\n"
                                "for r in final_results:\n"
                                "    print(round(r.score, 3), r.text[:80])"
                            ),
                            "explanation": "This single call now represents hybrid search plus reranking -- the complete retrieval-side pipeline this course has been building toward since the Retrieval module.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement the Reranker class and confirm it correctly reorders a small hand-crafted set of 5 candidates where you know which one should rank first.",
                            "difficulty": "medium",
                            "hint": "Craft one obviously-relevant and several obviously-irrelevant candidates to make the expected reordering clear.",
                        },
                        {
                            "prompt": "Run measure_precision_improvement on your evaluation set and report the before/after precision@5 numbers, along with the added latency reranking introduced.",
                            "difficulty": "hard",
                            "hint": "Wrap both the retrieval-only and full pipeline calls with time.perf_counter() to measure latency alongside precision.",
                        },
                        {
                            "prompt": "Explain a scenario, using the guidance at the end of this lesson, where you would recommend NOT adding reranking to a RAG system.",
                            "difficulty": "easy",
                            "hint": "Think about a system with already-high retrieval precision and a strict low-latency requirement.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Sentence-Transformers: pretrained cross-encoder models",
                            "url": "https://www.sbert.net/docs/pretrained-models/ce-msmarco.html",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "reranking", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "rag-evaluation",
            "title": "RAG Evaluation",
            "description": "Measuring retrieval quality and generation faithfulness with real, repeatable metrics instead of eyeballing outputs.",
            "order_index": 13,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "metrics-for-retrieval-quality",
                    "title": "Metrics for Retrieval Quality",
                    "description": "Formalize recall@k, precision@k, and MRR as repeatable ways to measure retrieval performance.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define recall@k, precision@k, and Mean Reciprocal Rank (MRR) precisely",
                        "Build a labeled evaluation set suitable for measuring these metrics",
                        "Explain why MRR captures ranking quality that recall@k alone misses",
                        "Interpret metric results to decide what part of the pipeline to improve next",
                    ],
                    "content_markdown": """
## Why this matters

Every earlier module in this course referenced "measure retrieval quality" as the right way to
tune chunk size, k, filters, and reranking. This lesson formalizes exactly how, turning
intuition into numbers you can track over time and compare across pipeline changes.

## Building a labeled evaluation set

Every retrieval metric needs ground truth: a set of (query, relevant_chunk_ids) pairs a human
has verified are correct.

```python
eval_set = [
    {"query": "How long is the return window?", "relevant_chunk_ids": {"return-policy-chunk-2"}},
    {"query": "Can I cancel during the free trial?", "relevant_chunk_ids": {"billing-chunk-5", "billing-chunk-6"}},
    # 30-100 examples is a reasonable starting size for meaningful signal
]
```

Building this set by hand, ideally from real user queries you've collected, is the single
highest-leverage investment in a RAG project's quality — every metric in this lesson is only as
trustworthy as this data.

## Recall@k and precision@k, formalized

```python
def recall_at_k(retrieved_ids: set, relevant_ids: set) -> float:
    if not relevant_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(relevant_ids)

def precision_at_k(retrieved_ids: set, relevant_ids: set) -> float:
    if not retrieved_ids:
        return 0.0
    return len(retrieved_ids & relevant_ids) / len(retrieved_ids)

def evaluate_retrieval(retriever, eval_set: list, k: int = 5) -> dict:
    recalls, precisions = [], []
    for item in eval_set:
        retrieved = {r.chunk_id for r in retriever.retrieve(item["query"], top_k=k)}
        recalls.append(recall_at_k(retrieved, item["relevant_chunk_ids"]))
        precisions.append(precision_at_k(retrieved, item["relevant_chunk_ids"]))
    return {"recall@k": sum(recalls) / len(recalls), "precision@k": sum(precisions) / len(precisions)}
```

## Mean Reciprocal Rank: measuring where the answer landed

Recall@k treats "the right chunk was rank 1" and "the right chunk was rank 5" identically, as
long as both are within k. MRR instead rewards results that rank the correct answer higher.

```python
def reciprocal_rank(ranked_ids: list, relevant_ids: set) -> float:
    for rank, chunk_id in enumerate(ranked_ids, start=1):
        if chunk_id in relevant_ids:
            return 1 / rank
    return 0.0

def mean_reciprocal_rank(retriever, eval_set: list, k: int = 10) -> float:
    scores = []
    for item in eval_set:
        ranked = [r.chunk_id for r in retriever.retrieve(item["query"], top_k=k)]
        scores.append(reciprocal_rank(ranked, item["relevant_chunk_ids"]))
    return sum(scores) / len(scores)
```

A system with MRR close to 1.0 consistently ranks the correct chunk first; an MRR around 0.3
means the correct chunk is often found, but buried several positions down — exactly the
situation reranking is built to fix, and exactly the signal that would tell you it's needed.

## Reading the metrics together

- **High recall, low precision** → retrieval finds the right chunk but surrounds it with noise
  → reranking is likely to help.
- **Low recall** → the right chunk often isn't found at all → revisit chunking, embedding model,
  or k before reaching for reranking, since reranking can't fix a candidate set that never
  contained the answer.
- **High recall, low MRR** → the right chunk is present but not ranked near the top → also
  points toward reranking, or reconsidering the embedding model's ranking quality.

## Tracking metrics over time

Treat these metrics like any other test suite: run them on every meaningful pipeline change
(new chunk size, new embedding model, added reranking) and track the trend. A change that
improves recall but tanks precision isn't a clear win — the tradeoffs discussed throughout this
course only become visible when you measure both sides.
""",
                    "examples": [
                        {
                            "title": "Comparing metrics before and after adding reranking",
                            "code": (
                                "before = evaluate_retrieval(vector_retriever, eval_set, k=5)\n"
                                "after = evaluate_retrieval(full_pipeline_retriever, eval_set, k=5)\n"
                                "print(\"Before:\", before)\n"
                                "print(\"After: \", after)\n"
                                "print(\"MRR before:\", mean_reciprocal_rank(vector_retriever, eval_set))\n"
                                "print(\"MRR after: \", mean_reciprocal_rank(full_pipeline_retriever, eval_set))"
                            ),
                            "explanation": "Running the same evaluation set through two pipeline versions is the concrete practice that turns 'reranking should help' into a measured, evidence-based claim.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a 15-item evaluation set for a document collection you have access to, and compute recall@5, precision@5, and MRR for your current retriever.",
                            "difficulty": "hard",
                            "hint": "Start from real questions you'd expect users to ask, then manually identify the correct chunk for each.",
                        },
                        {
                            "prompt": "Given a ranked result list where the correct chunk appears at rank 3, compute its reciprocal rank contribution by hand and explain what a system-wide MRR of 0.33 would suggest about typical ranking quality.",
                            "difficulty": "easy",
                            "hint": "1/3 = 0.33; an average MRR near this suggests the correct answer typically lands around rank 3, not rank 1.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "RAGAS: retrieval metrics documentation",
                            "url": "https://docs.ragas.io/en/stable/concepts/metrics/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.8}, {"slug": "evaluation", "weight": 0.6}],
                },
                {
                    "slug": "evaluating-generation-faithfulness",
                    "title": "Evaluating Generation Faithfulness and Relevance",
                    "description": "Measure whether generated answers are actually supported by retrieved context, and whether they answer the question asked.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define faithfulness and answer relevance as distinct generation-quality metrics",
                        "Explain how an LLM-as-judge evaluates faithfulness without ground-truth answers",
                        "Identify the limitations and biases of using an LLM to judge another LLM's output",
                        "Combine retrieval and generation metrics into one evaluation report",
                    ],
                    "content_markdown": """
## Why this matters

Good retrieval doesn't guarantee a good answer — generation can still ignore, misread, or
embellish beyond what the retrieved context supports. Retrieval metrics from the previous lesson
say nothing about this; faithfulness and relevance metrics do.

## Faithfulness: is the answer actually supported by the context?

Faithfulness measures whether every claim in the generated answer is backed by the retrieved
context, independent of whether the answer is factually true in the real world. A faithful
answer to wrong or incomplete context can still be an unhelpful answer — faithfulness and
correctness are related but distinct.

```python
def evaluate_faithfulness(question: str, context: str, answer: str, judge_llm) -> dict:
    prompt = (
        "Given the context and answer below, identify each factual claim in the answer and state "
        "whether it is directly supported by the context. Respond with a JSON list of "
        "{claim, supported} objects.\\n\\n"
        f"Context:\\n{context}\\n\\nAnswer:\\n{answer}"
    )
    response = judge_llm.generate(prompt)
    claims = parse_json(response)
    supported_count = sum(1 for c in claims if c["supported"])
    return {"faithfulness_score": supported_count / len(claims) if claims else 1.0, "claims": claims}
```

This is the **LLM-as-judge** pattern: using a (typically stronger or differently-prompted)
language model to evaluate another model's output, because faithfulness checking requires the
same kind of language understanding that generation itself requires — hard to do with simple
keyword or regex rules.

## Answer relevance: does the answer address the question?

A perfectly faithful answer can still miss the point of the question — technically true, fully
supported by context, but not what was asked.

```python
def evaluate_answer_relevance(question: str, answer: str, judge_llm) -> float:
    prompt = (
        "On a scale of 1-5, how directly does this answer address the question asked? "
        "5 means it fully and directly answers the question; 1 means it's off-topic or evasive.\\n\\n"
        f"Question: {question}\\nAnswer: {answer}\\n\\nRespond with only the number."
    )
    response = judge_llm.generate(prompt, temperature=0.0)
    return float(response.strip())
```

## The limitations of LLM-as-judge

LLM judges inherit the same weaknesses as the models they're evaluating: they can be
inconsistent between runs, biased toward longer or more confident-sounding answers regardless
of actual quality, and occasionally wrong about what counts as "supported." Mitigate this by
using a low temperature for judging, running each evaluation multiple times and averaging, and
periodically spot-checking judge outputs against human judgment — never treat LLM-as-judge
scores as ground truth without any human calibration.

```python
def evaluate_faithfulness_stable(question: str, context: str, answer: str, judge_llm, runs: int = 3) -> float:
    scores = [evaluate_faithfulness(question, context, answer, judge_llm)["faithfulness_score"] for _ in range(runs)]
    return sum(scores) / len(scores)
```

## Combining retrieval and generation metrics

```python
def full_evaluation_report(eval_set: list, retriever, reranker, llm, judge_llm) -> dict:
    retrieval_metrics = evaluate_retrieval(retriever, eval_set, k=5)
    faithfulness_scores, relevance_scores = [], []
    for item in eval_set:
        result = answer_question(item["query"], retriever, reranker, llm)
        context = format_context(result.sources)
        faithfulness_scores.append(evaluate_faithfulness(item["query"], context, result.answer, judge_llm)["faithfulness_score"])
        relevance_scores.append(evaluate_answer_relevance(item["query"], result.answer, judge_llm))
    return {
        **retrieval_metrics,
        "faithfulness": sum(faithfulness_scores) / len(faithfulness_scores),
        "answer_relevance": sum(relevance_scores) / len(relevance_scores),
    }
```

A report combining all four metrics tells a complete story: retrieval metrics diagnose whether
the right evidence was found, and faithfulness/relevance diagnose whether generation used that
evidence well — exactly the retrieval-vs-generation debugging split introduced back in the
Retrieval module, now backed by numbers instead of guesswork.
""",
                    "examples": [
                        {
                            "title": "A faithful answer scoring low on relevance",
                            "code": (
                                "question = \"What is the cancellation fee for enterprise plans?\"\n"
                                "answer = \"Enterprise plans include dedicated support and a named account manager.\"\n"
                                "# faithfulness_score could be 1.0 (every claim is true and in the context)\n"
                                "# answer_relevance could be 1 or 2 (the answer never addresses cancellation fees)\n"
                                "# This shows why the two metrics must be tracked separately"
                            ),
                            "explanation": "A high faithfulness score alone can mask a completely unhelpful answer -- this is exactly why both metrics are needed together.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a faithfulness evaluation prompt that also asks the judge to quote the specific context sentence supporting (or failing to support) each claim, and explain why this makes the score more auditable.",
                            "difficulty": "medium",
                            "hint": "Requiring a supporting quote forces the judge to ground its own judgment, similar to how you required citations from the generation model.",
                        },
                        {
                            "prompt": "Run full_evaluation_report on your evaluation set and identify, from the four scores, whether your system's weakest link is retrieval or generation.",
                            "difficulty": "hard",
                            "hint": "Low recall/precision points to retrieval; low faithfulness/relevance with good retrieval points to generation.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "RAGAS: faithfulness metric documentation",
                            "url": "https://docs.ragas.io/en/stable/concepts/metrics/available_metrics/faithfulness/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 0.7}, {"slug": "evaluation", "weight": 0.8}],
                },
                {
                    "slug": "building-a-rag-eval-harness",
                    "title": "Building a RAG Evaluation Harness",
                    "description": "Assemble retrieval and generation metrics into a reusable evaluation script you can run on every pipeline change.",
                    "lesson_type": "coding",
                    "order_index": 3,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Build a command-line evaluation harness that runs the full metric suite",
                        "Persist evaluation results to compare across pipeline versions over time",
                        "Set pass/fail thresholds to catch regressions automatically",
                        "Explain how to integrate a RAG eval harness into a CI-style workflow",
                    ],
                    "content_markdown": """
## Why this matters

An evaluation function you run manually once gets forgotten. An evaluation *harness* that's
easy to re-run, stores results over time, and can flag regressions automatically is what
actually keeps a RAG system's quality from silently degrading as you tune chunking, swap
embedding models, or change prompts.

## Structuring the harness

```python
import json
import time
from pathlib import Path

def run_eval_harness(eval_set_path: str, retriever, reranker, llm, judge_llm, output_dir: str = "./eval_runs") -> dict:
    eval_set = json.loads(Path(eval_set_path).read_text())
    report = full_evaluation_report(eval_set, retriever, reranker, llm, judge_llm)
    report["timestamp"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    report["eval_set_size"] = len(eval_set)

    Path(output_dir).mkdir(exist_ok=True)
    output_path = Path(output_dir) / f"eval_{int(time.time())}.json"
    output_path.write_text(json.dumps(report, indent=2))
    return report
```

Storing every run as a timestamped JSON file, rather than just printing results, is what makes
historical comparison possible later.

## Comparing against the previous run

```python
def compare_to_previous(current: dict, output_dir: str = "./eval_runs") -> dict:
    runs = sorted(Path(output_dir).glob("eval_*.json"))
    if len(runs) < 2:
        return {"comparison": "no previous run to compare against"}
    previous = json.loads(runs[-2].read_text())
    metrics = ["recall@k", "precision@k", "faithfulness", "answer_relevance"]
    return {
        m: {"previous": previous.get(m), "current": current.get(m), "delta": round(current.get(m, 0) - previous.get(m, 0), 3)}
        for m in metrics
    }
```

## Setting pass/fail thresholds

```python
THRESHOLDS = {"recall@k": 0.80, "precision@k": 0.70, "faithfulness": 0.90, "answer_relevance": 3.5}

def check_thresholds(report: dict) -> dict:
    failures = {m: report[m] for m, threshold in THRESHOLDS.items() if report.get(m, 0) < threshold}
    return {"passed": len(failures) == 0, "failures": failures}
```

Thresholds should come from your own baseline measurements, not arbitrary numbers — run the
harness on your current pipeline first, and set thresholds a bit below that baseline so genuine
regressions fail loudly while normal run-to-run noise doesn't.

## Wiring it into a CI-style workflow

```python
def main():
    report = run_eval_harness("./eval_set.json", retriever, reranker, llm, judge_llm)
    comparison = compare_to_previous(report)
    result = check_thresholds(report)

    print(json.dumps({"report": report, "comparison": comparison, "gate": result}, indent=2))
    if not result["passed"]:
        raise SystemExit(f"RAG eval gate failed: {result['failures']}")

if __name__ == "__main__":
    main()
```

Raising a non-zero exit code on failed thresholds is what lets this script plug directly into a
CI pipeline — a pull request that regresses faithfulness below your threshold fails the build,
the same way a broken unit test would, rather than shipping a silent quality regression to
production.

## Running this on a schedule matters too

Beyond CI, running the harness on a schedule (nightly, weekly) against your live index catches
drift that isn't tied to a code change at all — a source document quietly going stale, or an
upstream embedding API changing behavior. Evaluation isn't a one-time launch gate; it's an
ongoing signal, the same way you'd monitor any other production system.
""",
                    "examples": [
                        {
                            "title": "A failed threshold check blocking a bad deploy",
                            "code": (
                                "report = run_eval_harness(\"./eval_set.json\", retriever, reranker, llm, judge_llm)\n"
                                "result = check_thresholds(report)\n"
                                "print(result)\n"
                                "# {'passed': False, 'failures': {'faithfulness': 0.82}}\n"
                                "# A chunking change dropped faithfulness below the 0.90 threshold --\n"
                                "# caught before it reached production"
                            ),
                            "explanation": "This is exactly the kind of regression a manual eyeball check would likely miss, but a numeric threshold catches automatically.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Run the harness twice against two slightly different chunk_size configurations and use compare_to_previous to report which metrics improved or regressed.",
                            "difficulty": "hard",
                            "hint": "Rebuild your index with a different chunk_size between the two harness runs.",
                        },
                        {
                            "prompt": "Set your own THRESHOLDS dict based on a baseline run of your current pipeline, choosing values that would catch a meaningful regression without failing on normal noise.",
                            "difficulty": "medium",
                            "hint": "A common approach is baseline minus one standard deviation across a few repeated baseline runs.",
                        },
                        {
                            "prompt": "Describe how you would schedule this harness to run nightly against a live production index, and what you'd do when it fails outside of a deploy (no recent code change).",
                            "difficulty": "medium",
                            "hint": "Consider source document staleness, embedding API changes, or index corruption as non-code-change causes of regression.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "RAGAS: evaluating a RAG pipeline end to end",
                            "url": "https://docs.ragas.io/en/stable/getstarted/rag_eval/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "evaluation", "weight": 0.8}, {"slug": "rag", "weight": 0.5}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "advanced-rag",
            "title": "Advanced RAG",
            "description": "Techniques that go beyond the standard pipeline: transforming queries before retrieval and letting the system self-correct.",
            "order_index": 14,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "query-transformation-techniques",
                    "title": "Query Transformation Techniques",
                    "description": "Rewrite, expand, or hypothesize before retrieval to improve recall on poorly-phrased or ambiguous queries.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain the HyDE (Hypothetical Document Embeddings) technique and why it works",
                        "Describe multi-query retrieval and how it differs from simple query expansion",
                        "Implement query decomposition for multi-part questions",
                        "Recognize when query transformation adds meaningful value versus unnecessary cost",
                    ],
                    "content_markdown": """
## Why this matters

Sometimes the bottleneck in a RAG system isn't retrieval, reranking, or generation — it's the
raw user query itself. A short, ambiguous, or oddly-phrased query can embed poorly even when
the corpus contains a perfect answer. Query transformation techniques rewrite the query before
it ever reaches retrieval.

## HyDE: Hypothetical Document Embeddings

HyDE's insight is almost backwards at first glance: instead of embedding the user's question
directly, ask an LLM to *hypothesize what a good answer would look like*, and embed that
hypothetical answer instead. A generated answer, even if not perfectly accurate, tends to use
vocabulary and phrasing closer to the actual source documents than a short question does.

```python
def hyde_retrieve(query: str, retriever, llm, top_k: int = 10) -> list:
    hypothetical_prompt = f"Write a short, plausible passage that would answer this question:\\n{query}"
    hypothetical_answer = llm.generate(hypothetical_prompt, temperature=0.3)
    return retriever.retrieve(hypothetical_answer, top_k=top_k)
```

This works especially well when the user's query is much shorter or differently-worded than how
the answer is actually phrased in your source documents — for example, a terse query like
"cancel fee?" versus a document written in full sentences about "early termination charges."

## Multi-query retrieval

Rather than betting on one rewritten query, multi-query retrieval generates several different
phrasings and retrieves for each, merging the results — similar to the query expansion pattern
from the Retrieval module, but typically generating more diverse reformulations, including
different levels of specificity and different assumed contexts.

```python
def multi_query_retrieve(query: str, retriever, llm, top_k: int = 10) -> list:
    prompt = f"Generate 4 different ways to ask this same question, one per line:\\n{query}"
    variants = [line.strip() for line in llm.generate(prompt).split("\\n") if line.strip()]

    all_results, seen = [], set()
    for variant in [query] + variants:
        for r in retriever.retrieve(variant, top_k=top_k):
            if r.chunk_id not in seen:
                seen.add(r.chunk_id)
                all_results.append(r)
    return reciprocal_rank_fusion([retriever.retrieve(v, top_k=top_k) for v in [query] + variants])[:top_k]
```

## Query decomposition for multi-part questions

Some questions genuinely require multiple separate lookups: "What's the refund window, and does
it differ for international orders?" is really two questions. Answering it well means retrieving
for each sub-question separately rather than hoping one embedding captures both.

```python
def decompose_query(query: str, llm) -> list[str]:
    prompt = f"If this question has multiple distinct parts, list each part as a separate question, one per line. If it's a single question, return it unchanged.\\n\\n{query}"
    response = llm.generate(prompt, temperature=0.0)
    return [line.strip() for line in response.split("\\n") if line.strip()]

def decomposed_retrieve(query: str, retriever, llm, top_k_per_part: int = 5) -> list:
    sub_queries = decompose_query(query, llm)
    results = []
    for sub_q in sub_queries:
        results.extend(retriever.retrieve(sub_q, top_k=top_k_per_part))
    return results
```

## When transformation earns its cost

Every technique in this lesson adds at least one extra LLM call before retrieval even starts —
real latency and cost on every query. Reserve them for query patterns you've actually observed
causing retrieval failures (via the evaluation harness from the previous module), rather than
applying them universally. A well-phrased, specific query rarely benefits from HyDE or
decomposition and just pays the extra latency for nothing.
""",
                    "examples": [
                        {
                            "title": "HyDE closing a vocabulary gap",
                            "code": (
                                "query = \"can I get my money back\"\n"
                                "# Direct embedding may under-match a document written as:\n"
                                "# 'Refund requests are honored within thirty (30) calendar days...'\n"
                                "# A HyDE hypothetical answer like 'Yes, refunds are available within\n"
                                "# 30 days of purchase...' uses much closer vocabulary to that document,\n"
                                "# improving the odds of a strong match"
                            ),
                            "explanation": "HyDE's benefit comes specifically from vocabulary and phrasing alignment, not from the hypothetical answer being factually correct.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement hyde_retrieve and compare its top-5 results against plain retrieval for 3 short, terse queries against your corpus.",
                            "difficulty": "medium",
                            "hint": "Terse queries like 'cancel fee?' or 'shipping cost?' are good test cases for HyDE's benefit.",
                        },
                        {
                            "prompt": "Write a decompose_query test case with a genuinely two-part question and confirm the function returns two separate sub-questions rather than one.",
                            "difficulty": "easy",
                            "hint": "Use a question with an explicit 'and' joining two distinct asks.",
                        },
                        {
                            "prompt": "Estimate the added latency of HyDE (one extra LLM generation call) for a system with a 300ms average generation time, and discuss whether that cost is justified for a high-traffic, latency-sensitive product.",
                            "difficulty": "medium",
                            "hint": "HyDE roughly doubles the number of LLM calls per query -- one for the hypothetical answer, one for the final generation.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Precise Zero-Shot Dense Retrieval without Relevance Labels (HyDE paper)",
                            "url": "https://arxiv.org/abs/2212.10496",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "rag", "weight": 1.0}, {"slug": "retrieval", "weight": 0.4}],
                },
                {
                    "slug": "agentic-rag-and-self-correction",
                    "title": "Agentic RAG and Self-Correction",
                    "description": "Let the system decide when to retrieve again, critique its own retrieval, and correct course before answering.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain how agentic RAG differs from the fixed, linear pipeline built earlier in this course",
                        "Describe the Self-RAG and Corrective RAG patterns at a conceptual level",
                        "Implement a simple iterative retrieval loop with a stopping condition",
                        "Recognize the reliability and cost tradeoffs of adding agentic behavior to RAG",
                    ],
                    "content_markdown": """
## Why this matters

Everything built so far in this course follows one fixed path: retrieve once, generate once.
Agentic RAG breaks that rigidity — the system can decide retrieval wasn't good enough, retrieve
again with a different strategy, or even conclude no good answer exists, before committing to a
final response. This lesson previews ideas the AI Agents Fundamentals course covers in much
more depth.

## Why a fixed pipeline sometimes isn't enough

A single retrieve-then-generate pass assumes the first retrieval attempt was good enough. But
some questions need iterative investigation: an initial retrieval might surface a document that
references *another* document the system also needs to check, or the first retrieval attempt
might simply miss due to an unlucky query phrasing that a second, reformulated attempt would
catch.

## Self-RAG: the model critiques its own retrieval and generation

Self-RAG trains or prompts a model to interleave generation with self-assessment: after
retrieving, it judges whether the retrieved content is actually relevant; after generating, it
judges whether the answer is well-supported — retrying steps that fail these checks.

```python
def self_rag_answer(query: str, retriever, llm, max_attempts: int = 2) -> dict:
    for attempt in range(max_attempts):
        results = retriever.retrieve(query, top_k=10)
        relevance_check = llm.generate(
            f"Do these retrieved passages contain information to answer '{query}'? Answer YES or NO.\\n\\n{format_context(results)}"
        )
        if "YES" in relevance_check.upper():
            answer = llm.generate(build_prompt(query, format_context(results)))
            return {"answer": answer, "attempts": attempt + 1, "sources": results}
        query = llm.generate(f"Rewrite this question to be more specific or use different terms: {query}")
    return {"answer": "I could not find sufficient information to answer this confidently.", "attempts": max_attempts, "sources": []}
```

## Corrective RAG: fixing retrieval before it reaches generation

Corrective RAG (CRAG) focuses specifically on grading retrieval quality and taking a corrective
action — expanding the search, trying a different retrieval strategy, or falling back to a
broader web/knowledge source — before generation ever runs, rather than discovering the problem
only after a bad answer is produced.

```python
def corrective_retrieve(query: str, retriever, llm, top_k: int = 10) -> list:
    results = retriever.retrieve(query, top_k=top_k)
    grade_prompt = f"Rate the relevance of these passages to the query '{query}' as HIGH, MEDIUM, or LOW.\\n\\n{format_context(results)}"
    grade = llm.generate(grade_prompt).strip().upper()

    if grade == "LOW":
        expanded_query = llm.generate(f"Generate a broader search query for: {query}")
        results = retriever.retrieve(expanded_query, top_k=top_k * 2)
    return results
```

## A simple iterative retrieval loop with a stopping condition

```python
def iterative_rag(query: str, retriever, llm, max_iterations: int = 3, confidence_threshold: float = 0.8) -> dict:
    accumulated_context = []
    current_query = query

    for iteration in range(max_iterations):
        results = retriever.retrieve(current_query, top_k=5)
        accumulated_context.extend(results)

        confidence = estimate_answer_confidence(query, accumulated_context, llm)
        if confidence >= confidence_threshold:
            break
        current_query = llm.generate(f"What additional information is needed to fully answer '{query}' given what we know so far?")

    answer = llm.generate(build_prompt(query, format_context(accumulated_context)))
    return {"answer": answer, "iterations": iteration + 1, "sources": accumulated_context}
```

The stopping condition (`confidence_threshold` or `max_iterations`) is essential — without it,
an agentic RAG loop can retrieve indefinitely on a question that has no good answer in the
corpus, burning cost with no improvement in outcome.

## The reliability and cost tradeoff

Agentic RAG techniques trade predictable, single-pass latency and cost for potentially better
answers on hard queries — at the cost of variable latency (some queries take one pass, others
take three), higher average cost, and new failure modes like infinite-seeming retry loops if
stopping conditions are poorly tuned. Reserve agentic patterns for the subset of queries where
your evaluation harness shows the fixed pipeline genuinely struggles, rather than applying them
universally — the same discipline as reranking and query transformation before it. This
tradeoff between reliability and capability is a central theme you'll return to throughout the
AI Agents Fundamentals course.
""",
                    "examples": [
                        {
                            "title": "A query that benefits from a second retrieval pass",
                            "code": (
                                "query = \"What happens to my data if I cancel during a security incident?\"\n"
                                "# First retrieval: finds general cancellation policy chunks\n"
                                "# Relevance check: MEDIUM -- doesn't address the security incident angle\n"
                                "# Corrective step: broadens query to include 'data retention' and\n"
                                "# 'incident response', retrieving a chunk the first pass missed entirely"
                            ),
                            "explanation": "This is exactly the kind of compound question a single fixed retrieval pass often under-serves, and where corrective retrieval earns its extra cost.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement corrective_retrieve and test it against a query you've deliberately phrased to retrieve poorly on the first attempt, confirming the corrective expansion improves the result.",
                            "difficulty": "hard",
                            "hint": "Pick a query using vocabulary very different from your source documents so the first-pass grade comes back LOW.",
                        },
                        {
                            "prompt": "Explain, using the reliability/cost tradeoff discussed in this lesson, why you would NOT want every production query to go through a 3-iteration agentic RAG loop by default.",
                            "difficulty": "medium",
                            "hint": "Think about average latency and cost multiplication across a high-volume production system.",
                        },
                        {
                            "prompt": "Design a routing rule that sends only a subset of queries through agentic RAG and the rest through the standard fixed pipeline, and justify your routing criteria.",
                            "difficulty": "hard",
                            "hint": "Consider routing based on a fast initial confidence estimate, or query length/complexity heuristics.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Self-RAG: Learning to Retrieve, Generate, and Critique through Self-Reflection",
                            "url": "https://arxiv.org/abs/2310.11511",
                            "resource_type": "paper",
                        },
                        {
                            "title": "Corrective Retrieval Augmented Generation (CRAG paper)",
                            "url": "https://arxiv.org/abs/2401.15884",
                            "resource_type": "paper",
                        },
                    ],
                    "skills": [{"slug": "rag", "weight": 0.9}, {"slug": "agents", "weight": 0.4}],
                },
            ],
        },
    ],
}


COURSE_EXAM = {
    "title": "Retrieval Augmented Generation: Course Assessment",
    "description": "Checks readiness to move into AI Agents Fundamentals by testing the full RAG pipeline: ingestion, chunking, retrieval, hybrid search, reranking, and evaluation.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 40,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "What problem does Retrieval Augmented Generation primarily solve that prompting alone cannot?",
            "options": [
                {"id": "a", "text": "It makes the LLM generate text faster"},
                {"id": "b", "text": "It grounds generation in current, private, or otherwise unavailable data by retrieving it at query time"},
                {"id": "c", "text": "It permanently updates the model's weights with new knowledge"},
                {"id": "d", "text": "It eliminates the need for prompt engineering entirely"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "RAG retrieves relevant, current, or private information at query time and hands it to the model as context, closing the knowledge-cutoff and hallucination gaps that prompting alone cannot fix.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "rag",
        },
        {
            "question_type": "mcq",
            "prompt": "Why does fixed-size character chunking risk hurting retrieval quality compared to recursive character chunking?",
            "options": [
                {"id": "a", "text": "It is always slower to compute"},
                {"id": "b", "text": "It can cut sentences or key facts in half at an arbitrary character offset, regardless of meaning"},
                {"id": "c", "text": "It cannot be used with any embedding model"},
                {"id": "d", "text": "It only works on Markdown files"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Fixed-size chunking has no awareness of sentence or paragraph boundaries, so it can split the exact fact a query is looking for across two separate chunks.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "chunking",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are legitimate reasons to increase chunk overlap? (Select all that apply.)",
            "options": [
                {"id": "a", "text": "It preserves context that would otherwise be lost right at a chunk boundary"},
                {"id": "b", "text": "It guarantees zero increase in index size"},
                {"id": "c", "text": "It reduces the chance a sentence referencing earlier context loses that context entirely"},
                {"id": "d", "text": "It eliminates the need for chunking strategy decisions altogether"},
            ],
            "correct_answer": {"choices": ["a", "c"]},
            "explanation": "Overlap helps preserve cross-boundary context, but it comes at the real cost of a larger index (ruling out b), and it doesn't remove the need to choose a sensible chunking strategy (ruling out d).",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "chunking",
        },
        {
            "question_type": "mcq",
            "prompt": "A RAG system retrieves the wrong chunks for a query, and you confirm by manual search that the correct chunk exists somewhere in the corpus but never appears in the top-k results. What kind of problem is this?",
            "options": [
                {"id": "a", "text": "A precision problem"},
                {"id": "b", "text": "A recall problem"},
                {"id": "c", "text": "A generation faithfulness problem"},
                {"id": "d", "text": "A citation formatting problem"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "If the correct chunk exists but was never retrieved into the top-k, that's a recall failure -- the fix lies in chunking, embedding model, k, or query transformation, not in reranking or generation.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "mcq",
            "prompt": "Why can't raw BM25 scores and raw cosine similarity scores simply be averaged to combine keyword and vector search results?",
            "options": [
                {"id": "a", "text": "BM25 and cosine similarity measure completely unrelated things and cannot be combined at all"},
                {"id": "b", "text": "The two scores live on very different, incompatible scales, so a naive average would be dominated by whichever score happens to be numerically larger"},
                {"id": "c", "text": "Averaging scores is computationally too expensive to run at query time"},
                {"id": "d", "text": "Cosine similarity is always higher than BM25, so averaging always favors vector search"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Cosine similarity is bounded (roughly 0-1), while BM25 is unbounded and corpus-dependent -- naively averaging lets whichever score has the larger scale dominate the combined ranking, which is why rank-based fusion methods like RRF are used instead.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain how Reciprocal Rank Fusion (RRF) avoids the score-scale mismatch problem between BM25 and vector similarity.",
            "options": [],
            "correct_answer": {
                "expected": "RRF ignores the raw scores entirely and instead computes a combined score based only on each result's rank position in each list, using the formula sum of 1/(k + rank). Because it only ever looks at ranks, not raw score magnitudes, the scale of the underlying scores never matters.",
                "keywords": ["rank position", "not raw scores", "1/(k+rank)", "scale-independent"],
            },
            "explanation": "RRF's core design choice is to discard raw scores and work entirely from rank order, which sidesteps the scale-mismatch problem discussed in the Hybrid Search module.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "mcq",
            "prompt": "Why can't a cross-encoder reranker simply replace vector search for retrieval across an entire large corpus?",
            "options": [
                {"id": "a", "text": "Cross-encoders are less accurate than bi-encoder embedding models"},
                {"id": "b", "text": "Cross-encoders require a joint forward pass per query-document pair and cannot be precomputed, making them far too slow to run over millions of documents per query"},
                {"id": "c", "text": "Cross-encoders only work with keyword search, not semantic search"},
                {"id": "d", "text": "Cross-encoders cannot process text longer than a single sentence"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Cross-encoders score a query and document together, so unlike bi-encoder embeddings, their scores can't be precomputed and reused -- making them accurate but far too slow to run against an entire corpus, hence the retrieve-then-rerank pattern.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "reranking",
        },
        {
            "question_type": "scenario",
            "prompt": "Your RAG system's evaluation harness shows recall@10 of 0.92 (the right chunk is almost always retrieved) but precision@5 of 0.45 and MRR of 0.31 (the right chunk is often present but buried in the middle of the result list). What is the single most targeted improvement to try first, and why?",
            "options": [],
            "correct_answer": {
                "expected": "Add a reranking step. High recall shows the right chunk is being found by retrieval, so the problem isn't chunking or the embedding model -- it's that the initial ranking doesn't place the right chunk near the top. A cross-encoder reranker is specifically designed to re-score a candidate set for more precise ranking, which directly targets low precision@5 and low MRR without needing to touch the retrieval stage.",
                "keywords": ["reranking", "recall is fine", "ranking problem", "cross-encoder", "precision"],
            },
            "explanation": "This is the canonical 'high recall, low precision/MRR' pattern from the RAG Evaluation module that specifically points to reranking as the fix, rather than changes to chunking or the embedding model.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "reranking",
        },
        {
            "question_type": "mcq",
            "prompt": "In a multi-tenant RAG product, why is metadata-based tenant filtering a security requirement rather than just a quality feature?",
            "options": [
                {"id": "a", "text": "Without it, a query from one tenant could retrieve and expose another tenant's private documents purely because they're semantically similar"},
                {"id": "b", "text": "It has no security implications, only affects result ordering"},
                {"id": "c", "text": "It only matters for performance, not for data isolation"},
                {"id": "d", "text": "Vector databases automatically isolate tenants without any filtering configuration"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Without tenant filtering, semantic similarity alone provides no isolation -- a query could surface another tenant's documents simply because they're topically related, which is a data leak, not just a quality issue.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "rag",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is post-filtering (retrieve top-k first, then discard results that don't match a metadata filter) riskier than native pre-filtering supported by most modern vector databases?",
            "options": [
                {"id": "a", "text": "Post-filtering is always slower regardless of dataset size"},
                {"id": "b", "text": "Post-filtering can return fewer than k results, or even zero, if none of the retrieved candidates happen to satisfy the filter, even though matching documents exist elsewhere in the index"},
                {"id": "c", "text": "Post-filtering cannot be implemented in Python"},
                {"id": "d", "text": "Post-filtering only works with keyword search, not vector search"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Because post-filtering discards results after a fixed-size top-k search, it can under-return results if the filter happens to exclude most or all of the retrieved candidate set -- native pre-filtering avoids this by searching only within the allowed subset.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "rag",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function `recall_at_k(retrieved_ids, relevant_ids)` that takes two sets of chunk IDs and returns the fraction of relevant_ids that appear in retrieved_ids, returning 0.0 if relevant_ids is empty.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Returns len(retrieved_ids & relevant_ids) / len(relevant_ids) as a float, or 0.0 when relevant_ids is empty, correctly handling sets of any size.",
                "sample_solution": "def recall_at_k(retrieved_ids: set, relevant_ids: set) -> float:\n    if not relevant_ids:\n        return 0.0\n    return len(retrieved_ids & relevant_ids) / len(relevant_ids)",
            },
            "explanation": "This is the canonical recall@k implementation taught in the RAG Evaluation module: the fraction of truly relevant chunks that were successfully retrieved.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "rag",
        },
        {
            "question_type": "mcq",
            "prompt": "What does the faithfulness metric measure in RAG evaluation, and how does it differ from answer relevance?",
            "options": [
                {"id": "a", "text": "Faithfulness measures whether claims in the answer are supported by the retrieved context; relevance measures whether the answer actually addresses the question asked -- a system can score high on one and low on the other"},
                {"id": "b", "text": "Faithfulness and relevance measure the exact same thing and are interchangeable"},
                {"id": "c", "text": "Faithfulness measures retrieval quality, not generation quality"},
                {"id": "d", "text": "Relevance can only be measured by human annotators, never by an LLM judge"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Faithfulness and relevance are independent axes: an answer can be fully supported by context (faithful) while completely failing to address the actual question (irrelevant), which is exactly why both must be tracked separately.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "rag",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the core idea behind HyDE (Hypothetical Document Embeddings)?",
            "options": [
                {"id": "a", "text": "Embed the user's literal query text and nothing else"},
                {"id": "b", "text": "Generate a hypothetical answer to the query with an LLM, then embed that hypothetical answer instead of the raw query, since it tends to use vocabulary closer to real source documents"},
                {"id": "c", "text": "Skip embeddings entirely and use only keyword search"},
                {"id": "d", "text": "Always retrieve the single most recent document regardless of the query"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "HyDE embeds a generated hypothetical answer rather than the raw query, because the hypothetical answer's phrasing tends to be closer to how the true answer is written in the actual source documents, improving match quality especially for terse or oddly-phrased queries.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "rag",
        },
        {
            "question_type": "scenario",
            "prompt": "You are deciding whether to add an agentic, iterative retrieval loop (like corrective RAG) to a high-traffic, latency-sensitive customer support chatbot. Your evaluation harness shows the current fixed pipeline already achieves recall@10 of 0.95 and faithfulness of 0.93. Should you add the agentic loop? Justify your answer.",
            "options": [],
            "correct_answer": {
                "expected": "Likely not, or only for a narrow subset of queries. The evaluation numbers show the fixed pipeline is already performing well on both retrieval and faithfulness, so an agentic loop would add latency and cost (extra LLM calls per query, variable response time) without a clear quality problem to fix. Agentic techniques are best reserved for query patterns where evaluation shows the fixed pipeline genuinely struggles, not applied universally, especially in a latency-sensitive product.",
                "keywords": ["already performing well", "added latency/cost", "not universally", "reserve for struggling queries", "measure first"],
            },
            "explanation": "This tests the reliability/cost tradeoff from the Advanced RAG module: agentic techniques should be adopted based on measured need, not by default, especially when latency is a hard product constraint.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "rag",
        },
    ],
}
