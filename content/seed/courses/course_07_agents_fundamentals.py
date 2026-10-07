"""
Course 7: AI Agents Fundamentals

Teaches what makes a system an agent rather than a chatbot: the agent loop,
reasoning and acting, tool use, structured outputs, state, memory, planning,
reflection, and routing. This is the conceptual and practical foundation for
every framework-specific course (LangChain, LangGraph, multi-agent systems)
later in the program.
"""

COURSE = {
    "slug": "ai-agents-fundamentals",
    "title": "AI Agents Fundamentals",
    "subtitle": "From single-shot chatbots to systems that reason, act, and adapt.",
    "description": (
        "An AI agent is more than a chatbot with a system prompt -- it's a system that can "
        "reason about a goal, take actions in the world through tools, observe the results, "
        "and adjust its plan accordingly. This course builds that mental model from the ground "
        "up: the core agent loop, the ReAct reasoning pattern, tool and function calling, "
        "structured outputs, state management, memory, planning, reflection, and routing. "
        "You'll hand-roll a working agent loop before ever reaching for a framework, so the "
        "abstractions in later courses (LangChain, LangGraph) feel like conveniences, not magic."
    ),
    "learning_outcomes": [
        "Distinguish an AI agent from a chatbot and identify when agentic behavior is actually needed",
        "Implement the core agent loop: observe, reason, act, repeat",
        "Apply the ReAct pattern to interleave reasoning traces with tool actions",
        "Define tools and use function/tool calling to let a model invoke them reliably",
        "Enforce structured outputs so agent decisions can be parsed and executed safely",
        "Design agent state and memory architectures for multi-step and multi-turn tasks",
        "Implement planning and reflection loops that improve agent reliability",
        "Build a router that dispatches tasks to the right tool, agent, or workflow",
    ],
    "order_index": 7,
    "estimated_hours": 20,
    "level": "intermediate",
    "icon": "bot",
    "modules": [
        # ---------------------------------------------------------------
        {
            "slug": "what-is-an-ai-agent",
            "title": "What is an AI Agent?",
            "description": "Defining agency in AI systems: goals, autonomy, tool use, and the feedback loop that separates agents from single-shot generation.",
            "order_index": 1,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "defining-agency-in-ai-systems",
                    "title": "Defining Agency in AI Systems",
                    "description": "Understand the core properties -- goal-directedness, autonomy, tool use, feedback -- that make a system an agent.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define an AI agent in terms of goal-directed, multi-step behavior",
                        "Identify the four properties that distinguish agents from single-shot LLM calls",
                        "Explain why tool access alone doesn't make a system an agent",
                        "Recognize agentic and non-agentic systems from a description of their behavior",
                    ],
                    "content_markdown": """
## Why this matters

"Agent" has become one of the most overused words in AI, applied to everything from a single
LLM call with a system prompt to complex multi-step autonomous systems. Getting a precise
definition straight now will save you from both over-engineering simple problems and
under-engineering ones that genuinely need agentic behavior.

## A working definition

An **AI agent** is a system that, given a goal, can autonomously decide a sequence of actions
to take, execute those actions (often through tools), observe the results, and adjust its
subsequent actions based on those observations -- repeating until the goal is achieved or it
determines the goal cannot be reached.

```python
# NOT an agent: single-shot generation, no actions, no feedback loop
response = llm.generate("Summarize this document.")

# An agent: decides actions, executes them, observes results, adapts
goal = "Find out if we're low on stock for any bestselling product and reorder if so"
agent.run(goal)
# Internally: checks sales data (action) -> observes results -> checks
# inventory levels (action) -> observes low stock -> places reorder (action)
```

## The four properties of agency

**Goal-directedness.** An agent works toward an objective, not just a single response to a
single input. "Summarize this document" is a task; "keep our inventory above threshold" is a
goal that might require multiple different actions depending on what's discovered along the
way.

**Autonomy.** The agent decides *which* actions to take and *in what order*, rather than
following a hardcoded sequence a human wrote in advance. This is what separates an agent from a
regular script that happens to call an LLM at one step.

**Tool use.** Agents act on the world (or at least on external systems) through tools --
functions, APIs, databases -- rather than only producing text. This is necessary but not
sufficient on its own, which is the key nuance in the next section.

**Feedback and adaptation.** An agent observes the result of its actions and incorporates that
observation into its next decision. A system that calls one tool and stops, regardless of what
that tool returns, is not exhibiting the feedback loop that defines agentic behavior.

## Why tool access alone isn't enough

A common misconception: any system that calls a function is "an agent." Consider a chatbot that
always calls a weather API when asked about weather, formats the result, and replies -- this is
tool use, but it's a fixed, single-step pipeline, not agency. There's no autonomous decision
about *whether* or *how many times* to call the tool, and no adaptation based on what the tool
returns. Compare that to a system that checks the weather, realizes rain is forecast, decides on
its own to also check a calendar for outdoor events, and only then decides whether to send an
alert -- that chain of self-directed, observation-driven decisions is what agency actually looks
like.

## A quick test

Ask yourself: if you removed the ability to make more than one decision at a time, would this
system still work the same way? If yes, it's a single-shot or fixed pipeline. If the system's
value genuinely depends on chaining multiple *self-directed* decisions together, informed by
what it learns along the way, you're looking at an agent. This distinction will recur throughout
this course, most directly in the next lesson comparing agents to chatbots.
""",
                    "examples": [
                        {
                            "title": "Pipeline vs. agent for the same task",
                            "code": (
                                "# Fixed pipeline: always the same 3 steps, no matter what happens\n"
                                "def handle_request(order_id):\n"
                                "    order = lookup_order(order_id)\n"
                                "    status = check_shipping_status(order)\n"
                                "    return format_response(status)\n"
                                "\n"
                                "# Agent: decides its OWN next step based on what it observes\n"
                                "# e.g. if shipping_status shows 'delayed', it might autonomously\n"
                                "# decide to also check for a refund-eligibility rule before replying"
                            ),
                            "explanation": "The pipeline always executes the same three calls; the agent's second and third actions depend on what it learned from the first -- that dependency is the essence of agency.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Describe a system you've used (a form autofill tool, a search engine, a smart thermostat) and evaluate it against the four properties of agency from this lesson.",
                            "difficulty": "easy",
                            "hint": "Check each property individually -- a system can have some but not all four.",
                        },
                        {
                            "prompt": "Design a one-paragraph description of a genuinely agentic system for scheduling meetings, explicitly identifying which parts exhibit goal-directedness, autonomy, tool use, and feedback.",
                            "difficulty": "medium",
                            "hint": "Consider what happens when a preferred time slot is unavailable -- does the system autonomously try alternatives?",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}],
                },
                {
                    "slug": "when-to-build-an-agent-vs-a-simpler-system",
                    "title": "When to Build an Agent vs. a Simpler System",
                    "description": "Weigh the reliability and cost tradeoffs of agentic architectures against simpler, fixed pipelines.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify the reliability and latency costs that come with agentic autonomy",
                        "Recognize task characteristics that call for an agent versus a fixed workflow",
                        "Explain why unnecessary agency often makes a system harder to debug and test",
                        "Apply a simple decision framework for choosing agent vs. pipeline architecture",
                    ],
                    "content_markdown": """
## Why this matters

Agentic systems are harder to build, test, debug, and predict than fixed pipelines. Before
reaching for an agent architecture, it's worth being honest about whether the task actually
needs autonomous, multi-step decision-making, or whether a well-designed fixed pipeline (or even
a single well-crafted prompt) would do the job more reliably and more cheaply.

## The hidden costs of agency

**Reliability.** Every autonomous decision point is a place the agent can choose the wrong
action, loop unnecessarily, or misinterpret an observation. A fixed pipeline with 3 steps has 3
places to test; an agent that can choose among 5 tools across up to 10 iterations has a
combinatorially larger space of possible execution paths, many of which you'll never see until
they happen in production.

**Latency and cost.** Each reasoning-and-action step in an agent loop typically costs at least
one LLM call. A task that a fixed pipeline completes in one or two calls might take an agent
five or six calls to arrive at the same answer, simply because it has to reason about what to do
at each step rather than following a predetermined path.

**Debuggability.** When a fixed pipeline produces a wrong result, you know exactly which of its
N steps to inspect. When an agent produces a wrong result, you often have to reconstruct its
entire reasoning trace to understand *why* it chose the actions it did -- a much harder
debugging problem, covered in depth in the Agent Loop module.

## When a task doesn't need an agent

```python
# This task has a fixed, known sequence of steps regardless of input --
# a pipeline, not an agent, is the right tool:
def process_refund_request(request):
    validated = validate_request(request)
    eligible = check_refund_policy(validated)
    if eligible:
        return issue_refund(validated)
    return deny_refund(validated, reason="policy")
```

If you can write out the entire sequence of steps in advance, regardless of what the input
looks like, you almost certainly don't need an agent -- you need a well-structured pipeline,
possibly with one or two LLM calls embedded in it for specific sub-tasks like classification or
extraction.

## When a task genuinely needs an agent

```python
# This task's steps genuinely depend on what's discovered along the way --
# an agent is justified here:
goal = "Investigate why the deploy pipeline failed and propose a fix"
# The agent might need to: check recent commits, read error logs, run a
# diagnostic command, check if a dependency changed -- and WHICH of these
# it does, and in what order, depends entirely on what it finds at each step
```

Tasks with unpredictable branching, open-ended investigation, or a genuinely unknown number of
steps needed to reach a goal are where agentic autonomy earns its cost.

## A simple decision framework

1. **Can you enumerate the exact steps in advance, for any input?** If yes, build a pipeline.
2. **Does the task require deciding, based on intermediate results, whether more work is
   needed?** If yes, an agent (or at minimum a bounded loop) is likely justified.
3. **Is reliability more important than flexibility for this specific task?** If yes, lean
   toward a pipeline even if some agentic behavior would technically help, and constrain the
   agent's autonomy where you do use one.
4. **What's the cost of a wrong autonomous decision?** High-stakes tasks (financial
   transactions, irreversible actions) warrant tighter guardrails or human-in-the-loop
   checkpoints regardless of architecture.

## Hybrid approaches are common

Many production systems aren't purely one or the other -- a fixed pipeline with one embedded
agentic sub-step (like an open-ended research task within an otherwise deterministic workflow)
often captures most of the benefit of agency while keeping the overall system's behavior
predictable. Keep this hybrid option in mind rather than treating "agent or pipeline" as a
binary choice for an entire system.
""",
                    "examples": [
                        {
                            "title": "A hybrid system: mostly pipeline, one agentic step",
                            "code": (
                                "def handle_support_ticket(ticket):\n"
                                "    category = classify_ticket(ticket)  # fixed step\n"
                                "    if category == \"billing\":\n"
                                "        return handle_billing_pipeline(ticket)  # fixed pipeline\n"
                                "    elif category == \"complex_technical\":\n"
                                "        return technical_investigation_agent.run(ticket)  # agentic step\n"
                                "    return escalate_to_human(ticket)"
                            ),
                            "explanation": "Only the genuinely unpredictable branch (open-ended technical investigation) gets agentic treatment -- everything else stays a simpler, more testable pipeline.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For each of these three tasks, decide whether it needs an agent or a fixed pipeline, and justify your answer: (1) converting a CSV to JSON, (2) researching a competitor's pricing across multiple unknown sources, (3) answering a single FAQ question.",
                            "difficulty": "easy",
                            "hint": "Ask whether the sequence of steps can be fully enumerated in advance for each task.",
                        },
                        {
                            "prompt": "Design a hybrid system for handling customer emails, identifying exactly one sub-task that justifies agentic treatment and explaining why the rest should stay a fixed pipeline.",
                            "difficulty": "medium",
                            "hint": "Look for the one part of the workflow with genuinely unpredictable branching.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents -- when to use agentic systems",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "agent-vs-chatbot",
            "title": "Agent vs. Chatbot",
            "description": "A precise comparison of conversational chatbots and agents, and why the difference matters for what you build.",
            "order_index": 2,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "how-chatbots-and-agents-actually-differ",
                    "title": "How Chatbots and Agents Actually Differ",
                    "description": "Compare the architecture of a conversational chatbot to an agent, action by action.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Describe the architecture of a typical conversational chatbot",
                        "Identify what an agent adds on top of a chatbot's conversation loop",
                        "Explain why RAG chatbots sit on the spectrum between simple chatbot and full agent",
                        "Recognize that the same underlying model can power either architecture",
                    ],
                    "content_markdown": """
## Why this matters

"Chatbot" and "agent" are often used interchangeably in marketing material, but architecturally
they're quite different systems, built for different purposes. Knowing exactly where the line
is will help you scope projects correctly and avoid promising agentic reliability from a system
that's actually a conversational interface.

## What a chatbot is

A chatbot's core loop is simple: receive a user message, generate a response conditioned on
conversation history, return the response, wait for the next message.

```python
def chatbot_turn(conversation_history: list, user_message: str, llm) -> str:
    conversation_history.append({"role": "user", "content": user_message})
    response = llm.chat(messages=conversation_history)
    conversation_history.append({"role": "assistant", "content": response})
    return response
```

Everything a chatbot does happens within this single request-response pattern. Even a chatbot
with RAG retrieval bolted on (Course 6) still follows a fixed sequence per turn: retrieve once,
generate once, respond. It doesn't autonomously decide to retrieve again, take a different
action, or continue working after that one response.

## What an agent adds

An agent's loop doesn't stop at one response -- it continues taking actions and observing
results until the goal is met or it decides to stop, without necessarily waiting for the user
in between.

```python
def agent_turn(goal: str, tools: dict, llm, max_steps: int = 10) -> str:
    history = [{"role": "user", "content": goal}]
    for step in range(max_steps):
        decision = llm.chat(messages=history, tools=list(tools.values()))
        if decision.is_final_answer:
            return decision.content
        tool_result = tools[decision.tool_name](**decision.tool_args)
        history.append({"role": "assistant", "content": decision.raw})
        history.append({"role": "tool", "content": str(tool_result)})
    return "Could not complete the goal within the step limit."
```

The key structural difference: a chatbot's loop is driven by the *user* sending another message;
an agent's loop is driven by the *system itself* deciding another action is needed, without
waiting on the user at all.

## RAG chatbots sit in between

A RAG-powered support chatbot (Course 6) retrieves context and answers -- more capable than a
plain chatbot, since it can ground answers in real documents, but it still follows one fixed
retrieve-then-generate sequence per user turn. It doesn't decide to search a second source, call
an external API to check order status, or take any action beyond generating a grounded text
response. This puts RAG chatbots on the spectrum between simple chatbots and full agents,
closer to the chatbot end, since the *sequence* of operations per turn is fixed rather than
autonomously decided.

## The same model, two different architectures

Critically, the underlying LLM doesn't determine whether a system is a chatbot or an agent --
the same model can power either, depending on how the surrounding code is structured. A chatbot
becomes agent-like the moment you give it (a) tools, (b) the ability to decide whether and how
many times to use them, and (c) a loop that continues based on its own decisions rather than
only the user's next message.

## Why the distinction matters practically

Calling a simple RAG chatbot "an agent" in a product spec sets the wrong expectations --
stakeholders may expect autonomous multi-step problem solving that the fixed retrieve-generate
architecture simply cannot do. Conversely, building full agentic autonomy for a task that only
needed a well-grounded single-turn answer adds unnecessary complexity and failure surface, as
covered in the previous module's decision framework.
""",
                    "examples": [
                        {
                            "title": "Same task, chatbot response vs. agent response",
                            "code": (
                                "# Chatbot: answers from what it already knows or retrieves once\n"
                                "user_msg = \"Is my order #4521 going to arrive on time?\"\n"
                                "# Chatbot response: generic shipping policy info (no live lookup)\n"
                                "\n"
                                "# Agent: takes an action to find out, then answers based on the result\n"
                                "# Agent internally calls check_order_status(order_id=4521),\n"
                                "# observes 'delayed', and responds with the actual current status"
                            ),
                            "explanation": "The chatbot can only respond from what it was told or retrieved once; the agent takes an action to get a real answer, which is exactly the tool-use-plus-feedback loop from the previous module.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Take a chatbot you've interacted with (customer support, a coding assistant) and identify one feature that would require turning it into an agent, versus features it can support as a pure chatbot.",
                            "difficulty": "easy",
                            "hint": "Look for anything that requires taking an action in an external system, not just generating text.",
                        },
                        {
                            "prompt": "Explain why a RAG chatbot with retrieval is more capable than a plain chatbot but still isn't a full agent, using the agent_turn vs. chatbot_turn code from this lesson as a reference.",
                            "difficulty": "medium",
                            "hint": "Focus on whether the sequence of operations per turn is fixed or autonomously decided.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents -- workflows vs. agents",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}],
                },
                {
                    "slug": "upgrading-a-chatbot-into-an-agent",
                    "title": "Upgrading a Chatbot into an Agent",
                    "description": "Hands-on: take a simple chatbot loop and incrementally add the pieces that make it agentic.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Start from a minimal chatbot loop and identify what's missing for agency",
                        "Add a tool registry and tool invocation to the loop",
                        "Add a continuation condition so the system can act without waiting for the user",
                        "Compare the behavior of the upgraded system against the original chatbot on the same task",
                    ],
                    "content_markdown": """
## Why this matters

Reading about the chatbot-to-agent distinction is one thing; watching a chatbot's own code
transform, step by step, into an agent makes the distinction concrete and gives you a template
you'll reuse for the rest of this course.

## Step 1: the starting chatbot

```python
def chatbot(user_message: str, history: list, llm) -> str:
    history.append({"role": "user", "content": user_message})
    response = llm.chat(messages=history)
    history.append({"role": "assistant", "content": response})
    return response
```

This can hold a conversation, but it can't check anything, look anything up, or take any
action -- every response comes purely from the model's own knowledge and the conversation so
far.

## Step 2: add a tool registry

```python
def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "delayed", "eta": "2026-09-28"}

TOOLS = {
    "get_order_status": {
        "function": get_order_status,
        "description": "Look up the current shipping status of an order by ID.",
        "parameters": {"order_id": "string"},
    }
}
```

Having tools defined doesn't make the system agentic yet -- this step alone just gives the model
*access* to a capability, without any mechanism for it to decide to use it.

## Step 3: let the model decide to call a tool

```python
def chatbot_with_tools(user_message: str, history: list, llm) -> str:
    history.append({"role": "user", "content": user_message})
    decision = llm.chat(messages=history, tools=[t["description"] for t in TOOLS.values()])

    if decision.tool_call:
        result = TOOLS[decision.tool_call.name]["function"](**decision.tool_call.arguments)
        history.append({"role": "tool", "content": str(result)})
        final_response = llm.chat(messages=history)  # one more call to incorporate the result
        history.append({"role": "assistant", "content": final_response})
        return final_response

    history.append({"role": "assistant", "content": decision.content})
    return decision.content
```

This is now meaningfully agentic in a small way: the model *decides* whether to call a tool
based on the user's message, rather than it being hardcoded. But it's still bounded to at most
one tool call per turn.

## Step 4: add a continuation loop for multi-step tasks

```python
def agent_with_loop(goal: str, llm, max_steps: int = 5) -> str:
    history = [{"role": "user", "content": goal}]
    for step in range(max_steps):
        decision = llm.chat(messages=history, tools=[t["description"] for t in TOOLS.values()])
        if not decision.tool_call:
            return decision.content
        result = TOOLS[decision.tool_call.name]["function"](**decision.tool_call.arguments)
        history.append({"role": "assistant", "content": decision.raw})
        history.append({"role": "tool", "content": str(result)})
    return "Reached step limit without a final answer."
```

This final version can take *multiple* actions in sequence, each informed by the result of the
last, without waiting for the user in between -- the full agent loop the next module covers in
depth.

## Comparing behavior on the same task

```python
task = "Check if order #4521 is delayed, and if so, check if there's a known warehouse issue affecting it."
# chatbot_with_tools: can check the order status, but cannot ALSO check for
# a warehouse issue in the same turn without another explicit user message
# agent_with_loop: can chain both checks autonomously in one call, because
# the loop continues based on what it observes, not on user input
```

## What you just built

Each step in this lesson added exactly one property from the four-property definition of agency
in the first module of this course: tool use (Step 2-3) and multi-step autonomy plus feedback
(Step 4). Seeing them added incrementally like this should make the abstract definition from
Module 1 feel concrete and buildable, not theoretical.
""",
                    "examples": [
                        {
                            "title": "Running the same goal through both versions",
                            "code": (
                                "goal = \"Check if order #4521 is delayed, and if so, check for a warehouse issue.\"\n"
                                "print(chatbot_with_tools(goal, [], llm))   # handles at most one tool call\n"
                                "print(agent_with_loop(goal, llm))          # chains both checks autonomously"
                            ),
                            "explanation": "Running identical input through both implementations makes the practical difference between bounded and looped tool use directly observable.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a second tool, check_warehouse_issues(order_id), to the TOOLS registry, and confirm agent_with_loop can chain get_order_status followed by check_warehouse_issues for a single goal.",
                            "difficulty": "medium",
                            "hint": "The model needs both tool descriptions passed to llm.chat() for it to choose between them.",
                        },
                        {
                            "prompt": "Add step-by-step print logging to agent_with_loop showing which tool was called and what was returned at each iteration, and run it on a 3-step task.",
                            "difficulty": "easy",
                            "hint": "Print inside the loop before appending to history.",
                        },
                        {
                            "prompt": "Explain what would happen if max_steps were set to 1 in agent_with_loop for a task genuinely requiring 3 tool calls, and why this is a real production risk to guard against.",
                            "difficulty": "medium",
                            "hint": "Consider the 'Reached step limit' fallback path and what a user would actually see.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "OpenAI: function calling guide",
                            "url": "https://platform.openai.com/docs/guides/function-calling",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 0.8}, {"slug": "tools", "weight": 0.5}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "agent-loop",
            "title": "Agent Loop",
            "description": "The observe-reason-act cycle that powers every agent, and how to implement it with proper stopping conditions.",
            "order_index": 3,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "the-observe-reason-act-cycle",
                    "title": "The Observe-Reason-Act Cycle",
                    "description": "Break down the fundamental loop every agent architecture is built on, regardless of framework.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Name and explain each stage of the observe-reason-act cycle",
                        "Explain why this loop generalizes across every agent framework",
                        "Identify what state must persist across iterations of the loop",
                        "Trace a multi-step task through several iterations of the loop by hand",
                    ],
                    "content_markdown": """
## Why this matters

Whatever agent framework you eventually use -- LangGraph, a custom loop, or something else
entirely -- underneath it is some version of this same cycle. Understanding it at this level
means you can debug, extend, or reimplement agent behavior in any framework, because you
understand the mechanism, not just one library's API for it.

## The three stages

**Observe.** The agent receives information: the initial goal, the result of its last action, or
new input from the environment. This becomes part of what the agent reasons about next.

**Reason.** The agent (via an LLM call) decides what to do next, given everything it has
observed so far. This might be "call this tool with these arguments," "the goal is complete,
here's the final answer," or "I need more information before I can proceed."

**Act.** The agent executes the decision from the reasoning step -- typically calling a tool --
producing a new observation that feeds back into the next iteration.

```python
def agent_loop(goal: str, tools: dict, llm, max_iterations: int = 10) -> str:
    observations = [{"role": "user", "content": goal}]

    for iteration in range(max_iterations):
        # REASON: decide the next action given everything observed so far
        decision = llm.chat(messages=observations, tools=list(tools.values()))

        if decision.is_final_answer:
            return decision.content

        # ACT: execute the decided tool call
        result = tools[decision.tool_name]["function"](**decision.tool_args)

        # OBSERVE: the tool's result becomes the next observation
        observations.append({"role": "assistant", "content": decision.raw})
        observations.append({"role": "tool", "content": str(result)})

    return "Reached max iterations without a final answer."
```

## Why this loop generalizes

Every agent framework -- LangGraph's graph-based execution, a simple while-loop, a multi-agent
orchestrator -- is fundamentally implementing this same observe-reason-act cycle, just with
different amounts of structure around state transitions, parallelism, and error handling. The
LangGraph course later in this program will feel like "the same loop, with a more expressive way
to define the graph of possible transitions" rather than an entirely new concept.

## What state must persist across iterations

The `observations` list in the code above is the accumulated state the agent carries from one
iteration to the next -- without it, each reasoning step would have no memory of what happened
before, and the agent could get stuck repeating the same action forever. This is a first
glimpse of the Agent State module later in this course, which formalizes exactly what needs to
persist and how.

## Tracing a multi-step task by hand

Consider the goal "find the average order value for last month and flag it if it dropped more
than 10% from the month before."

1. **Observe:** the goal.
2. **Reason:** decide to call `get_orders(month="last")`.
3. **Act:** call it, get a list of orders.
4. **Observe:** the order list.
5. **Reason:** decide to call `calculate_average(orders)`.
6. **Act:** call it, get this month's average.
7. **Observe:** the average.
8. **Reason:** decide to call `get_orders(month="previous")` and `calculate_average` again.
9. **Act:** call both, get last month's average.
10. **Observe:** both averages.
11. **Reason:** compute the percentage change, decide it's a final answer.
12. **Act:** return the formatted answer.

Six full iterations, each building on the observation from the last -- exactly the pattern the
`agent_loop` function above implements generically, regardless of what the specific tools or
goal are.

## The loop needs a stopping condition -- explored next

Notice the `max_iterations` bound in the code above. Without an explicit stopping condition, an
agent loop has no guarantee of ever terminating -- a critical reliability concern the next
lesson addresses directly.
""",
                    "examples": [
                        {
                            "title": "Tracing state growth across iterations",
                            "code": (
                                "# After iteration 1: observations has 3 entries (goal, decision, tool result)\n"
                                "# After iteration 2: observations has 5 entries\n"
                                "# After iteration 3: observations has 7 entries\n"
                                "# Each reasoning step sees the FULL accumulated history --\n"
                                "# this is both the loop's strength (full context) and its cost\n"
                                "# (growing token usage per call, addressed in the Agent State module)"
                            ),
                            "explanation": "Watching the observations list grow makes concrete why long-running agent loops eventually need context management strategies, previewed here and covered fully later in this course.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Trace a 4-step version of the agent_loop function by hand for the goal 'find the cheapest flight from two providers and book the cheaper one,' listing what happens at each observe/reason/act stage.",
                            "difficulty": "medium",
                            "hint": "You'll likely need at least 3 tool calls: check provider A, check provider B, book the winner.",
                        },
                        {
                            "prompt": "Implement agent_loop with a simple print statement at each stage (OBSERVE/REASON/ACT) and run it against 2 fake tools for a 2-step task.",
                            "difficulty": "medium",
                            "hint": "You can stub out llm.chat() with a hardcoded sequence of decisions for testing without a real API.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents -- the augmented LLM and agent loops",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}],
                },
                {
                    "slug": "stopping-conditions-and-loop-safety",
                    "title": "Stopping Conditions and Loop Safety",
                    "description": "Implement iteration limits, cost budgets, and repeated-action detection so agent loops fail safely instead of running forever.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a maximum iteration limit as a hard stopping condition",
                        "Add a cost or token budget as a second, independent stopping condition",
                        "Detect and break out of repeated-action loops the agent gets stuck in",
                        "Design a graceful fallback response when a loop terminates without success",
                    ],
                    "content_markdown": """
## Why this matters

An agent loop without robust stopping conditions is a production incident waiting to happen: an
infinite loop calling a paid API, or a user staring at a spinner while an agent repeats the same
failed action forever. This lesson builds the safety rails every real agent loop needs before it
ever reaches production traffic.

## Layer 1: a hard iteration limit

```python
def agent_loop(goal: str, tools: dict, llm, max_iterations: int = 10) -> dict:
    observations = [{"role": "user", "content": goal}]
    for iteration in range(max_iterations):
        decision = llm.chat(messages=observations, tools=list(tools.values()))
        if decision.is_final_answer:
            return {"status": "success", "answer": decision.content, "iterations": iteration + 1}
        result = tools[decision.tool_name]["function"](**decision.tool_args)
        observations.append({"role": "assistant", "content": decision.raw})
        observations.append({"role": "tool", "content": str(result)})
    return {"status": "max_iterations_reached", "answer": None, "iterations": max_iterations}
```

A hard iteration cap is the simplest, most essential guardrail -- every agent loop needs one,
full stop, even if you also add the more sophisticated checks below.

## Layer 2: a cost or token budget

Iteration count alone doesn't capture cost -- a single iteration with a huge tool result can
cost far more in tokens than several iterations with small ones. Track cumulative token usage as
an independent budget.

```python
def agent_loop_with_budget(goal: str, tools: dict, llm, max_iterations: int = 10, max_tokens: int = 20000) -> dict:
    observations = [{"role": "user", "content": goal}]
    total_tokens = 0

    for iteration in range(max_iterations):
        decision = llm.chat(messages=observations, tools=list(tools.values()))
        total_tokens += decision.usage.total_tokens

        if total_tokens > max_tokens:
            return {"status": "budget_exceeded", "answer": None, "iterations": iteration + 1}
        if decision.is_final_answer:
            return {"status": "success", "answer": decision.content, "iterations": iteration + 1}

        result = tools[decision.tool_name]["function"](**decision.tool_args)
        observations.append({"role": "assistant", "content": decision.raw})
        observations.append({"role": "tool", "content": str(result)})

    return {"status": "max_iterations_reached", "answer": None, "iterations": max_iterations}
```

## Layer 3: detecting repeated actions

Agents can get stuck calling the same tool with the same arguments repeatedly, especially when a
tool result doesn't give the model enough signal to realize a different approach is needed.

```python
def detect_repeated_action(action_history: list, current_action: tuple, threshold: int = 2) -> bool:
    recent = action_history[-threshold:]
    return recent.count(current_action) >= threshold

def agent_loop_with_loop_detection(goal: str, tools: dict, llm, max_iterations: int = 10) -> dict:
    observations = [{"role": "user", "content": goal}]
    action_history = []

    for iteration in range(max_iterations):
        decision = llm.chat(messages=observations, tools=list(tools.values()))
        if decision.is_final_answer:
            return {"status": "success", "answer": decision.content, "iterations": iteration + 1}

        current_action = (decision.tool_name, tuple(sorted(decision.tool_args.items())))
        if detect_repeated_action(action_history, current_action):
            return {"status": "stuck_in_loop", "answer": None, "iterations": iteration + 1}
        action_history.append(current_action)

        result = tools[decision.tool_name]["function"](**decision.tool_args)
        observations.append({"role": "assistant", "content": decision.raw})
        observations.append({"role": "tool", "content": str(result)})

    return {"status": "max_iterations_reached", "answer": None, "iterations": max_iterations}
```

Catching this pattern early (after 2 identical repeats, rather than waiting for max_iterations)
saves both cost and latency on a task that was never going to succeed by repeating the same
failed action.

## Graceful fallback responses

Every non-success status (`budget_exceeded`, `stuck_in_loop`, `max_iterations_reached`) needs a
user-facing message that's honest about what happened without being alarming or exposing
internal details.

```python
FALLBACK_MESSAGES = {
    "budget_exceeded": "This task turned out to be more complex than expected. Let me connect you with a person who can help.",
    "stuck_in_loop": "I wasn't able to make progress on this. Could you rephrase or provide more detail?",
    "max_iterations_reached": "This is taking longer than expected. I'll flag it for follow-up.",
}

def render_agent_result(result: dict) -> str:
    if result["status"] == "success":
        return result["answer"]
    return FALLBACK_MESSAGES.get(result["status"], "Something went wrong. Please try again.")
```

## Why all three layers matter together

Iteration limits catch loops that take many small steps; token budgets catch loops with a few
expensive steps; repeated-action detection catches the specific failure mode of the agent
genuinely being stuck rather than just being slow. Production agent systems use all three
together, because each one catches a failure pattern the others miss.
""",
                    "examples": [
                        {
                            "title": "A stuck agent caught by loop detection before hitting max_iterations",
                            "code": (
                                "# An agent repeatedly calls search(query=\"refund policy\") because the\n"
                                "# tool keeps returning an empty result and the model doesn't adjust its\n"
                                "# query. Without loop detection, this runs all the way to max_iterations=10.\n"
                                "# With loop detection (threshold=2), it stops after iteration 3,\n"
                                "# saving 7 wasted LLM and tool calls."
                            ),
                            "explanation": "This is a realistic failure mode in agents with weak tools or ambiguous instructions -- loop detection turns a slow, expensive failure into a fast, cheap one.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement agent_loop_with_loop_detection and test it against a fake tool that always returns the same unhelpful result, confirming it stops early with status 'stuck_in_loop'.",
                            "difficulty": "medium",
                            "hint": "Stub the LLM to always request the same tool call when given the same unhelpful observation, simulating a genuinely stuck agent.",
                        },
                        {
                            "prompt": "Extend detect_repeated_action to also catch near-identical (not just exactly identical) repeated actions, such as the same tool called with slightly different but functionally equivalent arguments.",
                            "difficulty": "hard",
                            "hint": "Consider normalizing arguments (e.g., case-insensitive string comparison) before comparing.",
                        },
                        {
                            "prompt": "Write a table listing each of the three stopping conditions from this lesson, the specific failure mode each one catches, and one it would NOT catch on its own.",
                            "difficulty": "easy",
                            "hint": "Consider a single very expensive iteration versus many cheap repeated ones.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: recursion limits and loop safety",
                            "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#recursion-limit",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 0.8}, {"slug": "state", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "reasoning-and-action",
            "title": "Reasoning and Action",
            "description": "The ReAct pattern: interleaving explicit reasoning traces with actions to improve agent decision quality.",
            "order_index": 4,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "the-react-pattern",
                    "title": "The ReAct Pattern",
                    "description": "Understand why making an agent's reasoning explicit, interleaved with actions, improves decision quality over acting directly.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the ReAct pattern: Thought, Action, Observation cycles",
                        "Describe why explicit reasoning traces improve action selection",
                        "Compare ReAct-style prompting to direct action selection without reasoning",
                        "Recognize the tradeoff between reasoning verbosity and cost",
                    ],
                    "content_markdown": """
## Why this matters

The agent loop from the previous module says *what* happens at each step (reason, then act) but
not *how* to get good reasoning out of an LLM before it commits to an action. ReAct (Reason +
Act) is the specific prompting pattern that made this reliable enough to be the default approach
across nearly every agent framework since it was introduced.

## The core idea: explicit thoughts before actions

Rather than asking a model to directly output an action, ReAct asks it to first articulate its
reasoning in a "Thought," then decide an "Action" based on that reasoning, then incorporate the
resulting "Observation" before its next Thought.

```
Thought: The user wants to know if order #4521 will arrive on time. I should check its current shipping status first.
Action: get_order_status(order_id="4521")
Observation: {"status": "delayed", "eta": "2026-09-28"}
Thought: The order is delayed. I should check if there's a known warehouse issue explaining this before telling the user.
Action: check_warehouse_issues(order_id="4521")
Observation: {"issue": "weather delay at regional hub"}
Thought: I now have enough information to give a complete, useful answer.
Action: Final Answer: Your order is delayed due to a weather-related issue at our regional hub. New ETA is 2026-09-28.
```

## Why explicit reasoning improves action selection

Language models generate text autoregressively -- each token is conditioned on everything
generated before it. Forcing the model to write out its reasoning *before* committing to an
action means the action itself is conditioned on that reasoning, which measurably improves
decision quality on multi-step tasks compared to asking the model to jump straight to an action.
This is closely related to chain-of-thought prompting from prompt engineering, applied
specifically to the action-selection problem.

```python
REACT_SYSTEM_PROMPT = (
    "Solve the task by alternating between Thought, Action, and Observation steps.\\n"
    "Thought: reason about what you know and what to do next.\\n"
    "Action: either call a tool, or write 'Final Answer: <answer>' if you have enough information.\\n"
    "Always write a Thought before every Action."
)
```

## ReAct vs. direct action selection

Without ReAct, a model asked to "just pick the next tool call" often does so based on surface
pattern-matching to the goal text, without working through what it's actually learned from prior
observations. With ReAct, the model has to explicitly connect each observation to its next
decision in natural language first -- catching cases where, for example, an observation
contradicts an earlier assumption, which a direct-to-action approach is more likely to miss.

```python
# Without ReAct: the model might jump to a plausible-looking but wrong action
# based on the goal alone, without processing what get_order_status returned

# With ReAct: the Thought step forces the model to explicitly state
# "the order is delayed" before deciding the next action, making it much
# more likely the next action is actually informed by that observation
```

## The cost of verbosity

ReAct's explicit Thought steps cost extra tokens on every single iteration of the agent loop --
a real, measurable cost tradeoff for the improved reliability. For simple, low-stakes tasks
where action selection is rarely ambiguous, this overhead may not be worth it; for complex,
multi-step tasks where a wrong action is costly, it usually is. Many production systems tune
this by asking for brief, single-sentence Thoughts rather than long reasoning traces, balancing
the benefit against the cost.

## ReAct and the earlier definition of agency

Notice how directly ReAct's Thought-Action-Observation cycle maps onto the observe-reason-act
loop from the previous module -- ReAct is best understood as a specific, well-tested prompting
strategy for the "reason" stage of that general loop, not a separate architecture.
""",
                    "examples": [
                        {
                            "title": "A Thought catching a wrong assumption",
                            "code": (
                                "# Goal: \"Refund order #4521 if it hasn't shipped yet.\"\n"
                                "# Thought: I should check whether order #4521 has shipped before refunding.\n"
                                "# Action: get_order_status(order_id=\"4521\")\n"
                                "# Observation: {\"status\": \"shipped\", \"shipped_at\": \"2026-09-20\"}\n"
                                "# Thought: The order has already shipped, so per the goal I should NOT\n"
                                "# issue a refund. I'll explain this instead.\n"
                                "# Action: Final Answer: Order #4521 has already shipped, so per policy it's not eligible for this refund path."
                            ),
                            "explanation": "The explicit Thought after the observation is what catches the goal's condition ('if it hasn't shipped') and correctly avoids an incorrect refund -- a direct-to-action model might have refunded without re-checking the condition.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write out a full ReAct trace (Thought/Action/Observation, at least 3 cycles) by hand for the goal 'find out whether we should restock product SKU-882 based on current inventory and recent sales velocity.'",
                            "difficulty": "medium",
                            "hint": "You'll likely need a check_inventory tool and a check_sales_velocity tool, each producing an observation the next Thought should react to.",
                        },
                        {
                            "prompt": "Rewrite the REACT_SYSTEM_PROMPT to require Thoughts of at most one sentence, and explain what tradeoff this instruction is making.",
                            "difficulty": "easy",
                            "hint": "Shorter thoughts cost fewer tokens but may capture less nuanced reasoning.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "ReAct: Synergizing Reasoning and Acting in Language Models (original paper)",
                            "url": "https://arxiv.org/abs/2210.03629",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}],
                },
                {
                    "slug": "implementing-a-react-agent",
                    "title": "Implementing a ReAct Agent",
                    "description": "Build a working ReAct loop with a real LLM call, parsing Thought/Action/Observation steps from raw model output.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a ReAct loop that parses Thought and Action from model output",
                        "Distinguish tool-call actions from a final answer in the parsed output",
                        "Log the full reasoning trace for later debugging",
                        "Handle malformed model output that doesn't follow the expected format",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson explained ReAct conceptually; this one builds a working implementation you
could actually run, including the unglamorous but essential part: parsing potentially messy
model output into structured Thought/Action pairs your code can act on.

## The ReAct prompt template

```python
REACT_PROMPT = (
    "Answer the following goal using Thought/Action/Observation cycles.\\n"
    "Available tools: {tool_descriptions}\\n\\n"
    "Use this exact format:\\n"
    "Thought: <your reasoning>\\n"
    "Action: <tool_name>(<arguments as JSON>) OR Final Answer: <answer>\\n\\n"
    "Goal: {goal}\\n\\n"
    "{trace_so_far}"
)
```

## Parsing Thought and Action from raw text

```python
import re
import json

def parse_react_step(raw_output: str) -> dict:
    thought_match = re.search(r"Thought:\\s*(.+?)(?=\\nAction:|$)", raw_output, re.DOTALL)
    action_match = re.search(r"Action:\\s*(.+)", raw_output, re.DOTALL)

    thought = thought_match.group(1).strip() if thought_match else None
    action_text = action_match.group(1).strip() if action_match else None

    if action_text is None:
        return {"thought": thought, "type": "malformed", "raw": raw_output}
    if action_text.startswith("Final Answer:"):
        return {"thought": thought, "type": "final_answer", "content": action_text[len("Final Answer:"):].strip()}

    tool_match = re.match(r"(\\w+)\\((.*)\\)", action_text, re.DOTALL)
    if not tool_match:
        return {"thought": thought, "type": "malformed", "raw": raw_output}

    tool_name, args_str = tool_match.groups()
    try:
        args = json.loads(args_str) if args_str.strip() else {}
    except json.JSONDecodeError:
        return {"thought": thought, "type": "malformed", "raw": raw_output}

    return {"thought": thought, "type": "tool_call", "tool_name": tool_name, "tool_args": args}
```

Regex-and-JSON parsing like this is fragile compared to native structured output or tool-calling
APIs (covered in the Structured Outputs module) -- this manual version is worth building once to
understand exactly what those APIs are doing for you under the hood.

## The full ReAct loop

```python
def react_agent(goal: str, tools: dict, llm, max_iterations: int = 8) -> dict:
    trace = []
    tool_descriptions = "\\n".join(f"- {name}: {t['description']}" for name, t in tools.items())

    for iteration in range(max_iterations):
        trace_text = "\\n".join(trace)
        prompt = REACT_PROMPT.format(tool_descriptions=tool_descriptions, goal=goal, trace_so_far=trace_text)
        raw_output = llm.generate(prompt, temperature=0.2, stop=["Observation:"])
        step = parse_react_step(raw_output)

        if step["type"] == "malformed":
            trace.append(f"Thought: {step.get('thought', '')}\\nAction: [unparseable, retrying]")
            continue
        if step["type"] == "final_answer":
            return {"status": "success", "answer": step["content"], "trace": trace}

        result = tools[step["tool_name"]]["function"](**step["tool_args"])
        trace.append(f"Thought: {step['thought']}\\nAction: {step['tool_name']}({step['tool_args']})\\nObservation: {result}")

    return {"status": "max_iterations_reached", "answer": None, "trace": trace}
```

Passing `stop=["Observation:"]` to the LLM call prevents the model from hallucinating its own
fake observation instead of waiting for the real tool result -- a subtle but important detail,
since models will happily continue the pattern themselves if not stopped.

## Handling malformed output gracefully

Notice the `malformed` branch doesn't crash the loop -- it logs the issue and lets the loop try
again on the next iteration, since occasional format slips are common even with well-prompted
models and shouldn't take down the whole agent.

## The trace as a debugging artifact

```python
result = react_agent("Check if order #4521 is delayed and why.", tools, llm)
print("\\n".join(result["trace"]))
```

This full Thought/Action/Observation trace is exactly what makes agent debugging tractable, as
promised back in the Agent Loop module -- when the final answer is wrong, you can read this
trace top to bottom and see precisely which reasoning step led the agent astray.
""",
                    "examples": [
                        {
                            "title": "Reading a trace to debug a wrong answer",
                            "code": (
                                "# trace[0]: 'Thought: I should check order status first.\\n\"\n"
                                "#            'Action: get_order_status({\"order_id\": \"4521\"})\\n'\n"
                                "#            'Observation: {\"status\": \"shipped\"}'\n"
                                "# trace[1]: 'Thought: The order shipped, no need to check warehouse issues.\\n'\n"
                                "#            'Action: Final Answer: Order shipped, no delay.'\n"
                                "# If this answer is later found WRONG (order was actually delayed after\n"
                                "# shipping), the trace shows the agent never checked a post-ship tracking\n"
                                "# tool -- pointing directly at a missing tool, not a reasoning failure"
                            ),
                            "explanation": "This illustrates exactly how a ReAct trace turns 'the agent was wrong' into a specific, actionable diagnosis -- here, a missing tool rather than a flawed thought process.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement parse_react_step and test it against 3 raw output strings: one well-formed tool call, one final answer, and one malformed string missing an Action line.",
                            "difficulty": "medium",
                            "hint": "Write these as literal test strings rather than requiring a real LLM call.",
                        },
                        {
                            "prompt": "Run react_agent against a 2-tool task and print the full trace, then identify which line of the trace you'd check first if the final answer were wrong.",
                            "difficulty": "medium",
                            "hint": "Work backward from the Final Answer line through each preceding Thought.",
                        },
                        {
                            "prompt": "Add a retry limit specifically for malformed output (separate from max_iterations) so the agent gives up after 3 consecutive malformed steps instead of burning its full iteration budget on parsing failures.",
                            "difficulty": "hard",
                            "hint": "Track a separate counter that resets on any successfully parsed step.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain: ReAct agent implementation reference",
                            "url": "https://python.langchain.com/docs/how_to/agent_executor/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "tools",
            "title": "Tools",
            "description": "Defining external capabilities an agent can invoke, and what makes a tool definition genuinely usable by a model.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "what-makes-a-good-tool-definition",
                    "title": "What Makes a Good Tool Definition",
                    "description": "Design tool interfaces an LLM can reliably choose and invoke correctly, with clear names, descriptions, and parameters.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify the components of a complete tool definition",
                        "Explain why tool descriptions matter as much as the underlying implementation",
                        "Design tool parameter schemas that reduce invocation errors",
                        "Recognize common tool design mistakes that confuse model tool selection",
                    ],
                    "content_markdown": """
## Why this matters

An agent is only as capable as the tools it has access to, and only as reliable as those tools
are easy for the model to correctly choose and invoke. A powerful tool with a vague description
or ambiguous parameters will get called incorrectly or not at all -- the model can only work
with what you tell it about the tool, not what the tool's code actually does.

## The anatomy of a tool definition

```python
GET_ORDER_STATUS_TOOL = {
    "name": "get_order_status",
    "description": "Retrieve the current shipping status, ETA, and any known delay reason for a customer order.",
    "parameters": {
        "type": "object",
        "properties": {
            "order_id": {"type": "string", "description": "The order identifier, e.g. '4521' or 'ORD-4521'."},
        },
        "required": ["order_id"],
    },
}
```

Four things matter here: a clear **name** the model can pattern-match to intent, a
**description** explaining exactly what the tool does and when to use it, a **parameter
schema** the model must fill in correctly, and a marked **required** field list so the model
knows what it must gather before calling.

## Why descriptions matter as much as implementation

The model never sees your tool's source code -- it only sees the name, description, and
parameter schema you provide. A tool that does something powerful and correct internally is
useless to an agent if its description is vague ("handles orders") rather than specific ("looks
up shipping status, ETA, and delay reason for an order by ID"). Writing a good tool description
is a prompt engineering task, not just an API documentation task.

```python
# Vague -- the model can't tell when to use this vs. other order tools
{"name": "order_tool", "description": "Does stuff with orders."}

# Specific -- the model can clearly distinguish this from, say, a
# cancel_order or update_shipping_address tool
{"name": "get_order_status", "description": "Retrieve the current shipping status, ETA, and any known delay reason for a customer order. Use this when the user asks about order tracking or delivery timing."}
```

## Designing parameter schemas that reduce errors

Prefer simple, well-typed, well-described parameters over complex nested structures the model
is more likely to get wrong.

```python
# Error-prone: model has to correctly nest a complex object
{"filters": {"type": "object", "properties": {"date_range": {"type": "object", "properties": {"start": {}, "end": {}}}}}}

# More reliable: flat, explicit, individually described parameters
{
    "start_date": {"type": "string", "description": "ISO 8601 date, e.g. '2026-09-01'."},
    "end_date": {"type": "string", "description": "ISO 8601 date, e.g. '2026-09-30'."},
}
```

Enumerated string parameters (`"enum": ["pending", "shipped", "delivered", "cancelled"]`) are
especially valuable when a parameter has a small, fixed set of valid values -- they eliminate an
entire category of invalid-argument errors compared to a free-form string.

## Common tool design mistakes

- **Overlapping tools with unclear boundaries** -- two tools that both "look up order
  information" but differ in some subtle way the model can't infer from the descriptions alone.
- **Tools that do too much** -- a single tool that both looks up data and takes an irreversible
  action (like `process_refund_or_lookup_order`) makes it harder for the model to reason about
  when it's safe to call, and harder for you to add guardrails around the risky half.
- **Missing error guidance** -- not describing what the tool returns when it fails (empty
  result? error message? exception?), leaving the model to guess how to interpret an unexpected
  response.
- **Parameter names that don't match natural language** -- a parameter called `oid` instead of
  `order_id` forces the model to make an extra inferential leap that increases error rate for no
  benefit.

## Tool design as an iterative, measured process

Just like chunking or retrieval tuning in the RAG course, tool definitions benefit from
measurement: log how often the model selects the wrong tool, passes malformed arguments, or
fails to discover a tool that would have helped -- then revise names, descriptions, and schemas
based on those observed failures rather than guessing at the ideal design up front.
""",
                    "examples": [
                        {
                            "title": "Before and after a confusing tool description",
                            "code": (
                                "# Before: model frequently confuses this with a similar 'update_order' tool\n"
                                "{\"name\": \"modify_order\", \"description\": \"Modifies an order.\"}\n"
                                "\n"
                                "# After: explicit about scope and when to use it\n"
                                "{\"name\": \"update_shipping_address\", \"description\": \"Updates ONLY the shipping address on an order that has not yet shipped. Does not modify items, quantities, or payment.\"}"
                            ),
                            "explanation": "Narrowing both the name and description to describe exactly one specific capability eliminates the ambiguity that caused misselection.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Take a vague tool description ('handles customer data') and rewrite it into a specific, well-scoped tool definition with name, description, and parameter schema.",
                            "difficulty": "easy",
                            "hint": "Decide exactly what the tool does and doesn't do, and make that boundary explicit in the description.",
                        },
                        {
                            "prompt": "Design two tools, cancel_order and get_order_status, with descriptions specific enough that a model would never confuse which one to call for a 'is my order still coming' question versus a 'I want to cancel' request.",
                            "difficulty": "medium",
                            "hint": "Emphasize the read-only vs. action-taking distinction explicitly in each description.",
                        },
                        {
                            "prompt": "Identify one enum-appropriate parameter in a tool you've designed and rewrite it from a free-form string to a constrained enum, explaining what error category this eliminates.",
                            "difficulty": "easy",
                            "hint": "Look for any parameter with a small, known set of valid values, like a status or category field.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: tool use best practices",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/tool-use/overview",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tools", "weight": 1.0}],
                },
                {
                    "slug": "building-a-tool-registry",
                    "title": "Building a Tool Registry",
                    "description": "Implement a reusable registry that stores tool definitions and their implementations together, ready to hand to an agent loop.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a tool registry that pairs a callable with its schema",
                        "Generate a tool's schema automatically from a Python function's type hints and docstring",
                        "Validate tool arguments before execution to catch errors early",
                        "Handle tool execution errors without crashing the agent loop",
                    ],
                    "content_markdown": """
## Why this matters

Every example so far in this course has hand-written tool schemas alongside their
implementations, which is error-prone once you have more than a handful of tools -- the schema
and the actual function signature can silently drift apart. A tool registry keeps them coupled
and adds the validation and error handling a real agent loop needs.

## A simple registry class

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class Tool:
    name: str
    description: str
    parameters: dict
    function: Callable

class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register(self, tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_schemas(self) -> list[dict]:
        return [{"name": t.name, "description": t.description, "parameters": t.parameters} for t in self._tools.values()]

    def execute(self, name: str, arguments: dict):
        if name not in self._tools:
            raise ValueError(f"Unknown tool: {name}")
        return self._tools[name].function(**arguments)
```

## Generating schemas from function signatures

Writing JSON schemas by hand for every tool is tedious and error-prone. Deriving them from
Python type hints keeps the schema and implementation in sync automatically.

```python
import inspect
from typing import get_type_hints

TYPE_MAP = {str: "string", int: "integer", float: "number", bool: "boolean"}

def tool_from_function(func: Callable, description: str) -> Tool:
    signature = inspect.signature(func)
    hints = get_type_hints(func)
    properties, required = {}, []

    for param_name, param in signature.parameters.items():
        param_type = TYPE_MAP.get(hints.get(param_name, str), "string")
        properties[param_name] = {"type": param_type}
        if param.default is inspect.Parameter.empty:
            required.append(param_name)

    return Tool(
        name=func.__name__,
        description=description,
        parameters={"type": "object", "properties": properties, "required": required},
        function=func,
    )

def get_order_status(order_id: str) -> dict:
    return {"order_id": order_id, "status": "delayed"}

order_status_tool = tool_from_function(get_order_status, "Look up the current shipping status of an order by ID.")
```

Notice this approach still requires a hand-written `description` -- there's no way to
auto-generate the kind of specific, model-facing explanation from the previous lesson purely
from a function signature, so that part remains a deliberate design decision.

## Validating arguments before execution

```python
def validate_arguments(tool: Tool, arguments: dict) -> list[str]:
    errors = []
    required = tool.parameters.get("required", [])
    for field in required:
        if field not in arguments:
            errors.append(f"Missing required argument: {field}")
    for key in arguments:
        if key not in tool.parameters.get("properties", {}):
            errors.append(f"Unexpected argument: {key}")
    return errors
```

Catching a missing or unexpected argument *before* calling the underlying function turns a
confusing runtime exception (a Python `TypeError` from a mismatched function call) into a clear,
structured error the agent loop can feed back to the model as an observation -- letting the
model correct itself on the next iteration rather than crashing the whole agent.

## Wiring validation and error handling into execution

```python
class ToolRegistry:
    # ... register() and get_schemas() as before ...

    def execute(self, name: str, arguments: dict) -> dict:
        if name not in self._tools:
            return {"error": f"Unknown tool: {name}"}
        tool = self._tools[name]
        errors = validate_arguments(tool, arguments)
        if errors:
            return {"error": f"Invalid arguments: {'; '.join(errors)}"}
        try:
            return {"result": tool.function(**arguments)}
        except Exception as exc:
            return {"error": f"Tool execution failed: {exc}"}
```

Returning a structured `{"error": ...}` or `{"result": ...}` dict, rather than letting an
exception propagate, means the agent loop always gets *something* it can pass back as an
observation -- keeping the observe-reason-act cycle alive even when a single tool call fails.
""",
                    "examples": [
                        {
                            "title": "Registering and executing a tool end to end",
                            "code": (
                                "registry = ToolRegistry()\n"
                                "registry.register(tool_from_function(get_order_status, \"Look up shipping status by order ID.\"))\n"
                                "\n"
                                "print(registry.execute(\"get_order_status\", {\"order_id\": \"4521\"}))\n"
                                "# {'result': {'order_id': '4521', 'status': 'delayed'}}\n"
                                "print(registry.execute(\"get_order_status\", {}))\n"
                                "# {'error': 'Invalid arguments: Missing required argument: order_id'}"
                            ),
                            "explanation": "The registry turns both success and failure into a consistent, structured shape the agent loop can always handle the same way.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a second tool to the registry with an optional parameter (a default value), and confirm validate_arguments correctly does NOT flag it as missing when omitted.",
                            "difficulty": "medium",
                            "hint": "Check inspect.Parameter.default in tool_from_function to correctly exclude optional params from 'required'.",
                        },
                        {
                            "prompt": "Extend tool_from_function to also support enum parameters by reading a custom decorator or docstring convention of your design, and explain your design choice.",
                            "difficulty": "hard",
                            "hint": "Python type hints alone can't express 'one of these 3 strings' -- you'll need some additional metadata source.",
                        },
                        {
                            "prompt": "Write a test confirming that calling registry.execute with a tool name that doesn't exist returns a structured error rather than raising an exception.",
                            "difficulty": "easy",
                            "hint": "assert 'error' in registry.execute('nonexistent_tool', {}).",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Python inspect module documentation",
                            "url": "https://docs.python.org/3/library/inspect.html",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tools", "weight": 1.0}, {"slug": "python", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "tool-calling",
            "title": "Tool Calling",
            "description": "Using a model provider's native tool-calling API for structured, reliable tool invocation instead of manual text parsing.",
            "order_index": 6,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "native-tool-calling-apis",
                    "title": "Native Tool Calling APIs",
                    "description": "Understand how model providers implement tool calling under the hood and why it's more reliable than manual parsing.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain how native tool calling differs from the manual ReAct parsing approach",
                        "Describe the request/response shape of a tool-calling API call",
                        "Identify why native tool calling reduces parsing errors compared to free-text parsing",
                        "Recognize that tool calling is still probabilistic, not guaranteed-correct",
                    ],
                    "content_markdown": """
## Why this matters

The ReAct implementation from Module 4 parsed tool calls out of free-text model output with
regex -- functional, but fragile. Every major model provider now offers a **native tool calling**
API that handles this parsing internally and returns a structured, guaranteed-parseable
response, which is what nearly every production agent system uses instead of manual parsing.

## How native tool calling works

You pass the model a list of available tool schemas alongside your messages; the model can
choose to respond with regular text, or with a structured tool call request that your code
executes and feeds back.

```python
tools = [
    {
        "name": "get_order_status",
        "description": "Retrieve the current shipping status of an order by ID.",
        "input_schema": {
            "type": "object",
            "properties": {"order_id": {"type": "string"}},
            "required": ["order_id"],
        },
    }
]

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[{"role": "user", "content": "Is order 4521 delayed?"}],
)
```

## The structured response shape

```python
for block in response.content:
    if block.type == "tool_use":
        print(block.name, block.input, block.id)
        # 'get_order_status' {'order_id': '4521'} 'toolu_01A...'
    elif block.type == "text":
        print(block.text)
```

The model returns a `tool_use` content block with the tool name and arguments already parsed
into a proper dictionary -- no regex, no JSON parsing of free text, no risk of the model writing
`Action: get_order_status(order_id="4521")` in a slightly different format than you expected.

## Feeding the result back

```python
tool_result = get_order_status(order_id="4521")

follow_up = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1024,
    tools=tools,
    messages=[
        {"role": "user", "content": "Is order 4521 delayed?"},
        {"role": "assistant", "content": response.content},
        {"role": "user", "content": [
            {"type": "tool_result", "tool_use_id": block.id, "content": str(tool_result)}
        ]},
    ],
)
```

The `tool_use_id` links a tool result back to the specific tool call that requested it -- this
matters when a model requests multiple tool calls in one response, so each result is
unambiguously matched to its request.

## Why this is more reliable than manual parsing

Providers train and fine-tune their models specifically to reliably emit well-formed tool call
requests in this structured format, and the API layer guarantees you receive valid JSON
arguments (matching your declared schema) rather than free text that might or might not parse
correctly. This eliminates the entire `malformed` failure branch from the manual ReAct
implementation in Module 4 -- not because the model is smarter, but because the interface is
narrower and provider-optimized specifically for this purpose.

## Still probabilistic, not guaranteed-correct

Native tool calling guarantees *well-formed* output -- valid JSON matching your schema -- but it
does not guarantee the model chose the *right* tool, or supplied *correct* argument values. A
model can still confidently call `get_order_status(order_id="4521")` when the user actually
asked about order 5421, or call the wrong tool entirely for an ambiguous request. Tool calling
solves the parsing reliability problem; it does not solve the decision-quality problem, which is
still governed by prompt quality, tool description quality (Module 5), and techniques like ReAct
(Module 4).
""",
                    "examples": [
                        {
                            "title": "Multiple tool calls in one response",
                            "code": (
                                "# A model might request two independent tool calls in a single turn:\n"
                                "# [tool_use: get_order_status(order_id='4521'),\n"
                                "#  tool_use: get_order_status(order_id='4522')]\n"
                                "# Each has its own tool_use_id -- your code must execute both and\n"
                                "# return two separate tool_result blocks, each referencing the\n"
                                "# matching tool_use_id, before the model can continue"
                            ),
                            "explanation": "Parallel tool calls are a real capability of native tool calling APIs that a naive one-call-at-a-time regex-based ReAct loop wouldn't handle without extra work.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Compare the manual parse_react_step function from Module 4 against native tool calling, listing 3 specific failure modes native tool calling eliminates.",
                            "difficulty": "easy",
                            "hint": "Revisit the 'malformed' branch and JSON parsing errors from the earlier ReAct implementation.",
                        },
                        {
                            "prompt": "Make a real tool-calling API call (or write out the full request/response pair) for a tool with two required parameters, and trace through what happens if the model omits one.",
                            "difficulty": "medium",
                            "hint": "Most providers return an error or a request for clarification rather than an invalid tool_use block -- check your provider's documentation.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: tool use documentation",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/tool-use/overview",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 1.0}],
                },
                {
                    "slug": "building-a-tool-calling-agent-loop",
                    "title": "Building a Tool-Calling Agent Loop",
                    "description": "Replace the manual ReAct parser with a native tool-calling loop, handling multi-turn conversations and parallel tool calls.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement an agent loop using a native tool-calling API",
                        "Handle multiple tool calls requested in a single model turn",
                        "Correctly maintain conversation history across tool call/result pairs",
                        "Compare code complexity against the manual ReAct parsing implementation",
                    ],
                    "content_markdown": """
## Why this matters

This lesson rebuilds the Module 4 ReAct agent using native tool calling, so you can directly
compare the two approaches side by side and see exactly how much complexity a provider's tool
calling API removes.

## The tool-calling agent loop

```python
def tool_calling_agent(goal: str, registry: ToolRegistry, client, max_iterations: int = 8) -> dict:
    messages = [{"role": "user", "content": goal}]
    tool_schemas = registry.get_schemas()

    for iteration in range(max_iterations):
        response = client.messages.create(
            model="claude-sonnet-4-5",
            max_tokens=1024,
            tools=tool_schemas,
            messages=messages,
        )

        if response.stop_reason != "tool_use":
            final_text = "".join(b.text for b in response.content if b.type == "text")
            return {"status": "success", "answer": final_text, "iterations": iteration + 1}

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                outcome = registry.execute(block.name, block.input)
                tool_results.append({"type": "tool_result", "tool_use_id": block.id, "content": str(outcome)})
        messages.append({"role": "user", "content": tool_results})

    return {"status": "max_iterations_reached", "answer": None, "iterations": max_iterations}
```

Notice `response.stop_reason != "tool_use"` is the loop's termination check -- the API tells you
explicitly whether the model wants to call a tool or has produced its final response, replacing
the `is_final_answer` heuristic from earlier, manually-parsed implementations with a reliable,
provider-guaranteed signal.

## Handling multiple tool calls in one turn

The `for block in response.content` loop above already handles this correctly: if the model
requests two tool calls in a single response, both get executed and both results get appended
to the same `tool_results` list before the next API call. This is meaningfully simpler than
handling parallel actions in a manually-parsed ReAct loop, which would need custom logic to
detect and split multiple actions out of one block of free text.

```python
# A model turn requesting 2 parallel tool calls is handled by the SAME
# code path as a turn requesting 1 -- the loop over response.content
# naturally scales to however many tool_use blocks are present
```

## Maintaining conversation history correctly

The most common bug in a first tool-calling implementation is mismatched history: forgetting to
append the assistant's tool-call turn before appending the tool results, or forgetting a
`tool_use_id` on a result. Both cause the next API call to fail or behave unpredictably, because
the provider expects a strict alternating structure: assistant tool-call turn, followed
immediately by a user turn containing matching tool results.

```python
# Correct order:
# 1. messages.append({"role": "assistant", "content": response.content})  # the tool_use blocks
# 2. messages.append({"role": "user", "content": tool_results})           # matching tool_result blocks
# Reversing this order, or omitting step 1, will cause the next API call to fail
```

## Comparing complexity against manual ReAct

```python
# Manual ReAct (Module 4): needed parse_react_step, regex parsing,
# a "malformed" retry branch, and a stop=["Observation:"] hack to
# prevent hallucinated observations
#
# Native tool calling: no parsing code at all -- the API guarantees
# well-formed tool_use blocks, and stop_reason tells you definitively
# whether the model wants to act or has finished
```

For any production system, native tool calling is almost always the right choice over manual
ReAct parsing -- but having built the manual version first means you understand exactly what
capability you're relying on the provider for, rather than treating it as an opaque black box.
""",
                    "examples": [
                        {
                            "title": "A single call requesting two tools in parallel",
                            "code": (
                                "goal = \"Check the status of orders 4521 and 4522.\"\n"
                                "result = tool_calling_agent(goal, registry, client)\n"
                                "# response.content likely contains two tool_use blocks in one turn;\n"
                                "# both get executed and returned before the model's next turn,\n"
                                "# completing the task in fewer iterations than a strictly\n"
                                "# one-action-per-turn loop would require"
                            ),
                            "explanation": "Parallel tool calling can meaningfully reduce the number of loop iterations (and therefore latency) needed to complete multi-part tasks.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement tool_calling_agent against a real or stubbed client and confirm it correctly terminates with status 'success' when the model responds with text and no tool_use blocks.",
                            "difficulty": "medium",
                            "hint": "Stub client.messages.create to return a fake response object with stop_reason='end_turn' and a text content block.",
                        },
                        {
                            "prompt": "Deliberately break the message history ordering (append tool_results before the assistant turn) and describe what error or unexpected behavior you'd expect from the API.",
                            "difficulty": "medium",
                            "hint": "Most providers will reject the request or return an error about a missing corresponding tool_use.",
                        },
                        {
                            "prompt": "Extend tool_calling_agent to log, for each iteration, how many tool calls were requested in parallel, and run it against a task that requires checking 3 independent things.",
                            "difficulty": "hard",
                            "hint": "Count response.content blocks with type == 'tool_use' per iteration.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: multi-turn tool use and conversation structure",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/tool-use/implement-tool-use",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "function-calling",
            "title": "Function Calling",
            "description": "Mapping tool-calling requests onto real Python functions safely, including validation, sandboxing, and error propagation.",
            "order_index": 7,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "from-tool-call-to-function-execution",
                    "title": "From Tool Call to Function Execution",
                    "description": "Understand the full path from a model's tool call request to a safely-executed Python function and back.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Trace the full path from tool call request to function execution and back",
                        "Distinguish 'tool calling' (the model-facing API) from 'function calling' (your code executing it)",
                        "Identify the safety risks of executing model-requested function calls without validation",
                        "Explain why side-effecting functions need stronger guardrails than read-only ones",
                    ],
                    "content_markdown": """
## Why this matters

"Tool calling" and "function calling" are often used interchangeably, but it's worth separating
them precisely: tool calling is the model-facing protocol (what Module 6 covered); function
calling is what your code does on the receiving end -- taking a tool call request and safely
executing the actual Python function it maps to. This module focuses on that execution side.

## The full round trip

```python
# 1. You declare a tool schema the model can request
# 2. The model responds with a tool_use block: name="get_order_status", input={"order_id": "4521"}
# 3. YOUR CODE maps that name to an actual Python function and calls it -- this step is "function calling"
# 4. The function's return value becomes the tool_result sent back to the model

def dispatch_function_call(tool_name: str, arguments: dict, registry: ToolRegistry):
    return registry.execute(tool_name, arguments)  # from the Tools module
```

The model never directly executes anything -- it only ever *requests* an action by name and
arguments. Your code is entirely responsible for deciding whether and how to actually run
something in response to that request, which is precisely where safety considerations enter.

## Why unvalidated execution is dangerous

A tool call request is, structurally, just data the model generated -- and like any
model-generated content, it should not be blindly trusted, especially for anything with real
side effects. Directly evaluating or executing whatever the model requests without validation
opens the door to the model (whether through a reasoning error or a prompt injection attack via
retrieved content) requesting a destructive or unintended action.

```python
# Dangerous: no validation of which function or what arguments are allowed
def unsafe_dispatch(tool_name: str, arguments: dict):
    function = globals()[tool_name]  # NEVER do this -- allows calling ANY function in scope
    return function(**arguments)

# Safer: only functions explicitly registered as tools can ever be called,
# and only with arguments matching a declared, validated schema
def safe_dispatch(tool_name: str, arguments: dict, registry: ToolRegistry):
    return registry.execute(tool_name, arguments)  # registry enforces an explicit allowlist
```

The `ToolRegistry` from Module 5 already provides this safety property structurally: a model can
only ever request tools that were explicitly registered, with arguments validated against a
declared schema -- never arbitrary code execution.

## Read-only vs. side-effecting functions need different guardrails

A function like `get_order_status` is read-only -- calling it incorrectly wastes a bit of time
and cost, but causes no lasting harm, and it's generally safe to let an agent call repeatedly
during its reasoning process. A function like `issue_refund` or `send_email` has a real,
possibly irreversible side effect -- calling it incorrectly could cost real money or damage user
trust.

```python
REFUND_TOOL = {
    "name": "issue_refund",
    "description": "Issues a refund for an order. This is IRREVERSIBLE. Only call this after confirming the order is refund-eligible via check_refund_eligibility.",
    "parameters": {"type": "object", "properties": {"order_id": {"type": "string"}, "amount": {"type": "number"}}, "required": ["order_id", "amount"]},
}
```

Side-effecting tools deserve extra guardrails beyond schema validation: confirmation steps,
human-in-the-loop approval for high-value actions, dollar or rate limits, and audit logging of
every invocation -- covered hands-on in the next lesson.

## A mental model for the trust boundary

Treat every tool call request from the model the same way you'd treat input from an untrusted
user in a traditional web application: validate it, authorize it against what that specific
action is allowed to do, and log it -- never assume that because a model "decided" to call a
function, that decision is automatically safe to execute as-is.
""",
                    "examples": [
                        {
                            "title": "Tool calling vs. function calling, side by side",
                            "code": (
                                "# TOOL CALLING (Module 6): the model-facing protocol\n"
                                "# response.content -> [tool_use(name='issue_refund', input={'order_id': '4521', 'amount': 49.99})]\n"
                                "\n"
                                "# FUNCTION CALLING (this module): your code deciding what to actually do with that request\n"
                                "if requires_approval(tool_name, arguments):\n"
                                "    queue_for_human_review(tool_name, arguments)\n"
                                "else:\n"
                                "    result = registry.execute(tool_name, arguments)"
                            ),
                            "explanation": "The model only produces the request; your function-calling layer decides whether, and how, that request actually gets executed -- that decision layer is this module's focus.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List 3 tools from a hypothetical customer support agent, classify each as read-only or side-effecting, and propose one specific guardrail for each side-effecting tool.",
                            "difficulty": "easy",
                            "hint": "Consider a lookup tool, an update tool, and a cancellation or refund tool.",
                        },
                        {
                            "prompt": "Explain, in your own words, why globals()[tool_name] is dangerous even if you trust the model provider completely.",
                            "difficulty": "medium",
                            "hint": "Consider prompt injection: if a retrieved document contains text designed to manipulate the model into requesting an unintended function name.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "OWASP: LLM excessive agency risks",
                            "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications/",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 0.8}, {"slug": "agents", "weight": 0.4}],
                },
                {
                    "slug": "safe-function-execution-with-guardrails",
                    "title": "Safe Function Execution with Guardrails",
                    "description": "Implement confirmation steps, rate limits, and audit logging for side-effecting tool calls.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a human-in-the-loop confirmation step for high-risk tool calls",
                        "Add rate limiting to prevent runaway or repeated side-effecting actions",
                        "Log every tool execution for auditability",
                        "Design a risk classification scheme for tools that determines which guardrails apply",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson made the case for extra guardrails on side-effecting tools; this lesson
implements them. These patterns are exactly what separates a demo agent from one you'd trust
with real user data and real money.

## Classifying tool risk

```python
from enum import Enum

class RiskLevel(Enum):
    READ_ONLY = "read_only"
    LOW_RISK_ACTION = "low_risk_action"       # reversible, low-impact
    HIGH_RISK_ACTION = "high_risk_action"     # irreversible or high-impact

TOOL_RISK = {
    "get_order_status": RiskLevel.READ_ONLY,
    "update_shipping_address": RiskLevel.LOW_RISK_ACTION,
    "issue_refund": RiskLevel.HIGH_RISK_ACTION,
}
```

Explicitly classifying every tool by risk, rather than treating them uniformly, is what lets you
apply proportionate guardrails -- heavy friction on `issue_refund`, none on `get_order_status`.

## Human-in-the-loop confirmation for high-risk actions

```python
def dispatch_with_confirmation(tool_name: str, arguments: dict, registry: ToolRegistry) -> dict:
    risk = TOOL_RISK.get(tool_name, RiskLevel.HIGH_RISK_ACTION)  # unknown tools default to high risk

    if risk == RiskLevel.HIGH_RISK_ACTION:
        return {
            "status": "pending_approval",
            "tool_name": tool_name,
            "arguments": arguments,
            "message": f"This action ({tool_name}) requires human approval before execution.",
        }
    return {"status": "executed", "result": registry.execute(tool_name, arguments)}
```

Defaulting unrecognized tools to `HIGH_RISK_ACTION` is a deliberate fail-safe choice: it's far
better for a new or misconfigured tool to require unnecessary approval than to silently execute
with no guardrail at all.

## Rate limiting side-effecting actions

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_calls: int, window_minutes: int):
        self.max_calls = max_calls
        self.window = timedelta(minutes=window_minutes)
        self.call_log: dict[str, list] = defaultdict(list)

    def check_and_record(self, key: str) -> bool:
        now = datetime.now()
        self.call_log[key] = [t for t in self.call_log[key] if now - t < self.window]
        if len(self.call_log[key]) >= self.max_calls:
            return False
        self.call_log[key].append(now)
        return True

refund_limiter = RateLimiter(max_calls=3, window_minutes=60)

def dispatch_refund(order_id: str, amount: float, registry: ToolRegistry) -> dict:
    if not refund_limiter.check_and_record(order_id):
        return {"status": "rate_limited", "message": "Too many refund attempts for this order recently."}
    return dispatch_with_confirmation("issue_refund", {"order_id": order_id, "amount": amount}, registry)
```

Rate limiting per meaningful key (here, per `order_id`) catches both a genuinely stuck agent
loop and a more adversarial scenario where repeated attempts are being deliberately forced.

## Audit logging every execution

```python
import json
import time

def logged_execute(tool_name: str, arguments: dict, registry: ToolRegistry, actor: str = "agent") -> dict:
    outcome = registry.execute(tool_name, arguments)
    log_entry = {
        "timestamp": time.time(),
        "actor": actor,
        "tool_name": tool_name,
        "arguments": arguments,
        "outcome": outcome,
        "risk_level": TOOL_RISK.get(tool_name, RiskLevel.HIGH_RISK_ACTION).value,
    }
    append_to_audit_log(json.dumps(log_entry))
    return outcome
```

An audit log is what lets you answer, after the fact, "which orders did the agent refund this
week, and based on what reasoning?" -- essential for any system with real side effects, and
directly reusable as input to the Reflection module later in this course.

## Putting the guardrails together

```python
def safe_dispatch(tool_name: str, arguments: dict, registry: ToolRegistry) -> dict:
    risk = TOOL_RISK.get(tool_name, RiskLevel.HIGH_RISK_ACTION)
    if risk == RiskLevel.HIGH_RISK_ACTION:
        outcome = dispatch_with_confirmation(tool_name, arguments, registry)
    else:
        outcome = {"status": "executed", "result": registry.execute(tool_name, arguments)}
    log_entry = {"tool_name": tool_name, "arguments": arguments, "outcome": outcome}
    append_to_audit_log(json.dumps(log_entry))
    return outcome
```

This is the version of `execute` you'd actually want in a production agent loop -- every earlier
module's `registry.execute()` call is really shorthand for this full, guarded path.
""",
                    "examples": [
                        {
                            "title": "A refund attempt blocked by two independent guardrails",
                            "code": (
                                "# Attempt 1-3: dispatch_refund succeeds each time (rate limit not yet hit)\n"
                                "#   but each returns status='pending_approval' (high-risk confirmation gate)\n"
                                "# Attempt 4 within the hour: rate_limited, before confirmation is even reached\n"
                                "# Both guardrails are independent -- rate limiting protects against volume,\n"
                                "# confirmation protects against any single wrong action"
                            ),
                            "explanation": "Layering independent guardrails means a failure or gap in one (e.g., a misconfigured risk classification) doesn't leave the system with zero protection.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement dispatch_with_confirmation and RateLimiter, then simulate an agent attempting issue_refund 4 times in quick succession for the same order, confirming the 4th attempt is rate-limited.",
                            "difficulty": "medium",
                            "hint": "Call refund_limiter.check_and_record with the same key 4 times in a loop and check the 4th return value.",
                        },
                        {
                            "prompt": "Design an approval workflow function that takes a pending_approval result and either executes it (on human approval) or discards it (on rejection), logging the outcome either way.",
                            "difficulty": "medium",
                            "hint": "This function would typically be called from a separate human-facing interface, not the agent loop itself.",
                        },
                        {
                            "prompt": "Explain why defaulting unrecognized tools to HIGH_RISK_ACTION in TOOL_RISK.get(tool_name, RiskLevel.HIGH_RISK_ACTION) is safer than defaulting to READ_ONLY, with a concrete failure scenario each choice would cause.",
                            "difficulty": "medium",
                            "hint": "Consider what happens when a new tool is added to the registry but someone forgets to add it to TOOL_RISK.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: agent safety and human oversight patterns",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 0.8}, {"slug": "agents", "weight": 0.5}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "structured-outputs",
            "title": "Structured Outputs",
            "description": "Forcing model output into a strict, parseable schema so agent decisions can be reliably consumed by code.",
            "order_index": 8,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "why-agents-need-structured-outputs",
                    "title": "Why Agents Need Structured Outputs",
                    "description": "Understand the gap between free-text generation and the strict data shapes downstream code requires.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why free-text output is unreliable as an interface between model and code",
                        "Describe how JSON schema-constrained generation works at a conceptual level",
                        "Distinguish schema validation from prompt-based formatting instructions",
                        "Identify where structured outputs fit in agent decision-making beyond tool calls",
                    ],
                    "content_markdown": """
## Why this matters

Tool calling (Module 6) is really a specialized case of a more general problem: whenever an
agent's output needs to be consumed by code rather than read by a human, free-text generation is
an unreliable interface. Structured outputs solve this generally, for tool arguments and for
every other place an agent needs to hand structured data to the rest of your system.

## The reliability gap in free-text generation

Asking a model to "respond in JSON" as a prompt instruction produces JSON most of the time --
but "most of the time" is not good enough for code that will call `json.loads()` on the result
without a try/except and act on it directly.

```python
# Prompt-only formatting: NOT guaranteed to be valid JSON
prompt = "Classify this support ticket. Respond in JSON with fields 'category' and 'urgency'."
raw = llm.generate(prompt)
data = json.loads(raw)  # can raise json.JSONDecodeError if the model adds
                          # explanatory text before/after the JSON, or
                          # produces almost-valid-but-not-quite JSON
```

Common failure patterns: the model wraps the JSON in a markdown code fence, adds a sentence of
explanation before or after, uses single quotes instead of double quotes, or omits a required
field entirely -- none of which a plain prompt instruction reliably prevents.

## Schema-constrained generation

Modern model APIs offer a stronger guarantee: rather than just *asking* for JSON, you provide a
formal schema, and the API constrains the model's token generation so that only schema-valid
output is possible in the first place.

```python
TICKET_CLASSIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "category": {"type": "string", "enum": ["billing", "technical", "account", "other"]},
        "urgency": {"type": "string", "enum": ["low", "medium", "high"]},
        "summary": {"type": "string"},
    },
    "required": ["category", "urgency", "summary"],
}

response = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=500,
    tools=[{"name": "classify_ticket", "description": "Classify a support ticket.", "input_schema": TICKET_CLASSIFICATION_SCHEMA}],
    tool_choice={"type": "tool", "name": "classify_ticket"},
    messages=[{"role": "user", "content": ticket_text}],
)
classification = response.content[0].input  # guaranteed to match the schema
```

Using a tool definition purely to force structured output (`tool_choice` forcing exactly that
one "tool") is a common and effective pattern, even when the "tool" doesn't actually do
anything -- its schema is being used as a structured output contract, not an executable action.

## Schema validation vs. prompt-based formatting

Prompt-based formatting ("respond in JSON with these fields") is a *request*; schema-constrained
generation is a *guarantee* enforced by the API itself during token generation. The distinction
matters enormously for production reliability: code downstream of a prompt-only approach needs
defensive error handling for malformed output on every single call, while code downstream of
true schema-constrained generation can trust the shape of what it receives.

## Where structured outputs matter beyond tool arguments

This isn't only relevant to tool calling. Any time an agent needs to hand off a decision to
code -- routing logic (Module 13), a plan represented as a list of steps (Planning module), a
self-critique with a pass/fail verdict (Reflection module) -- structured outputs are the
mechanism that makes that handoff reliable. You'll see this exact schema-constrained-generation
pattern reused throughout the rest of this course, not just for literal tool calls.

## The cost of over-constraining

Very rigid schemas can sometimes make it harder for a model to express genuinely necessary
nuance -- an overly narrow enum might force a classification that doesn't quite fit any option.
Design schemas that are strict where correctness matters (a fixed enum for a routing decision)
but leave room for open text where nuance matters (a free-text `summary` or `reasoning` field
alongside the structured fields), rather than forcing every single piece of output into rigid
categories.
""",
                    "examples": [
                        {
                            "title": "A prompt-only failure schema-constrained generation prevents",
                            "code": (
                                "# Prompt-only output that breaks json.loads():\n"
                                "raw = 'Sure! Here is the classification:\\n```json\\n{\"category\": \"billing\"}\\n```'\n"
                                "# json.loads(raw) raises JSONDecodeError -- the code fence and\n"
                                "# preamble text are not valid JSON on their own\n"
                                "\n"
                                "# Schema-constrained generation guarantees response.content[0].input\n"
                                "# is ALREADY a parsed dict matching TICKET_CLASSIFICATION_SCHEMA --\n"
                                "# no fence, no preamble, no parsing step needed at all"
                            ),
                            "explanation": "This exact failure pattern -- a model wrapping JSON in conversational text or markdown -- is one of the most common bugs in early LLM-integration code, and schema-constrained generation eliminates it structurally rather than requiring ever-more-defensive parsing code.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a JSON schema for classifying an email as 'spam', 'important', or 'newsletter' with a confidence score between 0 and 1, using appropriate JSON schema types and constraints.",
                            "difficulty": "easy",
                            "hint": "Use 'enum' for the category and a 'number' type with minimum/maximum for the confidence score.",
                        },
                        {
                            "prompt": "Take a prompt-only formatting instruction you've seen produce malformed output, and rewrite it as a schema-constrained tool-choice call, explaining what specifically changed about the reliability guarantee.",
                            "difficulty": "medium",
                            "hint": "Contrast 'the model is asked to' versus 'the API constrains the model to.'",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: forcing tool use for structured output",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/tool-use/implement-tool-use#forcing-tool-use",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 0.7}, {"slug": "agents", "weight": 0.4}],
                },
                {
                    "slug": "validating-and-repairing-structured-output",
                    "title": "Validating and Repairing Structured Output",
                    "description": "Add a validation layer with Pydantic and a repair loop for the rare cases where structured output still fails.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Define and validate structured output schemas using Pydantic",
                        "Implement a repair loop that asks the model to fix invalid output",
                        "Distinguish schema-level validity from semantic correctness",
                        "Design fallback behavior for output that fails validation after repair attempts",
                    ],
                    "content_markdown": """
## Why this matters

Even with schema-constrained generation, you'll sometimes need an extra layer of validation --
for business rules a JSON schema can't express (like "urgency must be 'high' if category is
'security'"), or for providers/models that don't support hard schema constraints. This lesson
builds that validation and repair layer.

## Defining schemas with Pydantic

```python
from pydantic import BaseModel, Field, field_validator
from typing import Literal

class TicketClassification(BaseModel):
    category: Literal["billing", "technical", "account", "security", "other"]
    urgency: Literal["low", "medium", "high"]
    summary: str = Field(min_length=10, max_length=200)

    @field_validator("urgency")
    @classmethod
    def security_must_be_high_urgency(cls, urgency, info):
        if info.data.get("category") == "security" and urgency != "high":
            raise ValueError("security category must have high urgency")
        return urgency
```

Pydantic validators let you express business rules a raw JSON schema can't, like the
cross-field constraint here -- this is exactly the kind of semantic correctness check that
schema-constrained generation alone doesn't cover.

## Validating model output

```python
import json
from pydantic import ValidationError

def validate_classification(raw_output: dict) -> dict:
    try:
        validated = TicketClassification.model_validate(raw_output)
        return {"valid": True, "data": validated.model_dump()}
    except ValidationError as exc:
        return {"valid": False, "errors": exc.errors()}
```

## A repair loop for invalid output

Rather than immediately failing on invalid output, ask the model to fix its own mistake, showing
it exactly what went wrong.

```python
def classify_with_repair(ticket_text: str, llm, max_repair_attempts: int = 2) -> dict:
    prompt = f"Classify this ticket: {ticket_text}"
    for attempt in range(max_repair_attempts + 1):
        raw_output = generate_structured(prompt, schema=TICKET_CLASSIFICATION_SCHEMA, llm=llm)
        result = validate_classification(raw_output)
        if result["valid"]:
            return {"status": "success", "data": result["data"], "attempts": attempt + 1}

        prompt = (
            f"Classify this ticket: {ticket_text}\\n\\n"
            f"Your previous attempt was invalid: {result['errors']}\\n"
            "Please correct it and try again."
        )
    return {"status": "failed_validation", "data": None, "attempts": max_repair_attempts + 1}
```

Feeding the specific validation error back to the model, rather than just retrying blindly, is
what makes repair attempts likely to succeed -- the model can directly see and address exactly
what was wrong, the same principle behind Reflection (a later module in this course).

## Schema validity vs. semantic correctness

Passing Pydantic validation means the output has the right *shape* and satisfies any rules
you've encoded -- it does not mean the classification is *correct*. A ticket could be validly
formatted as `{"category": "technical", "urgency": "low"}` while a human reviewer would say it's
actually `"billing"` and `"high"`. Validation catches structural and rule-based errors; it
cannot catch a well-formed but substantively wrong judgment call, which is a generation-quality
problem, not a validation problem.

## Designing fallback behavior

```python
def classify_ticket_safely(ticket_text: str, llm) -> dict:
    result = classify_with_repair(ticket_text, llm)
    if result["status"] == "success":
        return result["data"]
    return {"category": "other", "urgency": "medium", "summary": "Needs manual review: automatic classification failed."}
```

A safe default (route to human review, or a conservative "medium" urgency bucket) is essential
for the rare case where repair attempts are exhausted and validation still fails -- the system
should degrade gracefully, never crash or silently pass through unvalidated data to whatever
consumes the classification next.
""",
                    "examples": [
                        {
                            "title": "A repair attempt fixing a business-rule violation",
                            "code": (
                                "# Attempt 1: {'category': 'security', 'urgency': 'low', 'summary': 'Login page shows odd behavior after update'}\n"
                                "# Fails validation: security_must_be_high_urgency rule violated\n"
                                "# Repair prompt includes the specific error message\n"
                                "# Attempt 2: {'category': 'security', 'urgency': 'high', 'summary': 'Login page shows odd behavior after update'}\n"
                                "# Passes validation -- the model corrected the exact issue it was shown"
                            ),
                            "explanation": "This is the repair loop working as intended: a specific, actionable error message led directly to a corrected second attempt.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define a Pydantic model for a 'meeting_request' structured output with fields for title, duration_minutes (between 15 and 240), and attendee_emails (a list), and write 2 test cases: one valid, one that should fail validation.",
                            "difficulty": "medium",
                            "hint": "Use Field(ge=15, le=240) for the duration constraint.",
                        },
                        {
                            "prompt": "Implement classify_with_repair with a stubbed LLM that fails validation on its first attempt and succeeds on its second, and confirm the function returns status 'success' with attempts=2.",
                            "difficulty": "medium",
                            "hint": "Have your stub track a call counter and return different (invalid, then valid) output based on the count.",
                        },
                        {
                            "prompt": "Explain, with an example, a case where output could pass Pydantic validation but still be semantically wrong, and discuss what kind of check (not validation) would be needed to catch it.",
                            "difficulty": "hard",
                            "hint": "Consider the Reflection or Evaluation-style checks needed for judgment quality, not structural correctness.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Pydantic: validators documentation",
                            "url": "https://docs.pydantic.dev/latest/concepts/validators/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "tool-calling", "weight": 0.7}, {"slug": "python", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "agent-state",
            "title": "Agent State",
            "description": "Modeling what an agent needs to remember and track as it works through a multi-step task.",
            "order_index": 9,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "modeling-state-across-agent-steps",
                    "title": "Modeling State Across Agent Steps",
                    "description": "Design a state object that captures everything an agent needs to carry between iterations of its loop.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain what 'state' means in the context of a multi-step agent",
                        "Identify the categories of information a well-designed agent state typically tracks",
                        "Distinguish conversation history from derived, structured state",
                        "Recognize the risk of unbounded state growth in long-running agent loops",
                    ],
                    "content_markdown": """
## Why this matters

Every agent loop example so far in this course has quietly relied on some form of state -- the
growing `observations` list, the `messages` array passed to each API call. This module makes
that dependency explicit: what exactly does an agent need to track, and how should it be
structured so the rest of the system (memory, planning, reflection) can build on it reliably.

## What "state" means for an agent

State is everything an agent's next decision depends on beyond the current input: the
conversation so far, results of previous tool calls, any plan it's following, and any derived
facts it has concluded along the way. Without persisted state, an agent loop would have no way
to avoid repeating already-completed steps or to build on what it has already learned.

```python
from dataclasses import dataclass, field

@dataclass
class AgentState:
    goal: str
    messages: list = field(default_factory=list)      # raw conversation/tool history
    facts: dict = field(default_factory=dict)          # derived, structured knowledge
    completed_actions: list = field(default_factory=list)
    current_step: int = 0
    status: str = "in_progress"                        # in_progress | success | failed
```

## Conversation history vs. derived state

**Conversation history** (`messages`) is the raw, ordered log of everything said and observed --
useful because it's exactly what you pass to the next LLM call, preserving full context.

**Derived state** (`facts`) is structured, extracted knowledge pulled out of that history --
useful because it's queryable and doesn't require re-parsing free text every time you need to
check something.

```python
# Conversation history: unstructured, in order, everything
state.messages.append({"role": "tool", "content": "{'status': 'delayed', 'eta': '2026-09-28'}"})

# Derived state: structured, directly usable by code without re-parsing
state.facts["order_4521_status"] = "delayed"
state.facts["order_4521_eta"] = "2026-09-28"
```

Both matter for different reasons: the LLM call needs conversation history to reason well; your
application code (deciding whether to short-circuit, log a metric, or trigger a downstream
action) often needs derived state instead, since parsing free text on every check is slow and
error-prone.

## Extracting derived facts as the loop progresses

```python
def update_state_from_tool_result(state: AgentState, tool_name: str, tool_args: dict, result: dict) -> None:
    state.messages.append({"role": "tool", "content": str(result)})
    state.completed_actions.append({"tool": tool_name, "args": tool_args})

    if tool_name == "get_order_status" and "result" in result:
        order_id = tool_args["order_id"]
        state.facts[f"order_{order_id}_status"] = result["result"].get("status")
```

Deciding which facts are worth extracting into structured state, versus leaving only in raw
conversation history, is a design choice specific to your agent's task -- extract what later
decisions (routing, planning, reflection) will need to check directly.

## The unbounded growth problem

`messages` grows by at least two entries per loop iteration (the reasoning step and its
observation) -- for a long-running agent working through a complex, many-step task, this can
eventually exceed the model's context window or become expensive to pass on every call. This is
a real constraint you'll need to manage; the Memory module next tackles it directly with
summarization and retrieval strategies for keeping state usable without keeping it unbounded.

## State as the foundation for everything that follows

Planning (representing a multi-step plan), Reflection (critiquing past actions), and Routing
(deciding where to send a task) all depend on state being well-structured and queryable. An
agent that only has a flat, unstructured conversation log to work with will struggle to
implement any of these more advanced capabilities cleanly -- which is exactly why this module
comes before them in the course.
""",
                    "examples": [
                        {
                            "title": "Using derived facts to short-circuit an unnecessary action",
                            "code": (
                                "if f\"order_{order_id}_status\" in state.facts:\n"
                                "    status = state.facts[f\"order_{order_id}_status\"]\n"
                                "    print(f\"Already know order {order_id} status: {status}, skipping redundant lookup\")\n"
                                "else:\n"
                                "    # proceed with a new tool call"
                            ),
                            "explanation": "Checking derived state before taking an action is a concrete way structured state can reduce redundant tool calls -- something raw conversation history alone would require re-parsing to achieve.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design an AgentState dataclass for an agent that researches and summarizes competitor pricing, identifying at least 3 fields beyond messages that belong in derived state.",
                            "difficulty": "medium",
                            "hint": "Think about what facts the agent would want to check without re-reading its entire conversation history.",
                        },
                        {
                            "prompt": "Implement update_state_from_tool_result for two different tools and confirm the correct facts get extracted into state.facts after simulating a 3-step tool call sequence.",
                            "difficulty": "medium",
                            "hint": "Add an if/elif branch per tool name, extracting whatever structured facts are relevant to each.",
                        },
                        {
                            "prompt": "Estimate how many messages a 20-iteration agent loop would accumulate (assuming 2 entries per iteration) and discuss at what point this would likely become a practical problem for a model with a 128K token context window.",
                            "difficulty": "hard",
                            "hint": "Consider both the token count AND the 'lost in the middle' effect from the RAG course's Context Construction module.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: state management concepts",
                            "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#state",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}],
                },
                {
                    "slug": "implementing-a-state-machine-for-agent-tasks",
                    "title": "Implementing a State Machine for Agent Tasks",
                    "description": "Model an agent's task as an explicit state machine with defined transitions, rather than an implicit, unstructured loop.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a simple state machine with explicit states and transitions",
                        "Map agent loop iterations onto state transitions rather than an unstructured loop",
                        "Persist and restore agent state to support resuming an interrupted task",
                        "Explain the benefit of explicit state machines for testing and debugging agents",
                    ],
                    "content_markdown": """
## Why this matters

The `AgentState` dataclass from the previous lesson tracks data, but the loop logic driving it
is still an implicit, unstructured Python loop. Modeling the agent's task explicitly as a state
machine -- with named states and defined transitions -- makes complex agent behavior far easier
to test, debug, and resume than an opaque `while` loop, and is the direct conceptual ancestor of
what LangGraph formalizes in a later course.

## Defining explicit states and transitions

```python
from enum import Enum

class TaskState(Enum):
    STARTED = "started"
    GATHERING_INFO = "gathering_info"
    READY_TO_ANSWER = "ready_to_answer"
    NEEDS_APPROVAL = "needs_approval"
    COMPLETE = "complete"
    FAILED = "failed"

VALID_TRANSITIONS = {
    TaskState.STARTED: {TaskState.GATHERING_INFO, TaskState.FAILED},
    TaskState.GATHERING_INFO: {TaskState.GATHERING_INFO, TaskState.READY_TO_ANSWER, TaskState.FAILED},
    TaskState.READY_TO_ANSWER: {TaskState.NEEDS_APPROVAL, TaskState.COMPLETE},
    TaskState.NEEDS_APPROVAL: {TaskState.COMPLETE, TaskState.FAILED},
}
```

Declaring valid transitions up front means an invalid transition (like jumping straight from
`STARTED` to `COMPLETE`, skipping information gathering) is a detectable bug rather than a
silent logic error buried in loop conditionals.

## A state machine wrapper around the agent loop

```python
@dataclass
class AgentState:
    goal: str
    task_state: TaskState = TaskState.STARTED
    messages: list = field(default_factory=list)
    facts: dict = field(default_factory=dict)

def transition(state: AgentState, new_task_state: TaskState) -> None:
    if new_task_state not in VALID_TRANSITIONS.get(state.task_state, set()):
        raise ValueError(f"Invalid transition: {state.task_state} -> {new_task_state}")
    state.task_state = new_task_state

def run_state_machine_agent(goal: str, tools: dict, llm, max_iterations: int = 10) -> AgentState:
    state = AgentState(goal=goal)
    transition(state, TaskState.GATHERING_INFO)

    for _ in range(max_iterations):
        if state.task_state == TaskState.GATHERING_INFO:
            decision = llm.chat(messages=state.messages, tools=list(tools.values()))
            if decision.is_final_answer:
                transition(state, TaskState.READY_TO_ANSWER)
            else:
                result = tools[decision.tool_name](**decision.tool_args)
                state.messages.append({"role": "tool", "content": str(result)})

        elif state.task_state == TaskState.READY_TO_ANSWER:
            if requires_approval(goal):
                transition(state, TaskState.NEEDS_APPROVAL)
            else:
                transition(state, TaskState.COMPLETE)

        elif state.task_state in (TaskState.COMPLETE, TaskState.NEEDS_APPROVAL, TaskState.FAILED):
            break

    return state
```

## Persisting and resuming state

Because `AgentState` is now an explicit, serializable object rather than implicit loop
variables, you can save it and resume the task later -- essential for anything requiring
human-in-the-loop approval (Module 7's guardrails) or a task that legitimately spans a long time
period.

```python
import json
from dataclasses import asdict

def save_state(state: AgentState, path: str) -> None:
    with open(path, "w") as f:
        json.dump({**asdict(state), "task_state": state.task_state.value}, f)

def load_state(path: str) -> AgentState:
    with open(path) as f:
        data = json.load(f)
    data["task_state"] = TaskState(data["task_state"])
    return AgentState(**data)

# A NEEDS_APPROVAL task can be saved, wait for human review, and resumed
# hours or days later without losing any accumulated context
```

## Why explicit state machines help testing and debugging

With an implicit loop, testing "does the agent correctly handle the approval path" requires
running the entire loop end to end and hoping it reaches that branch. With an explicit state
machine, you can construct an `AgentState` directly in `TaskState.READY_TO_ANSWER` and test the
transition logic for that state in isolation -- much faster and more precise than testing
through the full agent loop every time.

```python
def test_ready_to_answer_transitions_to_approval_for_refunds():
    state = AgentState(goal="refund order 4521", task_state=TaskState.READY_TO_ANSWER)
    transition(state, TaskState.NEEDS_APPROVAL)
    assert state.task_state == TaskState.NEEDS_APPROVAL
```

This testability benefit compounds as agent logic grows more complex -- exactly the problem
LangGraph's graph-based execution model, covered in a later course, is built to solve at scale.
""",
                    "examples": [
                        {
                            "title": "Catching an invalid transition before it causes a silent bug",
                            "code": (
                                "state = AgentState(goal=\"test\", task_state=TaskState.STARTED)\n"
                                "transition(state, TaskState.COMPLETE)\n"
                                "# raises ValueError: Invalid transition: TaskState.STARTED -> TaskState.COMPLETE\n"
                                "# This catches a logic bug immediately, rather than letting the agent\n"
                                "# silently skip the information-gathering phase entirely"
                            ),
                            "explanation": "This is the concrete payoff of explicit transitions -- a bug that would otherwise manifest as a confusing wrong answer instead fails loudly and immediately at the exact point of the mistake.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a new TaskState.RETRYING state that GATHERING_INFO can transition to after 3 failed tool calls, and update VALID_TRANSITIONS accordingly.",
                            "difficulty": "medium",
                            "hint": "Decide which states RETRYING itself should be allowed to transition to -- probably back to GATHERING_INFO or to FAILED.",
                        },
                        {
                            "prompt": "Implement save_state and load_state, then write a test that saves a NEEDS_APPROVAL state, loads it back, and confirms all fields (including the enum) match the original.",
                            "difficulty": "medium",
                            "hint": "Pay special attention to converting the TaskState enum to and from its string value during serialization.",
                        },
                        {
                            "prompt": "Write 2 unit tests for the transition function: one confirming a valid transition succeeds, one confirming an invalid transition raises ValueError, without running the full agent loop.",
                            "difficulty": "easy",
                            "hint": "Construct an AgentState directly with a specific task_state rather than running run_state_machine_agent.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: state machines and graphs conceptual guide",
                            "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}, {"slug": "python", "weight": 0.4}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "memory",
            "title": "Memory",
            "description": "Short-term and long-term memory architectures that let agents retain and reuse context across steps, sessions, and users.",
            "order_index": 10,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "short-term-vs-long-term-memory",
                    "title": "Short-Term vs. Long-Term Memory",
                    "description": "Distinguish working memory within a single task from persistent memory carried across sessions.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Distinguish short-term (working) memory from long-term (persistent) memory",
                        "Explain why unbounded conversation history is a poor short-term memory strategy",
                        "Describe summarization as a technique for compressing short-term memory",
                        "Identify use cases that genuinely require long-term memory across sessions",
                    ],
                    "content_markdown": """
## Why this matters

The Agent State module showed that `messages` grows unbounded across a long agent loop. Memory
is the set of strategies for managing that growth within a single task (short-term memory) and
for carrying useful information across entirely separate sessions or users (long-term memory) --
two related but distinct problems with different solutions.

## Short-term memory: working memory within one task

Short-term memory is everything an agent needs to complete its *current* task -- the equivalent
of human working memory. The naive approach (keep the entire conversation history) works for
short tasks but breaks down for long ones, both because of context window limits and because of
the "lost in the middle" attention degradation covered in the RAG course.

```python
# Naive short-term memory: unbounded growth
state.messages.append(new_message)  # never removed, never compressed

# A more sustainable approach: keep recent messages in full,
# summarize older ones once a threshold is reached
def manage_short_term_memory(messages: list, llm, max_recent: int = 10) -> list:
    if len(messages) <= max_recent:
        return messages
    older, recent = messages[:-max_recent], messages[-max_recent:]
    summary = llm.generate(f"Summarize the key facts and decisions from this conversation so far:\\n{format_messages(older)}")
    return [{"role": "system", "content": f"Summary of earlier context: {summary}"}] + recent
```

This keeps the most recent, most relevant messages in full detail while compressing older
context into a summary -- trading some detail for staying within a manageable size, a direct
practical application of the token-budgeting concerns from the RAG course's Context Construction
module.

## Long-term memory: persistent across sessions

Long-term memory persists information beyond a single task or conversation -- user preferences
learned last week, facts established in a previous session, or outcomes of past interactions
that should inform future ones.

```python
class LongTermMemory:
    def __init__(self, store):
        self.store = store  # a key-value store, database, or vector store

    def remember(self, user_id: str, fact: str, category: str) -> None:
        self.store.upsert(key=f"{user_id}:{category}:{hash(fact)}", value={"fact": fact, "category": category})

    def recall(self, user_id: str, category: str) -> list:
        return self.store.query(prefix=f"{user_id}:{category}:")

memory = LongTermMemory(store)
memory.remember(user_id="u_123", fact="Prefers email over phone contact", category="preferences")
```

## Use cases that genuinely need long-term memory

- A support agent that remembers a customer already explained their issue in a previous
  session, avoiding the frustration of asking them to repeat themselves.
- A personal assistant that recalls a user's stated preferences (timezone, communication style)
  without needing to re-derive them every conversation.
- An agent that learns from past task outcomes -- "the last three times I tried approach X for
  this kind of task, it failed for reason Y" -- to inform future planning, a theme picked up
  again in the Reflection module.

## Use cases that don't need it

Not every agent needs long-term memory, and adding it unnecessarily introduces real complexity:
storage infrastructure, privacy and data-retention considerations, and the risk of stale or
incorrect "memories" influencing future behavior. A single-session task-completion agent (like
"summarize this document") has no need for persistent memory across sessions at all -- its
short-term memory strategy alone is sufficient.

## The relationship to RAG

Long-term memory retrieval often looks architecturally identical to RAG (Course 6): facts are
embedded, stored in a vector database, and retrieved by relevance to the current context. The
key difference is what's being indexed -- RAG retrieves from a fixed external corpus; long-term
agent memory retrieves from a corpus the agent itself is continuously writing to as it operates.
""",
                    "examples": [
                        {
                            "title": "Short-term summarization kicking in mid-task",
                            "code": (
                                "# After 15 messages, manage_short_term_memory compresses the first 5\n"
                                "# into: 'Summary of earlier context: User wants a refund for order 4521.\n"
                                "# Order confirmed delayed due to weather. Refund eligibility confirmed.'\n"
                                "# The remaining 10 messages stay in full detail for the next reasoning step"
                            ),
                            "explanation": "This keeps the most recent, most actionable context fully detailed while still preserving the gist of everything that came before, within a bounded size.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a personal finance assistant agent, list 3 pieces of information that belong in long-term memory versus 3 that only need short-term memory within a single conversation.",
                            "difficulty": "easy",
                            "hint": "Long-term: stable facts about the user. Short-term: details specific to the current question being answered.",
                        },
                        {
                            "prompt": "Implement manage_short_term_memory and test it on a 20-message list with max_recent=5, confirming the result has exactly 6 entries (1 summary + 5 recent).",
                            "difficulty": "medium",
                            "hint": "You can stub the summarization LLM call to return a fixed string for testing purposes.",
                        },
                        {
                            "prompt": "Design a LongTermMemory.recall() call pattern for a support agent that needs to check whether a specific user has a known, unresolved billing dispute before answering a new question.",
                            "difficulty": "medium",
                            "hint": "Think about what category and query would retrieve exactly the relevant prior fact without pulling in irrelevant memories.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangChain: memory concepts",
                            "url": "https://python.langchain.com/docs/versions/migrating_memory/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "memory", "weight": 1.0}],
                },
                {
                    "slug": "implementing-a-memory-store-for-agents",
                    "title": "Implementing a Memory Store for Agents",
                    "description": "Build a working long-term memory store with save, retrieve-by-relevance, and forget operations.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a memory store supporting save, semantic retrieval, and deletion",
                        "Score and filter retrieved memories by relevance and recency",
                        "Design a strategy for handling conflicting or outdated memories",
                        "Wire memory retrieval into an agent's reasoning step",
                    ],
                    "content_markdown": """
## Why this matters

The previous lesson described long-term memory conceptually; this lesson builds an
implementation you could actually wire into an agent -- reusing the embedding and vector
storage skills from the RAG course, applied to a fundamentally different kind of corpus: facts
the agent itself generates over time.

## A memory record and store

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class MemoryRecord:
    id: str
    user_id: str
    content: str
    category: str
    created_at: datetime = field(default_factory=datetime.now)
    embedding: list = None

class AgentMemoryStore:
    def __init__(self, vector_db, embed_fn):
        self.vector_db = vector_db
        self.embed_fn = embed_fn

    def save(self, user_id: str, content: str, category: str) -> MemoryRecord:
        record = MemoryRecord(id=f"{user_id}-{hash(content)}", user_id=user_id, content=content, category=category)
        record.embedding = self.embed_fn(content)
        self.vector_db.upsert(
            ids=[record.id],
            vectors=[record.embedding],
            metadata=[{"user_id": user_id, "category": category, "created_at": record.created_at.isoformat(), "content": content}],
        )
        return record
```

This directly reuses the embedding and vector-store patterns from the RAG course's Embeddings
and Vector Databases modules -- the underlying mechanics are the same, only the source of the
content differs.

## Retrieving relevant memories

```python
def recall_relevant(self, user_id: str, query: str, top_k: int = 5, min_score: float = 0.7) -> list:
    query_vec = self.embed_fn(query)
    results = self.vector_db.query(vector=query_vec, top_k=top_k, filter={"user_id": user_id})
    return [r for r in results if r.score >= min_score]

AgentMemoryStore.recall_relevant = recall_relevant
```

Filtering by `user_id` is a metadata filtering pattern directly from the RAG course -- without
it, one user's memories could leak into another user's agent context, the same tenant-isolation
concern covered there.

## Scoring by relevance and recency together

A memory that's semantically relevant but five years old may be less useful than one that's
slightly less relevant but from yesterday, especially for facts that can go stale (like "current
project" or "recent preference").

```python
import math

def score_with_recency(result, half_life_days: float = 30) -> float:
    created_at = datetime.fromisoformat(result.metadata["created_at"])
    age_days = (datetime.now() - created_at).days
    recency_weight = math.exp(-age_days / half_life_days)
    return result.score * 0.7 + recency_weight * 0.3

def recall_with_recency(self, user_id: str, query: str, top_k: int = 5) -> list:
    candidates = self.recall_relevant(user_id, query, top_k=top_k * 2, min_score=0.5)
    ranked = sorted(candidates, key=score_with_recency, reverse=True)
    return ranked[:top_k]
```

The 0.7/0.3 weighting between relevance and recency is a tunable design choice, not a fixed
rule -- some domains (fast-changing preferences) should weight recency more heavily; others
(stable biographical facts) should weight relevance almost exclusively.

## Handling conflicting or outdated memories

```python
def save_with_conflict_check(self, user_id: str, content: str, category: str, llm) -> MemoryRecord:
    existing = self.recall_relevant(user_id, content, top_k=3)
    for record in existing:
        if record.metadata["category"] == category:
            conflict_check = llm.generate(
                f"Does this new fact contradict the old one? New: '{content}' Old: '{record.metadata['content']}'. Answer YES or NO."
            )
            if "YES" in conflict_check.upper():
                self.vector_db.delete(ids=[record.chunk_id])  # supersede the outdated memory
    return self.save(user_id, content, category)
```

Without conflict handling, an agent's memory can silently accumulate contradictory facts over
time (e.g., two different "current timezone" memories from different sessions) -- resolving
this at write time keeps the memory store internally consistent rather than pushing the problem
to read time, where it's much harder to detect.

## Wiring memory into an agent's reasoning step

```python
def build_prompt_with_memory(query: str, user_id: str, memory_store: AgentMemoryStore) -> str:
    memories = memory_store.recall_with_recency(user_id, query, top_k=3)
    memory_text = "\\n".join(f"- {m.metadata['content']}" for m in memories)
    return f"Relevant context from past interactions:\\n{memory_text}\\n\\nCurrent request: {query}"
```

This is the final integration point: memory retrieval happens before the agent's reasoning
step, in the same spirit as RAG's context construction -- relevant past facts become part of
the prompt the agent reasons over, not a separate system it queries only when explicitly asked.
""",
                    "examples": [
                        {
                            "title": "A conflicting memory getting superseded",
                            "code": (
                                "memory_store.save(\"u_123\", \"Timezone is US/Eastern\", category=\"preferences\")\n"
                                "# Weeks later, user relocates:\n"
                                "memory_store.save_with_conflict_check(\"u_123\", \"Timezone is US/Pacific\", category=\"preferences\", llm=llm)\n"
                                "# The old US/Eastern memory is detected as contradicting the new one\n"
                                "# and deleted, so future recalls return only the current timezone"
                            ),
                            "explanation": "Without this conflict check, both timezone memories would coexist, and a future retrieval might return either one, non-deterministically confusing the agent's behavior.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement AgentMemoryStore.save and recall_relevant against a fake in-memory vector_db, and confirm that memories saved for one user_id are never returned when recalling for a different user_id.",
                            "difficulty": "medium",
                            "hint": "This is directly testing the metadata filtering isolation discussed in this lesson.",
                        },
                        {
                            "prompt": "Tune the 0.7/0.3 relevance/recency weighting in score_with_recency for a use case of your choice, and justify your chosen weights.",
                            "difficulty": "medium",
                            "hint": "Consider whether your use case's facts are typically stable (favor relevance) or frequently changing (favor recency).",
                        },
                        {
                            "prompt": "Extend save_with_conflict_check to log every detected conflict (old content, new content, timestamp) rather than silently deleting the old memory, and explain why this audit trail might matter.",
                            "difficulty": "hard",
                            "hint": "Consider debugging a case where the conflict detection itself made a wrong call and incorrectly deleted a still-valid memory.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: long-term memory documentation",
                            "url": "https://langchain-ai.github.io/langgraph/concepts/memory/",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "memory", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "planning",
            "title": "Planning",
            "description": "Decomposing a goal into ordered steps up front, and adapting that plan as new information arrives.",
            "order_index": 11,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "decomposing-goals-into-plans",
                    "title": "Decomposing Goals into Plans",
                    "description": "Understand why explicit upfront planning helps complex agent tasks, and how to generate a structured plan.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the difference between reactive step-by-step reasoning and upfront planning",
                        "Generate a structured, ordered plan for a multi-step goal",
                        "Identify when planning helps versus when it adds unnecessary overhead",
                        "Represent a plan in a structured format an agent loop can execute against",
                    ],
                    "content_markdown": """
## Why this matters

Every agent loop so far in this course has been purely reactive: decide one action, observe the
result, decide the next action, with no explicit view of the whole task ahead of time. For
genuinely complex, multi-part goals, this can lead to inefficient or myopic behavior -- planning
introduces an explicit "think through the whole task first" step that often produces more
coherent, efficient execution.

## Reactive reasoning vs. upfront planning

A purely reactive agent (like the ReAct loop from Module 4) decides its next single action based
only on what it has seen so far, with no explicit representation of later steps. This works well
for tasks where the right next step only becomes clear after seeing a previous result, but it
can lead to a kind of tunnel vision on tasks with a genuinely foreseeable structure.

```python
# Purely reactive: no view of the full task, decided one step at a time
# Fine for tasks where step N+1 genuinely depends on step N's result
# in an unpredictable way

# Upfront planning: the agent first produces a structured plan for the
# WHOLE task, then executes (and can revise) it step by step
```

## Generating a structured plan

```python
PLANNING_PROMPT = (
    "Break this goal down into an ordered list of concrete steps. "
    "Each step should be a single, specific action, not a vague phase. "
    "Respond as a JSON list of step descriptions.\\n\\nGoal: {goal}"
)

def generate_plan(goal: str, llm) -> list[str]:
    raw = llm.generate(PLANNING_PROMPT.format(goal=goal))
    return json.loads(raw)

plan = generate_plan("Investigate why weekly active users dropped 15% last week and propose a fix.", llm)
# ["Check for recent product or infrastructure changes deployed last week",
#  "Compare engagement metrics across user segments to find where the drop is concentrated",
#  "Check for external factors (holidays, competitor launches, outages)",
#  "Summarize likely causes and propose next steps"]
```

Notice each step in a good plan is concrete and independently actionable -- "investigate the
problem" is too vague to execute against directly, while "check for recent product or
infrastructure changes deployed last week" maps clearly onto a specific tool call or research
action.

## Representing a plan for execution

```python
from dataclasses import dataclass, field

@dataclass
class PlanStep:
    description: str
    status: str = "pending"  # pending | in_progress | complete | failed
    result: str = None

@dataclass
class Plan:
    goal: str
    steps: list = field(default_factory=list)

def plan_from_descriptions(goal: str, descriptions: list[str]) -> Plan:
    return Plan(goal=goal, steps=[PlanStep(description=d) for d in descriptions])
```

Structuring the plan this way -- rather than just a flat list of strings -- lets the agent loop
track progress explicitly (which steps are done, which failed) and lets you inspect plan
execution state at any point, directly building on the state machine patterns from the Agent
State module.

## When planning helps

Planning earns its overhead for genuinely complex, multi-part goals where the overall structure
is knowable in advance (even if specific details within each step aren't) -- research tasks,
multi-stage investigations, tasks with clear sequential dependencies. Having an explicit plan
also makes agent behavior more predictable and auditable: you can show a user "here's what I'm
going to do" before execution even begins.

## When planning adds unnecessary overhead

For simple, single-action tasks ("look up this order's status"), generating a plan first is
pure overhead -- an extra LLM call that produces a one-item plan for a task a reactive loop
would have handled in the same number of steps anyway. And for tasks that are *genuinely*
unpredictable at every step (where each action fundamentally depends on the previous result in
ways you can't foresee), a rigid upfront plan can actually hurt by anchoring the agent to a
sequence that no longer fits what it's actually discovering -- which is exactly why the next
lesson covers adapting plans, not just generating them once and executing blindly.
""",
                    "examples": [
                        {
                            "title": "A vague step vs. a concrete, executable one",
                            "code": (
                                "# Too vague to execute directly:\n"
                                "\"Understand the problem\"\n"
                                "\n"
                                "# Concrete and mappable to a specific tool call:\n"
                                "\"Query the analytics database for daily active users over the last 30 days, segmented by platform\""
                            ),
                            "explanation": "A plan step needs to be specific enough that the agent loop can directly translate it into a tool call or well-scoped sub-task -- vague steps just push the ambiguity problem down to execution time.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a 4-6 step plan by hand for the goal 'prepare a competitive analysis of three named competitors' pricing pages,' making sure each step is concrete and independently actionable.",
                            "difficulty": "easy",
                            "hint": "Avoid steps like 'research competitors' -- break that into one concrete step per competitor or per data point needed.",
                        },
                        {
                            "prompt": "Implement generate_plan and plan_from_descriptions together, and print the resulting Plan object's steps with their initial 'pending' status for a goal of your choice.",
                            "difficulty": "medium",
                            "hint": "You can stub the LLM call with a hardcoded JSON list for testing without a real API.",
                        },
                        {
                            "prompt": "For a simple task ('what's 15% of 240') and a complex task ('plan and execute a product launch announcement'), argue whether upfront planning is worth its overhead for each.",
                            "difficulty": "medium",
                            "hint": "Consider the ratio of planning cost to task complexity for each case.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents -- planning patterns",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "planning", "weight": 1.0}],
                },
                {
                    "slug": "executing-and-adapting-plans",
                    "title": "Executing and Adapting Plans",
                    "description": "Execute a plan step by step, and revise it when a step's result invalidates the remaining steps.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a loop that executes a plan step by step, tracking status",
                        "Detect when a step's result invalidates the remaining plan",
                        "Implement plan revision that regenerates only the affected remaining steps",
                        "Combine planning with the agent loop's stopping conditions from earlier in this course",
                    ],
                    "content_markdown": """
## Why this matters

A plan that's generated once and blindly executed, ignoring what actually happens along the
way, isn't meaningfully better than a rigid pipeline -- it just moved the rigidity from "no
plan" to "an unchangeable plan." This lesson builds execution that both follows a plan *and*
adapts it, keeping the flexibility that makes agents valuable in the first place.

## Executing a plan step by step

```python
def execute_plan(plan: Plan, tools: dict, llm) -> Plan:
    for step in plan.steps:
        if step.status == "complete":
            continue
        step.status = "in_progress"
        decision = llm.chat(
            messages=[{"role": "user", "content": f"Execute this step: {step.description}\\nContext so far: {summarize_completed(plan)}"}],
            tools=list(tools.values()),
        )
        if decision.tool_call:
            result = tools[decision.tool_call.name](**decision.tool_call.arguments)
            step.result = str(result)
            step.status = "complete"
        else:
            step.result = decision.content
            step.status = "complete"
    return plan

def summarize_completed(plan: Plan) -> str:
    return "\\n".join(f"{s.description}: {s.result}" for s in plan.steps if s.status == "complete")
```

Passing `summarize_completed(plan)` as context to each step keeps later steps informed by
earlier results, without needing the entire raw conversation history -- a more structured
version of the short-term memory management from the Memory module.

## Detecting when a step invalidates the remaining plan

```python
def check_plan_still_valid(plan: Plan, completed_step: PlanStep, llm) -> bool:
    remaining = [s.description for s in plan.steps if s.status == "pending"]
    if not remaining:
        return True
    check_prompt = (
        f"Given this new information: '{completed_step.result}', "
        f"are these remaining planned steps still sensible?\\n{remaining}\\nAnswer YES or NO."
    )
    response = llm.generate(check_prompt)
    return "YES" in response.upper()
```

This check runs after each completed step, catching cases where an early discovery makes the
rest of the original plan obsolete -- for example, discovering in step 1 that a suspected cause
is ruled out, making a planned step 3 (investigating a consequence of that cause) pointless.

## Revising the plan

```python
def revise_plan(plan: Plan, completed_step: PlanStep, llm) -> Plan:
    completed_summary = summarize_completed(plan)
    revision_prompt = (
        f"Original goal: {plan.goal}\\nProgress so far: {completed_summary}\\n"
        "Given this progress, generate a revised list of remaining steps needed to complete the goal. "
        "Respond as a JSON list."
    )
    new_step_descriptions = json.loads(llm.generate(revision_prompt))
    completed_steps = [s for s in plan.steps if s.status == "complete"]
    return Plan(goal=plan.goal, steps=completed_steps + [PlanStep(description=d) for d in new_step_descriptions])
```

Regenerating only the *remaining* steps, while preserving completed ones untouched, avoids
redoing work that's already valid -- an important efficiency property, since re-planning from
scratch after every step would waste both the completed work and the cost of generating an
entirely new plan each time.

## The full adaptive execution loop

```python
def execute_plan_adaptively(goal: str, tools: dict, llm, max_revisions: int = 3) -> Plan:
    plan = plan_from_descriptions(goal, generate_plan(goal, llm))
    revisions = 0

    for step in list(plan.steps):
        if step.status == "complete":
            continue
        execute_plan(Plan(goal=plan.goal, steps=[step]), tools, llm)

        if not check_plan_still_valid(plan, step, llm) and revisions < max_revisions:
            plan = revise_plan(plan, step, llm)
            revisions += 1

    return plan
```

Bounding `max_revisions`, just like the iteration and budget limits from the Agent Loop module,
prevents a pathological case where the agent keeps re-planning indefinitely without ever
converging on a stable plan it can actually finish executing.

## Planning as an application of everything before it

This lesson's `execute_plan_adaptively` function directly composes ideas from across this
course: the agent loop's stopping conditions, structured outputs for parsing plan JSON reliably,
state tracking via the `Plan`/`PlanStep` objects, and tool calling for actually executing each
step -- planning isn't a separate system, it's these pieces arranged around an explicit,
inspectable task structure.
""",
                    "examples": [
                        {
                            "title": "A plan revision triggered by an early discovery",
                            "code": (
                                "# Original plan step 1: 'Check if the deploy from Tuesday caused the regression'\n"
                                "# Result: 'No deploys occurred in the relevant window'\n"
                                "# check_plan_still_valid: NO -- remaining steps 2-3 assumed a deploy was the cause\n"
                                "# revise_plan generates new remaining steps investigating infrastructure\n"
                                "# and traffic anomalies instead, since the deploy theory is now ruled out"
                            ),
                            "explanation": "This is exactly the scenario adaptive planning is built for: an early result invalidates an assumption baked into the rest of the original plan.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement execute_plan for a 3-step plan against stubbed tools, and confirm each step's status transitions from 'pending' to 'in_progress' to 'complete' correctly.",
                            "difficulty": "medium",
                            "hint": "Print plan.steps after execution to inspect the final status of each step.",
                        },
                        {
                            "prompt": "Write a test for check_plan_still_valid using a stubbed LLM that returns 'NO' for one specific completed_step.result and 'YES' otherwise, confirming the function's boolean return matches.",
                            "difficulty": "medium",
                            "hint": "Have your stub inspect the prompt content to decide which canned response to return.",
                        },
                        {
                            "prompt": "Trace through execute_plan_adaptively by hand for a 4-step plan where step 2's result triggers exactly one revision, and describe the final Plan object's steps.",
                            "difficulty": "hard",
                            "hint": "Remember that revise_plan preserves already-completed steps and only replaces the remaining ones.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: plan-and-execute agent tutorial",
                            "url": "https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/",
                            "resource_type": "tutorial",
                        }
                    ],
                    "skills": [{"slug": "planning", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "reflection",
            "title": "Reflection",
            "description": "Self-critique and self-correction loops that catch an agent's own mistakes before they reach the user.",
            "order_index": 12,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "self-critique-loops",
                    "title": "Self-Critique Loops",
                    "description": "Understand how an agent can evaluate its own output and decide whether to revise before finalizing an answer.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain the reflection pattern: generate, critique, revise",
                        "Distinguish reflection from the validation/repair loop covered in Structured Outputs",
                        "Identify what kinds of errors reflection can and cannot catch",
                        "Recognize the cost and diminishing-returns tradeoff of multiple reflection passes",
                    ],
                    "content_markdown": """
## Why this matters

Every agent built so far in this course commits to its first answer once its loop terminates.
Reflection adds one more capability: before finalizing, the agent evaluates its own work and
decides whether to revise it -- catching a category of mistakes that pure forward execution,
however well-planned, tends to miss.

## The generate-critique-revise pattern

```python
def generate_with_reflection(task: str, llm, max_revisions: int = 2) -> dict:
    draft = llm.generate(task)

    for revision in range(max_revisions):
        critique = llm.generate(
            f"Critique this response for accuracy, completeness, and clarity. "
            f"If it has no significant issues, respond with exactly 'NO ISSUES'.\\n\\n"
            f"Task: {task}\\nResponse: {draft}"
        )
        if "NO ISSUES" in critique.upper():
            return {"final": draft, "revisions": revision}

        draft = llm.generate(f"Revise this response to address the following critique.\\n\\nOriginal: {draft}\\nCritique: {critique}")

    return {"final": draft, "revisions": max_revisions}
```

The critique step deliberately uses a separate prompt from the original generation -- asking the
model to *evaluate* is a different task than asking it to *produce*, and separating them tends
to surface issues that generating and immediately trusting the first draft would miss.

## Reflection vs. structured output validation

The Structured Outputs module covered a repair loop for output that fails *schema* validation --
a mechanical, rule-based check ("is this valid JSON matching this schema?"). Reflection is
broader and more subjective: it evaluates *quality*, not just structural correctness -- is the
reasoning sound, is anything missing, is the tone appropriate. A response can pass schema
validation perfectly while still failing reflection's critique for being incomplete or
misleading.

```python
# Structured output validation: mechanical, rule-based
# "Does this JSON have all required fields with correct types?" -> deterministic yes/no

# Reflection: subjective, quality-based
# "Is this a genuinely good, complete, accurate answer to the question?" -> requires judgment
```

## What reflection can and cannot catch

Reflection is good at catching issues the model can recognize when explicitly asked to look for
them: missing considerations, logical inconsistencies within the response itself, unclear or
incomplete explanations. It is much weaker at catching errors the model doesn't know it's
making -- if the model's initial mistake stems from a genuine gap in its knowledge or a
misunderstanding of the retrieved context, a self-critique from the same underlying model may
simply repeat the same blind spot. This is why reflection complements, but doesn't replace,
external verification like the citation-checking from the RAG course or human review for
high-stakes decisions.

## The diminishing returns of multiple passes

```python
# Typical pattern across revision passes:
# Revision 0 -> 1: often catches a real, meaningful issue
# Revision 1 -> 2: sometimes catches a real issue, sometimes just rephrases
# Revision 2 -> 3: usually just stylistic changes, rarely substantive
```

Each reflection pass costs at least one extra LLM call (the critique) and often two (critique
plus revision), while the marginal quality improvement tends to shrink with each additional
pass. `max_revisions=1` or `2` is a reasonable default for most use cases -- pushing much higher
usually isn't worth the added cost and latency, similar to the reasoning-verbosity tradeoff
discussed for ReAct in Module 4.

## When reflection is worth adding

Reflection earns its cost for high-stakes or complex outputs where a subtle error is costly --
a legal summary, a financial analysis, code that will be executed. For low-stakes, simple
outputs (a quick factual lookup), the extra latency and cost of a reflection pass rarely pays
for itself, following the same "measure before adding complexity" discipline this course has
emphasized since the Agent vs. Chatbot module.
""",
                    "examples": [
                        {
                            "title": "A critique catching a real omission",
                            "code": (
                                "task = \"Explain the tradeoffs of using a managed vs. self-hosted vector database.\"\n"
                                "# Draft: covers cost and control, but omits latency and data residency\n"
                                "# Critique: 'This response is missing discussion of latency differences\n"
                                "#            and data residency/compliance considerations.'\n"
                                "# Revision: adds both missing points, producing a more complete answer"
                            ),
                            "explanation": "This is the kind of gap reflection is specifically good at catching -- an omission the model can recognize once explicitly asked to check for completeness, even though it didn't surface the gap unprompted.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement generate_with_reflection with max_revisions=1 against a task of your choice, and manually compare the draft and final versions to identify what the critique step actually changed.",
                            "difficulty": "medium",
                            "hint": "Print both draft and final and diff them by eye for a task with room for a genuine quality improvement.",
                        },
                        {
                            "prompt": "Describe a scenario where reflection would fail to catch an error because the mistake stems from the model's own knowledge gap, not a reasoning slip it can recognize.",
                            "difficulty": "medium",
                            "hint": "Consider a factual claim the model is simply wrong about and has no way to know it's wrong without external verification.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Self-Refine: Iterative Refinement with Self-Feedback (paper)",
                            "url": "https://arxiv.org/abs/2303.17651",
                            "resource_type": "paper",
                        }
                    ],
                    "skills": [{"slug": "reflection", "weight": 1.0}],
                },
                {
                    "slug": "implementing-a-reflection-loop-with-criteria",
                    "title": "Implementing a Reflection Loop with Explicit Criteria",
                    "description": "Build a reflection loop scored against named criteria instead of an open-ended critique, for more consistent results.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement reflection against a fixed set of named evaluation criteria",
                        "Score each criterion independently rather than producing one blended judgment",
                        "Trigger revision only for criteria that fall below a threshold",
                        "Log reflection outcomes to identify recurring weaknesses across many runs",
                    ],
                    "content_markdown": """
## Why this matters

An open-ended "critique this" prompt from the previous lesson can be inconsistent -- sometimes
focusing on tone, sometimes on completeness, with no guarantee the same dimensions get checked
every time. Structuring reflection against explicit, named criteria makes it more consistent and
lets you track quality along specific, comparable dimensions over time, echoing the RAG
Evaluation module's move from vague quality checks to concrete metrics.

## Defining explicit criteria

```python
from pydantic import BaseModel
from typing import Literal

class CriterionScore(BaseModel):
    criterion: str
    score: Literal[1, 2, 3, 4, 5]
    issue: str | None = None

class ReflectionResult(BaseModel):
    scores: list[CriterionScore]
    overall_pass: bool

CRITERIA = ["accuracy", "completeness", "clarity", "actionability"]
```

## Scoring against each criterion independently

```python
def critique_against_criteria(task: str, response: str, llm) -> ReflectionResult:
    prompt = (
        f"Score this response from 1-5 on each criterion below. For any score below 4, "
        f"briefly note the specific issue.\\n\\nCriteria: {', '.join(CRITERIA)}\\n\\n"
        f"Task: {task}\\nResponse: {response}\\n\\n"
        "Respond with a JSON object matching this shape: "
        '{"scores": [{"criterion": "...", "score": N, "issue": "..." or null}, ...]}'
    )
    raw = generate_structured(prompt, schema=REFLECTION_SCHEMA, llm=llm)
    scores = [CriterionScore(**s) for s in raw["scores"]]
    overall_pass = all(s.score >= 4 for s in scores)
    return ReflectionResult(scores=scores, overall_pass=overall_pass)
```

Scoring each criterion independently, rather than one blended "is this good?" judgment, makes
the feedback far more actionable for the revision step -- "clarity: 3, issue: uses jargon
without explanation" tells the model exactly what to fix, unlike a vague overall critique.

## Revising based on specific failing criteria

```python
def revise_for_issues(task: str, response: str, result: ReflectionResult, llm) -> str:
    failing = [s for s in result.scores if s.score < 4]
    issues_text = "\\n".join(f"- {s.criterion} (scored {s.score}/5): {s.issue}" for s in failing)
    return llm.generate(
        f"Revise this response to address these specific issues, without changing what's already working well.\\n\\n"
        f"Original: {response}\\nIssues to fix:\\n{issues_text}"
    )
```

The explicit instruction "without changing what's already working well" matters -- an
unconstrained revision prompt can sometimes degrade a criterion that was already scoring well
while fixing another, a subtle regression that's easy to miss without this guardrail.

## The full criteria-based reflection loop

```python
def generate_with_criteria_reflection(task: str, llm, max_revisions: int = 2) -> dict:
    response = llm.generate(task)
    history = []

    for revision in range(max_revisions):
        result = critique_against_criteria(task, response, llm)
        history.append(result)
        if result.overall_pass:
            return {"final": response, "revisions": revision, "history": history}
        response = revise_for_issues(task, response, result, llm)

    return {"final": response, "revisions": max_revisions, "history": history}
```

## Logging reflection outcomes to find recurring weaknesses

```python
def log_reflection_outcome(task_type: str, result: ReflectionResult) -> None:
    for score in result.scores:
        append_metric({"task_type": task_type, "criterion": score.criterion, "score": score.score})

def analyze_recurring_weaknesses(task_type: str, metrics: list) -> dict:
    by_criterion = defaultdict(list)
    for m in metrics:
        if m["task_type"] == task_type:
            by_criterion[m["criterion"]].append(m["score"])
    return {c: sum(scores) / len(scores) for c, scores in by_criterion.items()}
```

Tracking average scores per criterion across many runs reveals systematic weaknesses -- if
`clarity` consistently scores lower than other criteria across hundreds of tasks, that's a
signal worth addressing at the prompt or system level (better instructions, a different model,
a clearer output format), rather than relying on per-instance reflection to keep patching the
same underlying issue one response at a time.

## Reflection as a complement to evaluation

Notice how closely this parallels the RAG Evaluation module: named criteria, scores, and
thresholds turn "is this good?" from a vague feeling into something you can measure, track, and
act on systematically -- the same discipline applied to a different part of the pipeline.
""",
                    "examples": [
                        {
                            "title": "A revision that fixes one criterion without regressing another",
                            "code": (
                                "# Before: accuracy=5, completeness=3, clarity=4, actionability=4\n"
                                "# Issue: completeness -- missing a discussion of cost implications\n"
                                "# After revision (with the 'don't change what's working' guardrail):\n"
                                "# accuracy=5, completeness=5, clarity=4, actionability=4\n"
                                "# The fix targeted exactly the flagged gap without touching the other,\n"
                                "# already-strong dimensions"
                            ),
                            "explanation": "This is the concrete benefit of independent, named criteria scoring over a single blended critique -- targeted fixes with a much lower risk of accidentally regressing something that was already working.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define your own set of 4 criteria for evaluating customer support responses (different from the CRITERIA list in this lesson), and justify why each one matters for that specific domain.",
                            "difficulty": "easy",
                            "hint": "Consider tone/empathy as a domain-specific criterion support responses might need that general-purpose criteria don't capture.",
                        },
                        {
                            "prompt": "Implement critique_against_criteria and generate_with_criteria_reflection against a stubbed LLM, and trace through 2 revision cycles for a response that initially fails 'completeness' and 'clarity.'",
                            "difficulty": "hard",
                            "hint": "Have your stub return progressively better scores for the criteria being fixed across successive calls.",
                        },
                        {
                            "prompt": "Using analyze_recurring_weaknesses, describe what action you would take if you discovered 'actionability' consistently scored 2/5 lower than other criteria across 200 logged responses.",
                            "difficulty": "medium",
                            "hint": "Consider whether the fix belongs in the generation prompt, the reflection criteria definition, or elsewhere in the system.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: evaluating and improving agent outputs",
                            "url": "https://docs.claude.com/en/docs/build-with-claude/prompt-engineering/chain-of-thought",
                            "resource_type": "docs",
                        }
                    ],
                    "skills": [{"slug": "reflection", "weight": 1.0}, {"slug": "python", "weight": 0.3}],
                },
            ],
        },
        # ---------------------------------------------------------------
        {
            "slug": "routing",
            "title": "Routing",
            "description": "Dispatching a task to the right tool, specialized agent, or workflow based on what the task actually needs.",
            "order_index": 13,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "routing-strategies-for-agent-systems",
                    "title": "Routing Strategies for Agent Systems",
                    "description": "Compare classification-based, embedding-based, and rule-based approaches to routing a task to the right handler.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why routing is needed once a system has more than one specialized handler",
                        "Compare rule-based, classification-based, and embedding-based routing approaches",
                        "Identify the tradeoffs between routing accuracy, latency, and maintainability",
                        "Recognize routing as a foundational pattern for the multi-agent systems covered later in this program",
                    ],
                    "content_markdown": """
## Why this matters

As agent systems grow, you rarely want one single agent handling every possible task with one
enormous, generic prompt and every tool available -- specialization improves both reliability
and maintainability. Routing is the layer that decides, for a given input, which specialized
handler (tool, agent, or workflow) should take it.

## Why specialization needs routing

A single agent with 30 tools and instructions for every possible task category tends to perform
worse on any individual task than a set of focused agents, each with a handful of relevant tools
and instructions tailored to its specific domain -- more tools and instructions in context means
more opportunity for the model to select the wrong one, echoing the tool-design concerns from
Module 5. Routing is what lets you get the benefits of specialization while still presenting
users with one unified entry point.

```python
# Without routing: one agent, every tool, generic instructions -- harder
# for the model to reliably pick the right tool among many similar ones

# With routing: a lightweight router picks ONE specialized agent per
# request, and that agent only needs to reason about its own narrow toolset
```

## Rule-based routing

The simplest approach: hardcoded rules based on structured signals (keywords, metadata, explicit
user selection).

```python
def rule_based_route(request: dict) -> str:
    if request.get("category") == "billing":
        return "billing_agent"
    if "refund" in request["text"].lower():
        return "billing_agent"
    if request.get("category") == "technical":
        return "technical_agent"
    return "general_agent"
```

Fast, fully predictable, and easy to debug -- but brittle: it only handles signals you've
explicitly anticipated, and misses anything phrased in a way the rules don't cover.

## Classification-based routing

Use an LLM (often with structured outputs from Module 8) to classify the request into one of a
known set of categories.

```python
ROUTES = ["billing", "technical", "account", "general"]

def classification_route(request_text: str, llm) -> str:
    prompt = f"Classify this request into exactly one category: {ROUTES}.\\n\\nRequest: {request_text}"
    result = generate_structured(prompt, schema={"type": "object", "properties": {"category": {"enum": ROUTES}}}, llm=llm)
    return result["category"]
```

More flexible than rules -- it can handle novel phrasings a rule list wouldn't anticipate -- at
the cost of an extra LLM call per request and occasional misclassification, which rule-based
routing on an unambiguous signal (like an explicit category field) never has.

## Embedding-based routing

Embed the incoming request and compare it against embedded examples of each route category,
routing to whichever category's examples are most similar -- essentially a lightweight
classification task using the RAG course's similarity techniques rather than an LLM call.

```python
ROUTE_EXAMPLES = {
    "billing": ["I want a refund", "why was I charged twice", "update my payment method"],
    "technical": ["the app keeps crashing", "I can't log in", "getting an error message"],
}

def embedding_route(request_text: str, route_embeddings: dict) -> str:
    request_vec = embed_texts([request_text])[0]
    best_route, best_score = None, -1
    for route, example_vecs in route_embeddings.items():
        score = max(cosine_similarity(request_vec, v) for v in example_vecs)
        if score > best_score:
            best_route, best_score = route, score
    return best_route
```

Cheaper and faster than an LLM classification call (no generation, just embedding comparison),
but requires maintaining a representative set of examples per route and can be less accurate on
genuinely ambiguous or novel requests than a full LLM-based classifier that can reason about
edge cases.

## Choosing between approaches

| Approach | Accuracy on novel phrasing | Latency/cost | Maintainability |
|---|---|---|---|
| Rule-based | Low | Lowest | Easy, but brittle to new cases |
| Classification (LLM) | High | Higher (LLM call) | Easy, flexible |
| Embedding-based | Medium-high | Low (no generation) | Requires curating examples |

Many production systems layer these: cheap rule-based routing for unambiguous, high-confidence
signals, falling back to classification or embedding-based routing only for requests the rules
don't confidently resolve -- balancing cost against accuracy rather than committing to one
approach for every request.

## Routing as a foundation for multi-agent systems

This module's routing patterns are the direct precursor to the Multi-Agent Systems course later
in this program, where a "supervisor" or "orchestrator" agent routes sub-tasks to specialized
worker agents -- the same core problem (which handler should take this?) at a larger scale, with
richer feedback and coordination on top.
""",
                    "examples": [
                        {
                            "title": "A layered routing strategy",
                            "code": (
                                "def route_request(request: dict, llm, route_embeddings: dict) -> str:\n"
                                "    rule_result = rule_based_route(request)\n"
                                "    if rule_result != \"general_agent\":\n"
                                "        return rule_result  # confident, cheap, fast\n"
                                "    # Fall back to classification only when rules don't confidently resolve\n"
                                "    return classification_route(request[\"text\"], llm) + \"_agent\""
                            ),
                            "explanation": "This layered approach captures most requests cheaply via rules, reserving the more expensive LLM classification call for genuinely ambiguous cases the rules can't handle.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design rule-based routing logic for an email triage system with categories 'urgent', 'sales_lead', 'support', and 'spam', identifying which signals are reliable enough for pure rules versus which need classification.",
                            "difficulty": "medium",
                            "hint": "Sender domain or explicit subject-line markers might be reliable rule signals; ambiguous free-text content usually isn't.",
                        },
                        {
                            "prompt": "Implement embedding_route with 2 route categories and 3 example phrases each, and test it against 3 new requests to confirm it routes them to the expected category.",
                            "difficulty": "medium",
                            "hint": "Reuse the cosine_similarity function from the RAG course's Embeddings module.",
                        },
                        {
                            "prompt": "Compare the latency and cost implications of rule-based, classification-based, and embedding-based routing for a system handling 10,000 requests per day, and recommend a layered strategy.",
                            "difficulty": "hard",
                            "hint": "Estimate what fraction of requests could realistically be resolved by cheap rules before falling back to more expensive methods.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "Anthropic: Building effective agents -- routing pattern",
                            "url": "https://www.anthropic.com/research/building-effective-agents",
                            "resource_type": "article",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 0.8}, {"slug": "retrieval", "weight": 0.3}],
                },
                {
                    "slug": "building-a-router-for-a-multi-tool-agent",
                    "title": "Building a Router for a Multi-Tool Agent",
                    "description": "Implement a working router that dispatches requests to specialized agents, with a fallback and confidence threshold.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a router combining rule-based and classification-based strategies",
                        "Add a confidence threshold that falls back to a general handler on low-confidence routes",
                        "Log routing decisions to evaluate router accuracy over time",
                        "Test a router in isolation from the agents it dispatches to",
                    ],
                    "content_markdown": """
## Why this matters

This lesson builds a complete, testable router -- the specific implementation that ties together
this module's strategies and gives you a component ready to sit in front of the specialized
agents you'd build using every other pattern from this course.

## Defining specialized agents behind the router

```python
class SpecializedAgent:
    def __init__(self, name: str, tools: dict, system_prompt: str):
        self.name = name
        self.tools = tools
        self.system_prompt = system_prompt

    def handle(self, request_text: str, llm) -> dict:
        return tool_calling_agent(request_text, ToolRegistry.from_dict(self.tools), llm)

billing_agent = SpecializedAgent("billing", tools={"issue_refund": ..., "get_invoice": ...}, system_prompt="You handle billing questions only.")
technical_agent = SpecializedAgent("technical", tools={"check_system_status": ..., "restart_service": ...}, system_prompt="You handle technical issues only.")
general_agent = SpecializedAgent("general", tools={}, system_prompt="You handle general questions with no specialized tools.")
```

## A router combining rules and classification with confidence

```python
def route_with_confidence(request_text: str, llm, min_confidence: float = 0.7) -> dict:
    rule_result = rule_based_route({"text": request_text})
    if rule_result != "general_agent":
        return {"agent": rule_result, "confidence": 1.0, "method": "rule"}

    prompt = (
        f"Classify this request into one category: billing, technical, general. "
        f"Also provide a confidence score from 0 to 1.\\n\\nRequest: {request_text}"
    )
    result = generate_structured(
        prompt,
        schema={"type": "object", "properties": {"category": {"enum": ["billing", "technical", "general"]}, "confidence": {"type": "number"}}},
        llm=llm,
    )

    if result["confidence"] < min_confidence:
        return {"agent": "general_agent", "confidence": result["confidence"], "method": "fallback_low_confidence"}
    return {"agent": f"{result['category']}_agent", "confidence": result["confidence"], "method": "classification"}
```

Requiring the classifier to self-report a confidence score, and falling back to the safe general
handler below a threshold, prevents a low-confidence guess from routing a request to a
specialized agent that's actually the wrong fit -- similar in spirit to the risk-based defaults
from the Function Calling module's guardrails.

## Wiring the router to actual agents

```python
AGENTS = {"billing_agent": billing_agent, "technical_agent": technical_agent, "general_agent": general_agent}

def dispatch(request_text: str, llm) -> dict:
    routing_decision = route_with_confidence(request_text, llm)
    agent = AGENTS[routing_decision["agent"]]
    result = agent.handle(request_text, llm)
    return {**result, "routing": routing_decision}
```

## Logging routing decisions for evaluation

```python
def log_routing_decision(request_text: str, decision: dict, actual_correct_agent: str = None) -> None:
    entry = {"request": request_text, "routed_to": decision["agent"], "method": decision["method"], "confidence": decision["confidence"]}
    if actual_correct_agent:
        entry["correct"] = decision["agent"] == actual_correct_agent
    append_to_routing_log(entry)

def evaluate_router_accuracy(labeled_examples: list, llm) -> float:
    correct = 0
    for example in labeled_examples:
        decision = route_with_confidence(example["text"], llm)
        if decision["agent"] == example["expected_agent"]:
            correct += 1
    return correct / len(labeled_examples)
```

Building a labeled evaluation set for routing decisions -- exactly the same discipline as the
RAG Evaluation module's labeled retrieval set -- is how you'd actually validate a router before
trusting it in production, rather than assuming its classification prompt works well from a
handful of manual spot checks.

## Testing the router in isolation

```python
def test_billing_keyword_routes_correctly():
    decision = route_with_confidence("I want a refund for my last order", llm=fake_llm)
    assert decision["agent"] == "billing_agent"
    assert decision["method"] == "rule"

def test_low_confidence_falls_back_to_general():
    fake_llm.set_response({"category": "technical", "confidence": 0.4})
    decision = route_with_confidence("something vague and ambiguous", llm=fake_llm)
    assert decision["agent"] == "general_agent"
    assert decision["method"] == "fallback_low_confidence"
```

Testing `route_with_confidence` independently of the specialized agents it dispatches to --
using a fake or stubbed LLM -- means you can verify routing logic quickly and deterministically,
without needing to run the full downstream agent for every test case, echoing the test-double
pattern from the Generation module in the RAG course.
""",
                    "examples": [
                        {
                            "title": "A full request flowing through routing to a specialized agent",
                            "code": (
                                "result = dispatch(\"My last two charges look wrong, can you check?\", llm)\n"
                                "print(result[\"routing\"])   # {'agent': 'billing_agent', 'confidence': 1.0, 'method': 'rule'}\n"
                                "print(result[\"answer\"])    # the billing agent's response, using only its own tools"
                            ),
                            "explanation": "The routing decision and the final answer are returned together, giving full visibility into both which specialist handled the request and what it produced -- valuable for both debugging and the accuracy evaluation from this lesson.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement route_with_confidence and test both branches: a request that matches a rule, and a request that falls through to classification with confidence below your threshold.",
                            "difficulty": "medium",
                            "hint": "Use a fake LLM that returns a controllable confidence value for the classification branch.",
                        },
                        {
                            "prompt": "Build a 15-item labeled evaluation set (request text, expected_agent) covering all 3 categories plus a few deliberately ambiguous cases, and run evaluate_router_accuracy against it.",
                            "difficulty": "hard",
                            "hint": "Include at least 2-3 examples that are genuinely ambiguous between categories to stress-test the confidence threshold.",
                        },
                        {
                            "prompt": "Extend log_routing_decision and evaluate_router_accuracy to break down accuracy per category (billing vs. technical vs. general) rather than one overall number, and explain why per-category accuracy might reveal a problem the overall number hides.",
                            "difficulty": "medium",
                            "hint": "A router could have high overall accuracy while performing poorly on one specific, less-common category.",
                        },
                    ],
                    "resources": [
                        {
                            "title": "LangGraph: routing and multi-agent supervisor patterns",
                            "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/",
                            "resource_type": "tutorial",
                        }
                    ],
                    "skills": [{"slug": "agents", "weight": 0.9}, {"slug": "tool-calling", "weight": 0.3}],
                },
            ],
        },
    ],
}


COURSE_EXAM = {
    "title": "AI Agents Fundamentals: Course Assessment",
    "description": "Checks readiness to move into LangChain and framework-specific agent courses by testing the agent loop, tool/function calling, structured outputs, state, memory, planning, reflection, and routing.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 40,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "Which property, if removed, would turn a genuine AI agent into a fixed, single-step pipeline?",
            "options": [
                {"id": "a", "text": "The ability to produce text output"},
                {"id": "b", "text": "The ability to autonomously decide subsequent actions based on observed results"},
                {"id": "c", "text": "Access to a large language model"},
                {"id": "d", "text": "The ability to be deployed as an API"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Autonomy plus feedback -- deciding the next action based on what was just observed -- is what distinguishes an agent from a fixed pipeline that merely calls an LLM at one predetermined step.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "agents",
        },
        {
            "question_type": "mcq",
            "prompt": "A RAG-powered support chatbot retrieves documents and answers in a single fixed sequence per user turn, with no ability to decide to retrieve again or take further action. Where does this system sit relative to a full agent?",
            "options": [
                {"id": "a", "text": "It is a full agent because it uses retrieval and generates grounded answers"},
                {"id": "b", "text": "It is closer to a chatbot than a full agent, because its sequence of operations per turn is fixed rather than autonomously decided"},
                {"id": "c", "text": "It is identical to a full agent in every respect"},
                {"id": "d", "text": "It cannot be compared to agents or chatbots at all"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A RAG chatbot follows one fixed retrieve-then-generate sequence per turn without autonomously deciding on further actions, placing it on the spectrum closer to a chatbot despite being more capable than a plain chatbot.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "agents",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are legitimate stopping conditions to build into an agent loop for safety? (Select all that apply.)",
            "options": [
                {"id": "a", "text": "A hard maximum iteration count"},
                {"id": "b", "text": "A cumulative token or cost budget"},
                {"id": "c", "text": "Detection of repeated identical actions"},
                {"id": "d", "text": "Removing all limits so the agent can fully explore the problem space"},
            ],
            "correct_answer": {"choices": ["a", "b", "c"]},
            "explanation": "Iteration limits, cost budgets, and repeated-action detection are the three complementary safety layers covered in the Agent Loop module; removing all limits is exactly the reliability risk those layers are designed to prevent.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "agents",
        },
        {
            "question_type": "mcq",
            "prompt": "In the ReAct pattern, what is the primary benefit of requiring an explicit 'Thought' before each 'Action'?",
            "options": [
                {"id": "a", "text": "It makes the agent's output shorter and cheaper overall"},
                {"id": "b", "text": "Since models generate autoregressively, conditioning the action on an explicit prior reasoning step tends to improve the quality of action selection compared to jumping straight to an action"},
                {"id": "c", "text": "It removes the need for any tools"},
                {"id": "d", "text": "It guarantees the action will always be correct"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Because the action is generated after and conditioned on the explicit Thought, the model's reasoning directly informs the action choice, which measurably improves decision quality on multi-step tasks compared to direct action selection.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "agents",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is native tool calling (via a provider's structured tool-calling API) generally preferred over manually parsing tool calls out of free-text model output?",
            "options": [
                {"id": "a", "text": "It guarantees the model always chooses the semantically correct tool and arguments"},
                {"id": "b", "text": "It guarantees well-formed, schema-valid tool call requests, eliminating an entire category of parsing failures that manual regex-based extraction is prone to"},
                {"id": "c", "text": "It removes the need to validate tool arguments at all"},
                {"id": "d", "text": "It only works with a single tool at a time"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Native tool calling guarantees well-formed output matching your declared schema, which eliminates parsing failures -- but it does not guarantee the model's choice of tool or arguments is semantically correct, which remains a separate concern.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "tool-calling",
        },
        {
            "question_type": "scenario",
            "prompt": "An agent has a tool called issue_refund that is irreversible and involves real money. Design two independent guardrails you would add before this tool executes, and explain why having two independent layers is more robust than relying on just one.",
            "options": [],
            "correct_answer": {
                "expected": "Reasonable guardrails include: a human-in-the-loop confirmation/approval step for high-risk tools, and a rate limiter capping how many refund attempts can occur for the same order within a time window. Having two independent layers matters because a gap or misconfiguration in one guardrail (e.g., a tool accidentally missing from the risk classification) doesn't leave the system with zero protection -- the other layer still catches problematic behavior.",
                "keywords": ["human approval", "confirmation", "rate limiting", "independent layers", "defense in depth"],
            },
            "explanation": "This tests the Function Calling module's guardrail patterns: risk classification with human approval, and rate limiting, layered together so a single point of failure doesn't remove all protection.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "tool-calling",
        },
        {
            "question_type": "mcq",
            "prompt": "What guarantee does schema-constrained structured output generation provide that a prompt instruction like 'please respond in JSON' does not?",
            "options": [
                {"id": "a", "text": "That the output is factually correct"},
                {"id": "b", "text": "That the output's shape is enforced by the API during generation, rather than merely requested, eliminating malformed-output parsing failures"},
                {"id": "c", "text": "That the model will never make a wrong judgment call"},
                {"id": "d", "text": "That no validation code is ever needed downstream"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Schema-constrained generation enforces the output shape at the API level during token generation, which is a guarantee rather than a request -- but it says nothing about whether the underlying judgment or classification is semantically correct.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "tool-calling",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is 'derived state' (structured facts extracted from tool results) useful in addition to raw conversation history?",
            "options": [
                {"id": "a", "text": "It replaces the need for conversation history entirely"},
                {"id": "b", "text": "It's directly queryable by code without needing to re-parse free text, letting an agent efficiently check what it already knows before taking a redundant action"},
                {"id": "c", "text": "It makes the agent's context window unlimited"},
                {"id": "d", "text": "It is only useful for logging purposes, not decision-making"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Derived state gives application code a structured, queryable view of what the agent has learned, letting it check and reuse facts (like an already-known order status) without re-parsing raw conversation history on every check.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "state",
        },
        {
            "question_type": "short_answer",
            "prompt": "Explain the difference between short-term (working) memory and long-term (persistent) memory in an agent system, and give one example use case for each.",
            "options": [],
            "correct_answer": {
                "expected": "Short-term memory manages context within a single task or conversation, often via recent-message retention plus summarization of older content, e.g. keeping track of steps completed so far in a multi-step research task. Long-term memory persists information across separate sessions or users, e.g. remembering a user's stated communication preferences from a prior conversation so the agent doesn't need to re-derive them each time.",
                "keywords": ["within one task", "across sessions", "summarization", "persistent", "user preferences"],
            },
            "explanation": "This distinguishes the two memory scopes covered in the Memory module: short-term memory manages a single task's context window, while long-term memory persists facts across otherwise separate interactions.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "memory",
        },
        {
            "question_type": "mcq",
            "prompt": "In a long-term agent memory store built on a vector database, why is filtering retrieved memories by user_id (or another tenant identifier) essential, not optional?",
            "options": [
                {"id": "a", "text": "It improves embedding quality"},
                {"id": "b", "text": "Without it, one user's stored memories could be retrieved and surfaced to a different user simply because they're semantically similar -- a data isolation failure, not just a quality issue"},
                {"id": "c", "text": "It is only needed to reduce storage costs"},
                {"id": "d", "text": "Vector databases automatically isolate all data by user without configuration"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "This mirrors the RAG course's metadata filtering security concern: without a tenant/user filter, semantic similarity alone provides no isolation between different users' stored memories.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "memory",
        },
        {
            "question_type": "scenario",
            "prompt": "An agent executing a 5-step plan completes step 1 and discovers information that makes the assumption behind steps 3-5 invalid. What should the agent do, and what specific capability from the Planning module enables this?",
            "options": [],
            "correct_answer": {
                "expected": "The agent should check whether the remaining plan is still valid given the new information, and if not, revise the remaining (not yet completed) steps while preserving already-completed work. This is enabled by adaptive plan execution: a validity check after each step, combined with a revision function that regenerates only the affected remaining steps rather than the whole plan or blindly continuing the now-invalid original plan.",
                "keywords": ["check plan validity", "revise remaining steps", "preserve completed steps", "adaptive execution", "not blindly continue"],
            },
            "explanation": "This tests the adaptive planning pattern from the Planning module: detecting when new information invalidates the remaining plan and revising only the unexecuted portion, rather than rigidly continuing a now-outdated plan.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "planning",
        },
        {
            "question_type": "mcq",
            "prompt": "How does reflection (self-critique and revision) differ from the structured-output validation and repair loop covered earlier in this course?",
            "options": [
                {"id": "a", "text": "They are identical techniques with different names"},
                {"id": "b", "text": "Structured-output validation checks mechanical, rule-based correctness (does this match a schema?); reflection evaluates subjective quality (is this actually a good, complete, accurate answer?)"},
                {"id": "c", "text": "Reflection only applies to code generation tasks"},
                {"id": "d", "text": "Validation and repair cannot be automated, while reflection can"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Validation and repair is a mechanical, deterministic schema check; reflection is a broader, more subjective quality evaluation that can catch issues like incompleteness or unclear reasoning that pass schema validation perfectly.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "reflection",
        },
        {
            "question_type": "mcq",
            "prompt": "What is a key limitation of self-reflection as a quality-improvement technique?",
            "options": [
                {"id": "a", "text": "It always makes responses worse"},
                {"id": "b", "text": "If the original mistake stems from a genuine knowledge gap or blind spot the model has, a self-critique from the same underlying model may fail to catch it, since the model doesn't know what it doesn't know"},
                {"id": "c", "text": "It cannot be combined with structured outputs"},
                {"id": "d", "text": "It only works for mathematical tasks"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Reflection is good at catching issues the model can recognize when asked to look for them, but weak at catching errors rooted in the model's own knowledge gaps, since the same underlying model is doing the critiquing.",
            "difficulty": "medium",
            "points": 1.0,
            "skill_slug": "reflection",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function `rule_based_route(request)` that takes a dict with a 'text' key and returns 'billing_agent' if the text contains the word 'refund' (case-insensitive), 'technical_agent' if it contains the word 'error' (case-insensitive), and 'general_agent' otherwise.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Checks the lowercased text for the substrings 'refund' and 'error' and returns the corresponding agent name, defaulting to 'general_agent' when neither keyword is present.",
                "sample_solution": "def rule_based_route(request: dict) -> str:\n    text = request['text'].lower()\n    if 'refund' in text:\n        return 'billing_agent'\n    if 'error' in text:\n        return 'technical_agent'\n    return 'general_agent'",
            },
            "explanation": "This is a minimal version of the rule-based routing pattern from the Routing module: fast, deterministic dispatch based on simple keyword signals, with a safe default fallback.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "agents",
        },
        {
            "question_type": "scenario",
            "prompt": "You're building a router that uses LLM classification to dispatch requests to one of three specialized agents. The classifier occasionally returns a category with low self-reported confidence. What should the router do in that case, and why is this safer than always routing to whatever category the classifier returns?",
            "options": [],
            "correct_answer": {
                "expected": "The router should fall back to a general-purpose handler rather than dispatching to the low-confidence specialized agent. This is safer because a specialized agent is often configured with only a narrow set of tools and instructions for its domain -- if the request was actually miscategorized, that specialized agent may lack the right tools or context to handle it well, whereas a general handler (or human escalation) can respond more safely to an ambiguous or misrouted request.",
                "keywords": ["fall back to general agent", "low confidence threshold", "avoid wrong specialist", "safer default", "narrow toolset risk"],
            },
            "explanation": "This tests the confidence-threshold fallback pattern from the Routing module: routing decisions below a confidence threshold should default to a safe, general-purpose handler rather than committing to a possibly-wrong specialist.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "agents",
        },
    ],
}
