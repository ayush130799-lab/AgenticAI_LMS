"""
Course 9: LangChain

Covers building LLM applications with LangChain: the model I/O abstraction,
prompt templates, tool binding, agents, retrieval, memory, and structured
output. This is where the agent-architecture concepts from Course 8 (state,
tools, memory, planning) get implemented against a real, widely-used
framework instead of hand-rolled loops.
"""

COURSE = {
    "slug": "langchain",
    "title": "LangChain",
    "subtitle": "Building LLM applications with composable chains, tools, and agents",
    "description": (
        "A hands-on tour of LangChain's core abstractions: the Runnable interface "
        "and LCEL for composing chains, chat models and prompt templates for "
        "structured LLM I/O, tool binding and tool-calling agents, retrieval "
        "chains over your own documents, conversation memory, and structured "
        "output with Pydantic. You'll leave able to build a real, tool-using, "
        "retrieval-augmented agent on top of LangChain rather than from scratch."
    ),
    "learning_outcomes": [
        "Compose LCEL chains from prompts, models, and parsers using the Runnable interface",
        "Swap chat model providers without rewriting application logic",
        "Design prompt templates with partial variables and few-shot examples",
        "Define and bind tools to chat models for structured tool calling",
        "Build a tool-calling agent with AgentExecutor and inspect its intermediate steps",
        "Build a retrieval chain over custom documents using loaders, splitters, and a vector store",
        "Add conversation memory and persist chat history across sessions",
        "Get validated, structured output from a chat model using Pydantic schemas",
    ],
    "order_index": 9,
    "estimated_hours": 14,
    "level": "intermediate",
    "icon": "link",
    "modules": [
        # 1. LangChain Fundamentals
        {
            "slug": "langchain-fundamentals",
            "title": "LangChain Fundamentals",
            "description": "What problem LangChain solves, when it's the right tool, and the Runnable/LCEL abstraction everything else in the framework is built on.",
            "order_index": 1,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "what-langchain-solves-and-when-to-use-it",
                    "title": "What LangChain Solves and When to Use It",
                    "description": "The gap between a raw model API call and a production LLM application, and where LangChain fits.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the gap between a raw model API call and a full LLM application",
                        "Identify which parts of that gap LangChain standardizes",
                        "Recognize scenarios where a raw API call is simpler and preferable",
                        "Install and configure LangChain for a chat model provider",
                    ],
                    "content_markdown": """## The gap between "call the model" and "build the application"

A raw call to a model API returns text given text. Almost every real
application needs more: swappable prompts, structured output, tools the
model can invoke, retrieval over your own documents, memory across turns,
and a way to compose all of these into a pipeline you can test and reuse.
Writing all of that by hand, for every project, means re-solving the same
plumbing problems repeatedly. **LangChain** is a library of standardized
abstractions for exactly this plumbing: prompts, models, output parsers,
tools, retrievers, and memory, all expressed through one composable
interface.

## Installing and configuring

```python
# pip install langchain langchain-openai
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
response = llm.invoke("What is the capital of France?")
print(response.content)
```

`ChatOpenAI` is a **chat model wrapper** — one of several provider-specific
packages (`langchain-anthropic`, `langchain-google-genai`, and others) that
all implement the same interface. That shared interface is the whole value
proposition: your application code calls `.invoke()` the same way regardless
of which provider sits behind it, a point the next lesson in this module
builds on directly.

## When LangChain is the right choice — and when it isn't

LangChain earns its keep once you need at least two or three of: prompt
templating, tool calling, retrieval, memory, or provider portability, wired
together into a pipeline you'll iterate on. For a single, one-off API call
with no templating and no composition, the abstraction layer adds
indirection without buying you anything — a raw `openai` or `anthropic` SDK
call is simpler and more transparent. Treat LangChain as a tool for
*applications*, not a mandatory wrapper around every model call you'll ever
make.

## The mental model going forward

Every module in this course builds one more piece onto the same underlying
idea: a **Runnable** — a standard unit of "takes input, produces output,
composable with other Runnables" — that prompts, models, parsers, retrievers,
and even whole agents all implement. Once that clicks (the focus of the next
lesson), the rest of LangChain's surface area stops looking like a long list
of unrelated classes and starts looking like variations on one consistent
pattern.
""",
                    "examples": [
                        {
                            "title": "The same interface across two different providers",
                            "code": (
                                "from langchain_openai import ChatOpenAI\n"
                                "from langchain_anthropic import ChatAnthropic\n\n"
                                "openai_llm = ChatOpenAI(model=\"gpt-4o-mini\")\n"
                                "claude_llm = ChatAnthropic(model=\"claude-3-5-sonnet-20241022\")\n\n"
                                "for llm in (openai_llm, claude_llm):\n"
                                "    print(llm.invoke(\"Say hello in one word.\").content)"
                            ),
                            "explanation": "Both wrappers expose the same .invoke() method, so application code above this layer doesn't need to know which provider it's talking to.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Install langchain and langchain-openai, set an API key, and make a single .invoke() call that asks a model to explain what an AI agent is in one sentence.",
                            "difficulty": "easy",
                            "hint": "Remember to set the OPENAI_API_KEY environment variable before instantiating ChatOpenAI.",
                        },
                        {
                            "prompt": "List three concrete features (from the lesson) that would justify using LangChain for a project, and one scenario where a raw API call would be simpler.",
                            "difficulty": "easy",
                            "hint": "Think about templating, tool calling, retrieval, memory, and provider portability.",
                        },
                        {
                            "prompt": "Explain, in your own words, why having a shared interface across model providers matters for an application that might need to switch providers later.",
                            "difficulty": "medium",
                            "hint": "Consider what would need to change in your application code with and without that shared interface.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain Python documentation", "url": "https://python.langchain.com/docs/introduction/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
                {
                    "slug": "core-abstractions-runnables-and-lcel",
                    "title": "Core Abstractions: Runnables and LCEL",
                    "description": "The Runnable interface and the LangChain Expression Language (LCEL) for composing prompts, models, and parsers with the pipe operator.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain what makes an object a Runnable in LangChain",
                        "Compose a chain using the | (pipe) operator",
                        "Use .invoke(), .stream(), and .batch() on a composed chain",
                        "Read and reason about a multi-step LCEL chain",
                    ],
                    "content_markdown": """## Runnable: one interface, everywhere

A **Runnable** is anything in LangChain that implements a consistent set of
methods — `.invoke()` for a single call, `.batch()` for many inputs at once,
`.stream()` for token-by-token output — regardless of whether it's a prompt
template, a chat model, an output parser, or a retriever. This uniformity is
what makes composition possible: since every piece speaks the same
interface, you can chain them together generically.

## LCEL: composing with the pipe operator

The **LangChain Expression Language (LCEL)** lets you build a chain by
piping Runnables together with `|`, similar to a Unix pipeline:

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI

prompt = ChatPromptTemplate.from_template(
    "Explain {concept} to a beginner in two sentences."
)
model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
parser = StrOutputParser()

chain = prompt | model | parser

result = chain.invoke({"concept": "vector embeddings"})
print(result)  # a plain string, already parsed out of the model's response object
```

Reading this left to right: the input dict flows into `prompt`, which
produces a formatted set of chat messages; those flow into `model`, which
produces a message object; that flows into `parser`, which extracts just the
text content. Each `|` is function composition — `chain = parser(model(prompt(x)))`
written in a more readable, pipeline-like order.

## The three core call patterns

Every chain, being a Runnable, supports the same three ways of being called:

```python
chain.invoke({"concept": "gradient descent"})              # one input, one output
chain.batch([{"concept": "RAG"}, {"concept": "tokenization"}])  # many inputs, run efficiently
for chunk in chain.stream({"concept": "transformers"}):     # token-by-token output
    print(chunk, end="", flush=True)
```

`.batch()` is not just a for-loop in disguise — LangChain can parallelize or
otherwise optimize batched calls to a provider, which matters once you're
processing more than a handful of inputs. `.stream()` matters for anything
user-facing, where showing partial output as it's generated feels far more
responsive than waiting for a complete response.

## Why this abstraction pays off

Because a chain is itself a Runnable, chains compose into bigger chains the
same way their pieces did:

```python
translate_prompt = ChatPromptTemplate.from_template("Translate to French: {text}")
translate_chain = translate_prompt | model | parser

full_chain = chain | (lambda explanation: {"text": explanation}) | translate_chain
```

This composability is what lets LangChain scale from a two-line chain to the
much more elaborate retrieval and agent chains you'll build later in this
course, without introducing a fundamentally new mental model at each step —
it's always prompt, model, parser, retriever, and now chain, all
interoperating through the same `|` composition.
""",
                    "examples": [
                        {
                            "title": "Inspecting a chain's structure",
                            "code": (
                                "chain = prompt | model | parser\n"
                                "print(chain)\n"
                                "# RunnableSequence(first=ChatPromptTemplate(...), middle=[ChatOpenAI(...)], last=StrOutputParser())"
                            ),
                            "explanation": "LCEL chains are ordinary Python objects you can inspect, not a hidden DSL, which makes debugging straightforward.",
                        },
                        {
                            "title": "Streaming a chain's output to the console",
                            "code": (
                                "chain = prompt | model | parser\n"
                                "for token in chain.stream({\"concept\": \"attention mechanisms\"}):\n"
                                "    print(token, end=\"\", flush=True)"
                            ),
                            "explanation": "Because StrOutputParser is streaming-aware, tokens are printed as they arrive rather than all at once at the end.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build an LCEL chain that takes a {topic} and a {tone} variable, formats a prompt asking for a one-paragraph explanation in that tone, and parses the result as a plain string.",
                            "difficulty": "easy",
                            "hint": "Use ChatPromptTemplate.from_template with two placeholders.",
                        },
                        {
                            "prompt": "Use .batch() to run your chain from the previous exercise over three different topics in a single call, and print each result.",
                            "difficulty": "medium",
                            "hint": "Pass a list of dicts, one per invocation, to .batch().",
                        },
                        {
                            "prompt": "Explain what would break if you swapped the order of model and parser in a chain (parser | model instead of model | parser), and why LCEL doesn't prevent this at chain-construction time.",
                            "difficulty": "medium",
                            "hint": "Think about what type of object StrOutputParser expects as its input versus what a prompt template produces.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: LCEL", "url": "https://python.langchain.com/docs/concepts/lcel/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
            ],
        },
        # 2. Models
        {
            "slug": "models",
            "title": "Models",
            "description": "The chat model abstraction that standardizes calling any LLM provider, and how to switch providers without touching application logic.",
            "order_index": 2,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "chat-models-and-the-model-io-abstraction",
                    "title": "Chat Models and the Model I/O Abstraction",
                    "description": "How LangChain represents chat messages and model responses, and the configuration knobs available on every chat model.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Construct and pass HumanMessage, AIMessage, and SystemMessage objects",
                        "Configure common chat model parameters: temperature, max_tokens, timeout",
                        "Inspect a chat model response's metadata, including token usage",
                        "Explain the role of the model I/O abstraction in provider independence",
                    ],
                    "content_markdown": """## Messages as typed objects, not raw strings

LangChain represents a conversation as a list of typed message objects
rather than a single formatted string — `SystemMessage`, `HumanMessage`, and
`AIMessage`, mirroring the roles you'd send directly to a chat completion
API:

```python
from langchain_core.messages import SystemMessage, HumanMessage

messages = [
    SystemMessage(content="You are a concise technical writing assistant."),
    HumanMessage(content="Summarize what a vector database does in one sentence."),
]
response = llm.invoke(messages)
print(response.content)      # the text
print(response.response_metadata)  # provider-specific metadata, including token usage
```

Using typed objects instead of raw dicts or strings means your IDE and
LangChain itself can catch structural mistakes (passing a string where a
message list is expected) before you make an API call, and it keeps the role
of each piece of text explicit rather than implicit in string formatting.

## Configuring a chat model

Every chat model wrapper exposes a consistent set of configuration
parameters, since they all implement the same base interface:

```python
llm = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.2,     # lower = more deterministic, higher = more varied
    max_tokens=500,       # cap on response length
    timeout=30,           # seconds before the call is aborted
    max_retries=2,        # built-in retry handling for transient failures
)
```

Notice `max_retries` — LangChain's chat model wrappers already implement the
retry logic covered in Course 8's Retries module for you, for the common
case of transient API failures. You don't need to hand-roll a retry wrapper
around every model call, though the principles from that module (what's
retryable, backoff behavior) are exactly what's happening under the hood.

## Reading response metadata

A chat model response carries more than just text:

```python
response = llm.invoke("Explain RAG briefly.")
print(response.usage_metadata)
# {'input_tokens': 12, 'output_tokens': 48, 'total_tokens': 60}
```

Token usage metadata is essential for cost monitoring in any production
system — logging it per call lets you track spend and catch runaway prompts
before they become a billing surprise.

## Why this abstraction is the foundation for portability

Because every chat model wrapper accepts the same message format and
exposes the same configuration and response shape, application code written
against `ChatOpenAI` continues working almost unchanged if you swap in
`ChatAnthropic` or another provider — the next lesson makes this concrete.
This is the direct payoff of standardizing model I/O: your prompts, chains,
and agents stop being tied to one vendor's specific API shape.
""",
                    "examples": [
                        {
                            "title": "A full message-based conversation turn",
                            "code": (
                                "from langchain_core.messages import SystemMessage, HumanMessage, AIMessage\n\n"
                                "conversation = [\n"
                                "    SystemMessage(content=\"You are a helpful Python tutor.\"),\n"
                                "    HumanMessage(content=\"What does *args do?\"),\n"
                                "    AIMessage(content=\"It collects extra positional arguments into a tuple.\"),\n"
                                "    HumanMessage(content=\"Show me a one-line example.\"),\n"
                                "]\n"
                                "response = llm.invoke(conversation)"
                            ),
                            "explanation": "Prior turns are represented as explicit AIMessage objects in the list, which is how conversational context is threaded through multiple calls.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Construct a 4-message conversation (system, human, ai, human) and invoke a chat model on it, printing the final response's content.",
                            "difficulty": "easy",
                            "hint": "Import all three message types from langchain_core.messages.",
                        },
                        {
                            "prompt": "Configure a ChatOpenAI instance with temperature=0 and max_tokens=50, and observe how the response differs from a default-configured instance on the same prompt.",
                            "difficulty": "easy",
                            "hint": "Try the same prompt against two differently configured instances and compare outputs.",
                        },
                        {
                            "prompt": "Write a small helper function that logs input_tokens, output_tokens, and an estimated dollar cost (given a per-token price) after every .invoke() call.",
                            "difficulty": "medium",
                            "hint": "Read from response.usage_metadata after the call returns.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Chat models", "url": "https://python.langchain.com/docs/concepts/chat_models/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
                {
                    "slug": "swapping-providers-without-rewriting-your-app",
                    "title": "Swapping Providers Without Rewriting Your App",
                    "description": "Using LangChain's provider-agnostic interface to change models with a one-line swap, and designing for that flexibility deliberately.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Swap a chat model provider in an existing chain with a single-line change",
                        "Use init_chat_model for config-driven provider selection",
                        "Identify provider-specific behavior that portability does not paper over",
                        "Design an application to keep model selection at its edges, not scattered through the code",
                    ],
                    "content_markdown": """## The one-line swap

Because chat model wrappers share an interface, changing which provider or
model powers a chain is typically a one-line change at the point where the
model is constructed — nothing in the prompt, chain, or downstream logic
needs to change:

```python
# Before
from langchain_openai import ChatOpenAI
model = ChatOpenAI(model="gpt-4o-mini")

# After
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(model="claude-3-5-sonnet-20241022")

# Everything below is untouched
chain = prompt | model | parser
```

This matters commercially, not just academically: providers change pricing,
rate limits, and capabilities regularly, and being able to switch without a
rewrite is real optionality you'd otherwise have to build yourself.

## `init_chat_model`: provider selection as configuration

For applications that need to choose a provider at runtime (from an
environment variable, a config file, or a feature flag), LangChain provides
`init_chat_model`, which takes a model identifier string and resolves the
right wrapper automatically:

```python
from langchain.chat_models import init_chat_model

model_name = "openai:gpt-4o-mini"  # or "anthropic:claude-3-5-sonnet-20241022"
model = init_chat_model(model_name, temperature=0)
```

This turns "which model powers this feature" into a configuration value
rather than a code change, which is exactly the kind of flexibility you want
once you're running experiments (comparing providers on quality or cost) or
supporting customers who require a specific vendor for compliance reasons.

## What portability does NOT solve

The shared interface standardizes *how* you call a model, not *how the model
behaves*. Different providers vary in context window size, tool-calling
reliability, latency, and how they handle edge cases like empty responses or
refusals. A chain that works flawlessly against one provider can still need
prompt adjustments against another — portability removes the mechanical
rewrite, not the need to validate behavior on the new provider before
shipping.

```python
# Always re-test after a provider swap, don't assume identical behavior
for test_input in test_cases:
    result = chain.invoke(test_input)
    assert meets_quality_bar(result), f"regression on {test_input}"
```

## Keep model selection at the edges

A design discipline worth adopting early: construct your model object in one
place (a config module, a factory function) and pass it into your chains,
rather than importing a specific provider's wrapper directly inside business
logic scattered across the codebase. This is the same principle as
dependency injection in traditional software design, and it's what makes
the "one-line swap" actually be one line, instead of a search-and-replace
across dozens of files.
""",
                    "examples": [
                        {
                            "title": "A model factory that centralizes provider selection",
                            "code": (
                                "def get_model(purpose: str = \"default\"):\n"
                                "    from langchain.chat_models import init_chat_model\n"
                                "    config = {\"default\": \"openai:gpt-4o-mini\", \"summarize\": \"anthropic:claude-3-5-sonnet-20241022\"}\n"
                                "    return init_chat_model(config[purpose], temperature=0)\n\n"
                                "chain = prompt | get_model(\"summarize\") | parser"
                            ),
                            "explanation": "Every chain requests a model through this single factory function, so changing providers means editing one dict, not hunting through the codebase.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a get_model(purpose) factory function like the one in the example, supporting at least two named purposes mapped to two different models.",
                            "difficulty": "easy",
                            "hint": "A plain dict lookup is sufficient for this exercise.",
                        },
                        {
                            "prompt": "Take an existing chain and run the same set of 3 test inputs against two different providers, comparing the outputs for meaningful differences.",
                            "difficulty": "medium",
                            "hint": "Look for differences in tone, length, or refusal behavior, not just wording.",
                        },
                        {
                            "prompt": "Describe a concrete scenario where swapping providers would require a prompt change even though the LangChain code itself required none.",
                            "difficulty": "medium",
                            "hint": "Consider a provider that is stricter about following formatting instructions than another.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: init_chat_model", "url": "https://python.langchain.com/docs/how_to/chat_models_universal_init/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
            ],
        },
        # 3. Prompts
        {
            "slug": "prompts",
            "title": "Prompts",
            "description": "Templating prompts for reuse and variation, including partial variables and few-shot examples that steer model behavior reliably.",
            "order_index": 3,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "prompt-templates-and-partial-variables",
                    "title": "Prompt Templates and Partial Variables",
                    "description": "Building reusable ChatPromptTemplate objects, and pre-filling some variables while leaving others to be supplied at call time.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Build a ChatPromptTemplate from a multi-message template",
                        "Fill template variables at invocation time",
                        "Use partial variables to pre-bind values that don't change per call",
                        "Explain why templating beats string formatting for prompt maintenance",
                    ],
                    "content_markdown": """## Why not just use an f-string?

You could format a prompt with a plain Python f-string, and for a one-off
script that's fine. It stops being fine once a prompt is reused across
several chains, needs to combine a system message with structured
placeholders, or needs values filled in at different points in your
pipeline. `ChatPromptTemplate` gives you a reusable, composable, inspectable
object instead of a scattered pile of string formatting.

```python
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role} who explains things at a {level} level."),
    ("human", "{question}"),
])

formatted = prompt.invoke({"role": "physics teacher", "level": "high-school", "question": "What is entropy?"})
```

`prompt.invoke(...)` returns a `ChatPromptValue` — itself a Runnable output —
which is what feeds directly into a chat model in an LCEL chain
(`prompt | model`), as you saw in the LCEL lesson.

## Partial variables: fill some now, the rest later

Often some variables are fixed for a given use case (the `role` in the
example above rarely changes within one deployment) while others genuinely
vary per call (`question` always does). `.partial()` lets you bind the
former ahead of time:

```python
physics_prompt = prompt.partial(role="physics teacher", level="high-school")

# Later, at call time, only the remaining variable needs to be supplied
physics_prompt.invoke({"question": "What is entropy?"})
physics_prompt.invoke({"question": "Why does ice float?"})
```

This is a small thing syntactically but a meaningful thing architecturally:
it separates configuration (what kind of assistant this is) from per-request
input (what the user actually asked), which keeps call sites clean and
prevents the same fixed values from being repeated at every invocation.

## Dynamic partials

Partial values can also be functions, evaluated fresh at call time — useful
for things like the current date that change but aren't supplied by the
caller:

```python
from datetime import date

dated_prompt = prompt.partial(role="assistant", level=lambda: "expert")
# or, for a value like today's date:
prompt_with_date = ChatPromptTemplate.from_messages([
    ("system", "Today's date is {today}."),
    ("human", "{question}"),
]).partial(today=lambda: date.today().isoformat())
```

## Templating as maintenance discipline

Once a prompt is a `ChatPromptTemplate` object rather than an inline string,
it becomes something you can version, test, and reuse across multiple
chains — you can write a unit test that asserts a template formats correctly
given known inputs, something that's awkward to do cleanly with scattered
f-strings. As your application grows past a handful of prompts, this
discipline is what keeps prompt maintenance from becoming unmanageable.
""",
                    "examples": [
                        {
                            "title": "Inspecting a formatted prompt before sending it",
                            "code": (
                                "formatted = prompt.invoke({\"role\": \"tutor\", \"level\": \"beginner\", \"question\": \"What is a loop?\"})\n"
                                "for message in formatted.to_messages():\n"
                                "    print(message.type, \":\", message.content)"
                            ),
                            "explanation": "Inspecting the formatted messages before sending them to a model is a fast way to catch templating bugs without spending an API call.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a ChatPromptTemplate with a system message that includes a {domain} placeholder and a human message with a {query} placeholder, then invoke it with two different domains.",
                            "difficulty": "easy",
                            "hint": "Use from_messages with a list of (role, template) tuples.",
                        },
                        {
                            "prompt": "Use .partial() to fix the {domain} value for a specific use case, so downstream code only needs to supply {query}.",
                            "difficulty": "easy",
                            "hint": "Call .partial(domain='...') on the template object.",
                        },
                        {
                            "prompt": "Add a dynamic partial variable that inserts the current day of the week into the system message, without the caller ever supplying it.",
                            "difficulty": "medium",
                            "hint": "Pass a zero-argument callable as the partial value.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Prompt templates", "url": "https://python.langchain.com/docs/concepts/prompt_templates/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
                {
                    "slug": "few-shot-prompting-with-example-selectors",
                    "title": "Few-Shot Prompting with Example Selectors",
                    "description": "Embedding worked examples into a prompt to steer output format and style, and selecting the most relevant examples dynamically.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Build a FewShotChatMessagePromptTemplate from a fixed list of examples",
                        "Explain why worked examples often outperform pure instruction for format-sensitive tasks",
                        "Use a semantic example selector to pick the most relevant examples per query",
                        "Balance example count against token cost",
                    ],
                    "content_markdown": """## Show, don't just tell

For tasks where output format or style matters — classification labels, a
specific JSON shape, a particular tone — showing the model a few worked
examples is often more reliable than describing the requirement in prose
alone. This is **few-shot prompting**, and LangChain provides
`FewShotChatMessagePromptTemplate` to build it as a reusable, composable
piece rather than a hand-assembled string.

```python
from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

examples = [
    {"input": "The product broke after one day.", "output": "negative"},
    {"input": "Shipping was faster than expected!", "output": "positive"},
    {"input": "It's fine, does what it says.", "output": "neutral"},
]

example_prompt = ChatPromptTemplate.from_messages([
    ("human", "{input}"),
    ("ai", "{output}"),
])

few_shot_prompt = FewShotChatMessagePromptTemplate(
    examples=examples,
    example_prompt=example_prompt,
)

final_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the sentiment of the review as positive, negative, or neutral."),
    few_shot_prompt,
    ("human", "{input}"),
])
```

The `few_shot_prompt` slots directly into the larger `final_prompt` as one
more message block — the composability from the LCEL lesson applies to
prompt construction too, not just chains.

## Selecting examples dynamically

A fixed set of examples works fine for a small, stable example pool. Once
you have dozens or hundreds of potential examples, sending all of them on
every call wastes tokens and can even dilute relevance. A **semantic example
selector** embeds your examples and, at call time, retrieves only the ones
most similar to the current input:

```python
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

selector = SemanticSimilarityExampleSelector.from_examples(
    examples,
    OpenAIEmbeddings(),
    Chroma,
    k=2,  # only the 2 most relevant examples per query
)

dynamic_few_shot = FewShotChatMessagePromptTemplate(
    example_selector=selector,
    example_prompt=example_prompt,
)
```

This is the same embed-and-retrieve pattern you'll formalize in the
Retrieval module of this course, and the same idea behind retrieval-backed
agent memory from Course 8 — here applied to *examples* rather than
documents or facts.

## The token-cost tradeoff

Every example you include costs tokens on every single call, and more
examples doesn't always mean better output — beyond a handful, returns
diminish while cost keeps climbing linearly. Start with 2-4 well-chosen
examples, measure whether output quality actually improves with more, and
let a semantic selector pick a small, relevant subset per query rather than
always sending your entire example bank.
""",
                    "examples": [
                        {
                            "title": "Formatting the final few-shot prompt to inspect it",
                            "code": (
                                "formatted = final_prompt.invoke({\"input\": \"Customer service was unhelpful and slow.\"})\n"
                                "for m in formatted.to_messages():\n"
                                "    print(m.type, \":\", m.content)"
                            ),
                            "explanation": "Printing the fully assembled message list is the fastest way to verify examples were interpolated correctly before spending an API call.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a fixed few-shot prompt with 3 examples for extracting a person's name and age from a sentence into a 'Name, Age' format.",
                            "difficulty": "easy",
                            "hint": "Keep the example_prompt's structure identical to how you want the model to respond.",
                        },
                        {
                            "prompt": "Extend your few-shot prompt to a semantic example selector over a bank of 10 examples, retrieving only the 3 most relevant per query.",
                            "difficulty": "hard",
                            "hint": "You'll need an embeddings model and a vector store, as shown in the lesson.",
                        },
                        {
                            "prompt": "Design an experiment (inputs and what you'd measure) to determine whether adding a 5th example actually improves output quality over 4, for your classification task.",
                            "difficulty": "medium",
                            "hint": "Consider running the same test set against both configurations and comparing accuracy.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Few-shot prompting", "url": "https://python.langchain.com/docs/how_to/few_shot_examples_chat/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
            ],
        },
        # 4. Tools
        {
            "slug": "tools",
            "title": "Tools",
            "description": "Defining Python functions as LangChain tools and binding them to a chat model so it can request structured tool calls.",
            "order_index": 4,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "defining-tools-with-the-tool-decorator",
                    "title": "Defining Tools with the @tool Decorator",
                    "description": "Turning a plain Python function into a LangChain tool with the @tool decorator, and writing docstrings that double as the tool's schema.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define a tool using the @tool decorator",
                        "Explain how a function's type hints and docstring become its schema",
                        "Use Pydantic models for tools with complex, multi-field arguments",
                        "Apply the tool-design principles from Course 8 to LangChain's tool interface specifically",
                    ],
                    "content_markdown": """## From Python function to model-callable tool

Course 8 covered *why* tool interfaces need clear names, descriptions, and
typed parameters. LangChain's `@tool` decorator is the concrete mechanism
for turning an ordinary Python function into something a model can discover
and call, deriving the schema directly from your function's signature and
docstring:

```python
from langchain_core.tools import tool

@tool
def get_stock_price(ticker: str) -> str:
    \"\"\"Get the current stock price for a given ticker symbol, e.g. 'AAPL'.\"\"\"
    price = stock_api.lookup(ticker)
    return f"{ticker}: ${price:.2f}"

print(get_stock_price.name)         # "get_stock_price"
print(get_stock_price.description)  # the docstring
print(get_stock_price.args)         # {'ticker': {'title': 'Ticker', 'type': 'string'}}
```

The type hint (`ticker: str`) becomes the parameter's JSON Schema type, and
the docstring becomes the description the model sees. This is exactly the
"tool is a contract" idea from Course 8, now made literal: what you write in
Python *is* the schema, so a vague docstring produces a vague tool
description with no separate place to make it better.

## Multi-argument and complex tools with Pydantic

For tools with several arguments, or arguments needing their own
validation, define an explicit Pydantic input schema:

```python
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="The search query text")
    max_results: int = Field(default=5, description="Maximum number of results to return")

@tool("search_docs", args_schema=SearchInput)
def search_docs(query: str, max_results: int = 5) -> str:
    \"\"\"Search internal documentation and return matching snippets.\"\"\"
    results = doc_search(query, max_results)
    return "\\n".join(results)
```

Pydantic's `Field(description=...)` lets you document each individual
parameter, not just the tool as a whole — genuinely useful once a tool takes
more than one or two arguments and the model needs guidance on each.

## Applying Course 8's tool-design principles here directly

Everything from the Tool-Using Agents module of Course 8 translates
directly: name the tool after its capability (`get_stock_price`, not
`lookup`), state clearly in the docstring what it does *and does not* do,
keep the output compact and formatted for the model to reason about, and
decide on a consistent error-signaling convention. LangChain gives you the
mechanism; the design judgment about what makes a good tool is exactly what
you already learned — it doesn't change just because you're now using a
framework.

```python
@tool
def get_order_status(order_id: str) -> str:
    \"\"\"Get the shipping status of an order by its ID. Does NOT cancel or
    modify orders — use cancel_order for that.\"\"\"
    try:
        status = orders_api.get_status(order_id)
        return f"Order {order_id}: {status}"
    except OrderNotFoundError:
        return f"error: no order found with ID {order_id}"
```
""",
                    "examples": [
                        {
                            "title": "A tool with a compact, model-friendly return value",
                            "code": (
                                "@tool\n"
                                "def get_weather(city: str, unit: str = \"celsius\") -> str:\n"
                                "    \"\"\"Get current weather for a city. unit is 'celsius' or 'fahrenheit'.\"\"\"\n"
                                "    data = weather_api.current(city, unit)\n"
                                "    return f\"{city}: {data.temp}°{unit[0].upper()}, {data.condition}\""
                            ),
                            "explanation": "The return value is a short, information-dense string rather than a raw API payload, keeping the model's context efficient.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define a @tool-decorated function get_exchange_rate(from_currency: str, to_currency: str) -> str with a clear docstring, and print its .name, .description, and .args.",
                            "difficulty": "easy",
                            "hint": "The docstring becomes .description automatically; no extra step needed.",
                        },
                        {
                            "prompt": "Define a tool with a Pydantic args_schema for a 3-argument booking tool (destination, date, passenger_count), documenting each field individually.",
                            "difficulty": "medium",
                            "hint": "Use Field(description=...) on each Pydantic model attribute.",
                        },
                        {
                            "prompt": "Take a poorly-named tool function like do_lookup(x) and redesign it (name, docstring, types) for a concrete use case, applying the Course 8 tool-design checklist.",
                            "difficulty": "medium",
                            "hint": "Name it after the capability, and state explicitly what it does not do.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Tools", "url": "https://python.langchain.com/docs/concepts/tools/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 0.8}, {"slug": "tool-calling", "weight": 0.8}],
                },
                {
                    "slug": "binding-tools-to-chat-models",
                    "title": "Binding Tools to Chat Models",
                    "description": "Attaching a set of tools to a chat model with bind_tools, and reading the structured tool_calls the model produces.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Bind a list of tools to a chat model with .bind_tools()",
                        "Read and execute the structured tool_calls on a model response",
                        "Feed a tool's result back to the model as a ToolMessage",
                        "Distinguish tool binding from running a full agent loop",
                    ],
                    "content_markdown": """## Binding: making tools visible to the model

Defining a tool (previous lesson) doesn't yet let a model use it — you have
to explicitly **bind** the tool set to the chat model, which sends the
tools' schemas along with every request so the model can choose to call one:

```python
tools = [get_stock_price, get_weather]
model_with_tools = llm.bind_tools(tools)

response = model_with_tools.invoke("What's the weather in Austin?")
print(response.tool_calls)
# [{'name': 'get_weather', 'args': {'city': 'Austin'}, 'id': 'call_abc123'}]
```

`response.tool_calls` is a structured list — this is the mechanism behind
what Course 8 called "function calling" or "tool calling" at the API level,
now surfaced as a clean Python data structure rather than something you'd
have to parse out of raw JSON yourself.

## Executing a tool call and feeding the result back

The model requesting a tool call doesn't execute anything — your code has to
actually run the tool and hand the result back:

```python
from langchain_core.messages import ToolMessage

tool_map = {t.name: t for t in tools}
messages = [HumanMessage(content="What's the weather in Austin?")]

ai_message = model_with_tools.invoke(messages)
messages.append(ai_message)

for call in ai_message.tool_calls:
    tool_fn = tool_map[call["name"]]
    result = tool_fn.invoke(call["args"])
    messages.append(ToolMessage(content=result, tool_call_id=call["id"]))

final_response = model_with_tools.invoke(messages)
print(final_response.content)
```

Each `ToolMessage` is explicitly linked back to its originating call via
`tool_call_id`, which matters when the model requests multiple tool calls in
one turn — this is how the model (and you) can tell which result answers
which request.

## This is one turn, not a full agent

What you just built is a single request-tool-response cycle — exactly the
observe-decide-act step from Course 8's Tool-Using Agents module, but
without the surrounding loop that repeats until a final answer is reached.
Running that loop by hand, with your own `max_iters` bound and error
handling, is a completely valid way to build a tool-using system with
LangChain's binding primitives. The next module, Agents, introduces
`AgentExecutor`, which wraps exactly this loop for you — worth understanding
the manual version first so the prebuilt one isn't a black box.

## Parallel tool calls

Some models can request multiple tool calls in a single turn (e.g., "weather
in Austin and in Denver" triggering two `get_weather` calls at once). Your
execution code should handle `ai_message.tool_calls` as a list, as the
example above already does, rather than assuming exactly one call per turn —
an assumption that will silently drop results the moment a model actually
uses this capability.
""",
                    "examples": [
                        {
                            "title": "Handling multiple tool calls in one turn",
                            "code": (
                                "ai_message = model_with_tools.invoke([HumanMessage(content=\"Weather in Austin and in Denver?\")])\n"
                                "print(len(ai_message.tool_calls))  # 2, one per city\n"
                                "for call in ai_message.tool_calls:\n"
                                "    print(call[\"name\"], call[\"args\"])"
                            ),
                            "explanation": "Iterating over tool_calls as a list correctly handles both the single-call and multi-call case without special-casing either.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Bind two tools of your choosing to a chat model and invoke it with a prompt that should trigger exactly one of them. Print the resulting tool_calls.",
                            "difficulty": "easy",
                            "hint": "Phrase the prompt so it unambiguously matches only one tool's purpose.",
                        },
                        {
                            "prompt": "Write the full request-execute-respond loop from the lesson as a reusable function that takes a model_with_tools, a tool_map, and an initial message list, and returns the final response.",
                            "difficulty": "medium",
                            "hint": "This closely mirrors the tool_loop function from Course 8's Tool-Using Agents module.",
                        },
                        {
                            "prompt": "Modify your loop function to handle the case where a requested tool name isn't in tool_map, returning a ToolMessage with an error string instead of raising an exception.",
                            "difficulty": "medium",
                            "hint": "This is the same graceful-error-as-observation pattern from Course 8.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Tool calling", "url": "https://python.langchain.com/docs/concepts/tool_calling/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 1.0}, {"slug": "langchain", "weight": 0.6}],
                },
            ],
        },
        # 5. Agents
        {
            "slug": "agents",
            "title": "Agents",
            "description": "Building a full tool-calling agent loop with LangChain's prebuilt agent constructors, and inspecting how it makes decisions.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "building-agents-with-create-tool-calling-agent",
                    "title": "Building Agents with create_tool_calling_agent",
                    "description": "Assembling a complete tool-calling agent from a model, a tool list, and a prompt using LangChain's agent constructor.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Construct an agent with create_tool_calling_agent",
                        "Write an agent prompt that includes the required agent_scratchpad placeholder",
                        "Explain what create_tool_calling_agent handles automatically versus what you built by hand in the previous module",
                        "Choose appropriate tools and instructions for a specific agent's role",
                    ],
                    "content_markdown": """## From manual loop to prebuilt constructor

The previous module had you hand-build the request-execute-respond cycle.
`create_tool_calling_agent` packages that pattern (plus the looping logic
that repeats it until the model stops requesting tools) into a single
constructor call:

```python
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant with access to tools. Use them when needed."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

agent = create_tool_calling_agent(llm, tools, prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

result = executor.invoke({"input": "What's the weather in Austin, and what's AAPL trading at?"})
print(result["output"])
```

Two placeholders matter here: `{input}` for the user's request, and
`{agent_scratchpad}` — a required slot where LangChain injects the running
history of tool calls and results as the agent works through multiple steps.
Omitting `agent_scratchpad` from your prompt is a common mistake that breaks
multi-step tool use silently.

## What's automated versus what you already understand

`create_tool_calling_agent` and `AgentExecutor` handle: formatting tool
schemas for the model, parsing `tool_calls` out of responses, executing the
matched tool functions, appending results back into the scratchpad, and
looping until the model produces a final answer instead of another tool
call. Every one of these steps is something you implemented by hand in the
Tools module — the constructor doesn't introduce new concepts, it automates
mechanics you now understand well enough to debug when they go wrong.

## Designing the agent's role through its prompt and tool set

The system message and the tool list together define what the agent
actually is. A narrowly scoped agent (few tools, a specific system message)
behaves more predictably than a broad one with dozens of tools and a vague
system message — this is the same specialization argument from Course 8's
Routing module, now applied at the level of a single `create_tool_calling_agent`
call rather than a router dispatching between several.

```python
research_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a research assistant. You may search documents and "
               "summarize findings, but you never make purchases or send "
               "messages on the user's behalf."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])
research_agent = create_tool_calling_agent(llm, [search_docs, summarize], research_prompt)
```

Stating explicitly what the agent should *not* do, directly in the system
message, is the same disambiguation principle you applied to individual tool
docstrings — it applies just as much to the agent's overall role.
""",
                    "examples": [
                        {
                            "title": "A minimal end-to-end agent",
                            "code": (
                                "tools = [get_weather, get_stock_price]\n"
                                "agent = create_tool_calling_agent(llm, tools, prompt)\n"
                                "executor = AgentExecutor(agent=agent, tools=tools)\n"
                                "result = executor.invoke({\"input\": \"Should I bring an umbrella in Seattle today?\"})\n"
                                "print(result[\"output\"])"
                            ),
                            "explanation": "AgentExecutor handles the full loop internally; result['output'] is the agent's final answer after any tool calls it needed.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a tool-calling agent with two tools of your choosing and a prompt that includes the required placeholders. Invoke it with a request that should require using at least one tool.",
                            "difficulty": "medium",
                            "hint": "Don't forget the agent_scratchpad placeholder in your prompt.",
                        },
                        {
                            "prompt": "Deliberately omit the agent_scratchpad placeholder from your prompt and observe what error or behavior results when the agent needs to use a tool.",
                            "difficulty": "easy",
                            "hint": "This is a useful debugging exercise for recognizing this specific mistake later.",
                        },
                        {
                            "prompt": "Write a system message for a narrowly-scoped 'read-only reporting agent' that explicitly states which actions it must never take.",
                            "difficulty": "medium",
                            "hint": "Apply the same 'does NOT do X' pattern used for individual tool docstrings.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Agents", "url": "https://python.langchain.com/docs/concepts/agents/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}, {"slug": "tool-calling", "weight": 0.5}],
                },
                {
                    "slug": "agentexecutor-and-intermediate-steps",
                    "title": "AgentExecutor and Intermediate Steps",
                    "description": "Inspecting the tool calls an agent made along the way, configuring iteration limits and error handling on AgentExecutor.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Inspect an agent's intermediate_steps to see every tool call it made",
                        "Configure max_iterations and handle_parsing_errors on AgentExecutor",
                        "Explain why observability into intermediate steps matters for debugging and evaluation",
                        "Connect AgentExecutor's configuration to the reliability patterns from Course 8",
                    ],
                    "content_markdown": """## Seeing what the agent actually did

A final answer alone doesn't tell you *how* the agent got there — which
tools it called, in what order, and with what arguments. `AgentExecutor`
exposes this via `intermediate_steps` when you request it:

```python
executor = AgentExecutor(agent=agent, tools=tools, return_intermediate_steps=True)
result = executor.invoke({"input": "What's the weather in Austin, and what's AAPL trading at?"})

for action, observation in result["intermediate_steps"]:
    print(f"Called {action.tool} with {action.tool_input} -> {observation}")
```

This trace is the concrete, inspectable record that Course 8's Agent State
module argued for in the abstract — explicit, structured data about what the
agent did, rather than having to reverse-engineer it from a final answer
alone. It's also exactly what you'd log for debugging a wrong answer, or
feed into an evaluation pipeline (Course 12) that checks whether the agent
used the right tools for a given request.

## Configuring reliability limits

`AgentExecutor` exposes the same reliability knobs you built by hand in
Course 8:

```python
executor = AgentExecutor(
    agent=agent,
    tools=tools,
    max_iterations=6,             # same purpose as max_iters from Course 8's tool loop
    max_execution_time=30,         # a wall-clock timeout across the whole run
    handle_parsing_errors=True,    # feed malformed output back to the model as an observation, instead of crashing
    verbose=True,                  # print each step as it happens, useful during development
)
```

`max_iterations` is directly the runaway-loop guard from the Tool-Using
Agents module in Course 8; `handle_parsing_errors` is the self-correction
pattern from that course's Self-Correction module, applied automatically to
malformed tool-call output instead of you writing the retry-with-error-
feedback logic by hand.

## When the agent hits its limit

```python
result = executor.invoke({"input": complex_multi_step_request})
if result.get("output", "").startswith("Agent stopped"):
    # exceeded max_iterations without reaching a final answer
    log_incomplete_run(result["intermediate_steps"])
```

Treat an agent that exhausts `max_iterations` the same way Course 8 treated
an exhausted retry loop or replan counter: not a silent failure to ignore,
but a signal worth logging and investigating — it usually means either the
task was genuinely too complex for the tool set provided, or the agent got
stuck in an unproductive pattern worth understanding.

## Why this observability matters beyond debugging

Intermediate steps aren't just a debugging convenience — they're the raw
material for agent evaluation, which you'll build formally in Course 12.
Being able to answer "did the agent call the right tool, with the right
arguments, in the right order" for a batch of test cases depends entirely on
having this structured trace available, not just a final answer to eyeball.
""",
                    "examples": [
                        {
                            "title": "Counting tool calls per run for basic monitoring",
                            "code": (
                                "result = executor.invoke({\"input\": user_request})\n"
                                "tool_call_count = len(result[\"intermediate_steps\"])\n"
                                "if tool_call_count > 4:\n"
                                "    logger.warning(f\"unusually high tool call count: {tool_call_count}\")"
                            ),
                            "explanation": "A simple threshold on tool-call count is a cheap early-warning signal for agent runs that may be behaving unexpectedly.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Enable return_intermediate_steps on an AgentExecutor and print a human-readable trace (tool name, arguments, result) for a multi-tool request.",
                            "difficulty": "easy",
                            "hint": "Loop over result['intermediate_steps'], which is a list of (AgentAction, observation) tuples.",
                        },
                        {
                            "prompt": "Configure max_iterations=2 on an agent with a task that would normally require 3+ tool calls, and observe what result the agent returns when it hits the limit.",
                            "difficulty": "medium",
                            "hint": "Look at result['output'] for the 'Agent stopped' message.",
                        },
                        {
                            "prompt": "Write a function that takes intermediate_steps and returns True if the agent called a specific disallowed tool at any point, for use as a post-hoc safety check.",
                            "difficulty": "medium",
                            "hint": "Check action.tool for each step against a disallowed set.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Agents", "url": "https://python.langchain.com/docs/concepts/agents/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}, {"slug": "tool-calling", "weight": 0.4}],
                },
            ],
        },
        # 6. Retrieval
        {
            "slug": "retrieval",
            "title": "Retrieval",
            "description": "Loading and splitting your own documents, and composing a retrieval chain that grounds model output in that content.",
            "order_index": 6,
            "estimated_hours": 1.6,
            "lessons": [
                {
                    "slug": "document-loaders-and-text-splitters",
                    "title": "Document Loaders and Text Splitters",
                    "description": "Getting your own content into LangChain as Document objects, and splitting it into retrieval-sized chunks.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Load documents from a common source using a LangChain document loader",
                        "Explain what a Document object contains: page_content and metadata",
                        "Split documents into chunks with RecursiveCharacterTextSplitter",
                        "Choose chunk size and overlap based on the chunking principles from the RAG course",
                    ],
                    "content_markdown": """## Getting content into LangChain

Before anything can be retrieved, it has to be loaded and represented
consistently. LangChain's document loaders read from a wide range of
sources (PDFs, web pages, plain text, databases) and normalize them into
`Document` objects:

```python
from langchain_community.document_loaders import TextLoader

loader = TextLoader("./docs/product_faq.txt")
documents = loader.load()

print(documents[0].page_content[:200])  # the raw text
print(documents[0].metadata)             # {'source': './docs/product_faq.txt'}
```

Every `Document` has two parts: `page_content` (the text itself) and
`metadata` (a dict carrying source information, page numbers, or anything
else useful for filtering results later). Metadata matters more than it
looks — it's what lets you filter retrieval results by source, date, or
permission level down the line.

## Splitting into retrieval-sized chunks

Full documents are almost always too large, and too topically mixed, to
embed and retrieve as single units — this is exactly the chunking problem
you studied in the RAG portion of this program. LangChain's
`RecursiveCharacterTextSplitter` implements a sensible default strategy: it
tries to split on paragraph breaks first, falling back to sentences, then
words, only if a chunk is still too large.

```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,      # target size in characters
    chunk_overlap=50,     # overlap between consecutive chunks
)
chunks = splitter.split_documents(documents)
print(f"{len(documents)} documents split into {len(chunks)} chunks")
```

## Chunk size and overlap, revisited concretely

The RAG course covered *why* chunk size and overlap matter — too large, and
retrieval returns bloated, topically diluted chunks; too small, and you lose
surrounding context a chunk needs to be individually meaningful. Overlap
exists specifically to avoid severing a sentence or idea exactly at a chunk
boundary, so a detail near the edge of one chunk still appears, in context,
in the neighboring chunk too.

```python
# For dense technical documentation, smaller chunks with more overlap
technical_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=75)

# For narrative content where broader context matters more, larger chunks
narrative_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
```

There's no universally correct chunk size — it depends on your content's
density and how self-contained individual ideas tend to be. Start with the
defaults above, and tune based on whether retrieved chunks, when you inspect
them manually, actually contain complete, useful thoughts.

## Preserving metadata through the split

Splitting preserves each chunk's link back to its source document's
metadata automatically — `chunks[0].metadata` still carries the original
`source` field. This is what lets a retrieval chain later cite exactly which
document (and section, if you've added page numbers) an answer came from,
which matters enormously for trustworthiness in a production RAG system.
""",
                    "examples": [
                        {
                            "title": "Inspecting chunk boundaries for quality",
                            "code": (
                                "for chunk in chunks[:3]:\n"
                                "    print(\"---\")\n"
                                "    print(chunk.page_content)\n"
                                "    print(chunk.metadata)"
                            ),
                            "explanation": "Manually reviewing the first few chunks is the fastest way to catch a chunk_size that's cutting ideas off mid-thought.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Load a text file with TextLoader and split it with RecursiveCharacterTextSplitter using chunk_size=400 and chunk_overlap=40. Print the number of resulting chunks.",
                            "difficulty": "easy",
                            "hint": "Call .load() on the loader, then .split_documents() on the splitter.",
                        },
                        {
                            "prompt": "Split the same document with two different chunk_size values and compare how the chunk boundaries differ in practice by printing a few chunks from each.",
                            "difficulty": "medium",
                            "hint": "Look for whether sentences or ideas get cut off differently between the two settings.",
                        },
                        {
                            "prompt": "Add a custom metadata field (e.g. a document category) to loaded documents before splitting, and confirm it survives into each resulting chunk.",
                            "difficulty": "medium",
                            "hint": "You can mutate doc.metadata directly on each loaded Document before calling split_documents.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Document loaders", "url": "https://python.langchain.com/docs/concepts/document_loaders/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 0.8}, {"slug": "retrieval", "weight": 0.6}],
                },
                {
                    "slug": "building-a-retrieval-chain",
                    "title": "Building a Retrieval Chain",
                    "description": "Embedding chunks into a vector store and composing a full retrieval-augmented chain that answers questions grounded in your documents.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Embed and store document chunks in a vector store",
                        "Build a retriever and compose it into an LCEL chain",
                        "Assemble a full RAG chain: retrieve, format context, prompt, generate",
                        "Return source documents alongside the generated answer",
                    ],
                    "content_markdown": """## From chunks to a searchable store

With chunks in hand, the next step is embedding them and storing the
vectors for similarity search — the same embedding-and-store pattern from
the RAG course, now with LangChain handling the plumbing:

```python
from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector_store = Chroma.from_documents(chunks, embeddings)

retriever = vector_store.as_retriever(search_kwargs={"k": 4})
```

`.as_retriever()` turns the vector store into a Runnable — meaning it slots
directly into an LCEL chain the same way a prompt or model does, which is
the whole point of everything being a Runnable.

## Composing the full RAG chain

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def format_docs(docs):
    return "\\n\\n".join(d.page_content for d in docs)

rag_prompt = ChatPromptTemplate.from_template('''
Answer the question using only the context below. If the context doesn't
contain the answer, say you don't know.

Context:
{context}

Question: {question}
''')

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("What is the return policy for opened items?")
```

The dict at the start of the chain is LCEL's way of running two branches in
parallel and merging their outputs: `retriever | format_docs` fetches and
formats the relevant chunks into `context`, while `RunnablePassthrough()`
simply forwards the original question through unchanged into `question`.
Both results feed into `rag_prompt`'s two placeholders.

## Explicitly instructing groundedness

Notice the prompt explicitly says "using only the context below" and "if the
context doesn't contain the answer, say you don't know." This single
instruction is doing real work: without it, a model will often fall back on
its own general knowledge when retrieved context is thin, silently
undermining the entire point of retrieval-augmented generation, which is to
ground answers in *your* content specifically.

## Returning sources alongside the answer

For a production system, showing *which* documents an answer came from is
often as important as the answer itself — it's what lets a user verify a
claim rather than trust it blindly:

```python
from langchain_core.runnables import RunnableParallel

rag_chain_with_sources = RunnableParallel(
    answer=rag_chain,
    sources=retriever,
)
result = rag_chain_with_sources.invoke("What is the return policy for opened items?")
print(result["answer"])
for doc in result["sources"]:
    print("-", doc.metadata.get("source"))
```

`RunnableParallel` runs both branches against the same input and returns
both results together — the generated answer and the raw retrieved
documents it should be grounded in, letting your application surface
citations directly.
""",
                    "examples": [
                        {
                            "title": "Filtering retrieval by metadata",
                            "code": (
                                "retriever = vector_store.as_retriever(\n"
                                "    search_kwargs={\"k\": 4, \"filter\": {\"category\": \"billing\"}}\n"
                                ")"
                            ),
                            "explanation": "Combining semantic search with a metadata filter narrows retrieval to a relevant subset, using the metadata fields preserved from the loading step.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a full RAG chain over a small set of your own text chunks: embed, store, retrieve, prompt, generate. Ask it one question the documents can answer and one they can't.",
                            "difficulty": "medium",
                            "hint": "Verify the 'I don't know' instruction actually triggers on the unanswerable question.",
                        },
                        {
                            "prompt": "Modify the rag_chain to use RunnableParallel so it returns both the answer and the list of source documents used.",
                            "difficulty": "medium",
                            "hint": "Follow the rag_chain_with_sources pattern from the lesson.",
                        },
                        {
                            "prompt": "Change the retriever's k value from 4 to 1 and then to 10, and observe how answer quality and groundedness change at each extreme.",
                            "difficulty": "hard",
                            "hint": "Too few chunks can miss relevant context; too many can dilute the prompt with less relevant material.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Retrieval", "url": "https://python.langchain.com/docs/concepts/retrieval/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "retrieval", "weight": 1.0}, {"slug": "langchain", "weight": 0.7}],
                },
            ],
        },
        # 7. Memory
        {
            "slug": "memory",
            "title": "Memory",
            "description": "Adding conversation memory to a chain and persisting chat history across sessions using LangChain's message history abstractions.",
            "order_index": 7,
            "estimated_hours": 1.4,
            "lessons": [
                {
                    "slug": "conversation-memory-in-langchain",
                    "title": "Conversation Memory in LangChain",
                    "description": "Wiring a running conversation history into a chain with RunnableWithMessageHistory.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why a plain chain has no memory between .invoke() calls by default",
                        "Wrap a chain with RunnableWithMessageHistory to add conversational memory",
                        "Use a session_id to keep multiple users' conversations isolated",
                        "Connect this mechanism to the working-memory concepts from Course 8",
                    ],
                    "content_markdown": """## Chains are stateless by default

An LCEL chain, on its own, has no memory — call `.invoke()` twice in a row
and the second call knows nothing about the first, because each call is an
independent function application with no hidden state carried between them.
This is a deliberate design property (statelessness makes chains easy to
reason about, test, and run in parallel), but it means conversational memory
has to be added explicitly, exactly as Course 8's Short-Term Memory module
argued: memory is not something a model call has for free.

## Adding memory with RunnableWithMessageHistory

```python
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

store = {}  # session_id -> history object

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,  # your existing prompt | model | parser chain
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)

response1 = chain_with_memory.invoke(
    {"input": "My name is Priya."},
    config={"configurable": {"session_id": "user-42"}},
)
response2 = chain_with_memory.invoke(
    {"input": "What's my name?"},
    config={"configurable": {"session_id": "user-42"}},
)
print(response2)  # correctly recalls "Priya" from the same session's history
```

The underlying prompt needs a `history` placeholder for this to work:

```python
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("placeholder", "{history}"),
    ("human", "{input}"),
])
```

## session_id: the key to isolation

Every call passes a `session_id` in its config, and `get_session_history`
uses it to look up (or create) the right history object. This is what keeps
different users' — or different conversations' — histories from bleeding
into each other, the same isolation concern Course 8 raised when discussing
scoping memory retrieval to the correct user or entity.

## Connecting back to Course 8's memory model

`RunnableWithMessageHistory` with `InMemoryChatMessageHistory` is, in Course
8's terms, exactly a **working/short-term memory** mechanism: it keeps the
raw conversation for the current session, appended to the prompt on every
call, with no persistence beyond the process's lifetime and no summarization
or windowing. It answers "how do I thread history through a chain" — the
next lesson addresses "how do I make that history survive past this
process," and later lessons in this program build the summarization and
windowing strategies from Course 8 directly on top of this same mechanism.
""",
                    "examples": [
                        {
                            "title": "Two isolated sessions in the same process",
                            "code": (
                                "chain_with_memory.invoke({\"input\": \"I like tea.\"}, config={\"configurable\": {\"session_id\": \"alice\"}})\n"
                                "chain_with_memory.invoke({\"input\": \"I like coffee.\"}, config={\"configurable\": {\"session_id\": \"bob\"}})\n\n"
                                "r1 = chain_with_memory.invoke({\"input\": \"What do I like?\"}, config={\"configurable\": {\"session_id\": \"alice\"}})\n"
                                "print(r1)  # recalls tea, not coffee, because sessions are isolated by session_id"
                            ),
                            "explanation": "Each session_id maps to its own independent InMemoryChatMessageHistory, so Alice's and Bob's conversations never cross-contaminate.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Wrap a simple prompt | model | parser chain with RunnableWithMessageHistory and verify it correctly recalls a fact stated two turns earlier in the same session.",
                            "difficulty": "medium",
                            "hint": "Make sure your prompt includes a history placeholder that matches history_messages_key.",
                        },
                        {
                            "prompt": "Run two different session_ids through the same wrapped chain and confirm their histories don't leak into each other.",
                            "difficulty": "easy",
                            "hint": "State a distinct fact in each session and ask the chain to recall it in the other.",
                        },
                        {
                            "prompt": "Explain, referencing Course 8's memory layers, exactly which layer InMemoryChatMessageHistory implements and which layers it does NOT provide on its own.",
                            "difficulty": "medium",
                            "hint": "Consider what happens to the store dict when the Python process restarts.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Message history", "url": "https://python.langchain.com/docs/how_to/message_history/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "memory", "weight": 0.9}, {"slug": "langchain", "weight": 0.7}],
                },
                {
                    "slug": "persisting-chat-history-across-sessions",
                    "title": "Persisting Chat History Across Sessions",
                    "description": "Swapping in a durable chat message history backend so conversations survive process restarts, and considering history trimming.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Swap InMemoryChatMessageHistory for a durable, database-backed implementation",
                        "Explain why in-memory history is unsuitable for production without modification",
                        "Trim or window stored history to bound prompt size over long conversations",
                        "Relate this mechanism to the persistence concepts introduced in Course 8",
                    ],
                    "content_markdown": """## Why in-memory history doesn't survive production

`InMemoryChatMessageHistory`, as its name says, lives in a Python
dictionary in process memory. Restart the server, deploy a new version, or
run multiple server instances behind a load balancer, and that history is
gone or inconsistent across instances. Course 8's Agent State module made
this exact point about state in general: anything that needs to survive
beyond a single process's lifetime needs a durable backing store.

## Swapping in a durable backend

LangChain ships integrations for common durable stores — Redis, Postgres,
and others — that implement the same `BaseChatMessageHistory` interface, so
the swap requires no change to `RunnableWithMessageHistory` or your chain
itself:

```python
from langchain_community.chat_message_histories import RedisChatMessageHistory

def get_session_history(session_id: str):
    return RedisChatMessageHistory(session_id=session_id, url="redis://localhost:6379")

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history",
)
```

Only `get_session_history` changed — everything downstream of it is
identical to the in-memory version from the previous lesson. This is the
same "swap the implementation, keep the interface" pattern you already saw
with chat model providers in the Models module.

## Trimming history to bound prompt size

A conversation that runs for hours accumulates a lot of turns, and — as
Course 8's Short-Term Memory module covered — sending the entire raw history
on every call eventually blows the context window and wastes tokens. LangChain
provides `trim_messages` to cap history by token count before it's injected
into the prompt:

```python
from langchain_core.messages import trim_messages

def get_trimmed_history(session_id: str):
    full_history = RedisChatMessageHistory(session_id=session_id, url="redis://localhost:6379")
    return full_history  # trimming is applied in the chain itself, below

trimmer = trim_messages(max_tokens=1000, strategy="last", token_counter=llm)

chain_with_trimming = (
    RunnablePassthrough.assign(history=lambda x: trimmer.invoke(x["history"]))
    | rag_prompt  # or your prompt with a history placeholder
    | llm
)
```

This keeps the *durable* store complete (every turn is still persisted, in
case you need the full record later) while only a bounded, recent window is
actually sent to the model on each call — durability and prompt-size control
are separate concerns, and this pattern keeps them that way.

## Connecting back to Course 8

What you've built across these two lessons is a direct, working
implementation of the persistence and windowing concepts from Course 8's
Agent State and Short-Term Memory modules — a `session_id`-keyed durable
store standing in for the `task_id`-keyed store from that course, and
`trim_messages` standing in for the hand-rolled `windowed_messages` function.
The concepts transfer completely; only the concrete implementation changed.
""",
                    "examples": [
                        {
                            "title": "Verifying persistence across a simulated restart",
                            "code": (
                                "# First 'process': write some history\n"
                                "history = RedisChatMessageHistory(session_id=\"user-42\", url=\"redis://localhost:6379\")\n"
                                "history.add_user_message(\"I prefer email over phone calls.\")\n\n"
                                "# A brand-new RedisChatMessageHistory instance, simulating a fresh process\n"
                                "reloaded = RedisChatMessageHistory(session_id=\"user-42\", url=\"redis://localhost:6379\")\n"
                                "print(reloaded.messages)  # the prior message is still there"
                            ),
                            "explanation": "Because the history lives in Redis rather than a Python dict, a fresh object pointed at the same session_id sees the same data.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Swap InMemoryChatMessageHistory for a Redis-backed (or any other durable) implementation in a chain from the previous lesson, changing only get_session_history.",
                            "difficulty": "medium",
                            "hint": "The RunnableWithMessageHistory wrapper itself should not need to change.",
                        },
                        {
                            "prompt": "Add trim_messages to your chain with a small max_tokens value, and verify that only recent turns are actually sent to the model even though the full history is still stored.",
                            "difficulty": "medium",
                            "hint": "Add enough turns that trimming clearly has to drop earlier ones.",
                        },
                        {
                            "prompt": "Explain why durability (does the data survive a restart) and context-window management (how much of it gets sent per call) are separate concerns that shouldn't be conflated into a single mechanism.",
                            "difficulty": "medium",
                            "hint": "Consider a scenario where you need the full history available later for auditing, even though only a small window is used in any given prompt.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Message history", "url": "https://python.langchain.com/docs/how_to/message_history/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "memory", "weight": 1.0}, {"slug": "langchain", "weight": 0.5}],
                },
            ],
        },
        # 8. Structured Output
        {
            "slug": "structured-output",
            "title": "Structured Output",
            "description": "Getting a chat model to return validated, typed data instead of free text, using Pydantic schemas and output parsers.",
            "order_index": 8,
            "estimated_hours": 1.4,
            "lessons": [
                {
                    "slug": "getting-structured-output-with-pydantic-schemas",
                    "title": "Getting Structured Output with Pydantic Schemas",
                    "description": "Using with_structured_output to have a chat model return a validated Pydantic object directly.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define a Pydantic model describing a desired output shape",
                        "Use .with_structured_output() to bind that schema to a chat model",
                        "Explain how this differs from parsing free text after the fact",
                        "Handle nested and list fields in a structured output schema",
                    ],
                    "content_markdown": """## Free text is the wrong default for data your code will consume

Whenever an application needs to *use* a model's output programmatically —
populate a form, fill a database row, drive a conditional in your code — free
text is a liability: it has to be parsed, and every parsing step is a place
things can silently go wrong. LangChain's `.with_structured_output()`
sidesteps this by having the model return data matching a schema you define,
validated on the way out.

```python
from pydantic import BaseModel, Field

class ExtractedTicket(BaseModel):
    summary: str = Field(description="A one-sentence summary of the issue")
    urgency: str = Field(description="One of: low, medium, high")
    category: str = Field(description="One of: billing, technical, account")

structured_llm = llm.with_structured_output(ExtractedTicket)

result = structured_llm.invoke(
    "My payment failed twice this week and I need this resolved today."
)
print(result.summary, result.urgency, result.category)
print(type(result))  # <class '__main__.ExtractedTicket'>
```

`result` is a real `ExtractedTicket` instance — not a string you still need
to parse, and not a dict you have to trust blindly. Pydantic validates the
shape (types, required fields) before your code ever sees it, which is a
meaningfully stronger guarantee than "the model usually returns valid JSON."

## How this differs from parsing free text after the fact

The naive alternative — ask the model to "respond in JSON," then
`json.loads()` the result yourself — leaves you fully responsible for
handling malformed output, missing fields, and type mismatches. `with_structured_output`
typically works by having the underlying provider's native structured-output
or tool-calling mechanism constrain generation toward the schema directly,
which produces far more reliable results than a purely textual instruction
to "please output valid JSON," especially as the schema grows more complex.

## Nested and list fields

Schemas aren't limited to flat fields:

```python
from typing import Literal

class LineItem(BaseModel):
    name: str
    price: float

class Invoice(BaseModel):
    customer_name: str
    items: list[LineItem]
    payment_status: Literal["paid", "unpaid", "partial"]

structured_llm = llm.with_structured_output(Invoice)
invoice = structured_llm.invoke("Extract the invoice details from this text: ...")
total = sum(item.price for item in invoice.items)  # plain Python, no parsing needed
```

`Literal["paid", "unpaid", "partial"]` is worth calling out specifically —
constraining a field to an exact enum of allowed values is a strong, cheap
guardrail against the model inventing a category that doesn't fit your
downstream logic, and it composes naturally with everything else Pydantic
gives you.

## Where this replaces manual self-correction

Recall Course 8's `validate_and_fix_json` pattern from the Self-Correction
module — deterministic JSON parsing with an LLM-based repair fallback.
`with_structured_output` handles the common case of that pattern for you at
the framework level, though the underlying principle (validate before you
trust it) is identical; you're just no longer implementing the validation
loop by hand for every schema.
""",
                    "examples": [
                        {
                            "title": "Using structured output to drive application logic directly",
                            "code": (
                                "ticket = structured_llm.invoke(user_message)\n"
                                "if ticket.urgency == \"high\":\n"
                                "    escalate_to_on_call(ticket.summary)\n"
                                "else:\n"
                                "    queue_normally(ticket)"
                            ),
                            "explanation": "Because ticket is a typed object, application logic can branch on its fields directly, with no string parsing or key-existence checks required.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define a Pydantic model for extracting a person's name, role, and years of experience from a short bio, and use with_structured_output to extract it from a sample bio text.",
                            "difficulty": "easy",
                            "hint": "Use Field(description=...) on each attribute to guide the model.",
                        },
                        {
                            "prompt": "Extend your model with a list[str] field for 'skills mentioned' and verify the model correctly returns a Python list.",
                            "difficulty": "medium",
                            "hint": "List fields work the same way nested models do in the lesson's Invoice example.",
                        },
                        {
                            "prompt": "Add a Literal field constraining a 'seniority' value to exactly 'junior', 'mid', or 'senior', and test what happens with an ambiguous input bio.",
                            "difficulty": "medium",
                            "hint": "Try a bio that doesn't clearly state seniority and see how the model resolves the ambiguity.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Structured output", "url": "https://python.langchain.com/docs/concepts/structured_outputs/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
                {
                    "slug": "output-parsers-and-validation",
                    "title": "Output Parsers and Validation",
                    "description": "Using output parsers for providers or cases without native structured output support, and handling validation failures gracefully.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Use PydanticOutputParser as a fallback when native structured output isn't available",
                        "Inject format instructions into a prompt so the model knows the expected output shape",
                        "Handle a validation failure with a retry-with-error-feedback pattern",
                        "Decide between with_structured_output and a manual parser based on provider support",
                    ],
                    "content_markdown": """## When native structured output isn't an option

`with_structured_output` relies on provider-side support for constrained
generation or tool calling. For providers or models without that support —
or for local/open-source models — LangChain's `PydanticOutputParser` gives
you a manual equivalent: it generates format instructions to embed in your
prompt, then parses and validates the model's text response against your
schema after the fact.

```python
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field

class MovieReview(BaseModel):
    title: str
    rating: float = Field(description="Rating out of 10")
    recommend: bool

parser = PydanticOutputParser(pydantic_object=MovieReview)

prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract movie review details. {format_instructions}"),
    ("human", "{review_text}"),
]).partial(format_instructions=parser.get_format_instructions())

chain = prompt | llm | parser
result = chain.invoke({"review_text": "Dune Part Two was visually stunning, 9/10, absolutely see it."})
print(result.title, result.rating, result.recommend)
```

`parser.get_format_instructions()` generates a text block describing the
exact JSON shape expected, which gets baked into the prompt via
`.partial()` — the model is guided by instructions in the prompt itself,
rather than by provider-level generation constraints, which is why this
approach is somewhat less reliable than native structured output but works
anywhere.

## Handling validation failures gracefully

Because parsing happens after generation rather than being constrained
during it, a `PydanticOutputParser` can raise a validation error if the
model's text doesn't quite match the schema. `OutputFixingParser` wraps your
parser with exactly the repair-on-failure pattern from Course 8's
Self-Correction module — catch the validation error, feed it back to the
model along with the malformed output, and ask for a corrected version:

```python
from langchain.output_parsers import OutputFixingParser

fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)

chain = prompt | llm | fixing_parser  # falls back to a repair call only on failure
```

This is a direct, drop-in implementation of the `validate_and_fix_json`
pattern you saw in Course 8 — deterministic-first, with an LLM repair call
only triggered when the deterministic parse actually fails, keeping the
common, well-formed case cheap.

## Choosing between the two approaches

Prefer `with_structured_output` whenever your provider supports it — it's
generally more reliable and doesn't require you to manage format
instructions or a repair loop yourself. Reach for `PydanticOutputParser`
(with `OutputFixingParser` as a safety net) specifically when you're working
with a model or provider that lacks native structured output support, or
when you need fine-grained control over exactly how format instructions are
worded and where they appear in the prompt.

```python
def get_structured_chain(llm, schema, prompt):
    if hasattr(llm, "with_structured_output"):
        try:
            return prompt | llm.with_structured_output(schema)
        except NotImplementedError:
            pass
    parser = PydanticOutputParser(pydantic_object=schema)
    fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=llm)
    return prompt.partial(format_instructions=parser.get_format_instructions()) | llm | fixing_parser
```
""",
                    "examples": [
                        {
                            "title": "Comparing the two approaches on the same schema",
                            "code": (
                                "# Native (preferred when supported)\n"
                                "native_result = llm.with_structured_output(MovieReview).invoke(review_text)\n\n"
                                "# Manual fallback\n"
                                "manual_result = chain.invoke({\"review_text\": review_text})\n\n"
                                "assert native_result.title == manual_result.title"
                            ),
                            "explanation": "Both paths should converge on the same validated MovieReview shape; the difference is in how each gets there and how reliable that path is.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a PydanticOutputParser-based chain for the ExtractedTicket schema from the previous lesson, including format_instructions in the prompt.",
                            "difficulty": "medium",
                            "hint": "Use .partial(format_instructions=parser.get_format_instructions()) as shown in the lesson.",
                        },
                        {
                            "prompt": "Wrap your parser with OutputFixingParser and deliberately test it against a prompt likely to produce a slightly malformed response, observing the repair happen.",
                            "difficulty": "medium",
                            "hint": "A vague or contradictory instruction can sometimes induce a malformed first attempt worth observing.",
                        },
                        {
                            "prompt": "Write the decision logic (as a short function or flowchart) you'd use to choose between with_structured_output and a manual PydanticOutputParser for a new project.",
                            "difficulty": "easy",
                            "hint": "The main factor is whether your chosen provider/model supports native structured output.",
                        },
                    ],
                    "resources": [
                        {"title": "LangChain docs: Output parsers", "url": "https://python.langchain.com/docs/concepts/output_parsers/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langchain", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "LangChain: Course Assessment",
    "description": "Checks readiness to move from single-framework chains and agents into LangGraph's stateful, graph-based orchestration.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 35,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "What makes an object a 'Runnable' in LangChain, and why does this matter for composition?",
            "options": [
                {"id": "a", "text": "It is any class defined inside the langchain_core package"},
                {"id": "b", "text": "It implements a consistent interface (.invoke, .batch, .stream) shared by prompts, models, parsers, and retrievers, enabling them to be piped together with |"},
                {"id": "c", "text": "It can only be used inside an AgentExecutor"},
                {"id": "d", "text": "It is any function decorated with @tool"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The shared Runnable interface is what makes LCEL's pipe-based composition possible across otherwise very different component types.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "mcq",
            "prompt": "In the LCEL chain `chain = prompt | model | parser`, what does `parser` typically receive as its input?",
            "options": [
                {"id": "a", "text": "The raw dictionary originally passed to .invoke()"},
                {"id": "b", "text": "The formatted ChatPromptValue"},
                {"id": "c", "text": "The message object returned by the model"},
                {"id": "d", "text": "A list of available tools"},
            ],
            "correct_answer": {"choice": "c"},
            "explanation": "Each stage's output becomes the next stage's input; parser receives what model produced, typically an AIMessage-like object, and extracts the content from it.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "mcq",
            "prompt": "Why does swapping ChatOpenAI for ChatAnthropic in an existing chain typically require only a one-line change?",
            "options": [
                {"id": "a", "text": "Both providers are owned by the same company"},
                {"id": "b", "text": "All chat model wrappers implement the same shared interface, so downstream prompt/chain code doesn't need to know which provider it's talking to"},
                {"id": "c", "text": "LangChain automatically translates between providers at runtime with no configuration"},
                {"id": "d", "text": "Anthropic and OpenAI use an identical underlying API"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The model I/O abstraction standardizes how chat models are called, which is what enables swapping providers without rewriting application logic — though behavior should still be re-validated.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are true about the @tool decorator in LangChain? Select all that apply.",
            "options": [
                {"id": "a", "text": "The function's docstring becomes the tool's description shown to the model"},
                {"id": "b", "text": "Type hints on the function's parameters are used to derive the tool's argument schema"},
                {"id": "c", "text": "A Pydantic args_schema can be supplied for tools needing per-field documentation"},
                {"id": "d", "text": "Tools defined with @tool cannot return strings"},
            ],
            "correct_answer": {"choices": ["a", "b", "c"]},
            "explanation": "The decorator derives the schema from type hints and docstring, and supports an explicit Pydantic args_schema for richer documentation. Tools commonly return strings, which is the recommended compact format.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "tool-calling",
        },
        {
            "question_type": "mcq",
            "prompt": "After binding tools to a chat model and invoking it, the model requests a tool call. What must your application code do next?",
            "options": [
                {"id": "a", "text": "Nothing; LangChain executes the tool automatically before returning the response"},
                {"id": "b", "text": "Manually execute the matching tool function and feed the result back as a ToolMessage linked by tool_call_id"},
                {"id": "c", "text": "Restart the chain from the beginning with a new prompt"},
                {"id": "d", "text": "Call .stream() instead of .invoke()"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Binding tools only makes them visible to the model for selection; your code is still responsible for actually executing the requested tool and returning its result.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "tool-calling",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the purpose of the {agent_scratchpad} placeholder in an agent's prompt when using create_tool_calling_agent?",
            "options": [
                {"id": "a", "text": "It holds the user's original question"},
                {"id": "b", "text": "It is where LangChain injects the running history of tool calls and results as the agent works through multiple steps"},
                {"id": "c", "text": "It configures the model's temperature"},
                {"id": "d", "text": "It is optional and can be safely omitted for any agent"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Omitting agent_scratchpad breaks multi-step tool use, since the agent has nowhere to see the results of its own prior tool calls.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "scenario",
            "prompt": "You've deployed an AgentExecutor-based customer support agent. In production, you notice some requests result in the agent hitting max_iterations without producing a useful final answer. Describe how you would use return_intermediate_steps to diagnose the problem, and what you'd change depending on what you find.",
            "options": [],
            "correct_answer": {"expected": "Enable return_intermediate_steps=True and inspect the (AgentAction, observation) pairs for the failing runs to see exactly which tools were called, with what arguments, and what they returned. If the trace shows the agent repeatedly calling the same tool with similar arguments (looping unproductively), the fix might be a better tool description, a narrower tool set, or a cap-and-handoff strategy. If the trace shows the agent genuinely needed more steps than max_iterations allowed for a legitimately complex request, raising max_iterations (or breaking the task into sub-agents) may be appropriate. The key diagnostic step is examining the actual sequence of tool calls rather than guessing from the final output alone."},
            "explanation": "This scenario tests the ability to connect AgentExecutor's observability features to real diagnostic workflow, mirroring the reliability patterns (bounded iteration, inspectable traces) from Course 8.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "mcq",
            "prompt": "In RecursiveCharacterTextSplitter, what is the purpose of chunk_overlap?",
            "options": [
                {"id": "a", "text": "It determines how many documents are loaded at once"},
                {"id": "b", "text": "It duplicates a small amount of text between consecutive chunks so an idea near a chunk boundary still appears in context in the neighboring chunk"},
                {"id": "c", "text": "It sets the embedding model's dimensionality"},
                {"id": "d", "text": "It controls how many results a retriever returns"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Overlap exists specifically to avoid severing a sentence or idea exactly at a chunk boundary.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "mcq",
            "prompt": "In a RAG chain built with `{\"context\": retriever | format_docs, \"question\": RunnablePassthrough()} | rag_prompt | llm | parser`, what does RunnablePassthrough() do?",
            "options": [
                {"id": "a", "text": "It retrieves documents from the vector store"},
                {"id": "b", "text": "It forwards the original input (the question) through unchanged into the question field of the prompt"},
                {"id": "c", "text": "It formats retrieved documents into a single string"},
                {"id": "d", "text": "It validates the final output against a schema"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "RunnablePassthrough lets the original input flow through one branch of a parallel step unchanged, while another branch (the retriever) transforms it, and both results merge into the prompt's variables.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "mcq",
            "prompt": "Why does the RAG prompt in this course's Retrieval module explicitly instruct the model to answer 'using only the context' and say 'I don't know' if the context is insufficient?",
            "options": [
                {"id": "a", "text": "It reduces token usage"},
                {"id": "b", "text": "Without this instruction, the model may fall back on its own general knowledge when retrieved context is thin, undermining the point of grounding answers in your own content"},
                {"id": "c", "text": "It is required by the Chroma vector store API"},
                {"id": "d", "text": "It speeds up the retrieval step"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "This explicit instruction is what enforces groundedness — without it, retrieval augmentation can be silently undermined by the model's own parametric knowledge.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "retrieval",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is InMemoryChatMessageHistory unsuitable for a production deployment running multiple server instances behind a load balancer?",
            "options": [
                {"id": "a", "text": "It cannot store more than 10 messages"},
                {"id": "b", "text": "It lives only in a single process's memory, so history isn't shared or durable across instances or restarts"},
                {"id": "c", "text": "It only works with ChatOpenAI"},
                {"id": "d", "text": "It requires a paid LangChain license"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Durable, shared history requires a backing store like Redis or Postgres that all instances can access consistently, unlike a per-process in-memory dictionary.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "memory",
        },
        {
            "question_type": "coding",
            "prompt": "Write LangChain code that defines a Pydantic model `Contact` with fields `name: str`, `email: str`, and `phone: str | None`, and uses with_structured_output on a chat model `llm` to extract a Contact from a string variable `text`.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Defines a Pydantic BaseModel with the three specified fields (phone optional/nullable) and calls llm.with_structured_output(Contact).invoke(text) to get a validated Contact instance back.",
                "sample_solution": (
                    "from pydantic import BaseModel\n\n"
                    "class Contact(BaseModel):\n"
                    "    name: str\n"
                    "    email: str\n"
                    "    phone: str | None = None\n\n"
                    "structured_llm = llm.with_structured_output(Contact)\n"
                    "contact = structured_llm.invoke(text)"
                ),
            },
            "explanation": "Correct usage requires defining the schema with appropriate typing (including the optional phone field) and binding it via with_structured_output rather than manually parsing text.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "mcq",
            "prompt": "When should you reach for PydanticOutputParser plus OutputFixingParser instead of with_structured_output?",
            "options": [
                {"id": "a", "text": "Always — it is strictly better in every case"},
                {"id": "b", "text": "When the provider or model in use lacks native structured-output/tool-calling support that with_structured_output relies on"},
                {"id": "c", "text": "Only when using ChatOpenAI specifically"},
                {"id": "d", "text": "Never — PydanticOutputParser is deprecated"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "with_structured_output is generally preferred when the provider supports it; the manual parser plus fixing parser is the fallback for providers or models without that native support.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langchain",
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain what session_id is used for in RunnableWithMessageHistory and why isolating by it matters.",
            "options": [],
            "correct_answer": {
                "expected": "session_id is passed in the config of each .invoke() call and is used by get_session_history to look up (or create) the correct history object for that specific conversation or user. Isolating by session_id prevents different users' or conversations' histories from bleeding into each other, which would otherwise cause one user's stated facts or context to incorrectly appear in another user's conversation.",
                "keywords": ["session_id", "isolation", "history", "lookup", "user"],
            },
            "explanation": "Correct session isolation is essential for any multi-user conversational application built on RunnableWithMessageHistory.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "memory",
        },
    ],
}
