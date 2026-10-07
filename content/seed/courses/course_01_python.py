"""
Course 1: Python for AI
Seed content for the Agentic AI LMS. See content/seed/SCHEMA.md for the
field-by-field contract this file must follow.
"""

COURSE = {
    "slug": "python-for-ai",
    "title": "Python for AI",
    "subtitle": "The Python you actually need before you touch a single model.",
    "description": (
        "A practical, no-fluff tour of Python built specifically for people headed toward AI "
        "engineering. You will write the same data structures, functions, classes, and async "
        "patterns that show up constantly in LLM SDKs, RAG pipelines, and agent frameworks later "
        "in this program, so every exercise here is chosen because you will use it again."
    ),
    "learning_outcomes": [
        "Write idiomatic Python using core data structures, functions, and control flow",
        "Design classes with inheritance and composition to model real systems",
        "Read and write files, CSV data, and JSON payloads confidently",
        "Call REST APIs and handle their responses the way AI SDKs expect",
        "Manage isolated project environments and dependencies like a professional",
        "Use async/await to run concurrent I/O-bound work such as parallel API calls",
    ],
    "order_index": 1,
    "estimated_hours": 18,
    "level": "beginner",
    "icon": "python",
    "modules": [
        {
            "slug": "python-fundamentals",
            "title": "Python Fundamentals",
            "description": (
                "The building blocks: variables, types, expressions, and the control-flow "
                "constructs that every script and agent loop you'll ever write is made from."
            ),
            "order_index": 1,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "variables-types-and-expressions",
                    "title": "Variables, Types, and Expressions",
                    "description": "How Python stores and manipulates values, and why dynamic typing matters for fast AI prototyping.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Create and reassign variables using Python's dynamic typing model",
                        "Identify Python's core built-in types: int, float, str, bool, None",
                        "Evaluate arithmetic, comparison, and boolean expressions correctly",
                        "Explain why type flexibility speeds up prototyping but requires discipline in production code",
                    ],
                    "content_markdown": """
## Why this matters

Every AI pipeline you will build in this program — from a RAG ingestion script to a LangGraph
agent — starts as a handful of variables holding text, numbers, and configuration values. Python's
dynamic typing lets you move fast: you don't declare types up front, you just assign. That speed is
exactly why Python became the default language of AI research and, later, AI engineering. But
dynamic typing is also where subtle bugs creep in once your agent has ten tools and three retry
loops, so building good instincts now pays off for the rest of the course.

## Variables and assignment

A variable is a name bound to a value. Python figures out the type from the value itself:

```python
model_name = "claude-sonnet"      # str
max_tokens = 4096                 # int
temperature = 0.7                 # float
streaming_enabled = True          # bool
system_prompt = None              # NoneType
```

Names are rebindable — the same variable can point to a string now and an integer later. This is
convenient, but in real agent code you generally want a name to keep the *same kind* of value
throughout its life, even though Python won't stop you from changing it.

## Core built-in types

- `int` — whole numbers, used for things like `max_tokens` or retry counts.
- `float` — decimal numbers, used for `temperature`, `top_p`, similarity scores.
- `str` — text, the type you will spend the most time with once you start handling prompts.
- `bool` — `True`/`False`, used constantly in conditionals that gate agent behavior.
- `None` — represents "no value yet," which you will see everywhere as a default function argument.

## Expressions

An expression is anything Python can evaluate to produce a value:

```python
tokens_used = 120 + 340          # arithmetic -> 460
is_within_budget = tokens_used < 4096   # comparison -> True
should_retry = (not is_within_budget) or False  # boolean logic -> False
```

Python follows familiar operator precedence (`**` before `*`/`/` before `+`/`-`), and comparison
operators (`==`, `!=`, `<`, `>=`, ...) always return a `bool`. Chained comparisons like
`0 <= temperature <= 1` are valid Python and read almost like math notation — useful when you
validate LLM parameters before sending a request.

## Type coercion and checking

Python will not silently add a string and an int:

```python
"tokens: " + str(120)   # must convert explicitly
```

Use `type(x)` to inspect a value's type and `isinstance(x, float)` to check membership, which you'll
use later when validating tool-call arguments an LLM sends back to your agent — those arguments
arrive as loosely-typed JSON and you cannot trust them blindly.

## Looking ahead

In Course 13 (Production AI) you'll validate incoming API payloads with Pydantic models built on
exactly these primitive types. Getting comfortable now with what `int`, `float`, `str`, and `bool`
really mean under the hood makes that validation code click immediately instead of feeling like
magic.
""",
                    "examples": [
                        {
                            "title": "Example: Validating a temperature parameter",
                            "code": "temperature = 0.7\nis_valid = isinstance(temperature, float) and 0.0 <= temperature <= 1.0\nprint(is_valid)  # True",
                            "explanation": "Combines a type check with a range check, the same pattern used to validate parameters before calling an LLM API.",
                        },
                        {
                            "title": "Example: Building a config string",
                            "code": "model = \"claude-sonnet-5\"\nmax_tokens = 1024\nconfig = \"model=\" + model + \", max_tokens=\" + str(max_tokens)\nprint(config)",
                            "explanation": "Shows explicit type coercion with str() since Python refuses to concatenate a string and an int directly.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create variables for a hypothetical LLM call: model (str), max_tokens (int), temperature (float), and stream (bool). Print each variable's type using type().",
                            "difficulty": "easy",
                            "hint": "Use type(variable_name) inside print().",
                        },
                        {
                            "prompt": "Write an expression that checks whether max_tokens is between 1 and 8192 inclusive, and store the result in a variable called is_valid_tokens.",
                            "difficulty": "easy",
                            "hint": "Chained comparisons work in Python: 1 <= max_tokens <= 8192.",
                        },
                        {
                            "prompt": "Given a variable count = 42, build a message string 'Retrieved 42 documents' without using str() by using an f-string instead.",
                            "difficulty": "medium",
                            "hint": "f-strings automatically convert embedded expressions to strings: f'Retrieved {count} documents'.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Built-in Types", "url": "https://docs.python.org/3/library/stdtypes.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "control-flow-conditionals-and-loops",
                    "title": "Control Flow: Conditionals and Loops",
                    "description": "Branching and repetition, the two mechanisms every agent decision loop is ultimately built from.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Write if/elif/else chains to branch program logic",
                        "Use for and while loops to iterate and repeat work",
                        "Apply break, continue, and else clauses on loops correctly",
                        "Recognize how retry loops and agent step loops are built from these primitives",
                    ],
                    "content_markdown": """
## Why this matters

Strip away the marketing language and an "AI agent" is a loop: check a condition, decide what to
do, act, repeat. Every retry-with-backoff call to an LLM API, every "keep calling tools until the
model returns a final answer" loop you'll write in Course 9 (AI Agents), is built from the same
`if`, `for`, and `while` statements you're learning here.

## Conditionals

```python
response_status = 429  # rate limited

if response_status == 200:
    print("success")
elif response_status == 429:
    print("rate limited, back off and retry")
elif response_status >= 500:
    print("server error, retry with backoff")
else:
    print("unrecoverable error")
```

Python has no switch statement in older versions, so chained `elif` (or `match` in 3.10+) is the
idiomatic way to branch across several discrete cases like HTTP status codes.

## for loops

`for` loops iterate over anything iterable — lists, strings, ranges, dictionaries:

```python
documents = ["doc1.txt", "doc2.txt", "doc3.txt"]
for doc in documents:
    print(f"Indexing {doc}")

for i in range(3):
    print(f"Attempt {i + 1}")
```

## while loops and retry logic

`while` loops repeat until a condition becomes false, which is exactly the shape of a retry loop:

```python
max_retries = 3
attempt = 0
succeeded = False

while attempt < max_retries and not succeeded:
    attempt += 1
    print(f"Calling API, attempt {attempt}")
    succeeded = attempt == 3  # pretend it succeeds on the 3rd try

print("Success" if succeeded else "Gave up")
```

This exact pattern — bounded retries with a success flag — reappears when you build resilient LLM
API calls in Course 8 (LLM APIs) and tool-calling agents in Course 9.

## break, continue, and loop else

`break` exits a loop immediately; `continue` skips to the next iteration; a loop's `else` clause runs
only if the loop finished without hitting `break`:

```python
target_id = "doc-042"
found = False
for doc_id in ["doc-01", "doc-042", "doc-99"]:
    if doc_id == target_id:
        found = True
        break
else:
    print("not found")  # skipped here because we broke out
```

## Looking ahead

When you build a LangGraph agent in Course 11, the graph's execution engine is doing this same
"loop until a stop condition" logic for you — but understanding it explicitly here means you'll be
able to debug a stuck agent instead of treating the framework as a black box.
""",
                    "examples": [
                        {
                            "title": "Example: Retry loop with exponential backoff (conceptual)",
                            "code": "attempt = 0\ndelay = 1\nwhile attempt < 4:\n    attempt += 1\n    print(f\"attempt {attempt}, waiting {delay}s\")\n    delay *= 2",
                            "explanation": "Doubles the wait time each attempt, the standard shape of backoff logic used before real network calls.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a for loop over the list [200, 404, 429, 500, 200] that prints 'ok' for 200, 'retry' for 429 or 500, and 'skip' for anything else.",
                            "difficulty": "easy",
                            "hint": "Use if/elif inside the loop body, checking membership with `in (429, 500)`.",
                        },
                        {
                            "prompt": "Write a while loop that simulates polling a job status ('pending', 'pending', 'done') and stops as soon as it sees 'done', printing each status checked.",
                            "difficulty": "medium",
                            "hint": "Use a list as a stand-in for real API responses and pop(0) or an index counter.",
                        },
                        {
                            "prompt": "Using break and a loop else clause, search a list of tool names for 'web_search' and print 'found' or 'not available' accordingly.",
                            "difficulty": "medium",
                            "hint": "Put the print('not available') in the for loop's else block.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: More Control Flow Tools", "url": "https://docs.python.org/3/tutorial/controlflow.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "data-structures",
            "title": "Data Structures",
            "description": "Lists, tuples, sets, and dictionaries — the containers that hold every prompt, document, and API payload you will process.",
            "order_index": 2,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "lists-tuples-and-sets",
                    "title": "Lists, Tuples, and Sets",
                    "description": "Ordered, mutable sequences; immutable sequences; and unordered unique collections, and when to reach for each.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Create, index, and slice lists and tuples",
                        "Explain the mutability difference between lists and tuples",
                        "Use sets to deduplicate and perform membership checks efficiently",
                        "Choose the right collection type for a given AI-pipeline task",
                    ],
                    "content_markdown": """
## Why this matters

A batch of retrieved document chunks, the conversation history you send to an LLM, the list of tool
names an agent can call — these are all Python lists in practice. Picking the right collection type
(list vs tuple vs set) affects both correctness and performance once you're processing thousands of
embeddings in Course 6.

## Lists: ordered and mutable

```python
retrieved_chunks = ["Paris is the capital of France.", "The Eiffel Tower is in Paris."]
retrieved_chunks.append("France is in Western Europe.")
retrieved_chunks[0] = "Paris is France's capital city."  # mutation in place
print(len(retrieved_chunks))  # 3
```

Lists support slicing, which you'll use constantly to trim conversation history to fit a context
window:

```python
conversation = ["msg1", "msg2", "msg3", "msg4", "msg5"]
last_three = conversation[-3:]   # most recent 3 messages
```

## Tuples: ordered and immutable

Tuples look like lists but cannot be changed after creation, which makes them ideal for fixed
records like a (role, content) pair or a coordinate:

```python
message = ("user", "What's the weather in Paris?")
role, content = message  # unpacking
```

Because tuples are immutable, they're hashable and can be used as dictionary keys — lists cannot.

## Sets: unordered and unique

Sets automatically deduplicate and give you fast membership tests:

```python
seen_doc_ids = set()
doc_ids = ["d1", "d2", "d1", "d3", "d2"]
for doc_id in doc_ids:
    seen_doc_ids.add(doc_id)
print(seen_doc_ids)          # {'d1', 'd2', 'd3'}
print("d1" in seen_doc_ids)  # True, and O(1) on average
```

Set operations (`union`, `intersection`, `difference`) are useful when comparing tool names two
agents support, or deduplicating retrieved chunks across multiple retrieval passes.

## Choosing between them

- Need order and the ability to change contents? Use a **list**.
- Need a fixed, unchangeable record, possibly as a dict key? Use a **tuple**.
- Need uniqueness and fast "have I seen this before" checks? Use a **set**.

## Looking ahead

In Course 5 (RAG) you'll deduplicate retrieved chunks across multiple queries using sets, and in
Course 9 (AI Agents) tool registries are frequently modeled as lists of dictionaries wrapped by a
set of available tool names for fast lookup. These are not academic exercises — they are the exact
data shapes production RAG and agent code uses.
""",
                    "examples": [
                        {
                            "title": "Example: Deduplicating retrieved chunks",
                            "code": "chunks = [\"a\", \"b\", \"a\", \"c\"]\nunique_chunks = list(set(chunks))\nprint(sorted(unique_chunks))",
                            "explanation": "Converts to a set to drop duplicates, then back to a list; sorted() gives deterministic output for printing.",
                        },
                        {
                            "title": "Example: Slicing recent conversation turns",
                            "code": "history = [\"hi\", \"hello\", \"how are you\", \"good\", \"great\"]\nrecent = history[-2:]\nprint(recent)",
                            "explanation": "Negative slicing grabs the tail of a list, a common trick for trimming context sent to an LLM.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a list of 5 document filenames, then use slicing to get the first 2 and the last 2 in separate variables.",
                            "difficulty": "easy",
                            "hint": "Use docs[:2] and docs[-2:].",
                        },
                        {
                            "prompt": "Given two lists of tool names available to Agent A and Agent B, use sets to find tools available to both, and tools available only to A.",
                            "difficulty": "medium",
                            "hint": "set(a) & set(b) for intersection, set(a) - set(b) for difference.",
                        },
                        {
                            "prompt": "Create a tuple representing a chat message as (role, content, token_count), then unpack it into three variables and print a formatted summary.",
                            "difficulty": "easy",
                            "hint": "role, content, token_count = message_tuple",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Data Structures", "url": "https://docs.python.org/3/tutorial/datastructures.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "dictionaries-and-nested-data",
                    "title": "Dictionaries and Nested Data",
                    "description": "Key-value mappings and the nested list-of-dicts shapes that every LLM API request and response is built from.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Create, access, and update dictionaries using keys",
                        "Safely handle missing keys with .get() and defaults",
                        "Navigate nested dictionaries and lists of dictionaries",
                        "Recognize the dict shape used by chat message APIs",
                    ],
                    "content_markdown": """
## Why this matters

Open the documentation for any LLM API — Claude, OpenAI, anything — and the request body is a
dictionary with a `messages` key holding a list of dictionaries, each with `role` and `content`
keys. If nested dictionaries feel awkward to you, every single API call in this program will feel
awkward. This lesson makes them feel natural.

## Creating and accessing dictionaries

```python
message = {"role": "user", "content": "Summarize this document."}
print(message["role"])       # "user"
message["content"] = "New content"  # update in place
message["timestamp"] = 1234567890   # add a new key
```

Accessing a missing key with `[]` raises a `KeyError`. Use `.get()` to avoid crashing on optional
fields, which matters because API responses often omit fields you don't expect:

```python
usage = {"input_tokens": 120}
output_tokens = usage.get("output_tokens", 0)  # 0, no crash
```

## Nested structures: the shape of a real API call

```python
request_body = {
    "model": "claude-sonnet-5",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "What is the capital of France?"},
        {"role": "assistant", "content": "Paris."},
        {"role": "user", "content": "And its population?"},
    ],
}

last_user_message = request_body["messages"][-1]["content"]
print(last_user_message)  # "And its population?"
```

This is not a contrived example — it is essentially the exact JSON body you will send to an LLM API
in Course 8. Being able to read `request_body["messages"][-1]["content"]` fluently, without
counting brackets, is a real productivity skill.

## Iterating over dictionaries

```python
for message in request_body["messages"]:
    print(f"{message['role']}: {message['content']}")

for key, value in usage.items():
    print(key, "->", value)
```

## Building dictionaries dynamically

Dict and list comprehensions let you transform data compactly:

```python
token_counts = {"doc1": 120, "doc2": 340, "doc3": 90}
over_budget = {name: count for name, count in token_counts.items() if count > 100}
print(over_budget)  # {'doc1': 120, 'doc2': 340}
```

## Looking ahead

Course 8 (LLM APIs) has you construct request bodies exactly like `request_body` above, and Course
9 (AI Agents) has you parse tool-call arguments out of nested response dictionaries. Comfort with
`.get()`, safe defaults, and bracket-chaining now removes an entire category of friction later.
""",
                    "examples": [
                        {
                            "title": "Example: Safely reading optional API fields",
                            "code": "response = {\"id\": \"msg_1\", \"usage\": {\"input_tokens\": 50}}\noutput_tokens = response.get(\"usage\", {}).get(\"output_tokens\", 0)\nprint(output_tokens)  # 0",
                            "explanation": "Chains .get() calls with defaults so a missing nested key never raises a KeyError.",
                        },
                        {
                            "title": "Example: Extracting all user messages",
                            "code": "messages = [\n    {\"role\": \"user\", \"content\": \"hi\"},\n    {\"role\": \"assistant\", \"content\": \"hello\"},\n    {\"role\": \"user\", \"content\": \"bye\"},\n]\nuser_texts = [m[\"content\"] for m in messages if m[\"role\"] == \"user\"]\nprint(user_texts)",
                            "explanation": "A list comprehension filters and extracts in one line, a pattern you will use constantly when processing message histories.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a dictionary representing an LLM API request with keys model, max_tokens, and messages (a list with one user message). Print the model name.",
                            "difficulty": "easy",
                            "hint": "Nest a list of dicts inside the outer dict under the 'messages' key.",
                        },
                        {
                            "prompt": "Given a response dict that may or may not have a 'stop_reason' key, write code that prints the stop reason or 'unknown' if missing, without raising an error.",
                            "difficulty": "easy",
                            "hint": "Use response.get('stop_reason', 'unknown').",
                        },
                        {
                            "prompt": "Given a list of message dicts with 'role' and 'tokens' keys, use a dict comprehension to build a mapping from role to total tokens used by that role.",
                            "difficulty": "hard",
                            "hint": "You'll need a loop or a small helper since summing per-key requires accumulation, not a plain comprehension alone.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Mapping Types - dict", "url": "https://docs.python.org/3/library/stdtypes.html#mapping-types-dict", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "functions",
            "title": "Functions",
            "description": "Packaging logic into reusable, composable units — the shape of every tool an agent will eventually call.",
            "order_index": 3,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "writing-reusable-functions",
                    "title": "Writing Reusable Functions",
                    "description": "Defining functions with parameters, defaults, and return values that keep your code DRY and testable.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define functions with positional, keyword, and default parameters",
                        "Return single and multiple values from a function",
                        "Write clear docstrings that describe a function's contract",
                        "Explain how function signatures map to agent tool definitions",
                    ],
                    "content_markdown": """
## Why this matters

Every "tool" you give an AI agent in Course 9 is, underneath the framework glue, a plain Python
function with a clear signature and a docstring. Frameworks like LangChain literally read your
function's name, parameters, and docstring to build the tool schema an LLM sees. Writing clean
functions now is directly writing better agent tools later.

## Defining a function

```python
def summarize(text, max_words=50):
    '''Return the first max_words words of text, followed by '...' if truncated.'''
    words = text.split()
    if len(words) <= max_words:
        return text
    return " ".join(words[:max_words]) + "..."

result = summarize("This is a long document about AI agents...", max_words=5)
```

`max_words=50` is a default parameter — callers can omit it. Parameters without defaults must come
before parameters with defaults.

## Keyword arguments

```python
def call_model(prompt, model="claude-sonnet-5", temperature=0.7, max_tokens=1024):
    return {"prompt": prompt, "model": model, "temperature": temperature, "max_tokens": max_tokens}

call_model("Hello", temperature=0.2, max_tokens=500)
```

Passing arguments by keyword (`temperature=0.2`) instead of position makes calls self-documenting —
critical once a function has four or five configuration parameters, which is typical for LLM call
wrappers.

## Returning multiple values

Python functions can return a tuple, which callers unpack:

```python
def split_prompt(text):
    if ":" in text:
        role, content = text.split(":", 1)
        return role.strip(), content.strip()
    return "user", text

role, content = split_prompt("system: Be concise.")
```

## Docstrings as contracts

```python
def retry_call(fn, max_attempts=3):
    '''
    Call fn() up to max_attempts times, returning its result on first success.
    Raises the last exception if all attempts fail.
    '''
    ...
```

A good docstring states what goes in, what comes out, and what can go wrong — exactly the
information an LLM needs when a docstring is exposed to it as a tool description.

## Looking ahead

When you define your first LangChain tool in Course 10, you'll write `def get_weather(city: str) ->
str:` with a docstring, and the framework will hand the function's name, parameters, and docstring
straight to the model. There is no new concept there — it's this lesson, wrapped in a decorator.
""",
                    "examples": [
                        {
                            "title": "Example: A validation function with a default",
                            "code": "def is_valid_temperature(value, minimum=0.0, maximum=1.0):\n    \"\"\"Return True if value is within [minimum, maximum].\"\"\"\n    return minimum <= value <= maximum\n\nprint(is_valid_temperature(0.7))\nprint(is_valid_temperature(1.5))",
                            "explanation": "Uses default parameters so most callers can just pass a value, while still allowing custom bounds.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a function count_tokens_approx(text) that returns len(text) // 4 as a rough token estimate, with a clear docstring.",
                            "difficulty": "easy",
                            "hint": "Integer division // rounds down automatically.",
                        },
                        {
                            "prompt": "Write a function build_message(role, content, name=None) that returns a dict, including the 'name' key only if it was provided.",
                            "difficulty": "medium",
                            "hint": "Check `if name is not None:` before adding it to the dict.",
                        },
                        {
                            "prompt": "Write a function that returns both the shortest and longest string from a list of strings as a tuple, and unpack the result when calling it.",
                            "difficulty": "medium",
                            "hint": "Use the built-in min() and max() functions with the key=len argument.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Defining Functions", "url": "https://docs.python.org/3/tutorial/controlflow.html#defining-functions", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "args-kwargs-and-higher-order-functions",
                    "title": "*args, **kwargs, and Higher-Order Functions",
                    "description": "Flexible function signatures and functions that take or return other functions — the backbone of decorators and callbacks.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Use *args and **kwargs to accept variable numbers of arguments",
                        "Pass functions as arguments to other functions",
                        "Write and apply a simple decorator",
                        "Connect these patterns to callback and middleware code used in agent frameworks",
                    ],
                    "content_markdown": """
## Why this matters

Agent frameworks lean heavily on functions that wrap other functions — retry decorators, logging
middleware, tool dispatchers that accept arbitrary keyword arguments because they don't know in
advance what parameters a given tool needs. `*args` and `**kwargs` are how Python expresses "I don't
know exactly what will be passed here, but I need to accept it and forward it."

## *args: variable positional arguments

```python
def call_tools_in_order(*tool_names):
    for name in tool_names:
        print(f"calling {name}")

call_tools_in_order("search", "summarize", "translate")
```

Inside the function, `tool_names` is a tuple: `("search", "summarize", "translate")`.

## **kwargs: variable keyword arguments

```python
def build_request(**params):
    return params

req = build_request(model="claude-sonnet-5", temperature=0.7, max_tokens=1024)
print(req)  # {'model': 'claude-sonnet-5', 'temperature': 0.7, 'max_tokens': 1024}
```

This is exactly how a generic `call_llm(**kwargs)` wrapper can forward arbitrary parameters to an
underlying SDK without hardcoding every possible option.

## Combining them

```python
def dispatch_tool(tool_name, *args, **kwargs):
    print(f"Dispatching {tool_name} with args={args} kwargs={kwargs}")

dispatch_tool("web_search", "python tutorials", max_results=5)
```

This signature — name, then flexible positional and keyword arguments — is essentially what a tool
dispatcher inside an agent loop looks like in Course 9.

## Higher-order functions

A function that accepts or returns another function is "higher-order":

```python
def with_logging(fn):
    def wrapper(*args, **kwargs):
        print(f"calling {fn.__name__}")
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} returned {result}")
        return result
    return wrapper

@with_logging
def add(a, b):
    return a + b

add(2, 3)
```

`@with_logging` is a decorator — syntactic sugar for `add = with_logging(add)`. Decorators are how
you'll add retry logic, timing, and caching around LLM calls without cluttering the calls
themselves.

## Looking ahead

Course 13 (Production AI) uses decorators for caching and rate-limiting LLM calls, and Course 9's
tool-calling agents use `**kwargs`-style dispatch to route arguments an LLM generated to the correct
Python function. This lesson is the direct prerequisite for both.
""",
                    "examples": [
                        {
                            "title": "Example: A generic retry decorator",
                            "code": "def retry(times=3):\n    def decorator(fn):\n        def wrapper(*args, **kwargs):\n            last_error = None\n            for _ in range(times):\n                try:\n                    return fn(*args, **kwargs)\n                except Exception as e:\n                    last_error = e\n            raise last_error\n        return wrapper\n    return decorator\n\n@retry(times=2)\ndef flaky_call():\n    raise ValueError(\"boom\")",
                            "explanation": "A decorator factory: retry(times=3) returns a decorator, which wraps flaky_call and retries it on failure.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a function sum_all(*numbers) that returns the sum of any number of positional numeric arguments.",
                            "difficulty": "easy",
                            "hint": "Use the built-in sum() on the numbers tuple.",
                        },
                        {
                            "prompt": "Write a function make_request(url, **headers) that returns a dict with 'url' and a nested 'headers' dict built from the kwargs.",
                            "difficulty": "medium",
                            "hint": "return {'url': url, 'headers': headers} — kwargs is already a dict inside the function.",
                        },
                        {
                            "prompt": "Write a decorator time_it that prints how many arguments were passed to the wrapped function each time it's called (don't worry about real timing).",
                            "difficulty": "hard",
                            "hint": "Use len(args) + len(kwargs) inside the wrapper function.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: More on Defining Functions (arbitrary argument lists)", "url": "https://docs.python.org/3/tutorial/controlflow.html#arbitrary-argument-lists", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "object-oriented-programming",
            "title": "Object-Oriented Programming",
            "description": "Modeling stateful systems — like agents, memory stores, and tool registries — with classes.",
            "order_index": 4,
            "estimated_hours": 2.5,
            "lessons": [
                {
                    "slug": "classes-and-objects",
                    "title": "Classes and Objects",
                    "description": "Defining classes with attributes and methods to model real entities like a conversation or an agent.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Define a class with __init__ and instance methods",
                        "Distinguish instance attributes from class attributes",
                        "Create and use multiple independent instances of a class",
                        "Explain why agent state is naturally modeled as an object",
                    ],
                    "content_markdown": """
## Why this matters

An AI agent has state: a conversation history, a set of available tools, a memory buffer, a current
plan. Functions alone struggle to carry state around cleanly between calls. Classes solve exactly
this problem, which is why every agent framework you'll meet later — LangChain's `AgentExecutor`,
LangGraph's stateful graphs — is built out of classes.

## Defining a class

```python
class Conversation:
    def __init__(self, system_prompt="You are a helpful assistant."):
        self.system_prompt = system_prompt
        self.messages = []

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_history(self):
        return self.messages

convo = Conversation()
convo.add_message("user", "What's the capital of France?")
convo.add_message("assistant", "Paris.")
print(convo.get_history())
```

`__init__` is the constructor: it runs when you create a new instance and sets up initial state.
`self` refers to the specific instance a method is called on — it's how `add_message` knows *which*
conversation's `messages` list to append to.

## Instance attributes vs class attributes

```python
class Agent:
    default_model = "claude-sonnet-5"  # class attribute, shared unless overridden

    def __init__(self, name):
        self.name = name               # instance attribute, unique per object
        self.memory = []

agent_a = Agent("Researcher")
agent_b = Agent("Writer")
print(agent_a.name, agent_b.name)      # different
print(agent_a.default_model)           # shared class-level default
```

Instance attributes (`self.name`) belong to one object. Class attributes are shared by all instances
unless an instance overrides them.

## Multiple independent instances

```python
convo1 = Conversation()
convo2 = Conversation(system_prompt="You are a terse assistant.")
convo1.add_message("user", "Hi")
print(len(convo1.get_history()), len(convo2.get_history()))  # 1, 0
```

Each instance keeps its own `messages` list — this is the whole point. Two users chatting with your
app simultaneously need two separate `Conversation` objects, not one shared list.

## Looking ahead

In Course 9 you'll build an `Agent` class that owns a conversation, a tool registry, and a step
counter. In Course 12 (Multi-Agent Systems) you'll instantiate several such agent objects that
coordinate with each other. None of that is a new idea beyond what's in this lesson — it's this
lesson, scaled up.
""",
                    "examples": [
                        {
                            "title": "Example: A simple token budget tracker object",
                            "code": "class TokenBudget:\n    def __init__(self, limit):\n        self.limit = limit\n        self.used = 0\n\n    def spend(self, amount):\n        self.used += amount\n        return self.used <= self.limit\n\nbudget = TokenBudget(1000)\nprint(budget.spend(400))  # True\nprint(budget.spend(700))  # False, over budget",
                            "explanation": "Encapsulates both the limit and running total inside one object, so callers never manage two separate variables by hand.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define a class Document with attributes title and content, and a method word_count() that returns the number of words in content.",
                            "difficulty": "easy",
                            "hint": "Use len(self.content.split()) inside word_count.",
                        },
                        {
                            "prompt": "Define a class ToolRegistry with an empty list of tools, a method register(name) to add a tool name, and a method is_registered(name) to check membership.",
                            "difficulty": "medium",
                            "hint": "Store tools as self.tools = [] in __init__, and use `in` for membership checks.",
                        },
                        {
                            "prompt": "Create two instances of your Document class with different content and show that calling word_count() on each gives independent results.",
                            "difficulty": "easy",
                            "hint": "Just instantiate twice with different arguments and call the method on each.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Classes", "url": "https://docs.python.org/3/tutorial/classes.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "inheritance-and-composition",
                    "title": "Inheritance and Composition",
                    "description": "Two ways to reuse and share behavior between classes, and how to pick the right one for agent and tool hierarchies.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Create a subclass that extends a base class's behavior",
                        "Override a method and call the parent implementation with super()",
                        "Model a 'has-a' relationship using composition instead of inheritance",
                        "Decide when inheritance vs composition better fits an agent design",
                    ],
                    "content_markdown": """
## Why this matters

Agent frameworks give you a base `Agent` or `BaseTool` class and expect you to subclass it, or they
expect you to compose an agent out of smaller pieces (a memory object, a tool registry, an LLM
client). Knowing both patterns — and when each is the better fit — is a design skill you'll use in
every course from here through Course 12.

## Inheritance: "is-a" relationships

```python
class Tool:
    def __init__(self, name):
        self.name = name

    def run(self, **kwargs):
        raise NotImplementedError("Subclasses must implement run()")

class WeatherTool(Tool):
    def __init__(self):
        super().__init__(name="get_weather")

    def run(self, city):
        return f"The weather in {city} is sunny."  # placeholder logic

tool = WeatherTool()
print(tool.name)          # "get_weather", inherited
print(tool.run(city="Paris"))
```

`WeatherTool` **is a** `Tool` — it inherits `name` handling and the `run` contract, then provides its
own implementation. `super().__init__(...)` calls the parent class's constructor so you don't
duplicate its setup logic.

## Overriding methods

```python
class LoggingTool(Tool):
    def run(self, **kwargs):
        print(f"Running {self.name} with {kwargs}")
        return super().run(**kwargs)  # still calls parent, which raises here
```

Overriding lets a subclass customize behavior while optionally still invoking the original
implementation via `super()`.

## Composition: "has-a" relationships

Sometimes inheritance is the wrong tool. An `Agent` doesn't "is-a" `Memory` — it **has-a** memory.
Composition models that directly:

```python
class Memory:
    def __init__(self):
        self.items = []

    def remember(self, item):
        self.items.append(item)

class Agent:
    def __init__(self, name):
        self.name = name
        self.memory = Memory()   # composition: Agent HAS a Memory

agent = Agent("Researcher")
agent.memory.remember("User prefers concise answers.")
```

## Inheritance vs composition, in practice

Prefer composition when you're combining independent capabilities (memory + tools + an LLM client).
Prefer inheritance when subclasses genuinely share a contract and behavior, like different `Tool`
implementations that all need a `run()` method. The common advice "favor composition over
inheritance" holds here too — it keeps agent classes flexible instead of locking you into a rigid
hierarchy.

## Looking ahead

LangChain's `BaseTool` (Course 10) is a base class you inherit from, exactly like `Tool` above.
LangGraph agent state (Course 11), on the other hand, is usually composed from smaller pieces rather
than inherited. Recognizing which pattern a framework is using will make its documentation far
easier to read.
""",
                    "examples": [
                        {
                            "title": "Example: A composed Agent with memory and tools",
                            "code": "class ToolRegistry:\n    def __init__(self):\n        self.tools = {}\n\n    def register(self, tool):\n        self.tools[tool.name] = tool\n\nclass Agent:\n    def __init__(self, name):\n        self.name = name\n        self.tools = ToolRegistry()\n        self.memory = []\n\nagent = Agent(\"Researcher\")\nagent.tools.register(WeatherTool())\nprint(list(agent.tools.tools.keys()))",
                            "explanation": "The Agent is composed of a ToolRegistry and a memory list rather than inheriting from them, keeping each piece independently testable.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a base class Tool with a run() method that raises NotImplementedError, then subclass it as CalculatorTool that overrides run(expression) to return eval(expression).",
                            "difficulty": "medium",
                            "hint": "Remember to call super().__init__() if the base class sets attributes in __init__.",
                        },
                        {
                            "prompt": "Model an Agent class that HAS a list of Tool instances (composition) rather than inheriting from Tool, with a method run_tool(name, **kwargs) that finds and runs the matching tool.",
                            "difficulty": "hard",
                            "hint": "Store tools in a dict keyed by tool.name for O(1) lookup by name.",
                        },
                        {
                            "prompt": "Explain in a short comment why an Agent should NOT inherit from Tool, even though both classes have a run()-like method.",
                            "difficulty": "easy",
                            "hint": "Think about whether 'an Agent is a Tool' is true, versus 'an Agent uses tools'.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Inheritance", "url": "https://docs.python.org/3/tutorial/classes.html#inheritance", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "file-handling",
            "title": "File Handling",
            "description": "Reading, writing, and safely closing files — how documents get into and out of your AI pipelines.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "reading-and-writing-files",
                    "title": "Reading and Writing Files",
                    "description": "Safe file I/O with the with statement, text modes, and encoding.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Open, read, and write text files using the with statement",
                        "Explain why context managers prevent resource leaks",
                        "Read files line by line versus all at once",
                        "Handle file encoding issues in real-world documents",
                    ],
                    "content_markdown": """
## Why this matters

Before you can embed, chunk, or retrieve a document in Course 5, you have to get it off disk and
into a Python string. Every RAG pipeline in this program starts with file I/O exactly like this.

## Reading a file safely

```python
with open("policy.txt", "r", encoding="utf-8") as f:
    content = f.read()

print(len(content))
```

The `with` statement is a context manager: it guarantees the file is closed automatically, even if
an exception happens inside the block. Never rely on manually calling `f.close()` — it's easy to
forget, and forgotten file handles cause hard-to-debug resource leaks in long-running services like
an agent backend.

## Reading line by line

```python
with open("faq.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            print(line)
```

Iterating a file object line by line is memory-efficient for large files, since it doesn't load the
whole file into memory at once — important once you're processing large document sets in Course 5.

## Writing files

```python
with open("output.txt", "w", encoding="utf-8") as f:
    f.write("Summary generated by the agent.\\n")
    f.writelines(["Line one\\n", "Line two\\n"])
```

`"w"` mode overwrites the file entirely; `"a"` mode appends instead. Mixing them up is a classic bug
that silently destroys logs or cached results.

## Encoding matters

Real documents are rarely pure ASCII — they contain curly quotes, accented characters, emoji. Always
pass `encoding="utf-8"` explicitly rather than relying on the OS default, which varies across
Windows, macOS, and Linux and will bite you the moment a document has non-English text.

```python
try:
    with open("doc.txt", "r", encoding="utf-8") as f:
        text = f.read()
except UnicodeDecodeError:
    with open("doc.txt", "r", encoding="latin-1") as f:
        text = f.read()
```

## Looking ahead

Course 5's document loaders for RAG are a thin wrapper around exactly this pattern, generalized
across PDFs, Markdown, and HTML. Get comfortable with `with open(...) as f` now and loader code
later will read as familiar rather than mysterious.
""",
                    "examples": [
                        {
                            "title": "Example: Loading and word-counting a document",
                            "code": "with open(\"notes.txt\", \"w\", encoding=\"utf-8\") as f:\n    f.write(\"Agentic AI systems plan, act, and reflect.\")\n\nwith open(\"notes.txt\", \"r\", encoding=\"utf-8\") as f:\n    text = f.read()\n\nprint(len(text.split()))  # word count",
                            "explanation": "Writes a small file then reads it back, demonstrating the write-then-read round trip you'll do constantly with cached outputs.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write code that creates a file 'log.txt', writes three lines to it, then reads it back and prints the number of lines.",
                            "difficulty": "easy",
                            "hint": "Use f.readlines() after reopening, or count while reading.",
                        },
                        {
                            "prompt": "Write a function load_document(path) that returns the file's text content, or the string '' if the file does not exist (use try/except FileNotFoundError).",
                            "difficulty": "medium",
                            "hint": "Wrap the with-open block in a try/except FileNotFoundError.",
                        },
                        {
                            "prompt": "Write code that appends a new log line to 'log.txt' without erasing the previous contents.",
                            "difficulty": "easy",
                            "hint": "Open in 'a' mode instead of 'w'.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Reading and Writing Files", "url": "https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "working-with-csv-and-text-data",
                    "title": "Working with CSV and Text Data",
                    "description": "Parsing structured text data with the csv module and cleaning raw text for downstream AI processing.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Read and write CSV files using Python's csv module",
                        "Use DictReader/DictWriter to work with rows as dictionaries",
                        "Apply basic text-cleaning operations to raw text",
                        "Recognize CSV as a common source format for evaluation datasets",
                    ],
                    "content_markdown": """
## Why this matters

Evaluation datasets, labeled examples for few-shot prompts, and exported chat logs are very often
handed to you as CSV files. In Course 12 (Evaluation), your test sets will frequently be CSVs with
columns like `question`, `expected_answer`, `category`. Parsing them cleanly is a prerequisite for
running any evaluation.

## Reading CSV files

```python
import csv

with open("qa_pairs.csv", "r", encoding="utf-8", newline="") as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        print(row)  # each row is a list of strings
```

`newline=""` is recommended by the csv module documentation to avoid extra blank lines on some
platforms.

## DictReader: rows as dictionaries

```python
with open("qa_pairs.csv", "r", encoding="utf-8", newline="") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(row["question"], "->", row["expected_answer"])
```

`DictReader` uses the header row as keys automatically, which is almost always more readable than
indexing into a plain list by position.

## Writing CSV files

```python
rows = [
    {"question": "What is RAG?", "expected_answer": "Retrieval Augmented Generation"},
    {"question": "What is a token?", "expected_answer": "A unit of text the model processes"},
]

with open("results.csv", "w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["question", "expected_answer"])
    writer.writeheader()
    writer.writerows(rows)
```

## Basic text cleaning

Raw text pulled from documents or CSV cells often needs cleanup before it's fed to a model:

```python
def clean_text(text):
    text = text.strip()
    text = " ".join(text.split())   # collapse repeated whitespace
    return text

raw = "  This   has\\n\\nextra   whitespace.  "
print(clean_text(raw))  # "This has extra whitespace."
```

Collapsing whitespace and stripping leading/trailing spaces before chunking or embedding a document
prevents subtle inconsistencies in retrieval quality later.

## Looking ahead

Your Course 12 evaluation harness will load a CSV of test questions with `DictReader`, run each
through your agent, and write results back out with `DictWriter` — the exact pair of operations in
this lesson, applied to a real pipeline.
""",
                    "examples": [
                        {
                            "title": "Example: Building an evaluation dataset loader",
                            "code": "import csv\n\ndef load_eval_set(path):\n    with open(path, \"r\", encoding=\"utf-8\", newline=\"\") as f:\n        return list(csv.DictReader(f))\n\n# eval_set = load_eval_set(\"tests.csv\")\n# print(eval_set[0][\"question\"])",
                            "explanation": "Wraps DictReader in a reusable function that returns a list of dict rows, ready for iteration in an evaluation loop.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write code that creates a CSV file with columns 'prompt' and 'category' containing 3 rows, then reads it back using DictReader and prints each row.",
                            "difficulty": "easy",
                            "hint": "Use csv.DictWriter to create it, then csv.DictReader to read it.",
                        },
                        {
                            "prompt": "Write a function clean_text(text) that strips whitespace, collapses multiple spaces into one, and removes any tab characters.",
                            "difficulty": "medium",
                            "hint": "text.replace('\\t', ' ') then ' '.join(text.split()).",
                        },
                        {
                            "prompt": "Given a CSV of question/answer pairs, write code that filters and writes out only rows where the category column equals 'hard' to a new CSV file.",
                            "difficulty": "medium",
                            "hint": "Read with DictReader, filter with a list comprehension or loop, write with DictWriter.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: csv — CSV File Reading and Writing", "url": "https://docs.python.org/3/library/csv.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "apis-and-json",
            "title": "APIs and JSON",
            "description": "The two technologies underneath every LLM SDK call: JSON serialization and HTTP requests.",
            "order_index": 6,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "parsing-and-producing-json",
                    "title": "Parsing and Producing JSON",
                    "description": "Converting between Python objects and JSON text with the json module, and handling malformed data.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Serialize Python dicts/lists to JSON strings with json.dumps",
                        "Parse JSON strings into Python objects with json.loads",
                        "Handle malformed or unexpected JSON gracefully",
                        "Explain why JSON is the universal interchange format for LLM tool calls",
                    ],
                    "content_markdown": """
## Why this matters

Every LLM API request body and response body is JSON. When an agent decides to call a tool, the
model literally generates JSON describing which tool and which arguments. If you're not fluent with
Python's `json` module, tool calling in Course 9 will feel like fighting the framework instead of
using it.

## Python objects to JSON: json.dumps

```python
import json

request = {"model": "claude-sonnet-5", "max_tokens": 1024, "messages": [{"role": "user", "content": "Hi"}]}
json_string = json.dumps(request)
print(json_string)

pretty = json.dumps(request, indent=2)  # human-readable for logging/debugging
```

`json.dumps` converts Python `dict`/`list`/`str`/`int`/`float`/`bool`/`None` into their JSON
equivalents. Note: Python's `True`/`False`/`None` become JSON's `true`/`false`/`null`.

## JSON to Python objects: json.loads

```python
raw_response = '{"stop_reason": "end_turn", "usage": {"input_tokens": 12, "output_tokens": 34}}'
data = json.loads(raw_response)
print(data["usage"]["output_tokens"])  # 34, now a normal Python int
```

This is exactly what happens when an HTTP client hands you a raw JSON response body from an LLM API
— you `json.loads()` it once, then work with normal Python dicts and lists.

## Handling malformed JSON

LLMs occasionally produce JSON that's almost-but-not-quite valid (trailing commas, missing quotes).
Always guard parsing:

```python
def safe_parse(raw):
    try:
        return json.loads(raw), None
    except json.JSONDecodeError as e:
        return None, str(e)

data, error = safe_parse('{"bad": }')
if error:
    print(f"Failed to parse: {error}")
```

## Reading and writing JSON files directly

```python
with open("config.json", "w", encoding="utf-8") as f:
    json.dump(request, f, indent=2)

with open("config.json", "r", encoding="utf-8") as f:
    loaded = json.load(f)
```

Note the naming: `dumps`/`loads` work with strings; `dump`/`load` work directly with file objects.

## Looking ahead

In Course 9, when an agent's tool-calling response comes back, you will `json.loads()` the
arguments the model generated before passing them to your Python function — and you'll wrap that
call in exactly the `safe_parse` pattern above, because trusting a model's JSON output blindly is a
common source of agent crashes.
""",
                    "examples": [
                        {
                            "title": "Example: Round-tripping a tool call payload",
                            "code": "import json\n\ntool_call = {\"name\": \"get_weather\", \"arguments\": {\"city\": \"Paris\", \"units\": \"celsius\"}}\nserialized = json.dumps(tool_call)\nparsed_back = json.loads(serialized)\nprint(parsed_back[\"arguments\"][\"city\"])  # Paris",
                            "explanation": "Simulates what happens when a tool call crosses a network boundary as JSON and is parsed back into a usable Python dict.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Serialize a dict {'model': 'claude-sonnet-5', 'temperature': 0.5} to a JSON string with 2-space indentation and print it.",
                            "difficulty": "easy",
                            "hint": "json.dumps(data, indent=2)",
                        },
                        {
                            "prompt": "Write a function extract_tool_name(raw_json) that parses a JSON string and returns the value of its 'name' key, or None if parsing fails or the key is missing.",
                            "difficulty": "medium",
                            "hint": "Combine try/except json.JSONDecodeError with dict.get('name').",
                        },
                        {
                            "prompt": "Write code that reads a list of dicts from a JSON file, filters to only entries where 'active' is True, and writes the filtered list to a new JSON file.",
                            "difficulty": "medium",
                            "hint": "json.load to read, a list comprehension to filter, json.dump to write.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: json — JSON encoder and decoder", "url": "https://docs.python.org/3/library/json.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "calling-rest-apis-with-requests",
                    "title": "Calling REST APIs with requests",
                    "description": "Making HTTP GET/POST calls, sending headers and JSON bodies, and handling status codes and errors.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Make GET and POST requests using the requests library",
                        "Send JSON bodies and authentication headers correctly",
                        "Check response status codes and handle errors",
                        "Recognize this pattern as the foundation of every LLM SDK call",
                    ],
                    "content_markdown": """
## Why this matters

Under the hood, every call you make through the Anthropic SDK, OpenAI SDK, or any HTTP-based tool
(web search, a weather API, your own backend) is an HTTP request built on exactly the patterns in
this lesson. SDKs are convenience wrappers around `requests`-style calls — understanding the raw
mechanics means you can debug an SDK when something goes wrong instead of being stuck.

## A basic GET request

```python
import requests

response = requests.get("https://api.example.com/status")
print(response.status_code)   # 200
print(response.json())        # parsed JSON body, if the response is JSON
```

## A POST request with a JSON body and headers

```python
headers = {
    "Authorization": "Bearer YOUR_API_KEY",
    "Content-Type": "application/json",
}
payload = {
    "model": "claude-sonnet-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "Explain RAG in one sentence."}],
}

response = requests.post(
    "https://api.example.com/v1/messages",
    headers=headers,
    json=payload,   # requests serializes this to JSON for you
)
```

Passing `json=payload` does two things: serializes `payload` to a JSON string and sets the
`Content-Type: application/json` header automatically. This is precisely the shape of the raw call
that the Anthropic SDK makes for you in Course 8, just with retries, typed responses, and streaming
handled for you.

## Checking status codes and handling errors

```python
if response.status_code == 200:
    data = response.json()
elif response.status_code == 429:
    print("Rate limited — back off and retry")
elif response.status_code >= 500:
    print("Server error — safe to retry")
else:
    print(f"Unexpected error: {response.status_code}")
    response.raise_for_status()  # raises an HTTPError for 4xx/5xx
```

`response.raise_for_status()` is a convenient way to turn a bad status code into a Python exception
you can catch, rather than manually checking every code.

## Timeouts matter

Always set a timeout — a hung network call with no timeout can freeze an entire agent step:

```python
response = requests.post(url, json=payload, headers=headers, timeout=30)
```

## Looking ahead

Course 8 (LLM APIs) has you make this exact kind of call directly against Anthropic's Messages API
before switching to the official SDK, specifically so the SDK stops feeling like a black box. Course
9's tools that hit external APIs (search, weather, databases) are built on this same
`requests.get`/`requests.post` pattern with proper status and timeout handling.
""",
                    "examples": [
                        {
                            "title": "Example: A resilient API call wrapper",
                            "code": "import requests\n\ndef safe_get(url, timeout=10):\n    try:\n        response = requests.get(url, timeout=timeout)\n        response.raise_for_status()\n        return response.json(), None\n    except requests.exceptions.RequestException as e:\n        return None, str(e)\n\n# data, error = safe_get(\"https://api.example.com/status\")",
                            "explanation": "Wraps a GET call with a timeout, status checking, and exception handling so callers get either clean data or a clean error, never a crash.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write code that makes a GET request to 'https://httpbin.org/get' and prints the response status code and the JSON body's 'url' field.",
                            "difficulty": "easy",
                            "hint": "response.json() returns a dict you can index like any other.",
                        },
                        {
                            "prompt": "Write a function post_json(url, payload) that POSTs payload as JSON with a 10 second timeout and returns response.json() only if status_code == 200, else returns None.",
                            "difficulty": "medium",
                            "hint": "Use requests.post(url, json=payload, timeout=10) and check response.status_code.",
                        },
                        {
                            "prompt": "Extend safe_get from the example so it retries up to 3 times if a requests.exceptions.Timeout occurs, before giving up and returning the error.",
                            "difficulty": "hard",
                            "hint": "Wrap the existing try/except in a for loop over range(3), and break on success.",
                        },
                    ],
                    "resources": [
                        {"title": "Requests: HTTP for Humans - Quickstart", "url": "https://requests.readthedocs.io/en/latest/user/quickstart/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "virtual-environments",
            "title": "Virtual Environments",
            "description": "Isolating project dependencies so your AI projects don't collide with each other or your system Python.",
            "order_index": 7,
            "estimated_hours": 1.0,
            "lessons": [
                {
                    "slug": "isolating-projects-with-venv",
                    "title": "Isolating Projects with venv",
                    "description": "Why and how to create a dedicated virtual environment per project using Python's built-in venv module.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why virtual environments prevent dependency conflicts",
                        "Create, activate, and deactivate a venv",
                        "Verify which Python interpreter and packages are active",
                        "Adopt one-venv-per-project as a default habit",
                    ],
                    "content_markdown": """
## Why this matters

By Course 5 you'll have a project depending on specific versions of `numpy`, a vector database
client, and an LLM SDK. By Course 11 you'll have a second project depending on a different version
of some of the same libraries because LangGraph moves fast. Without isolation, installing one
project's dependencies can silently break another's. A virtual environment gives each project its
own private, disposable copy of installed packages.

## What a virtual environment actually is

A venv is a self-contained directory containing a Python interpreter (or a link to one) and a
`site-packages` folder for that project's installed libraries, completely separate from your
system-wide Python installation and from every other project's venv.

## Creating a venv

```bash
python -m venv .venv
```

This creates a `.venv` folder in your project directory. Convention: name it `.venv` and add it to
`.gitignore` — never commit a virtual environment to version control, only the list of what's
installed in it.

## Activating a venv

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\\Scripts\\Activate.ps1
```

Once activated, your shell prompt usually shows `(.venv)`, and `python`/`pip` now point inside the
venv instead of the system installation.

## Verifying isolation

```bash
which python        # macOS/Linux
where python         # Windows
python -m pip list   # should show only what YOU installed in this venv
```

A freshly created venv has almost nothing installed — that emptiness is the point. You add exactly
what this project needs, nothing more.

## Deactivating

```bash
deactivate
```

Returns your shell to using the system Python. You'll do this constantly when switching between
projects that need different dependency sets.

## Looking ahead

Every later course in this program assumes you're working inside an activated project venv before
running `pip install`. Course 13 (Production AI) also covers reproducing this isolation inside
Docker containers for deployment — the same core idea, one level up.
""",
                    "examples": [
                        {
                            "title": "Example: Full create-activate-verify cycle (macOS/Linux)",
                            "code": "# python -m venv .venv\n# source .venv/bin/activate\n# python -m pip list\n# deactivate",
                            "explanation": "Shell commands, not Python code, but the sequence every project in this program starts with — creating isolation before installing anything.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a virtual environment named .venv in a new project folder, activate it, and run `python -m pip list` to confirm it's nearly empty.",
                            "difficulty": "easy",
                            "hint": "python -m venv .venv, then the platform-appropriate activate command.",
                        },
                        {
                            "prompt": "Explain in your own words (1-2 sentences) what would go wrong if two AI projects on your machine shared one global Python installation and required different versions of the same library.",
                            "difficulty": "easy",
                            "hint": "Think about pip install overwriting a version one project still needs.",
                        },
                        {
                            "prompt": "Add a .gitignore file to a project that excludes .venv/ from version control, and verify with `git status` that it no longer appears as untracked.",
                            "difficulty": "medium",
                            "hint": "A single line '.venv/' in .gitignore is usually enough.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: venv — Creation of virtual environments", "url": "https://docs.python.org/3/library/venv.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 0.8}],
                },
                {
                    "slug": "managing-dependencies-with-requirements-txt",
                    "title": "Managing Dependencies with requirements.txt",
                    "description": "Capturing, pinning, and restoring a project's exact dependency set so it runs the same way everywhere.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Generate a requirements.txt from an active environment",
                        "Pin dependency versions and explain why pinning matters",
                        "Install a project's dependencies from a requirements.txt on a new machine",
                        "Distinguish direct dependencies from transitive ones",
                    ],
                    "content_markdown": """
## Why this matters

You will hand off, deploy, or revisit your AI projects across machines and over time — a teammate
clones your RAG project, or you redeploy your agent service six months from now. `requirements.txt`
is the contract that says "here is exactly what this project needs to run," and without it your
project only works on the one machine you built it on.

## Generating a requirements.txt

With your project's venv activated and packages installed:

```bash
python -m pip freeze > requirements.txt
```

This captures every installed package **and its exact version**, for example:

```
anthropic==0.34.0
requests==2.32.3
python-dotenv==1.0.1
```

## Why pinning versions matters

An unpinned `anthropic` dependency might resolve to a newer major version next month that renamed a
method you rely on, silently breaking your agent in production. Pinned versions (`==`) guarantee
that installing from `requirements.txt` today and installing from it a year from now produce
identical environments.

## Installing from requirements.txt

On a fresh machine or a teammate's laptop, after creating and activating a new venv:

```bash
python -m pip install -r requirements.txt
```

This installs every listed package at its pinned version, reproducing your environment exactly.

## Direct vs transitive dependencies

`pip freeze` dumps *everything* installed, including packages your direct dependencies pulled in
automatically (transitive dependencies). For small projects this is fine; for larger ones, tools
like `pip-tools` or `poetry` let you maintain a clean list of direct dependencies (`requirements.in`)
and generate a fully pinned lock file separately. For this course, `pip freeze` is sufficient and
standard.

## A minimal, hand-written alternative

For small projects you can also write `requirements.txt` by hand with loose version constraints:

```
anthropic>=0.34,<1.0
requests>=2.31
```

This trades reproducibility for flexibility — reasonable for early prototyping, risky for anything
you plan to deploy.

## Looking ahead

Course 13's Docker-based deployment copies your `requirements.txt` into the image and runs `pip
install -r requirements.txt` as one of the very first build steps — the exact command from this
lesson, running inside a container instead of your laptop.
""",
                    "examples": [
                        {
                            "title": "Example: A pinned requirements.txt for an LLM project",
                            "code": "# requirements.txt\n# anthropic==0.34.0\n# requests==2.32.3\n# python-dotenv==1.0.1\n\n# install with:\n# python -m pip install -r requirements.txt",
                            "explanation": "Shows the typical shape of a requirements file for a small LLM-backed project, with exact pinned versions.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "In an activated venv, install the 'requests' package, then run pip freeze and identify which line corresponds to the package you installed.",
                            "difficulty": "easy",
                            "hint": "python -m pip install requests, then python -m pip freeze | look for the 'requests==' line.",
                        },
                        {
                            "prompt": "Write a requirements.txt by hand pinning three fictional packages to specific versions, then explain what command installs them into a fresh venv.",
                            "difficulty": "easy",
                            "hint": "Format is package==version, one per line; install with pip install -r requirements.txt.",
                        },
                        {
                            "prompt": "Explain a scenario where an unpinned dependency broke a project, and how pinning in requirements.txt would have prevented it.",
                            "difficulty": "medium",
                            "hint": "Think about a library releasing a breaking major version update.",
                        },
                    ],
                    "resources": [
                        {"title": "pip docs: Requirements Files", "url": "https://pip.pypa.io/en/stable/user_guide/#requirements-files", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 0.8}],
                },
            ],
        },
        {
            "slug": "package-management",
            "title": "Package Management",
            "description": "Installing, updating, and understanding third-party packages, and how Python packaging fits together.",
            "order_index": 8,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "installing-packages-with-pip",
                    "title": "Installing Packages with pip",
                    "description": "Using pip to install, upgrade, and remove packages, and reading what got installed.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Install, upgrade, and uninstall packages using pip",
                        "Install a specific version of a package",
                        "Inspect installed packages and their metadata",
                        "Understand where pip fetches packages from by default",
                    ],
                    "content_markdown": """
## Why this matters

Every SDK you'll use for the rest of this program — `anthropic`, `openai`, `langchain`, `langgraph`,
`chromadb` — arrives via `pip install`. Being fluent with pip's everyday commands removes friction
from every single following course.

## Installing packages

```bash
python -m pip install anthropic
python -m pip install anthropic==0.34.0     # exact version
python -m pip install "anthropic>=0.30,<1.0"  # version range
```

Running pip as `python -m pip` rather than bare `pip` avoids a common trap where `pip` on your PATH
points at a different Python installation than the `python` command does — a subtle source of "it
installed but I still get ModuleNotFoundError" bugs.

## Upgrading and uninstalling

```bash
python -m pip install --upgrade anthropic
python -m pip uninstall anthropic
```

## Where packages come from

By default, pip installs from the Python Package Index (PyPI), the public repository hosting
hundreds of thousands of open-source packages. When you `pip install anthropic`, pip resolves the
name against PyPI, downloads the package and its dependencies, and installs them into the active
environment.

## Inspecting what's installed

```bash
python -m pip show anthropic     # version, location, dependencies
python -m pip list               # everything installed in this environment
python -m pip list --outdated    # packages with newer versions available
```

`pip show` is especially useful when debugging: it tells you exactly which version is installed and
where on disk, which matters when you suspect the wrong environment is active.

## A note on trust

Packages on PyPI are not reviewed the way an app store reviews apps. Only install packages you
recognize or that are well-established (high download counts, active maintenance, and in this
program's case, packages explicitly named in course materials). Installing an unfamiliar package
from an untrusted source can run arbitrary code on your machine during installation.

## Looking ahead

Course 3 (LLM Fundamentals) has you `pip install anthropic` as one of the first commands you run in
this program. Every later course adds one or two more packages to your venv using exactly these
commands.
""",
                    "examples": [
                        {
                            "title": "Example: Inspecting an installed package",
                            "code": "# python -m pip show requests\n# Name: requests\n# Version: 2.32.3\n# Location: /path/to/.venv/lib/python3.x/site-packages\n# Requires: charset-normalizer, idna, urllib3, certifi",
                            "explanation": "pip show reveals a package's version, install location, and its own dependencies, useful for debugging version mismatches.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "In an activated venv, install the 'rich' package, then use pip show to find its version and list of dependencies.",
                            "difficulty": "easy",
                            "hint": "python -m pip install rich, then python -m pip show rich.",
                        },
                        {
                            "prompt": "Install a specific older version of a package of your choice, verify the installed version with pip show, then upgrade it to the latest and verify again.",
                            "difficulty": "medium",
                            "hint": "pip install package==X.Y.Z, then pip install --upgrade package.",
                        },
                        {
                            "prompt": "List all outdated packages in your current environment and identify which, if any, look safe to upgrade versus risky.",
                            "difficulty": "medium",
                            "hint": "python -m pip list --outdated; consider major vs minor version jumps as a rough risk signal.",
                        },
                    ],
                    "resources": [
                        {"title": "pip documentation", "url": "https://pip.pypa.io/en/stable/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 0.8}],
                },
                {
                    "slug": "understanding-python-packaging",
                    "title": "Understanding Python Packaging",
                    "description": "What a package actually is, how imports resolve, and the basics of structuring your own multi-file project.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the difference between a module and a package",
                        "Structure a multi-file project with an __init__.py",
                        "Use absolute and relative imports correctly",
                        "Understand why sys.path determines what 'import X' can find",
                    ],
                    "content_markdown": """
## Why this matters

Your agent project by Course 9 will span multiple files: `tools.py`, `agent.py`, `memory.py`, a
`main.py` entry point. Understanding how Python resolves imports across files is what lets you
organize growing projects instead of cramming everything into one script.

## Modules vs packages

A **module** is a single `.py` file. A **package** is a directory of modules with an `__init__.py`
file (even an empty one) that tells Python "treat this directory as importable."

```
my_agent/
    __init__.py
    tools.py
    memory.py
    agent.py
main.py
```

From `main.py`:

```python
from my_agent.tools import web_search
from my_agent.agent import Agent
```

## What __init__.py does

An empty `__init__.py` simply marks a directory as a package. You can also use it to control what's
exposed when someone imports the package itself:

```python
# my_agent/__init__.py
from .agent import Agent
from .tools import web_search

__all__ = ["Agent", "web_search"]
```

This lets callers do `from my_agent import Agent` instead of the longer `from my_agent.agent import
Agent`.

## Absolute vs relative imports

```python
# absolute import (preferred for clarity)
from my_agent.tools import web_search

# relative import (used inside the package itself)
from .tools import web_search    # one dot: same package
from ..shared import utils       # two dots: parent package
```

Absolute imports are generally easier to read and refactor; relative imports are common inside a
package's own internal files.

## How Python finds modules: sys.path

When you write `import requests`, Python searches directories listed in `sys.path` — your current
directory, your venv's `site-packages`, and a few others — in order, and imports the first match it
finds. This is why activating the correct venv matters: it changes what `sys.path` points to.

```python
import sys
print(sys.path)  # shows exactly where Python will look for imports
```

## Looking ahead

By Course 9 you'll organize an agent project into `tools.py`, `agent.py`, and `memory.py` modules
under one package, importing between them with exactly this pattern. Structuring code this way from
the start avoids the common beginner trap of a single 800-line script that's impossible to navigate.
""",
                    "examples": [
                        {
                            "title": "Example: A minimal multi-file agent package",
                            "code": "# my_agent/tools.py\ndef web_search(query):\n    return f\"results for {query}\"\n\n# my_agent/__init__.py\nfrom .tools import web_search\n\n# main.py\nfrom my_agent import web_search\nprint(web_search(\"agentic AI\"))",
                            "explanation": "Demonstrates a package exposing a clean top-level import path via __init__.py, hiding the internal tools.py file structure from callers.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a package directory 'mathutils' with an __init__.py and a file ops.py containing an add(a, b) function. From a separate script, import and call add via 'from mathutils import add'.",
                            "difficulty": "medium",
                            "hint": "Re-export add in __init__.py with 'from .ops import add'.",
                        },
                        {
                            "prompt": "Print sys.path in a Python shell and identify which entry corresponds to your active virtual environment's site-packages.",
                            "difficulty": "easy",
                            "hint": "import sys; print(sys.path) — look for a path containing '.venv'.",
                        },
                        {
                            "prompt": "Explain, in 2-3 sentences, why 'from .tools import web_search' works inside a package's own files but fails if you try to run that file directly as a standalone script.",
                            "difficulty": "hard",
                            "hint": "Relative imports require the file to be executed as part of a package, not as __main__.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: Modules", "url": "https://docs.python.org/3/tutorial/modules.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 0.8}],
                },
            ],
        },
        {
            "slug": "async-programming",
            "title": "Async Programming",
            "description": "Running I/O-bound work concurrently with async/await, so waiting on one LLM call doesn't block another.",
            "order_index": 9,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "introduction-to-async-await",
                    "title": "Introduction to async/await",
                    "description": "Why concurrency matters for I/O-bound work, and the basics of coroutines, async def, and await.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain the difference between concurrency and parallelism",
                        "Define and run a coroutine with async def and await",
                        "Identify why LLM API calls are a textbook case for async I/O",
                        "Run a coroutine using asyncio.run",
                    ],
                    "content_markdown": """
## Why this matters

An LLM API call spends most of its time waiting — for the network round trip, for the model to
generate tokens. That waiting is "I/O-bound" time during which your CPU is doing nothing. Async
programming lets your program start several such waits at once instead of one at a time, which is
exactly what you'll need in Course 9 when an agent calls multiple tools, or in Course 12 when you
evaluate hundreds of test prompts against an LLM.

## Concurrency vs parallelism

Concurrency means *dealing with* multiple tasks by interleaving their waiting periods — one CPU
core can run many concurrent I/O-bound tasks efficiently because it switches to another task
whenever the current one is just waiting on the network. Parallelism means literally running tasks
at the same time on multiple CPU cores. Async/await in Python gives you concurrency, not
parallelism — but for I/O-bound work like API calls, concurrency is exactly what you need.

## Defining and running a coroutine

```python
import asyncio

async def fetch_greeting(name):
    await asyncio.sleep(1)   # simulates waiting on a network call
    return f"Hello, {name}!"

async def main():
    result = await fetch_greeting("world")
    print(result)

asyncio.run(main())
```

`async def` defines a coroutine function — calling it doesn't run the function immediately, it
returns a coroutine object that must be `await`ed (or scheduled) to actually execute.
`asyncio.run(main())` is the standard entry point that starts the event loop and runs your top-level
coroutine.

## await only works inside async functions

```python
async def get_data():
    return await fetch_greeting("Ada")   # OK, inside an async function

# result = await fetch_greeting("Ada")   # SyntaxError outside an async function
```

`await` pauses the current coroutine until the awaited coroutine finishes, handing control back to
the event loop so it can work on something else in the meantime — that "handing control back" is
the whole mechanism that makes concurrency possible.

## A sequential (non-concurrent) example, for contrast

```python
async def main():
    r1 = await fetch_greeting("Ada")   # waits fully here
    r2 = await fetch_greeting("Alan")  # then waits again here
    print(r1, r2)
```

This code is still async syntax, but it runs sequentially — each `await` fully completes before the
next line runs. Real concurrency (running both at once) needs `asyncio.gather`, covered in the next
lesson.

## Looking ahead

The next lesson in this module builds directly on this one to run multiple LLM API calls
concurrently with `asyncio.gather`. Course 9's agent loops that call several tools "at once" and
Course 12's evaluation harnesses that score hundreds of prompts quickly are both built on exactly
this foundation.
""",
                    "examples": [
                        {
                            "title": "Example: A coroutine that simulates an LLM call",
                            "code": "import asyncio\n\nasync def call_llm(prompt):\n    await asyncio.sleep(2)  # simulate network latency\n    return f\"Response to: {prompt}\"\n\nasync def main():\n    result = await call_llm(\"Summarize this text\")\n    print(result)\n\nasyncio.run(main())",
                            "explanation": "asyncio.sleep stands in for a real network wait; in production this would be an await on an actual async HTTP client call.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write an async function delayed_square(n) that awaits asyncio.sleep(1) then returns n * n. Run it for n=5 using asyncio.run and print the result.",
                            "difficulty": "easy",
                            "hint": "Define with async def, use await asyncio.sleep(1) inside, then asyncio.run(delayed_square(5)).",
                        },
                        {
                            "prompt": "Write two async functions that each simulate a different delay, and call them sequentially with await inside a main() coroutine, printing how long the whole thing conceptually takes (sum of delays).",
                            "difficulty": "medium",
                            "hint": "Sequential awaits mean total time is the sum of each delay, not the max.",
                        },
                        {
                            "prompt": "Explain in your own words why calling an async function without await (e.g. just `fetch_greeting('x')`) does not run its body and instead returns a coroutine object.",
                            "difficulty": "medium",
                            "hint": "Try printing the return value of calling an async function without await — it prints something like <coroutine object ...>.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: asyncio — Coroutines and Tasks", "url": "https://docs.python.org/3/library/asyncio-task.html", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "concurrent-api-calls-with-asyncio",
                    "title": "Concurrent API Calls with asyncio",
                    "description": "Using asyncio.gather to run multiple awaitable calls at the same time, and when concurrency actually helps.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Use asyncio.gather to run multiple coroutines concurrently",
                        "Measure and compare sequential vs concurrent execution time",
                        "Handle exceptions raised by individual concurrent tasks",
                        "Recognize when concurrency helps versus when it adds unnecessary complexity",
                    ],
                    "content_markdown": """
## Why this matters

Imagine evaluating an agent against 50 test prompts, or fanning a query out to three different
retrieval sources before merging results. Doing this one call at a time could take minutes; running
them concurrently with `asyncio.gather` can cut that to roughly the time of the single slowest
call. This is a direct, measurable speedup you will rely on in Course 5 (parallel retrieval) and
Course 12 (batch evaluation).

## Sequential vs concurrent: measuring the difference

```python
import asyncio
import time

async def call_llm(prompt, delay=1):
    await asyncio.sleep(delay)  # stand-in for real network latency
    return f"Response to: {prompt}"

async def sequential_demo():
    start = time.perf_counter()
    r1 = await call_llm("prompt 1")
    r2 = await call_llm("prompt 2")
    r3 = await call_llm("prompt 3")
    print(f"Sequential took {time.perf_counter() - start:.2f}s")  # ~3s

async def concurrent_demo():
    start = time.perf_counter()
    r1, r2, r3 = await asyncio.gather(
        call_llm("prompt 1"),
        call_llm("prompt 2"),
        call_llm("prompt 3"),
    )
    print(f"Concurrent took {time.perf_counter() - start:.2f}s")  # ~1s
```

`asyncio.gather` schedules all its coroutines to run concurrently and returns their results in the
same order they were passed in, once all have completed.

## Gathering a dynamic list of calls

```python
async def evaluate_all(prompts):
    tasks = [call_llm(p) for p in prompts]
    return await asyncio.gather(*tasks)

# results = asyncio.run(evaluate_all(["q1", "q2", "q3", "q4", "q5"]))
```

The `*tasks` unpacking passes each coroutine in the list as a separate argument to `gather`, which
is the standard pattern for fanning out an arbitrary number of concurrent calls.

## Handling errors in concurrent tasks

By default, if any task raises an exception, `gather` immediately raises that exception, potentially
losing results from tasks that already succeeded. Pass `return_exceptions=True` to collect
exceptions alongside successful results instead of crashing the whole batch:

```python
results = await asyncio.gather(*tasks, return_exceptions=True)
for result in results:
    if isinstance(result, Exception):
        print(f"Task failed: {result}")
    else:
        print(f"Success: {result}")
```

This matters enormously for evaluation harnesses: one flaky call to an LLM API shouldn't discard 49
other successful results.

## When concurrency doesn't help

Concurrency speeds up I/O-bound work (waiting on network calls). It does **not** speed up CPU-bound
work (heavy computation) — for that you'd need multiprocessing instead, which is outside this
course's scope. Don't reach for `asyncio` to speed up a tight numeric loop; reach for it when you're
waiting on network calls to LLMs, databases, or external APIs.

## Looking ahead

Course 9's multi-tool agent steps and Course 12's batch evaluation scripts both use
`asyncio.gather(*tasks, return_exceptions=True)` verbatim as their core concurrency pattern. This
lesson is not a side topic — it's infrastructure you will reuse directly.
""",
                    "examples": [
                        {
                            "title": "Example: Fanning out 5 simulated LLM calls concurrently",
                            "code": "import asyncio\n\nasync def call_llm(prompt):\n    await asyncio.sleep(1)\n    return f\"answer to {prompt}\"\n\nasync def main():\n    prompts = [f\"q{i}\" for i in range(5)]\n    results = await asyncio.gather(*(call_llm(p) for p in prompts))\n    print(results)\n\nasyncio.run(main())",
                            "explanation": "All 5 simulated calls run concurrently, so the whole batch takes about 1 second rather than 5.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write three async functions with different asyncio.sleep delays (1s, 2s, 3s), run them concurrently with asyncio.gather, and print the total elapsed time using time.perf_counter.",
                            "difficulty": "medium",
                            "hint": "Total time should be close to the longest delay (3s), not the sum (6s).",
                        },
                        {
                            "prompt": "Modify the concurrent example so one of the coroutines raises a ValueError, then use return_exceptions=True to collect results without crashing, printing which ones failed.",
                            "difficulty": "hard",
                            "hint": "Check isinstance(result, Exception) when iterating the gathered results.",
                        },
                        {
                            "prompt": "Write an async function evaluate_prompts(prompts) that concurrently calls a simulated call_llm() for each prompt and returns a dict mapping prompt to result.",
                            "difficulty": "medium",
                            "hint": "Gather the results in order, then zip(prompts, results) to build the dict.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: asyncio.gather", "url": "https://docs.python.org/3/library/asyncio-task.html#asyncio.gather", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "python-for-ai-applications",
            "title": "Python for AI Applications",
            "description": "Pulling everything together: environment configuration, SDK basics, and a first working chat loop.",
            "order_index": 10,
            "estimated_hours": 2.0,
            "lessons": [
                {
                    "slug": "working-with-ai-sdks-and-environment-config",
                    "title": "Working with AI SDKs and Environment Config",
                    "description": "Managing API keys safely with environment variables and .env files, and the shape of a typical AI SDK client.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Store secrets in environment variables instead of hardcoding them",
                        "Load a .env file using python-dotenv",
                        "Instantiate and configure a typical AI SDK client object",
                        "Explain the security risk of committing API keys to source control",
                    ],
                    "content_markdown": """
## Why this matters

The very first thing you'll do in Course 3 is get an API key and use it to call an LLM. How you
store that key is a real security decision, not a formality — leaked API keys get abused and billed
to your account within minutes of being pushed to a public GitHub repo. This lesson is the habit
that prevents that.

## Never hardcode secrets

```python
# NEVER do this:
api_key = "sk-ant-abc123..."  # visible to anyone who sees this file or its git history
```

Even a private repo isn't safe enough — git history remembers deleted lines forever unless you
rewrite history, which is painful and easy to get wrong.

## Environment variables

```python
import os

api_key = os.environ.get("ANTHROPIC_API_KEY")
if api_key is None:
    raise RuntimeError("ANTHROPIC_API_KEY is not set")
```

Environment variables live outside your source code, set in your shell or deployment platform, so
they never end up in a file that gets committed to git.

## Using a .env file locally with python-dotenv

For local development, a `.env` file (never committed — add it to `.gitignore`) keeps secrets out of
your shell history too:

```
# .env
ANTHROPIC_API_KEY=sk-ant-abc123...
```

```python
from dotenv import load_dotenv
import os

load_dotenv()  # reads .env and sets values into os.environ
api_key = os.environ.get("ANTHROPIC_API_KEY")
```

`python-dotenv` is a small, standard package (`pip install python-dotenv`) used across almost every
Python AI project for exactly this purpose.

## The shape of a typical AI SDK client

Nearly every LLM SDK follows the same pattern: construct a client with your credentials, then call a
method on it.

```python
# conceptual example, real usage covered fully in Course 8
from anthropic import Anthropic

client = Anthropic(api_key=api_key)  # or it reads ANTHROPIC_API_KEY automatically
response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hello!"}],
)
```

Notice this is the exact `messages` list-of-dicts shape from the earlier lesson on dictionaries —
the SDK is just a typed, convenient wrapper around the raw JSON/HTTP call you learned in the APIs
and JSON module.

## Looking ahead

Course 3 has you set up `ANTHROPIC_API_KEY` using exactly this `.env` + `python-dotenv` pattern
before making your first real API call. Every project for the rest of the program starts the same
way: load environment variables first, construct a client second.
""",
                    "examples": [
                        {
                            "title": "Example: Safe config loading with a fallback error",
                            "code": "from dotenv import load_dotenv\nimport os\n\nload_dotenv()\n\ndef get_required_env(name):\n    value = os.environ.get(name)\n    if not value:\n        raise RuntimeError(f\"Missing required environment variable: {name}\")\n    return value\n\n# api_key = get_required_env(\"ANTHROPIC_API_KEY\")",
                            "explanation": "Fails loudly and immediately with a clear error if a required secret is missing, instead of letting a cryptic error surface later.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Create a .env file with a fake key MY_API_KEY=test123, load it with python-dotenv, and print the value from os.environ.",
                            "difficulty": "easy",
                            "hint": "pip install python-dotenv first, then load_dotenv() before reading os.environ.",
                        },
                        {
                            "prompt": "Write a function get_required_env(name) that raises a clear RuntimeError if the named environment variable is missing or empty, and returns its value otherwise.",
                            "difficulty": "medium",
                            "hint": "Treat both None and an empty string as 'missing'.",
                        },
                        {
                            "prompt": "Add .env to a project's .gitignore and explain, in 1-2 sentences, what could go wrong if you forgot to do this before pushing to a public repository.",
                            "difficulty": "easy",
                            "hint": "Think about automated bots that scan public repos for leaked API keys.",
                        },
                    ],
                    "resources": [
                        {"title": "python-dotenv documentation", "url": "https://pypi.org/project/python-dotenv/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
                {
                    "slug": "building-a-simple-cli-chat-loop",
                    "title": "Building a Simple CLI Chat Loop",
                    "description": "Capstone project: combine input loops, lists of dicts, and functions into a working command-line chat interface.",
                    "lesson_type": "project",
                    "order_index": 2,
                    "estimated_minutes": 40,
                    "learning_objectives": [
                        "Combine while loops, functions, and data structures into a complete small program",
                        "Maintain conversation history as a growing list of message dicts",
                        "Implement a clean exit condition and basic input handling",
                        "Structure code so an LLM API call can be dropped in later without a rewrite",
                    ],
                    "content_markdown": """
## Why this matters

This lesson is the capstone of Course 1: every concept from this course — variables, control flow,
lists and dicts, functions, classes, file I/O — comes together in one small but real program. It
will not call a real LLM yet (that's Course 3), but its structure is exactly what Course 3's first
real chat script will look like, with one function swapped out.

## The shape of the program

```python
class ChatSession:
    def __init__(self, system_prompt="You are a helpful assistant."):
        self.system_prompt = system_prompt
        self.history = []

    def add_user_message(self, content):
        self.history.append({"role": "user", "content": content})

    def add_assistant_message(self, content):
        self.history.append({"role": "assistant", "content": content})

    def get_response(self, user_input):
        '''Placeholder for a real LLM call -- Course 3 replaces this body.'''
        return f"(stub) You said: {user_input}"
```

## The main loop

```python
def run_chat():
    session = ChatSession()
    print("Chat started. Type 'exit' or 'quit' to end.")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not user_input:
            continue  # skip empty input, don't waste a turn

        session.add_user_message(user_input)
        reply = session.get_response(user_input)
        session.add_assistant_message(reply)
        print(f"Assistant: {reply}")

if __name__ == "__main__":
    run_chat()
```

Notice every piece is something you've already built in isolation this course: a `while True` loop
with a clean `break` condition, input validation with `continue`, a class holding growing state (the
`history` list of message dicts), and a method whose body is intentionally a stub — a placeholder
you'll replace with a real `client.messages.create(...)` call in Course 3 without touching anything
else in this file.

## Saving the conversation to disk

```python
import json

def save_history(session, path="chat_log.json"):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(session.history, f, indent=2)
```

Add a call to `save_history(session)` right before `break` in the main loop, and you have a working
transcript logger — the exact pattern Course 12's evaluation harness uses to record agent
conversations for later scoring.

## Why the stub matters

Keeping `get_response` as an isolated method with one clear job (take a string, return a string) is
the entire reason Course 3 can slot in a real API call by rewriting a handful of lines instead of
your whole program. This is the same "swap the implementation, keep the interface" idea you'll rely
on constantly when swapping LLM providers or tool implementations later in the program.

## Looking ahead

In Course 3, `get_response` becomes a real call to the Claude API using the `.env`-loaded API key
from the previous lesson. In Course 9, `ChatSession` grows a `tools` attribute and the loop grows a
branch that checks whether the model's response is a tool call or a final answer — but the skeleton
you build here doesn't change shape.
""",
                    "examples": [
                        {
                            "title": "Example: A minimal end-to-end run",
                            "code": "session = ChatSession()\nsession.add_user_message(\"Hi there\")\nreply = session.get_response(\"Hi there\")\nsession.add_assistant_message(reply)\nprint(session.history)",
                            "explanation": "Exercises the class directly without the input() loop, useful for testing the ChatSession logic in isolation before wiring up interactive input.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement the ChatSession class and run_chat() function exactly as described, and confirm typing 'exit' cleanly ends the program.",
                            "difficulty": "medium",
                            "hint": "Test the exit condition first with a minimal loop before adding history tracking.",
                        },
                        {
                            "prompt": "Add a 'history' command: when the user types it, print the full conversation so far as role: content lines instead of sending it as a chat message.",
                            "difficulty": "medium",
                            "hint": "Check for the command before calling add_user_message, using a separate if branch and continue.",
                        },
                        {
                            "prompt": "Add save_history() and call it automatically whenever the user exits, writing to a JSON file named with the current timestamp so each session's log doesn't overwrite the last.",
                            "difficulty": "hard",
                            "hint": "Use Python's time or datetime module to build a filename like f'chat_log_{timestamp}.json'.",
                        },
                    ],
                    "resources": [
                        {"title": "Python docs: input() built-in function", "url": "https://docs.python.org/3/library/functions.html#input", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "python", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "Python for AI: Course Assessment",
    "description": "Checks readiness to move from core Python into AI & Machine Learning Foundations.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 35,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "What is the type of the value produced by the expression `5 / 2` in Python 3?",
            "options": [
                {"id": "a", "text": "int"},
                {"id": "b", "text": "float"},
                {"id": "c", "text": "str"},
                {"id": "d", "text": "It raises a TypeError"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The `/` operator always performs true division and returns a float in Python 3, even when both operands are ints. Use `//` for floor division that returns an int.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "Which loop construct is best suited for a bounded retry-with-backoff pattern where the number of attempts is not known ahead of time but is capped at a maximum?",
            "options": [
                {"id": "a", "text": "A for loop over range(len(items))"},
                {"id": "b", "text": "A while loop with a counter and a success flag"},
                {"id": "c", "text": "A list comprehension"},
                {"id": "d", "text": "A dict comprehension"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A while loop naturally expresses 'keep trying until success or the attempt limit is reached,' which is exactly the shape of retry logic used when calling flaky APIs.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are true about Python tuples compared to lists? (Select all that apply.)",
            "options": [
                {"id": "a", "text": "Tuples are immutable after creation"},
                {"id": "b", "text": "Tuples can be used as dictionary keys, but lists cannot"},
                {"id": "c", "text": "Tuples support indexing and slicing just like lists"},
                {"id": "d", "text": "Tuples cannot contain more than 3 elements"},
            ],
            "correct_answer": {"choices": ["a", "b", "c"]},
            "explanation": "Tuples are immutable, which makes them hashable and usable as dict keys unlike lists, and they support the same indexing/slicing as lists. There is no element-count limit on tuples.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "Given `usage = {'input_tokens': 100}`, which expression safely returns 0 if 'output_tokens' is missing, without raising an error?",
            "options": [
                {"id": "a", "text": "usage['output_tokens']"},
                {"id": "b", "text": "usage.get('output_tokens', 0)"},
                {"id": "c", "text": "usage.output_tokens"},
                {"id": "d", "text": "usage['output_tokens'] or 0"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "dict.get(key, default) returns the default value instead of raising a KeyError when the key is absent, which is the safe way to read optional fields from API response dicts.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function `extract_user_messages(messages)` that takes a list of dicts, each with 'role' and 'content' keys, and returns a list containing only the 'content' values where role == 'user'.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Returns a list of content strings for every message dict whose 'role' key equals 'user', preserving original order, and returns an empty list if there are none.",
                "sample_solution": "def extract_user_messages(messages):\n    return [m[\"content\"] for m in messages if m[\"role\"] == \"user\"]",
            },
            "explanation": "This uses a list comprehension to filter and extract in one pass, the same pattern used throughout the course to process chat message histories.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "What does `*args` capture inside a function definition like `def f(*args): ...`?",
            "options": [
                {"id": "a", "text": "A dictionary of keyword arguments"},
                {"id": "b", "text": "A tuple of positional arguments"},
                {"id": "c", "text": "A list of default values"},
                {"id": "d", "text": "Nothing unless keyword arguments are also passed"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "*args collects any extra positional arguments into a tuple inside the function body, which is why tool dispatcher functions use it to forward arbitrary positional inputs.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "short_answer",
            "prompt": "In one or two sentences, explain the difference between inheritance and composition, and give one example of when you would prefer composition when designing an AI agent class.",
            "options": [],
            "correct_answer": {
                "expected": "Inheritance models an 'is-a' relationship where a subclass extends a base class's behavior; composition models a 'has-a' relationship where an object holds other objects as attributes. An Agent should use composition to hold a Memory and a ToolRegistry, since an Agent is not a kind of Memory or Tool.",
                "keywords": ["is-a", "has-a", "inheritance", "composition", "agent"],
            },
            "explanation": "Composition is generally preferred when combining independent capabilities like memory, tools, and an LLM client inside an Agent, since none of those relationships are truly 'is-a'.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "Why should you always specify `encoding='utf-8'` explicitly when opening text files that may contain non-English characters?",
            "options": [
                {"id": "a", "text": "It makes file reads faster"},
                {"id": "b", "text": "The operating system's default encoding varies across platforms and can cause UnicodeDecodeErrors"},
                {"id": "c", "text": "Python requires it syntactically"},
                {"id": "d", "text": "It automatically translates the text to English"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Different operating systems default to different encodings; explicitly requesting UTF-8 avoids inconsistent behavior and decode errors when documents contain accented characters or other non-ASCII text.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the key difference between `json.dumps()` and `json.dump()`?",
            "options": [
                {"id": "a", "text": "dumps() writes to a file, dump() returns a string"},
                {"id": "b", "text": "dump() writes directly to a file object, dumps() returns a JSON string"},
                {"id": "c", "text": "They are interchangeable aliases"},
                {"id": "d", "text": "dumps() only works with lists, dump() only works with dicts"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The 's' in dumps/loads stands for 'string' — those functions work with in-memory strings, while dump/load work directly with an open file object.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "scenario",
            "prompt": "You're building an agent that calls a public weather API. The call occasionally times out, and when it fails, you don't want the whole agent request to crash — you want to log the error and let the agent continue with a fallback message. Describe the Python constructs you would combine to implement this safely (mention at least three).",
            "options": [],
            "correct_answer": {
                "expected": "Use a try/except block around the requests.post/get call to catch requests.exceptions.RequestException, set a timeout parameter on the request to avoid hanging indefinitely, and return a fallback dict/string from the except branch instead of letting the exception propagate; optionally wrap the whole thing in a retry loop or decorator for a few attempts before falling back.",
            },
            "explanation": "Production-grade API calls combine an explicit timeout, exception handling scoped to the specific exception type, and a defined fallback behavior — exactly the pattern taught across the APIs/JSON and async modules.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "In `asyncio.gather(*tasks)`, what does passing `return_exceptions=True` change?",
            "options": [
                {"id": "a", "text": "It cancels all tasks the moment one fails"},
                {"id": "b", "text": "It collects exceptions as results in the returned list instead of raising immediately on the first failure"},
                {"id": "c", "text": "It converts all coroutines into synchronous functions"},
                {"id": "d", "text": "It retries failed tasks automatically"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "With return_exceptions=True, a failing task's exception is placed in the results list at its corresponding position instead of being raised, so one failure doesn't discard the other successful results.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is `python -m pip install -r requirements.txt` with pinned versions (e.g. `anthropic==0.34.0`) preferred over unpinned installs for a project you plan to deploy?",
            "options": [
                {"id": "a", "text": "Pinned versions install faster"},
                {"id": "b", "text": "Pinned versions guarantee the exact same dependency versions are installed every time, preventing surprise breaking changes"},
                {"id": "c", "text": "Unpinned installs are not allowed by pip"},
                {"id": "d", "text": "Pinning is only relevant for Windows systems"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Pinning guarantees reproducibility: installing from the same requirements.txt today or a year from now produces an identical environment, avoiding silent breakage from upstream library updates.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is it unsafe to hardcode an API key directly in a Python source file that gets committed to a git repository, even a private one?",
            "options": [
                {"id": "a", "text": "Python source files cannot contain string literals longer than 40 characters"},
                {"id": "b", "text": "Git history retains old versions of files, so the key remains recoverable even after being 'removed' in a later commit"},
                {"id": "c", "text": "Private repositories automatically reject commits containing API keys"},
                {"id": "d", "text": "It causes a SyntaxError at import time"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Deleting a secret in a new commit does not remove it from git's history; anyone with access to the repo's history (or a future leak of it) can still recover the key unless history is explicitly rewritten.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "python",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the primary reason async/await speeds up a batch of LLM API calls, given that Python's asyncio provides concurrency rather than true parallelism?",
            "options": [
                {"id": "a", "text": "It runs each call on a separate CPU core"},
                {"id": "b", "text": "Most of an API call's time is spent waiting on the network, and the event loop can work on other calls during that wait instead of blocking"},
                {"id": "c", "text": "It compresses the request payloads to reduce transfer time"},
                {"id": "d", "text": "It automatically caches identical prompts"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "LLM API calls are I/O-bound: the CPU is idle during the network round trip. Async lets the event loop switch to other pending calls during that idle time, so many calls can be 'in flight' concurrently on a single thread.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "python",
        },
    ],
}
