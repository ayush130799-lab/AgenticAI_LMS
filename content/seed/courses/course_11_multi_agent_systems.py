"""
Course 11: Multi-Agent Systems

Covers architecture patterns, communication, supervision, delegation,
orchestration, shared state, and conflict resolution for systems built from
multiple cooperating LLM agents rather than a single monolithic agent.
"""

COURSE = {
    "slug": "multi-agent-systems",
    "title": "Multi-Agent Systems",
    "subtitle": "Design teams of AI agents that plan, delegate, and resolve conflict together",
    "description": (
        "A single agent hits a wall once tasks span multiple domains, need parallel work, "
        "or require specialized judgment at each step. This course teaches you to decompose "
        "problems across a team of cooperating agents: how they talk to each other, how a "
        "supervisor routes work, how specialists stay narrow and reliable, and how the whole "
        "system shares state without stepping on itself. You'll build supervisor-worker and "
        "orchestrator patterns in LangGraph and learn to detect and resolve the conflicts that "
        "emerge once more than one agent can take action."
    ),
    "learning_outcomes": [
        "Choose the right multi-agent topology (supervisor-worker, hierarchical, peer-to-peer, pipeline) for a given problem",
        "Design structured message-passing and handoff protocols between agents",
        "Build a supervisor agent that routes tasks to specialist agents based on capability",
        "Implement delegation and orchestration graphs with LangGraph",
        "Design a shared state schema that avoids race conditions and context bloat",
        "Detect, arbitrate, and resolve conflicting outputs from multiple agents",
    ],
    "order_index": 11,
    "estimated_hours": 16,
    "level": "advanced",
    "icon": "network",
    "modules": [
        {
            "slug": "multi-agent-architecture",
            "title": "Multi-Agent Architecture",
            "description": "Why single agents hit a ceiling, and the core topologies used to structure teams of agents.",
            "order_index": 1,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "why-single-agents-hit-a-ceiling",
                    "title": "Why Single Agents Hit a Ceiling",
                    "description": "The concrete failure modes that push teams from one agent to many.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify the three failure modes that motivate multi-agent design",
                        "Explain context dilution and tool-set overload in a single agent",
                        "Distinguish problems that need decomposition from problems that need a bigger prompt",
                    ],
                    "content_markdown": """
## The single-agent ceiling

A single ReAct-style agent with a system prompt, a dozen tools, and a context window works
remarkably well for bounded tasks. It starts to fail in three predictable ways as scope grows.

**Tool-set overload.** Once an agent has more than roughly 15-20 tools, tool selection accuracy
drops. The model has to hold every tool's name, signature, and appropriate-use conditions in
context simultaneously, and closely related tools (`search_web` vs `search_docs` vs
`search_internal_kb`) get confused for each other. Splitting tools across specialist agents,
each with 3-5 tools relevant to its job, restores selection accuracy.

**Context dilution.** A long-running agent accumulates conversation history, tool outputs, and
intermediate reasoning in one context window. By turn 20, the instructions from turn 1 are
competing for attention with a wall of accumulated noise, and instruction-following degrades.
Multi-agent systems let each agent keep a short, focused context scoped to its sub-task, and
only pass a compact summary forward.

**Conflicting personas.** A support agent that also needs to write SQL, review legal contracts,
and negotiate refunds is being asked to be four different things in one system prompt. Persona
and policy instructions start to conflict subtly, and the model averages between them rather
than doing any one well. Separate agents can each have a sharp, unambiguous persona.

## When decomposition is the wrong answer

Not every hard problem needs multiple agents. If the task is genuinely sequential and no step
benefits from a different tool set, persona, or model, adding agents just adds coordination
overhead, extra LLM calls, and more places for information to get lost in translation. A good
rule of thumb: reach for multi-agent design when you can name at least two genuinely different
*roles* the task requires (e.g., "plan" vs "execute", or "research" vs "write"), not simply
because the task is long.

```python
# A signal that a task wants decomposition: distinct, nameable responsibilities
task = {
    "research": "Find the top 5 competitor pricing pages and extract tiers",
    "analyze": "Compare tiers against our own pricing and flag gaps",
    "write": "Draft a one-page pricing recommendation memo",
}
# Three different skills, three different tool sets, three different "voices" -> good candidate
```

## Cost and latency trade-offs

Multi-agent systems make more LLM calls than a single agent for the same task, because every
handoff usually involves at least one summarization step. Budget for this explicitly: a
supervisor call, two specialist calls, and a synthesis call is 4x the tokens of a single
end-to-end call. The payoff is accuracy and maintainability, not cost — treat that trade-off
as a design decision, not an accident.
""",
                    "examples": [
                        {
                            "title": "Example: measuring tool selection accuracy as tool count grows",
                            "code": (
                                "results = []\n"
                                "for n_tools in [5, 10, 20, 30]:\n"
                                "    subset = ALL_TOOLS[:n_tools]\n"
                                "    accuracy = eval_tool_selection(agent, subset, test_cases)\n"
                                "    results.append((n_tools, accuracy))\n"
                                "# results typically show accuracy dropping sharply past ~20 tools"
                            ),
                            "explanation": "Running the same test suite against a growing tool list is the fastest way to prove to a team that tool-set overload is real, not theoretical.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Take a single-agent system prompt you've seen (or write a rough one for a 'do everything' support bot) and list the distinct personas or skill sets it's being asked to hold at once.",
                            "difficulty": "easy",
                            "hint": "Look for sentences that start with 'You are also responsible for...' — each one is a candidate persona.",
                        },
                        {
                            "prompt": "For a trip-planning assistant that books flights, hotels, and restaurants, decide whether it needs multiple agents. Justify your answer using the tool-count and persona criteria from this lesson.",
                            "difficulty": "medium",
                            "hint": "Count the tools each sub-task would need and check for conflicting personas (e.g., frugal vs luxury recommender).",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Building effective agents", "url": "https://www.anthropic.com/research/building-effective-agents", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "core-multi-agent-topologies",
                    "title": "Core Multi-Agent Topologies",
                    "description": "Supervisor-worker, hierarchical, peer-to-peer, and pipeline patterns compared.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Describe four common multi-agent topologies and their trade-offs",
                        "Map a real business workflow onto the appropriate topology",
                        "Explain why supervisor-worker is the default starting point for most teams",
                    ],
                    "content_markdown": """
## Four topologies

**Supervisor-worker (hub and spoke).** A single supervisor agent receives the task, decides
which specialist to invoke, and synthesizes the final answer. Workers never talk to each other
directly. This is the easiest topology to reason about and debug — every decision passes
through one place — and it's the right default unless you have a specific reason to deviate.

**Hierarchical (supervisor of supervisors).** Large systems nest supervisor-worker pairs: a
top-level supervisor routes to mid-level supervisors, each of which manages its own team of
specialists. Useful when a system genuinely spans multiple business domains (e.g., a top-level
"customer request" router that hands off to a "billing team" supervisor or a "technical
support team" supervisor).

**Peer-to-peer.** Agents can message each other directly without going through a central
router. This maximizes flexibility but makes the system's behavior much harder to predict or
debug, since there's no single place to trace a decision. Reserve this for cases with a small,
fixed number of agents (2-3) that need tight, low-latency back-and-forth, such as a
writer/critic pair.

**Pipeline (sequential).** Agents run in a fixed order, each consuming the previous agent's
output — research agent, then analysis agent, then writer agent. No routing decision is made
at runtime; the structure is the routing. Pipelines are the simplest topology to implement and
the easiest to test stage-by-stage, but they can't adapt if a step reveals the plan needs to
change.

```python
# Pseudocode contrasting the shapes
def supervisor_worker(task):
    plan = supervisor.decide_route(task)
    result = WORKERS[plan.worker].run(task)
    return supervisor.synthesize(result)

def pipeline(task):
    step1 = research_agent.run(task)
    step2 = analysis_agent.run(step1)
    return writer_agent.run(step2)
```

## Choosing a topology

Start every design with supervisor-worker. Move to hierarchical only once a single supervisor's
routing logic becomes unwieldy (more than ~6-8 specialists, or specialists that naturally
cluster into domains). Reach for a pipeline when the sequence of steps genuinely never changes
based on intermediate results. Reach for peer-to-peer only for small, tightly coupled pairs
where the overhead of a supervisor round-trip would hurt quality (e.g., an iterative
draft-critique loop).

## Topology affects failure isolation

A supervisor-worker system fails gracefully: if one specialist errors out, the supervisor can
retry, fall back to a different specialist, or apologize and stop — the blast radius is one
worker. A peer-to-peer system without careful design can cascade: agent A's bad output becomes
agent B's bad input becomes agent C's bad input, and by the time a human looks at the
transcript the original error is three hops upstream. This is one of the strongest practical
arguments for defaulting to hub-and-spoke designs in production.
""",
                    "examples": [
                        {
                            "title": "Example: mapping a workflow to hierarchical topology",
                            "code": (
                                "# Top-level supervisor routes by domain\n"
                                "TOP_LEVEL_ROUTES = {\n"
                                "    'billing': billing_team_supervisor,\n"
                                "    'technical': tech_team_supervisor,\n"
                                "    'sales': sales_team_supervisor,\n"
                                "}\n"
                                "# Each team supervisor then routes to its own specialists\n"
                                "BILLING_ROUTES = {\n"
                                "    'refund': refund_agent,\n"
                                "    'invoice': invoice_agent,\n"
                                "}"
                            ),
                            "explanation": "Nesting supervisors keeps each routing decision small (a handful of options) even as the total specialist count grows into the dozens.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Sketch which topology fits a content pipeline that always runs: outline -> draft -> fact-check -> edit, in that fixed order.",
                            "difficulty": "easy",
                            "hint": "The order never changes based on results — that's a strong signal for one specific topology.",
                        },
                        {
                            "prompt": "A company wants one system to handle HR questions, IT tickets, and expense reports, each with 4-5 specialist sub-agents. Design the topology and justify the number of levels.",
                            "difficulty": "medium",
                            "hint": "Count how many total specialists a single supervisor would need to route between.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Multi-agent systems", "url": "https://langchain-ai.github.io/langgraph/concepts/multi_agent/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "agent-communication",
            "title": "Agent Communication",
            "description": "How agents pass messages and structured payloads to each other reliably.",
            "order_index": 2,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "message-passing-between-agents",
                    "title": "Message Passing Between Agents",
                    "description": "Implementing a shared message format that agents append to and read from.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a shared message list as the communication backbone between agents",
                        "Distinguish full-history passing from summarized handoffs",
                        "Attach agent identity metadata to messages for traceability",
                    ],
                    "content_markdown": """
## The message list as shared backbone

The simplest, most debuggable way for agents to communicate is an append-only list of typed
messages that every agent reads from and writes to, similar to a chat transcript. Each message
carries who sent it, what kind of message it is, and its content.

```python
from dataclasses import dataclass, field
from typing import Literal
import time

@dataclass
class AgentMessage:
    sender: str
    role: Literal["task", "result", "clarification", "error"]
    content: str
    metadata: dict = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)

class MessageBus:
    def __init__(self):
        self.messages: list[AgentMessage] = []

    def publish(self, message: AgentMessage) -> None:
        self.messages.append(message)

    def history_for(self, sender: str | None = None) -> list[AgentMessage]:
        if sender is None:
            return list(self.messages)
        return [m for m in self.messages if m.sender == sender]
```

Every agent function takes the bus (or a slice of it) as input and publishes its output back
before returning control to the caller. This gives you a complete, ordered audit trail for
free — invaluable when debugging why a multi-agent run went wrong.

## Full history vs. summarized handoff

Passing the entire message history to every agent is simple but expensive and eventually hits
context limits. The alternative is a **handoff summary**: before invoking the next agent, an
explicit summarization step condenses everything relevant into a few hundred tokens.

```python
def handoff_summary(bus: MessageBus, for_agent: str) -> str:
    relevant = [m for m in bus.messages if m.role in ("task", "result")]
    joined = "\n".join(f"[{m.sender}] {m.content}" for m in relevant[-10:])
    prompt = (
        f"Summarize the following for the {for_agent} agent. "
        f"Keep only facts it needs to act; drop reasoning trails.\n\n{joined}"
    )
    return llm_call(prompt)
```

Use full history for short chains (2-3 agents) where token cost is negligible. Use summarized
handoffs once a chain has 4+ hops or any single agent's context is already large.

## Tagging sender identity

Always attach `sender` to every message, even in a two-agent system. The first time you debug
a multi-agent run at 2am, an untagged transcript that just says "here's the analysis" without
saying *which* agent produced it is nearly useless. Treat sender tagging as non-negotiable,
the same way you'd never skip log levels in application logging.
""",
                    "examples": [
                        {
                            "title": "Example: a two-agent exchange over the bus",
                            "code": (
                                "bus = MessageBus()\n"
                                "bus.publish(AgentMessage(sender='supervisor', role='task', content='Find Q3 churn rate'))\n"
                                "result = research_agent.run(bus.history_for())\n"
                                "bus.publish(AgentMessage(sender='research_agent', role='result', content=result))\n"
                                "print(len(bus.messages))  # 2"
                            ),
                            "explanation": "The bus accumulates a complete, replayable trace of the interaction without any agent needing to know about the others directly.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Extend `AgentMessage` with a `cost_tokens` field and write a function that sums total tokens used across a run.",
                            "difficulty": "easy",
                            "hint": "Add the field with a default of 0, then use sum() with a generator expression over bus.messages.",
                        },
                        {
                            "prompt": "Implement `handoff_summary` so it only fires when the accumulated history exceeds 3000 characters, otherwise it passes full history.",
                            "difficulty": "medium",
                            "hint": "Compute total length of joined content first and branch on it.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Send API for multi-agent messaging", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#send", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "structured-communication-protocols",
                    "title": "Structured Communication Protocols",
                    "description": "Using typed schemas instead of free text for inter-agent handoffs.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain why free-text handoffs are brittle at scale",
                        "Design a Pydantic schema for a structured agent handoff",
                        "Validate incoming handoff payloads before an agent acts on them",
                    ],
                    "content_markdown": """
## Why free text breaks down

A handoff message like `"the user wants a refund for order 4471, approved for $32.50"` works
until the receiving agent parses it slightly wrong, or the sending agent phrases it
differently next time. Free text is fine for logs a human reads; it's a liability for a
payload another program parses and acts on. As soon as a downstream agent branches on the
*content* of a handoff (not just prints it), structure it.

## Schema-first handoffs

Define a Pydantic model for each handoff type your system uses, and have the sending agent
produce structured output (via tool calling or JSON mode) directly into that shape.

```python
from pydantic import BaseModel, Field
from typing import Literal

class RefundHandoff(BaseModel):
    order_id: str
    amount_usd: float = Field(gt=0)
    reason: Literal["damaged", "wrong_item", "changed_mind", "other"]
    requires_manager_approval: bool

class RefundHandoffResult(RefundHandoff):
    status: Literal["approved", "denied", "escalated"]
    notes: str = ""
```

The receiving agent's first action is `RefundHandoff.model_validate(payload)`. If validation
fails, that's a clear, catchable error — not a downstream agent silently misinterpreting a
sentence.

## Versioning handoff schemas

Once a schema is in production, treat it like an API contract: add fields as optional with
defaults, never rename or repurpose a field in place, and log the schema version alongside
each handoff. This matters more in multi-agent systems than typical APIs because agents are
non-deterministic — a subtle prompt change can start producing a slightly different shape, and
without validation that drift goes unnoticed until it causes a downstream failure.

```python
class RefundHandoff(BaseModel):
    schema_version: int = 2
    order_id: str
    amount_usd: float = Field(gt=0)
    reason: Literal["damaged", "wrong_item", "changed_mind", "other"]
    requires_manager_approval: bool
    currency: str = "USD"  # added in v2, defaulted for backward compatibility
```

## Structured output plus a free-text rationale

The best of both worlds is usually a schema with one `rationale: str` field alongside the
typed fields. Downstream logic branches on the typed fields; humans reviewing the trace read
the rationale. This avoids forcing every nuance of the agent's reasoning into rigid enum
values while still keeping the fields that matter to program logic strictly typed.
""",
                    "examples": [
                        {
                            "title": "Example: validating a handoff before acting",
                            "code": (
                                "from pydantic import ValidationError\n\n"
                                "def receive_handoff(raw: dict) -> RefundHandoff | None:\n"
                                "    try:\n"
                                "        return RefundHandoff.model_validate(raw)\n"
                                "    except ValidationError as e:\n"
                                "        log.error('bad handoff payload: %s', e)\n"
                                "        return None"
                            ),
                            "explanation": "Failing loudly and early at the schema boundary prevents a malformed handoff from silently corrupting a downstream agent's behavior.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a Pydantic schema for a handoff from a research agent to a writer agent that needs sources and a confidence score.",
                            "difficulty": "easy",
                            "hint": "Include a list[str] for sources and a float confidence between 0 and 1 using Field(ge=0, le=1).",
                        },
                        {
                            "prompt": "Add a schema_version field to your handoff model and write a small migration function that upgrades a v1 payload (missing a new field) to v2 by filling in a sensible default.",
                            "difficulty": "medium",
                            "hint": "Check for the absence of the new key in the raw dict before validating.",
                        },
                    ],
                    "resources": [
                        {"title": "Pydantic: Models", "url": "https://docs.pydantic.dev/latest/concepts/models/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 0.8}, {"slug": "state", "weight": 0.3}],
                },
            ],
        },
        {
            "slug": "supervisor-agents",
            "title": "Supervisor Agents",
            "description": "Designing the agent responsible for routing and synthesis in a supervisor-worker system.",
            "order_index": 3,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "designing-a-supervisor-agent",
                    "title": "Designing a Supervisor Agent",
                    "description": "Building the routing brain of a supervisor-worker system.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a supervisor that routes tasks to the correct specialist",
                        "Write a routing prompt that includes each specialist's capability boundaries",
                        "Handle the case where no specialist is a good fit",
                    ],
                    "content_markdown": """
## The supervisor's two jobs

A supervisor agent does exactly two things: decide which specialist(s) should handle a piece
of work, and synthesize their outputs into a final response. It should not try to do the
specialists' work itself — if the supervisor's prompt starts accumulating domain knowledge
about refunds or SQL, that logic belongs in a specialist, not the router.

```python
from pydantic import BaseModel
from typing import Literal

class RoutingDecision(BaseModel):
    specialist: Literal["research", "billing", "technical", "none"]
    rationale: str

SUPERVISOR_PROMPT = \"\"\"
You are a routing supervisor. Given the user's request, decide which specialist should
handle it. Available specialists:
- research: answers factual questions using web and internal search tools
- billing: handles refunds, invoices, and payment disputes
- technical: debugs product issues and reads error logs
- none: use only if the request needs no specialist (e.g., a greeting)

Do not attempt to answer the request yourself. Return a routing decision only.
\"\"\"

def route(user_request: str) -> RoutingDecision:
    return structured_llm_call(SUPERVISOR_PROMPT, user_request, schema=RoutingDecision)
```

## Capability boundaries, not vibes

The routing prompt should describe each specialist by what it *can and cannot* do, not by a
vague label. "billing: handles refunds, invoices, payment disputes" routes correctly far more
often than "billing: the billing agent" because the model has concrete criteria to match
against rather than a name to guess from.

## Handling no-good-fit cases

Always give the supervisor an explicit escape hatch (`"none"` or `"clarify"`) rather than
forcing a choice among specialists that don't fit. A supervisor forced to always pick a
specialist will eventually route billing questions to technical support out of desperation,
producing a confidently wrong answer. An explicit `clarify` route that asks the user a
follow-up question is almost always better than a wrong specialist.

```python
def handle_request(user_request: str):
    decision = route(user_request)
    if decision.specialist == "none":
        return ask_clarifying_question(user_request)
    result = SPECIALISTS[decision.specialist].run(user_request)
    return synthesize(user_request, result)
```

## Synthesis is a real step, not a formality

Don't just return the specialist's raw output to the user. The supervisor's synthesis pass
should reframe the specialist's technical output in the voice and format the user expects,
and — critically — should be the place where you catch a specialist returning something that
doesn't actually answer the original question, and retry or escalate instead of shipping it.
""",
                    "examples": [
                        {
                            "title": "Example: full supervisor loop with a fallback",
                            "code": (
                                "def handle_request(user_request: str) -> str:\n"
                                "    decision = route(user_request)\n"
                                "    if decision.specialist == 'none':\n"
                                "        return 'Could you clarify what you need help with?'\n"
                                "    try:\n"
                                "        result = SPECIALISTS[decision.specialist].run(user_request)\n"
                                "    except SpecialistError:\n"
                                "        return synthesize_fallback(user_request)\n"
                                "    return synthesize(user_request, result)"
                            ),
                            "explanation": "The try/except ensures a single specialist failure degrades to a fallback response rather than crashing the whole request.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a routing prompt for a supervisor with three specialists: 'legal', 'hr', 'it'. Include capability boundaries for each.",
                            "difficulty": "easy",
                            "hint": "Describe each specialist by concrete task types it handles, not a one-word label.",
                        },
                        {
                            "prompt": "Add a 'multi' routing option that lets the supervisor invoke two specialists in sequence when a request spans both, and update `handle_request` to support it.",
                            "difficulty": "hard",
                            "hint": "Change specialist from a single Literal to a list, and loop over it while accumulating results before synthesis.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Supervisor pattern tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/agent_supervisor/", "resource_type": "tutorial"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "routing-logic-and-decision-boundaries",
                    "title": "Routing Logic and Decision Boundaries",
                    "description": "Making routing decisions robust at the edges where specialist responsibilities overlap.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Identify ambiguous routing cases where specialist boundaries overlap",
                        "Use few-shot examples to sharpen a supervisor's routing accuracy",
                        "Evaluate a router's accuracy against a labeled test set",
                    ],
                    "content_markdown": """
## Where routing breaks

Routing decisions are easy at the center of each specialist's territory and hard at the edges.
"I was charged twice and the app also crashed" spans billing and technical. "Why did my
subscription upgrade fail" could be billing (payment declined) or technical (a bug). These
boundary cases are exactly where a router without concrete guidance guesses inconsistently.

## Few-shot examples fix boundary cases faster than more prose

Adding another paragraph of description to a specialist rarely improves routing at the
boundary. Adding 3-5 labeled examples of exactly the ambiguous cases you've seen in production
does. Few-shot examples let the model pattern-match against precedent instead of applying a
rule it has to infer from a description.

```python
ROUTING_EXAMPLES = [
    {"request": "I was charged twice and the app crashed after", "route": "billing",
     "why": "duplicate charge is the actionable issue; app crash is secondary context"},
    {"request": "My upgrade failed and no charge appears on my card", "route": "technical",
     "why": "no charge occurred, so this is a product bug, not a billing dispute"},
]
```

Include these directly in the routing prompt, updated periodically from real routing mistakes
you observe in production — this is the highest-leverage maintenance work for a supervisor
agent.

## Confidence thresholds and human-in-the-loop

Have the router emit a confidence score alongside its decision, and route low-confidence
decisions to a human reviewer or a clarifying question instead of a specialist.

```python
class RoutingDecision(BaseModel):
    specialist: str
    confidence: float
    rationale: str

if decision.confidence < 0.6:
    return ask_clarifying_question(user_request)
```

This single threshold check eliminates a large fraction of embarrassing misroutes for a small
cost in occasional extra clarifying questions.

## Evaluating a router like a classifier

Because routing is fundamentally a classification problem, evaluate it like one: build a
labeled test set of (request, correct_specialist) pairs pulled from real traffic, compute
accuracy and a confusion matrix, and track both over time as you tune the prompt. A confusion
matrix will show you exactly which specialist pairs get confused, which tells you precisely
where to add few-shot examples next.
""",
                    "examples": [
                        {
                            "title": "Example: a tiny routing confusion matrix",
                            "code": (
                                "from collections import Counter\n\n"
                                "confusions = Counter()\n"
                                "for request, true_route in test_set:\n"
                                "    predicted = route(request).specialist\n"
                                "    if predicted != true_route:\n"
                                "        confusions[(true_route, predicted)] += 1\n"
                                "print(confusions.most_common(5))"
                            ),
                            "explanation": "The most common confused pairs tell you exactly which specialist boundary needs more few-shot examples.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write 4 few-shot routing examples for boundary cases between a 'sales' and 'support' specialist.",
                            "difficulty": "easy",
                            "hint": "Think of requests that mention both wanting to buy something and having a problem with an existing purchase.",
                        },
                        {
                            "prompt": "Build a small labeled test set (10 examples) and compute routing accuracy for a router with and without few-shot examples, then compare.",
                            "difficulty": "medium",
                            "hint": "Keep everything else in the prompt identical between the two runs so the comparison isolates the effect of the examples.",
                        },
                    ],
                    "resources": [
                        {"title": "OpenAI Cookbook: Techniques to improve reliability", "url": "https://cookbook.openai.com/articles/techniques_to_improve_reliability", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "specialist-agents",
            "title": "Specialist Agents",
            "description": "Building narrow, reliable agents scoped to a single job and a small tool set.",
            "order_index": 4,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "building-narrow-reliable-specialists",
                    "title": "Building Narrow, Reliable Specialists",
                    "description": "Designing a specialist agent's prompt, scope, and success criteria.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Write a specialist system prompt scoped to a single responsibility",
                        "Define clear success and refusal criteria for a specialist",
                        "Implement a specialist as a self-contained, testable function",
                    ],
                    "content_markdown": """
## Narrow beats general

A specialist agent's entire value proposition is that it is good at one thing because it isn't
trying to be good at everything. A billing specialist should refuse (politely, and by routing
back to the supervisor) any request that isn't actually about billing, even if it technically
could produce an answer. Scope creep in a specialist's prompt is how multi-agent systems slide
back into single-agent problems, just with extra steps.

```python
BILLING_SPECIALIST_PROMPT = \"\"\"
You are the billing specialist. You handle: refunds, invoice questions, payment disputes,
and subscription charges. You do NOT handle: technical bugs, account access issues, or
general product questions — if asked about those, respond with a REFUSE action so the
supervisor can re-route.

You have access to: lookup_order, issue_refund (requires amount <= 100 without approval,
escalate above that), get_invoice.
\"\"\"
```

## Self-contained and testable

Implement each specialist as a function with a clear input and output type, independent of how
it's invoked. This lets you unit test a specialist in isolation, without spinning up the whole
supervisor system.

```python
from pydantic import BaseModel

class SpecialistResult(BaseModel):
    handled: bool
    output: str
    needs_escalation: bool = False

def billing_specialist(request: str, context: dict) -> SpecialistResult:
    if not is_billing_related(request):
        return SpecialistResult(handled=False, output="not a billing request")
    order = lookup_order(context["order_id"])
    if order.refund_amount > 100:
        return SpecialistResult(handled=True, output="pending manager approval", needs_escalation=True)
    issue_refund(order.id, order.refund_amount)
    return SpecialistResult(handled=True, output=f"Refunded ${order.refund_amount}")
```

## Success and refusal criteria as part of the contract

Every specialist should have documented, testable criteria for what counts as success, partial
success, and refusal — not just a prompt describing its job. This makes specialists behave
like real software components: you can write assertions against `SpecialistResult` the same
way you'd test any other function, independent of the LLM's exact wording.

## Specialists own their tools, not the supervisor

Keep tool definitions colocated with the specialist that uses them, not in a shared global
registry the supervisor also sees. This keeps the supervisor's own context small (it never
needs to know that `issue_refund` takes an `amount` and a `reason` — only that billing
handles refunds) and prevents tool-set overload from creeping back into the router.
""",
                    "examples": [
                        {
                            "title": "Example: unit testing a specialist without the supervisor",
                            "code": (
                                "def test_billing_specialist_refuses_non_billing():\n"
                                "    result = billing_specialist('my app keeps crashing', context={})\n"
                                "    assert result.handled is False\n\n"
                                "def test_billing_specialist_escalates_large_refund():\n"
                                "    result = billing_specialist('refund my order', {'order_id': 'ord_9'})\n"
                                "    assert result.needs_escalation is True"
                            ),
                            "explanation": "Because the specialist is a plain function with a typed return value, it's testable with ordinary unit tests — no need to mock the whole multi-agent graph.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Write a system prompt for a 'technical support' specialist, including at least one explicit thing it does NOT handle.",
                            "difficulty": "easy",
                            "hint": "Mirror the billing example's structure: handles / does not handle / available tools.",
                        },
                        {
                            "prompt": "Implement a `SpecialistResult`-returning function for a scheduling specialist that books meetings, and write two unit tests for it (success and refusal cases).",
                            "difficulty": "medium",
                            "hint": "Refusal should trigger when the request isn't actually about scheduling, mirroring the billing_specialist example.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Multi-agent tutorials", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/", "resource_type": "tutorial"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "tool-scoping-per-specialist",
                    "title": "Tool Scoping per Specialist",
                    "description": "Deciding which tools belong to which specialist, and how to avoid duplication and drift.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Apply the principle of least privilege to specialist tool access",
                        "Avoid duplicate or conflicting tool implementations across specialists",
                        "Design shared low-level tools reused by multiple specialists safely",
                    ],
                    "content_markdown": """
## Least privilege for tools, not just data

Security discussions about agents usually focus on data access, but tool access deserves the
same discipline. A research specialist that also has `issue_refund` in its tool list is a risk
even if its prompt never asks it to use that tool — a sufficiently unusual input, or a prompt
injection from a retrieved document, could still coax the model into calling it. Give each
specialist only the tools its job requires, full stop.

```python
RESEARCH_TOOLS = [search_web, search_internal_kb, fetch_url]
BILLING_TOOLS = [lookup_order, issue_refund, get_invoice]
# research_agent should never be constructed with BILLING_TOOLS, even for convenience
```

## Shared low-level tools

Some tools are genuinely needed by multiple specialists — `lookup_order` might be used by both
billing and technical support. That's fine; share the *implementation*, but still declare it
explicitly in each specialist's own tool list rather than importing a giant shared bundle. The
goal is that anyone reading a specialist's definition can see its complete tool surface without
cross-referencing another file.

```python
# shared_tools.py
def lookup_order(order_id: str) -> Order: ...

# billing_agent.py
from shared_tools import lookup_order, issue_refund, get_invoice
BILLING_TOOLS = [lookup_order, issue_refund, get_invoice]

# technical_agent.py
from shared_tools import lookup_order, get_error_logs
TECHNICAL_TOOLS = [lookup_order, get_error_logs]
```

## Avoiding drift between similar tools

When two specialists need conceptually similar but not identical tools (e.g., billing's
`search_invoices` vs research's `search_web`), give them clearly distinct names and
docstrings, even if implemented similarly under the hood. Ambiguous or overlapping tool names
across specialists reintroduce exactly the tool-selection confusion that motivated splitting
into specialists in the first place — the confusion just moves from "which of 20 tools" to
"which of 2 near-identical tools across agents," which is arguably worse because it's less
visible in a code review.

## Auditing tool access over time

As a system grows, periodically print each specialist's tool list and review it like a
permissions audit. It's easy for a tool to get added to a specialist "just for this one edge
case" and never removed. Treat specialist tool lists as something that should shrink or stay
flat over time, not silently grow.
""",
                    "examples": [
                        {
                            "title": "Example: a simple tool-access audit",
                            "code": (
                                "SPECIALISTS = {'billing': BILLING_TOOLS, 'research': RESEARCH_TOOLS, 'technical': TECHNICAL_TOOLS}\n\n"
                                "def audit_tool_access():\n"
                                "    for name, tools in SPECIALISTS.items():\n"
                                "        tool_names = [t.__name__ for t in tools]\n"
                                "        print(f'{name}: {tool_names}')"
                            ),
                            "explanation": "A one-function audit like this, run in CI or reviewed at each release, catches tool-list creep before it becomes a security review problem.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List the minimal tool set a 'scheduling' specialist needs versus a 'billing' specialist, and identify any tool that would be a least-privilege violation if shared.",
                            "difficulty": "easy",
                            "hint": "Ask, for each tool, whether the specialist's stated job actually requires it.",
                        },
                        {
                            "prompt": "Write the `audit_tool_access` function to also flag any tool that appears in more than two specialists' lists, as a signal it might need to become a shared, explicitly-named utility.",
                            "difficulty": "medium",
                            "hint": "Build a Counter across all tool names first, then filter for count > 2.",
                        },
                    ],
                    "resources": [
                        {"title": "OWASP: LLM excessive agency risks", "url": "https://owasp.org/www-project-top-10-for-large-language-model-applications/", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 0.8}, {"slug": "planning", "weight": 0.2}],
                },
            ],
        },
        {
            "slug": "delegation",
            "title": "Delegation",
            "description": "Patterns for breaking a task down and handing pieces to the right agent with the right context.",
            "order_index": 5,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "task-delegation-patterns",
                    "title": "Task Delegation Patterns",
                    "description": "Static, dynamic, and recursive delegation strategies.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Compare static, dynamic, and recursive delegation strategies",
                        "Decide how much of a task to delegate at once versus incrementally",
                        "Recognize when recursive delegation risks infinite loops",
                    ],
                    "content_markdown": """
## Static vs. dynamic delegation

**Static delegation** decomposes the whole task into sub-tasks up front, before any specialist
runs, then dispatches them (possibly in parallel). This works well when the sub-tasks are
genuinely independent — "research competitor A, competitor B, and competitor C" can be three
parallel research calls with no dependency between them.

**Dynamic delegation** decomposes one step at a time, using the result of each step to decide
the next. This is necessary when later sub-tasks depend on earlier results — you can't decide
which specialist handles "fix the bug" until a research step has identified what the bug even
is.

```python
# Static: decompose once, dispatch in parallel
subtasks = ["competitor A pricing", "competitor B pricing", "competitor C pricing"]
results = [research_agent.run(t) for t in subtasks]  # could be parallelized

# Dynamic: each step's output shapes the next decision
finding = research_agent.run("investigate the reported outage")
if finding.root_cause == "database":
    fix = database_specialist.run(finding)
else:
    fix = infra_specialist.run(finding)
```

## Recursive delegation

A supervisor can itself be a specialist invoked by a higher-level supervisor — this is how
hierarchical topologies are built. Recursive delegation is powerful but needs an explicit depth
limit; without one, a supervisor that occasionally delegates back "up" the chain (directly or
indirectly) can loop indefinitely, silently burning tokens until a timeout or budget kills it.

```python
def delegate(task, depth=0, max_depth=4):
    if depth >= max_depth:
        raise DelegationDepthExceeded(task)
    decision = route(task)
    if decision.specialist == "sub_supervisor":
        return delegate(task, depth=depth + 1, max_depth=max_depth)
    return SPECIALISTS[decision.specialist].run(task)
```

## How much to delegate at once

Delegating an entire vague goal ("improve our pricing page") to one specialist produces worse
results than delegating a well-scoped sub-task ("rewrite the headline on the pricing page to
emphasize the annual discount") because the specialist has to do implicit planning it wasn't
designed for. Planning and delegation are separate skills — let a planning step (often the
supervisor itself, or a dedicated planner agent) produce concrete sub-tasks, and let
specialists execute concrete sub-tasks, not raw goals.
""",
                    "examples": [
                        {
                            "title": "Example: guarding against unbounded recursive delegation",
                            "code": (
                                "class DelegationDepthExceeded(Exception):\n"
                                "    pass\n\n"
                                "try:\n"
                                "    result = delegate(task, max_depth=4)\n"
                                "except DelegationDepthExceeded:\n"
                                "    result = 'Could not resolve after 4 levels of delegation; escalating to a human.'"
                            ),
                            "explanation": "An explicit depth ceiling turns a silent infinite loop into a clear, handleable exception.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Given the goal 'launch a referral program', write 4 concrete, delegable sub-tasks a planner should produce before any specialist runs.",
                            "difficulty": "easy",
                            "hint": "Each sub-task should be specific enough that a specialist wouldn't need to ask a clarifying question.",
                        },
                        {
                            "prompt": "Modify the `delegate` function to log the full delegation chain (task, depth, chosen specialist) so a run can be replayed for debugging.",
                            "difficulty": "medium",
                            "hint": "Accumulate a trace list passed through each recursive call, or use a module-level logger keyed by a run id.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Planning agents", "url": "https://langchain-ai.github.io/langgraph/tutorials/plan-and-execute/plan-and-execute/", "resource_type": "tutorial"}
                    ],
                    "skills": [{"slug": "planning", "weight": 0.7}, {"slug": "multi-agent-systems", "weight": 0.5}],
                },
                {
                    "slug": "handoffs-and-context-transfer",
                    "title": "Handoffs and Context Transfer",
                    "description": "Deciding exactly what context a delegated agent needs, and packaging it correctly.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement a context-transfer function for a delegation handoff",
                        "Avoid both under-sharing and over-sharing context at a handoff boundary",
                        "Preserve traceability of a sub-task back to its originating goal",
                    ],
                    "content_markdown": """
## The Goldilocks problem of context transfer

Hand off too little context and the receiving specialist re-asks questions already answered
upstream, or acts on stale assumptions. Hand off too much (the entire conversation, every tool
call, every intermediate thought) and you dilute the specialist's context exactly the way a
single overloaded agent would be diluted — you've just moved the problem. A handoff function's
job is to select, not just forward.

```python
from pydantic import BaseModel

class DelegationHandoff(BaseModel):
    origin_goal: str          # the top-level goal, for traceability
    subtask: str               # the concrete, scoped task for this specialist
    relevant_facts: list[str]  # only facts this specialist actually needs
    constraints: list[str] = []

def build_handoff(goal: str, subtask: str, full_history: list[AgentMessage]) -> DelegationHandoff:
    facts = extract_relevant_facts(subtask, full_history)  # LLM or rule-based filter
    return DelegationHandoff(origin_goal=goal, subtask=subtask, relevant_facts=facts)
```

## Preserving traceability

Always carry `origin_goal` through every handoff, even many levels deep. When a specialist
three hops downstream produces something wrong, you need to be able to trace it back to the
original user request without replaying the entire message bus. This is cheap to include and
expensive to reconstruct after the fact.

## Constraints travel with the task, not just facts

It's easy to forget that delegation needs to carry *constraints* (budget limits, tone
requirements, deadlines, things explicitly ruled out) alongside facts. A specialist that
receives "write the announcement" without the constraint "do not mention pricing yet" can
easily produce something that has to be redone. Treat constraints as a first-class field in
your handoff schema, not something buried in prose.

## Testing handoff quality directly

Because `build_handoff` returns a typed object, you can test it in isolation: feed it a known
history and goal, and assert the extracted facts contain what the specialist needs and exclude
irrelevant noise. This catches context-transfer bugs long before they show up as a confusing
wrong answer three agents downstream.
""",
                    "examples": [
                        {
                            "title": "Example: testing that a handoff carries constraints correctly",
                            "code": (
                                "def test_handoff_preserves_constraints():\n"
                                "    history = [AgentMessage(sender='user', role='task',\n"
                                "               content='Draft the announcement, do not mention pricing yet')]\n"
                                "    handoff = build_handoff('launch announcement', 'write announcement copy', history)\n"
                                "    assert any('pricing' in c.lower() for c in handoff.constraints)"
                            ),
                            "explanation": "This kind of test catches a very common real bug: constraints mentioned once early in a conversation quietly getting dropped by the time a specialist several hops downstream receives its handoff.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Extend `DelegationHandoff` with a `deadline: str | None` field and update `build_handoff` to populate it when the history mentions a deadline.",
                            "difficulty": "easy",
                            "hint": "A simple keyword or LLM-extraction check for phrases like 'by Friday' or 'deadline' is enough for a first pass.",
                        },
                        {
                            "prompt": "Write `extract_relevant_facts` as a rule-based function (no LLM call) that pulls only messages whose content overlaps with keywords in the subtask, and discuss one weakness of this approach compared to an LLM-based extractor.",
                            "difficulty": "hard",
                            "hint": "Keyword overlap misses paraphrases and synonyms — a fact stated differently than the subtask's wording will be missed.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: State and context passing", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#state", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "planning", "weight": 0.6}, {"slug": "multi-agent-systems", "weight": 0.6}],
                },
            ],
        },
        {
            "slug": "orchestration",
            "title": "Orchestration",
            "description": "Building the graphs that coordinate agent execution order, branching, and parallelism.",
            "order_index": 6,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "orchestrator-worker-pattern-in-langgraph",
                    "title": "Orchestrator-Worker Pattern in LangGraph",
                    "description": "Implementing a supervisor-worker graph with LangGraph's StateGraph.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 35,
                    "learning_objectives": [
                        "Build a StateGraph with a supervisor node and multiple worker nodes",
                        "Use conditional edges to implement routing",
                        "Run worker nodes in parallel where the task allows it",
                    ],
                    "content_markdown": """
## A minimal orchestrator graph

LangGraph models an orchestrator-worker system as a `StateGraph`: nodes are agents, edges
define control flow, and a shared state object flows through every node.

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Literal

class OrchestratorState(TypedDict):
    task: str
    route: str
    result: str

def supervisor_node(state: OrchestratorState) -> OrchestratorState:
    decision = route(state["task"])
    return {**state, "route": decision.specialist}

def research_node(state: OrchestratorState) -> OrchestratorState:
    output = research_agent.run(state["task"])
    return {**state, "result": output}

def billing_node(state: OrchestratorState) -> OrchestratorState:
    output = billing_agent.run(state["task"])
    return {**state, "result": output}

graph = StateGraph(OrchestratorState)
graph.add_node("supervisor", supervisor_node)
graph.add_node("research", research_node)
graph.add_node("billing", billing_node)

def pick_route(state: OrchestratorState) -> Literal["research", "billing"]:
    return state["route"]

graph.add_conditional_edges("supervisor", pick_route, {"research": "research", "billing": "billing"})
graph.add_edge("research", END)
graph.add_edge("billing", END)
graph.set_entry_point("supervisor")

app = graph.compile()
result = app.invoke({"task": "What's my refund status?", "route": "", "result": ""})
```

## Conditional edges are the routing mechanism

`add_conditional_edges` is where the topology decision from earlier lessons becomes real code:
the function passed to it (`pick_route` above) is exactly the supervisor's routing decision,
translated into which node executes next. Keep this function pure and cheap — it should read
state and return a key, not do LLM calls itself; the LLM call belongs in `supervisor_node`.

## Fan-out for parallel workers

When sub-tasks are independent (the static delegation case from the previous module), LangGraph
can fan out to multiple worker nodes concurrently using the `Send` API, then fan back in once
all branches complete.

```python
from langgraph.types import Send

def fan_out(state: OrchestratorState):
    return [Send("research", {"task": t}) for t in state["subtasks"]]

graph.add_conditional_edges("supervisor", fan_out)
```

Each `Send` spins up an independent invocation of the target node with its own state slice,
and LangGraph merges results back according to the state's reducer functions once all branches
finish — the mechanism you'll use for shared state in the next module.

## Compiling and visualizing

Always call `app.get_graph().draw_mermaid()` (or the ASCII equivalent) during development.
Multi-agent graphs get hard to hold in your head past 5-6 nodes, and a visual diagram catches
wiring mistakes — a missing edge, an unreachable node — far faster than reading code.
""",
                    "examples": [
                        {
                            "title": "Example: printing the compiled graph structure for a sanity check",
                            "code": (
                                "print(app.get_graph().draw_mermaid())\n"
                                "# Inspect the printed diagram before running real traffic through it —\n"
                                "# a node with no outgoing edge, or two nodes both routing to END\n"
                                "# incorrectly, jump out visually far faster than in code review."
                            ),
                            "explanation": "Visualizing the graph is a five-second check that catches structural wiring bugs before they become runtime surprises.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a third worker node, 'technical', to the graph above, including its routing branch.",
                            "difficulty": "easy",
                            "hint": "You need a new node function, an entry in the conditional edges mapping, and an edge to END.",
                        },
                        {
                            "prompt": "Implement fan-out for a case where the supervisor splits a research task into 3 parallel sub-queries, and write the reducer needed to merge 3 results back into a single list in shared state.",
                            "difficulty": "hard",
                            "hint": "Use Annotated[list[str], operator.add] as the state field's type so LangGraph knows how to merge parallel writes.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: StateGraph API reference", "url": "https://langchain-ai.github.io/langgraph/reference/graphs/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "planning", "weight": 0.6}, {"slug": "multi-agent-systems", "weight": 0.8}],
                },
                {
                    "slug": "dynamic-vs-static-orchestration-graphs",
                    "title": "Dynamic vs. Static Orchestration Graphs",
                    "description": "When the graph structure itself needs to change at runtime versus stay fixed.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Distinguish a fixed graph topology from one that changes shape per run",
                        "Recognize the debugging cost of highly dynamic orchestration",
                        "Choose the least dynamic graph structure that still solves the problem",
                    ],
                    "content_markdown": """
## Fixed topology, dynamic routing

Most systems that feel "dynamic" are actually a fixed graph (the same nodes and edges every
run) with dynamic *routing* (which edge gets taken depends on state). This is the pattern from
the previous lesson — `add_conditional_edges` picks among a known, finite set of pre-wired
paths. This is easy to test exhaustively: enumerate every possible route value and verify each
leads somewhere sensible.

## Truly dynamic graphs

A smaller set of problems need the graph's *shape* to change per run — for instance, an agent
that decides at runtime how many parallel research sub-agents to spawn based on how many
distinct sub-questions it identifies. LangGraph's `Send` API supports this (as seen in the
fan-out example), generating a variable number of node invocations rather than choosing among
a fixed set of pre-wired edges.

```python
def fan_out(state):
    # number of Send() calls varies per run based on the plan the LLM produced
    return [Send("research", {"task": q}) for q in state["subquestions"]]
```

## The debugging cost of dynamic shape

A graph whose shape changes per run is harder to reason about than one whose shape is fixed
and only its routing varies: you can't draw one diagram and trust it describes every
execution, and a bug that only appears when exactly 7 sub-questions are generated can be hard
to reproduce. Use dynamic shape only where the problem genuinely requires a variable number of
parallel branches — don't reach for `Send`-based fan-out just because it feels more flexible.

## A practical rule

Default to a fixed graph with conditional routing. Introduce dynamic fan-out only for the
specific sub-problem that needs a variable-width parallel step (like "research N independent
sub-questions"), and keep everything else in that same graph on fixed edges. Mixing a small
amount of dynamic shape into an otherwise fixed graph is far more debuggable than making the
whole graph dynamic.

## Testing implications

For fixed-topology graphs, write tests that enumerate every routing branch and assert each
reaches a terminal state correctly — this is complete, exhaustive coverage. For the dynamic
fan-out portion, test the *fan-out function* in isolation (given a state, does it produce the
right number and shape of `Send` calls) separately from testing the worker node it dispatches
to, since testing them together multiplies the cases you need to cover.
""",
                    "examples": [
                        {
                            "title": "Example: exhaustive routing test for a fixed graph",
                            "code": (
                                "@pytest.mark.parametrize('route', ['research', 'billing', 'technical'])\n"
                                "def test_all_routes_reach_end(route):\n"
                                "    state = {'task': 'x', 'route': route, 'result': ''}\n"
                                "    final = app.invoke(state)\n"
                                "    assert final['result'] != ''"
                            ),
                            "explanation": "Because the graph's routes are a known, finite set, a parametrized test can exhaustively cover every branch — something impossible for a dynamically-shaped graph.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Describe a real task where a fixed-topology graph with conditional routing is sufficient, and one where true dynamic fan-out is necessary. Justify each.",
                            "difficulty": "easy",
                            "hint": "The fan-out case should involve a variable, data-dependent number of parallel sub-tasks.",
                        },
                        {
                            "prompt": "Write a unit test for the `fan_out` function above that asserts it produces exactly as many `Send` calls as there are subquestions in state, without invoking the actual research agent.",
                            "difficulty": "medium",
                            "hint": "Call fan_out directly with a hand-built state dict and inspect the length and .arg of the returned Send objects.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Map-reduce / Send patterns", "url": "https://langchain-ai.github.io/langgraph/how-tos/graph-api/#map-reduce-and-the-send-api", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "planning", "weight": 0.6}, {"slug": "multi-agent-systems", "weight": 0.6}],
                },
            ],
        },
        {
            "slug": "shared-state",
            "title": "Shared State",
            "description": "Designing the state schema multiple agents read and write without stepping on each other.",
            "order_index": 7,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "designing-a-shared-state-schema",
                    "title": "Designing a Shared State Schema",
                    "description": "Building a TypedDict/Pydantic state schema with reducers for concurrent writes.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Design a shared state schema for a multi-agent graph",
                        "Use reducer functions to merge concurrent writes safely",
                        "Avoid state bloat by scoping fields to what agents actually need",
                    ],
                    "content_markdown": """
## State is the contract between agents

In a LangGraph system, the state schema *is* the interface every agent programs against. Get
it wrong and you get subtle bugs: two agents overwriting each other's fields, a specialist
reading a field that hasn't been populated yet, or state ballooning until every node pays a
context-size tax for fields it never uses.

```python
from typing import TypedDict, Annotated
import operator

class TeamState(TypedDict):
    task: str
    research_findings: Annotated[list[str], operator.add]  # concurrent writes append
    final_answer: str
    errors: Annotated[list[str], operator.add]
```

## Reducers resolve concurrent writes

When two parallel branches (from a `Send` fan-out) both write to `research_findings` in the
same step, LangGraph needs to know how to combine them — that's what `Annotated[..., operator.add]`
declares: concatenate the lists rather than one write silently clobbering the other. Every
field a parallel branch can write to needs an explicit reducer; fields only ever written by one
node at a time can stay plain.

```python
class TeamState(TypedDict):
    task: str
    # plain field: only the supervisor node ever writes this, no concurrent writers
    route: str
    # reducer field: multiple parallel research branches can each append
    research_findings: Annotated[list[str], operator.add]
```

Forgetting a reducer on a field that concurrent branches write to is one of the most common
LangGraph bugs — it doesn't crash, it just silently loses data, since without a reducer, the
last write wins.

## Scope state fields to actual need

Resist adding a field to shared state "in case a future agent needs it." Every field is context
every node has to at least skim when deciding what's relevant, and it's much easier to add a
field later than to safely remove one that some node may have started depending on. Start
minimal: task, routing decision, results, errors — and add fields only when a concrete agent
needs to read or write them.

## Namespacing per-agent scratch space

For agents that need private working memory that shouldn't leak into what other agents see,
nest it under a per-agent key rather than mixing it into the flat top level.

```python
class TeamState(TypedDict):
    task: str
    final_answer: str
    # each specialist's private scratch space, never read by other agents
    _research_scratch: dict
    _billing_scratch: dict
```

The underscore prefix is a convention, not enforcement — document clearly that these fields are
private, and keep synthesis and routing logic from ever reading them.
""",
                    "examples": [
                        {
                            "title": "Example: verifying a reducer merges concurrent writes correctly",
                            "code": (
                                "state = {'research_findings': ['fact A']}\n"
                                "update_1 = {'research_findings': ['fact B']}\n"
                                "update_2 = {'research_findings': ['fact C']}\n"
                                "# LangGraph applies operator.add across both updates before the next node runs\n"
                                "merged = state['research_findings'] + update_1['research_findings'] + update_2['research_findings']\n"
                                "assert merged == ['fact A', 'fact B', 'fact C']"
                            ),
                            "explanation": "This mirrors what LangGraph's reducer machinery does internally: it never overwrites a list field, it folds concurrent partial updates into it using the declared operator.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a `total_cost_usd: Annotated[float, operator.add]` field to TeamState and explain why a plain float field (no reducer) would be dangerous here if two agents run in parallel.",
                            "difficulty": "easy",
                            "hint": "Without a reducer, the second parallel write would replace, not add to, the first — silently undercounting cost.",
                        },
                        {
                            "prompt": "Design a state schema for a 3-agent content pipeline (outline, draft, edit) where only the final agent's output should be shown to the user, and explain your field choices.",
                            "difficulty": "medium",
                            "hint": "Consider which fields need reducers (none, if each agent runs sequentially and writes a distinct field) versus which are purely internal.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: State reducers", "url": "https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}, {"slug": "multi-agent-systems", "weight": 0.5}],
                },
                {
                    "slug": "state-isolation-vs-shared-scratchpads",
                    "title": "State Isolation vs. Shared Scratchpads",
                    "description": "Deciding when agents should share a scratchpad versus keep fully isolated working memory.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Compare shared scratchpad and isolated state designs",
                        "Identify the risks of a fully shared scratchpad across agents",
                        "Choose the right isolation level for a given multi-agent task",
                    ],
                    "content_markdown": """
## Two ends of a spectrum

**Fully shared scratchpad**: every agent reads and writes the same working-memory space, seeing
everything every other agent has written. **Fully isolated state**: each agent only sees its own
input and produces its own output, with no visibility into other agents' intermediate work.
Real systems live somewhere between these, and where you land is a design decision with real
consequences.

## The case for shared scratchpads

A shared scratchpad helps when agents genuinely benefit from each other's partial progress —
a writer/critic pair iterating on the same draft, or a research team where seeing what other
sub-agents have already found prevents duplicate work. It reduces redundant tool calls and lets
later agents build directly on earlier partial results instead of waiting for a full summary.

## The case for isolation

Isolation helps when agents need to work independently and simultaneously without interference
— parallel research branches investigating unrelated sub-questions gain nothing from seeing
each other's scratch space, and sharing it just adds noise and risks one branch's assumptions
leaking into another's, or context growing unnecessarily for every branch. Isolation also makes
each agent's behavior easier to test and reason about independently, since its inputs are fully
determined by its own state slice.

```python
# Isolated: each parallel branch gets only its own slice
def fan_out(state):
    return [Send("research", {"subquestion": q}) for q in state["subquestions"]]
# research node only ever sees {"subquestion": q} — no access to siblings' progress

# Shared: all branches read/write the same scratchpad field
class SharedScratchState(TypedDict):
    scratchpad: Annotated[list[str], operator.add]
# every research node appends to and can read the same growing list
```

## A practical default

Default to isolation for parallel, independent sub-tasks (the "map" side of a map-reduce
pattern), and use a shared scratchpad only for genuinely collaborative, sequential pairs (like
writer/critic) where agents are meant to build on each other turn by turn. Mixing the two
carelessly — giving parallel branches a shared scratchpad "just in case" — reintroduces the
race-condition and context-bloat problems isolation was meant to solve.

## Scratchpad hygiene

If you do use a shared scratchpad, cap its size and periodically summarize/prune it, the same
way you would the message bus from the communication module. An ever-growing shared scratchpad
is one of the fastest ways for a multi-agent system to silently regress into the exact context
dilution problem that motivated moving to multiple agents in the first place.
""",
                    "examples": [
                        {
                            "title": "Example: pruning a shared scratchpad before it grows unbounded",
                            "code": (
                                "def prune_scratchpad(state: SharedScratchState, max_entries: int = 20):\n"
                                "    if len(state['scratchpad']) > max_entries:\n"
                                "        summary = summarize('\\n'.join(state['scratchpad'][:-max_entries]))\n"
                                "        state['scratchpad'] = [summary] + state['scratchpad'][-max_entries:]\n"
                                "    return state"
                            ),
                            "explanation": "Summarizing and dropping older entries keeps a shared scratchpad bounded in size while preserving the gist of earlier contributions.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a writer/critic loop where the critic needs to see the writer's full draft history to avoid repeating the same feedback, decide: shared scratchpad or isolated state? Justify.",
                            "difficulty": "easy",
                            "hint": "Consider whether the critic's value depends on seeing prior iterations, not just the latest draft.",
                        },
                        {
                            "prompt": "Implement `prune_scratchpad` so it's called automatically as a LangGraph node inserted after every 3rd agent turn.",
                            "difficulty": "medium",
                            "hint": "You can add a counter field to state and route to a pruning node conditionally based on counter % 3 == 0.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Multi-agent state sharing", "url": "https://langchain-ai.github.io/langgraph/concepts/multi_agent/#shared-state", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "state", "weight": 1.0}, {"slug": "multi-agent-systems", "weight": 0.5}],
                },
            ],
        },
        {
            "slug": "conflict-handling",
            "title": "Conflict Handling",
            "description": "Detecting and resolving disagreement between agents, and escalating what can't be resolved automatically.",
            "order_index": 8,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "detecting-and-resolving-agent-conflicts",
                    "title": "Detecting and Resolving Agent Conflicts",
                    "description": "Recognizing when two agents disagree and applying a resolution strategy.",
                    "lesson_type": "reading",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Identify the common shapes of multi-agent conflict",
                        "Apply a resolution strategy appropriate to the conflict type",
                        "Design a system that surfaces unresolved conflicts rather than guessing",
                    ],
                    "content_markdown": """
## What agent conflict looks like

Conflict in a multi-agent system usually takes one of three shapes. **Factual conflict**: two
agents state contradictory facts (research agent says the API supports webhooks, technical
agent's docs lookup says it doesn't). **Recommendation conflict**: agents agree on facts but
disagree on the right action (billing agent recommends a partial refund, policy agent flags it
as against policy). **Resource conflict**: two agents attempt to act on the same resource in a
way that isn't safely composable (both try to update the same database row).

## Detecting conflict before it reaches the user

The cheapest place to catch conflict is at the synthesis step, before a final answer goes out.
A synthesis prompt that explicitly asks the model to check for contradictions between
specialist outputs — rather than just concatenating them — catches a meaningful fraction of
factual conflicts.

```python
SYNTHESIS_PROMPT = \"\"\"
You are combining outputs from multiple specialist agents into one final answer.
Before writing the final answer, check: do any of the specialist outputs below
contradict each other? If so, do not silently pick one — flag it explicitly.

Specialist outputs:
{outputs}
\"\"\"

class SynthesisResult(BaseModel):
    final_answer: str
    conflict_detected: bool
    conflict_description: str = ""
```

## Resolution strategies by conflict type

Factual conflicts are best resolved by re-querying a more authoritative source (or the same
source with a more specific query) rather than picking one agent's claim by default — trusting
whichever agent "sounds more confident" is not a real resolution strategy, since LLM confidence
in phrasing doesn't correlate reliably with correctness. Recommendation conflicts are resolved
by an explicit precedence rule (e.g., policy agent always wins over billing agent on
policy questions) decided at design time, not improvised at runtime. Resource conflicts need a
concurrency control mechanism (locking, optimistic version checks) rather than a "resolution
strategy" at all — that's a systems problem, not an agent-reasoning problem.

```python
PRECEDENCE = {"policy": 3, "billing": 2, "research": 1}

def resolve_recommendation_conflict(outputs: list[SpecialistResult]) -> SpecialistResult:
    return max(outputs, key=lambda o: PRECEDENCE.get(o.source, 0))
```

## When to escalate instead of resolving automatically

Not every conflict should be silently auto-resolved. High-stakes conflicts (anything touching
money, legal commitments, or irreversible actions) should be surfaced to a human reviewer with
both conflicting outputs shown side by side, rather than resolved by a precedence rule the user
never sees. Build the `conflict_detected` flag from the synthesis step into a real escalation
path, not just a log line.
""",
                    "examples": [
                        {
                            "title": "Example: routing a detected conflict to human review",
                            "code": (
                                "synthesis = synthesize(user_request, specialist_outputs)\n"
                                "if synthesis.conflict_detected and involves_money(user_request):\n"
                                "    queue_for_human_review(user_request, specialist_outputs, synthesis.conflict_description)\n"
                                "    return 'This needs a quick human check before I can confirm — routing it now.'"
                            ),
                            "explanation": "Gating escalation on both 'conflict detected' and 'high stakes' avoids flooding a human queue with every minor factual discrepancy while still catching the ones that matter.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Classify each as factual, recommendation, or resource conflict: (a) two agents give different account balances, (b) two agents both try to append to the same order's status field, (c) one agent recommends approving a loan, another recommends denying it.",
                            "difficulty": "easy",
                            "hint": "Ask whether the disagreement is about a fact, a judgment call, or simultaneous access to the same piece of data.",
                        },
                        {
                            "prompt": "Design a precedence table for a system with 'legal', 'sales', and 'support' agents, and justify the ordering for at least one pair.",
                            "difficulty": "medium",
                            "hint": "Precedence should usually follow which agent bears more downstream risk if overridden.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Human-in-the-loop", "url": "https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
                {
                    "slug": "voting-arbitration-and-escalation",
                    "title": "Voting, Arbitration, and Escalation",
                    "description": "Implementing multi-agent voting and an arbitrator agent for cases precedence rules can't settle.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement a voting mechanism across multiple agent outputs",
                        "Build a dedicated arbitrator agent for complex disagreements",
                        "Design an escalation path with a clear audit trail",
                    ],
                    "content_markdown": """
## Voting across redundant agents

For high-stakes or ambiguous decisions, running the same query through multiple independent
agent instances (or the same agent with different prompts/temperatures) and voting on the
outcome improves reliability over trusting a single run. This trades cost (N calls instead of
1) for a meaningful reduction in single-run errors.

```python
from collections import Counter

def vote(task: str, n: int = 3) -> str:
    results = [specialist_agent.run(task) for _ in range(n)]
    votes = Counter(r.decision for r in results)
    winner, count = votes.most_common(1)[0]
    if count <= n / 2:
        return "no_majority"  # treat a split vote as its own outcome, don't force a winner
    return winner
```

Voting works best for decisions with a small, discrete outcome space (approve/deny,
categorize into one of five buckets) — it doesn't meaningfully apply to open-ended text
generation, where "majority vote" isn't well-defined.

## A dedicated arbitrator agent

When precedence rules aren't enough — two specialists of *equal* precedence disagree, or the
conflict is nuanced enough that a fixed rule would be too blunt — introduce a separate
arbitrator agent whose only job is to look at the conflicting outputs and decide, with
reasoning, which one to trust or how to merge them. Keeping arbitration as its own agent (not
folded into the supervisor's synthesis step) keeps its prompt focused purely on adjudication.

```python
ARBITRATOR_PROMPT = \"\"\"
Two specialist agents produced conflicting outputs for the same request. Your only job is
to decide which is correct, or whether neither is, and explain why. Do not soften or
average the disagreement — pick a side or explicitly say the conflict needs a human.
\"\"\"

class ArbitrationResult(BaseModel):
    winner: Literal["a", "b", "neither"]
    reasoning: str
    needs_human: bool
```

## Escalation with a full audit trail

Whatever your escalation path, log everything needed to reconstruct the decision later: the
original request, every specialist's output, the arbitrator's reasoning (if any), and the
final resolution. Multi-agent conflicts are exactly the failures a team will need to
investigate after the fact, and a resolution with no audit trail is nearly as bad as no
resolution at all — you can't improve precedence rules or specialist prompts based on
conflicts you can't reconstruct.

## Cost-awareness in conflict handling

Voting and arbitration both add LLM calls on top of an already multi-call system. Reserve
them for genuinely high-stakes or genuinely ambiguous cases — gate voting behind a check like
"does this decision involve money or an irreversible action," rather than applying it
universally, or the cost multiplier compounds across every request in the system.
""",
                    "examples": [
                        {
                            "title": "Example: full conflict-handling audit record",
                            "code": (
                                "audit_record = {\n"
                                "    'request': user_request,\n"
                                "    'specialist_outputs': [o.model_dump() for o in specialist_outputs],\n"
                                "    'arbitration': arbitration_result.model_dump() if arbitration_result else None,\n"
                                "    'final_resolution': final_answer,\n"
                                "    'timestamp': time.time(),\n"
                                "}\n"
                                "audit_log.write(audit_record)"
                            ),
                            "explanation": "Persisting the full context of every conflict resolution turns each incident into training data for improving precedence rules and specialist prompts later.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement `vote` for a 3-way categorical decision and write a test asserting that a 2-1 split returns the majority option while a genuine no-majority case (e.g. 3 different results) returns 'no_majority'.",
                            "difficulty": "medium",
                            "hint": "For n=3, a true no-majority case requires all three results to differ from each other.",
                        },
                        {
                            "prompt": "Write the arbitrator prompt and ArbitrationResult usage for a case where a 'legal' and 'sales' agent disagree about whether a contract clause can be waived, including the audit record you'd log.",
                            "difficulty": "hard",
                            "hint": "Include both agents' full reasoning, not just their final positions, in what you pass to the arbitrator.",
                        },
                    ],
                    "resources": [
                        {"title": "LangGraph: Multi-agent collaboration tutorial", "url": "https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi-agent-collaboration/", "resource_type": "tutorial"}
                    ],
                    "skills": [{"slug": "multi-agent-systems", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "Multi-Agent Systems: Course Assessment",
    "description": "Checks readiness to design, build, and debug supervisor-worker and orchestrated multi-agent systems before moving into evaluation and safety.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 40,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "Which failure mode most directly motivates splitting a single agent's tools across multiple specialist agents?",
            "options": [
                {"id": "a", "text": "Tool-set overload degrading tool selection accuracy"},
                {"id": "b", "text": "LLMs cannot call more than one tool per turn"},
                {"id": "c", "text": "Tools cannot share an API key across agents"},
                {"id": "d", "text": "Vector databases require a dedicated agent per index"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Beyond roughly 15-20 tools, tool selection accuracy for a single agent drops sharply because the model must hold every tool's signature and use-case in context at once; splitting tools across specialists restores accuracy.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "A workflow always executes research, then analysis, then writing, in that fixed order, and later steps never change which earlier steps ran. Which topology fits best?",
            "options": [
                {"id": "a", "text": "Peer-to-peer"},
                {"id": "b", "text": "Pipeline"},
                {"id": "c", "text": "Hierarchical"},
                {"id": "d", "text": "Supervisor-worker with dynamic routing"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A pipeline is the right fit when the sequence of steps is fixed and doesn't need to adapt based on intermediate results.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are legitimate reasons to move from a supervisor-worker topology to a hierarchical (supervisor of supervisors) topology? Select all that apply.",
            "options": [
                {"id": "a", "text": "A single supervisor's routing logic has grown unwieldy with 8+ specialists"},
                {"id": "b", "text": "Specialists naturally cluster into distinct business domains"},
                {"id": "c", "text": "The team wants agents to message each other directly without a router"},
                {"id": "d", "text": "The task always executes the same fixed sequence of steps"},
            ],
            "correct_answer": {"choices": ["a", "b"]},
            "explanation": "Hierarchical topologies help when a single supervisor's routing space has grown too large or when specialists cluster into domains. Direct peer messaging is a different topology (peer-to-peer), and a fixed sequence suggests a pipeline instead.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "In a shared LangGraph state schema, why does a field written concurrently by multiple parallel branches need an explicit reducer like `operator.add`?",
            "options": [
                {"id": "a", "text": "Without a reducer, LangGraph refuses to compile the graph"},
                {"id": "b", "text": "Without a reducer, the last concurrent write silently overwrites earlier ones instead of merging"},
                {"id": "c", "text": "Reducers are required for every field, even ones written by only one node"},
                {"id": "d", "text": "Reducers convert state fields from TypedDict to Pydantic automatically"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Without a declared reducer, concurrent partial updates to the same field aren't merged — the last write silently wins, which is a common and hard-to-notice source of lost data.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "state",
        },
        {
            "question_type": "scenario",
            "prompt": "A supervisor agent for a support system is forced to always route every incoming request to exactly one of three specialists, with no way to say 'none of these fit.' Support tickets that don't match any specialist's domain get routed to the closest-sounding one anyway. What should be changed, and why?",
            "options": [],
            "correct_answer": {"expected": "Add an explicit escape-hatch route (e.g., 'none' or 'clarify') so the supervisor isn't forced to pick a bad-fit specialist; a forced choice among ill-fitting options produces confidently wrong routing, whereas an explicit clarify path lets the system ask a follow-up question instead."},
            "explanation": "Forcing a router to always choose among a fixed set of specialists guarantees it will occasionally pick badly when nothing fits; an explicit non-committal route is a cheap, high-value fix.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "Which technique most directly improves a supervisor's routing accuracy at ambiguous boundary cases between two specialists, with less effort than rewriting the specialist descriptions?",
            "options": [
                {"id": "a", "text": "Adding a longer prose description of each specialist's responsibilities"},
                {"id": "b", "text": "Adding 3-5 few-shot examples of exactly the ambiguous cases seen in production"},
                {"id": "c", "text": "Increasing the LLM's temperature for the routing call"},
                {"id": "d", "text": "Removing the confidence score from the routing decision"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Few-shot examples targeted at real boundary cases let the model pattern-match against precedent, which is typically far more effective at fixing ambiguous routing than adding more descriptive prose.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function `route_with_fallback(decision, specialists, threshold=0.6)` that takes a routing decision object with `.specialist`, `.confidence`, and `.rationale` attributes and a dict of specialist callables. It should return the specialist's result if confidence >= threshold, or the string 'CLARIFY_NEEDED' otherwise.",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Returns 'CLARIFY_NEEDED' when decision.confidence < threshold; otherwise looks up and calls the matching specialist from the dict and returns its result.",
                "sample_solution": "def route_with_fallback(decision, specialists, threshold=0.6):\n    if decision.confidence < threshold:\n        return 'CLARIFY_NEEDED'\n    specialist_fn = specialists[decision.specialist]\n    return specialist_fn()",
            },
            "explanation": "This encodes the confidence-threshold pattern from the routing lesson: low-confidence decisions should trigger a clarification path rather than a guessed route.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "A specialist agent has a tool in its list that its prompt never instructs it to use, but which is dangerous if invoked unexpectedly (e.g., a refund tool inside a research specialist). What principle does this violate?",
            "options": [
                {"id": "a", "text": "Least privilege for tool access"},
                {"id": "b", "text": "Reducer correctness"},
                {"id": "c", "text": "Static delegation"},
                {"id": "d", "text": "Hierarchical topology"},
            ],
            "correct_answer": {"choice": "a"},
            "explanation": "Every specialist should only have the tools its job requires. A dangerous tool that isn't needed is a risk even if the prompt never asks for it, since unusual inputs or injected content could still trigger it.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "short_answer",
            "prompt": "In one or two sentences, explain the difference between static and dynamic task delegation, and give an example of a task that requires dynamic delegation.",
            "options": [],
            "correct_answer": {
                "expected": "Static delegation decomposes the whole task into sub-tasks up front, dispatched independently or in parallel; dynamic delegation decomposes one step at a time, using each step's result to decide the next. Example: diagnosing then routing a bug fix, where the next specialist depends on what the diagnosis finds.",
                "keywords": ["static", "dynamic", "up front", "depends on", "result"],
            },
            "explanation": "Static delegation suits independent sub-tasks; dynamic delegation is required whenever a later routing decision depends on an earlier result.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "planning",
        },
        {
            "question_type": "mcq",
            "prompt": "Why should `origin_goal` (the top-level user goal) be carried through every delegation handoff, even many levels deep?",
            "options": [
                {"id": "a", "text": "It's required by the Pydantic BaseModel base class"},
                {"id": "b", "text": "It preserves traceability so a wrong output several hops downstream can be traced back to the original request"},
                {"id": "c", "text": "It reduces the number of LLM calls needed"},
                {"id": "d", "text": "It replaces the need for a message bus"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Carrying the origin goal through every handoff is cheap and makes it possible to trace a downstream error back to its root cause without replaying the entire message history.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "mcq",
            "prompt": "Two specialist agents of equal precedence produce genuinely conflicting recommendations, and no existing precedence rule resolves it. What's the appropriate next step?",
            "options": [
                {"id": "a", "text": "Silently pick whichever output sounds more confident"},
                {"id": "b", "text": "Always default to the first specialist that ran"},
                {"id": "c", "text": "Invoke a dedicated arbitrator agent (or escalate to a human for high-stakes cases)"},
                {"id": "d", "text": "Average the two textual outputs together"},
            ],
            "correct_answer": {"choice": "c"},
            "explanation": "When precedence rules don't resolve a conflict, a dedicated arbitrator agent (or human escalation for high-stakes decisions) should adjudicate — LLM confidence in phrasing doesn't reliably correlate with correctness, so picking by apparent confidence is not a sound strategy.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "multi-agent-systems",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of these are appropriate uses of a shared scratchpad between agents, as opposed to fully isolated state? Select all that apply.",
            "options": [
                {"id": "a", "text": "A writer/critic pair iterating on the same draft together"},
                {"id": "b", "text": "Parallel research branches investigating unrelated, independent sub-questions"},
                {"id": "c", "text": "Two collaborative agents where seeing each other's partial progress avoids duplicate work"},
                {"id": "d", "text": "A billing specialist's private computation of a refund amount before returning a result"},
            ],
            "correct_answer": {"choices": ["a", "c"]},
            "explanation": "Shared scratchpads suit genuinely collaborative, sequential work where agents benefit from seeing each other's partial progress. Independent parallel branches and private per-agent computation are better served by isolated state.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "state",
        },
        {
            "question_type": "scenario",
            "prompt": "A multi-agent graph fans out to 5 parallel research sub-agents, each of which appends findings to a shared scratchpad field with no size cap. After several months in production, individual node latency and token cost have crept up significantly even though the tasks themselves haven't changed. What is the most likely cause, and what's the fix?",
            "options": [],
            "correct_answer": {"expected": "The unbounded shared scratchpad has grown over time (or per long-running session) and every node now pays a context-size tax reading a bloated scratchpad; the fix is to cap its size and periodically summarize/prune older entries, the same discipline applied to the message bus."},
            "explanation": "An ever-growing shared scratchpad reproduces the exact context-dilution problem that motivated splitting into multiple agents in the first place; bounding and pruning it is the standard fix.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "state",
        },
        {
            "question_type": "mcq",
            "prompt": "In LangGraph, what is the primary purpose of the `Send` API?",
            "options": [
                {"id": "a", "text": "To send the final answer back to the end user over HTTP"},
                {"id": "b", "text": "To dynamically fan out to a variable number of parallel node invocations at runtime"},
                {"id": "c", "text": "To persist state to a database between graph runs"},
                {"id": "d", "text": "To define a fixed conditional edge between two nodes"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "`Send` lets a node dispatch a variable number of parallel invocations of a target node, generated at runtime — the mechanism behind dynamic fan-out, as opposed to a fixed, pre-wired conditional edge.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "multi-agent-systems",
        },
    ],
}
