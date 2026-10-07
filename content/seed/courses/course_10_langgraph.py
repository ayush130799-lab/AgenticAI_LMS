"""
Course 10: LangGraph

Covers stateful, graph-based orchestration of agent workflows: state, nodes,
edges, conditional routing, loops, checkpoints, persistence, human-in-the-loop
interrupts, and multi-agent workflows. This is where the agent-architecture
concepts from Course 8 (state machines, replanning, routing, verification
gates) get a dedicated, production-grade execution engine, and where
Course 9's chains and agents become one node among many in a larger graph.
"""

COURSE = {
    "slug": "langgraph",
    "title": "LangGraph",
    "subtitle": "Stateful, graph-based orchestration for agent workflows",
    "description": (
        "A hands-on build-up of LangGraph's execution model: defining typed graph "
        "state, writing nodes and wiring them with edges, branching with "
        "conditional edges, running controlled loops, checkpointing and "
        "persisting state across sessions, pausing execution for human approval, "
        "and coordinating multiple specialized agents through a supervisor graph. "
        "You'll leave able to express the agent patterns from Course 8 as an "
        "explicit, inspectable, resumable graph rather than an ad hoc loop."
    ),
    "learning_outcomes": [
        "Explain why a graph, rather than a linear chain, fits branching and looping agent workflows",
        "Define typed graph state with TypedDict and custom reducers",
        "Write node functions and wire them into a graph with add_node and add_edge",
        "Build conditional edges that route execution based on the graph's current state",
        "Implement controlled loops with explicit exit conditions and recursion limits",
        "Checkpoint and replay graph execution for debugging and reliability",
        "Persist graph state across sessions using a production-grade checkpointer",
        "Add human-in-the-loop interrupts for high-stakes actions",
        "Coordinate multiple specialized agents through a supervisor graph",
    ],
    "order_index": 10,
    "estimated_hours": 17,
    "level": "advanced",
    "icon": "workflow",
    "modules": [
        # 1. Graph Architecture
        {
            "slug": "graph-architecture",
            "title": "Graph Architecture",
            "description": "Why graphs, not linear chains, are the right execution model for agent workflows with branches and loops, and the anatomy of a StateGraph.",
            "order_index": 1,
            "estimated_hours": 1.6,
            "lessons": [
                {
                    "slug": "why-graphs-instead-of-chains",
                    "title": "Why Graphs Instead of Chains",
                    "description": "The structural limitation of linear LCEL chains for agentic workflows, and how a graph resolves it.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why a linear chain cannot naturally express branching or looping control flow",
                        "Describe a graph's nodes and edges as the units of computation and control flow",
                        "Map the agent-loop and routing patterns from Course 8 onto a graph structure",
                        "Recognize when a simple LCEL chain is still the better, simpler choice",
                    ],
                    "content_markdown": """## The shape problem with linear chains

An LCEL chain, as you built in Course 9, is fundamentally a straight line:
step A always flows into step B, which always flows into step C. That's
exactly right for a fixed pipeline — retrieve, format, prompt, generate —
where every input follows the same sequence of steps. But Course 8's
material was full of workflows that are *not* straight lines: a router that
sends a request down one of several paths, a tool-calling loop that repeats
an unknown number of times, a replanning step that jumps back to an earlier
stage when new information invalidates the plan. Forcing these into a
linear chain means smuggling control flow into conditional logic wrapped
around chain calls in your own Python code — which works, but produces
something that's no longer declarative, inspectable, or resumable the way a
chain is.

## Nodes and edges: computation and control flow, separated

A **graph** separates these two concerns explicitly. **Nodes** are units of
computation — ordinary functions that take the current state and return an
update to it, much like the node functions you'll write starting in this
course's Nodes module. **Edges** are the control flow — which node runs
next, given where execution currently is and what the state says. Unlike a
chain, an edge doesn't have to lead to exactly one fixed next step: a
**conditional edge** can route to different nodes depending on the state, and
an edge can point backward to a node that already ran, creating a loop.

```
        ┌─────────┐
        │  start  │
        └────┬────┘
             │
        ┌────▼────┐        ┌──────────────┐
        │  route  ├───────►│ handle_lookup│──► end
        └────┬────┘        └──────────────┘
             │
        ┌────▼────┐   loop back while more steps remain
        │  agent  ├──────┐
        └────┬────┘      │
             │◄───────────┘
             ▼
            end
```

This is a direct visual expression of exactly the control flow Course 8
built by hand: `dispatch()` from the Routing module is the `route` node's
conditional edges; the `tool_loop` from the Tool-Using Agents module is the
cycle back into `agent`.

## LangGraph's StateGraph

LangGraph is the concrete implementation of this idea, built on top of
LangChain's Runnable ecosystem — a `StateGraph` you'll construct in the next
lesson is itself compiled into a Runnable, so everything you learned about
`.invoke()`, `.stream()`, and composing Runnables in Course 9 still applies.
What's new is the ability to express branching and cycles as first-class,
declared structure rather than nested if/else and while loops buried in
application code.

## When a plain chain is still the right call

Not every workflow needs a graph. A fixed, linear pipeline with no branching
and no looping — the RAG chain from Course 9, for instance — is genuinely
simpler and clearer as an LCEL chain. Reach for a graph specifically when
your workflow has real branches (different paths depending on content),
real loops (an unknown number of iterations), or needs the checkpointing and
persistence features covered later in this course. Using a graph for a
task that's actually linear adds ceremony without adding value — match the
tool to the shape of the problem, not the other way around.
""",
                    "examples": [
                        {
                            "title": "The same control flow, chain-shaped vs. graph-shaped",
                            "code": (
                                "# Chain-shaped: control flow hidden in Python if/else around chain calls\n"
                                "def run(request):\n"
                                "    intent = classify_chain.invoke(request)\n"
                                "    if intent == \"lookup\":\n"
                                "        return lookup_chain.invoke(request)\n"
                                "    return task_chain.invoke(request)\n\n"
                                "# Graph-shaped: control flow is declared structure, not buried logic\n"
                                "# graph.add_conditional_edges(\"route\", lambda s: s[\"intent\"], {\"lookup\": \"handle_lookup\", \"task\": \"handle_task\"})"
                            ),
                            "explanation": "Both produce the same behavior, but the graph version makes the routing decision visible in the graph's structure rather than hidden inside a function body.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Sketch (in words or an ASCII diagram) the graph shape for a support agent that routes to either a billing handler or a technical handler, where the technical handler can loop back to itself up to 3 times before finishing.",
                            "difficulty": "easy",
                            "hint": "You'll need a routing node, two handler nodes, and a conditional edge that either loops or exits.",
                        },
                        {
                            "prompt": "Identify which Course 8 module's pattern each of these maps to: a conditional edge choosing between two nodes; an edge pointing back to an earlier node; a node that checks a replan counter before looping.",
                            "difficulty": "medium",
                            "hint": "Match to Routing, the tool-calling loop, and the bounded-replan guard respectively.",
                        },
                        {
                            "prompt": "Describe a workflow you've built or used that is genuinely linear (no branches, no loops) and explain why it would NOT benefit from being expressed as a graph.",
                            "difficulty": "medium",
                            "hint": "Think of something like a fixed ETL-style pipeline with a single fixed sequence of steps.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph conceptual guide: overview", "url": "https://langchain-ai.github.io/langgraph/concepts/high_level/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
                {
                    "slug": "anatomy-of-a-stategraph",
                    "title": "Anatomy of a StateGraph",
                    "description": "Building your first StateGraph: declaring state, adding nodes, wiring edges, and compiling it into a runnable graph.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Construct a StateGraph from a state schema",
                        "Add nodes and wire them with add_edge",
                        "Set an entry point and compile the graph",
                        "Invoke a compiled graph and inspect its output",
                    ],
                    "content_markdown": """## The five pieces of a StateGraph

Every LangGraph graph is built from the same five ingredients: a state
schema, nodes, edges, an entry point, and a compile step. Seeing all five in
one minimal example makes the structure concrete before the next several
modules dig into each piece individually.

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END

class GraphState(TypedDict):
    question: str
    answer: str

def generate_answer(state: GraphState) -> dict:
    response = llm.invoke(f"Answer concisely: {state['question']}")
    return {"answer": response.content}

graph_builder = StateGraph(GraphState)
graph_builder.add_node("generate_answer", generate_answer)
graph_builder.set_entry_point("generate_answer")
graph_builder.add_edge("generate_answer", END)

graph = graph_builder.compile()
result = graph.invoke({"question": "What is a vector database?", "answer": ""})
print(result["answer"])
```

## Walking through each piece

`GraphState` is a `TypedDict` — the same pattern Course 8's Agent State
module used for hand-rolled state, now formalized as the schema LangGraph
uses to validate what nodes are allowed to read and write.

`add_node("generate_answer", generate_answer)` registers a node under a
string name; the function itself takes the current state and returns a
**partial update** — a dict of the fields it's changing, not the entire
state object. LangGraph merges this update into the full state for you.

`set_entry_point` declares which node runs first when the graph is invoked.
`add_edge("generate_answer", END)` wires an unconditional edge to the
special `END` marker, meaning execution stops once `generate_answer`
finishes — the simplest possible graph shape, structurally a single-node
chain.

`.compile()` turns the builder into an executable graph — a Runnable, in
fact, which is why `.invoke()` works exactly the way it did on the chains
from Course 9.

## Nodes return partial updates, not full state

This is worth dwelling on because it's a common early mistake: a node
function like `generate_answer` above returns `{"answer": response.content}`,
not a full `GraphState` dict with every field re-specified. LangGraph takes
that partial dict and merges it into the existing state, leaving fields the
node didn't touch (like `question`) untouched. The next module, State,
covers exactly how that merge behavior works and how to customize it for
fields — like a running list of messages — where "merge" should mean
"append" rather than "overwrite."

## A slightly larger example: two nodes in sequence

```python
def classify(state: GraphState) -> dict:
    return {"question_type": "factual"}  # imagine real classification logic here

def generate_answer(state: GraphState) -> dict:
    response = llm.invoke(f"Answer this {state['question_type']} question: {state['question']}")
    return {"answer": response.content}

graph_builder = StateGraph(GraphState)
graph_builder.add_node("classify", classify)
graph_builder.add_node("generate_answer", generate_answer)
graph_builder.set_entry_point("classify")
graph_builder.add_edge("classify", "generate_answer")
graph_builder.add_edge("generate_answer", END)
graph = graph_builder.compile()
```

Two nodes, one unconditional edge between them, and an edge to `END` — this
is structurally still a straight line (equivalent to an LCEL chain), which
is deliberate: starting simple before the Conditional Routing and Loops
modules introduce the branching and cycling that actually justify reaching
for a graph over a chain.
""",
                    "examples": [
                        {
                            "title": "Visualizing a compiled graph's structure",
                            "code": (
                                "print(graph.get_graph().draw_mermaid())\n"
                                "# Produces Mermaid diagram syntax you can render to see the graph's shape"
                            ),
                            "explanation": "Every compiled graph can render its own structure, which is a fast way to sanity-check that your edges wire up the way you intended.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a minimal StateGraph with a single node that takes a {name: str, greeting: str} state and fills in greeting, then compile and invoke it.",
                            "difficulty": "easy",
                            "hint": "Follow the generate_answer example, adapting the state fields.",
                        },
                        {
                            "prompt": "Extend your graph to two nodes in sequence: one that computes a value, and a second that uses it to produce a final field.",
                            "difficulty": "medium",
                            "hint": "Wire them with add_edge in order, and remember each node returns only the fields it changes.",
                        },
                        {
                            "prompt": "Deliberately have a node return an entire new state dict (overwriting fields it didn't intend to change) and observe what breaks compared to returning only a partial update.",
                            "difficulty": "medium",
                            "hint": "This demonstrates why returning partial updates, not full state, is the correct pattern.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: StateGraph API", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.4}],
                },
            ],
        },
        # 2. State
        {
            "slug": "state",
            "title": "State",
            "description": "Defining graph state precisely with TypedDict, and controlling how updates from different nodes merge using reducers.",
            "order_index": 2,
            "estimated_hours": 1.7,
            "lessons": [
                {
                    "slug": "defining-graph-state-with-typeddict",
                    "title": "Defining Graph State with TypedDict",
                    "description": "Designing a precise, typed state schema for a graph, building directly on the state-modeling discipline from Course 8.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Define a graph state schema with TypedDict, including optional and required fields",
                        "Use Annotated types to attach metadata to a state field",
                        "Apply the 'derive, don't duplicate' principle from Course 8 to graph state design",
                        "Recognize the connection between LangGraph state and the AgentState from Course 8",
                    ],
                    "content_markdown": """## Graph state is Course 8's AgentState, formalized

If you worked through Course 8's Agent State module, LangGraph's state
schema will feel immediately familiar — it's the same idea (explicit,
typed, inspectable data representing an in-flight task) with a real
execution engine built around it:

```python
from typing import TypedDict, Literal

class AgentState(TypedDict):
    goal: str
    plan: list[str]
    completed_steps: list[str]
    current_step: str | None
    status: Literal["planning", "acting", "done", "failed"]
```

This is nearly identical to the `AgentState` you designed in Course 8. The
difference isn't the schema design — it's that LangGraph now owns the
mechanics of reading and updating this state as execution moves between
nodes, instead of you writing that plumbing by hand.

## Required vs. optional fields

By default, every field in a `TypedDict` is required — a node returning a
partial update doesn't need to supply every field (LangGraph merges updates,
it doesn't require completeness), but the *initial* state you pass to
`.invoke()` does need every required field populated, or you'll get a type
error from your IDE (and potentially a runtime error) if a node tries to
read a field that was never set:

```python
class AgentState(TypedDict, total=False):
    goal: str            # still effectively required in practice if nodes depend on it
    error_message: str    # truly optional; only set if something goes wrong

# total=False makes all fields optional at the type level;
# combine with NotRequired[] on individual fields for finer control
from typing import NotRequired

class AgentState(TypedDict):
    goal: str                          # required
    error_message: NotRequired[str]     # optional
```

## Attaching metadata with Annotated

Some state fields need more than just a type — they need instructions for
*how* to merge updates from different nodes, which the next lesson covers
via reducers. The mechanism for attaching that instruction is `Annotated`:

```python
from typing import Annotated
import operator

class AgentState(TypedDict):
    goal: str
    tool_results: Annotated[list[str], operator.add]  # updates get appended, not overwritten
```

This single line is doing real work, and the next lesson unpacks exactly
what — for now, notice that the *type* (`list[str]`) and the *merge
behavior* (`operator.add`, meaning concatenate) are specified together, right
in the schema, rather than being implicit or scattered across your node
functions.

## Derive, don't duplicate — still applies

Course 8's discipline against redundant state fields (don't store both
`current_step` and a separately-tracked `step_index` that has to be kept in
sync by hand) applies just as much here. A graph state schema with
duplicated, derivable fields is exactly as prone to silent drift as a
hand-rolled one — LangGraph's merge mechanics don't protect you from a
poorly designed schema, they just execute whatever schema you give them
faithfully, bugs and all.
""",
                    "examples": [
                        {
                            "title": "A state schema mirroring Course 8's AgentState almost exactly",
                            "code": (
                                "class ResearchAgentState(TypedDict):\n"
                                "    goal: str\n"
                                "    plan: list[str]\n"
                                "    completed_steps: list[str]\n"
                                "    tool_results: Annotated[dict, lambda a, b: {**a, **b}]  # custom merge: shallow-merge dicts\n"
                                "    status: Literal[\"planning\", \"acting\", \"done\", \"failed\"]"
                            ),
                            "explanation": "The Annotated field customizes how concurrent or sequential updates to tool_results combine, rather than defaulting to a plain overwrite.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a TypedDict state schema for a graph-based customer support workflow, including at least one Annotated field with a merge behavior of your choosing.",
                            "difficulty": "medium",
                            "hint": "Consider a field like escalation_notes that should accumulate rather than overwrite.",
                        },
                        {
                            "prompt": "Take the hand-rolled AgentState TypedDict from Course 8's Agent State module and adapt it into a LangGraph-ready schema, identifying which fields need Annotated merge behavior.",
                            "difficulty": "medium",
                            "hint": "Fields like completed_steps or tool_results are good candidates for append/merge behavior.",
                        },
                        {
                            "prompt": "Identify a redundant, derivable field in a state schema of your choosing (similar to the step_index example) and explain how you'd compute it instead of storing it.",
                            "difficulty": "easy",
                            "hint": "Ask whether the field's value could always be recomputed from other fields already in state.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: State management", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#state", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}, {"slug": "langgraph", "weight": 0.6}],
                },
                {
                    "slug": "reducers-and-state-merging",
                    "title": "Reducers and State Merging",
                    "description": "Controlling exactly how updates from a node combine with existing state using reducer functions, and the built-in add_messages reducer.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain the default overwrite merge behavior for state fields",
                        "Write a custom reducer function for a field that needs append or merge semantics",
                        "Use the built-in add_messages reducer for conversation history fields",
                        "Reason about how reducers resolve concurrent updates from parallel nodes",
                    ],
                    "content_markdown": """## The default: last write wins

Without any annotation, LangGraph's default merge behavior for a state
field is simple overwrite — the most recent node to return a value for that
field replaces whatever was there before:

```python
class State(TypedDict):
    status: str  # default reducer: plain overwrite

# Node A returns {"status": "acting"} -> state["status"] becomes "acting"
# Node B later returns {"status": "done"} -> state["status"] becomes "done"
```

This is exactly right for fields like `status` that should genuinely
represent only the latest value. It is exactly wrong for fields that should
accumulate — a list of completed steps, a running set of tool results, a
message history — where overwriting would silently discard everything a
previous node contributed.

## Reducers: custom merge functions

A **reducer** is a two-argument function `(current_value, new_value) ->
merged_value` that LangGraph calls instead of overwriting, whenever a field
is annotated with one:

```python
from typing import Annotated
import operator

def append_unique(current: list[str], new: list[str]) -> list[str]:
    return current + [item for item in new if item not in current]

class State(TypedDict):
    completed_steps: Annotated[list[str], append_unique]
    tool_results: Annotated[list[str], operator.add]  # operator.add on lists = concatenation
```

`operator.add` is the standard library's function for `+`, and using it
directly as a reducer is a common, terse idiom for "just concatenate the
lists." The custom `append_unique` function shows that reducers can encode
real merge logic, not just simple concatenation — here, avoiding duplicate
entries.

## The built-in add_messages reducer

Conversation history is common enough that LangGraph ships a dedicated
reducer for it, `add_messages`, which does more than plain list
concatenation — it also handles updating an existing message in place by
matching message IDs, which matters once you start editing state
mid-execution (covered in the Human-in-the-Loop module later in this
course):

```python
from langgraph.graph.message import add_messages
from langchain_core.messages import AnyMessage

class ChatState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]
```

This single line is doing the same job as the `windowed_messages` and
`update_summary` functions you hand-built in Course 8's Short-Term Memory
module — accumulating conversational turns into state correctly across
multiple node executions — but with LangGraph handling the mechanics and
message-identity edge cases for you.

## Reducers and parallel execution

When a graph runs multiple nodes in parallel (covered more in later
modules) and both write to the same annotated field in the same step, the
reducer is what determines the combined result — this is precisely the race
condition Course 8's Agent State module warned about when discussing shared
mutable state, and reducers are LangGraph's structural answer to it: instead
of an unpredictable last-write-wins race, the reducer function deterministically
defines how concurrent contributions combine.

```python
# Two parallel nodes both write to tool_results in the same step
# node_a returns {"tool_results": ["result A"]}
# node_b returns {"tool_results": ["result B"]}
# with operator.add as the reducer, the merged result is deterministic:
# tool_results == ["result A", "result B"] (order depends on execution, but nothing is lost)
```
""",
                    "examples": [
                        {
                            "title": "Comparing default overwrite to an explicit reducer on the same shape of field",
                            "code": (
                                "class NoReducer(TypedDict):\n"
                                "    logs: list[str]  # each node's update REPLACES the whole list\n\n"
                                "class WithReducer(TypedDict):\n"
                                "    logs: Annotated[list[str], operator.add]  # each node's update EXTENDS the list"
                            ),
                            "explanation": "Identical field type, completely different behavior — the Annotated reducer is the only thing distinguishing 'replace' from 'accumulate'.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define a state field `errors: Annotated[list[str], operator.add]` and write two node functions that each append a different error string, then trace what the final list looks like after both run in sequence.",
                            "difficulty": "easy",
                            "hint": "Each node returns {'errors': ['its own error message']}; the reducer concatenates them.",
                        },
                        {
                            "prompt": "Write a custom reducer for a `metrics: dict` field that merges two dicts, summing values for keys that appear in both.",
                            "difficulty": "medium",
                            "hint": "Iterate over the union of both dicts' keys, adding values where a key exists in both.",
                        },
                        {
                            "prompt": "Explain, referencing Course 8's discussion of race conditions, why a reducer is a better solution than simply avoiding parallel writes to the same field altogether.",
                            "difficulty": "hard",
                            "hint": "Consider cases where parallel execution is genuinely necessary for performance, and a reducer gives you correctness without sacrificing that parallelism.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Reducers", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}, {"slug": "langgraph", "weight": 0.6}],
                },
            ],
        },
        # 3. Nodes
        {
            "slug": "nodes",
            "title": "Nodes",
            "description": "Writing the functions that do a graph's actual work, and using LangGraph's prebuilt nodes for common patterns like tool execution.",
            "order_index": 3,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "writing-node-functions",
                    "title": "Writing Node Functions",
                    "description": "The contract a node function fulfills, common patterns, and how nodes relate to the tools and chains built in Course 9.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Write a node function that reads state and returns a partial update",
                        "Call an LLM or an LCEL chain from inside a node",
                        "Access configuration passed at invocation time from within a node",
                        "Keep node functions focused on a single responsibility",
                    ],
                    "content_markdown": """## The node contract

A node is just a Python function (or any Runnable) with a specific shape:
it takes the current state as input and returns a dict of the fields it's
updating. That's the entire contract — everything else (what the node
actually does internally) is up to you.

```python
def summarize(state: State) -> dict:
    text = state["document_text"]
    response = llm.invoke(f"Summarize this in 2 sentences:\\n\\n{text}")
    return {"summary": response.content}
```

## Calling Course 9's chains from inside a node

Because a node function can contain arbitrary Python, an entire LCEL chain
from Course 9 can live inside a single node — a graph doesn't replace
chains, it orchestrates them:

```python
def answer_with_rag(state: State) -> dict:
    result = rag_chain.invoke(state["question"])  # the RAG chain built in Course 9
    return {"answer": result}
```

This is a genuinely important mental model: a LangGraph node is often *one
call* to a chain or agent you already know how to build, not a
fundamentally new kind of code. The graph's job is deciding *when* that
node runs and *what happens next* — the node itself can be as simple or as
sophisticated as the task requires.

## Accessing runtime configuration

Nodes can also read configuration passed at invocation time — useful for
things like a `session_id` or a feature flag that shouldn't live in the
graph's persisted state itself:

```python
from langgraph.graph import StateGraph
from langchain_core.runnables import RunnableConfig

def personalized_greeting(state: State, config: RunnableConfig) -> dict:
    user_id = config["configurable"].get("user_id", "unknown")
    return {"greeting": f"Welcome back, user {user_id}!"}

graph.invoke({"question": "..."}, config={"configurable": {"user_id": "u-42"}})
```

This mirrors the `session_id`-in-config pattern from Course 9's Memory
module — configuration that varies per call but shouldn't be part of the
durable, checkpointed state itself belongs in `config`, not in the state
schema.

## One responsibility per node

A node that does three unrelated things (call a tool, update three
unrelated state fields, and make a routing decision) is harder to test,
harder to reuse, and harder to reason about than three smaller nodes each
doing one of those things, wired together with edges. This is the same
single-responsibility instinct that makes any function easier to maintain,
and it pays off specifically in LangGraph because smaller nodes produce a
more legible graph structure — the graph's shape becomes a genuine map of
your application's logic, rather than a thin wrapper around a few
monolithic functions.

```python
# Prefer this:
graph_builder.add_node("call_tool", call_tool)
graph_builder.add_node("validate_result", validate_result)
graph_builder.add_node("update_summary", update_summary)

# Over a single node doing all three internally
```
""",
                    "examples": [
                        {
                            "title": "A node wrapping a tool call with error handling",
                            "code": (
                                "def search_node(state: State) -> dict:\n"
                                "    try:\n"
                                "        results = search_tool.invoke(state[\"query\"])\n"
                                "        return {\"search_results\": results, \"error\": None}\n"
                                "    except Exception as exc:\n"
                                "        return {\"search_results\": None, \"error\": str(exc)}"
                            ),
                            "explanation": "Error handling lives inside the node and surfaces as a state field, which a downstream conditional edge (covered in the next module) can then branch on.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a node function that takes a {topic: str} state and returns a {facts: list[str]} update by calling an LLM and parsing its response into a list.",
                            "difficulty": "easy",
                            "hint": "Keep the node focused on this one transformation only.",
                        },
                        {
                            "prompt": "Wrap an existing LCEL chain from Course 9 (e.g. a RAG chain) as a single LangGraph node, and add it to a minimal one-node graph.",
                            "difficulty": "medium",
                            "hint": "The node function's body can be a single line calling chain.invoke(...).",
                        },
                        {
                            "prompt": "Refactor a hypothetical node that both calls a tool AND makes a routing decision into two separate nodes with a clear division of responsibility.",
                            "difficulty": "medium",
                            "hint": "The routing decision likely belongs in a conditional edge, not inside the node itself.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Nodes", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#nodes", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
                {
                    "slug": "tool-nodes-and-prebuilt-components",
                    "title": "Tool Nodes and Prebuilt Components",
                    "description": "Using LangGraph's prebuilt ToolNode and create_react_agent instead of hand-writing common node patterns.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Use ToolNode to execute tool calls without hand-writing the execution loop",
                        "Wire a ToolNode into a graph alongside a model-calling node",
                        "Use create_react_agent as a prebuilt, complete tool-calling graph",
                        "Decide when to hand-roll nodes versus reach for a prebuilt component",
                    ],
                    "content_markdown": """## ToolNode: the tool-execution step, prebuilt

Course 9's manual tool-execution loop (bind tools, read `tool_calls`,
execute the matching function, wrap the result in a `ToolMessage`) is common
enough that LangGraph ships it as a ready-made node:

```python
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage
from typing import Annotated
from langgraph.graph.message import add_messages

class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

tools = [get_weather, get_stock_price]
tool_node = ToolNode(tools)

def call_model(state: State) -> dict:
    model_with_tools = llm.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

graph_builder = StateGraph(State)
graph_builder.add_node("call_model", call_model)
graph_builder.add_node("tools", tool_node)
graph_builder.set_entry_point("call_model")
```

`ToolNode` reads the most recent AI message's `tool_calls`, executes each
one against the tool list you gave it, and returns the resulting
`ToolMessage` objects as a state update — exactly the mechanics from Course
9's Tools module, now packaged as a single reusable node you wire in rather
than code you maintain yourself. Wiring the conditional edge that decides
*when* to route into `tools` versus finish is covered in the next module.

## create_react_agent: an entire tool-calling graph, prebuilt

For the common case of "a model that loops through tool calls until it
produces a final answer" — the exact pattern behind `AgentExecutor` in
Course 9 — LangGraph provides `create_react_agent`, which returns a fully
compiled graph, not just a node:

```python
from langgraph.prebuilt import create_react_agent

agent_graph = create_react_agent(llm, tools)
result = agent_graph.invoke({"messages": [("human", "What's AAPL trading at?")]})
print(result["messages"][-1].content)
```

Internally, this constructs essentially the `call_model` / `tools` graph
shown above, plus the conditional edge and loop wiring you'll build by hand
in the next two modules. It's the LangGraph-native equivalent of Course 9's
`create_tool_calling_agent` plus `AgentExecutor` — same underlying pattern,
graph-based implementation.

## When to hand-roll versus use a prebuilt

`create_react_agent` is an excellent default for a straightforward
tool-calling agent with no unusual control flow. Once you need something it
doesn't provide out of the box — custom routing logic, a verification gate
before certain tool calls (as in Course 8's Self-Correction module), human-
in-the-loop interrupts at specific points, or coordination between multiple
specialized sub-agents — you'll build the graph by hand using the nodes and
edges primitives from this and the following modules. Understanding what
`create_react_agent` constructs under the hood (which this lesson and the
next two modules are building toward) is exactly what lets you extend past
it confidently rather than treating it as an opaque black box.
""",
                    "examples": [
                        {
                            "title": "Inspecting what create_react_agent builds",
                            "code": (
                                "agent_graph = create_react_agent(llm, tools)\n"
                                "print(agent_graph.get_graph().draw_mermaid())\n"
                                "# Reveals the call_model / tools node structure and the conditional edge between them"
                            ),
                            "explanation": "Visualizing the prebuilt graph's structure demystifies it — it's built from the same primitives you're learning to use directly.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a graph with a call_model node and a ToolNode wired together (entry point at call_model, an edge from call_model to tools), using 2 tools of your choosing.",
                            "difficulty": "medium",
                            "hint": "You'll wire the conditional edge that decides whether to go to tools or END in the next module — for now, a simple unconditional edge is fine to confirm the nodes work.",
                        },
                        {
                            "prompt": "Use create_react_agent to build a complete tool-calling agent in 3 lines of code, and invoke it with a request that requires a tool call.",
                            "difficulty": "easy",
                            "hint": "Pass the messages in the {'messages': [(...)]} shape shown in the lesson.",
                        },
                        {
                            "prompt": "List two specific capabilities from Course 8 (e.g. a verification gate, a replan counter) that create_react_agent does NOT provide out of the box, and that you'd need to hand-build a custom graph for.",
                            "difficulty": "medium",
                            "hint": "Think about what's genuinely custom control flow versus the standard tool-call loop.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Prebuilt ReAct agent", "url": "https://langchain-ai.github.io/langgraph/reference/prebuilt/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
            ],
        },
        # 4. Edges
        {
            "slug": "edges",
            "title": "Edges",
            "description": "Wiring nodes together with unconditional edges, and the entry-point and compilation mechanics that turn a graph builder into an executable graph.",
            "order_index": 4,
            "estimated_hours": 1.4,
            "lessons": [
                {
                    "slug": "wiring-nodes-with-add-edge",
                    "title": "Wiring Nodes with add_edge",
                    "description": "The mechanics of unconditional edges, fan-out to parallel nodes, and fan-in patterns.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Wire a sequence of nodes with add_edge",
                        "Fan out from one node to multiple nodes that run in parallel",
                        "Fan in from multiple nodes into a single downstream node",
                        "Explain how parallel branches and reducers interact",
                    ],
                    "content_markdown": """## The simplest edge: a fixed next step

`add_edge(source, target)` declares an unconditional transition: whenever
`source` finishes, `target` runs next, unconditionally. Chaining several of
these produces a straight-line graph, structurally equivalent to an LCEL
chain:

```python
graph_builder.add_edge("load_data", "clean_data")
graph_builder.add_edge("clean_data", "analyze")
graph_builder.add_edge("analyze", END)
```

## Fan-out: one node triggers several in parallel

Adding more than one edge *from* the same source node causes all of those
targets to run in parallel once the source completes:

```python
graph_builder.add_edge("fetch_document", "extract_entities")
graph_builder.add_edge("fetch_document", "extract_summary")
graph_builder.add_edge("fetch_document", "extract_sentiment")
```

`extract_entities`, `extract_summary`, and `extract_sentiment` all run
concurrently once `fetch_document` finishes, rather than one after another —
a direct performance win for independent pieces of work that don't depend
on each other's output. This is exactly where the previous module's
discussion of reducers becomes practically important: if two of these
parallel nodes write to the same state field, the reducer (not the graph
structure) determines how those concurrent updates combine.

## Fan-in: converging back to a single node

The mirror image — multiple edges *into* the same target — makes that node
wait until all of its incoming branches have completed before it runs:

```python
graph_builder.add_node("combine_results", combine_results)
graph_builder.add_edge("extract_entities", "combine_results")
graph_builder.add_edge("extract_summary", "combine_results")
graph_builder.add_edge("extract_sentiment", "combine_results")
```

`combine_results` only executes once all three extraction nodes have
finished, and by that point, state contains the merged results of all three
(again, governed by each field's reducer) — a clean map-reduce shape
expressed directly as graph structure.

## Entry points and compilation, revisited

`set_entry_point("load_data")` (or the newer `add_edge(START, "load_data")`
form, using LangGraph's `START` marker the same way `END` marks
termination) declares where execution begins:

```python
from langgraph.graph import StateGraph, START, END

graph_builder.add_edge(START, "load_data")
graph_builder.add_edge("load_data", "clean_data")
graph_builder.add_edge("clean_data", END)
```

Using `START` and `END` as explicit nodes in every edge (rather than the
separate `set_entry_point` call) is the more current, more consistent style
— everything, including the graph's beginning and end, is expressed as an
edge in the same list, making the full control-flow graph readable in one
place rather than split between `add_edge` calls and a separate entry-point
declaration.

`.compile()` validates the graph you've built — every node referenced by an
edge must actually exist, every node (except ones with edges to `END`) must
have an outgoing edge, or compilation fails with a clear error rather than
letting a malformed graph run and fail unpredictably partway through
execution.
""",
                    "examples": [
                        {
                            "title": "A complete fan-out/fan-in graph",
                            "code": (
                                "graph_builder = StateGraph(State)\n"
                                "for name, fn in [(\"fetch\", fetch_document), (\"entities\", extract_entities),\n"
                                "                 (\"summary\", extract_summary), (\"combine\", combine_results)]:\n"
                                "    graph_builder.add_node(name, fn)\n\n"
                                "graph_builder.add_edge(START, \"fetch\")\n"
                                "graph_builder.add_edge(\"fetch\", \"entities\")\n"
                                "graph_builder.add_edge(\"fetch\", \"summary\")\n"
                                "graph_builder.add_edge(\"entities\", \"combine\")\n"
                                "graph_builder.add_edge(\"summary\", \"combine\")\n"
                                "graph_builder.add_edge(\"combine\", END)\n"
                                "graph = graph_builder.compile()"
                            ),
                            "explanation": "fetch fans out to two parallel branches, which both fan back in to combine before the graph ends.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build a 4-node graph with a fan-out from one node to two parallel nodes, and a fan-in from both back into a final node before END.",
                            "difficulty": "medium",
                            "hint": "Follow the fetch/entities/summary/combine shape from the lesson's example.",
                        },
                        {
                            "prompt": "Add a state field with an operator.add reducer that both parallel branches in your graph write to, and verify after running that both contributions appear in the final merged list.",
                            "difficulty": "medium",
                            "hint": "Each parallel node should return a single-item list for this field.",
                        },
                        {
                            "prompt": "Explain what would happen, at compile time, if you forgot to wire an outgoing edge from one of your non-terminal nodes.",
                            "difficulty": "easy",
                            "hint": "Try it and read the compilation error message.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Edges", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#edges", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
                {
                    "slug": "entry-points-and-graph-compilation",
                    "title": "Entry Points and Graph Compilation",
                    "description": "A closer look at what compilation validates and produces, and how a compiled graph behaves as a Runnable.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what .compile() validates before producing a runnable graph",
                        "Pass configuration like a checkpointer at compile time",
                        "Treat a compiled graph as a Runnable, consistent with Course 9's abstractions",
                        "Recognize common compile-time errors and what they indicate",
                    ],
                    "content_markdown": """## Compilation as a validation gate

`.compile()` isn't just a formality — it's where LangGraph checks that the
graph you've described is actually well-formed: every node referenced by an
edge exists, there's a path from `START`, nodes have a way to eventually
reach `END` (directly or through the branches you've wired). Catching these
issues at compile time, rather than at some arbitrary point during
execution, is a deliberate design choice — it's far easier to fix a
malformed graph before you've invoked it than to debug why execution got
stuck partway through a run.

```python
graph_builder = StateGraph(State)
graph_builder.add_node("a", node_a)
graph_builder.add_edge(START, "a")
# forgot: graph_builder.add_edge("a", END)
graph = graph_builder.compile()  # raises an error: node 'a' has no outgoing edge
```

## Compile-time configuration

Compilation is also where you attach cross-cutting configuration that
applies to every run of the graph — most importantly, the checkpointer
you'll use starting in the Checkpoints module:

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
```

Passing a checkpointer at compile time (rather than at invoke time) reflects
that checkpointing is a structural property of how this graph runs, not a
per-call option — every invocation of this compiled graph will be
checkpointed, which is exactly the behavior you want for a graph you intend
to make resumable or persistent.

## A compiled graph is a Runnable

Consistent with everything in Course 9, a compiled `StateGraph` implements
the same Runnable interface as a chain: `.invoke()`, `.batch()`, `.stream()`
all work exactly as you'd expect, and a compiled graph can even be used as a
node inside a *larger* graph — the same composability principle from LCEL,
now one level up. This is what makes the Multi-Agent Workflows module later
in this course possible: a specialized sub-agent is often just another
compiled graph, nested as a node inside a supervisor graph.

```python
def sub_agent_node(state: ParentState) -> dict:
    result = compiled_sub_graph.invoke({"messages": state["messages"]})
    return {"sub_agent_output": result["messages"][-1].content}
```

## Reading compile-time errors

A "node X has no outgoing edge" error means you've built a dead end. A
"node X referenced in an edge but never added" error means a typo or a
missing `add_node` call. Both are examples of the same underlying value
compilation provides: structural mistakes in your graph's shape surface
immediately and specifically, rather than manifesting later as a confusing
runtime hang or an incomplete state update that's much harder to trace back
to its actual cause.
""",
                    "examples": [
                        {
                            "title": "Attaching a checkpointer at compile time",
                            "code": (
                                "from langgraph.checkpoint.memory import MemorySaver\n\n"
                                "checkpointer = MemorySaver()\n"
                                "graph = graph_builder.compile(checkpointer=checkpointer)\n"
                                "# every .invoke() on `graph` from here on is automatically checkpointed"
                            ),
                            "explanation": "The checkpointer is graph-level configuration, set once at compile time, not something you pass on every individual invocation.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Deliberately reference a node name in add_edge that was never registered with add_node, attempt to compile, and read the resulting error message.",
                            "difficulty": "easy",
                            "hint": "This is a fast way to build intuition for what compile-time errors look like and mean.",
                        },
                        {
                            "prompt": "Nest a small, previously compiled graph as a node inside a new, larger graph, and invoke the larger graph end to end.",
                            "difficulty": "hard",
                            "hint": "The node function's body just needs to call the inner compiled graph's .invoke() and translate the result into the outer state's shape.",
                        },
                        {
                            "prompt": "Explain why catching a malformed graph at compile time is preferable to discovering the same problem only when a specific execution path happens to hit the dead end at runtime.",
                            "difficulty": "medium",
                            "hint": "Consider a dead-end node that's only reached by a rare conditional branch.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Graphs", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
            ],
        },
        # 5. Conditional Routing
        {
            "slug": "conditional-routing",
            "title": "Conditional Routing",
            "description": "Branching a graph's execution based on the current state, and building a full router node for multi-path workflows.",
            "order_index": 5,
            "estimated_hours": 1.6,
            "lessons": [
                {
                    "slug": "conditional-edges-and-routing-functions",
                    "title": "Conditional Edges and Routing Functions",
                    "description": "Using add_conditional_edges to select the next node dynamically based on a routing function's output.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Write a routing function that inspects state and returns a branch label",
                        "Wire a conditional edge with add_conditional_edges",
                        "Include an explicit default/fallback branch",
                        "Distinguish a conditional edge from a node that happens to change behavior internally",
                    ],
                    "content_markdown": """## A conditional edge is a function, not a fixed target

`add_conditional_edges` wires a *function* — not a fixed next node — as the
thing that decides where execution goes after a given node finishes. The
function reads the current state and returns a label; a mapping from labels
to node names determines the actual next node:

```python
def route_by_length(state: State) -> str:
    if len(state["document_text"]) > 5000:
        return "detailed_summary"
    return "quick_summary"

graph_builder.add_conditional_edges(
    "load_document",
    route_by_length,
    {"detailed_summary": "detailed_summary", "quick_summary": "quick_summary"},
)
```

This is the direct graph-native expression of Course 8's Routing module —
`route_by_length` here plays exactly the role `classify_intent` and
`route()` played in that course's hand-rolled dispatch logic, except the
branching is now declared structure the compiled graph itself understands
and can validate, rather than an if/else buried inside a Python function.

## Always include an explicit default

A routing function that returns a label not present in the mapping causes a
runtime error — the graph has no idea where to go. Just as Course 8's
Routing module insisted on an explicit fallback for unrecognized intents,
a conditional edge's routing function should guard against unexpected
values defensively:

```python
def route_by_intent(state: State) -> str:
    intent = state.get("intent", "task")
    valid_intents = {"lookup", "task", "complaint"}
    return intent if intent in valid_intents else "task"  # explicit, safe default
```

## Conditional edges vs. a node with internal branching

It's tempting to skip the conditional edge and just have a node internally
call different logic based on state — but this hides the branching from the
graph's own structure, meaning you lose the ability to visualize it, and
LangGraph can no longer reason about which paths are reachable. Reserve
internal branching inside a node for minor implementation details; use a
conditional edge whenever the branch represents a genuinely different *path*
through the workflow — different downstream nodes, not just a different
formula inside the same node.

```python
# Prefer: the branch is visible graph structure
graph_builder.add_conditional_edges("classify", route_by_intent,
    {"lookup": "handle_lookup", "task": "handle_task", "complaint": "handle_complaint"})

# Over: the branch is hidden inside one big node
def classify_and_handle(state):
    intent = classify(state)
    if intent == "lookup": ...
    elif intent == "task": ...
    # graph structure shows nothing about this branching
```

## Routing to END conditionally

A conditional edge's mapping can include `END` directly as a target,
letting a routing function decide the workflow is complete rather than
looping or continuing:

```python
def check_if_done(state: State) -> str:
    return "END" if state["status"] == "done" else "continue"

graph_builder.add_conditional_edges("agent_step", check_if_done, {"END": END, "continue": "agent_step"})
```

This exact pattern — conditionally routing back to the same node versus
exiting — is the mechanism the Loops module, next, builds directly on top
of.
""",
                    "examples": [
                        {
                            "title": "A routing function mirroring Course 8's classify_intent",
                            "code": (
                                "def route_request(state: State) -> str:\n"
                                "    intent = state[\"intent\"]  # set by an earlier classification node\n"
                                "    return intent if intent in {\"lookup\", \"task\", \"complaint\"} else \"task\"\n\n"
                                "graph_builder.add_conditional_edges(\n"
                                "    \"classify\", route_request,\n"
                                "    {\"lookup\": \"handle_lookup\", \"task\": \"handle_task\", \"complaint\": \"handle_complaint\"},\n"
                                ")"
                            ),
                            "explanation": "The routing function and the fallback default here are structurally identical to the dispatch logic from Course 8's Routing module.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a conditional edge to a graph that routes to one of two nodes based on a boolean state field, and test both branches by invoking with each value.",
                            "difficulty": "easy",
                            "hint": "The routing function just needs to return one of two labels based on the field's value.",
                        },
                        {
                            "prompt": "Add a third branch and an explicit default case to your routing function from the previous exercise, so an unexpected field value doesn't cause a runtime error.",
                            "difficulty": "medium",
                            "hint": "Mirror the safe-default pattern from the lesson.",
                        },
                        {
                            "prompt": "Refactor a node that internally branches into two very different code paths into a conditional edge plus two separate nodes, and explain what became visible in the graph's structure as a result.",
                            "difficulty": "medium",
                            "hint": "Draw the mermaid diagram before and after to see the difference.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Conditional edges", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.3}],
                },
                {
                    "slug": "building-a-router-node-for-multi-path-workflows",
                    "title": "Building a Router Node for Multi-Path Workflows",
                    "description": "Combining a classification node with conditional edges to build a complete router for a multi-intent agent workflow.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Separate a classification node from its routing decision",
                        "Build a complete router: classify, then conditionally dispatch",
                        "Design deterministic pre-checks before an LLM-based classification node",
                        "Extend a router with a new branch without disturbing existing ones",
                    ],
                    "content_markdown": """## Two pieces: classify, then route

A robust router in LangGraph is usually two separate things working
together: a **node** that determines the intent (writing it into state) and
a **conditional edge** that reads that field and dispatches accordingly.
Keeping these separate — rather than doing classification and dispatch in
one step — makes the classification logic independently testable and the
routing structure visible in the graph.

```python
class State(TypedDict):
    request: str
    intent: str

def classify(state: State) -> dict:
    intent = classify_intent(state["request"], llm)  # from Course 8's Routing module
    return {"intent": intent}

def route(state: State) -> str:
    return state["intent"] if state["intent"] in HANDLERS else "task"

graph_builder = StateGraph(State)
graph_builder.add_node("classify", classify)
graph_builder.add_node("handle_lookup", handle_lookup_node)
graph_builder.add_node("handle_task", handle_task_node)
graph_builder.add_node("handle_complaint", handle_complaint_node)

graph_builder.add_edge(START, "classify")
graph_builder.add_conditional_edges("classify", route, {
    "lookup": "handle_lookup", "task": "handle_task", "complaint": "handle_complaint",
})
for handler in ("handle_lookup", "handle_task", "handle_complaint"):
    graph_builder.add_edge(handler, END)
```

## Deterministic pre-checks before the LLM classifier

Course 8 argued for a tiered approach: cheap, deterministic checks first,
LLM classification only as a fallback. In a graph, this becomes its own
conditional edge, checked *before* the LLM-based classify node even runs:

```python
def deterministic_route(state: State) -> str:
    if state["request"].startswith("/"):
        return "command"
    if any(kw in state["request"].lower() for kw in ("refund", "broken")):
        return "complaint"
    return "needs_llm_classification"

graph_builder.add_conditional_edges(START, deterministic_route, {
    "command": "handle_command",
    "complaint": "handle_complaint",
    "needs_llm_classification": "classify",  # only ambiguous requests reach the LLM node
})
```

This shape — a fast deterministic router at the graph's entry, falling
through to a slower LLM-based one only when needed — keeps the common,
cheap cases cheap while the graph's structure makes that tiering explicit
and inspectable, rather than buried in a single function's control flow.

## Extending the router without disturbing existing branches

Adding a new intent to this router is additive: register a new handler
node, add one more entry to the routing dict, wire its edge to `END` (or
wherever it should go next). None of the existing branches need to change,
which is a direct structural benefit over a large if/elif chain, where
adding a new case means editing a function that every other case also lives
inside of, with more opportunity to introduce a regression.

```python
graph_builder.add_node("handle_billing", handle_billing_node)
graph_builder.add_edge("handle_billing", END)
# update only the conditional edges mapping to add "billing": "handle_billing"
```
""",
                    "examples": [
                        {
                            "title": "Visualizing the two-tier router",
                            "code": (
                                "graph = graph_builder.compile()\n"
                                "print(graph.get_graph().draw_mermaid())\n"
                                "# Shows the deterministic pre-check branching directly from START,\n"
                                "# with only the ambiguous path flowing into the LLM-based classify node"
                            ),
                            "explanation": "The rendered graph makes the tiered routing strategy visually obvious, which is a genuine debugging and communication advantage over equivalent nested Python conditionals.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build the full classify-then-route graph from the lesson with 3 intent branches, and invoke it with a request for each branch to confirm correct dispatch.",
                            "difficulty": "medium",
                            "hint": "Follow the State/classify/route structure shown in the lesson closely.",
                        },
                        {
                            "prompt": "Add a deterministic pre-check conditional edge at START that bypasses the LLM classify node for command-prefixed requests (e.g. starting with '/').",
                            "difficulty": "medium",
                            "hint": "Wire this as a separate conditional edge from START, feeding into classify only for the fallback case.",
                        },
                        {
                            "prompt": "Add a fourth intent branch to your router (a new handler node and routing entry) without modifying any of the existing three handler nodes.",
                            "difficulty": "easy",
                            "hint": "This should only require adding a node, an edge to END, and one dict entry.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph conceptual guide: routing", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.3}],
                },
            ],
        },
        # 6. Loops
        {
            "slug": "loops",
            "title": "Loops",
            "description": "Building cyclical graphs for agent loops, with explicit exit conditions and recursion limits to keep them bounded.",
            "order_index": 6,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "cycles-in-langgraph-agent-loops",
                    "title": "Cycles in LangGraph: Agent Loops",
                    "description": "Building the classic tool-calling agent loop as a graph cycle, using a conditional edge to decide whether to loop or exit.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Build a graph with a cycle between a model-calling node and a tool node",
                        "Write the conditional edge that decides whether to continue looping or exit",
                        "Explain how this graph shape maps to Course 8's and Course 9's tool-calling loops",
                        "Trace a multi-iteration execution through the graph's state changes",
                    ],
                    "content_markdown": """## An edge pointing backward is a loop

Everything covered so far in this course — nodes, edges, conditional
routing — composes into the one graph shape that most directly justifies
choosing a graph over a chain in the first place: a **cycle**, where a
conditional edge can route back to a node that already ran. This is the
graph-native version of the observe-decide-act loop from Course 8's
Tool-Using Agents module, and the underlying mechanics of Course 9's
`AgentExecutor`, now expressed as explicit, visible structure.

```python
from langgraph.graph.message import add_messages
from typing import Annotated

class State(TypedDict):
    messages: Annotated[list, add_messages]

def call_model(state: State) -> dict:
    model_with_tools = llm.bind_tools(tools)
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: State) -> str:
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else "end"

graph_builder = StateGraph(State)
graph_builder.add_node("call_model", call_model)
graph_builder.add_node("tools", ToolNode(tools))

graph_builder.add_edge(START, "call_model")
graph_builder.add_conditional_edges("call_model", should_continue, {"tools": "tools", "end": END})
graph_builder.add_edge("tools", "call_model")  # <- the edge that creates the cycle

graph = graph_builder.compile()
```

## Tracing an execution

Walk through what happens on a request that needs one tool call: `call_model`
runs, the model requests a tool call, `should_continue` routes to `tools`,
`ToolNode` executes it and appends a `ToolMessage`, the unconditional edge
`tools -> call_model` sends execution back to `call_model`, which now sees
the tool's result in `messages` and (this time) responds with a final
answer instead of another tool call, so `should_continue` routes to `end`.

This is precisely the `tool_loop` function from Course 8, and precisely
what `AgentExecutor` does internally in Course 9 — the difference here is
that the loop is declared graph structure: `should_continue` and the
`tools -> call_model` edge together *are* the loop, rather than a `while`
statement in a Python function.

## Why express it this way instead of a while loop

The graph version buys you everything the rest of this course builds on top
of: every iteration through the cycle is a checkpointable, inspectable step
(next module), the loop can be paused for human review at a specific point
(Human-in-the-Loop module), and the cycle can be one node inside a *larger*
graph that does routing, verification, or multi-agent coordination around
it. A plain `while` loop in a function gives you none of that for free —
you'd have to build each capability by hand, which is exactly what Course 8
had you do, and exactly what LangGraph now provides as reusable
infrastructure.
""",
                    "examples": [
                        {
                            "title": "Running the loop and inspecting the full message trace afterward",
                            "code": (
                                "result = graph.invoke({\"messages\": [(\"human\", \"What's AAPL trading at, and what's the weather in Austin?\")]})\n"
                                "for m in result[\"messages\"]:\n"
                                "    print(m.type, \":\", getattr(m, \"content\", m.tool_calls))"
                            ),
                            "explanation": "The full messages list shows every cycle the graph took: the model's tool requests, each ToolMessage response, and the final answer, in order.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build the call_model / tools cycle from the lesson with a single tool, and invoke it with a request that requires exactly one tool call. Confirm the graph correctly exits after the tool result comes back.",
                            "difficulty": "medium",
                            "hint": "Follow the State/call_model/should_continue/ToolNode structure exactly as shown.",
                        },
                        {
                            "prompt": "Invoke your graph with a request that needs two sequential tool calls (where the second depends on the first's result) and trace the messages list to confirm two full cycles occurred.",
                            "difficulty": "medium",
                            "hint": "Print result['messages'] and count the AIMessage/ToolMessage pairs.",
                        },
                        {
                            "prompt": "Explain, in your own words, which specific line of code creates the cycle in this graph, and what would happen structurally if it were removed.",
                            "difficulty": "easy",
                            "hint": "It's the add_edge('tools', 'call_model') line — without it, the graph could still execute one tool call but couldn't loop back to consider the result.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Prebuilt ReAct agent", "url": "https://langchain-ai.github.io/langgraph/reference/prebuilt/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
                {
                    "slug": "setting-recursion-limits-and-exit-conditions",
                    "title": "Setting Recursion Limits and Exit Conditions",
                    "description": "Bounding graph cycles with recursion_limit, and designing exit conditions that fail informatively rather than looping forever.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Configure recursion_limit to bound a graph's total steps",
                        "Handle GraphRecursionError gracefully instead of letting it propagate as a crash",
                        "Design an explicit iteration counter in state as a complementary safeguard",
                        "Connect recursion limits to the bounded-retry discipline from Course 8",
                    ],
                    "content_markdown": """## The same runaway-loop risk, a built-in safeguard

Course 8 was emphatic about bounding every loop — tool-calling iterations,
replanning attempts, handoffs between sub-agents — because an unbounded loop
is a real, not hypothetical, failure mode once a model gets into an
unproductive pattern. LangGraph provides this safeguard at the framework
level: `recursion_limit` caps the total number of steps (node executions,
including all iterations of a cycle) a single graph invocation can take.

```python
result = graph.invoke(
    {"messages": [("human", "help me with a very open-ended request")]},
    config={"recursion_limit": 25},
)
```

If the graph exceeds this limit before reaching `END`, LangGraph raises a
`GraphRecursionError` rather than looping indefinitely — the graph-native
equivalent of the `max_iters` bound from Course 8's Tool-Using Agents
module, enforced by the framework instead of a hand-written counter.

## Handling the limit gracefully

An uncaught `GraphRecursionError` crashes your application — exactly the
"unhandled exception in a long-running loop" problem Course 8's Error
Handling module warned about. Catch it and respond the way that module
recommended: log the technical detail, surface something actionable to the
user.

```python
from langgraph.errors import GraphRecursionError

try:
    result = graph.invoke(initial_state, config={"recursion_limit": 25})
except GraphRecursionError:
    logger.warning("graph exceeded recursion limit", extra={"initial_state": initial_state})
    result = {"messages": [("ai", "This request needs more steps than I'm able to take right now. Could you break it into smaller parts?")]}
```

## An explicit counter as a complementary safeguard

`recursion_limit` bounds the *entire graph's* total steps, which is coarser
than a bound on a *specific* cycle. For finer control — say, capping just
the tool-calling loop at 5 iterations while leaving room for other parts of
a larger graph — track an explicit counter in state, exactly as Course 8's
Planning module did for its `replan_count`:

```python
class State(TypedDict):
    messages: Annotated[list, add_messages]
    tool_call_count: int

def call_model(state: State) -> dict:
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response], "tool_call_count": state.get("tool_call_count", 0) + 1}

def should_continue(state: State) -> str:
    if state.get("tool_call_count", 0) >= 5:
        return "end"  # explicit, in-domain limit, independent of the graph-wide recursion_limit
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else "end"
```

## Two layers, deliberately

`recursion_limit` is your backstop against a graph-wide runaway (useful
across every graph you build, requiring no extra state design); an explicit
counter is a targeted, in-domain limit that can carry more specific meaning
("stop after 5 tool calls" versus "stop after 25 total graph steps of any
kind") and can trigger different, more informative handling — a distinct
message, a fallback strategy, a handoff to a human — rather than a generic
recursion error. Production graphs generally want both, the same way Course
8 combined retries with circuit breaking rather than relying on just one
mechanism.
""",
                    "examples": [
                        {
                            "title": "Setting a conservative default recursion limit application-wide",
                            "code": (
                                "DEFAULT_CONFIG = {\"recursion_limit\": 20}\n\n"
                                "def run_agent(initial_state):\n"
                                "    try:\n"
                                "        return graph.invoke(initial_state, config=DEFAULT_CONFIG)\n"
                                "    except GraphRecursionError:\n"
                                "        return {\"messages\": [(\"ai\", \"I wasn't able to finish this within my step budget.\")]}"
                            ),
                            "explanation": "Wrapping every graph invocation with the same default config and catch block centralizes this safeguard rather than repeating it at every call site.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Set recursion_limit=5 on a graph whose loop would normally take more than 5 steps to resolve a given request, and observe the GraphRecursionError.",
                            "difficulty": "easy",
                            "hint": "Choose a request you know requires several tool-call cycles.",
                        },
                        {
                            "prompt": "Wrap a graph invocation in a try/except for GraphRecursionError that logs the failure and returns a user-facing fallback message instead of crashing.",
                            "difficulty": "medium",
                            "hint": "Follow the run_agent pattern from the lesson's example.",
                        },
                        {
                            "prompt": "Add an explicit tool_call_count field to a graph's state, incrementing it in call_model, and use it in should_continue to cap tool calls at 3 independent of the graph-wide recursion_limit.",
                            "difficulty": "medium",
                            "hint": "This mirrors the replan_count pattern from Course 8's Planning module.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Recursion limit", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#recursion-limit", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
            ],
        },
        # 7. Checkpoints
        {
            "slug": "checkpoints",
            "title": "Checkpoints",
            "description": "Saving graph state after every step with a checkpointer, and using that saved history to inspect or replay execution.",
            "order_index": 7,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "checkpointing-with-memorysaver",
                    "title": "Checkpointing with MemorySaver",
                    "description": "Attaching a checkpointer to a graph so every step's state is saved, and understanding what that unlocks.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Attach a MemorySaver checkpointer to a compiled graph",
                        "Explain what a thread_id is and why it's required with a checkpointer",
                        "Resume a conversation across multiple .invoke() calls using the same thread_id",
                        "Connect checkpointing to the state-persistence concepts from Course 8",
                    ],
                    "content_markdown": """## Checkpointing: state, saved automatically, at every step

Course 8's Agent State module had you hand-write `save_state` and
`load_state` functions to persist an agent's progress. LangGraph automates
this entirely with a **checkpointer**: attach one at compile time, and the
graph's state is saved after every single node execution, with zero extra
code in your nodes.

```python
from langgraph.checkpoint.memory import MemorySaver

checkpointer = MemorySaver()
graph = graph_builder.compile(checkpointer=checkpointer)
```

`MemorySaver` keeps checkpoints in process memory — the checkpointing
equivalent of `InMemoryChatMessageHistory` from Course 9's Memory module:
perfect for development and testing, not durable across a process restart
(the next module, Persistence, covers the production-grade alternative).

## thread_id: identifying which conversation you're resuming

A checkpointer needs to know *which* saved state to load or continue —
exactly the `session_id` concept from Course 9's memory chains, here called
`thread_id`:

```python
config = {"configurable": {"thread_id": "conversation-1"}}

result1 = graph.invoke({"messages": [("human", "My name is Priya.")]}, config=config)
result2 = graph.invoke({"messages": [("human", "What's my name?")]}, config=config)
print(result2["messages"][-1].content)  # correctly recalls "Priya"
```

Because both calls share the same `thread_id`, the second `.invoke()`
automatically loads the state saved after the first call and continues from
there — you never manually pass the prior message history yourself, unlike
the raw `messages` list management from earlier courses. The checkpointer
handles it.

## What checkpointing unlocks beyond memory

Persisting state after every node isn't only about conversational memory —
it's the foundation for three capabilities the rest of this course builds
on: **resumability** (a crashed or interrupted run can pick back up from its
last checkpoint instead of restarting from scratch), **time travel**
(inspecting or even replaying execution from any earlier checkpoint, covered
in the next lesson), and **human-in-the-loop interrupts** (pausing a graph
mid-execution at a specific point and resuming later, once a human has acted
— covered in a dedicated module later in this course). None of these are
separate systems bolted on — they're all direct consequences of the graph
saving its state at every step by default.

## Inspecting saved state directly

```python
state_snapshot = graph.get_state(config)
print(state_snapshot.values)   # the current state dict
print(state_snapshot.next)      # which node(s) would run next
```

`get_state` gives you the same kind of inspectable, structured view of an
agent's progress that Course 8 argued explicit state modeling should
provide — except now it's a framework guarantee rather than something you
had to design and maintain yourself.
""",
                    "examples": [
                        {
                            "title": "Two separate threads staying isolated, exactly like Course 9's session_id",
                            "code": (
                                "graph.invoke({\"messages\": [(\"human\", \"I like tea.\")]}, config={\"configurable\": {\"thread_id\": \"alice\"}})\n"
                                "graph.invoke({\"messages\": [(\"human\", \"I like coffee.\")]}, config={\"configurable\": {\"thread_id\": \"bob\"}})\n\n"
                                "r = graph.invoke({\"messages\": [(\"human\", \"What do I like?\")]}, config={\"configurable\": {\"thread_id\": \"alice\"}})\n"
                                "print(r[\"messages\"][-1].content)  # recalls tea, not coffee"
                            ),
                            "explanation": "thread_id-based isolation works identically to session_id-based isolation from Course 9 — different keys, same underlying principle.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Attach a MemorySaver checkpointer to a graph with a messages state field, and confirm it correctly recalls information across two separate .invoke() calls sharing the same thread_id.",
                            "difficulty": "medium",
                            "hint": "Follow the conversation-1 example from the lesson closely.",
                        },
                        {
                            "prompt": "Run the same graph with two different thread_id values and confirm their states remain isolated from each other.",
                            "difficulty": "easy",
                            "hint": "State a distinct fact in each thread and ask the graph to recall it in the other thread.",
                        },
                        {
                            "prompt": "Use graph.get_state(config) after an invocation and print both .values and .next, explaining what each tells you about the graph's current status.",
                            "difficulty": "medium",
                            "hint": ".next tells you which node(s) would run if you invoked again; it's empty once the graph has reached END.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Persistence", "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.4}],
                },
                {
                    "slug": "time-travel-and-replaying-state",
                    "title": "Time Travel and Replaying State",
                    "description": "Inspecting a graph's full checkpoint history, replaying execution from an earlier point, and forking alternate branches.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "List a thread's full checkpoint history with get_state_history",
                        "Resume execution from a specific earlier checkpoint",
                        "Explain a practical debugging use case for replaying from an earlier state",
                        "Distinguish replay from simply re-invoking the graph from scratch",
                    ],
                    "content_markdown": """## Every step, individually addressable

Because a checkpointer saves state after *every* node execution, not just at
the end, a thread's full history is a sequence of checkpoints you can list,
inspect, and — critically — resume execution from any point in:

```python
history = list(graph.get_state_history(config))
for snapshot in history:
    print(snapshot.config["configurable"]["checkpoint_id"], "->", snapshot.values.get("status"))
```

This is the direct, practical realization of the "immutable state updates"
idea from Course 8's Agent State module — recall that lesson noted
copy-on-write state updates preserve a full history of every state the
agent passed through, which is "exactly the property that frameworks like
LangGraph rely on for checkpointing and replay." This is that property, now
concretely usable.

## Replaying from an earlier checkpoint

To resume execution from a specific earlier point — rather than the most
recent checkpoint — pass that checkpoint's ID explicitly in the config:

```python
earlier_checkpoint_id = history[3].config["configurable"]["checkpoint_id"]
replay_config = {"configurable": {"thread_id": "conversation-1", "checkpoint_id": earlier_checkpoint_id}}

result = graph.invoke(None, config=replay_config)  # continues from that earlier state
```

Passing `None` as the input tells LangGraph "don't add new input, just
continue executing from here" — useful when you want to see how the graph
behaves from a known-good earlier state, without re-supplying the original
request.

## A concrete debugging use case

Imagine a multi-step agent run that ultimately produced a wrong answer.
Rather than guessing which step went wrong from the final output alone
(exactly the problem Course 8's Error Handling module raised about opaque
failures), you can walk the checkpoint history, inspect the state at each
step, find the exact point where something went sideways — a tool returned
unexpected data, a routing decision picked the wrong branch — and even
replay from just before that point with a fix in place, without re-running
every step that was already correct.

```python
for snapshot in history:
    if snapshot.values.get("error"):
        print("First error appeared after:", snapshot.config["configurable"]["checkpoint_id"])
        break
```

## Replay vs. starting over

Re-invoking a graph from scratch discards everything it had already
computed and re-runs the entire workflow from the beginning — wasteful if
most of the run was correct, and it loses the specific state that led to the
interesting behavior in the first place. Replaying from a checkpoint
resumes *exactly* where that checkpoint left off, with the full state as it
existed at that moment, which is both cheaper and far more useful for
targeted debugging or for correcting a single step without redoing
everything before it — a capability with no equivalent in a plain, uncheckpointed
Python loop.
""",
                    "examples": [
                        {
                            "title": "Finding and replaying from the checkpoint right before a tool failure",
                            "code": (
                                "history = list(graph.get_state_history(config))\n"
                                "for i, snapshot in enumerate(history):\n"
                                "    if \"error\" in str(snapshot.values.get(\"messages\", [])[-1:]):\n"
                                "        good_checkpoint = history[i + 1]  # the one just before the error appeared\n"
                                "        break\n\n"
                                "replay_config = {\"configurable\": {\n"
                                "    \"thread_id\": \"conversation-1\",\n"
                                "    \"checkpoint_id\": good_checkpoint.config[\"configurable\"][\"checkpoint_id\"],\n"
                                "}}\n"
                                "result = graph.invoke(None, config=replay_config)"
                            ),
                            "explanation": "Locating the last known-good checkpoint and resuming from there avoids re-running the parts of the workflow that already worked correctly.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Run a multi-step graph, then call get_state_history and print the status or key field at each checkpoint in order, from earliest to latest.",
                            "difficulty": "medium",
                            "hint": "get_state_history returns most-recent-first by default; reverse it if you want chronological order.",
                        },
                        {
                            "prompt": "Pick a checkpoint from the middle of a run's history and replay from it using invoke(None, config=replay_config). Confirm the graph resumes rather than restarting.",
                            "difficulty": "medium",
                            "hint": "Compare the resulting final state's step count against a fresh, from-scratch invocation.",
                        },
                        {
                            "prompt": "Describe, using a scenario of your own choosing, when replaying from an earlier checkpoint would save meaningfully more work than simply re-invoking the graph from scratch.",
                            "difficulty": "medium",
                            "hint": "Consider a workflow where an expensive early step (a slow retrieval or a costly tool call) succeeded, and only a later step needs correcting.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Time travel", "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/#replay", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.4}],
                },
            ],
        },
        # 8. Persistence
        {
            "slug": "persistence",
            "title": "Persistence",
            "description": "Moving from in-memory checkpointing to a production-grade, durable checkpointer, and designing thread-based conversation persistence.",
            "order_index": 8,
            "estimated_hours": 1.4,
            "lessons": [
                {
                    "slug": "persistent-checkpointers-for-production",
                    "title": "Persistent Checkpointers for Production",
                    "description": "Swapping MemorySaver for a durable, database-backed checkpointer that survives process restarts.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Explain why MemorySaver is unsuitable for a production deployment",
                        "Configure a durable checkpointer backed by Postgres or SQLite",
                        "Recognize that the swap requires no change to graph structure or node logic",
                        "Consider checkpoint storage growth and retention as an operational concern",
                    ],
                    "content_markdown": """## Same limitation, same fix, as Course 9's memory

`MemorySaver`'s checkpoints live in process memory, which means exactly the
limitation Course 9's Memory module raised about `InMemoryChatMessageHistory`:
restart the process, run multiple instances behind a load balancer, or
deploy a new version, and checkpoint data is gone or inconsistent. Course
8's Agent State module made the general point — anything that needs to
survive beyond a single process's lifetime needs a durable backing store —
and LangGraph's answer is the same swap-the-implementation pattern you've
now seen twice before.

```python
from langgraph.checkpoint.postgres import PostgresSaver

DB_URI = "postgresql://user:password@localhost:5432/agent_db"

with PostgresSaver.from_conn_string(DB_URI) as checkpointer:
    checkpointer.setup()  # creates the necessary tables on first run
    graph = graph_builder.compile(checkpointer=checkpointer)
    result = graph.invoke(initial_state, config={"configurable": {"thread_id": "conversation-1"}})
```

For lighter-weight deployments, `SqliteSaver` provides the same durability
guarantee backed by a local file instead of a full Postgres instance —
useful for a single-server deployment or local development that still needs
restarts to preserve state.

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("checkpoints.db") as checkpointer:
    graph = graph_builder.compile(checkpointer=checkpointer)
```

## The graph itself doesn't change

Exactly as with the ChatOpenAI-to-ChatAnthropic swap in Course 9, and the
InMemoryChatMessageHistory-to-RedisChatMessageHistory swap in that same
course's Memory module, moving from `MemorySaver` to `PostgresSaver`
touches only the checkpointer construction — every node, edge, and piece of
state schema stays exactly as it was. This consistency across the whole
program isn't a coincidence: it's the direct payoff of LangChain and
LangGraph's shared design principle of standardized interfaces behind which
implementations can be swapped freely.

## Checkpoint growth is an operational concern

Every node execution writes a new checkpoint. Over a long-running thread —
or across millions of threads in a production system — this data grows
continuously, and unlike a single "current state" row, a full checkpoint
history is, by design, an append-only log. Left unmanaged, this becomes a
real storage and query-performance cost. Production deployments typically
need an explicit retention policy: how long to keep full checkpoint history
per thread, whether older checkpoints can be pruned once a thread is
concluded, and whether you need the full time-travel capability from the
previous lesson for every thread indefinitely, or only for a bounded recent
window.

```python
# A rough sketch: periodically delete checkpoints for threads inactive
# past a retention window, keeping recent/active threads fully intact
def prune_old_checkpoints(checkpointer, retention_days: int = 90):
    # Actual implementation depends on the checkpointer backend's schema;
    # the operational principle is what matters here: decide on and enforce
    # a retention policy rather than letting checkpoint storage grow unbounded.
    ...
```
""",
                    "examples": [
                        {
                            "title": "A local development setup with SqliteSaver, mirroring a production PostgresSaver deployment",
                            "code": (
                                "import os\n\n"
                                "def get_checkpointer():\n"
                                "    if os.environ.get(\"ENV\") == \"production\":\n"
                                "        from langgraph.checkpoint.postgres import PostgresSaver\n"
                                "        return PostgresSaver.from_conn_string(os.environ[\"DATABASE_URL\"])\n"
                                "    from langgraph.checkpoint.sqlite import SqliteSaver\n"
                                "    return SqliteSaver.from_conn_string(\"dev_checkpoints.db\")"
                            ),
                            "explanation": "Centralizing checkpointer selection behind one function, keyed by environment, is the same 'keep provider selection at the edges' discipline from Course 9's Models module.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Swap MemorySaver for SqliteSaver in an existing checkpointed graph, and verify a thread's conversation still resumes correctly across two separate Python process runs.",
                            "difficulty": "medium",
                            "hint": "Run one script that invokes the graph once, exit the process, then run a second script that invokes it again with the same thread_id.",
                        },
                        {
                            "prompt": "Write a get_checkpointer() factory function that selects between SqliteSaver and PostgresSaver based on an environment variable, following the example in the lesson.",
                            "difficulty": "easy",
                            "hint": "A simple if/else on an environment variable is sufficient.",
                        },
                        {
                            "prompt": "Sketch (in prose, no need to implement) a retention policy for checkpoint storage in a production system handling 100,000 threads per day, including what data you'd need to decide when a checkpoint is safe to prune.",
                            "difficulty": "hard",
                            "hint": "Consider thread completion status, last-activity timestamp, and whether time-travel is a required feature for concluded threads.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Persistence", "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.3}],
                },
                {
                    "slug": "thread-based-conversation-persistence",
                    "title": "Thread-Based Conversation Persistence",
                    "description": "Designing a thread_id scheme for a multi-user application, and managing thread lifecycle: listing, resuming, and archiving conversations.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Design a thread_id naming scheme for a multi-user, multi-conversation application",
                        "List and resume a user's prior threads from persisted checkpoint data",
                        "Distinguish a concluded thread from an active one, and handle each appropriately",
                        "Apply Course 8's memory-layer thinking to decide what belongs in thread state versus elsewhere",
                    ],
                    "content_markdown": """## Designing thread_id for a real application

A single hardcoded `thread_id` string, as used in this course's examples so
far, doesn't scale to a real application with many users and many
conversations per user. A practical scheme typically composes identifiers:

```python
def make_thread_id(user_id: str, conversation_id: str) -> str:
    return f"user:{user_id}:conv:{conversation_id}"

config = {"configurable": {"thread_id": make_thread_id("u-42", "c-7")}}
```

This mirrors the persistence key scheme exercise from Course 8's Agent
State module directly — the same reasoning (you need enough identifying
information in the key to avoid collisions across users and across that
user's separate conversations) applies whether you're hand-rolling a Redis
key or constructing a LangGraph `thread_id`.

## Listing a user's threads

LangGraph's checkpointers don't provide a built-in "list all threads for
user X" query out of the box — that's an application-level concern you
typically solve by maintaining your own lightweight index (a database table
mapping `user_id` to `thread_id`s, updated whenever a new conversation
starts) alongside the checkpointer's own storage:

```python
def start_new_conversation(user_id: str, db) -> str:
    conversation_id = str(uuid.uuid4())
    thread_id = make_thread_id(user_id, conversation_id)
    db.insert("conversations", {"user_id": user_id, "thread_id": thread_id, "created_at": now()})
    return thread_id

def list_user_conversations(user_id: str, db) -> list[str]:
    return db.query("conversations", filter={"user_id": user_id})
```

This index is metadata *about* threads, distinct from the thread's actual
state (which the checkpointer manages) — a clean separation between "what
conversations does this user have" and "what's the current state of any one
of them."

## Active vs. concluded threads

Not every thread needs to remain resumable forever. A thread that reached a
natural conclusion (the user's task was completed, or the conversation was
explicitly closed) is a good candidate for the retention/pruning policy
discussed in the previous lesson, while an active thread — one the user
might return to — should be fully preserved. Tracking a thread's status
explicitly (in your application-level index, not necessarily in the
graph's own state) is what makes this distinction actionable:

```python
def mark_conversation_concluded(thread_id: str, db):
    db.update("conversations", {"thread_id": thread_id}, {"status": "concluded", "concluded_at": now()})
```

## What belongs in thread state versus elsewhere

Revisiting Course 8's memory-layer framework one more time: a thread's
checkpointed state is fundamentally *session-scoped* — it's the working and
short-term memory for that specific conversation. Facts that should persist
*across* a user's different threads (their name, their preferences, a
running profile) belong in the long-term memory store from Course 8's
Long-Term Memory module — a separate system a node can read from and write
to, not something duplicated into every thread's own checkpointed state.
Conflating these, just as Course 8 warned, risks both cost (redundant data
in every thread) and correctness (a preference updated in one thread not
being visible in another) problems.
""",
                    "examples": [
                        {
                            "title": "A node that reads long-term memory into a thread-scoped conversation",
                            "code": (
                                "def load_user_context(state: State, config) -> dict:\n"
                                "    user_id = config[\"configurable\"][\"user_id\"]\n"
                                "    facts = retrieve_relevant_memories(state[\"messages\"][-1].content, user_id, embedder, vector_store)\n"
                                "    return {\"user_context\": facts}"
                            ),
                            "explanation": "Long-term facts are fetched fresh into this thread's state on demand, rather than being copied and stored redundantly inside the thread's own checkpoint history.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a thread_id scheme for an application where a single conversation can also be shared between two users (e.g. a shared support ticket). What additional identifying information would you need?",
                            "difficulty": "medium",
                            "hint": "Consider whether thread_id should be keyed by a ticket ID rather than by an individual user ID in this case.",
                        },
                        {
                            "prompt": "Sketch the schema for an application-level 'conversations' index table that would let you list all of a given user's threads, ordered by most recently active.",
                            "difficulty": "easy",
                            "hint": "You'll likely want at least user_id, thread_id, created_at, and last_active_at columns.",
                        },
                        {
                            "prompt": "Explain, with a concrete example, why storing a user's long-term preference (like their preferred language) redundantly inside every thread's checkpointed state would cause a correctness bug when that preference changes.",
                            "difficulty": "medium",
                            "hint": "Consider what happens to old threads' copies of the preference after the user updates it.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Persistence", "url": "https://langchain-ai.github.io/langgraph/concepts/persistence/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 0.8}, {"slug": "state", "weight": 0.5}],
                },
            ],
        },
        # 9. Human-in-the-Loop
        {
            "slug": "human-in-the-loop",
            "title": "Human-in-the-Loop",
            "description": "Pausing graph execution for human approval before high-stakes actions, and allowing a human to edit state before resuming.",
            "order_index": 9,
            "estimated_hours": 1.6,
            "lessons": [
                {
                    "slug": "interrupts-for-human-approval",
                    "title": "Interrupts for Human Approval",
                    "description": "Using LangGraph's interrupt mechanism to pause execution before an irreversible action, and resuming after approval.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Configure a graph to pause before a specific node using interrupt_before",
                        "Resume a paused graph after human approval",
                        "Implement conditional, dynamic interrupts using the interrupt() function",
                        "Connect this mechanism directly to the verification gate pattern from Course 8",
                    ],
                    "content_markdown": """## From "ask an LLM if this is safe" to "actually stop and ask a human"

Course 8's Self-Correction module built a verification gate: an LLM check
that ran before an irreversible action and either approved it or flagged it
for human review — but "flagged for human review" was left unimplemented,
noted as exactly the gap this LangGraph module would fill. **Interrupts**
are that mechanism: they pause a graph's execution at a specific point,
durably (thanks to the checkpointing from earlier in this course), until a
human explicitly resumes it.

## Static interrupts: interrupt_before

The simplest form pauses before a named node runs, every time, no
conditional logic required:

```python
graph = graph_builder.compile(checkpointer=checkpointer, interrupt_before=["send_email"])

result = graph.invoke(initial_state, config=config)
# execution pauses here, right before the send_email node would run
print(graph.get_state(config).next)  # ('send_email',) - shows what's about to happen
```

At this point, the graph is genuinely paused — not busy-waiting, not
consuming resources — its state is checkpointed exactly as it was, and it
will remain that way until you explicitly resume it:

```python
# after a human reviews and approves, in a separate request/process entirely
result = graph.invoke(None, config=config)  # None = resume with no new input, proceed to send_email
```

## Dynamic, conditional interrupts

`interrupt_before` pauses unconditionally, every time that node is reached.
For the Course 8 pattern — pause only for *irreversible* actions, not every
action — use the `interrupt()` function inside a node, which lets you decide
dynamically whether to actually pause:

```python
from langgraph.types import interrupt

IRREVERSIBLE_TOOLS = {"send_email", "charge_card", "delete_record"}

def call_model_with_gate(state: State) -> dict:
    response = model_with_tools.invoke(state["messages"])
    if response.tool_calls:
        requested_tool = response.tool_calls[0]["name"]
        if requested_tool in IRREVERSIBLE_TOOLS:
            approval = interrupt({"tool": requested_tool, "args": response.tool_calls[0]["args"]})
            if approval != "approved":
                return {"messages": [response, ("ai", "Action was not approved; stopping.")]}
    return {"messages": [response]}
```

Calling `interrupt(...)` pauses the graph exactly at that point and surfaces
the payload you passed (here, the tool and its arguments) to whatever
system is managing the pause — a UI showing a human the pending action for
review. Resuming later with `Command(resume="approved")` (or a rejection)
continues execution from exactly that point, with the human's decision now
available.

```python
from langgraph.types import Command

result = graph.invoke(Command(resume="approved"), config=config)
```

## This is Course 8's verification gate, completed

Recall Course 8's `verify_before_execute` function ended with: "a failed
verification changes the agent's status rather than crashing... That
pattern... is exactly what you'll build formally with LangGraph's interrupt
mechanism." This lesson is that promise fulfilled — the risk classification
(which actions are irreversible) is the same judgment call from Course 8;
what LangGraph adds is a durable, resumable pause, rather than an in-memory
status flag your process would lose if it restarted while waiting for a
human.
""",
                    "examples": [
                        {
                            "title": "A full approve/reject flow around an interrupt",
                            "code": (
                                "result = graph.invoke(initial_state, config=config)\n"
                                "pending = graph.get_state(config)\n"
                                "if pending.next:  # graph is paused, waiting on a human\n"
                                "    print(\"Pending action:\", pending.values.get(\"pending_tool_call\"))\n"
                                "    human_decision = get_human_approval_via_ui()  # your application's own UI/API\n"
                                "    result = graph.invoke(Command(resume=human_decision), config=config)"
                            ),
                            "explanation": "The graph's paused state is fully inspectable via get_state before deciding how to resume it, letting a UI show exactly what's pending approval.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Compile a graph with interrupt_before set on a specific node, invoke it, confirm execution pauses there, then resume with invoke(None, config=config) and confirm it completes.",
                            "difficulty": "medium",
                            "hint": "Check graph.get_state(config).next after the first invoke to confirm the pause happened where expected.",
                        },
                        {
                            "prompt": "Implement a call_model_with_gate node using interrupt() that only pauses when the requested tool is in an IRREVERSIBLE_TOOLS set, letting other tool calls proceed without pausing.",
                            "difficulty": "hard",
                            "hint": "Follow the lesson's example closely, checking response.tool_calls before deciding whether to call interrupt().",
                        },
                        {
                            "prompt": "Extend the approve/reject flow so a rejected action logs the rejection and routes to a different node (e.g. asking the model to propose an alternative) rather than simply stopping.",
                            "difficulty": "hard",
                            "hint": "You can branch on the resume value inside the node after interrupt() returns.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Human-in-the-loop", "url": "https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}],
                },
                {
                    "slug": "editing-state-mid-execution",
                    "title": "Editing State Mid-Execution",
                    "description": "Letting a human modify a paused graph's state directly before resuming, and the safety considerations that come with it.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Update a paused graph's state using update_state before resuming",
                        "Explain the difference between approving/rejecting an action and editing its parameters",
                        "Design a safe interface for human edits that doesn't bypass validation",
                        "Recognize the limits of human review as a safety mechanism",
                    ],
                    "content_markdown": """## Beyond approve/reject: letting a human fix the details

The previous lesson's interrupts support a binary approve/reject decision.
Often the more useful intervention is smaller and more surgical: the
proposed action is *almost* right, but a human should correct one detail —
a misspelled recipient, a slightly wrong dollar amount — before it proceeds.
LangGraph's `update_state` lets you modify a paused graph's state directly:

```python
config = {"configurable": {"thread_id": "conversation-1"}}
graph.invoke(initial_state, config=config)  # pauses before send_email, as in the previous lesson

current = graph.get_state(config)
print(current.values["pending_tool_call"])  # {'tool': 'send_email', 'args': {'to': 'jon@example.com', ...}}

# A human notices the email is misspelled and corrects it
graph.update_state(config, {"pending_tool_call": {"tool": "send_email", "args": {"to": "john@example.com", "subject": "...", "body": "..."}}})

result = graph.invoke(None, config=config)  # resumes with the corrected value
```

`update_state` merges the given update into the checkpointed state using
the same reducers that would apply to a node's return value — it's not a
separate, special mechanism, it's the identical merge logic from this
course's State module, just triggered by a human's edit instead of a node's
return value.

## Approve/reject vs. edit: different failure modes, different value

Approve/reject is the right interface when the only real question is "should
this happen at all" — the parameters, if it does happen, are already
correct. Editing is the right interface when the parameters themselves are
the risk — an almost-right amount, a near-miss recipient — and rejecting the
whole action wholesale would just force the agent to regenerate a new
attempt from scratch, wasting the (correct) parts of its original proposal.
Designing which interface a given interrupt point offers is a genuine
product decision, not just a technical one.

## Don't let a human edit bypass validation

A human-supplied edit is still just data flowing back into your graph — it
deserves the same scrutiny you'd apply to any other input. If
`pending_tool_call`'s arguments are meant to satisfy a tool's schema, a human
edit that violates that schema should be caught before the graph resumes,
not silently accepted and passed straight to the tool:

```python
def validated_update_state(config, update: dict, graph):
    if "pending_tool_call" in update:
        tool_name = update["pending_tool_call"]["tool"]
        args = update["pending_tool_call"]["args"]
        if not check_permission(current_role, tool_name):  # from Course 8's Guardrails module
            raise PermissionError(f"edited action still not permitted: {tool_name}")
    graph.update_state(config, update)
```

This is the same defense-in-depth principle from Course 8's Guardrails
module, applied one layer later: guardrails should catch a bad action
whether it originated from the model or from a human's correction, because
the tool being called doesn't know or care which source the arguments came
from.

## The limits of human review as a safety mechanism

Human-in-the-loop review is a strong safeguard, but it's not infallible — a
reviewer under time pressure, reviewing many similar-looking approvals in a
row, can rubber-stamp a request they'd have caught with more scrutiny (a
well-documented failure mode sometimes called "approval fatigue"). Treat
human review as one layer in the same defense-in-depth stack as Course 8's
guardrails and verification gates — a strong layer, but not a substitute for
the deterministic checks (permission systems, spending limits) that don't
depend on a reviewer's attention holding up under repetition.
""",
                    "examples": [
                        {
                            "title": "A minimal review UI backend, tying update_state and resume together",
                            "code": (
                                "def submit_human_review(thread_id: str, decision: str, edited_args: dict | None):\n"
                                "    config = {\"configurable\": {\"thread_id\": thread_id}}\n"
                                "    if decision == \"edit\" and edited_args:\n"
                                "        graph.update_state(config, {\"pending_tool_call\": {\"args\": edited_args}})\n"
                                "        return graph.invoke(None, config=config)\n"
                                "    if decision == \"approve\":\n"
                                "        return graph.invoke(Command(resume=\"approved\"), config=config)\n"
                                "    return graph.invoke(Command(resume=\"rejected\"), config=config)"
                            ),
                            "explanation": "One function handles all three human-review outcomes — approve, reject, and edit-then-approve — dispatching to the appropriate LangGraph mechanism for each.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Pause a graph before a node using interrupt_before, use update_state to modify a field in its state, then resume and confirm the modified value was actually used.",
                            "difficulty": "medium",
                            "hint": "Print the state both before and after update_state to confirm the change took effect.",
                        },
                        {
                            "prompt": "Write a validated_update_state wrapper (following the lesson's example) that rejects an edit attempting to set a tool argument to an empty or missing required field.",
                            "difficulty": "medium",
                            "hint": "Check the edited args against the tool's expected schema before calling the real update_state.",
                        },
                        {
                            "prompt": "Describe a concrete scenario in a high-volume review workflow where approval fatigue could plausibly cause a reviewer to approve a genuinely bad action, and propose one mitigation.",
                            "difficulty": "hard",
                            "hint": "Consider mitigations like randomly sampling approvals for deeper audit, or capping how many approvals one reviewer handles per hour.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph docs: Human-in-the-loop", "url": "https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 1.0}, {"slug": "state", "weight": 0.3}],
                },
            ],
        },
        # 10. Multi-Agent Workflows
        {
            "slug": "multi-agent-workflows",
            "title": "Multi-Agent Workflows",
            "description": "Coordinating several specialized agents within one graph using a supervisor pattern, and handing off work between them.",
            "order_index": 10,
            "estimated_hours": 1.7,
            "lessons": [
                {
                    "slug": "supervisor-architectures-in-langgraph",
                    "title": "Supervisor Architectures in LangGraph",
                    "description": "Building a supervisor node that routes work to specialized sub-agent nodes, each a compiled graph of its own.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Explain the supervisor pattern as a formalization of Course 8's Routing module",
                        "Wire specialized sub-agents (as compiled graphs) into nodes of a parent graph",
                        "Implement a supervisor node that decides which sub-agent handles a given request",
                        "Design each sub-agent's scope narrowly, following the specialization principles from earlier courses",
                    ],
                    "content_markdown": """## This is Course 8's Routing module, fully realized

Course 8's Routing module ended by naming exactly where this was heading:
"What you're building here... is structurally identical to the supervisor
pattern that anchors multi-agent system design, which you'll build formally
with LangGraph in Course 10." This lesson is that promise. A **supervisor**
is a node whose entire job is deciding which specialized sub-agent should
handle the current request — the same `classify_intent` / dispatch logic
from Course 8, now coordinating full LangGraph sub-agents instead of simple
handler functions.

## Sub-agents as nodes

Because a compiled graph is itself a Runnable (Course 10's Edges module
covered this), a specialized sub-agent — built with `create_react_agent` or
hand-rolled with its own narrow tool set — can be wrapped as a single node
inside a larger supervisor graph:

```python
billing_agent = create_react_agent(llm, [get_invoice, update_payment_method])
tech_agent = create_react_agent(llm, [restart_service, check_system_status])

def billing_node(state: SupervisorState) -> dict:
    result = billing_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}

def tech_node(state: SupervisorState) -> dict:
    result = tech_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"]}
```

Each sub-agent only knows about its own tools — the same least-privilege
scoping from Course 8's Guardrails module, now enforced structurally by
simply never binding a sub-agent to tools outside its role.

## The supervisor node

```python
from typing import Literal

class SupervisorState(TypedDict):
    messages: Annotated[list, add_messages]
    next_agent: str

def supervisor(state: SupervisorState) -> dict:
    decision_prompt = f'''
    Given this conversation, which specialist should handle the next step:
    "billing", "technical", or "done" if the request is fully resolved?

    Conversation: {state["messages"]}
    Respond with just one word.
    '''
    decision = llm.invoke(decision_prompt).content.strip().lower()
    valid = {"billing", "technical", "done"}
    return {"next_agent": decision if decision in valid else "done"}

def route_to_specialist(state: SupervisorState) -> str:
    return state["next_agent"]

graph_builder = StateGraph(SupervisorState)
graph_builder.add_node("supervisor", supervisor)
graph_builder.add_node("billing", billing_node)
graph_builder.add_node("technical", tech_node)

graph_builder.add_edge(START, "supervisor")
graph_builder.add_conditional_edges("supervisor", route_to_specialist, {
    "billing": "billing", "technical": "technical", "done": END,
})
graph_builder.add_edge("billing", "supervisor")   # back to supervisor for the next decision
graph_builder.add_edge("technical", "supervisor")
```

Notice the cycle back to `supervisor` after each specialist runs — this
lets the supervisor re-evaluate after every step, exactly the re-routing
capability Course 8's Dynamic Routing lesson argued was necessary ("a
request classified as technical_support can reveal... it's actually a
billing issue in disguise").

## Why this belongs in a graph, not a hand-rolled dispatcher

Everything this module needs — the supervisor's decision as visible graph
structure, the ability to checkpoint and resume a multi-agent conversation,
the ability to interrupt for human approval before a specific specialist
takes an irreversible action — is exactly what the rest of this course
built. A hand-rolled Python dispatcher (Course 8's version) works, but
reimplementing checkpointing, interrupts, and recursion limits on top of it
would mean rebuilding everything LangGraph already gives you for free once
the workflow is expressed as a graph.
""",
                    "examples": [
                        {
                            "title": "Invoking the supervisor graph on a mixed request",
                            "code": (
                                "graph = graph_builder.compile(checkpointer=checkpointer)\n"
                                "result = graph.invoke(\n"
                                "    {\"messages\": [(\"human\", \"My last invoice looks wrong AND my service keeps disconnecting.\")]},\n"
                                "    config={\"configurable\": {\"thread_id\": \"support-99\"}},\n"
                                ")\n"
                                "# the supervisor will likely route to billing first, then technical, then \"done\""
                            ),
                            "explanation": "A single request spanning two domains gets handled by both specialists in turn, with the supervisor re-evaluating after each one completes.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Build the full supervisor graph from the lesson with two specialist sub-agents, and invoke it with a request that only needs one of them.",
                            "difficulty": "hard",
                            "hint": "Confirm the supervisor correctly routes straight to 'done' after the single relevant specialist finishes.",
                        },
                        {
                            "prompt": "Add a third specialist sub-agent to the graph (a new create_react_agent, a new node, and an update to the supervisor's routing options), without modifying the billing or technical nodes.",
                            "difficulty": "medium",
                            "hint": "This mirrors the 'extending a router without disturbing existing branches' exercise from the Conditional Routing module.",
                        },
                        {
                            "prompt": "Test the mixed request from the lesson's example and trace, via the messages list, how many times the supervisor ran and which specialist it chose at each step.",
                            "difficulty": "medium",
                            "hint": "Enable return of intermediate state or inspect checkpoint history to see the sequence of supervisor decisions.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph conceptual guide: multi-agent systems", "url": "https://langchain-ai.github.io/langgraph/concepts/multi_agent/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "langgraph", "weight": 0.8}, {"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "handing-off-between-specialized-agents",
                    "title": "Handing Off Between Specialized Agents",
                    "description": "Letting a sub-agent signal it needs a different specialist, and passing enough context along that the handoff doesn't lose information.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement a handoff signal a sub-agent can raise to request a different specialist",
                        "Design shared state so a handoff doesn't lose context gathered so far",
                        "Bound the number of handoffs to prevent unproductive ping-ponging between agents",
                        "Evaluate the tradeoff between a centralized supervisor and peer-to-peer handoffs",
                    ],
                    "content_markdown": """## Two handoff architectures

The supervisor pattern from the previous lesson is centralized: every
routing decision flows back through one supervisor node. An alternative,
sometimes called **peer-to-peer handoff**, lets a sub-agent itself decide it
can't help and specify which specialist should take over next, without
going back through a central decision-maker each time:

```python
class HandoffState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str

def billing_node(state: HandoffState) -> dict:
    result = billing_agent.invoke({"messages": state["messages"]})
    last_content = result["messages"][-1].content
    if "i can't help with technical issues" in last_content.lower():
        return {"messages": result["messages"], "current_agent": "technical"}
    return {"messages": result["messages"], "current_agent": "done"}
```

This is a direct implementation of the `run_with_handoff_check` pattern
from Course 8's Dynamic Routing lesson — a specialized agent recognizing the
limits of its own competence and naming who should take over, rather than a
central router pre-deciding everything up front.

## Preserving context across the handoff

A handoff is only useful if the receiving specialist has access to
everything learned so far — re-explaining the problem from scratch to each
new specialist is exactly the kind of information loss Course 8's Agent
State module warned against. Because `messages` is shared graph state with
the `add_messages` reducer, every specialist naturally sees the full
conversation history, including what previous specialists already
discovered:

```python
def technical_node(state: HandoffState) -> dict:
    # tech_agent sees the FULL messages history, including billing's prior findings,
    # not just the original user request
    result = tech_agent.invoke({"messages": state["messages"]})
    return {"messages": result["messages"], "current_agent": "done"}
```

## Bounding handoffs

Exactly as Course 8's `run_with_rerouting` capped `max_handoffs` to prevent
a request ping-ponging indefinitely between specialists, a graph-based
handoff system needs the same guard — otherwise two sub-agents that each
believe the other is better suited can loop forever:

```python
class HandoffState(TypedDict):
    messages: Annotated[list, add_messages]
    current_agent: str
    handoff_count: int

def route_next(state: HandoffState) -> str:
    if state.get("handoff_count", 0) >= 3:
        return "escalate_to_human"  # bounded, same discipline as Course 8
    return state["current_agent"]
```

This is the same `recursion_limit`-plus-explicit-counter combination from
this course's Loops module, applied specifically to handoffs rather than
generic tool-calling iterations — the principle (bound every loop, whatever
it's called) doesn't change; only the specific counter does.

## Supervisor vs. peer-to-peer: a real tradeoff

A centralized supervisor gives you one place to see and audit every routing
decision, which matters for debuggability and for applying consistent
policy (like Course 8's guardrails) uniformly. Peer-to-peer handoff can be
more efficient — a specialist that already knows it needs to hand off
doesn't have to wait for a separate supervisor call to confirm it — but
scatters routing logic across every sub-agent, which is harder to audit and
easier to get subtly wrong as the number of specialists grows. Most
production multi-agent systems lean centralized for exactly this
auditability reason, reserving peer-to-peer handoff for cases where the
extra supervisor round-trip is a genuine, measured performance problem.
""",
                    "examples": [
                        {
                            "title": "A bounded peer-to-peer handoff graph",
                            "code": (
                                "graph_builder = StateGraph(HandoffState)\n"
                                "graph_builder.add_node(\"billing\", billing_node)\n"
                                "graph_builder.add_node(\"technical\", technical_node)\n"
                                "graph_builder.add_node(\"escalate_to_human\", escalate_node)\n\n"
                                "graph_builder.add_edge(START, \"billing\")  # assume requests start here for this example\n"
                                "graph_builder.add_conditional_edges(\"billing\", route_next, {\n"
                                "    \"technical\": \"technical\", \"done\": END, \"escalate_to_human\": \"escalate_to_human\",\n"
                                "})\n"
                                "graph_builder.add_edge(\"technical\", END)\n"
                                "graph_builder.add_edge(\"escalate_to_human\", END)"
                            ),
                            "explanation": "route_next checks handoff_count before allowing another handoff, guaranteeing the graph terminates even if the two specialists disagree indefinitely about who should own the request.",
                        },
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement a handoff_count field that increments on every handoff, and a route_next function that escalates to a human node after 3 handoffs, following the lesson's pattern.",
                            "difficulty": "medium",
                            "hint": "Increment the counter inside each specialist node's return value, using an operator.add-style reducer or manual increment.",
                        },
                        {
                            "prompt": "Test a scenario where two specialists would otherwise ping-pong a request back and forth indefinitely, and confirm your bounded handoff logic correctly escalates instead of looping forever.",
                            "difficulty": "hard",
                            "hint": "You can simulate this by having both specialist nodes always request a handoff to the other, regardless of content.",
                        },
                        {
                            "prompt": "Write a short comparison (3-5 sentences) arguing for either the supervisor or peer-to-peer architecture for a 6-specialist customer support system, considering auditability and latency.",
                            "difficulty": "medium",
                            "hint": "Weigh the value of a single auditable routing point against the cost of an extra round-trip per specialist decision.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph conceptual guide: multi-agent systems", "url": "https://langchain-ai.github.io/langgraph/concepts/multi_agent/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}, {"slug": "langgraph", "weight": 0.6}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "LangGraph: Course Assessment",
    "description": "Checks readiness to move from graph-based single and multi-agent orchestration into formal agent evaluation and safety.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 40,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "Why does a linear LCEL chain struggle to express the routing and looping patterns from Course 8, while a graph handles them naturally?",
            "options": [
                {"id": "a", "text": "LCEL chains cannot call tools at all"},
                {"id": "b", "text": "A chain's steps always flow in one fixed sequence; a graph's conditional and backward-pointing edges let execution branch and cycle as first-class, declared structure"},
                {"id": "c", "text": "Chains are slower than graphs for every workload"},
                {"id": "d", "text": "Graphs cannot use chat models"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The core structural difference is that a chain is a straight line, while a graph's conditional and cyclical edges directly express branching and looping control flow.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "When a LangGraph node function returns {'answer': 'some text'}, what happens to the other fields already present in the graph's state?",
            "options": [
                {"id": "a", "text": "They are all reset to their default values"},
                {"id": "b", "text": "They remain unchanged; the returned dict is merged as a partial update, not a full state replacement"},
                {"id": "c", "text": "The graph raises an error because the return value is incomplete"},
                {"id": "d", "text": "They are deleted from state permanently"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Nodes return partial updates; LangGraph merges them into the existing state rather than requiring or expecting a full state object back.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "state",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are true about reducers in LangGraph state? Select all that apply.",
            "options": [
                {"id": "a", "text": "The default reducer behavior, with no annotation, is to overwrite a field with the most recent value"},
                {"id": "b", "text": "A reducer is a two-argument function that combines the current value and a new value"},
                {"id": "c", "text": "add_messages is a built-in reducer suited for conversation history fields"},
                {"id": "d", "text": "Reducers can only be used with fields of type int"},
            ],
            "correct_answer": {"choices": ["a", "b", "c"]},
            "explanation": "Default merge behavior is overwrite; a reducer is a (current, new) -> merged function; add_messages is LangGraph's built-in reducer for message lists. Reducers work with any field type, not just int.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "state",
        },
        {
            "question_type": "mcq",
            "prompt": "In a graph with two edges both originating from the same node ('fetch' -> 'extract_a' and 'fetch' -> 'extract_b'), what happens after 'fetch' completes?",
            "options": [
                {"id": "a", "text": "Only the first-defined edge's target runs"},
                {"id": "b", "text": "'extract_a' and 'extract_b' run in parallel (fan-out)"},
                {"id": "c", "text": "The graph raises a compile error because a node cannot have two outgoing edges"},
                {"id": "d", "text": "'extract_a' and 'extract_b' run sequentially in an undefined order"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Multiple outgoing edges from the same source node create a fan-out, where all target nodes run in parallel.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "Why should a conditional edge's routing function always include an explicit default/fallback branch?",
            "options": [
                {"id": "a", "text": "LangGraph requires exactly 3 branches minimum"},
                {"id": "b", "text": "If the routing function returns a label not present in the edge mapping, the graph has no defined next node and errors at runtime"},
                {"id": "c", "text": "Default branches make the graph run faster"},
                {"id": "d", "text": "It is only needed when using create_react_agent"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "An unmapped label from a routing function leaves the graph with no valid next step, so defensive routing functions guard against unexpected values with an explicit default.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "coding",
            "prompt": "Write the should_continue routing function for a LangGraph tool-calling loop: given a State with a 'messages' field (a list of message objects, most recent last), return 'tools' if the last message has any tool_calls, and 'end' otherwise.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Inspects the last message in state['messages'] and returns 'tools' if it has a non-empty tool_calls attribute, otherwise returns 'end'.",
                "sample_solution": (
                    "def should_continue(state: State) -> str:\n"
                    "    last_message = state[\"messages\"][-1]\n"
                    "    return \"tools\" if last_message.tool_calls else \"end\""
                ),
            },
            "explanation": "This is the exact conditional edge logic that creates the tool-calling cycle: routing back to the tool node when more tool calls are requested, or to END when the model has produced a final answer.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "What is the relationship between recursion_limit and an explicit in-state counter like tool_call_count, as covered in the Loops module?",
            "options": [
                {"id": "a", "text": "They are redundant; only one should ever be used"},
                {"id": "b", "text": "recursion_limit bounds the entire graph's total steps as a coarse backstop; an explicit counter provides finer, domain-specific control over a particular cycle, and production graphs often use both"},
                {"id": "c", "text": "recursion_limit only applies to conditional edges, not cycles"},
                {"id": "d", "text": "An explicit counter replaces the need for a checkpointer"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "The two mechanisms operate at different levels of granularity and are complementary, mirroring Course 8's combination of retries with circuit breaking.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "What does a checkpointer do that a plain, uncheckpointed graph invocation does not provide?",
            "options": [
                {"id": "a", "text": "It makes every LLM call faster"},
                {"id": "b", "text": "It saves state after every node execution, enabling resumability across calls, inspection of history, and time-travel replay"},
                {"id": "c", "text": "It automatically translates the graph into a different programming language"},
                {"id": "d", "text": "It removes the need for a state schema"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Checkpointing is the foundation for resumable conversations, inspectable execution history, and replaying from earlier states — none of which a stateless, uncheckpointed invocation provides.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is MemorySaver unsuitable for a production deployment running multiple server instances, in the same way InMemoryChatMessageHistory was unsuitable in Course 9?",
            "options": [
                {"id": "a", "text": "It only supports a single tool"},
                {"id": "b", "text": "Its checkpoints live only in one process's memory, so they aren't shared across instances or durable across restarts"},
                {"id": "c", "text": "It cannot be used with conditional edges"},
                {"id": "d", "text": "It requires a paid LangGraph license"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Durable, shared checkpointing across instances and restarts requires a database-backed checkpointer like PostgresSaver, the same durability requirement covered for chat history in Course 9.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "scenario",
            "prompt": "You're building a graph-based agent that can send refund confirmation emails. Refunds under $50 should proceed automatically; refunds of $50 or more should pause for a human to review and, if needed, correct the amount before it's sent. Describe how you would use interrupt_before or interrupt(), plus update_state, to implement this, and explain why a static interrupt_before alone would be insufficient.",
            "options": [],
            "correct_answer": {"expected": "Use the dynamic interrupt() function inside the node that would send the refund email, checking the refund amount and only calling interrupt() when it is >= $50 (a static interrupt_before would pause for every refund unconditionally, including ones under $50 that shouldn't need review). Once paused, a human can review the pending refund via get_state, and if the amount needs correcting, call update_state to modify the pending action's arguments before resuming the graph with invoke(None, config) or Command(resume=...). This mirrors Course 8's verification gate pattern (only gate irreversible/high-risk actions) combined with the ability to edit, not just approve/reject, the pending action."},
            "explanation": "This scenario tests the ability to combine conditional (dynamic) interrupts with state editing, and to reason about why a blanket static interrupt would be the wrong tool for a threshold-based policy.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "langgraph",
        },
        {
            "question_type": "mcq",
            "prompt": "In a supervisor-pattern multi-agent graph, why does the edge structure typically route from each specialist node back to the supervisor, rather than straight to END?",
            "options": [
                {"id": "a", "text": "It is required by LangGraph's compiler for all graphs"},
                {"id": "b", "text": "It lets the supervisor re-evaluate after every specialist's turn, enabling re-routing if the request turns out to need a different or additional specialist"},
                {"id": "c", "text": "It reduces the number of tokens used by the graph"},
                {"id": "d", "text": "It is only necessary when using create_react_agent for the sub-agents"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Routing back to the supervisor after each specialist enables the re-routing capability Course 8 argued was necessary when a request's true nature only becomes clear partway through handling it.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "Why must a handoff mechanism between peer specialist agents include a bounded counter (like handoff_count), similar to Course 8's max_handoffs?",
            "options": [
                {"id": "a", "text": "LangGraph does not allow more than 2 nodes to communicate"},
                {"id": "b", "text": "Without a bound, two specialists that each believe the other is better suited for a request could hand off back and forth indefinitely, never resolving"},
                {"id": "c", "text": "Handoffs are always slower than a single specialist handling the full request"},
                {"id": "d", "text": "A bounded counter is required syntax for add_conditional_edges"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "An unbounded handoff mechanism risks the same unproductive ping-ponging failure mode Course 8 identified, so a counter with an escalation path (e.g., to a human) is necessary.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain why a specialized sub-agent's messages history, when it's part of shared graph state with the add_messages reducer, naturally solves the 'context loss on handoff' problem described in the Multi-Agent Workflows module.",
            "options": [],
            "correct_answer": {
                "expected": "Because messages is shared state with an accumulating reducer (add_messages), every specialist node that runs receives the full conversation history built up so far, including findings and exchanges from any previous specialist. This means a newly handed-off specialist doesn't need the problem re-explained from scratch; it already sees everything earlier specialists and the user have said, preventing the information loss that would occur if each specialist only saw the original request in isolation.",
                "keywords": ["shared state", "add_messages", "context", "handoff", "accumulate"],
            },
            "explanation": "This connects the reducer mechanics from the State module directly to a practical multi-agent design benefit: context preservation across specialist handoffs.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "state",
        },
        {
            "question_type": "mcq",
            "prompt": "A compiled StateGraph in LangGraph implements the same Runnable interface (.invoke, .batch, .stream) as a LangChain chain. What does this enable?",
            "options": [
                {"id": "a", "text": "Graphs can only be called from within another graph, never standalone"},
                {"id": "b", "text": "A compiled graph can be composed with other Runnables and even nested as a node inside a larger graph, the same composability principle from LCEL"},
                {"id": "c", "text": "It means graphs cannot use conditional edges"},
                {"id": "d", "text": "It eliminates the need for a state schema"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Because compiled graphs are Runnables, they compose the same way chains do, which is exactly what makes nesting sub-agent graphs inside a supervisor graph possible.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "langgraph",
        },
    ],
}
