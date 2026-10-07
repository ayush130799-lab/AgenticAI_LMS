"""
Course 3: LLM Fundamentals
Seed content for the Agentic AI LMS. See content/seed/SCHEMA.md for the
field-by-field contract this file must follow.
"""

COURSE = {
    "slug": "llm-fundamentals",
    "title": "LLM Fundamentals",
    "subtitle": "How large language models actually work, from tokens to the API call.",
    "description": (
        "A practitioner's introduction to large language models: how text becomes tokens, how "
        "transformers turn tokens into predictions, how sampling turns predictions into generated "
        "text, and how to actually call an LLM API in production. This course trades hype for "
        "mechanism, so that every prompt you write in Course 4 onward is grounded in an accurate "
        "mental model of what's happening underneath it."
    ),
    "learning_outcomes": [
        "Explain how LLMs generate text one token at a time from learned probability distributions",
        "Describe tokenization and its practical impact on cost and context limits",
        "Explain the transformer architecture and self-attention at a conceptual level",
        "Control generation behavior using temperature and sampling parameters",
        "Structure conversations using system, user, and assistant message roles",
        "Call a real LLM API, including streaming responses, using Python",
        "Recognize hallucinations and other model limitations, and mitigate them appropriately",
    ],
    "order_index": 3,
    "estimated_hours": 16,
    "level": "beginner",
    "icon": "message-circle",
    "modules": [
        {
            "slug": "what-are-llms",
            "title": "What are LLMs?",
            "description": "Grounding large language models in the older idea of a language model, and the core mechanism behind text generation.",
            "order_index": 1,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "from-language-models-to-llms",
                    "title": "From Language Models to LLMs",
                    "description": "What a language model predicts, and what changed to make today's LLMs so capable.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define a language model as a system that predicts the next token given context",
                        "Explain what makes an LLM 'large' beyond just parameter count",
                        "Identify the role of scale (data, parameters, compute) in modern LLM capability",
                        "Distinguish a base model from an instruction-tuned/chat model",
                    ],
                    "content_markdown": """
## Why this matters

Every course from here to the end of this program assumes you have an accurate mental model of what
an LLM fundamentally does. Get this lesson wrong and prompt engineering, RAG, and agents will all
feel like folklore instead of engineering — you'll be following recipes without understanding why
they work, which falls apart the moment you hit an unfamiliar situation.

## The core idea: predicting the next token

A language model is, at its core, a system trained to answer one question extremely well: "given
the text so far, what token is most likely to come next?"

```python
# Conceptual illustration, not real model internals
context = "The capital of France is"
next_token_probabilities = {
    "Paris": 0.92,
    "a": 0.03,
    "located": 0.02,
    "the": 0.01,
    # ... probability mass spread across the model's entire vocabulary
}
```

That's it. That's the whole trick, repeated one token at a time. Generate a probability distribution
over the vocabulary, pick a token (more on exactly how in the Temperature and Sampling module),
append it to the context, and repeat. Everything you'll learn in this program about prompting,
context, and agent behavior is downstream of this one mechanism.

## This idea long predates modern LLMs

Statistical language models existed decades before ChatGPT — simple ones counted how often word
pairs or triples appeared together in a corpus and used those frequencies to predict the next word.
Those models could generate locally plausible but globally incoherent text; they had no way to use
information from more than a couple of words back. What's genuinely new about LLMs isn't the "predict
the next token" idea — it's the combination of a much better architecture (the transformer, covered
in a later module) and a massive increase in scale.

## What "large" actually means

"Large" language model refers to a combination of factors, not just one number:

- **Parameters** — the learned numeric weights inside the model; modern LLMs have from billions to
  well over a hundred billion.
- **Training data** — a huge and diverse corpus of text, often measured in trillions of tokens.
- **Compute** — the sheer amount of processing used to train the model, often thousands of GPUs
  running for weeks or months.

Scaling all three together produced qualitative jumps in capability that smaller models simply don't
exhibit — abilities like following multi-step instructions, writing working code, or reasoning
through a novel problem tend to emerge more reliably only past certain scale thresholds.

## Base models vs instruction-tuned (chat) models

A **base model** is trained purely to predict the next token across its training corpus — ask it a
question and it might just continue the text as if it were autocompleting a random document
containing that question, rather than actually answering it helpfully. An **instruction-tuned** (or
"chat") model goes through additional training specifically to behave like a helpful assistant that
follows instructions, refuses harmful requests, and responds in a conversational format. Every model
you'll interact with through an API in this program — Claude included — is instruction-tuned. This
distinction matters because it explains *why* wrapping input in a "system/user/assistant" structure
(covered later in this course) reliably shapes model behavior: the model was specifically trained to
respond to that structure.

## Looking ahead

The next lesson walks through exactly how generation proceeds one token at a time in practice, and
the Tokens module right after formalizes what a "token" actually is — the atomic unit everything in
this course operates on.
""",
                    "examples": [
                        {
                            "title": "Example: Next-token prediction as a dictionary of probabilities",
                            "code": "context = \"My favorite programming language is\"\n# A real model outputs a probability distribution over its ENTIRE vocabulary\n# (tens of thousands of tokens); this is a drastically simplified illustration.\nlikely_next_tokens = {\"Python\": 0.35, \"JavaScript\": 0.15, \"Rust\": 0.08, \"...\": 0.42}\nmost_likely = max(likely_next_tokens, key=likely_next_tokens.get)\nprint(most_likely)",
                            "explanation": "Shows next-token prediction as picking the highest-probability entry from a distribution, the conceptual core of what every LLM call does at each generation step.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "In your own words, write a 2-3 sentence explanation of the difference between a base model and an instruction-tuned model, using an example of how each might respond to 'What is the capital of France?'",
                            "difficulty": "easy",
                            "hint": "A base model might continue the sentence as if completing a quiz document; an instruction-tuned model answers directly and conversationally.",
                        },
                        {
                            "prompt": "List the three factors that combine to make a language model 'large,' and briefly explain why scaling all three together (not just one) mattered for modern LLM capabilities.",
                            "difficulty": "medium",
                            "hint": "Consider that a model with huge data but tiny parameter count, or huge parameters but tiny data, would each be limited in different ways.",
                        },
                        {
                            "prompt": "Explain why a simple word-frequency-counting language model from decades ago could generate locally plausible but globally incoherent text, connecting this to the 'next-token prediction' framing from this lesson.",
                            "difficulty": "medium",
                            "hint": "Think about how far back in the context such a model could actually 'see' when making its prediction.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Intro to Claude", "url": "https://docs.anthropic.com/en/docs/intro-to-claude", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "how-llms-generate-text",
                    "title": "How LLMs Generate Text",
                    "description": "The autoregressive loop that turns a prompt into a full response, one token at a time.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Describe the autoregressive generation loop step by step",
                        "Explain why generation is inherently sequential",
                        "Identify what a stop condition is and why generation needs one",
                        "Connect this loop to observed LLM behaviors like streaming output",
                    ],
                    "content_markdown": """
## Why this matters

When you watch an LLM's response appear word by word in a chat interface, you're watching the
autoregressive loop happen live. Understanding this loop explains several things you'll rely on
throughout this program: why streaming is possible at all, why a model can't "go back and revise" an
earlier part of its own answer mid-generation, and why longer generations take proportionally longer.

## The autoregressive generation loop

"Autoregressive" means the model's own previous outputs become part of the input for predicting the
next output. Concretely, the loop looks like this:

```python
def generate(prompt, max_tokens=50):
    tokens = tokenize(prompt)  # tokenize() covered fully in the next module
    generated = []

    for _ in range(max_tokens):
        next_token = model_predict_next_token(tokens + generated)
        if next_token == STOP_TOKEN:
            break
        generated.append(next_token)

    return detokenize(generated)
```

At every single step, the model looks at the entire sequence so far (original prompt plus everything
it has generated up to that point) and predicts just one more token. That new token gets appended,
and the whole sequence — now one token longer — is fed back in for the next prediction. This repeats
until a stop condition is hit.

## Why generation is inherently sequential

Because each new token depends on every token generated before it, an LLM cannot generate token 50
before it has generated token 49 — there's a hard sequential dependency baked into the mechanism
itself. This is exactly why response latency scales with output length: a 500-token response
genuinely requires roughly 500 sequential prediction steps, not one big computation. It's also why
parallelizing across many *separate* requests (as you did with `asyncio.gather` in Course 1) helps
throughput, while a single response's generation itself can't be similarly parallelized.

## Stop conditions

Generation has to know when to stop. Common stop conditions:

- The model predicts a special **end-of-turn** token it was trained to emit when its response is
  complete.
- The response hits a **max_tokens** limit you configured, cutting it off even mid-thought.
- The response hits a **custom stop sequence** you specified (e.g., stop as soon as the model
  generates `"\\n\\nHuman:"`, useful for preventing a model from fabricating the other side of a
  conversation).

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    stop_sequences=["END"],
    messages=[{"role": "user", "content": "List 3 fruits, then write END."}],
)
```

Knowing which stop condition ended a response (available in the API response's `stop_reason` field)
matters in practice — a response that stopped because it hit `max_tokens` is truncated mid-thought
and should usually be handled differently from one that stopped naturally.

## Why streaming is possible

Because tokens are generated one at a time in sequence, an API can send each token to you the
instant it's produced, rather than waiting for the entire response to finish — this is exactly what
streaming responses (covered later in the LLM APIs module) take advantage of, and it's why streaming
noticeably improves perceived responsiveness for long responses even though the total generation time
doesn't change.

## Looking ahead

The Tokens module immediately following this one formalizes exactly what gets fed into and produced
by each step of this loop, and the Temperature and Sampling module covers precisely how
`model_predict_next_token` chooses among several plausible candidates rather than always picking the
single most likely token.
""",
                    "examples": [
                        {
                            "title": "Example: Simulating the generation loop with a toy vocabulary",
                            "code": "import random\n\nvocab_after = {\n    \"The\": [\"cat\", \"dog\", \"sky\"],\n    \"cat\": [\"sat\", \"ran\", \"slept\"],\n    \"sat\": [\"on\", \"quietly\", \"STOP\"],\n}\n\ndef toy_generate(start_token, max_steps=5):\n    sequence = [start_token]\n    current = start_token\n    for _ in range(max_steps):\n        options = vocab_after.get(current, [\"STOP\"])\n        next_token = random.choice(options)\n        if next_token == \"STOP\":\n            break\n        sequence.append(next_token)\n        current = next_token\n    return \" \".join(sequence)\n\nprint(toy_generate(\"The\"))",
                            "explanation": "A deliberately tiny, deterministic-vocabulary stand-in for the autoregressive loop, making the step-by-step 'extend the sequence, feed it back in' mechanic concrete without needing a real model.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Trace through the generate() pseudocode in the lesson by hand for a 5-token max_tokens limit, writing out what 'tokens + generated' would contain at each of the 5 iterations, assuming no STOP_TOKEN is hit.",
                            "difficulty": "medium",
                            "hint": "At iteration i, generated should contain i-1 tokens already appended from previous steps.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why a chat UI can start displaying a response before the model has finished generating the entire thing, connecting your answer to the autoregressive loop.",
                            "difficulty": "easy",
                            "hint": "Think about whether the full response needs to exist before the first token can be shown to a user.",
                        },
                        {
                            "prompt": "Describe a real scenario where a response getting cut off by hitting max_tokens (rather than a natural stop) would cause a problem for a downstream agent parsing that response as JSON.",
                            "difficulty": "hard",
                            "hint": "Consider what happens when json.loads() is called on a JSON string that was truncated mid-object.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic API: Messages", "url": "https://docs.anthropic.com/en/api/messages", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "tokens",
            "title": "Tokens",
            "description": "The atomic unit of text an LLM actually operates on, and why it matters for cost, limits, and prompt design.",
            "order_index": 2,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "tokenization-explained",
                    "title": "Tokenization Explained",
                    "description": "How raw text is broken into tokens using subword tokenization, and how to count them yourself.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why LLMs operate on tokens rather than raw characters or whole words",
                        "Describe subword tokenization at a conceptual level",
                        "Count tokens in a piece of text using a real tokenizer",
                        "Predict, roughly, how a word being 'rare' affects its tokenization",
                    ],
                    "content_markdown": """
## Why this matters

Every number you'll care about operationally — API cost, context window usage, response length
limits — is measured in tokens, not words or characters. If your mental model of tokens is fuzzy,
every budget calculation and context-management decision you make for the rest of this program will
be guesswork.

## Why not just use whole words or characters?

Using single characters as the unit keeps the vocabulary tiny but makes sequences extremely long (a
500-word document might be 3,000 characters), which is computationally expensive since transformers'
cost scales with sequence length. Using whole words keeps sequences shorter, but the vocabulary
would need an entry for every distinct word ever seen, including rare names, typos, and words in
other languages — an impractically enormous and still-incomplete vocabulary.

## Subword tokenization: the practical middle ground

Modern LLMs use subword tokenization: common words become a single token, while rare or unusual
words get broken into smaller, more common pieces.

```python
# Conceptual illustration of subword tokenization
tokenize("the")           # -> ["the"]                     1 token, very common word
tokenize("cats")          # -> ["cats"]                     1 token, common word
tokenize("tokenization")  # -> ["token", "ization"]         2 tokens, less common whole word
tokenize("Kwyjibo")       # -> ["K", "wy", "ji", "bo"]      4 tokens, made-up/rare word
```

This means common English words are usually 1 token, moderately common words might be split into 2,
and rare words, typos, or non-English text can fragment into many small tokens — which directly
inflates your token count and cost for that content.

## Counting tokens with a real tokenizer

```python
# Requires: pip install anthropic
import anthropic

client = anthropic.Anthropic()
response = client.messages.count_tokens(
    model="claude-sonnet-5",
    messages=[{"role": "user", "content": "Tokenization is the first step in every LLM pipeline."}],
)
print(response.input_tokens)
```

Anthropic (like other LLM providers) exposes a token-counting endpoint specifically so you can check
costs and context usage *before* sending a real, billed request — a good habit for any code that
constructs prompts dynamically from variable-length user input or retrieved documents.

## A useful rule of thumb

For English text, a common rough estimate is about 4 characters per token, or roughly 0.75 tokens
per word — useful for quick mental math, but never a substitute for actually counting tokens when
precision matters (e.g., right at the edge of a context window limit).

```python
def rough_token_estimate(text):
    return len(text) // 4

print(rough_token_estimate("This is a rough estimate of token count."))
```

## Why this matters for prompt design

Since tokenization isn't uniform across languages and content types — code, non-English text, and
unusual formatting often tokenize less efficiently than plain English prose — the same *meaning*
expressed in different ways can have meaningfully different token costs. This becomes directly
actionable in Course 4 (Prompt Engineering), where concise, well-structured prompts aren't just
stylistically nicer, they measurably reduce cost and leave more room in the context window.

## Looking ahead

The next lesson in this module turns token counts into a concrete cost and context-limit
calculation, and the Context Windows module right after builds directly on the token-counting habit
from this lesson to manage long conversations that would otherwise exceed a model's limit.
""",
                    "examples": [
                        {
                            "title": "Example: Comparing token counts for similar-length but different content",
                            "code": "texts = [\n    \"The quick brown fox jumps over the lazy dog.\",\n    \"def quick_brown_fox(): return jumps_over(lazy_dog)\",\n    \"Kwyjibo Zxcvqp Blorf Trxynn\",\n]\nfor t in texts:\n    print(t, \"-> approx tokens:\", len(t) // 4)",
                            "explanation": "Illustrates (with a rough estimate, since a real tokenizer isn't always available) that code and unusual/made-up words tend to tokenize less efficiently than plain natural-language prose of similar character length.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write the rough_token_estimate(text) function from the lesson and apply it to three sentences of your own, at least one containing unusual or made-up words.",
                            "difficulty": "easy",
                            "hint": "len(text) // 4 is the rule-of-thumb estimator described in the lesson.",
                        },
                        {
                            "prompt": "If you have access to the anthropic Python package, call client.messages.count_tokens on a short and a long paragraph and compare the result to your rough_token_estimate for both.",
                            "difficulty": "medium",
                            "hint": "Compare how close the rough estimate is to the real count -- it should be in the right ballpark but rarely exact.",
                        },
                        {
                            "prompt": "Explain, in 2-3 sentences, why a prompt containing a lot of non-English text or unusual technical jargon might cost more per sentence than an equivalent-length plain English prompt.",
                            "difficulty": "medium",
                            "hint": "Recall that rare or unusual words fragment into more subword tokens than common English words.",
                        },
                    ],
                    "resources": [
                        {"title": "OpenAI: Tokenizer (interactive tool)", "url": "https://platform.openai.com/tokenizer", "resource_type": "tutorial"},
                    ],
                    "skills": [{"slug": "tokens", "weight": 1.0}],
                },
                {
                    "slug": "token-limits-and-cost",
                    "title": "Token Limits and Cost",
                    "description": "How input and output tokens are priced separately, and how to estimate and budget for API cost.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why input and output tokens are typically priced differently",
                        "Estimate the cost of an API call given token counts and a pricing table",
                        "Identify where token costs accumulate silently in agent and RAG systems",
                        "Apply basic strategies to reduce token spend without sacrificing quality",
                    ],
                    "content_markdown": """
## Why this matters

By Course 13 (Production AI), you'll be responsible for keeping an AI system's operating cost under
control. That entire discipline starts here: understanding exactly what you're being charged for and
where costs tend to balloon unnoticed.

## Input tokens vs output tokens

LLM providers typically charge separately for input tokens (everything you send: system prompt,
conversation history, retrieved documents) and output tokens (what the model generates), usually at
different per-token rates, with output tokens typically costing more than input tokens because
generation is more computationally expensive than reading.

```python
def estimate_cost(input_tokens, output_tokens, input_price_per_million, output_price_per_million):
    input_cost = (input_tokens / 1_000_000) * input_price_per_million
    output_cost = (output_tokens / 1_000_000) * output_price_per_million
    return input_cost + output_cost

# Example prices are illustrative; always check current provider pricing pages for real numbers.
cost = estimate_cost(
    input_tokens=1200,
    output_tokens=400,
    input_price_per_million=3.00,
    output_price_per_million=15.00,
)
print(f"${cost:.4f}")
```

## Where costs accumulate silently

- **Conversation history** — in a naive chat loop, every previous turn is resent as input on every
  new turn, so a long conversation's *input* token cost grows with every message, even though the
  user only typed one short new message.
- **RAG context** — retrieved documents injected into a prompt (Course 5) are input tokens; a system
  that retrieves 10 large chunks per query can dwarf the cost of the user's actual question.
- **Agent loops** — a multi-step agent (Course 9) that calls several tools before producing a final
  answer pays input + output token cost at *every* step, not just once, so cost can multiply quickly
  with the number of reasoning/tool-call steps.
- **System prompts** — a large, detailed system prompt gets resent as input tokens on every single
  request in a session, even though its content never changes turn to turn.

```python
def estimate_conversation_cost(turns, system_prompt_tokens, avg_response_tokens, prices):
    total_input = 0
    total_output = 0
    running_history = system_prompt_tokens
    for _ in range(turns):
        total_input += running_history
        total_output += avg_response_tokens
        running_history += avg_response_tokens + 50  # + new user message, roughly
    return estimate_cost(total_input, total_output, *prices)
```

This function makes explicit something easy to miss intuitively: cost in a growing conversation
isn't linear per turn, because each new turn resends the entire growing history as input.

## Strategies to reduce token spend

- **Trim conversation history** — summarize or drop older turns instead of resending the full
  history forever (a technique explored fully in the Context Windows module).
- **Cache stable content** — some providers support prompt caching for content (like a large system
  prompt) that repeats unchanged across requests, avoiding paying full input price for it every time.
- **Retrieve fewer, better documents** — improving retrieval precision (Course 5) so you only inject
  the 3 genuinely relevant chunks instead of 10 mediocre ones directly reduces input cost.
- **Set explicit max_tokens** — bounding output length prevents runaway generations from
  unexpectedly inflating output cost.

## Looking ahead

Course 13's production cost-control lesson builds a real dashboard around exactly the input/output
split and per-step accounting introduced here. Course 9's agent loops are the single biggest
practical source of runaway token cost you'll encounter in this program, precisely because of the
"pay at every step" dynamic described above.
""",
                    "examples": [
                        {
                            "title": "Example: Comparing cost of a short vs a long system prompt across 20 turns",
                            "code": "prices = (3.00, 15.00)  # illustrative input/output price per million tokens\nshort_prompt_cost = estimate_conversation_cost(20, system_prompt_tokens=50, avg_response_tokens=150, prices=prices)\nlong_prompt_cost = estimate_conversation_cost(20, system_prompt_tokens=800, avg_response_tokens=150, prices=prices)\nprint(round(short_prompt_cost, 2), round(long_prompt_cost, 2))",
                            "explanation": "Demonstrates how a bulky system prompt's cost compounds across many turns of a conversation, since it gets resent as input every single turn.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using estimate_cost, compute the cost of a single API call with 5,000 input tokens and 1,000 output tokens at $3/million input and $15/million output tokens.",
                            "difficulty": "easy",
                            "hint": "Plug the numbers directly into the estimate_cost function from the lesson.",
                        },
                        {
                            "prompt": "Using estimate_conversation_cost, compare the total cost of a 10-turn conversation with a 100-token system prompt versus a 1,500-token system prompt, holding everything else constant, and explain the difference in your own words.",
                            "difficulty": "medium",
                            "hint": "The gap should widen noticeably because the larger system prompt is resent as input on every turn.",
                        },
                        {
                            "prompt": "Describe two concrete changes you could make to a RAG-based chatbot to reduce its per-conversation token cost, referencing specific strategies from this lesson.",
                            "difficulty": "medium",
                            "hint": "Consider retrieval precision and conversation history trimming as your two levers.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Pricing", "url": "https://www.anthropic.com/pricing", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "tokens", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "context-windows",
            "title": "Context Windows",
            "description": "The hard limit on how much text a model can consider at once, and how to work within it.",
            "order_index": 3,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "understanding-context-windows",
                    "title": "Understanding Context Windows",
                    "description": "What a context window is, why it's finite, and what happens when you exceed it.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define a context window in terms of total tokens, not characters or messages",
                        "Explain why context windows have a fixed maximum size",
                        "Predict what happens to a request that exceeds the context window",
                        "Distinguish context window size from output length limits",
                    ],
                    "content_markdown": """
## Why this matters

Every RAG system (Course 5), every long agent conversation (Course 9), and every large document
summarization task in this program runs directly into this single hard constraint. Misunderstanding
it produces either confusing API errors or, worse, silently degraded output quality.

## What a context window actually is

A context window is the maximum number of tokens a model can consider at once — the combined total
of everything you send (system prompt, conversation history, retrieved documents) **plus** everything
the model generates in response. It is not measured in characters, words, or messages — always
tokens, from the previous module.

```python
context_window_limit = 200_000  # example limit, check current model docs for real numbers

def fits_in_context(input_tokens, expected_output_tokens, limit=context_window_limit):
    return (input_tokens + expected_output_tokens) <= limit
```

## Why context windows are finite

Transformers (covered in depth in the next module) compute attention between every pair of tokens in
the input, which means the computational and memory cost of processing a sequence grows faster than
linearly as the sequence gets longer. This is a fundamental architectural reason — not an arbitrary
business decision — why every LLM has some maximum sequence length it can process, even though that
maximum has grown dramatically across model generations.

## What happens when you exceed it

Sending a request whose total token count (input) exceeds the context window typically produces an
explicit API error rather than silently truncating your input — providers generally prefer to fail
loudly so you notice and fix the problem, rather than have a model silently ignore part of your
prompt.

```python
try:
    response = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=1024,
        messages=huge_conversation_history,  # exceeds the context window
    )
except Exception as e:
    print(f"Request failed, likely exceeded context window: {e}")
```

In practice, you want to catch this *before* it happens by counting tokens ahead of time (using the
techniques from the Tokens module) and trimming or summarizing content proactively, rather than
relying on the API's error as your only signal.

## Context window vs output length limit

These are two different numbers that are easy to conflate:

- **Context window** — the total budget shared across input + output combined.
- **max_tokens parameter** — a separate setting you control, capping how many tokens the model is
  *allowed* to generate in this particular response, which must fit within whatever context window
  budget remains after your input.

```python
context_window = 200_000
input_tokens = 195_000
max_tokens_you_can_request = context_window - input_tokens  # 5,000, not the model's usual max
```

If your input alone is close to the context window limit, you may need to explicitly lower
`max_tokens` for the response, or the request may fail outright.

## Looking ahead

The next lesson in this module builds a practical conversation-trimming strategy directly on top of
this concept, and Course 5 (RAG) treats the context window as a hard budget constraint that retrieval
quality must respect — you cannot simply keep injecting more and more retrieved documents "to be
safe."
""",
                    "examples": [
                        {
                            "title": "Example: Checking whether a request fits before sending it",
                            "code": "def rough_tokens(text):\n    return len(text) // 4\n\nsystem_prompt = \"You are a helpful assistant.\" * 5\nhistory_text = \"...\" * 5000  # stand-in for a long conversation\n\ntotal_input = rough_tokens(system_prompt) + rough_tokens(history_text)\ncontext_window = 200_000\nrequested_max_tokens = 1024\n\nif total_input + requested_max_tokens > context_window:\n    print(\"Would exceed context window -- trim history before sending\")\nelse:\n    print(\"Safe to send\")",
                            "explanation": "Performs a pre-flight budget check using the rough token estimator, catching an over-budget request before it ever reaches the API.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a function fits_in_context(input_tokens, max_tokens, context_window) that returns True or False, and test it with values that should pass and values that should fail.",
                            "difficulty": "easy",
                            "hint": "The check is simply input_tokens + max_tokens <= context_window.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why the context window limit is fundamentally different from a max_tokens setting, even though both involve 'how much text.'",
                            "difficulty": "medium",
                            "hint": "One is a fixed architectural ceiling shared by input and output together; the other is a per-request choice you make about how much output to allow.",
                        },
                        {
                            "prompt": "Describe a real scenario in a RAG chatbot where failing to check the context window budget before sending a request could cause a production incident, and how you would prevent it.",
                            "difficulty": "hard",
                            "hint": "Consider a query that happens to retrieve an unusually large number of long documents.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Models overview", "url": "https://docs.anthropic.com/en/docs/about-claude/models", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "managing-long-conversations",
                    "title": "Managing Long Conversations",
                    "description": "Practical strategies -- trimming, summarizing, and windowing -- for keeping conversations within the context budget.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement a sliding-window strategy to trim old conversation turns",
                        "Implement a summarization strategy to compress old history",
                        "Compare the tradeoffs of trimming versus summarizing",
                        "Design a hybrid strategy appropriate for a long-running agent",
                    ],
                    "content_markdown": """
## Why this matters

A naive chat loop that resends the entire conversation history forever will eventually exceed the
context window, and will get expensive (per the Token Limits and Cost lesson) long before that. This
lesson gives you concrete, implementable strategies you'll reuse directly when building the memory
system for a long-running agent in Course 9.

## Strategy 1: Sliding window (simple truncation)

Keep only the most recent N messages, dropping older ones entirely.

```python
def sliding_window(history, max_messages=10):
    return history[-max_messages:]

history = [{"role": "user", "content": f"message {i}"} for i in range(20)]
trimmed = sliding_window(history, max_messages=6)
print(len(trimmed))  # 6, only the most recent messages survive
```

Simple and cheap to implement, but it can abruptly lose important context from earlier in the
conversation — a user preference stated in message 2 is completely gone by message 20 under a pure
sliding window.

## Strategy 2: Summarization

Periodically compress older messages into a short summary, keeping recent messages verbatim.

```python
def summarize_old_messages(old_messages, summarize_fn):
    combined_text = "\\n".join(m["content"] for m in old_messages)
    summary = summarize_fn(combined_text)  # in practice, this is itself an LLM call
    return {"role": "system", "content": f"Earlier conversation summary: {summary}"}

def manage_history(history, keep_recent=6, summarize_fn=None):
    if len(history) <= keep_recent:
        return history
    old, recent = history[:-keep_recent], history[-keep_recent:]
    summary_message = summarize_old_messages(old, summarize_fn)
    return [summary_message] + recent
```

Summarization preserves the gist of older context at a fraction of the token cost, at the price of
losing exact wording and detail — and the summarization call itself costs tokens, so it's not free.

## Strategy 3: Token-budget-aware windowing

Rather than a fixed number of messages, trim based on an actual token budget, which is more accurate
since message lengths vary a lot.

```python
def rough_tokens(text):
    return len(text) // 4

def fit_to_budget(history, token_budget):
    kept = []
    used = 0
    for message in reversed(history):  # start from most recent
        cost = rough_tokens(message["content"])
        if used + cost > token_budget:
            break
        kept.append(message)
        used += cost
    return list(reversed(kept))
```

This is closer to what production systems actually do — reason in tokens, not message counts, since
one very long message can silently blow a fixed-message-count budget.

## Choosing a strategy

- Short-lived, simple chatbots: sliding window is often good enough.
- Long-running assistants that need to remember earlier facts (a user's name, stated preferences):
  summarization, or a dedicated memory system (Course 9's Agent Memory module), is worth the extra
  complexity.
- Cost- and limit-sensitive production systems: token-budget-aware windowing, often combined with
  summarization for anything trimmed out.

## Looking ahead

Course 9's Agent Memory module generalizes this exact problem — what to keep, what to compress, what
to discard — into a full short-term/long-term memory architecture. Everything you build there is an
elaboration of the three strategies in this lesson, not a fundamentally different idea.
""",
                    "examples": [
                        {
                            "title": "Example: Combining token-budget windowing with a stand-in summary",
                            "code": "history = [{\"role\": \"user\", \"content\": f\"turn {i} \" * 20} for i in range(30)]\n\ndef fake_summarize(text):\n    return f\"(summary of {len(text)} characters of earlier chat)\"\n\ntrimmed = fit_to_budget(history, token_budget=200)\nprint(len(trimmed), \"messages kept out of\", len(history))",
                            "explanation": "Runs the token-budget-aware windowing function on a synthetic long conversation, showing that far fewer messages survive once real token costs (not message counts) drive the cutoff.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement sliding_window(history, max_messages) and test it on a 15-message synthetic history, confirming only the most recent max_messages entries remain in order.",
                            "difficulty": "easy",
                            "hint": "Python's negative slicing history[-max_messages:] does this in one line.",
                        },
                        {
                            "prompt": "Implement fit_to_budget(history, token_budget) from the lesson and test it with messages of varying lengths, confirming it stops adding messages once the budget would be exceeded.",
                            "difficulty": "medium",
                            "hint": "Iterate from the end of the list backward, accumulating a running token total.",
                        },
                        {
                            "prompt": "Describe, in 3-4 sentences, a hybrid strategy for a customer support agent that needs to remember the user's account ID stated early in a long conversation, while still staying within a token budget for everything else.",
                            "difficulty": "hard",
                            "hint": "Consider extracting and pinning specific important facts (like an account ID) separately from the general sliding-window or summarization logic.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Context windows", "url": "https://docs.anthropic.com/en/docs/build-with-claude/context-windows", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "transformers",
            "title": "Transformers",
            "description": "The architecture underlying essentially every modern LLM, and the self-attention mechanism at its core.",
            "order_index": 4,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "the-transformer-architecture",
                    "title": "The Transformer Architecture",
                    "description": "A conceptual tour of the transformer, from embeddings in to probabilities out.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Name the major components of a transformer at a conceptual level",
                        "Explain why transformers replaced earlier sequential architectures like RNNs",
                        "Describe the role of positional encoding",
                        "Connect the transformer's structure to the neural network fundamentals from Course 2",
                    ],
                    "content_markdown": """
## Why this matters

Every capability and every limitation you'll encounter with LLMs traces back to this architecture.
You don't need to be able to implement a transformer from scratch, but a solid conceptual model of
what it's doing explains, later in this course, *why* hallucinations happen, *why* context windows
are finite, and *why* prompt structure (Course 4) has such an outsized effect on output quality.

## Building on Course 2's neural network fundamentals

Recall from Course 2 that a neural network is layers of simple units, each computing a weighted sum
of its inputs passed through a non-linear activation, with weights learned via gradient descent and
backpropagation. A transformer is a specific, carefully designed arrangement of exactly that kind of
layer, with one crucial addition: a mechanism for each token to look at every other token in the
sequence before deciding what it "means" in context — that mechanism is self-attention, covered in
depth in the next lesson.

## Why transformers replaced earlier architectures

Before transformers, the dominant architecture for sequence data was the recurrent neural network
(RNN), which processes tokens one at a time in strict order, carrying forward a "memory" state from
one step to the next. RNNs have two major problems: they're inherently sequential (you can't process
token 10 before token 9, which makes them slow to train on modern parallel hardware), and their
fixed-size memory state tends to "forget" information from much earlier in a long sequence. The
transformer, introduced in the 2017 paper "Attention Is All You Need," replaced sequential recurrence
with self-attention, allowing every token to directly access every other token's information
regardless of distance, and allowing far more of the computation to run in parallel during training.

## The major components, at a conceptual level

```
Input text
    -> Tokenization (Tokens module)
    -> Token embeddings (numeric vectors per token, echoing Course 2's Embeddings Introduction)
    -> + Positional encoding (adds information about EACH token's position in the sequence)
    -> Stack of transformer layers, each containing:
         - Self-attention (tokens gather relevant information from other tokens)
         - Feed-forward network (further processes each token's representation)
    -> Output layer producing a probability distribution over the next token
```

## Why positional encoding is necessary

Self-attention, on its own, treats the input as an unordered set of tokens — it has no inherent
sense of "this word comes before that word." Positional encoding injects information about each
token's position into its representation before it enters the attention layers, so the model can
still distinguish "the dog bit the man" from "the man bit the dog," which use identical tokens in a
different order with a very different meaning.

```python
# Conceptual illustration only, real positional encodings use fixed or learned mathematical patterns
def add_position_info(token_embedding, position):
    return [x + 0.001 * position for x in token_embedding]  # crude illustrative nudge only
```

## Stacking layers

Just as Course 2's neural network lesson described early layers learning simple patterns and later
layers building more abstract ones, a transformer stacks many self-attention + feed-forward layers on
top of each other — early layers tend to capture more local, syntactic patterns, while later layers
build up more abstract, semantic representations that ultimately support the next-token prediction at
the output.

## Looking ahead

The next lesson zooms all the way into self-attention itself — the specific mechanism that lets a
transformer decide, for each token, which other tokens in the sequence are most relevant to
understanding it. That mechanism is the single most important idea to walk away from this module
with.
""",
                    "examples": [
                        {
                            "title": "Example: The conceptual pipeline as a sequence of function calls",
                            "code": "def transformer_forward_pass(text):\n    tokens = tokenize(text)\n    embeddings = embed(tokens)               # numeric vectors, Course 2 concept\n    embeddings = add_positional_encoding(embeddings)\n    for layer in transformer_layers:\n        embeddings = layer.self_attention(embeddings)\n        embeddings = layer.feed_forward(embeddings)\n    return output_layer(embeddings)           # probability distribution over next token\n\n# This is illustrative structure, not runnable code -- real transformer internals\n# are implemented in frameworks like PyTorch, not plain Python loops.",
                            "explanation": "Lays out the conceptual pipeline from the lesson as pseudocode function calls, making the ordering of operations concrete even though none of these functions actually exist as written.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List the major components of a transformer in the order data flows through them, from raw text input to next-token probability output.",
                            "difficulty": "easy",
                            "hint": "Follow the pipeline diagram in the lesson: tokenize, embed, add position info, then repeated attention + feed-forward layers, then output.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why RNNs are inherently harder to parallelize during training than transformers, referencing the sequential dependency described in this lesson.",
                            "difficulty": "medium",
                            "hint": "Consider whether an RNN can compute its state at step 10 without first computing its state at every step before it.",
                        },
                        {
                            "prompt": "Give an example sentence (other than the one in the lesson) where word order changes the meaning, and explain why positional encoding is necessary for a transformer to distinguish the two orderings.",
                            "difficulty": "medium",
                            "hint": "Try a sentence where swapping the subject and object changes who is doing what to whom.",
                        },
                    ],
                    "resources": [
                        {"title": "Vaswani et al., 'Attention Is All You Need' (2017)", "url": "https://arxiv.org/abs/1706.03762", "resource_type": "paper"},
                    ],
                    "skills": [{"slug": "transformers", "weight": 1.0}],
                },
                {
                    "slug": "self-attention-explained",
                    "title": "Self-Attention Explained",
                    "description": "How a transformer decides which other tokens matter most for understanding each token in a sequence.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain self-attention as a weighted lookup across all tokens in a sequence",
                        "Describe the intuitive roles of queries, keys, and values",
                        "Explain why attention weights differ per token and per context",
                        "Connect self-attention to why LLMs can resolve ambiguous pronouns and references",
                    ],
                    "content_markdown": """
## Why this matters

Self-attention is the single mechanical idea that explains why LLMs are so good at using context —
resolving what "it" refers to three sentences back, weighing a system prompt's instructions against a
user's request, or noticing that a detail mentioned early in a long document is relevant to a
question asked at the end. All of that traces back to this one lesson.

## Self-attention as a weighted lookup

For each token in a sequence, self-attention computes a weighted combination of information from
every other token, where the weights reflect how *relevant* each other token is to understanding the
current one, in this specific context.

```python
# Deliberately simplified illustration of the RESULT self-attention produces,
# not the actual matrix math used to compute it.
sentence = ["The", "trophy", "didn't", "fit", "in", "the", "suitcase", "because", "it", "was", "too", "big"]

# When processing the token "it", self-attention assigns HIGH weight to "trophy"
# and LOW weight to "suitcase", correctly resolving the ambiguous pronoun --
# but if the sentence continued differently ("...because it was too small"),
# the SAME mechanism could instead weight "suitcase" more heavily.
attention_weights_for_it = {
    "trophy": 0.72,
    "suitcase": 0.08,
    "fit": 0.11,
    # ... small weights spread across the remaining tokens
}
```

This example (a version of the classic "Winograd schema" ambiguity test) illustrates the key insight:
the *same* word "it" gets a different, context-dependent interpretation depending on the rest of the
sentence, and self-attention is the mechanism that lets the model compute exactly that kind of
context-sensitive weighting for every token, automatically, from data.

## Queries, keys, and values: the intuitive version

Self-attention is often explained using a query/key/value framing, borrowed from search systems:

- **Query** — what the current token is "looking for" — think of it as the current token's search
  request.
- **Key** — what each token (including itself) "advertises" about itself — think of it as each
  token's searchable label.
- **Value** — the actual content/information each token contributes if it's deemed relevant.

```python
# Conceptual, not literal matrix operations
def self_attention_step(current_token, all_tokens):
    query = compute_query(current_token)
    scores = {t: compute_key(t) @ query for t in all_tokens}  # similarity between query and each key
    weights = softmax(scores)                                  # normalize into a probability-like distribution
    output = sum(weights[t] * compute_value(t) for t in all_tokens)
    return output
```

The model compares the current token's query against every other token's key, converts those
similarity scores into normalized weights (via a function called softmax, which squashes a list of
numbers into a distribution that sums to 1), and then produces a weighted sum of every token's value
using those weights. This whole process happens for every token, simultaneously, at every layer —
which is why it's computationally expensive as sequence length grows (recall the Context Windows
lesson's explanation of why context limits exist).

## Why attention weights are context-dependent, not fixed

A crucial property: the weights aren't a fixed lookup table (like "it" always maps to "trophy") —
they're recomputed fresh for every specific input sequence, based on the actual surrounding words.
Change one word elsewhere in the sentence, and the attention pattern for "it" can shift entirely.
This context-sensitivity is exactly why LLMs handle ambiguous language so much better than older,
rule-based NLP systems, which relied on fixed heuristics that couldn't adapt this fluidly.

## Multi-head attention, briefly

Real transformers run many attention computations ("heads") in parallel, each potentially learning to
focus on different kinds of relationships — one head might specialize in tracking grammatical
subject-verb agreement, another in resolving pronoun references, another in topic-level relevance.
Their outputs are combined, giving the model several simultaneous "perspectives" on the same
sequence rather than just one.

## Looking ahead

This lesson closes out your conceptual understanding of the transformer. Everything from here forward
in this program — prompt engineering, RAG, agents — is really about skillfully feeding good context
into this attention mechanism and interpreting what comes out, rather than modifying the mechanism
itself.
""",
                    "examples": [
                        {
                            "title": "Example: A toy softmax to illustrate turning scores into weights",
                            "code": "import math\n\ndef softmax(scores):\n    max_score = max(scores.values())\n    exp_scores = {k: math.exp(v - max_score) for k, v in scores.items()}\n    total = sum(exp_scores.values())\n    return {k: v / total for k, v in exp_scores.items()}\n\nraw_scores = {\"trophy\": 4.2, \"suitcase\": 1.1, \"fit\": 1.8}\nprint(softmax(raw_scores))",
                            "explanation": "Implements the softmax function used to turn raw attention scores into normalized weights that sum to 1, directly matching the 'weights = softmax(scores)' step in the lesson's pseudocode.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement the softmax function from scratch (without importing it from a library) and verify that its output values always sum to approximately 1.0 for at least two different input dictionaries.",
                            "difficulty": "medium",
                            "hint": "Sum the values of the returned dictionary and check it's close to 1.0 using round() or a small tolerance.",
                        },
                        {
                            "prompt": "Write your own Winograd-style ambiguous sentence (like the trophy/suitcase example) with a pronoun whose correct referent depends on one specific other word in the sentence, and explain which word self-attention would need to weight most heavily.",
                            "difficulty": "medium",
                            "hint": "Think of two nouns and an adjective or verb where swapping the adjective flips which noun the pronoun refers to.",
                        },
                        {
                            "prompt": "In your own words, explain the difference between the 'key' and the 'value' in the query/key/value framing, using the search-engine analogy from the lesson.",
                            "difficulty": "hard",
                            "hint": "A key is like a searchable label/index entry; a value is like the actual document content returned once that entry is deemed a match.",
                        },
                    ],
                    "resources": [
                        {"title": "Jay Alammar: The Illustrated Transformer", "url": "https://jalammar.github.io/illustrated-transformer/", "resource_type": "tutorial"},
                    ],
                    "skills": [{"slug": "transformers", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "inference",
            "title": "Inference",
            "description": "What actually happens when you send a request to an LLM, and the tradeoffs that shape latency, throughput, and cost.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "how-inference-works",
                    "title": "How Inference Works",
                    "description": "The distinction between training and inference, and what happens computationally when a model responds to a request.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Distinguish training from inference clearly",
                        "Describe the two-phase structure of inference: prompt processing and generation",
                        "Explain why prompt processing and generation have different performance characteristics",
                        "Recognize the practical implications of this split for latency in real applications",
                    ],
                    "content_markdown": """
## Why this matters

Every API call you make from Course 3 onward is an inference request, not a training run. Knowing
what actually happens during inference — and specifically why the first response token often takes
noticeably longer to arrive than each subsequent one — explains latency patterns you'll see
constantly once you start building real applications and streaming responses in a later module.

## Training vs inference

**Training** (covered conceptually in Course 2) is the one-time, extremely expensive process of
learning the model's weights from data. **Inference** is using an already-trained model, with its
weights now fixed, to generate a response to a new input. Every request you send through an API for
the rest of this program is inference — you are never retraining the model itself by using it.

## Two phases of inference: prefill and decode

Inference for a single request actually happens in two distinct phases with different performance
characteristics:

1. **Prefill (prompt processing)** — the model processes your entire input prompt at once, computing
   attention across all the input tokens simultaneously (this step can be heavily parallelized, since
   the whole input is already known upfront).
2. **Decode (generation)** — the model generates the response one token at a time, autoregressively,
   as covered in the "How LLMs Generate Text" lesson — and this phase is inherently sequential,
   token by token.

```python
def inference(prompt_tokens, max_output_tokens):
    # Phase 1: prefill -- process the whole prompt in parallel
    hidden_state = process_prompt(prompt_tokens)

    # Phase 2: decode -- generate one token at a time, sequentially
    output_tokens = []
    for _ in range(max_output_tokens):
        next_token, hidden_state = generate_next(hidden_state)
        if next_token == STOP_TOKEN:
            break
        output_tokens.append(next_token)

    return output_tokens
```

## Why this split matters for latency

Because prefill is parallelizable but decode is sequential, a longer input prompt increases latency
less dramatically (per token) than a longer expected output does. This is one reason "time to first
token" (how long until the first piece of the response starts streaming back) and "tokens per second
during generation" are reported as two separate performance metrics by LLM providers, rather than one
combined number — they reflect genuinely different phases of the computation with different
bottlenecks.

## Why the first token can feel slower than the rest

If you've ever noticed a brief pause before a streamed response starts appearing, and then a
steadier flow of tokens after that, you're observing the prefill-then-decode split directly: prefill
has to finish processing your entire prompt before the very first output token can be produced, while
each subsequent token during decode reuses cached computation from prefill and previous decode steps,
so it doesn't repeat that upfront work.

## Practical implications

- Very long prompts (a huge RAG context, or a long conversation history) primarily affect **time to
  first token**, since that's when prefill happens.
- Long expected outputs primarily affect **total generation time**, since decode is strictly
  sequential.
- These two costs are additive, but they respond differently to your design choices — trimming
  context (previous module) mainly helps time-to-first-token; setting a tighter `max_tokens` mainly
  helps total generation time.

## Looking ahead

The next lesson in this module puts numbers on exactly this tradeoff — latency, throughput, and cost
— and the LLM APIs module later in this course shows you how streaming lets your application start
using the first tokens the moment decode begins, without waiting for the entire response.
""",
                    "examples": [
                        {
                            "title": "Example: Modeling total latency as prefill time plus decode time",
                            "code": "def estimate_latency(prompt_tokens, output_tokens, prefill_tokens_per_sec=5000, decode_tokens_per_sec=50):\n    prefill_time = prompt_tokens / prefill_tokens_per_sec\n    decode_time = output_tokens / decode_tokens_per_sec\n    return prefill_time + decode_time\n\nprint(estimate_latency(prompt_tokens=3000, output_tokens=500))\nprint(estimate_latency(prompt_tokens=100, output_tokens=500))",
                            "explanation": "Uses illustrative (not official) throughput numbers to show that decode time dominates total latency once output length is non-trivial, since prefill is so much faster per token than sequential decode.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using estimate_latency from the example, compare the latency of a request with a 10,000-token prompt and 100-token output versus one with a 100-token prompt and 2,000-token output. Which dominates the total time, and why?",
                            "difficulty": "medium",
                            "hint": "Given that decode is much slower per-token than prefill in the example rates, output length tends to dominate more than you might initially expect.",
                        },
                        {
                            "prompt": "In your own words, explain why 'time to first token' and 'tokens per second' are reported as two separate metrics rather than being combined into one number.",
                            "difficulty": "medium",
                            "hint": "Connect each metric to one of the two phases: prefill (parallel) versus decode (sequential).",
                        },
                        {
                            "prompt": "Describe a real product scenario where reducing prompt length would meaningfully improve perceived responsiveness, even if the eventual full response length stays the same.",
                            "difficulty": "hard",
                            "hint": "Think about a chat UI that streams tokens -- users perceive 'time to first token' directly, even if total generation time is unchanged.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Streaming Messages", "url": "https://docs.anthropic.com/en/docs/build-with-claude/streaming", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "latency-throughput-and-cost-tradeoffs",
                    "title": "Latency, Throughput, and Cost Tradeoffs",
                    "description": "Balancing response speed, request volume, and spend when choosing models and designing systems.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Distinguish latency from throughput as separate performance concerns",
                        "Explain why larger, more capable models are typically slower and more expensive",
                        "Identify design choices that trade one of latency/throughput/cost for another",
                        "Apply this tradeoff reasoning to a realistic system design decision",
                    ],
                    "content_markdown": """
## Why this matters

Course 13 (Production AI) will have you choose models and design request patterns under real
constraints — a support chatbot that needs to feel instant, versus a nightly batch job summarizing
thousands of documents where total throughput matters far more than any single response's speed.
This lesson gives you the vocabulary and tradeoff framework for that decision before you're under
production pressure to make it quickly.

## Latency vs throughput: two different questions

- **Latency** — how long does a single request take, from send to complete response? This is what
  an individual user waiting on a chat response actually experiences.
- **Throughput** — how many requests (or tokens) can the system handle per unit of time, in
  aggregate, often across many concurrent requests? This is what matters for a batch job processing
  thousands of documents overnight.

A system can have low latency but low throughput (fast for one user, falls over under load), or
higher latency but high throughput (each request takes a bit longer, but the system handles massive
concurrent volume smoothly) — optimizing for one doesn't automatically optimize for the other, and
sometimes improving one costs you the other.

## Why bigger models are typically slower and pricier

A model with more parameters generally produces higher-quality, more capable output — but every one
of those extra parameters means more computation per token during both prefill and decode, which
directly increases latency per request and typically increases price per token as well, since more
compute resources are needed to serve it.

```python
models = {
    "small-fast-model":  {"quality": "good",      "latency_per_1k_tokens": 0.8, "price_per_million": 0.80},
    "large-capable-model": {"quality": "excellent", "latency_per_1k_tokens": 2.5, "price_per_million": 15.00},
}

def choose_model(task_needs_top_quality, latency_sensitive):
    if latency_sensitive and not task_needs_top_quality:
        return "small-fast-model"
    return "large-capable-model"
```

This isn't a rule that "bigger is always better" — for many well-scoped tasks (simple classification,
short extraction, routing decisions), a smaller, faster, cheaper model performs just as well as a
larger one, and choosing it is a genuine engineering win, not a compromise.

## Design choices that trade one dimension for another

- **Model choice** — smaller models trade some output quality for lower latency and cost, as above.
- **Batching** — grouping multiple requests together can improve overall throughput on the provider
  side, sometimes at the cost of added latency for any individual request in the batch.
- **Caching** — serving a cached response for a repeated or near-identical query gives near-zero
  latency and cost for that request, at the cost of engineering effort to build and invalidate the
  cache correctly.
- **Streaming** — doesn't change total generation time, but dramatically improves *perceived*
  latency by showing partial output immediately (directly building on the prefill/decode split from
  the previous lesson).
- **Parallel requests** — using the async patterns from Course 1 to run independent requests
  concurrently improves overall throughput for a batch job without needing a faster model at all.

## A worked tradeoff scenario

A customer support chatbot needs responses to feel instant (latency-sensitive) but handles individual
conversations, not massive batch volume (throughput is less critical); a nightly job classifying
10,000 support tickets by urgency cares much more about total throughput and cost per ticket than the
latency of any single classification. These two systems should reasonably choose different models and
different concurrency strategies, even if they're solving conceptually similar classification-style
problems.

## Looking ahead

Course 13's production cost-control and scaling lessons return to exactly this three-way tradeoff —
latency, throughput, cost — as the central design question behind model selection, caching strategy,
and concurrency limits for a real deployed system.
""",
                    "examples": [
                        {
                            "title": "Example: A simple model-selection policy based on task requirements",
                            "code": "def select_model(task_type):\n    routing = {\n        \"simple_classification\": \"small-fast-model\",\n        \"complex_reasoning\": \"large-capable-model\",\n        \"real_time_chat\": \"small-fast-model\",\n        \"final_report_generation\": \"large-capable-model\",\n    }\n    return routing.get(task_type, \"large-capable-model\")  # default to safer, more capable choice\n\nprint(select_model(\"simple_classification\"))\nprint(select_model(\"complex_reasoning\"))",
                            "explanation": "A minimal routing function that picks a cheaper, faster model for simpler tasks and reserves a larger model for tasks that genuinely need its extra capability, the same pattern used in multi-model production systems.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For each of these three systems -- a real-time voice assistant, an overnight document summarization batch job, and an interactive coding assistant -- identify whether latency or throughput matters more, and justify your answer in one sentence each.",
                            "difficulty": "medium",
                            "hint": "Consider whether a human is actively waiting in real time, or whether the job just needs to finish by some later deadline across many items.",
                        },
                        {
                            "prompt": "Extend the select_model routing function to include a third tier, 'medium-model', and add at least 2 new task types that should route to it, explaining your reasoning.",
                            "difficulty": "medium",
                            "hint": "Think of tasks that need more capability than simple classification but don't require the largest model's full power.",
                        },
                        {
                            "prompt": "Describe a scenario where streaming improves perceived latency without changing total generation time at all, and explain why that distinction matters for user experience design.",
                            "difficulty": "hard",
                            "hint": "Consider a long response that starts appearing immediately versus one that appears all at once after the full generation finishes.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Choosing the right model", "url": "https://docs.anthropic.com/en/docs/about-claude/models/choosing-a-model", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "temperature-and-sampling",
            "title": "Temperature and Sampling",
            "description": "How a model turns a probability distribution into an actual chosen token, and how to control that choice.",
            "order_index": 6,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "sampling-strategies",
                    "title": "Sampling Strategies",
                    "description": "Greedy decoding, top-k, and top-p sampling -- the different ways to pick a token from a probability distribution.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain greedy decoding and its main drawback",
                        "Implement top-k and top-p (nucleus) sampling conceptually",
                        "Compare the tradeoffs between different sampling strategies",
                        "Choose an appropriate sampling strategy for a given task",
                    ],
                    "content_markdown": """
## Why this matters

Two calls to the same LLM with the same prompt can produce different outputs — that isn't a bug,
it's a deliberate consequence of how the model chooses among several plausible next tokens rather
than always picking exactly one. Understanding sampling explains this behavior and gives you direct
control over it for tasks where you want consistency versus tasks where you want variety.

## Greedy decoding: always pick the most likely token

```python
def greedy_decode(probabilities):
    return max(probabilities, key=probabilities.get)

probs = {"Paris": 0.92, "a": 0.03, "located": 0.02, "the": 0.01}
print(greedy_decode(probs))  # always "Paris", every single time
```

Greedy decoding is fully deterministic: given the exact same input, it always produces the exact
same output. Its major drawback is that it can produce repetitive, overly generic text — always
taking the single "safest" next word at every step tends to avoid more interesting, still-plausible
phrasings, and can even get stuck in repetitive loops on some inputs.

## Top-k sampling: sample from the k most likely options

```python
import random

def top_k_sample(probabilities, k=3):
    sorted_tokens = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    top_k_tokens = sorted_tokens[:k]
    tokens, weights = zip(*top_k_tokens)
    return random.choices(tokens, weights=weights, k=1)[0]

probs = {"Paris": 0.70, "a": 0.10, "located": 0.08, "the": 0.07, "France": 0.05}
print(top_k_sample(probs, k=3))  # samples among {Paris, a, located} weighted by their probabilities
```

Top-k restricts sampling to only the k highest-probability tokens, then samples among just those,
weighted by their relative probabilities. This introduces controlled randomness while still avoiding
very unlikely, potentially nonsensical tokens.

## Top-p (nucleus) sampling: sample from the smallest set that covers probability p

```python
def top_p_sample(probabilities, p=0.9):
    sorted_tokens = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)
    cumulative = 0.0
    nucleus = []
    for token, prob in sorted_tokens:
        nucleus.append((token, prob))
        cumulative += prob
        if cumulative >= p:
            break
    tokens, weights = zip(*nucleus)
    return random.choices(tokens, weights=weights, k=1)[0]
```

Top-p is adaptive in a way top-k isn't: instead of always considering a fixed number of candidates,
it considers however many tokens are needed to reach a cumulative probability of `p`. When the model
is very confident (one token dominates), the nucleus might contain just 1-2 tokens; when the model is
genuinely uncertain across many plausible options, the nucleus naturally grows larger. This usually
makes top-p a more robust default than a fixed top-k across varied contexts.

## Comparing the strategies

| Strategy | Determinism | Typical use case |
|---|---|---|
| Greedy | Fully deterministic | Classification, extraction, anything needing consistency |
| Top-k | Randomized, fixed candidate pool size | Creative writing with bounded randomness |
| Top-p | Randomized, adaptive candidate pool size | General-purpose default for most generation tasks |

## Looking ahead

The next lesson in this module covers temperature, a separate but related parameter that adjusts how
"peaked" or "flat" the underlying probability distribution is *before* any of these sampling
strategies are applied — the two controls compose together, and most APIs let you tune both.
""",
                    "examples": [
                        {
                            "title": "Example: Running the same distribution through all three strategies",
                            "code": "probs = {\"Paris\": 0.6, \"a\": 0.15, \"located\": 0.1, \"the\": 0.08, \"France\": 0.07}\nprint(\"greedy:\", greedy_decode(probs))\nprint(\"top-k(2):\", top_k_sample(probs, k=2))\nprint(\"top-p(0.8):\", top_p_sample(probs, p=0.8))",
                            "explanation": "Runs one probability distribution through all three decoding strategies side by side, making their different behaviors directly comparable on the same input.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement greedy_decode, top_k_sample, and top_p_sample from the lesson, then run each 10 times on the same probability distribution and observe which strategy (if any) ever produces a different result across runs.",
                            "difficulty": "medium",
                            "hint": "greedy_decode should always return the exact same token; the others may vary run to run.",
                        },
                        {
                            "prompt": "For a JSON-extraction task where you need exactly one correct, repeatable answer, which sampling strategy from this lesson would you choose, and why?",
                            "difficulty": "easy",
                            "hint": "Consider which strategy guarantees the same output every time given the same input.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why top-p sampling is described as 'adaptive' while top-k is not, using an example of a very confident distribution and a very uncertain one.",
                            "difficulty": "hard",
                            "hint": "Consider how many tokens each strategy ends up considering when one token has 95% probability versus when probability is spread evenly across 10 tokens.",
                        },
                    ],
                    "resources": [
                        {"title": "Hugging Face: Text generation strategies", "url": "https://huggingface.co/docs/transformers/generation_strategies", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "controlling-randomness-with-temperature",
                    "title": "Controlling Randomness with Temperature",
                    "description": "How the temperature parameter reshapes a probability distribution before sampling, and how to set it for different tasks.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain what temperature does mathematically to a probability distribution",
                        "Predict the qualitative effect of low, medium, and high temperature settings",
                        "Set temperature appropriately for a given task via an LLM API",
                        "Distinguish temperature's role from sampling strategy's role",
                    ],
                    "content_markdown": """
## Why this matters

Temperature is the single most commonly adjusted generation parameter you'll set in every course
from here forward. Getting an intuitive feel for what it does — and isn't — prevents both the
common mistake of cranking it up "to make responses more creative" for tasks that actually need
consistency, and the opposite mistake of leaving it at a default that's wrong for a genuinely
creative task.

## What temperature does mathematically

Before sampling, the model's raw output scores get converted into a probability distribution using
softmax (introduced in the Self-Attention lesson). Temperature is a parameter applied *before* that
softmax step that reshapes how "peaked" or "flat" the resulting distribution is.

```python
import math

def softmax_with_temperature(scores, temperature=1.0):
    adjusted = {k: v / temperature for k, v in scores.items()}
    max_score = max(adjusted.values())
    exp_scores = {k: math.exp(v - max_score) for k, v in adjusted.items()}
    total = sum(exp_scores.values())
    return {k: v / total for k, v in exp_scores.items()}

raw_scores = {"Paris": 4.0, "a": 1.5, "located": 1.2, "the": 0.9}

print(softmax_with_temperature(raw_scores, temperature=0.3))  # very peaked -- "Paris" dominates
print(softmax_with_temperature(raw_scores, temperature=1.0))  # standard distribution
print(softmax_with_temperature(raw_scores, temperature=2.0))  # flatter -- other tokens more competitive
```

Dividing scores by a **temperature less than 1** amplifies differences between them, making the
distribution more peaked (the model becomes more confident, favoring its top choice even more
strongly than before). Dividing by a **temperature greater than 1** shrinks differences between
scores, flattening the distribution and giving lower-probability tokens a relatively better chance of
being sampled.

## Qualitative effects at different settings

- **Low temperature (near 0)** — nearly deterministic, very focused output; good for factual
  question-answering, code generation, structured data extraction, classification-style tasks — any
  task where you want the "best" answer reliably, every time.
- **Medium temperature (around 0.5-0.8)** — a reasonable default for general assistant-style
  conversation, balancing coherence with some natural variation.
- **High temperature (above 1.0)** — noticeably more varied, sometimes surprising or creative output;
  useful for brainstorming, creative writing, generating diverse examples — but riskier for tasks
  needing precision, since it increases the chance of picking a less sensible token.

## Setting temperature via an API

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    temperature=0.2,  # low temperature: favor consistent, focused output
    messages=[{"role": "user", "content": "Extract the invoice total as a single number."}],
)
```

For the extraction task above, a low temperature is the right choice — you want the same, correct
number every time, not creative variation in how the number gets reported.

## Temperature is not the same as sampling strategy

Temperature reshapes the probability distribution itself; top-k/top-p (previous lesson) then decide
*which subset* of that (possibly reshaped) distribution to sample from. The two parameters compose:
you might use temperature=0.7 together with top_p=0.9, applying temperature's reshaping first and
then restricting sampling to the top_p nucleus of that reshaped distribution. Setting temperature to
0 with any sampling strategy effectively collapses to greedy decoding, since the distribution becomes
so peaked that the top token gets essentially all the probability mass.

## Looking ahead

Course 4 (Prompt Engineering) treats temperature as one of your standard tools for shaping output
behavior, right alongside prompt wording itself — and you'll make an explicit, task-specific
temperature choice for nearly every prompt template you build from here through the rest of the
program.
""",
                    "examples": [
                        {
                            "title": "Example: Comparing distribution spread at three temperatures",
                            "code": "for temp in [0.2, 1.0, 2.0]:\n    dist = softmax_with_temperature({\"yes\": 2.0, \"no\": 1.0, \"maybe\": 0.5}, temperature=temp)\n    print(temp, {k: round(v, 3) for k, v in dist.items()})",
                            "explanation": "Prints the reshaped distribution at low, standard, and high temperature for the same raw scores, making the peaked-vs-flat effect directly visible in the numbers.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement softmax_with_temperature from the lesson and run it on a distribution of your own choosing at temperature=0.1 and temperature=3.0, describing the difference in the resulting probabilities.",
                            "difficulty": "easy",
                            "hint": "At very low temperature, the top score's probability should approach 1.0; at high temperature, probabilities should be much closer to each other.",
                        },
                        {
                            "prompt": "For each of these four tasks, recommend a temperature setting (low, medium, or high) and justify it in one sentence: (1) generating 10 diverse marketing taglines, (2) extracting a date from an email, (3) writing a casual chatbot reply, (4) generating unit test names.",
                            "difficulty": "medium",
                            "hint": "Match each task's need for either consistency or creative variety to the appropriate temperature range from the lesson.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why setting temperature to 0 is not exactly the same as setting it to a very small positive number like 0.01, from a purely mathematical standpoint (consider what happens when you divide by 0 in the temperature formula).",
                            "difficulty": "hard",
                            "hint": "Most APIs treat temperature=0 as a special case (equivalent to greedy decoding) precisely because dividing by zero is undefined in the raw formula.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic API: Messages (temperature parameter)", "url": "https://docs.anthropic.com/en/api/messages", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "message-roles",
            "title": "System/User/Assistant Messages",
            "description": "The structured message format nearly every LLM API uses, and how to use it deliberately.",
            "order_index": 7,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "the-chat-message-format",
                    "title": "The Chat Message Format",
                    "description": "How system, user, and assistant roles structure a conversation, and how to build a multi-turn messages list correctly.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain the purpose of each of the system, user, and assistant roles",
                        "Construct a valid multi-turn messages list for an API call",
                        "Explain why the assistant's previous responses must be included as history",
                        "Identify common mistakes when building message histories programmatically",
                    ],
                    "content_markdown": """
## Why this matters

This is the exact data structure you practiced building in Course 1's dictionaries lesson and reused
in the CLI chat loop project — now you're seeing why it's shaped the way it is, and how to use it
correctly for real multi-turn conversations with an LLM.

## The three roles

- **system** — instructions that set the model's overall behavior, persona, and constraints for the
  entire conversation; typically sent once, not per-turn.
- **user** — messages representing what the human (or calling application) sent.
- **assistant** — messages representing what the model previously generated; critically, you must
  include the model's own past responses in the history you send back on the next turn.

```python
messages = [
    {"role": "user", "content": "What's the capital of France?"},
    {"role": "assistant", "content": "The capital of France is Paris."},
    {"role": "user", "content": "What's its population?"},
]

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=200,
    system="You are a concise, factual assistant. Keep answers under 2 sentences.",
    messages=messages,
)
```

Note that in the Anthropic API specifically, the system prompt is a separate top-level parameter,
not a message with role "system" inside the messages list — API conventions vary by provider, so
always check the specific SDK's documentation rather than assuming every API structures this
identically.

## Why the model doesn't "remember" anything on its own

This is one of the most important operational facts about LLM APIs: **the model has no memory
between API calls**. Every single request is entirely self-contained — if you want the model to
"remember" what it said two turns ago, you must literally resend that earlier exchange as part of the
`messages` list on every subsequent call. This directly explains why the Context Windows module's
token-management strategies matter so much: what looks like "the model remembering the conversation"
is actually your application resending the entire relevant history every single time.

```python
def add_turn(messages, role, content):
    messages.append({"role": role, "content": content})
    return messages

conversation = []
conversation = add_turn(conversation, "user", "My name is Alex.")
# ... call the API, get a response ...
conversation = add_turn(conversation, "assistant", "Nice to meet you, Alex!")
conversation = add_turn(conversation, "user", "What's my name?")
# The API can only answer this correctly because "My name is Alex" is STILL in the messages list
```

## Common mistakes when building message histories

- **Forgetting to append the assistant's response** — if you only ever append user messages, the
  model loses all memory of its own prior answers, and conversations become incoherent.
- **Alternating roles incorrectly** — most APIs expect messages to alternate user/assistant/user/...;
  sending two consecutive user messages (or two consecutive assistant messages) without an
  intervening turn can cause errors or degrade response quality, depending on the provider.
- **Resending an oversized history** — directly connects to the Context Windows module: an
  ever-growing, never-trimmed messages list will eventually exceed the context window or become
  needlessly expensive.

## Looking ahead

This exact `messages` list structure is what your Course 1 `ChatSession` class's stub `get_response`
method will be filled in with in the LLM APIs module later in this course — and it's the foundation
every framework in Courses 10-12 (LangChain, LangGraph, multi-agent systems) builds its own,
fancier conversation and state abstractions on top of.
""",
                    "examples": [
                        {
                            "title": "Example: Building a multi-turn conversation incrementally",
                            "code": "messages = []\n\ndef user_turn(messages, text):\n    messages.append({\"role\": \"user\", \"content\": text})\n\ndef assistant_turn(messages, text):\n    messages.append({\"role\": \"assistant\", \"content\": text})\n\nuser_turn(messages, \"Recommend a good beginner Python project.\")\nassistant_turn(messages, \"Try building a command-line to-do list app.\")\nuser_turn(messages, \"What libraries would I need?\")\n\nfor m in messages:\n    print(m[\"role\"], \":\", m[\"content\"])",
                            "explanation": "Builds a conversation turn by turn using small helper functions, mirroring exactly how a real chat application accumulates history before each new API call.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a messages list representing a 3-turn conversation (user, assistant, user) about a topic of your choice, then print each message's role and content on its own line.",
                            "difficulty": "easy",
                            "hint": "Use a list of dicts, each with 'role' and 'content' keys, in the correct alternating order.",
                        },
                        {
                            "prompt": "Write a function validate_alternation(messages) that returns False if two consecutive messages have the same role, and True otherwise.",
                            "difficulty": "medium",
                            "hint": "Loop through the list comparing each message's role to the previous message's role.",
                        },
                        {
                            "prompt": "Explain, in 2-3 sentences, why forgetting to append the assistant's own response to the messages list would break a multi-turn conversation, even though the API call itself wouldn't necessarily raise an error.",
                            "difficulty": "medium",
                            "hint": "Consider what the model actually has access to on the next call if its own prior response is missing from history.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic API: Messages", "url": "https://docs.anthropic.com/en/api/messages", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "designing-effective-system-prompts",
                    "title": "Designing Effective System Prompts",
                    "description": "Using the system role deliberately to set persona, constraints, and behavior for an entire conversation.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what belongs in a system prompt versus a user message",
                        "Write a system prompt that sets persona, scope, and output constraints clearly",
                        "Identify common system prompt anti-patterns",
                        "Preview the deeper system-prompt design work covered in Course 4",
                    ],
                    "content_markdown": """
## Why this matters

The system prompt is the single highest-leverage piece of text in most LLM applications — it shapes
every single response in a conversation, not just one. A vague or poorly structured system prompt
produces inconsistent behavior across an entire product; a well-designed one is often the difference
between a demo and something reliable enough to ship.

## What belongs in a system prompt

- **Persona and tone** — who is the assistant, and how should it "sound"?
- **Scope and boundaries** — what should it help with, and what should it explicitly decline?
- **Output format constraints** — should responses be short, use bullet points, avoid markdown, stay
  under a certain length?
- **Standing context** — facts that are true for the entire conversation, not just one turn (e.g.,
  "the user is a beginner programmer").

```python
system_prompt = '''You are a customer support assistant for a software company called Acme Tools.

- Answer only questions related to Acme Tools products and billing.
- If asked about anything unrelated, politely redirect the user to a relevant topic.
- Keep responses under 4 sentences unless the user explicitly asks for more detail.
- Never make up pricing information; if you're unsure, say so and suggest contacting sales.
'''
```

## What belongs in a user message instead

Anything specific to a single turn — the actual question being asked right now — belongs in a user
message, not the system prompt. Mixing per-turn specifics into the system prompt (e.g., baking a
single user's specific question into the system prompt text) defeats the purpose of having a stable,
reusable system prompt at all.

## Common system prompt anti-patterns

- **Vague instructions** — "Be helpful and nice" gives the model almost no concrete guidance on scope
  or format; specific, checkable instructions ("keep responses under 4 sentences") work far better.
- **Contradictory instructions** — "Be extremely detailed" alongside "keep responses very short"
  forces the model to somehow reconcile an impossible constraint, usually producing inconsistent
  behavior.
- **Overloading with too many rules at once** — a system prompt with 40 unprioritized bullet points
  is harder for a model to reliably follow than a tighter set of 5-8 clearly stated, high-priority
  rules.
- **Treating the system prompt as a security boundary** — a system prompt shapes behavior, but a
  sufficiently motivated user can sometimes get a model to deviate from it (this is explored directly
  in Course 4's prompt injection material and Course 12's safety module); never rely on the system
  prompt alone to enforce something safety-critical without additional guardrails.

## A worked before/after example

```python
# Before: vague, hard for the model to act on consistently
weak_system_prompt = "You are a helpful coding assistant."

# After: specific, checkable, scoped
strong_system_prompt = '''You are a Python coding assistant for intermediate developers.

- Always include a brief explanation alongside any code you provide.
- Default to Python 3.10+ syntax unless the user specifies otherwise.
- If a request is ambiguous, ask one clarifying question before writing code.
- Never claim code has been tested; you have not executed it.
'''
```

The "after" version gives the model concrete, checkable behaviors rather than a vague aspiration,
which produces measurably more consistent output across many different user requests.

## Looking ahead

Course 4 (Prompt Engineering) devotes an entire module to role prompting and treats system prompt
design as a first-class engineering discipline — including techniques like ordering instructions by
priority and testing a system prompt against a battery of edge-case inputs, both of which build
directly on the good/bad patterns introduced in this lesson.
""",
                    "examples": [
                        {
                            "title": "Example: A system prompt with explicit output-format constraints",
                            "code": "system_prompt = \"\"\"You are a data extraction assistant.\n\n- Extract only the fields explicitly requested by the user.\n- Respond with valid JSON only, no explanation text before or after.\n- If a requested field is not present in the input, use null for its value.\n\"\"\"\n\n# response = client.messages.create(\n#     model=\"claude-sonnet-5\", max_tokens=300,\n#     system=system_prompt,\n#     messages=[{\"role\": \"user\", \"content\": \"Extract name and email from: Contact Jane at jane@example.com\"}],\n# )",
                            "explanation": "Shows a system prompt purpose-built for a structured extraction task, with explicit, checkable constraints on both scope and output format -- exactly the kind of specificity the lesson recommends over vague instructions.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Rewrite the vague system prompt 'You are a helpful assistant for a travel booking app' into a specific, scoped version with at least 4 concrete rules covering persona, scope, and output format.",
                            "difficulty": "medium",
                            "hint": "Address what topics it should and shouldn't help with, how long responses should be, and how it should handle uncertainty.",
                        },
                        {
                            "prompt": "Identify and fix the contradiction in this system prompt: 'Always respond in exactly one word. Provide thorough, detailed explanations for every answer.'",
                            "difficulty": "easy",
                            "hint": "These two instructions cannot both be followed simultaneously; decide which behavior you actually want and remove or rewrite the conflicting one.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why you should not rely solely on a system prompt instruction like 'never reveal confidential information' as your only safeguard against a user trying to extract sensitive data from a conversation.",
                            "difficulty": "hard",
                            "hint": "Consider that instructions shape typical behavior but aren't a hard technical guarantee against a determined adversarial user, a topic explored fully in later safety-focused courses.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: System Prompts", "url": "https://docs.anthropic.com/en/docs/build-with-claude/system-prompts", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "llm-apis",
            "title": "LLM APIs",
            "description": "Actually calling a real LLM from Python -- authentication, requests, parsing responses, and streaming.",
            "order_index": 8,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "calling-the-claude-api",
                    "title": "Calling the Claude API",
                    "description": "Making your first real API call using the Anthropic Python SDK, and reading the response object.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Install and configure the Anthropic Python SDK",
                        "Make a basic messages.create call and read the response",
                        "Access usage information (input/output token counts) from a response",
                        "Wire a real API call into the Course 1 CLI chat loop project",
                    ],
                    "content_markdown": """
## Why this matters

This is the moment everything from Courses 1-3 converges into a real, working system: your Course 1
`.env` habits, your dictionary and JSON fluency, your understanding of tokens, context, roles, and
sampling parameters all come together in a single function call in this lesson.

## Installing and configuring the SDK

```bash
python -m pip install anthropic
```

```python
# .env file: ANTHROPIC_API_KEY=sk-ant-...
from dotenv import load_dotenv
import anthropic

load_dotenv()
client = anthropic.Anthropic()  # automatically reads ANTHROPIC_API_KEY from the environment
```

This is exactly the `.env` + `python-dotenv` pattern from Course 1's "Working with AI SDKs and
Environment Config" lesson, now used for real.

## Making a basic call

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    system="You are a helpful, concise assistant.",
    messages=[{"role": "user", "content": "Explain what a REST API is in two sentences."}],
)

print(response.content[0].text)
```

Note that `response.content` is a list (a model's response can, in general, include multiple content
blocks, such as text mixed with tool calls, which you'll meet in Course 9) — for a simple text
response, you typically want `response.content[0].text`.

## Reading usage information

```python
print(response.usage.input_tokens)
print(response.usage.output_tokens)
print(response.stop_reason)  # e.g. "end_turn", "max_tokens", "stop_sequence"
```

This directly enables the cost-tracking work from the Token Limits and Cost lesson — every real
response tells you exactly how many input and output tokens it consumed, which you can log and feed
into a running cost estimate.

## Setting generation parameters

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=500,
    temperature=0.2,
    messages=[{"role": "user", "content": "List 3 Python testing frameworks as a JSON array."}],
)
```

Every parameter from this course's earlier modules — `max_tokens`, `temperature`, `system`,
`messages` — shows up here as a keyword argument on the exact same function call.

## Wiring this into the Course 1 CLI chat loop

Recall the `ChatSession.get_response` stub from Course 1's capstone project:

```python
class ChatSession:
    def __init__(self, system_prompt="You are a helpful assistant."):
        self.system_prompt = system_prompt
        self.history = []
        self.client = anthropic.Anthropic()

    def add_user_message(self, content):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.history.append({"role": "assistant", "content": content})

    def get_response(self, user_input):
        response = self.client.messages.create(
            model="claude-sonnet-5",
            max_tokens=1024,
            system=self.system_prompt,
            messages=self.history,
        )
        return response.content[0].text
```

Notice how little changed from the Course 1 stub: the method's signature and role in the class are
identical, only its body now makes a real call instead of returning a placeholder string — exactly
the "swap the implementation, keep the interface" design the Course 1 lesson set up.

## Handling errors gracefully

```python
try:
    response = client.messages.create(model="claude-sonnet-5", max_tokens=1024, messages=messages)
except anthropic.APIError as e:
    print(f"API call failed: {e}")
```

Real production code (Course 13) wraps this in retry logic with backoff, echoing the retry patterns
from Course 1's async programming module.

## Looking ahead

The next lesson covers streaming, which changes how you read `response` but not the underlying
`messages.create`-style call itself, and the Hallucinations module later in this course revisits this
exact response object to discuss how to interpret model output critically rather than trusting it
blindly.
""",
                    "examples": [
                        {
                            "title": "Example: A minimal reusable call_llm helper",
                            "code": "import anthropic\n\nclient = anthropic.Anthropic()\n\ndef call_llm(prompt, system=None, temperature=0.7, max_tokens=1024):\n    response = client.messages.create(\n        model=\"claude-sonnet-5\",\n        max_tokens=max_tokens,\n        temperature=temperature,\n        system=system or \"You are a helpful assistant.\",\n        messages=[{\"role\": \"user\", \"content\": prompt}],\n    )\n    return response.content[0].text\n\n# print(call_llm(\"What is 2 + 2?\"))",
                            "explanation": "Wraps the raw SDK call in a small reusable function with sensible defaults, the kind of helper you'll build once and reuse throughout the rest of this program.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Set up a .env file with your API key, install the anthropic package, and make a single call_llm-style request, printing both the response text and the input/output token counts.",
                            "difficulty": "medium",
                            "hint": "Reuse the .env loading pattern from Course 1 and the usage-reading code from this lesson.",
                        },
                        {
                            "prompt": "Update the Course 1 ChatSession class's get_response method to make a real API call as shown in the lesson, and run the full CLI chat loop end to end.",
                            "difficulty": "hard",
                            "hint": "Only the body of get_response needs to change; the rest of the class and the run_chat loop should work unmodified.",
                        },
                        {
                            "prompt": "Write a wrapper function safe_call_llm(prompt) that catches anthropic.APIError and returns a fallback string instead of raising, then test it by intentionally passing an invalid model name.",
                            "difficulty": "medium",
                            "hint": "Wrap the messages.create call in try/except anthropic.APIError as e, returning a fallback message in the except block.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Getting started with the API", "url": "https://docs.anthropic.com/en/api/getting-started", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "streaming-responses",
                    "title": "Streaming Responses",
                    "description": "Receiving a response incrementally as it's generated, for better perceived responsiveness.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why streaming improves perceived latency without changing total generation time",
                        "Implement a streaming API call and process events as they arrive",
                        "Accumulate a full response from a stream of partial events",
                        "Identify when streaming is and isn't the right choice for a system",
                    ],
                    "content_markdown": """
## Why this matters

Streaming is directly built on the prefill/decode split from the Inference module: since tokens are
generated sequentially, there's no reason to make a user wait for the *entire* response to finish
before showing them anything. This lesson turns that architectural fact into working code.

## A non-streaming call, for contrast

```python
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=500,
    messages=[{"role": "user", "content": "Write a short paragraph about the history of Python."}],
)
print(response.content[0].text)  # nothing printed until the ENTIRE response is ready
```

## A streaming call

```python
with client.messages.stream(
    model="claude-sonnet-5",
    max_tokens=500,
    messages=[{"role": "user", "content": "Write a short paragraph about the history of Python."}],
) as stream:
    for text in stream.text_stream:
        print(text, end="", flush=True)  # prints incrementally, as each chunk arrives
    final_message = stream.get_final_message()

print()
print(final_message.usage.output_tokens)
```

`stream.text_stream` yields chunks of text as the model generates them; `flush=True` ensures each
chunk appears immediately in the terminal rather than being buffered. `stream.get_final_message()`
gives you the complete, assembled response object afterward, including usage information, exactly
like the non-streaming call's return value.

## Accumulating a full response manually

Sometimes you need the full text as you go (not just to print it), for example to detect when a
complete JSON object has arrived:

```python
def stream_and_collect(client, **kwargs):
    collected = []
    with client.messages.stream(**kwargs) as stream:
        for text in stream.text_stream:
            collected.append(text)
            print(text, end="", flush=True)
    return "".join(collected)

full_text = stream_and_collect(
    client,
    model="claude-sonnet-5",
    max_tokens=500,
    messages=[{"role": "user", "content": "List 3 benefits of async programming."}],
)
```

## When streaming helps and when it doesn't

Streaming meaningfully improves perceived responsiveness for **long, user-facing text responses** —
a chat UI, a long explanation, generated prose — where showing partial progress keeps a human
engaged rather than staring at a blank loading spinner.

Streaming is usually **not worth the added complexity** for:
- Very short responses, where the entire generation finishes quickly enough that streaming adds
  little perceptible benefit.
- Structured output you need to parse as a complete unit anyway (e.g., a JSON object you can't safely
  use until it's fully formed) — though even here, some applications stream and only attempt to parse
  once a closing brace is detected.
- Backend-to-backend calls with no human directly watching the response arrive, such as one step in
  an automated agent pipeline (Course 9), where total completion time matters more than perceived
  responsiveness.

## Looking ahead

Course 9's agent loops mostly do NOT stream intermediate tool-calling steps to the end user (since
there's no human watching each internal step), but DO often stream the agent's final natural-language
answer once it's ready — applying exactly the "when streaming helps" judgment call from this lesson
to a more complex system.
""",
                    "examples": [
                        {
                            "title": "Example: Streaming with a simple progress indicator",
                            "code": "chunk_count = 0\nwith client.messages.stream(\n    model=\"claude-sonnet-5\",\n    max_tokens=300,\n    messages=[{\"role\": \"user\", \"content\": \"Explain recursion briefly.\"}],\n) as stream:\n    for text in stream.text_stream:\n        chunk_count += 1\n        print(text, end=\"\", flush=True)\nprint(f\"\\n\\nReceived {chunk_count} chunks\")",
                            "explanation": "Streams a response while also counting how many discrete chunks arrived, illustrating that a streamed response is delivered as many small pieces rather than one atomic block.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a streaming API call that prints each chunk of text as it arrives, then prints the total output token count once the stream completes.",
                            "difficulty": "medium",
                            "hint": "Use stream.text_stream for the incremental text and stream.get_final_message().usage for the token count afterward.",
                        },
                        {
                            "prompt": "Implement stream_and_collect from the lesson and verify that joining the collected chunks produces text identical to what a non-streaming call to the same prompt would return (allowing for sampling randomness if temperature > 0).",
                            "difficulty": "medium",
                            "hint": "Set temperature=0 for both calls to make the comparison deterministic and meaningful.",
                        },
                        {
                            "prompt": "Describe a specific feature in a product you use that likely relies on streaming LLM output, and explain what the user experience would feel like if that feature switched to non-streaming instead.",
                            "difficulty": "hard",
                            "hint": "Think about AI chat assistants you've used, and how long a total response might take to appear all at once versus incrementally.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Streaming Messages", "url": "https://docs.anthropic.com/en/docs/build-with-claude/streaming", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "hallucinations",
            "title": "Hallucinations",
            "description": "Why LLMs confidently produce false information, and practical strategies to reduce and catch it.",
            "order_index": 9,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-llms-hallucinate",
                    "title": "Why LLMs Hallucinate",
                    "description": "The mechanistic reasons hallucination happens, rooted directly in next-token prediction and sampling.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define hallucination precisely, distinct from simple factual errors in training data",
                        "Explain how next-token prediction and sampling both contribute to hallucination",
                        "Identify why confident-sounding text and correct text are not the same thing",
                        "Recognize the categories of prompts most likely to trigger hallucination",
                    ],
                    "content_markdown": """
## Why this matters

Hallucination is the single most important limitation to internalize before you build anything a
real user will rely on. Every RAG system (Course 5) and every safety guardrail (Course 12) in this
program exists at least partly to manage this one problem, so understanding *why* it happens — not
just that it happens — will make those later design decisions feel motivated rather than arbitrary.

## What hallucination actually means

A hallucination is text that is fluent, confident, and plausible-sounding, but factually incorrect or
entirely fabricated — a made-up citation, a nonexistent API method, a wrong date stated with total
confidence. This is distinct from the model simply repeating a factual error that existed in its
training data; hallucination specifically describes the model generating something with no clear
grounding at all, essentially inventing a plausible-sounding answer where it lacks one.

## The root cause: next-token prediction doesn't know what it doesn't know

Recall from the "What are LLMs?" module that an LLM's core mechanism is predicting the most likely
next token given context — it is optimizing for **fluency and plausibility**, not for a built-in
notion of "truth" that it checks against before generating. When asked about something the model has
weak or no real knowledge of, it doesn't have a reliable internal mechanism to say "I don't actually
know this" — it will still produce *some* fluent continuation, because generating fluent continuations
is fundamentally what the mechanism does, regardless of whether the specific facts in that
continuation are grounded in anything real.

```python
# A simplified mental model, not literal model internals
def next_token_prediction(context):
    # The model predicts what's PLAUSIBLE to say next, not what's independently VERIFIED to be true.
    # These usually align for well-represented facts, but can diverge for obscure or absent knowledge.
    return most_plausible_continuation(context)
```

## Sampling makes this worse, not better

Recall the Temperature and Sampling module: any sampling strategy other than pure greedy decoding at
temperature 0 introduces some randomness into token selection. This means the same question, asked
twice, can produce two different answers — and if the model has no solid grounding for the answer,
different sampling runs might confidently fabricate different specific (and equally wrong) details
each time, which is itself a useful diagnostic signal, covered in the next lesson.

## Confident-sounding is not the same as correct

Because the model was trained (in its instruction-tuning phase) to produce helpful, fluent,
confident-sounding responses, hallucinated text often reads with exactly the same tone and certainty
as accurate text — there is typically no built-in "uncertainty marker" that reliably distinguishes a
well-grounded answer from a fabricated one just by reading the surface style of the response. This is
precisely why you cannot use "does this sound confident and well-written?" as your test for whether
an LLM's factual claim is true.

## Prompts most likely to trigger hallucination

- Questions about very obscure, recent, or narrow topics that were underrepresented (or entirely
  absent) in training data.
- Requests for specific citations, exact statistics, or precise dates — categories where being
  slightly wrong is easy and the model has strong pressure (from its training) to produce *something*
  specific-sounding rather than admit uncertainty.
- Questions phrased in a way that presupposes a false premise (e.g., asking "why did X happen" when X
  never actually happened), which can lead the model to play along and fabricate an explanation.
- Multi-step reasoning chains, where a small error early on can compound into a confidently wrong
  final answer.

## Looking ahead

The next lesson turns this understanding into action: concrete mitigation strategies, including the
single most effective one you'll implement at scale starting in Course 5 — grounding the model's
answer in retrieved, verifiable source documents (RAG) rather than relying purely on what it
memorized during training.
""",
                    "examples": [
                        {
                            "title": "Example: A prompt category likely to induce hallucination",
                            "code": "risky_prompt = \"Cite the exact page number in RFC 9110 where content negotiation headers are defined.\"\n# Highly specific, narrow factual detail -- exactly the kind of request where an LLM,\n# lacking reliable access to the literal document, is prone to confidently inventing\n# a plausible-sounding but potentially incorrect page number.",
                            "explanation": "Identifies a concrete example of the 'specific citation' risk category from the lesson, illustrating why certain prompt shapes are inherently higher-risk for hallucination than others.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write three example prompts, one from each of the four 'high hallucination risk' categories described in the lesson (pick 3 of the 4 categories), and explain why each is risky.",
                            "difficulty": "medium",
                            "hint": "Pick concrete examples: an obscure fact, a request for an exact citation, and a false-premise question, for instance.",
                        },
                        {
                            "prompt": "Explain in 2-3 sentences why an LLM's confident tone cannot be used as a reliable signal for whether its factual claim is actually true, referencing the training process from earlier in this course.",
                            "difficulty": "medium",
                            "hint": "Recall that instruction-tuning trains the model to sound helpful and fluent, which is a stylistic property independent of factual grounding.",
                        },
                        {
                            "prompt": "Describe, in your own words, the distinction between a hallucination and the model simply repeating a wrong fact that existed in its training data. Give an example of each.",
                            "difficulty": "hard",
                            "hint": "One is the model inventing something with no real grounding at all; the other is the model faithfully reproducing an error that was actually present in what it learned from.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Reducing hallucinations", "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "mitigating-hallucinations",
                    "title": "Mitigating Hallucinations",
                    "description": "Practical, implementable strategies to reduce hallucination and catch it when it happens.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "List concrete prompting strategies that reduce hallucination risk",
                        "Explain why grounding in retrieved sources is the most effective mitigation",
                        "Apply a self-consistency check to detect likely hallucinations",
                        "Design a system that flags low-confidence or ungrounded claims for human review",
                    ],
                    "content_markdown": """
## Why this matters

You cannot eliminate hallucination entirely — it's rooted in the fundamental mechanism covered in the
previous lesson, not a bug you can patch away. But you can meaningfully reduce its likelihood and,
just as importantly, build systems that catch it when it happens rather than presenting fabricated
information to a user with full confidence.

## Strategy 1: Explicitly permit "I don't know"

```python
system_prompt = '''Answer the user's question accurately.
If you are not confident about a specific fact, or if the answer requires
information you don't have reliable access to, explicitly say so rather than guessing.
Do not fabricate specific numbers, dates, or citations you are not confident about.
'''
```

Simply instructing the model that uncertainty is an acceptable, even preferred, response measurably
reduces confident fabrication in many cases — though it is not a guarantee, since the model's own
sense of its "confidence" is itself an imperfect internal signal.

## Strategy 2: Ground answers in retrieved source material (RAG)

This is the single most effective mitigation, and the entire motivation behind Course 5. Instead of
relying on the model's memorized training knowledge, you retrieve actual relevant documents and
include them directly in the prompt, then instruct the model to answer *only* based on the provided
context.

```python
system_prompt = '''Answer the user's question using ONLY the information in the provided context.
If the context does not contain enough information to answer, say so explicitly.
Do not use any outside knowledge beyond what is given in the context below.
'''

prompt_with_context = f'''Context:
{retrieved_documents}

Question: {user_question}
'''
```

Grounding doesn't make hallucination impossible (the model can still misread or misrepresent the
provided context), but it dramatically narrows the gap between "plausible" and "true," since the
model now has real source material to draw from rather than only its training-time memorization.

## Strategy 3: Self-consistency checks

Recall from the previous lesson that sampling randomness can cause hallucinated details to vary
across repeated runs, while well-grounded facts tend to stay consistent. You can exploit this
directly as a detection signal:

```python
def check_consistency(prompt, n_samples=3, temperature=0.7):
    answers = [call_llm(prompt, temperature=temperature) for _ in range(n_samples)]
    unique_answers = set(answers)
    return {
        "answers": answers,
        "consistent": len(unique_answers) == 1,
        "agreement_ratio": answers.count(max(unique_answers, key=answers.count)) / n_samples,
    }

# result = check_consistency("What year was the RFC 9110 standard published?")
# if not result["consistent"]:
#     flag_for_human_review(result)
```

If the same question produces meaningfully different specific answers across several sampled runs,
that disagreement is a useful (though imperfect) signal that the model may be fabricating rather than
recalling a genuinely well-grounded fact.

## Strategy 4: Ask for citations and verify them

Requesting that the model cite its source for a specific claim, and then programmatically checking
that the cited source actually exists and actually supports the claim (rather than trusting the
citation itself, which can also be fabricated), catches a real and common category of hallucination —
plausible-looking but entirely invented references.

## Building a system that flags low-confidence claims

```python
def answer_with_flag(prompt, context=None):
    if context:
        response = call_llm(f"Context:\\n{context}\\n\\nQuestion: {prompt}", temperature=0.0)
    else:
        response = call_llm(prompt, temperature=0.0)
        response += "\\n\\n[NOTE: This answer was not grounded in verified source material.]"
    return response
```

A simple but genuinely useful production pattern: clearly distinguish, in the response itself or in
accompanying metadata, whether an answer was grounded in retrieved context or relied purely on the
model's own training knowledge — giving the end user or downstream system the information needed to
apply appropriate skepticism.

## Looking ahead

Course 5 builds an entire retrieval pipeline around Strategy 2, and Course 12's evaluation module
formalizes Strategies 3 and 4 into automated hallucination-detection tests that run against your
agent's outputs before you ship — this lesson is the conceptual seed for both.
""",
                    "examples": [
                        {
                            "title": "Example: A grounded vs ungrounded prompt side by side",
                            "code": "ungrounded_prompt = \"What was our company's Q3 revenue?\"\n# The model has NO real information about \"our company\" and will likely fabricate a plausible number.\n\ngrounded_prompt = \"\"\"Context: Q3 2025 internal report states revenue was $4.2M, up 12% from Q2.\n\nQuestion: What was our company's Q3 revenue?\"\"\"\n# The model can now answer accurately by reading the provided context instead of guessing.",
                            "explanation": "Contrasts an ungrounded prompt (high hallucination risk, since the model has no real access to this private fact) with a grounded one that supplies the needed information directly, the core RAG mitigation strategy.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Rewrite a system prompt of your choice to explicitly permit the model to say 'I don't know' rather than guessing, following the pattern from Strategy 1.",
                            "difficulty": "easy",
                            "hint": "Add explicit instructions about what to do when the model is uncertain, similar to the lesson's system_prompt example.",
                        },
                        {
                            "prompt": "Implement check_consistency from the lesson (you can simulate call_llm with a function that returns random pre-set answers) and test it with a case that should be flagged as inconsistent and one that should be flagged as consistent.",
                            "difficulty": "medium",
                            "hint": "Use a mock call_llm that sometimes returns different strings and sometimes returns the same string every time.",
                        },
                        {
                            "prompt": "Design (in words, no code required) a full pipeline for an internal company Q&A tool that combines grounding (Strategy 2) and explicit uncertainty flagging (Strategy 1) to minimize hallucination risk, describing each step.",
                            "difficulty": "hard",
                            "hint": "Think through: retrieve relevant internal documents, build a grounded prompt, instruct the model to only use provided context, and flag any answer where the context was insufficient.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Reducing hallucinations", "url": "https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails/reduce-hallucinations", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "llm-limitations",
            "title": "LLM Limitations",
            "description": "Reasoning and knowledge boundaries, and how to match the right model to the right task.",
            "order_index": 10,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "reasoning-and-knowledge-limits",
                    "title": "Reasoning and Knowledge Limits",
                    "description": "Where LLMs genuinely struggle -- knowledge cutoffs, multi-step arithmetic, and consistency over long tasks.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what a knowledge cutoff is and why it exists",
                        "Identify categories of tasks LLMs handle unreliably without external tools",
                        "Explain why LLMs can struggle with precise, multi-step arithmetic",
                        "Connect these limitations directly to the motivation for giving agents tools",
                    ],
                    "content_markdown": """
## Why this matters

Knowing exactly where an LLM's raw capabilities end is what will make you good at designing agents
in Course 9 — nearly every "tool" you give an agent exists specifically to patch one of the gaps
described in this lesson, rather than being an arbitrary feature addition.

## Knowledge cutoffs

A model's training data has a cutoff date — it has no direct knowledge of events, releases, or
information that emerged after that point, since it was never trained on that content. Some models
gain limited awareness of more recent events indirectly (through fine-tuning updates or tool access
like web search), but the base model's core knowledge is fundamentally frozen at training time. This
is precisely why time-sensitive questions ("who won yesterday's game?") are a poor fit for relying on
a model's raw parametric knowledge alone — and exactly the gap RAG (Course 5) and tool use (Course 9)
are designed to fill, by supplying current information at request time instead.

```python
def needs_current_info(question):
    time_sensitive_markers = ["today", "yesterday", "this week", "latest", "current", "right now"]
    return any(marker in question.lower() for marker in time_sensitive_markers)
```

## Precise, multi-step arithmetic

LLMs generate text token by token based on learned patterns, not by executing a guaranteed, exact
calculation procedure the way a calculator does. For simple, common arithmetic the model has likely
seen similar examples of during training, it often gets the right answer; for larger numbers or
multi-step calculations, errors become meaningfully more likely, and the model may confidently state
a wrong result with no internal mechanism forcing it to double-check.

```python
# An LLM asked to compute 847293 * 58201 by "reasoning it through" in text
# is meaningfully more error-prone than a tool call to Python's actual multiplication.
# result = 847293 * 58201  # exact, guaranteed correct via a real calculator/interpreter
```

This single limitation is the direct motivation for giving agents a calculator or code-execution
tool (Course 9) rather than trusting the model's own arithmetic for anything precision-critical.

## Long, complex reasoning chains

While modern LLMs can handle surprisingly sophisticated multi-step reasoning, reliability tends to
degrade as a reasoning chain gets longer and more complex — a single wrong intermediate step early in
a chain can propagate and compound into a confidently wrong final conclusion, since the model has no
built-in mechanism to detect and backtrack from its own earlier reasoning error mid-generation. This
is part of the motivation behind explicit reasoning techniques (chain-of-thought prompting, covered
in Course 4) and reflection loops where a model critiques its own prior output (Course 9's Reflection
skill).

## Consistency across a long task

Because generation is influenced by both the model's learned patterns and sampling randomness
(Temperature and Sampling module), a model asked to maintain a complex set of constraints across a
very long generation can sometimes drift — subtly contradicting an earlier stated fact or instruction
by the time it reaches the end of a long response. This is one reason production systems often break
a large task into smaller, separately verified steps rather than asking for one enormous, complex
output all at once — an architectural pattern you'll build directly in Course 9's planning module.

## These are capability gaps, not unfixable flaws

None of these limitations mean LLMs are unreliable in general — they mean raw, unaided LLM output
should not be trusted blindly for tasks that specifically fall into these known weak categories.
Recognizing exactly *which* category a given task falls into is what lets you decide, task by task,
whether to trust the model directly, ground it with retrieval, or hand it off to a more reliable
external tool.

## Looking ahead

Course 9's entire "Tools" and "Tool Calling" skill area exists to directly address the arithmetic and
current-information gaps from this lesson; Course 12's evaluation module directly tests for
consistency and reasoning-chain reliability using systematic methods built on the ideas introduced
here.
""",
                    "examples": [
                        {
                            "title": "Example: Routing a question based on its risk category",
                            "code": "def route_question(question):\n    if needs_current_info(question):\n        return \"use_web_search_tool\"\n    if any(op in question for op in [\"*\", \"/\", \"calculate\", \"compute\"]):\n        return \"use_calculator_tool\"\n    return \"answer_directly\"\n\nfor q in [\"What's the latest news on AI?\", \"Calculate 4821 * 93\", \"What is a REST API?\"]:\n    print(q, \"->\", route_question(q))",
                            "explanation": "A simple routing function that decides, based on the shape of the question, whether raw LLM knowledge is sufficient or an external tool is needed -- a preview of the tool-routing logic built in Course 9.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List three types of questions where you would trust an LLM's raw answer without any external tool or retrieval, and three types where you would not, justifying each choice.",
                            "difficulty": "medium",
                            "hint": "Consider stable, well-established knowledge versus time-sensitive, precise-arithmetic, or highly specific factual claims.",
                        },
                        {
                            "prompt": "Implement the needs_current_info function from the lesson and test it against at least 5 example questions, some time-sensitive and some not.",
                            "difficulty": "easy",
                            "hint": "The function should return True for questions containing words like 'today', 'latest', or 'current'.",
                        },
                        {
                            "prompt": "Explain, in 2-3 sentences, why breaking a long, complex generation task into smaller separately-verified steps reduces the risk of compounding reasoning errors, using this lesson's explanation of error propagation.",
                            "difficulty": "hard",
                            "hint": "Consider that verifying and correcting an error early, before it's built upon by later steps, prevents that error from silently affecting everything downstream of it.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Claude's constitutional AI and model capabilities overview", "url": "https://docs.anthropic.com/en/docs/about-claude/models", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
                {
                    "slug": "choosing-the-right-model-for-the-job",
                    "title": "Choosing the Right Model for the Job",
                    "description": "A practical framework for matching model capability, cost, and speed to a task's actual requirements.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify the key dimensions along which models differ",
                        "Apply a task-requirements framework to choose an appropriately sized model",
                        "Explain why using the largest available model for every task is often a mistake",
                        "Preview how this decision becomes systematic in a production multi-model system",
                    ],
                    "content_markdown": """
## Why this matters

This lesson closes out the course by turning everything you've learned — tokens, context, inference
cost, sampling, hallucination risk — into a single, practical decision you'll make repeatedly for the
rest of this program: which model should actually handle this task?

## The dimensions models differ along

- **Capability** — how well the model handles complex reasoning, nuanced instructions, and
  challenging edge cases.
- **Speed** — latency per request, directly shaped by model size (recall the Inference module).
- **Cost** — price per token, which typically correlates with model size and capability.
- **Context window size** — how much input the model can consider at once (recall the Context
  Windows module); this can vary meaningfully between models from the same provider.

No single model dominates on all four dimensions simultaneously — a model that's excellent on
capability is rarely also the cheapest and fastest option available.

## A task-requirements framework

Before picking a model, ask:

1. **How complex is the reasoning required?** Simple classification, extraction, or routing tasks
   often don't need a frontier-capability model at all.
2. **How latency-sensitive is this?** A real-time chat interface has very different tolerance than a
   nightly batch job.
3. **What's the cost budget, especially at expected volume?** A cost difference that's negligible for
   10 requests can be significant at 10 million requests.
4. **What's the cost of a wrong answer here?** A high-stakes task (medical, legal, financial content)
   justifies paying for more capability even at higher cost and latency; a low-stakes, easily
   reversible task often doesn't.

```python
def recommend_model(task):
    if task["stakes"] == "high" or task["reasoning_complexity"] == "high":
        return "large-capable-model"
    if task["latency_sensitive"] and task["reasoning_complexity"] == "low":
        return "small-fast-model"
    return "medium-model"

example_task = {"stakes": "low", "reasoning_complexity": "low", "latency_sensitive": True}
print(recommend_model(example_task))  # small-fast-model
```

## Why "always use the biggest model" is often a mistake

Beyond the direct cost and latency downsides (Inference module), there are two subtler reasons:
first, a larger, more capable model doesn't automatically produce better results on a genuinely
simple, well-scoped task — the ceiling on quality for "classify this ticket as urgent or not" is
often already reached by a much smaller model. Second, at scale, an unnecessarily expensive default
model choice compounds into a real, ongoing cost burden across every single request your system ever
serves, which Course 13's production economics module treats as a first-class design constraint, not
an afterthought.

## Multi-model systems in production

Real production systems commonly route different tasks to different models, rather than picking one
model for the entire application:

```python
def process_ticket(ticket_text):
    category = call_llm(ticket_text, model="small-fast-model")   # cheap classification step
    if category == "complex_technical_issue":
        return call_llm(ticket_text, model="large-capable-model")  # escalate only when needed
    return call_llm(ticket_text, model="small-fast-model")
```

This pattern — cheap model for routing/triage, expensive model only for the subset of cases that
genuinely need it — appears constantly in production AI systems and directly previews Course 12's
Multi-Agent Systems material, where different specialized agents (often backed by different models)
handle different parts of a larger workflow.

## Looking ahead

This lesson closes Course 3. From here, Course 4 (Prompt Engineering) assumes you can already reason
about tokens, context, roles, sampling, hallucination risk, and model choice — and focuses
specifically on how to write the actual prompt text and structure that gets the most reliable
behavior out of whichever model you've chosen for the task at hand.
""",
                    "examples": [
                        {
                            "title": "Example: A two-tier triage-then-escalate pattern",
                            "code": "def recommend_model(task):\n    if task[\"stakes\"] == \"high\" or task[\"reasoning_complexity\"] == \"high\":\n        return \"large-capable-model\"\n    if task[\"latency_sensitive\"] and task[\"reasoning_complexity\"] == \"low\":\n        return \"small-fast-model\"\n    return \"medium-model\"\n\ntasks = [\n    {\"name\": \"spam triage\", \"stakes\": \"low\", \"reasoning_complexity\": \"low\", \"latency_sensitive\": True},\n    {\"name\": \"legal contract review\", \"stakes\": \"high\", \"reasoning_complexity\": \"high\", \"latency_sensitive\": False},\n]\nfor t in tasks:\n    print(t[\"name\"], \"->\", recommend_model(t))",
                            "explanation": "Applies the recommend_model function to two realistically different tasks, showing the framework producing sensible, different model choices for each.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Using the recommend_model function and framework from the lesson, classify these three tasks by their stakes, reasoning_complexity, and latency_sensitive attributes, then determine which model tier each should use: (1) auto-tagging blog post topics, (2) drafting a response to a medical question, (3) a real-time customer chat greeting.",
                            "difficulty": "medium",
                            "hint": "Consider the real-world consequence of a wrong answer for each task when assigning 'stakes'.",
                        },
                        {
                            "prompt": "Implement the two-tier triage-then-escalate process_ticket pattern from the lesson (you can mock call_llm), and test it with an input that should stay on the cheap model and one that should escalate.",
                            "difficulty": "medium",
                            "hint": "Have your mock call_llm return 'complex_technical_issue' for one test input and something else for another.",
                        },
                        {
                            "prompt": "Write a short argument (3-4 sentences) for why a company serving millions of simple classification requests per day should NOT default to its most capable, most expensive model for every single one, referencing both cost and the 'ceiling effect' idea from this lesson.",
                            "difficulty": "hard",
                            "hint": "Connect per-request cost multiplied by huge volume to the fact that a simple task's quality ceiling is often already met by a cheaper model.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Choosing the right model", "url": "https://docs.anthropic.com/en/docs/about-claude/models/choosing-a-model", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "llm", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "LLM Fundamentals: Course Assessment",
    "description": "Checks readiness to move from LLM fundamentals into Prompt Engineering.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 35,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "At its core, what does a language model do at each step of generation?",
            "options": [
                {"id": "a", "text": "Looks up the exact answer in a stored database of facts"},
                {"id": "b", "text": "Predicts a probability distribution over the next token given the context so far"},
                {"id": "c", "text": "Randomly selects any word from the entire dictionary"},
                {"id": "d", "text": "Executes a fixed, hand-written set of grammar rules"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A language model's core mechanism is predicting the next token's probability distribution given prior context, then selecting a token from that distribution via some decoding strategy.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "Why do LLMs use subword tokenization instead of treating each whole word as a single unit?",
            "options": [
                {"id": "a", "text": "Subword tokenization makes text generation slower"},
                {"id": "b", "text": "A whole-word vocabulary would need to be impractically large and still couldn't cover every possible word, name, or typo"},
                {"id": "c", "text": "Subwords are required by law for AI systems"},
                {"id": "d", "text": "It has no effect on vocabulary size"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Subword tokenization keeps the vocabulary manageable while still being able to represent rare words, typos, and unfamiliar terms by breaking them into smaller, more common pieces.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "tokens",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function estimate_cost(input_tokens, output_tokens, input_price, output_price) that returns the total cost given per-million-token prices, matching the formula used in this course.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Returns (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price.",
                "sample_solution": "def estimate_cost(input_tokens, output_tokens, input_price, output_price):\n    return (input_tokens / 1_000_000) * input_price + (output_tokens / 1_000_000) * output_price",
            },
            "explanation": "This mirrors the cost calculation from the Token Limits and Cost lesson, reinforcing that input and output tokens are typically priced separately at different per-token rates.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "tokens",
        },
        {
            "question_type": "mcq",
            "prompt": "What happens, architecturally, when a request's total token count (input + requested output) would exceed a model's context window?",
            "options": [
                {"id": "a", "text": "The model silently ignores the earliest part of the input with no error"},
                {"id": "b", "text": "The API typically returns an explicit error rather than silently truncating the request"},
                {"id": "c", "text": "The model automatically switches to a larger context window"},
                {"id": "d", "text": "Context windows have no maximum size in modern LLMs"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Providers generally fail loudly with an explicit error when a request would exceed the context window, so developers notice and handle the problem rather than receiving silently degraded output.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are valid strategies for managing a long-running conversation's growing token cost? (Select all that apply.)",
            "options": [
                {"id": "a", "text": "Summarizing older messages into a compact summary"},
                {"id": "b", "text": "Keeping only the most recent N messages (sliding window)"},
                {"id": "c", "text": "Trimming based on an actual token budget rather than a fixed message count"},
                {"id": "d", "text": "Always resending the full, untrimmed history on every single turn regardless of length"},
            ],
            "correct_answer": {"choices": ["a", "b", "c"]},
            "explanation": "Summarization, sliding windows, and token-budget-aware trimming are all valid strategies covered in this course; always resending the full untrimmed history is exactly the problem these strategies solve.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "Why did the transformer architecture largely replace recurrent neural networks (RNNs) for language modeling?",
            "options": [
                {"id": "a", "text": "Transformers use less memory than RNNs in every case"},
                {"id": "b", "text": "Self-attention lets every token access every other token directly and allows far more parallel computation than RNNs' strictly sequential processing"},
                {"id": "c", "text": "RNNs cannot process text at all"},
                {"id": "d", "text": "Transformers do not require any training data"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Self-attention removes the strict sequential dependency of RNNs, enabling both better long-range context handling and far more parallelizable training on modern hardware.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "transformers",
        },
        {
            "question_type": "mcq",
            "prompt": "In the query/key/value framing of self-attention, what does the 'value' represent?",
            "options": [
                {"id": "a", "text": "The current token's search request"},
                {"id": "b", "text": "The actual content/information a token contributes if it's deemed relevant"},
                {"id": "c", "text": "A token's position in the sequence"},
                {"id": "d", "text": "The final probability distribution over the next token"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The value is the information a token contributes to the weighted output once it's been determined to be relevant, analogous to the actual content returned by a matching search result.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "transformers",
        },
        {
            "question_type": "mcq",
            "prompt": "Why does a longer expected OUTPUT length typically increase LLM response latency more than an equivalently sized increase in INPUT length?",
            "options": [
                {"id": "a", "text": "Output tokens cost more money, which directly causes slower processing"},
                {"id": "b", "text": "Input (prefill) can be processed largely in parallel, while output (decode) must be generated sequentially, one token at a time"},
                {"id": "c", "text": "Output text uses a different, slower tokenizer than input text"},
                {"id": "d", "text": "There is no meaningful difference between input and output length effects on latency"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The prefill phase processes the entire input in parallel, while the decode phase is inherently sequential -- each output token depends on all previous ones -- making output length a stronger driver of total latency.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the key difference between top-k and top-p (nucleus) sampling?",
            "options": [
                {"id": "a", "text": "Top-k always considers a fixed number of top candidates; top-p considers however many candidates are needed to reach a cumulative probability threshold"},
                {"id": "b", "text": "Top-p is fully deterministic while top-k is always random"},
                {"id": "c", "text": "Top-k can only be used with temperature 0"},
                {"id": "d", "text": "They are mathematically identical, just named differently"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Top-k uses a fixed candidate pool size, while top-p adapts the pool size based on cumulative probability, making it more sensitive to how confident or uncertain the underlying distribution is.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "For a task that requires extracting a single, exact, repeatable number from a document every time, which temperature setting is most appropriate?",
            "options": [
                {"id": "a", "text": "A high temperature, around 1.5-2.0, for creative flexibility"},
                {"id": "b", "text": "A low temperature, near 0, to favor consistent, focused output"},
                {"id": "c", "text": "Temperature has no effect on this kind of task"},
                {"id": "d", "text": "Temperature should be set randomly for each request"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Tasks needing consistent, repeatable, precise output should use low temperature to minimize randomness in token selection, closely approximating deterministic greedy decoding.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "llm",
        },
        {
            "question_type": "scenario",
            "prompt": "You're building a customer-facing chatbot and notice it sometimes fabricates specific product return policy details that don't match your company's actual documented policy. Using concepts from this course, describe at least two concrete changes you would make to reduce this, and explain the mechanism behind why each change helps.",
            "options": [],
            "correct_answer": {
                "expected": "Ground the model's answers in the actual retrieved return policy document text (RAG-style grounding) instead of relying on its own memorized/training knowledge, and instruct it explicitly (via the system prompt) to answer only from the provided context and say so when the context doesn't cover the question, rather than guessing. Optionally, run a self-consistency check across multiple samples to detect answers that vary suspiciously between runs.",
            },
            "explanation": "This scenario checks whether the student can apply the mitigation strategies from the Hallucinations module (grounding, explicit permission to express uncertainty, self-consistency checks) to a realistic, concrete production problem.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "llm",
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain, in 2-3 sentences, why an LLM's confident, fluent tone is not a reliable indicator that its factual claim is actually true.",
            "options": [],
            "correct_answer": {
                "expected": "LLMs are trained via next-token prediction and instruction-tuning to produce fluent, confident-sounding text, which is a stylistic property learned independently of whether any specific factual claim within that text is actually grounded or true. Hallucinated and accurate statements can both be generated with the same confident tone.",
                "keywords": ["fluency", "confidence", "hallucination", "training", "not the same as truth"],
            },
            "explanation": "This captures the central insight of the hallucination module: tone and factual correctness are produced by different (and not necessarily correlated) aspects of how the model was trained and how it generates text.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "Why are LLMs generally unreliable for precise, multi-step arithmetic compared to a calculator or code execution tool?",
            "options": [
                {"id": "a", "text": "LLMs are not allowed to output numbers"},
                {"id": "b", "text": "LLMs generate answers based on learned text patterns rather than executing a guaranteed, exact calculation procedure"},
                {"id": "c", "text": "Arithmetic tokens are removed from LLM vocabularies"},
                {"id": "d", "text": "This is not actually true; LLMs are always as reliable as calculators"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Because LLMs predict plausible token sequences rather than executing exact algorithms, larger or more complex calculations become increasingly error-prone -- exactly why agent frameworks give models a calculator or code-execution tool instead of trusting raw arithmetic output.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
        {
            "question_type": "mcq",
            "prompt": "A company processes millions of simple, low-stakes classification requests per day and is deciding which model to use. According to this course's model-selection framework, what is the most likely mistake to avoid?",
            "options": [
                {"id": "a", "text": "Using a small, fast, cheap model for all of them"},
                {"id": "b", "text": "Defaulting to the largest, most expensive, most capable model for every single request regardless of actual task complexity"},
                {"id": "c", "text": "Ever using more than one model in the same system"},
                {"id": "d", "text": "Measuring cost at all"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "For simple, well-scoped, low-stakes tasks at high volume, defaulting to the largest available model wastes cost and latency without improving output quality, since the task's quality ceiling is often already met by a smaller model.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "llm",
        },
    ],
}
