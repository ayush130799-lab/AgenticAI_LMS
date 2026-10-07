"""
Course 13: Production AI Agents

Covers the software engineering practices needed to ship AI agents as real
services: APIs, auth, databases, integration, caching, queues, logging,
monitoring, deployment, cost optimization, and rate limiting.
"""

COURSE = {
    "slug": "production-ai-agents",
    "title": "Production AI Agents",
    "subtitle": "Ship agents as reliable, secure, cost-controlled services",
    "description": (
        "A working agent in a notebook is not a working product. This course covers the "
        "engineering practices that turn an agent prototype into a service real users can "
        "depend on: exposing it through a FastAPI service, authenticating requests, persisting "
        "conversations and state in a database, integrating safely with external APIs, caching "
        "expensive LLM calls, offloading long-running work to queues, logging and monitoring "
        "what's happening in production, deploying without downtime, controlling token cost, "
        "and rate-limiting to protect the system under load."
    ),
    "learning_outcomes": [
        "Expose an agent as a FastAPI service with streaming responses and typed request/response models",
        "Implement API key and JWT authentication with scoped permissions for tool access",
        "Persist agent conversations and state using SQLAlchemy with a multi-tenant schema",
        "Cache LLM responses and implement semantic caching to cut cost and latency",
        "Offload long-running agent work to a background task queue",
        "Instrument, log, monitor, and deploy an agent service with cost and rate controls",
    ],
    "order_index": 13,
    "estimated_hours": 20,
    "level": "advanced",
    "icon": "server",
    "modules": [
        {
            "slug": "fastapi",
            "title": "FastAPI",
            "description": "Exposing an agent as an HTTP service with typed requests, responses, and streaming.",
            "order_index": 1,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "building-an-agent-api-with-fastapi",
                    "title": "Building an Agent API with FastAPI",
                    "description": "Structuring a FastAPI service around an agent, with typed request/response models.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Define typed request and response models for an agent endpoint with Pydantic",
                        "Structure an agent invocation as an async FastAPI route",
                        "Handle agent errors as proper HTTP responses instead of raw exceptions",
                    ],
                    "content_markdown": """
## Why FastAPI for agent services

FastAPI's native Pydantic integration matches an agent's own data shapes almost exactly — the
same typed models you use for tool arguments and handoffs (from earlier courses) double as your
API's request and response schemas. Combined with native `async` support, it's a natural fit for
services that spend most of their time waiting on LLM and tool calls rather than doing CPU work.

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI(title="Agent Service")

class AgentRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: str | None = None

class AgentResponse(BaseModel):
    reply: str
    conversation_id: str
    tokens_used: int

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest) -> AgentResponse:
    conversation_id = request.conversation_id or create_conversation_id()
    result = await run_agent(request.message, conversation_id)
    return AgentResponse(
        reply=result.text,
        conversation_id=conversation_id,
        tokens_used=result.tokens_used,
    )
```

## Async all the way down

If `run_agent` internally calls a synchronous LLM SDK, that call blocks FastAPI's event loop and
kills the concurrency benefit of using `async def` in the first place. Use the async client
variant your LLM SDK provides (most major providers ship one), and make sure every I/O call in
the chain — the LLM call, tool calls that hit external APIs, database queries — is awaited, not
called synchronously from inside an async route.

```python
async def run_agent(message: str, conversation_id: str) -> AgentResult:
    history = await load_conversation(conversation_id)
    response = await async_llm_client.messages.create(
        model="claude-sonnet-4-5",
        messages=history + [{"role": "user", "content": message}],
    )
    await save_conversation(conversation_id, message, response)
    return AgentResult(text=response.content[0].text, tokens_used=response.usage.output_tokens)
```

## Converting agent errors into HTTP responses

An agent's internal error types (tool failures, guardrail blocks, loop detection) shouldn't leak
as raw 500s with stack traces. Map them explicitly to meaningful HTTP status codes and
structured error bodies.

```python
from fastapi import Request
from fastapi.responses import JSONResponse

@app.exception_handler(GuardrailBlockedError)
async def guardrail_error_handler(request: Request, exc: GuardrailBlockedError):
    return JSONResponse(
        status_code=400,
        content={"error": "request_blocked", "reason": exc.reason},
    )

@app.exception_handler(AgentTimeoutError)
async def timeout_error_handler(request: Request, exc: AgentTimeoutError):
    return JSONResponse(status_code=504, content={"error": "agent_timeout"})
```

## Dependency injection for shared resources

FastAPI's `Depends` mechanism is the right place to wire up database sessions, the LLM client,
and configuration, rather than constructing them freshly inside every route or relying on module-
level globals that make testing harder.

```python
from fastapi import Depends

async def get_db_session():
    async with SessionLocal() as session:
        yield session

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest, db=Depends(get_db_session)) -> AgentResponse:
    ...
```
""",
                    "examples": [
                        {
                            "title": "Example: a minimal end-to-end request through the service",
                            "code": (
                                "# client request\n"
                                "import httpx\n"
                                "response = httpx.post('http://localhost:8000/agent/chat',\n"
                                "    json={'message': 'What is my order status?'})\n"
                                "print(response.json())\n"
                                "# {'reply': '...', 'conversation_id': '...', 'tokens_used': 142}"
                            ),
                            "explanation": "The typed AgentResponse model guarantees every client gets a consistent, documented shape back, which OpenAPI docs (auto-generated by FastAPI) surface for free.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a `GET /agent/conversations/{conversation_id}` route that returns the full stored message history for a conversation, with a 404 if it doesn't exist.",
                            "difficulty": "easy",
                            "hint": "Raise HTTPException(status_code=404) when load_conversation returns nothing.",
                        },
                        {
                            "prompt": "Add an exception handler for a `RateLimitExceededError` that returns a 429 with a `Retry-After` header.",
                            "difficulty": "medium",
                            "hint": "JSONResponse accepts a `headers` argument; set 'Retry-After' to a computed number of seconds.",
                        },
                    ],
                    "resources": [
                        {"title": "FastAPI: Official documentation", "url": "https://fastapi.tiangolo.com/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}, {"slug": "python", "weight": 0.5}],
                },
                {
                    "slug": "streaming-agent-responses-with-sse",
                    "title": "Streaming Agent Responses with Server-Sent Events",
                    "description": "Streaming token-by-token agent output to the client instead of waiting for the full response.",
                    "lesson_type": "coding",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement a streaming FastAPI endpoint using Server-Sent Events",
                        "Stream tokens from an LLM provider's streaming API through to the client",
                        "Handle client disconnects gracefully during a stream",
                    ],
                    "content_markdown": """
## Why streaming matters for agent UX

An agent response that takes 8 seconds to fully generate feels much worse as a single blocking
wait than as text appearing progressively, even though the total time is identical. Server-Sent
Events (SSE) is the standard, simple way to stream text over plain HTTP without the complexity
of WebSockets when you only need one-directional server-to-client streaming.

```python
from fastapi.responses import StreamingResponse
import json

async def event_stream(message: str, conversation_id: str):
    async for chunk in async_llm_client.messages.stream(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": message}],
    ):
        if chunk.type == "content_block_delta":
            data = json.dumps({"delta": chunk.delta.text})
            yield f"data: {data}\\n\\n"
    yield f"data: {json.dumps({'done': True})}\\n\\n"

@app.post("/agent/chat/stream")
async def chat_stream(request: AgentRequest):
    return StreamingResponse(
        event_stream(request.message, request.conversation_id or create_conversation_id()),
        media_type="text/event-stream",
    )
```

## Persisting the full response after streaming completes

The client sees tokens as they arrive, but you still need the complete text for conversation
history and logging. Accumulate chunks server-side as they're yielded, and persist once the
stream finishes.

```python
async def event_stream(message: str, conversation_id: str):
    full_text = []
    async for chunk in async_llm_client.messages.stream(
        model="claude-sonnet-4-5",
        messages=[{"role": "user", "content": message}],
    ):
        if chunk.type == "content_block_delta":
            full_text.append(chunk.delta.text)
            yield f"data: {json.dumps({'delta': chunk.delta.text})}\\n\\n"
    await save_conversation(conversation_id, message, "".join(full_text))
    yield f"data: {json.dumps({'done': True})}\\n\\n"
```

## Handling client disconnects

A user closing their browser tab mid-stream shouldn't leave the server still generating (and
paying for) tokens nobody will see. FastAPI's `StreamingResponse` generator raises
`asyncio.CancelledError` when the client disconnects — catch it to stop the upstream LLM stream
and log the partial completion rather than letting it run to completion unobserved.

```python
async def event_stream(message: str, conversation_id: str):
    full_text = []
    try:
        async for chunk in async_llm_client.messages.stream(...):
            full_text.append(chunk.delta.text)
            yield f"data: {json.dumps({'delta': chunk.delta.text})}\\n\\n"
    except asyncio.CancelledError:
        log.info("client_disconnected", conversation_id=conversation_id, partial_length=len(full_text))
        raise
    finally:
        if full_text:
            await save_conversation(conversation_id, message, "".join(full_text))
```

## Streaming tool calls, not just text

For agents that call tools mid-response, stream structured events for tool-call start/end
alongside text deltas, so the client UI can show "searching..." or "calling billing API..."
rather than an unexplained pause in text output.

```python
yield f"data: {json.dumps({'event': 'tool_call_start', 'tool': 'lookup_order'})}\\n\\n"
result = await lookup_order(order_id)
yield f"data: {json.dumps({'event': 'tool_call_end', 'tool': 'lookup_order'})}\\n\\n"
```
""",
                    "examples": [
                        {
                            "title": "Example: a minimal client consuming an SSE stream",
                            "code": (
                                "import httpx\n\n"
                                "with httpx.stream('POST', 'http://localhost:8000/agent/chat/stream',\n"
                                "                   json={'message': 'Summarize our refund policy'}) as r:\n"
                                "    for line in r.iter_lines():\n"
                                "        if line.startswith('data: '):\n"
                                "            print(line[6:])"
                            ),
                            "explanation": "Consuming SSE from a plain HTTP client requires no special protocol handling beyond reading lines prefixed with 'data: ', which is part of why SSE is a lighter-weight choice than WebSockets for one-way streaming.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Modify `event_stream` to also yield an `{'event': 'error'}` message and stop cleanly if the LLM stream raises an exception mid-generation.",
                            "difficulty": "medium",
                            "hint": "Wrap the async for loop in a try/except around the LLM-specific exception type, yield an error event, then return.",
                        },
                        {
                            "prompt": "Add a heartbeat comment (a `: keepalive\\n\\n` SSE comment line) sent every 15 seconds if no content has been yielded, to prevent proxies from timing out an idle stream.",
                            "difficulty": "hard",
                            "hint": "You'll need to race the next chunk against an asyncio timeout and yield a keepalive comment when the timeout fires instead of a real chunk.",
                        },
                    ],
                    "resources": [
                        {"title": "FastAPI: StreamingResponse", "url": "https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse", "resource_type": "docs"},
                        {"title": "MDN: Using server-sent events", "url": "https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "authentication",
            "title": "Authentication",
            "description": "Authenticating and authorizing requests to an agent service, including scoped tool permissions.",
            "order_index": 2,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "api-key-and-jwt-auth",
                    "title": "API Key and JWT Authentication for Agent Endpoints",
                    "description": "Implementing both simple API-key and JWT-based authentication in FastAPI.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement API key authentication using a FastAPI dependency",
                        "Implement JWT-based authentication with expiry validation",
                        "Choose between API keys and JWTs for different client types",
                    ],
                    "content_markdown": """
## API keys for service-to-service clients

API keys are the right fit for machine clients (another backend service calling your agent
API) where there's no interactive login flow. Validate them as a FastAPI dependency so every
protected route declares its requirement explicitly and consistently.

```python
from fastapi import Depends, Header, HTTPException

async def verify_api_key(x_api_key: str = Header(...)) -> str:
    key_record = await lookup_api_key(x_api_key)
    if key_record is None or key_record.revoked:
        raise HTTPException(status_code=401, detail="invalid or revoked API key")
    return key_record.owner_id

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest, owner_id: str = Depends(verify_api_key)) -> AgentResponse:
    ...
```

Store API keys hashed (never plaintext) the same way you'd store passwords, and support
revocation by looking up a record rather than validating a key format alone — a leaked key
needs to be killable without rotating every key in the system.

```python
import hashlib

def hash_api_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()

async def lookup_api_key(raw_key: str):
    hashed = hash_api_key(raw_key)
    return await db.fetch_one("SELECT * FROM api_keys WHERE key_hash = :hashed", {"hashed": hashed})
```

## JWTs for user-facing clients

JWTs fit interactive clients (a web or mobile app with a logged-in user) better, since they
carry claims (user id, roles, expiry) that a client already has after login, without a database
lookup on every request.

```python
import jwt
from datetime import datetime, timezone

def verify_jwt(authorization: str = Header(...)) -> dict:
    token = authorization.removeprefix("Bearer ")
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="invalid token")
    return payload

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest, claims: dict = Depends(verify_jwt)) -> AgentResponse:
    user_id = claims["sub"]
    ...
```

Always validate expiry (`exp` claim) explicitly rather than assuming the library enforces it by
default in every configuration, and keep JWT lifetimes short (minutes to a few hours) paired
with a refresh-token flow rather than issuing long-lived JWTs directly.

## Choosing between them

Use API keys for backend/service clients and long-lived integrations; use JWTs for end-user
sessions in web/mobile clients. A system with both kinds of clients typically supports both auth
methods, dispatched by which header is present, rather than forcing one client type to awkwardly
adopt the other's mechanism.

```python
async def verify_any_auth(x_api_key: str | None = Header(None), authorization: str | None = Header(None)):
    if x_api_key:
        return await verify_api_key(x_api_key)
    if authorization:
        return verify_jwt(authorization)["sub"]
    raise HTTPException(status_code=401, detail="no credentials provided")
```
""",
                    "examples": [
                        {
                            "title": "Example: generating a short-lived JWT after login",
                            "code": (
                                "def issue_jwt(user_id: str, expires_in_minutes: int = 30) -> str:\n"
                                "    payload = {\n"
                                "        'sub': user_id,\n"
                                "        'exp': datetime.now(timezone.utc).timestamp() + expires_in_minutes * 60,\n"
                                "    }\n"
                                "    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')"
                            ),
                            "explanation": "Short expiry limits the damage window if a token leaks, and pairing this with a separate refresh-token flow (not shown) is the standard way to keep sessions usable without issuing long-lived tokens directly.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement an API key revocation endpoint `POST /admin/api-keys/{key_id}/revoke` and update `lookup_api_key` usage to reject revoked keys.",
                            "difficulty": "easy",
                            "hint": "Set a `revoked` boolean column to true rather than deleting the row, preserving an audit trail.",
                        },
                        {
                            "prompt": "Implement `verify_any_auth` as a full FastAPI dependency and write a test showing it returns 401 when neither header is present and succeeds when exactly one valid one is.",
                            "difficulty": "medium",
                            "hint": "Use FastAPI's TestClient and pass headers explicitly in each test case.",
                        },
                    ],
                    "resources": [
                        {"title": "FastAPI: Security and authentication", "url": "https://fastapi.tiangolo.com/tutorial/security/", "resource_type": "docs"},
                        {"title": "PyJWT documentation", "url": "https://pyjwt.readthedocs.io/", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "oauth2-and-scoped-permissions",
                    "title": "OAuth2 and Scoped Permissions for Tool Access",
                    "description": "Restricting which tools an authenticated caller's agent session can use, based on scopes.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain how OAuth2 scopes map onto agent tool permissions",
                        "Design a scope model that restricts tool access per caller",
                        "Enforce scope checks at the tool-invocation layer, not just the route layer",
                    ],
                    "content_markdown": """
## Scopes as the bridge between auth and tool permissions

Authentication answers "who is this caller." Authorization answers "what is this caller allowed
to do" — and for an agent service, that specifically means which tools the agent is allowed to
invoke on this caller's behalf. OAuth2 scopes are a natural fit: encode allowed tool categories
as scopes in the token, and check them before any tool call executes, not just before the route
handler runs.

```python
# JWT payload carrying scopes
{
    "sub": "user_123",
    "scopes": ["agent:chat", "tools:read_only"],
    "exp": 1234567890,
}
```

```python
from fastapi import Security
from fastapi.security import SecurityScopes

async def verify_scopes(security_scopes: SecurityScopes, claims: dict = Depends(verify_jwt)):
    token_scopes = set(claims.get("scopes", []))
    required = set(security_scopes.scopes)
    if not required.issubset(token_scopes):
        raise HTTPException(status_code=403, detail=f"missing required scope(s): {required - token_scopes}")
    return claims

@app.post("/agent/chat")
async def chat(request: AgentRequest, claims: dict = Security(verify_scopes, scopes=["agent:chat"])):
    ...
```

## Route-level scopes aren't enough for agents

A route-level scope check (does this caller have `agent:chat`) doesn't know which specific tools
the agent might invoke mid-conversation. The tool-dispatch layer itself needs to check the
caller's scopes against each tool's required scope before executing it — otherwise a caller with
only read-only permissions could still trigger a write-capable tool simply because the agent
decided to call it.

```python
TOOL_REQUIRED_SCOPES = {
    "lookup_order": "tools:read_only",
    "issue_refund": "tools:write",
    "send_email": "tools:write",
}

async def dispatch_tool_call(tool_name: str, args: dict, caller_scopes: set[str]):
    required = TOOL_REQUIRED_SCOPES.get(tool_name)
    if required and required not in caller_scopes:
        return {"error": "forbidden", "tool": tool_name, "required_scope": required}
    return await TOOLS[tool_name](**args)
```

## Designing a scope model

Keep scopes coarse enough to be manageable (a handful of categories: read-only tools,
write tools, admin tools) rather than one scope per individual tool, which becomes unwieldy to
issue and reason about. Map new tools to an existing scope category by risk level as they're
added, rather than inventing a new scope for every tool — this mirrors the least-privilege
tool-scoping principle from the multi-agent and prompt-injection courses, applied at the
caller-identity layer instead of the agent-design layer.

## Scopes and multi-tenant isolation

For a multi-tenant service, scopes alone aren't sufficient to prevent one tenant's agent from
accessing another tenant's data — that's a data-layer isolation problem, covered in the
databases module. Scopes control *what kind* of action is allowed; tenant isolation controls
*whose* data the action can touch. Both checks are needed, and conflating them is a common
security gap.
""",
                    "examples": [
                        {
                            "title": "Example: a forbidden tool call surfaced back through the agent response",
                            "code": (
                                "result = await dispatch_tool_call('issue_refund', {'order_id': '4471'}, caller_scopes={'tools:read_only'})\n"
                                "if result.get('error') == 'forbidden':\n"
                                "    agent_reply = 'I can look into that, but I don\\'t have permission to issue refunds for this account.'"
                            ),
                            "explanation": "Turning a forbidden tool call into a clear, honest message to the end user is much better UX than a silent failure or a generic error.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a scope model (list of scope names and what each permits) for an agent service with read-only research tools, write-capable billing tools, and admin-only user-management tools.",
                            "difficulty": "easy",
                            "hint": "Aim for 3-4 scopes total, not one per tool.",
                        },
                        {
                            "prompt": "Implement `dispatch_tool_call` to log every forbidden attempt with the caller id, tool name, and required scope, and explain why this log matters for security review even though the call was correctly blocked.",
                            "difficulty": "medium",
                            "hint": "A pattern of forbidden attempts from one caller could indicate a compromised credential or a misconfigured client, worth investigating even though no single blocked call caused harm.",
                        },
                    ],
                    "resources": [
                        {"title": "FastAPI: OAuth2 scopes", "url": "https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "databases",
            "title": "Databases",
            "description": "Persisting agent conversations and state, and designing schemas for multi-tenant systems.",
            "order_index": 3,
            "estimated_hours": 2,
            "lessons": [
                {
                    "slug": "persisting-conversations-with-sqlalchemy",
                    "title": "Persisting Agent Conversations with SQLAlchemy",
                    "description": "Modeling and storing conversation history and agent runs with SQLAlchemy's async ORM.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Define SQLAlchemy models for conversations, messages, and agent runs",
                        "Implement async database operations for reading and writing conversation state",
                        "Use database transactions to keep multi-step writes consistent",
                    ],
                    "content_markdown": """
## Modeling conversation state

A minimal but real schema needs at least three related tables: conversations (the top-level
thread), messages (individual turns within it), and, for agent systems specifically, a runs or
tool_calls table capturing what the agent actually did, not just what it said.

```python
from sqlalchemy import String, ForeignKey, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship, DeclarativeBase
from datetime import datetime, timezone
import uuid

class Base(DeclarativeBase):
    pass

class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    owner_id: Mapped[str] = mapped_column(String, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    messages: Mapped[list["Message"]] = relationship(back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: uuid.uuid4().hex)
    conversation_id: Mapped[str] = mapped_column(ForeignKey("conversations.id"), index=True)
    role: Mapped[str] = mapped_column(String)  # "user" | "assistant" | "tool"
    content: Mapped[str] = mapped_column(String)
    tool_calls: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))
    conversation: Mapped["Conversation"] = relationship(back_populates="messages")
```

## Async reads and writes

```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def load_conversation(session: AsyncSession, conversation_id: str) -> list[Message]:
    result = await session.execute(
        select(Message).where(Message.conversation_id == conversation_id).order_by(Message.created_at)
    )
    return list(result.scalars().all())

async def save_message(session: AsyncSession, conversation_id: str, role: str, content: str, tool_calls: dict | None = None):
    message = Message(conversation_id=conversation_id, role=role, content=content, tool_calls=tool_calls)
    session.add(message)
    await session.commit()
```

## Transactions for multi-step writes

Saving a user message, the agent's tool calls, and the final assistant reply are logically one
unit — if the process crashes between saving the user message and the assistant reply, you don't
want a conversation stuck in a half-written state. Wrap related writes in a single transaction
so they commit or roll back together.

```python
async def save_full_turn(session: AsyncSession, conversation_id: str, user_msg: str, assistant_msg: str, tool_calls: dict | None):
    async with session.begin():
        session.add(Message(conversation_id=conversation_id, role="user", content=user_msg))
        session.add(Message(conversation_id=conversation_id, role="assistant", content=assistant_msg, tool_calls=tool_calls))
    # both inserts commit together, or neither does
```

## Indexing for the access patterns you actually have

`conversation_id` and `owner_id` need indexes because nearly every query filters by one or both
of them (loading a conversation's messages, listing a user's conversations). Add indexes based on
your actual query patterns, not defensively on every column — unnecessary indexes slow down
writes for no read benefit.
""",
                    "examples": [
                        {
                            "title": "Example: loading history and appending a new turn in one flow",
                            "code": (
                                "async def handle_turn(session: AsyncSession, conversation_id: str, user_message: str):\n"
                                "    history = await load_conversation(session, conversation_id)\n"
                                "    reply = await run_agent(user_message, history)\n"
                                "    await save_full_turn(session, conversation_id, user_message, reply.text, reply.tool_calls)\n"
                                "    return reply"
                            ),
                            "explanation": "Loading history before generating and saving after keeps the read and write concerns cleanly separated, and the transactional save keeps the persisted state consistent even if something downstream fails.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a `feedback` column to Message (nullable string: 'up', 'down', or null) and write an async function to record user feedback on a specific message by id.",
                            "difficulty": "easy",
                            "hint": "A simple UPDATE via session.get(Message, message_id) then setting the attribute and committing works fine here.",
                        },
                        {
                            "prompt": "Write a query that returns the 10 most recently active conversations for a given owner_id, ordered by their most recent message's created_at.",
                            "difficulty": "hard",
                            "hint": "You'll need a subquery or join that computes max(created_at) per conversation_id, then order and limit on that.",
                        },
                    ],
                    "resources": [
                        {"title": "SQLAlchemy: Asynchronous I/O", "url": "https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 0.8}, {"slug": "python", "weight": 0.7}],
                },
                {
                    "slug": "schema-design-for-multi-tenant-systems",
                    "title": "Schema Design for Multi-Tenant Agent Systems",
                    "description": "Isolating tenant data and enforcing row-level access safely at the schema and query layer.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Compare shared-schema and separate-schema multi-tenant strategies",
                        "Enforce tenant isolation consistently at the query layer",
                        "Recognize the risk of relying on application code alone for tenant isolation",
                    ],
                    "content_markdown": """
## Multi-tenancy strategies

**Shared schema, tenant column**: every table carries a `tenant_id` column, and all tenants
share the same tables. Simplest to operate and migrate, but every single query must remember to
filter by tenant — a forgotten `WHERE tenant_id = ...` is a direct data leak between customers.

**Schema-per-tenant**: each tenant gets its own database schema (or database) with identical
table structure. Stronger isolation — a bug in one query can't leak another tenant's rows purely
by omission — at the cost of more operational complexity (migrations must run per schema,
cross-tenant analytics are harder).

```python
# Shared-schema approach: every model carries tenant_id
class Conversation(Base):
    __tablename__ = "conversations"
    id: Mapped[str] = mapped_column(String, primary_key=True)
    tenant_id: Mapped[str] = mapped_column(String, index=True)
    owner_id: Mapped[str] = mapped_column(String, index=True)
```

## Enforcing isolation consistently

For the shared-schema approach, don't rely on every developer remembering to add a tenant filter
to every query by hand. Centralize it: a query-building helper or a session-scoped filter that
makes it structurally hard to forget.

```python
async def query_for_tenant(session: AsyncSession, model, tenant_id: str, **filters):
    stmt = select(model).where(model.tenant_id == tenant_id)
    for key, value in filters.items():
        stmt = stmt.where(getattr(model, key) == value)
    return (await session.execute(stmt)).scalars().all()

# Every call site goes through this helper, not raw select(Conversation).where(...)
conversations = await query_for_tenant(session, Conversation, tenant_id, owner_id=user_id)
```

For stronger guarantees, PostgreSQL Row-Level Security (RLS) policies enforce tenant filtering
at the database level, so even a query that forgets the `WHERE tenant_id = ...` clause in
application code still can't see another tenant's rows — this is defense in depth on top of, not
instead of, careful application code.

```sql
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON conversations
    USING (tenant_id = current_setting('app.current_tenant_id')::text);
```

## Application-layer isolation alone is a risk

Relying solely on developers remembering to filter every query is exactly the kind of thing that
holds up fine in code review and then fails once under time pressure, a new team member, or an
ORM relationship that silently joins across tables without carrying the filter. Treat tenant
isolation the same way you'd treat authentication — as a cross-cutting concern enforced at a
single, hard-to-bypass layer (RLS, or a strictly-enforced query helper with tests), not as a
convention every query author has to remember individually.

## Testing tenant isolation directly

Write tests that specifically attempt cross-tenant access and assert it fails — create two
tenants, seed data for each, and verify tenant A's session genuinely cannot retrieve tenant B's
conversations through any code path you expose. This is one of the highest-value security tests
a multi-tenant agent service can have, precisely because a leak here is silent and severe.
""",
                    "examples": [
                        {
                            "title": "Example: a cross-tenant isolation test",
                            "code": (
                                "async def test_cannot_read_other_tenant_conversation(db_session):\n"
                                "    convo_a = await create_conversation(db_session, tenant_id='tenant_a')\n"
                                "    result = await query_for_tenant(db_session, Conversation, tenant_id='tenant_b', id=convo_a.id)\n"
                                "    assert result == []  # tenant_b's query must not see tenant_a's row"
                            ),
                            "explanation": "This test directly exercises the isolation guarantee rather than just testing that queries return the right shape of data — it's specifically checking for the absence of a leak.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "List two operational costs of schema-per-tenant isolation that a team should weigh against its stronger isolation guarantee.",
                            "difficulty": "easy",
                            "hint": "Consider migration tooling complexity and the difficulty of running a single cross-tenant analytics query.",
                        },
                        {
                            "prompt": "Write the RLS policy and application-side `SET app.current_tenant_id` statement needed to enforce isolation on a `messages` table joined to `conversations` by tenant.",
                            "difficulty": "hard",
                            "hint": "messages doesn't need its own tenant_id column if you enforce isolation via a policy that checks the parent conversation's tenant_id through a subquery, though duplicating tenant_id onto messages directly is often simpler and faster.",
                        },
                    ],
                    "resources": [
                        {"title": "PostgreSQL: Row Security Policies", "url": "https://www.postgresql.org/docs/current/ddl-rowsecurity.html", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "api-integration",
            "title": "API Integration",
            "description": "Calling external APIs safely from agent tools, and handling their failures gracefully.",
            "order_index": 4,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "calling-external-apis-safely",
                    "title": "Calling External APIs Safely from Agent Tools",
                    "description": "Wrapping external API calls with timeouts, validation, and safe defaults for use as agent tools.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Wrap an external API call as a well-behaved agent tool with validated inputs and outputs",
                        "Apply timeouts and response validation to every external call",
                        "Avoid passing raw external responses directly into agent context",
                    ],
                    "content_markdown": """
## A tool wrapping an external API is still a tool

Every principle from earlier courses about tool design (least privilege, typed inputs/outputs,
clear success/failure signaling) applies just as much when the tool's implementation happens to
be an HTTP call to a third party. The agent shouldn't need to know or care that `get_weather` is
backed by an external API versus a local database — the tool's contract should look the same
either way.

```python
import httpx
from pydantic import BaseModel

class WeatherResult(BaseModel):
    location: str
    temp_f: float
    conditions: str

async def get_weather(location: str) -> WeatherResult:
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            "https://api.weather-provider.com/v1/current",
            params={"q": location},
            headers={"Authorization": f"Bearer {WEATHER_API_KEY}"},
        )
        response.raise_for_status()
        data = response.json()
    return WeatherResult(location=location, temp_f=data["temp_f"], conditions=data["conditions"])
```

## Validate external responses before trusting them

Never pass a raw external API response directly into the agent's context. Parse it into your own
typed model first (as `WeatherResult` does above) — this catches unexpected shape changes from
the provider immediately as a validation error, rather than the agent silently receiving
malformed or unexpected data and trying to make sense of it.

```python
async def get_weather_safe(location: str) -> WeatherResult | dict:
    try:
        return await get_weather(location)
    except httpx.HTTPStatusError as e:
        return {"error": "weather_api_error", "status": e.response.status_code}
    except (KeyError, ValueError):
        return {"error": "weather_api_unexpected_response"}
```

## Timeouts are mandatory, not optional

Every external call needs an explicit timeout — the same principle from the reliability module
of the evaluation course, applied concretely here. Without one, a slow or hanging third-party API
can stall an entire agent run indefinitely, and the default timeout for most HTTP clients (often
"no timeout" or a very long one) is the wrong choice for a tool call embedded in a user-facing
request path.

## Not leaking API credentials through the agent

Never construct a tool such that the API key or secret used to call an external service could
end up echoed back into the agent's context or output — build the authenticated request
entirely inside the tool function, with the credential read from server-side configuration, never
passed as a tool argument the model could see or repeat.

```python
# Wrong: credential passed as a tool argument the model constructs
async def get_weather_bad(location: str, api_key: str) -> dict: ...

# Right: credential is closed over from server config, never visible to the model
async def get_weather(location: str) -> WeatherResult:
    api_key = settings.WEATHER_API_KEY  # never a parameter the model supplies
    ...
```
""",
                    "examples": [
                        {
                            "title": "Example: registering the tool with the agent, credential-free from the model's view",
                            "code": (
                                "TOOL_SCHEMA = {\n"
                                "    'name': 'get_weather',\n"
                                "    'description': 'Get current weather for a location.',\n"
                                "    'input_schema': {\n"
                                "        'type': 'object',\n"
                                "        'properties': {'location': {'type': 'string'}},\n"
                                "        'required': ['location'],\n"
                                "    },\n"
                                "}\n"
                                "# note: no api_key field anywhere in what the model can see or supply"
                            ),
                            "explanation": "The tool schema exposed to the model only ever includes 'location' — the API key lives entirely in server-side code the model has no visibility into or control over.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Wrap a hypothetical currency-conversion API as a tool following the same pattern (typed result model, timeout, validated response, credential-free schema).",
                            "difficulty": "medium",
                            "hint": "Mirror get_weather's structure exactly: an async function, a Pydantic result model, and error handling for both HTTP and parsing failures.",
                        },
                        {
                            "prompt": "Add retry-with-backoff (from the evaluation course's reliability module) to `get_weather_safe` for 5xx responses specifically, while not retrying 4xx responses.",
                            "difficulty": "hard",
                            "hint": "Check e.response.status_code >= 500 inside the except block before deciding to retry versus returning the error immediately.",
                        },
                    ],
                    "resources": [
                        {"title": "httpx: Async support", "url": "https://www.python-httpx.org/async/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "handling-third-party-api-failures",
                    "title": "Handling Third-Party API Failures Gracefully",
                    "description": "Designing fallback behavior and user-facing messaging for external dependency failures.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Design fallback strategies for a failed external API call",
                        "Communicate external failures honestly to end users without technical detail leakage",
                        "Distinguish partial degradation from total failure at the integration layer",
                    ],
                    "content_markdown": """
## Every external dependency will eventually fail

Third-party APIs have their own outages, rate limits, and breaking changes, entirely outside
your control. The question isn't whether to plan for this, but what the agent should do when it
happens — and "let the whole conversation crash with a 500" is rarely the right answer for a
failure in one specific tool.

## Fallback strategies, ranked by preference

**Cached/stale data**: if a slightly outdated answer is acceptable (weather from 10 minutes ago,
a stock price from the last successful fetch), serve it with a clear "as of" timestamp rather
than failing outright. **Degraded functionality**: if the tool's exact data isn't available, can
the agent still be useful without it (answer the parts of the question it can, and be explicit
about what it couldn't check)? **Honest failure**: when neither is possible, tell the user
plainly that this specific capability is temporarily unavailable, without technical detail
leakage (never surface a raw stack trace, HTTP status code, or internal service name to an end
user).

```python
async def answer_with_weather(location: str, question: str) -> str:
    weather = await get_weather_safe(location)
    if isinstance(weather, dict) and "error" in weather:
        return (
            "I'm having trouble reaching the weather service right now, so I can't give you "
            "current conditions. Is there anything else I can help with in the meantime?"
        )
    return generate_weather_response(question, weather)
```

## Partial degradation vs. total failure

Distinguish these explicitly in how you design multi-tool responses: if an agent call needs
three tools and one fails, that's partial degradation — the other two tools' results are still
valid and useful. Don't discard everything and fail the whole request just because one dependency
had a bad moment; synthesize the best answer possible from what did succeed, and be transparent
about the gap.

```python
async def multi_source_answer(question: str, location: str, order_id: str) -> str:
    weather_result = await get_weather_safe(location)
    order_result = await lookup_order_safe(order_id)
    available = {k: v for k, v in {"weather": weather_result, "order": order_result}.items()
                 if not (isinstance(v, dict) and "error" in v)}
    missing = set(["weather", "order"]) - available.keys()
    answer = synthesize(question, available)
    if missing:
        answer += f"\\n\\n(Note: I couldn't retrieve {', '.join(missing)} information right now.)"
    return answer
```

## Communicating failure without technical leakage

A message like "Error 503: upstream service unavailable at weather-provider-internal.corp.net"
both looks unprofessional and can leak internal architecture details to an end user (or, worse,
to an attacker probing the system). Map every internal error type to a small set of plain,
honest, non-technical user-facing messages, and keep the technical detail in your logs (from the
monitoring module) where engineers, not end users, can see it.
""",
                    "examples": [
                        {
                            "title": "Example: mapping internal errors to safe user-facing messages",
                            "code": (
                                "USER_FACING_MESSAGES = {\n"
                                "    'weather_api_error': \"I can't check the weather right now — please try again shortly.\",\n"
                                "    'order_api_timeout': \"Looking up your order is taking longer than expected — I'll keep trying.\",\n"
                                "}\n\n"
                                "def safe_message_for(error_code: str) -> str:\n"
                                "    return USER_FACING_MESSAGES.get(error_code, 'Something went wrong — please try again.')"
                            ),
                            "explanation": "A lookup table like this keeps user-facing copy consistent and reviewable in one place, and guarantees no internal error detail accidentally reaches the response by default.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Rewrite a hypothetical error message that currently reads 'Error: Connection refused to internal-payments-svc:8443' into an appropriate user-facing equivalent.",
                            "difficulty": "easy",
                            "hint": "Keep it honest about what the user can't do right now, without any hostname, port, or internal service naming.",
                        },
                        {
                            "prompt": "Extend `multi_source_answer` to also log (not just note in the response) which specific sources failed and why, for later monitoring/alerting.",
                            "difficulty": "medium",
                            "hint": "Log the structured error dict for each failed source before synthesizing the user-facing answer.",
                        },
                    ],
                    "resources": [
                        {"title": "Google SRE Workbook: Handling overload", "url": "https://sre.google/workbook/handling-overload/", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "caching",
            "title": "Caching",
            "description": "Caching LLM responses and using semantic similarity to reuse answers to similar queries.",
            "order_index": 5,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "caching-llm-responses-with-redis",
                    "title": "Caching LLM Responses with Redis",
                    "description": "Implementing exact-match response caching keyed on prompt content.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Implement an exact-match LLM response cache using Redis",
                        "Choose an appropriate cache key and TTL for different query types",
                        "Avoid caching responses that shouldn't be reused",
                    ],
                    "content_markdown": """
## Why cache LLM calls at all

Identical prompts producing identical (or acceptably similar) answers are common in production:
FAQ-style questions, repeated lookups of static reference information, or retries of the exact
same request. Caching these skips the LLM call entirely, cutting both latency (often from
seconds to milliseconds) and cost.

```python
import redis.asyncio as redis
import hashlib
import json

redis_client = redis.from_url("redis://localhost:6379")

def cache_key(model: str, messages: list[dict]) -> str:
    payload = json.dumps({"model": model, "messages": messages}, sort_keys=True)
    return "llm_cache:" + hashlib.sha256(payload.encode()).hexdigest()

async def cached_llm_call(model: str, messages: list[dict], ttl_seconds: int = 3600) -> str:
    key = cache_key(model, messages)
    cached = await redis_client.get(key)
    if cached:
        return cached.decode()
    response = await async_llm_client.messages.create(model=model, messages=messages)
    text = response.content[0].text
    await redis_client.set(key, text, ex=ttl_seconds)
    return text
```

## Choosing a TTL by content volatility

A cached answer about a fixed policy (return window, terms of service) can safely have a long
TTL (hours to days). A cached answer that might reference time-sensitive information (current
promotions, live status) needs a short TTL or no caching at all. Set TTL per query category, not
one global value for every cached response — a single blanket TTL is either too long for volatile
content or too short to capture savings on stable content.

```python
TTL_BY_CATEGORY = {
    "policy_question": 86400,      # 24 hours — rarely changes
    "product_info": 3600,          # 1 hour — occasionally updated
    "order_status": 0,             # never cache — always current, per-user, sensitive
}
```

## What not to cache

Never cache responses containing per-user personal data (an answer that includes a specific
customer's order details) under a key that could be looked up by a different user, and never
cache anything downstream of a request that failed a guardrail check. A cache is a shared store
by nature — the moment it holds something that shouldn't be shared across requests, you've built
a data leak, not a performance optimization.

```python
async def cached_llm_call_safe(model: str, messages: list[dict], contains_pii: bool, ttl_seconds: int = 3600):
    if contains_pii:
        return await async_llm_client.messages.create(model=model, messages=messages)  # never cached
    return await cached_llm_call(model, messages, ttl_seconds)
```

## Cache invalidation on underlying data change

If a cached answer is derived from data that can change (a product description, a policy
document), invalidate the relevant cache entries when the source data updates, rather than
relying purely on TTL expiry. A simple approach: include a data version or last-modified
timestamp as part of the cache key, so a data update naturally produces a new key instead of
serving a stale cached answer until TTL expiry catches up.
""",
                    "examples": [
                        {
                            "title": "Example: measuring cache hit rate",
                            "code": (
                                "async def cached_llm_call_tracked(model, messages, ttl_seconds=3600):\n"
                                "    key = cache_key(model, messages)\n"
                                "    cached = await redis_client.get(key)\n"
                                "    metrics.increment('llm_cache.hit' if cached else 'llm_cache.miss')\n"
                                "    if cached:\n"
                                "        return cached.decode()\n"
                                "    response = await async_llm_client.messages.create(model=model, messages=messages)\n"
                                "    text = response.content[0].text\n"
                                "    await redis_client.set(key, text, ex=ttl_seconds)\n"
                                "    return text"
                            ),
                            "explanation": "Tracking hit/miss rate is the number you need to justify caching effort and to notice when a change in traffic patterns has quietly degraded your cache's effectiveness.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement a cache key function that also incorporates a data_version parameter, so cached answers automatically become unreachable (a cache miss) after a version bump.",
                            "difficulty": "easy",
                            "hint": "Include data_version in the payload dict passed to json.dumps before hashing.",
                        },
                        {
                            "prompt": "Design (in prose, no code required) which of the following would be safe to cache and which would not, with justification: (a) 'What's your refund policy?', (b) 'What's the status of my order #4471?', (c) 'What's the capital of France?'",
                            "difficulty": "medium",
                            "hint": "The distinguishing factor is whether the answer is the same for every user asking, versus per-user and time-sensitive.",
                        },
                    ],
                    "resources": [
                        {"title": "Redis: Python client documentation", "url": "https://redis-py.readthedocs.io/en/stable/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "semantic-caching-for-similar-queries",
                    "title": "Semantic Caching for Similar Queries",
                    "description": "Caching based on embedding similarity to reuse answers for paraphrased queries.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Explain how semantic caching extends exact-match caching using embeddings",
                        "Choose a similarity threshold that balances hit rate against answer correctness",
                        "Identify the risks semantic caching introduces that exact-match caching doesn't have",
                    ],
                    "content_markdown": """
## Beyond exact match

Exact-match caching (the previous lesson) misses an enormous number of real cache opportunities:
"what's your return policy" and "how do returns work" are semantically identical questions with
different wording, and would produce two separate cache misses under exact-match keying.
Semantic caching embeds the incoming query, searches a vector store of previously-answered
queries for a close match, and reuses that cached answer if similarity exceeds a threshold.

```python
async def semantic_cache_lookup(query: str, threshold: float = 0.92) -> str | None:
    query_embedding = await embed(query)
    matches = await vector_store.search(query_embedding, top_k=1)
    if matches and matches[0].score >= threshold:
        return matches[0].metadata["cached_answer"]
    return None

async def semantic_cached_llm_call(query: str, model: str) -> str:
    cached = await semantic_cache_lookup(query)
    if cached:
        return cached
    answer = await async_llm_client.messages.create(model=model, messages=[{"role": "user", "content": query}])
    text = answer.content[0].text
    embedding = await embed(query)
    await vector_store.upsert(embedding, metadata={"query": query, "cached_answer": text})
    return text
```

## Threshold selection is a real trade-off, not a tuning nicety

A low threshold (e.g., 0.80) increases hit rate but risks serving a cached answer to a query
that's similar in topic but meaningfully different in what it's actually asking — "what's your
return policy for electronics" and "what's your return policy" are similar but not
interchangeable if electronics have different rules. A high threshold (e.g., 0.97) is safer but
captures far fewer genuine paraphrase matches, reducing the cache's value. Tune this threshold
against a labeled set of query pairs you've explicitly judged as "same answer applies" vs. "looks
similar but isn't," not by intuition alone.

## Risks specific to semantic caching

Unlike exact-match caching, a semantic cache can confidently serve a *wrong* answer — it will
always return something above threshold if anything exists in that neighborhood, and there's no
guarantee "close in embedding space" means "the same answer is correct." This risk compounds for
queries with subtle but important distinctions (different dollar amounts, different product
lines, different time periods) that embeddings may not weight heavily enough to separate. For
any domain where a wrong-but-plausible cached answer is costly (billing, legal, medical), either
use a very high threshold, add a secondary verification step (an LLM judge confirming the cached
answer still applies to the new query), or don't use semantic caching for that content category
at all.

```python
async def verified_semantic_cache_lookup(query: str, threshold: float = 0.9) -> str | None:
    candidate = await semantic_cache_lookup(query, threshold)
    if candidate is None:
        return None
    verification = await judge_still_applies(query, candidate)  # a targeted LLM-judge check
    return candidate if verification.applies else None
```

## Combine both layers

A well-built cache typically checks exact-match first (cheap, zero risk of a wrong answer), and
only falls back to semantic matching on an exact-match miss, reserving the higher-risk semantic
path for the queries that genuinely need it rather than paying its cost and risk on every
request.
""",
                    "examples": [
                        {
                            "title": "Example: layering exact-match and semantic caching",
                            "code": (
                                "async def layered_cached_call(query: str, model: str) -> str:\n"
                                "    exact = await redis_client.get(cache_key(model, [{'role': 'user', 'content': query}]))\n"
                                "    if exact:\n"
                                "        return exact.decode()\n"
                                "    semantic = await semantic_cache_lookup(query)\n"
                                "    if semantic:\n"
                                "        return semantic\n"
                                "    return await semantic_cached_llm_call(query, model)"
                            ),
                            "explanation": "Checking exact-match first means the zero-risk, zero-cost path is always tried before the higher-risk semantic path, minimizing unnecessary exposure to the wrong-answer risk semantic caching introduces.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Give two example query pairs: one where a 0.90 similarity threshold would correctly reuse the same answer, and one where it would incorrectly reuse an answer that should actually differ.",
                            "difficulty": "medium",
                            "hint": "For the incorrect case, think of queries that share most words but differ in one critical qualifier (a product line, a date range, an amount).",
                        },
                        {
                            "prompt": "Implement `judge_still_applies(query, candidate_answer)` returning a Pydantic model with `applies: bool` and `reasoning: str`, following the LLM-as-judge pattern from the evaluation course.",
                            "difficulty": "medium",
                            "hint": "Prompt the judge with both the new query and the candidate cached answer, asking specifically whether the answer still correctly and fully addresses this new query.",
                        },
                    ],
                    "resources": [
                        {"title": "Redis: Semantic caching for LLMs", "url": "https://redis.io/docs/latest/develop/get-started/vector-database/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "queues",
            "title": "Queues",
            "description": "Offloading long-running agent work to background task queues.",
            "order_index": 6,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "background-processing-with-celery",
                    "title": "Background Task Processing with Celery",
                    "description": "Moving long-running agent tasks off the request path using Celery and Redis as a broker.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a Celery task for a long-running agent workflow",
                        "Design a polling or webhook pattern for delivering async results",
                        "Set task-level timeouts and retry policies",
                    ],
                    "content_markdown": """
## Why some agent work doesn't belong in the request path

A simple chat turn fits in a synchronous (or streamed) HTTP request. A multi-step research task
that runs for several minutes, or a batch job processing hundreds of documents, does not — an
HTTP client shouldn't have to hold a connection open for minutes, and a web server shouldn't
tie up a request-handling worker for that long either. Move genuinely long-running agent work
into a background task queue.

```python
from celery import Celery

celery_app = Celery("agent_tasks", broker="redis://localhost:6379/0", backend="redis://localhost:6379/1")

@celery_app.task(bind=True, max_retries=2, soft_time_limit=300)
def run_research_task(self, query: str, user_id: str) -> dict:
    try:
        result = run_deep_research_agent(query)  # synchronous entry point for a sync Celery worker
        return {"status": "completed", "result": result}
    except SoftTimeLimitExceeded:
        return {"status": "timeout", "partial_result": None}
```

## Kicking off and checking on a task from FastAPI

```python
@app.post("/agent/research")
async def start_research(request: ResearchRequest, user_id: str = Depends(verify_api_key)):
    task = run_research_task.delay(request.query, user_id)
    return {"task_id": task.id, "status": "queued"}

@app.get("/agent/research/{task_id}")
async def get_research_status(task_id: str):
    result = celery_app.AsyncResult(task_id)
    if result.state == "PENDING":
        return {"status": "queued"}
    if result.state == "SUCCESS":
        return {"status": "completed", "result": result.result}
    if result.state == "FAILURE":
        return {"status": "failed", "error": str(result.result)}
    return {"status": result.state.lower()}
```

## Polling vs. webhooks for result delivery

Polling (client periodically calls `GET /agent/research/{task_id}`) is simple to implement on
both sides and works for most internal or dashboard-style clients. Webhooks (your service calls
back to a client-provided URL when the task completes) suit integrations where the calling
system needs to react immediately without polling overhead. Support polling by default; add
webhook delivery as an opt-in for clients that register a callback URL, since webhook delivery
itself needs its own retry and failure-handling logic.

## Task-level timeouts and retries

Every background task needs a `soft_time_limit` (raises a catchable exception inside the task,
letting it save partial progress) and often a hard `time_limit` (kills the task forcibly) as a
backstop. Retry policy should distinguish transient failures (network blip calling an external
API mid-task — worth retrying) from task-inherent failures (a malformed input that will fail
identically every time — not worth retrying).

```python
@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def run_tool_heavy_task(self, args: dict):
    try:
        return execute_task(args)
    except TransientError as exc:
        raise self.retry(exc=exc)
    except ValidationError:
        raise  # don't retry — this input will never succeed
```
""",
                    "examples": [
                        {
                            "title": "Example: a client polling loop for a research task",
                            "code": (
                                "import time, httpx\n\n"
                                "task = httpx.post('http://localhost:8000/agent/research', json={'query': 'competitor pricing'}).json()\n"
                                "while True:\n"
                                "    status = httpx.get(f\"http://localhost:8000/agent/research/{task['task_id']}\").json()\n"
                                "    if status['status'] in ('completed', 'failed'):\n"
                                "        print(status)\n"
                                "        break\n"
                                "    time.sleep(2)"
                            ),
                            "explanation": "A simple poll-with-delay loop is often all a client needs; the interval should be tuned to the task's typical duration so you're not hammering the status endpoint for a task that takes minutes.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a `progress` field the task updates periodically (e.g., 'searching sources', 'synthesizing findings') that the status endpoint surfaces, so a client polling mid-task sees more than just 'queued' or 'completed'.",
                            "difficulty": "medium",
                            "hint": "Celery tasks can call self.update_state(state='PROGRESS', meta={'step': '...'}) to report intermediate status.",
                        },
                        {
                            "prompt": "Design (in prose) a webhook delivery system's retry policy for a client callback URL that's temporarily unreachable, including how many attempts and what backoff you'd use before giving up.",
                            "difficulty": "hard",
                            "hint": "Consider exponential backoff similar to the retry pattern from the evaluation course's reliability module, with a final dead-letter fallback for delivery that never succeeds.",
                        },
                    ],
                    "resources": [
                        {"title": "Celery: User guide", "url": "https://docs.celeryq.dev/en/stable/userguide/index.html", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "queue-based-architectures-for-long-running-agents",
                    "title": "Queue-Based Architectures for Long-Running Agents",
                    "description": "Structuring multi-stage agent pipelines as chained queue tasks rather than one monolithic task.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Decompose a long-running agent pipeline into chained, independently-retryable queue tasks",
                        "Apply backpressure by controlling worker concurrency and queue depth",
                        "Choose appropriate queue priority and routing for different task types",
                    ],
                    "content_markdown": """
## One giant task vs. a chain of smaller tasks

A single Celery task running an entire multi-step agent pipeline (research, then analyze, then
write, then email) is simple to write but fragile: if step 3 fails, you've lost the work from
steps 1 and 2 too, unless you've built manual checkpointing. Structuring the pipeline as chained
tasks — each stage its own task, passing results forward — gives you per-stage retry, per-stage
visibility, and the ability to reuse a stage's output if only a later stage needs to be retried.

```python
from celery import chain

@celery_app.task
def research_stage(query: str) -> dict:
    return {"findings": run_research_agent(query)}

@celery_app.task
def analyze_stage(research_result: dict) -> dict:
    return {**research_result, "analysis": run_analysis_agent(research_result["findings"])}

@celery_app.task
def write_stage(analysis_result: dict) -> dict:
    return {**analysis_result, "report": run_writer_agent(analysis_result["analysis"])}

pipeline = chain(research_stage.s("competitor pricing"), analyze_stage.s(), write_stage.s())
result = pipeline.apply_async()
```

If `write_stage` fails, only `write_stage` needs to retry — `research_stage` and `analyze_stage`
already succeeded and their results are preserved, mirroring the multi-agent handoff patterns
from earlier in the curriculum but implemented at the infrastructure layer.

## Backpressure through worker concurrency

An unbounded number of concurrent agent tasks can exhaust LLM API rate limits, database
connections, or memory all at once. Control concurrency explicitly at the worker level (Celery's
`--concurrency` flag, or a separate worker pool per task type) rather than letting the queue
dispatch every available task simultaneously — this is backpressure applied at the
infrastructure layer, working alongside the token-bucket rate limiting covered later in this
course.

```bash
# Limit this worker pool to 4 concurrent tasks, protecting downstream LLM rate limits
celery -A agent_tasks worker --concurrency=4 --queues=research_queue
```

## Priority and routing for different task types

Not every task deserves equal queue priority. A user-triggered interactive request (even one
offloaded to a queue because it's long-running) usually deserves priority over a scheduled batch
job. Route different task types to separate named queues with separate worker pools, so a
backlog of low-priority batch work never delays a user actively waiting on a result.

```python
celery_app.conf.task_routes = {
    "agent_tasks.run_research_task": {"queue": "interactive"},
    "agent_tasks.run_nightly_batch_summary": {"queue": "batch"},
}
```

## Monitoring queue depth as a health signal

Queue depth (how many tasks are waiting, not yet picked up by a worker) is one of the most
direct signals of whether your background processing capacity matches demand. A steadily growing
queue depth means workers can't keep up — this is exactly the kind of metric that belongs on the
health-monitoring dashboard from the evaluation course's observability module, with an alert rule
for sustained growth rather than a momentary spike.
""",
                    "examples": [
                        {
                            "title": "Example: retrying only the failed stage of a chain",
                            "code": (
                                "try:\n"
                                "    final = pipeline.apply_async().get(timeout=600)\n"
                                "except Exception:\n"
                                "    # research_stage and analyze_stage results are already persisted upstream;\n"
                                "    # only re-run write_stage using the previously stored analysis_result\n"
                                "    retry_result = write_stage.delay(stored_analysis_result)"
                            ),
                            "explanation": "Because each stage's output can be persisted independently, a failure late in the chain doesn't require redoing the expensive earlier stages.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Redesign a hypothetical single monolithic 'process_document' task (extract text, summarize, translate, email) into a chain of 4 separate tasks, and explain one concrete benefit of the split.",
                            "difficulty": "medium",
                            "hint": "Focus your benefit explanation on retry cost or per-stage observability, using the pattern shown in this lesson.",
                        },
                        {
                            "prompt": "Propose a queue-routing scheme for a system with 3 task types: interactive chat follow-ups, scheduled nightly reports, and user-triggered bulk exports. Justify the priority ordering.",
                            "difficulty": "easy",
                            "hint": "Interactive tasks usually get highest priority since a human is actively waiting; nightly reports have no urgency and can run whenever capacity allows.",
                        },
                    ],
                    "resources": [
                        {"title": "Celery: Canvas — designing workflows", "url": "https://docs.celeryq.dev/en/stable/userguide/canvas.html", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "logging",
            "title": "Logging",
            "description": "Structured logging for agent pipelines and correlating logs across multi-agent, multi-service requests.",
            "order_index": 7,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "structured-logging-for-agent-pipelines",
                    "title": "Structured Logging for Agent Pipelines",
                    "description": "Implementing structured, queryable logging across an agent service.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Configure structured JSON logging for a FastAPI agent service",
                        "Attach consistent contextual fields across a request's log lines",
                        "Separate log levels appropriately for agent-specific events",
                    ],
                    "content_markdown": """
## JSON logging as the default, not an afterthought

Plain-text log lines are fine for local development but painful to query at production scale.
Configure structured (JSON) logging from the start of a project, so every log line is a
consistent, filterable record from day one rather than requiring a painful migration later once
you have years of unstructured logs to reconcile.

```python
import structlog
import logging

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
log = structlog.get_logger()
```

## Binding request-scoped context automatically

Rather than passing `request_id`, `user_id`, and `conversation_id` explicitly into every single
log call throughout a request's lifecycle, bind them once at the top of the request and let every
subsequent log call in that context inherit them automatically.

```python
from fastapi import Request
import uuid

@app.middleware("http")
async def bind_request_context(request: Request, call_next):
    request_id = uuid.uuid4().hex
    structlog.contextvars.bind_contextvars(request_id=request_id)
    response = await call_next(request)
    structlog.contextvars.clear_contextvars()
    return response
```

Now any `log.info(...)` call anywhere in the request's code path — including inside deeply
nested agent or tool functions — automatically includes `request_id` without needing to thread it
through every function signature.

## Choosing log levels for agent-specific events

`DEBUG`: full prompt/response text, useful locally but usually too verbose and too
privacy-sensitive for default production logging. `INFO`: routine operational events — a tool
was called, a route decision was made, a run completed successfully. `WARNING`: a recoverable
but noteworthy event — a retry fired, a guardrail triggered, a cache miss on something expected
to usually hit. `ERROR`: an operation failed and could not recover automatically — a tool call
exhausted retries, an unhandled exception was caught by a top-level handler.

```python
log.info("tool_call", tool="lookup_order", conversation_id=conv_id, duration_ms=42)
log.warning("guardrail_triggered", check="injection_pattern", conversation_id=conv_id)
log.error("tool_call_failed", tool="issue_refund", conversation_id=conv_id, error=str(exc))
```

## Avoid logging what shouldn't be logged

Apply the PII redaction discipline from the evaluation course directly to your logging layer —
a structured logger makes it *easier* to accidentally log an entire request body verbatim (since
it's just one more field to pass in), which makes this an even easier mistake to make silently.
Build redaction into a shared logging helper used everywhere, rather than trusting every
individual log call site to remember it.
""",
                    "examples": [
                        {
                            "title": "Example: a full request's log lines sharing one request_id",
                            "code": (
                                "# All three lines below share request_id automatically via bound context\n"
                                "log.info('request_received', endpoint='/agent/chat')\n"
                                "log.info('tool_call', tool='lookup_order', duration_ms=38)\n"
                                "log.info('request_completed', status_code=200, duration_ms=1240)"
                            ),
                            "explanation": "Because request_id is bound once via middleware, every log line for this request can be grouped and traced together in a log aggregator without any call site needing to pass it explicitly.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add `conversation_id` to the bound context as soon as it's known (inside the route handler, after parsing the request body), so subsequent nested calls also inherit it automatically.",
                            "difficulty": "easy",
                            "hint": "Call structlog.contextvars.bind_contextvars(conversation_id=...) right after you have the value, not just in the middleware.",
                        },
                        {
                            "prompt": "Write a shared `safe_log` helper that wraps structlog's log.info but automatically redacts any field named 'message', 'content', or 'body' using the PII redaction function from the evaluation course before logging.",
                            "difficulty": "medium",
                            "hint": "Intercept the kwargs dict, apply redact() to values under those specific keys, then call through to the real logger.",
                        },
                    ],
                    "resources": [
                        {"title": "structlog: Documentation", "url": "https://www.structlog.org/en/stable/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "correlating-logs-across-multi-agent-requests",
                    "title": "Correlating Logs Across Multi-Agent Requests",
                    "description": "Propagating trace context across service and agent boundaries so a full request can be reconstructed.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Propagate a correlation id across service and agent boundaries",
                        "Distinguish request-level from run-level and agent-level identifiers",
                        "Reconstruct a full multi-agent trace from correlated logs after the fact",
                    ],
                    "content_markdown": """
## One request, many identifiers

A single user-facing request in a multi-agent system can span multiple internally meaningful
identifiers, and conflating them makes debugging harder, not easier. `request_id` identifies one
HTTP request. `run_id` identifies one full agent execution (which might outlive a single HTTP
request if offloaded to a queue, per the queues module). `agent_id`/`span_id` identifies one
specific agent or step within that run (from the tracing lesson in the evaluation course). Log
all three together, distinctly named, rather than collapsing them into a single generic "id"
field that loses this structure.

```python
log.info(
    "specialist_invoked",
    request_id=request_id,
    run_id=run_id,
    agent="billing_specialist",
    span_id=span_id,
)
```

## Propagating context across service boundaries

If an agent's tool call goes out to another internal microservice (not just a third-party API),
that service needs to receive and continue the same correlation ids, typically via HTTP headers,
so its own logs can be joined back to the originating request.

```python
async def call_internal_service(url: str, payload: dict, request_id: str, run_id: str):
    headers = {"X-Request-Id": request_id, "X-Run-Id": run_id}
    async with httpx.AsyncClient() as client:
        return await client.post(url, json=payload, headers=headers)
```

```python
@app.middleware("http")
async def propagate_incoming_context(request: Request, call_next):
    request_id = request.headers.get("X-Request-Id", uuid.uuid4().hex)
    run_id = request.headers.get("X-Run-Id", request_id)
    structlog.contextvars.bind_contextvars(request_id=request_id, run_id=run_id)
    return await call_next(request)
```

## Propagating across the queue boundary too

When work moves from an HTTP request into a background task (from the queues module), the
correlation ids need to travel with it explicitly as task arguments — a Celery worker process is
a different process entirely, with no shared request-scoped context to inherit from
automatically.

```python
@celery_app.task
def run_research_task(query: str, request_id: str, run_id: str):
    structlog.contextvars.bind_contextvars(request_id=request_id, run_id=run_id)
    return run_deep_research_agent(query)
```

## Reconstructing a trace after the fact

With consistent correlation ids logged everywhere, reconstructing what happened for one user's
report of "the agent gave me a wrong answer at 3:47pm" becomes a straightforward log query — pull
every log line matching that `run_id`, order by timestamp, and you have the complete story across
every specialist, tool call, and service boundary the request touched, without needing to
reproduce the issue live. This is the payoff for the discipline of consistent, propagated
correlation ids: turning "we can't reproduce it" into "here's exactly what happened."
""",
                    "examples": [
                        {
                            "title": "Example: a log query reconstructing one run's full trace",
                            "code": (
                                "# Pseudocode for a log-aggregator query\n"
                                "logs = log_store.query(run_id='run_8f2a1c', order_by='timestamp')\n"
                                "for entry in logs:\n"
                                "    print(entry['timestamp'], entry['agent'], entry['event'], entry.get('duration_ms'))"
                            ),
                            "explanation": "A well-correlated logging setup turns 'debug this one specific bad run' into a single filtered query rather than a manual cross-referencing exercise across multiple log sources.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Explain, in your own words, why run_id and request_id need to be distinct fields rather than always being the same value, using the queue-offloading scenario as your example.",
                            "difficulty": "easy",
                            "hint": "A queued task's run can continue well after the original HTTP request has already returned a 'queued' response and closed.",
                        },
                        {
                            "prompt": "Extend `call_internal_service` to also propagate a `span_id` representing the specific calling agent, and update the receiving service's middleware to bind it into its own logging context.",
                            "difficulty": "medium",
                            "hint": "Add 'X-Span-Id' as a third header alongside the two already shown, following the same propagate/bind pattern.",
                        },
                    ],
                    "resources": [
                        {"title": "W3C Trace Context specification", "url": "https://www.w3.org/TR/trace-context/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "monitoring",
            "title": "Monitoring",
            "description": "Instrumenting agent services with metrics and alerting on latency, cost, and error budgets.",
            "order_index": 8,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "instrumenting-agents-with-prometheus",
                    "title": "Instrumenting Agents with Prometheus Metrics",
                    "description": "Exposing counters, histograms, and gauges from an agent service for Prometheus scraping.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Instrument a FastAPI agent service with Prometheus counters and histograms",
                        "Choose appropriate metric types for latency, cost, and error tracking",
                        "Label metrics usefully without causing cardinality explosion",
                    ],
                    "content_markdown": """
## Metric types and what each is for

**Counters** only go up — total requests, total tool calls, total errors. **Histograms** track
the distribution of a value — latency, tokens used — letting you compute percentiles later, not
just an average that hides tail behavior. **Gauges** track a value that can go up or down at any
time — current queue depth, current number of in-flight requests.

```python
from prometheus_client import Counter, Histogram, Gauge, make_asgi_app

agent_requests_total = Counter(
    "agent_requests_total", "Total agent requests", ["specialist", "status"]
)
agent_request_duration = Histogram(
    "agent_request_duration_seconds", "Agent request duration", ["specialist"]
)
in_flight_requests = Gauge("agent_in_flight_requests", "Currently in-flight agent requests")

app.mount("/metrics", make_asgi_app())
```

## Instrumenting a route

```python
import time

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest) -> AgentResponse:
    in_flight_requests.inc()
    start = time.monotonic()
    specialist = "unknown"
    try:
        decision = route(request.message)
        specialist = decision.specialist
        result = await run_agent(request.message, specialist)
        agent_requests_total.labels(specialist=specialist, status="success").inc()
        return result
    except Exception:
        agent_requests_total.labels(specialist=specialist, status="error").inc()
        raise
    finally:
        agent_request_duration.labels(specialist=specialist).observe(time.monotonic() - start)
        in_flight_requests.dec()
```

## Cost as a first-class metric

Because LLM calls have a direct, meaningful dollar cost per request (unlike most traditional web
requests), track it explicitly as its own histogram, not just inferred from token counts buried
in logs — this is what feeds the cost-optimization module later in this course.

```python
llm_cost_usd = Histogram("llm_cost_usd", "Cost per LLM call in USD", ["model"])

def record_llm_cost(model: str, input_tokens: int, output_tokens: int):
    cost = calculate_cost(model, input_tokens, output_tokens)
    llm_cost_usd.labels(model=model).observe(cost)
```

## Avoiding cardinality explosion

Every unique combination of label values creates a new time series in Prometheus, and
high-cardinality labels (a raw `user_id` or `conversation_id` as a label) can create millions of
series, degrading or crashing your metrics backend. Use labels for low-cardinality dimensions
(specialist name, model name, status) and put high-cardinality identifiers (user id, request id)
in your structured logs and traces instead, where they belong — metrics are for aggregates,
logs and traces are for individual-instance detail.

```python
# Wrong: user_id as a label creates unbounded cardinality
agent_requests_total.labels(user_id=user_id, status="success").inc()

# Right: keep labels low-cardinality; user_id belongs in logs, not metrics
agent_requests_total.labels(specialist=specialist, status="success").inc()
log.info("request_completed", user_id=user_id, specialist=specialist)
```
""",
                    "examples": [
                        {
                            "title": "Example: a PromQL query for p95 latency by specialist",
                            "code": (
                                "# Run in Prometheus/Grafana, not Python\n"
                                "histogram_quantile(0.95,\n"
                                "  sum(rate(agent_request_duration_seconds_bucket[5m])) by (specialist, le)\n"
                                ")"
                            ),
                            "explanation": "This is exactly the kind of query the histogram metric type exists to support — computing a percentile, broken down by specialist, directly from the raw bucketed data collected in production.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a Gauge tracking current guardrail-triggered request rate over the last 5 minutes, and explain why this might be better implemented as a Counter queried with a rate() function in Prometheus instead of a Gauge you update manually.",
                            "difficulty": "medium",
                            "hint": "Prometheus's rate() function over a Counter is the idiomatic way to compute a rate over a time window — a manually-maintained Gauge duplicates work Prometheus already does well.",
                        },
                        {
                            "prompt": "Identify which of these would be safe metric labels and which would cause cardinality problems: model name, HTTP status code, conversation_id, specialist name, day-of-week.",
                            "difficulty": "easy",
                            "hint": "conversation_id is unbounded and grows forever — that's the cardinality red flag; the others are all small, fixed sets of values.",
                        },
                    ],
                    "resources": [
                        {"title": "Prometheus Python client library", "url": "https://github.com/prometheus/client_python", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "alerting-on-latency-cost-error-budgets",
                    "title": "Alerting on Latency, Cost, and Error Budgets",
                    "description": "Defining SLOs and error budgets for an agent service and alerting on budget burn rate.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Define a service level objective (SLO) for an agent service",
                        "Explain the error-budget-burn-rate approach to alerting",
                        "Set a cost budget alert distinct from latency and error alerts",
                    ],
                    "content_markdown": """
## SLOs give alerting a target to measure against

An SLO (service level objective) is a specific, measurable target — "99% of chat requests
complete in under 5 seconds" or "99.5% of requests succeed without error, measured over a
rolling 30 days." Without an explicit SLO, alert thresholds tend to be arbitrary numbers picked
once and never revisited; with one, every alert can be justified by "this threatens the SLO we
committed to."

```python
SLOS = {
    "latency_p95_seconds": {"target": 5.0, "window_days": 7},
    "success_rate": {"target": 0.995, "window_days": 30},
}
```

## Error budgets and burn rate

If your success-rate SLO is 99.5% over 30 days, your error budget is the remaining 0.5% — the
amount of failure you're allowed before breaching the SLO. Burn-rate alerting asks: at the
current rate of errors, how quickly is that budget being consumed? A burn rate of 1x means
you'll exactly exhaust the 30-day budget in 30 days (expected, fine). A burn rate of 20x means
you'll exhaust a 30-day budget in about 36 hours — that's the signal worth an urgent alert, even
though the absolute error count in any single short window might look small.

```python
def burn_rate(error_rate_now: float, slo_error_budget: float) -> float:
    return error_rate_now / slo_error_budget

# SLO: 99.5% success -> 0.5% error budget
current_error_rate = 0.05  # 5% errors right now
rate = burn_rate(current_error_rate, slo_error_budget=0.005)
print(rate)  # 10.0 — burning the monthly budget 10x faster than sustainable
```

This is a more principled alerting signal than a flat "alert if error rate > X%" threshold,
because it directly ties the alert to whether you're actually at risk of breaching a commitment,
scaled appropriately by how aggressive or lenient that commitment is.

## Cost budgets as their own alert category

Unlike traditional services, agent systems have a direct, continuously-accruing dollar cost that
can spike independently of latency or error rate — a bug that causes an agent to loop and burn
tokens (the loop-detection failure mode from the evaluation course) can be entirely invisible to
latency and error-rate monitoring while still being a real incident. Track cost per hour (or per
day) against a budget, with its own alert tier, separate from performance SLOs.

```python
COST_BUDGET_USD_PER_HOUR = 50.0

def check_cost_alert(current_hourly_spend: float) -> str | None:
    if current_hourly_spend > COST_BUDGET_USD_PER_HOUR * 2:
        return "page"  # spending at 2x budget — likely a bug, not just higher traffic
    if current_hourly_spend > COST_BUDGET_USD_PER_HOUR * 1.2:
        return "urgent"
    return None
```

## Reviewing SLOs and budgets periodically

SLOs and cost budgets aren't set-once constants — revisit them as traffic patterns, model
pricing, and business priorities change. A budget set when the service had 100 daily users needs
revisiting at 10,000 daily users, and a latency SLO set against one model's typical response time
needs revisiting after a model upgrade changes that baseline meaningfully.
""",
                    "examples": [
                        {
                            "title": "Example: multi-window burn rate check to reduce false positives",
                            "code": (
                                "def multi_window_burn_alert(rate_1h: float, rate_6h: float, threshold: float = 10.0) -> bool:\n"
                                "    # require both a short window AND a longer window to confirm sustained burn,\n"
                                "    # avoiding a page triggered by one noisy 5-minute spike\n"
                                "    return rate_1h >= threshold and rate_6h >= threshold"
                            ),
                            "explanation": "Requiring agreement across two time windows before paging is a standard SRE technique to avoid false-positive alerts from momentary noise while still catching genuinely sustained problems quickly.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Define an SLO for tool-call success rate for an agent service, including target percentage and measurement window, and justify your chosen numbers.",
                            "difficulty": "easy",
                            "hint": "Consider that tool calls to flaky third-party APIs might warrant a slightly more lenient SLO than the agent's own core success rate.",
                        },
                        {
                            "prompt": "Implement `check_cost_alert`'s companion function that also compares current spend against the same hour yesterday and same hour last week, flagging an anomaly if current spend is more than 3x either baseline.",
                            "difficulty": "hard",
                            "hint": "You'll need historical cost data queryable by hour-of-day; compare current_hourly_spend against both baselines and flag if it exceeds 3x either one.",
                        },
                    ],
                    "resources": [
                        {"title": "Google SRE Book: Implementing SLOs", "url": "https://sre.google/workbook/implementing-slos/", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "deployment",
            "title": "Deployment",
            "description": "Containerizing and safely rolling out an agent service to production.",
            "order_index": 9,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "containerizing-an-agent-service-with-docker",
                    "title": "Containerizing an Agent Service with Docker",
                    "description": "Building a production-appropriate Docker image for a FastAPI agent service.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 25,
                    "learning_objectives": [
                        "Write a multi-stage Dockerfile for a FastAPI agent service",
                        "Manage secrets and configuration without baking them into the image",
                        "Configure health checks appropriate for an agent service's dependencies",
                    ],
                    "content_markdown": """
## A multi-stage Dockerfile

Multi-stage builds keep the final image lean by separating build-time dependencies (compilers,
build tools) from what's actually needed at runtime.

```dockerfile
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
```

Running as a non-root user is a basic hardening step worth including by default:

```dockerfile
RUN useradd --create-home appuser
USER appuser
```

## Secrets never belong in the image

API keys, database credentials, and JWT signing secrets must never be baked into the Docker
image via `COPY` or a hardcoded `ENV` — anyone with access to the image (including anyone who
can pull it from a registry) can extract them. Inject secrets at runtime through environment
variables set by your orchestration platform (Kubernetes secrets, a cloud provider's secret
manager) or mounted files, never committed into the image layers.

```python
# main.py reads secrets from the environment at runtime, never from a file baked into the image
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    anthropic_api_key: str
    database_url: str
    jwt_secret: str

    class Config:
        env_file = ".env"  # for local dev only — never copied into the production image

settings = Settings()
```

## Health checks that reflect real readiness

A health check that only confirms "the web server process is running" misses the more important
question for an agent service: can it actually reach its dependencies (the LLM API, the
database, Redis)? A shallow health check can report healthy while the service is actually unable
to serve any real request.

```python
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/health/ready")
async def readiness():
    checks = {
        "database": await check_database_connection(),
        "redis": await check_redis_connection(),
        "llm_api": await check_llm_api_reachable(),
    }
    healthy = all(checks.values())
    return JSONResponse(
        status_code=200 if healthy else 503,
        content={"status": "ready" if healthy else "not_ready", "checks": checks},
    )
```

Use `/health` (liveness — is the process alive at all) for restart decisions and `/health/ready`
(readiness — can it actually serve traffic right now) for load balancer routing decisions; these
answer different questions and orchestration platforms typically support configuring both
separately.
""",
                    "examples": [
                        {
                            "title": "Example: a .dockerignore preventing secrets and bloat from entering the build context",
                            "code": (
                                ".env\n"
                                "*.pem\n"
                                "__pycache__/\n"
                                "*.pyc\n"
                                ".git/\n"
                                "tests/\n"
                                "*.md"
                            ),
                            "explanation": "A .dockerignore file prevents accidentally including a local .env file or credentials in the build context in the first place, which is a stronger guarantee than relying on remembering not to COPY them explicitly.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Add a HEALTHCHECK instruction to the Dockerfile that calls /health every 30 seconds, and explain the difference between this Docker-level healthcheck and the /health/ready endpoint's purpose.",
                            "difficulty": "easy",
                            "hint": "HEALTHCHECK CMD curl -f http://localhost:8000/health || exit 1 — this is for Docker/container orchestration restart decisions, distinct from load-balancer readiness routing.",
                        },
                        {
                            "prompt": "Implement `check_llm_api_reachable()` as a lightweight check (not a full generation call) that verifies connectivity without incurring meaningful token cost on every health check poll.",
                            "difficulty": "medium",
                            "hint": "Many LLM provider SDKs expose a lightweight models-list or similar low-cost endpoint suitable for connectivity checks rather than a real completion call.",
                        },
                    ],
                    "resources": [
                        {"title": "Docker: Multi-stage builds", "url": "https://docs.docker.com/build/building/multi-stage/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "blue-green-and-canary-deployments",
                    "title": "Blue-Green and Canary Deployments for Agents",
                    "description": "Rolling out agent changes (prompt updates, model swaps) with reduced blast radius.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Compare blue-green and canary deployment strategies",
                        "Apply gradual rollout specifically to prompt and model changes, not just code",
                        "Define rollback triggers based on agent-specific metrics",
                    ],
                    "content_markdown": """
## Deployment strategy applies to prompts and models too, not just code

Traditional deployment strategy discussions focus on application code changes. For agent
systems, the same discipline needs to apply to prompt changes and model version swaps — a new
system prompt or a switch to a new model version is just as capable of degrading quality as a
code bug, and often less immediately obvious, since it might not throw an exception at all, just
quietly produce worse answers.

## Blue-green deployment

Run two complete environments ("blue" = current production, "green" = new version), fully
switch traffic from blue to green once green is verified, and keep blue running as an instant
rollback target. This gives a clean, instant cutover and rollback, at the cost of running double
infrastructure during the transition.

```python
# Router-level cutover, not a code deploy
ACTIVE_ENVIRONMENT = "blue"  # flip to "green" once verified

def route_to_environment(request):
    return ENVIRONMENTS[ACTIVE_ENVIRONMENT].handle(request)
```

## Canary deployment

Route a small percentage of traffic to the new version while most traffic stays on the current
one, gradually increasing the new version's share as confidence builds. This limits blast radius
if something's wrong — 5% of users hitting a regression is a much smaller incident than 100% —
at the cost of running two versions concurrently for longer and needing traffic-splitting
infrastructure.

```python
import random

def route_with_canary(request, canary_percent: float = 5.0):
    if random.random() * 100 < canary_percent:
        return new_agent_version.handle(request)
    return current_agent_version.handle(request)
```

For a prompt or model change specifically, canary is usually the safer default over blue-green,
precisely because prompt/model regressions are often subtle quality issues rather than hard
crashes — a small canary percentage combined with the evaluation harness from earlier in this
curriculum, run continuously against canary traffic, catches subtle degradation before it reaches
everyone.

## Rollback triggers specific to agent quality

Beyond the standard rollback triggers (error rate, latency), define rollback triggers tied to
agent-specific quality metrics from the evaluation course: a drop in average faithfulness score,
a spike in guardrail triggers, or a spike in loop-detection exits on canary traffic versus the
baseline version. A canary that has zero code errors but a measurably worse faithfulness score
is still a regression that should trigger a rollback.

```python
def should_rollback_canary(canary_metrics: dict, baseline_metrics: dict) -> bool:
    if canary_metrics["error_rate"] > baseline_metrics["error_rate"] * 1.5:
        return True
    if canary_metrics["avg_faithfulness"] < baseline_metrics["avg_faithfulness"] - 0.1:
        return True
    if canary_metrics["guardrail_trigger_rate"] > baseline_metrics["guardrail_trigger_rate"] * 2:
        return True
    return False
```

## Automating the rollback decision, not just the metric collection

Where possible, wire canary metric comparison into an automated rollback (revert the traffic
split back to 0% on the new version) rather than requiring a human to notice and act — the delay
between "the metrics show a problem" and "a human sees the dashboard and acts" is exactly the
window where a bad canary continues causing harm to the small percentage of users routed to it.
""",
                    "examples": [
                        {
                            "title": "Example: gradually increasing canary share on sustained good metrics",
                            "code": (
                                "def next_canary_percent(current: float, metrics_healthy: bool) -> float:\n"
                                "    if not metrics_healthy:\n"
                                "        return 0.0  # roll back immediately\n"
                                "    return min(current * 2, 100.0)  # double share on each healthy check, capped at 100%"
                            ),
                            "explanation": "A simple doubling ramp (5% -> 10% -> 20% -> ...) with an immediate full rollback on unhealthy metrics balances rollout speed against caution without needing a complex scheduler.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "For a change that swaps the underlying LLM model version (not a code change), argue whether blue-green or canary is the more appropriate strategy, and why.",
                            "difficulty": "medium",
                            "hint": "Consider that model swaps often cause subtle quality shifts rather than hard failures — which strategy limits exposure to a subtle, hard-to-detect regression better?",
                        },
                        {
                            "prompt": "Extend `should_rollback_canary` to also check cost per request, rolling back if canary cost per request exceeds baseline by more than 50%, and explain why cost regressions deserve their own rollback trigger separate from quality metrics.",
                            "difficulty": "easy",
                            "hint": "A prompt change could accidentally cause much longer generations (more output tokens) without any quality or error signal changing at all.",
                        },
                    ],
                    "resources": [
                        {"title": "Martin Fowler: BlueGreenDeployment", "url": "https://martinfowler.com/bliki/BlueGreenDeployment.html", "resource_type": "article"},
                        {"title": "Martin Fowler: CanaryRelease", "url": "https://martinfowler.com/bliki/CanaryRelease.html", "resource_type": "article"},
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "cost-optimization",
            "title": "Cost Optimization",
            "description": "Controlling LLM spend through token budgeting, model routing, and prompt efficiency.",
            "order_index": 10,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "token-budgeting-and-model-routing",
                    "title": "Token Budgeting and Model Routing",
                    "description": "Setting per-request token budgets and routing requests to the cheapest capable model.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a per-request token budget enforcement mechanism",
                        "Design a model-routing strategy that matches task difficulty to model cost",
                        "Track cost attribution by feature, customer, or specialist",
                    ],
                    "content_markdown": """
## Token budgets as a hard limit, not just a cost estimate

Beyond tracking cost after the fact, enforce a per-request or per-conversation token budget
proactively — a runaway agent loop (from the evaluation course's reliability module) or an
unexpectedly long tool-result chain can otherwise consume far more tokens than any single
request should reasonably need.

```python
class TokenBudgetExceeded(Exception):
    pass

class TokenBudget:
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used = 0

    def consume(self, tokens: int):
        self.used += tokens
        if self.used > self.max_tokens:
            raise TokenBudgetExceeded(f"used {self.used}, budget {self.max_tokens}")

async def run_agent_with_budget(task: str, max_tokens: int = 50_000) -> str:
    budget = TokenBudget(max_tokens)
    for step in agent_loop(task):
        response = await llm_call(step)
        budget.consume(response.usage.total_tokens)
    return final_result
```

## Model routing: match task difficulty to model cost

Not every request needs your most expensive, most capable model. Route simple, well-defined
tasks (classification, short factual lookups, routing decisions) to a smaller, cheaper model, and
reserve the most capable model for tasks that genuinely need deep reasoning (complex analysis,
nuanced writing, multi-step planning).

```python
def select_model(task_type: str) -> str:
    ROUTING = {
        "intent_classification": "claude-haiku-4-5",
        "simple_lookup": "claude-haiku-4-5",
        "customer_conversation": "claude-sonnet-4-5",
        "complex_analysis": "claude-opus-4-1",
    }
    return ROUTING.get(task_type, "claude-sonnet-4-5")
```

The supervisor's own routing decision (from the multi-agent course) is itself usually a great
candidate for a cheaper model — classifying which specialist should handle a request rarely needs
your most expensive model's full reasoning capability, even though the specialist it routes to
might.

## Cost attribution

Track cost broken down by dimensions that map to business decisions: which feature, which
customer/tenant, which specialist is driving spend. Without this breakdown, "our LLM bill went up
30%" is a fact you can observe but can't act on; with it, you can identify that, say, one
specific specialist's prompts got 3x longer after a recent change, or one enterprise customer's
usage pattern is disproportionately expensive relative to their plan.

```python
def record_cost(specialist: str, tenant_id: str, model: str, cost_usd: float):
    cost_ledger.insert({
        "specialist": specialist, "tenant_id": tenant_id,
        "model": model, "cost_usd": cost_usd, "timestamp": time.time(),
    })

def cost_by_specialist(since: float) -> dict[str, float]:
    entries = cost_ledger.query(since=since)
    totals = {}
    for e in entries:
        totals[e["specialist"]] = totals.get(e["specialist"], 0) + e["cost_usd"]
    return totals
```

## Budget enforcement should degrade gracefully, not just fail

When a token budget is exceeded mid-run, don't just raise an unhandled exception to the user.
Catch it and either return the best partial result accumulated so far with an honest note, or
fall back to a cheaper/faster completion strategy — the same graceful-degradation principle from
the API integration module, applied to your own internal cost controls rather than an external
dependency's failure.
""",
                    "examples": [
                        {
                            "title": "Example: graceful degradation when a budget is hit mid-run",
                            "code": (
                                "async def run_agent_safe(task: str, max_tokens: int = 50_000) -> str:\n"
                                "    try:\n"
                                "        return await run_agent_with_budget(task, max_tokens)\n"
                                "    except TokenBudgetExceeded:\n"
                                "        log.warning('token_budget_exceeded', task_preview=task[:100])\n"
                                "        return 'This request needed more processing than usual — here\\'s what I found so far: ' + partial_result"
                            ),
                            "explanation": "Returning a partial, honest answer is a better user experience than an opaque error, while still surfacing the event for engineering review via the warning log.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a model-routing table for a 5-specialist system, assigning each specialist a model tier (cheap/mid/premium) based on the complexity of its typical task, with justification.",
                            "difficulty": "medium",
                            "hint": "A routing/classification specialist and a billing lookup specialist likely belong on a cheaper tier than a specialist doing open-ended research synthesis.",
                        },
                        {
                            "prompt": "Extend `cost_by_specialist` to also compute cost per successful task completion (not just raw cost), and explain why this normalized metric can reveal a different priority order than raw cost alone.",
                            "difficulty": "hard",
                            "hint": "A specialist with high raw cost but a very high success/volume rate might have a lower and more acceptable cost-per-success than a cheaper specialist that fails often and needs retries.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Pricing", "url": "https://www.anthropic.com/pricing", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "batching-and-prompt-compression",
                    "title": "Batching and Prompt Compression Strategies",
                    "description": "Reducing token spend through request batching, prompt caching, and context trimming.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Apply provider-level batch APIs for non-urgent workloads",
                        "Use prompt caching for repeated, stable context",
                        "Trim and compress conversation history without losing needed information",
                    ],
                    "content_markdown": """
## Batch APIs for non-urgent work

Most major LLM providers offer a batch API — submit a large set of requests together for
asynchronous processing at a significant discount (often around 50%) compared to synchronous
calls, in exchange for higher latency (results within hours, not seconds). Any workload that
doesn't need a real-time response — nightly summarization jobs, bulk classification, offline
evaluation runs — is a strong candidate for the batch API rather than the standard synchronous
endpoint.

```python
batch_requests = [
    {"custom_id": f"doc_{i}", "params": {"model": "claude-sonnet-4-5", "messages": [...]}}
    for i, doc in enumerate(documents_to_summarize)
]
batch = await async_llm_client.batches.create(requests=batch_requests)
# poll batch.id for completion, results available at a fraction of synchronous cost
```

## Prompt caching for stable, repeated context

When the same large block of context (a system prompt, a set of few-shot examples, a knowledge
base excerpt) is sent on every request, provider-level prompt caching lets the provider reuse the
processed representation of that stable prefix instead of reprocessing it from scratch each time,
cutting both cost and latency for the cached portion.

```python
response = await async_llm_client.messages.create(
    model="claude-sonnet-4-5",
    system=[
        {"type": "text", "text": LONG_STABLE_SYSTEM_PROMPT, "cache_control": {"type": "ephemeral"}},
    ],
    messages=[{"role": "user", "content": user_message}],
)
```

Structure prompts so the stable, reusable portion (instructions, few-shot examples, static
reference material) comes first and the variable, request-specific portion comes last — this
maximizes what can actually be served from cache across requests, since a cache typically applies
to a matching prefix, not the whole prompt indiscriminately.

## Trimming conversation history deliberately

A long-running conversation's full history sent on every turn grows linearly in cost per turn.
Apply the same summarization/handoff techniques from the multi-agent communication module: once
history exceeds a threshold, summarize older turns into a compact recap and keep only recent
turns verbatim, rather than sending an ever-growing, unbounded transcript on every single call.

```python
def build_context(history: list[Message], max_recent: int = 10) -> list[dict]:
    if len(history) <= max_recent:
        return [m.to_dict() for m in history]
    older, recent = history[:-max_recent], history[-max_recent:]
    summary = summarize_history(older)  # a cheaper model call, done once and cached
    return [{"role": "system", "content": f"Earlier conversation summary: {summary}"}] + [m.to_dict() for m in recent]
```

## Compression is a trade-off against fidelity, not a free win

Every compression technique here — batching, caching, summarization — trades something: batching
trades latency, summarization trades some fidelity of older context. Apply them deliberately
based on what each specific workload can actually tolerate, verified against the evaluation
harness from earlier in the curriculum (does summarized history still produce faithful, relevant
answers?), rather than applying every cost optimization uniformly everywhere regardless of
whether that workload can absorb the trade-off.
""",
                    "examples": [
                        {
                            "title": "Example: estimating savings from prompt caching on a stable system prompt",
                            "code": (
                                "system_prompt_tokens = 3000\n"
                                "requests_per_day = 10_000\n"
                                "uncached_cost_per_day = system_prompt_tokens * requests_per_day * INPUT_TOKEN_PRICE\n"
                                "cached_cost_per_day = system_prompt_tokens * INPUT_TOKEN_PRICE + (\n"
                                "    system_prompt_tokens * requests_per_day * CACHED_TOKEN_PRICE\n"
                                ")\n"
                                "print(f'savings: ${uncached_cost_per_day - cached_cost_per_day:.2f}/day')"
                            ),
                            "explanation": "For a large, stable system prompt sent on every one of many daily requests, prompt caching's savings scale directly with request volume, which is why it's one of the highest-leverage cost optimizations for high-traffic agent services.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Identify two workloads in a typical agent system that are good batch-API candidates and two that are not, with justification based on latency requirements.",
                            "difficulty": "easy",
                            "hint": "Anything user-facing and interactive is a poor batch candidate; anything scheduled or bulk/offline is a good one.",
                        },
                        {
                            "prompt": "Implement `summarize_history` so it's only re-computed when the 'older' portion of history actually changes, caching the summary rather than regenerating it on every single turn even when older messages haven't changed.",
                            "difficulty": "medium",
                            "hint": "Key a cache by a hash of the older messages' content, similar to the exact-match LLM response caching pattern from the caching module.",
                        },
                    ],
                    "resources": [
                        {"title": "Anthropic: Prompt caching", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching", "resource_type": "docs"},
                        {"title": "Anthropic: Message Batches API", "url": "https://docs.anthropic.com/en/docs/build-with-claude/batch-processing", "resource_type": "docs"},
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
        {
            "slug": "rate-limiting",
            "title": "Rate Limiting",
            "description": "Protecting an agent service and its dependencies from overload with rate limiting and backpressure.",
            "order_index": 11,
            "estimated_hours": 1.5,
            "lessons": [
                {
                    "slug": "rate-limiting-with-redis-and-fastapi",
                    "title": "Implementing Rate Limiting with Redis and FastAPI",
                    "description": "Building a token-bucket rate limiter as FastAPI middleware, backed by Redis.",
                    "lesson_type": "coding",
                    "order_index": 1,
                    "estimated_minutes": 30,
                    "learning_objectives": [
                        "Implement a token-bucket rate limiter backed by Redis",
                        "Apply per-caller rate limits as FastAPI middleware or a dependency",
                        "Return correct rate-limit response headers to well-behaved clients",
                    ],
                    "content_markdown": """
## Why rate limiting matters specifically for agent services

Beyond the usual reasons (protecting against abuse, ensuring fair usage across customers), agent
services have a rate-limiting-specific concern: the LLM provider itself imposes rate limits, and
a single misbehaving client can exhaust your entire shared quota, degrading service for every
other caller. Rate limiting your own API is partly about protecting your downstream LLM provider
relationship, not just protecting your own infrastructure.

## Token bucket algorithm with Redis

The token bucket algorithm allows short bursts while enforcing a sustained average rate — a
caller accumulates tokens over time up to a cap, and each request consumes one; if the bucket is
empty, the request is rejected or delayed. Redis makes this straightforward to implement
correctly across multiple service instances sharing the same rate limit state.

```python
import time

async def check_rate_limit(redis_client, key: str, capacity: int, refill_rate_per_sec: float) -> bool:
    now = time.time()
    bucket_key = f"ratelimit:{key}"
    async with redis_client.pipeline(transaction=True) as pipe:
        bucket = await redis_client.hgetall(bucket_key)
        tokens = float(bucket.get(b"tokens", capacity))
        last_refill = float(bucket.get(b"last_refill", now))

        elapsed = now - last_refill
        tokens = min(capacity, tokens + elapsed * refill_rate_per_sec)

        if tokens < 1:
            return False

        tokens -= 1
        await pipe.hset(bucket_key, mapping={"tokens": tokens, "last_refill": now})
        await pipe.expire(bucket_key, 3600)
        await pipe.execute()
        return True
```

## Applying it as a FastAPI dependency

```python
from fastapi import Depends, HTTPException

async def enforce_rate_limit(owner_id: str = Depends(verify_api_key)):
    allowed = await check_rate_limit(
        redis_client, key=owner_id, capacity=100, refill_rate_per_sec=100 / 60
    )
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="rate limit exceeded",
            headers={"Retry-After": "1"},
        )
    return owner_id

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest, owner_id: str = Depends(enforce_rate_limit)) -> AgentResponse:
    ...
```

## Returning informative rate-limit headers

Well-behaved clients benefit from knowing their current rate-limit status even on successful
requests, not just when they're blocked — this lets them self-throttle proactively rather than
discovering the limit by hitting it.

```python
from fastapi import Response

@app.post("/agent/chat", response_model=AgentResponse)
async def chat(request: AgentRequest, response: Response, owner_id: str = Depends(enforce_rate_limit)):
    remaining = await get_remaining_tokens(redis_client, owner_id)
    response.headers["X-RateLimit-Remaining"] = str(int(remaining))
    response.headers["X-RateLimit-Limit"] = "100"
    return await run_agent(request.message, owner_id)
```

## Tiered limits by caller type

Not every caller needs the same limit. A free-tier API key, a paid-tier key, and an internal
service-to-service call typically warrant different capacity and refill rates — encode this as a
lookup rather than a single global constant, so limits can evolve independently per tier without
code changes to the enforcement logic itself.

```python
RATE_LIMIT_TIERS = {
    "free": {"capacity": 20, "refill_per_sec": 20 / 3600},
    "paid": {"capacity": 500, "refill_per_sec": 500 / 3600},
    "internal": {"capacity": 10_000, "refill_per_sec": 10_000 / 60},
}
```
""",
                    "examples": [
                        {
                            "title": "Example: a client that respects rate-limit headers to self-throttle",
                            "code": (
                                "response = httpx.post(url, json=payload)\n"
                                "remaining = int(response.headers.get('X-RateLimit-Remaining', 1))\n"
                                "if remaining < 5:\n"
                                "    time.sleep(2)  # proactively back off before hitting the hard limit"
                            ),
                            "explanation": "Exposing remaining-capacity headers lets well-behaved clients avoid ever seeing a 429 in the first place, which is a better experience for everyone than only signaling the limit at the moment it's breached.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Implement `get_remaining_tokens(redis_client, key)` matching the bucket state format used by `check_rate_limit`.",
                            "difficulty": "easy",
                            "hint": "Read the same hash fields (tokens, last_refill) and compute the current refilled token count the same way check_rate_limit does, without consuming one.",
                        },
                        {
                            "prompt": "Extend the rate limiter to support a separate, stricter limit specifically for the most expensive route (e.g., a deep-research endpoint) layered on top of the general per-caller limit.",
                            "difficulty": "hard",
                            "hint": "Use a compound key like f'ratelimit:{owner_id}:{route_name}' for the route-specific bucket, checked in addition to (not instead of) the general per-caller bucket.",
                        },
                    ],
                    "resources": [
                        {"title": "Redis: Rate limiting patterns", "url": "https://redis.io/glossary/rate-limiting/", "resource_type": "docs"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
                {
                    "slug": "backpressure-and-graceful-degradation",
                    "title": "Backpressure and Graceful Degradation",
                    "description": "Shedding or degrading load intentionally when the system approaches capacity, rather than falling over.",
                    "lesson_type": "reading",
                    "order_index": 2,
                    "estimated_minutes": 20,
                    "learning_objectives": [
                        "Distinguish rate limiting from backpressure and load shedding",
                        "Design a graceful degradation strategy for an overloaded agent service",
                        "Prioritize which requests to serve first under sustained overload",
                    ],
                    "content_markdown": """
## Rate limiting, backpressure, and load shedding are related but distinct

Rate limiting controls how much any single caller can send, enforced regardless of overall system
load. Backpressure is a system-wide signal that capacity is currently constrained, propagated
back to callers (or to earlier stages of an internal pipeline) so they slow down before things get
worse. Load shedding is the last resort: deliberately refusing some requests outright when the
system is overloaded, to protect its ability to serve the requests it does accept, rather than
degrading uniformly until everything times out.

## Signaling backpressure internally

If your queue depth (from the queues module) or in-flight request gauge (from the monitoring
module) crosses a threshold, that's a backpressure signal your own request-handling layer should
react to — not just something to display on a dashboard after the fact.

```python
MAX_IN_FLIGHT = 200

@app.middleware("http")
async def backpressure_check(request: Request, call_next):
    if in_flight_requests._value.get() > MAX_IN_FLIGHT:
        return JSONResponse(
            status_code=503,
            content={"error": "service_at_capacity", "retry_after_seconds": 5},
            headers={"Retry-After": "5"},
        )
    return await call_next(request)
```

## Graceful degradation over binary up/down

Under sustained load, a well-designed agent service degrades progressively rather than serving
every request perfectly until it suddenly serves none at all. Concrete degradation steps:
disable optional, expensive verification steps (the faithfulness/grounding checks from the
evaluation course) temporarily under extreme load while keeping the core response path working;
switch to a cheaper, faster model tier for new requests while capacity is constrained; shorten
retrieved context or skip non-essential tool calls. Each of these trades quality for
availability deliberately, which is a better trade-off under real overload than an outage that
serves nobody.

```python
def select_model_under_load(current_load_pct: float) -> str:
    if current_load_pct > 90:
        return "claude-haiku-4-5"  # degrade to cheaper/faster model under extreme load
    return "claude-sonnet-4-5"
```

## Prioritizing which requests to serve first

Under sustained overload where load shedding is unavoidable, decide deliberately which requests
to shed first rather than shedding randomly. Common priority signals: paying customers over
free-tier, interactive requests over batch/background work (tying back to the queue-routing
priority from the queues module), and requests already in-progress (partway through a multi-step
agent run) over brand-new requests, since abandoning in-progress work wastes the resources
already spent on it.

```python
def should_accept_under_load(request_priority: str, current_load_pct: float) -> bool:
    THRESHOLDS = {"paid": 98, "free": 80, "batch": 60}
    return current_load_pct < THRESHOLDS.get(request_priority, 80)
```

## Backpressure needs to be visible to callers, not just internal

A caller receiving a 503 with a `Retry-After` header and a clear `service_at_capacity` error code
can react sensibly (back off, retry later, alert their own on-call). A caller receiving a
generic timeout or connection reset has no signal to act on and will likely retry immediately,
making the overload worse. Treat the shape of your degradation response as part of the design,
not an afterthought — a clear, actionable error under load is itself a form of graceful behavior.
""",
                    "examples": [
                        {
                            "title": "Example: distinguishing the three concepts in one incident timeline",
                            "code": (
                                "# 1. Rate limiting: a single caller sending 1000 req/s gets 429s immediately, unrelated to overall load\n"
                                "# 2. Backpressure: overall queue depth crosses a threshold; the service starts returning 503s to NEW requests\n"
                                "# 3. Load shedding: under sustained 503s, free-tier requests are shed first while paid-tier continues"
                            ),
                            "explanation": "These three mechanisms operate on different signals (per-caller volume, system-wide load, and priority under scarcity) and typically all exist together in a mature system, each catching a different failure scenario.",
                        }
                    ],
                    "practice_exercises": [
                        {
                            "prompt": "Design a degradation ladder (3-4 steps, from 'normal operation' to 'severe overload') for an agent service, specifying what capability is reduced or disabled at each step.",
                            "difficulty": "medium",
                            "hint": "Order steps from least to most impactful: e.g., disable optional verification first, switch model tier second, shed low-priority traffic last.",
                        },
                        {
                            "prompt": "Explain why abandoning in-progress multi-step agent runs during load shedding is worse than rejecting brand-new requests, and propose one way to protect in-progress runs specifically.",
                            "difficulty": "hard",
                            "hint": "Resources (tokens, tool calls) already spent on an in-progress run are sunk cost if abandoned; consider tracking run state so shedding logic can check 'is this a continuation of existing work' before rejecting.",
                        },
                    ],
                    "resources": [
                        {"title": "AWS Builders' Library: Avoiding overload with load shedding", "url": "https://aws.amazon.com/builders-library/using-load-shedding-to-avoid-overload/", "resource_type": "article"}
                    ],
                    "skills": [{"slug": "production-ai", "weight": 1.0}],
                },
            ],
        },
    ],
}

COURSE_EXAM = {
    "title": "Production AI Agents: Course Assessment",
    "description": "Checks readiness to design, deploy, and operate agent services in production before capstone project work.",
    "assessment_type": "course_exam",
    "passing_score": 0.7,
    "time_limit_minutes": 45,
    "questions": [
        {
            "question_type": "mcq",
            "prompt": "Why does calling a synchronous LLM SDK client from inside an `async def` FastAPI route defeat much of the benefit of using async in the first place?",
            "options": [
                {"id": "a", "text": "FastAPI does not support synchronous function calls at all"},
                {"id": "b", "text": "The synchronous call blocks the event loop, preventing FastAPI from handling other requests concurrently while it waits"},
                {"id": "c", "text": "Synchronous SDKs cannot authenticate correctly"},
                {"id": "d", "text": "Async routes automatically reject any blocking call with an error"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "A blocking synchronous call inside an async route ties up the single event loop thread, preventing concurrent handling of other requests — the async SDK variant (or offloading to a thread pool) is needed to preserve concurrency.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "When a client disconnects mid-stream from an SSE endpoint, what is the correct behavior for the server?",
            "options": [
                {"id": "a", "text": "Continue generating the full response regardless, since the LLM call has already started"},
                {"id": "b", "text": "Catch the resulting CancelledError, stop the upstream generation, and log the partial completion"},
                {"id": "c", "text": "Immediately restart the entire request from scratch"},
                {"id": "d", "text": "Ignore the disconnect since SSE does not support detecting it"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Continuing to generate (and pay for) tokens nobody will see wastes resources; catching the cancellation and stopping upstream generation is the correct, cost-aware behavior.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "Why should API keys be stored hashed in the database rather than in plaintext?",
            "options": [
                {"id": "a", "text": "Hashed keys are faster to look up than plaintext"},
                {"id": "b", "text": "So that a database breach doesn't directly expose usable credentials, the same principle applied to password storage"},
                {"id": "c", "text": "FastAPI requires hashed keys to function"},
                {"id": "d", "text": "Hashing allows the original key to be recovered if a user forgets it"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Storing keys hashed means a database compromise doesn't hand an attacker directly usable credentials — the same reasoning applied to password storage, and hashing is one-way, so it does not support recovering the original value.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "scenario",
            "prompt": "A caller authenticated with a JWT that only has the 'tools:read_only' scope manages to trigger the agent's write-capable 'issue_refund' tool, because the route-level check only verified 'agent:chat' scope and nothing checked the tool-dispatch layer. What's the missing control, and where should it live?",
            "options": [],
            "correct_answer": {"expected": "The missing control is a scope check at the tool-dispatch layer itself, not just the route layer — before executing any tool call, the system should verify the caller's scopes include that specific tool's required scope (e.g., issue_refund requiring 'tools:write'), rejecting the call if not, since route-level scopes don't know which tools the agent might invoke mid-conversation."},
            "explanation": "Route-level scope checks only gate entry to the endpoint; tool-level scope enforcement is needed because the agent's tool choices are decided dynamically mid-conversation, not fixed by which route was called.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "In a shared-schema multi-tenant database design, why is relying solely on developers remembering to add a `WHERE tenant_id = ...` filter to every query considered risky?",
            "options": [
                {"id": "a", "text": "It's not risky — this is a fully sufficient isolation strategy on its own"},
                {"id": "b", "text": "A single forgotten filter (e.g., during time pressure, a new team member, or a silent ORM join) can directly leak one tenant's data to another, so isolation should be enforced at a harder-to-bypass layer like RLS or a centralized query helper"},
                {"id": "c", "text": "Shared-schema designs don't support tenant_id columns at all"},
                {"id": "d", "text": "PostgreSQL does not support row-level security"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Application-layer-only isolation is fragile precisely because it depends on every query author remembering a convention; centralizing enforcement (a query helper, or database-level Row-Level Security) provides a much stronger, harder-to-bypass guarantee.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "Why should an API credential (like a weather API key) never be passed as a tool argument the model can see or construct?",
            "options": [
                {"id": "a", "text": "Tool arguments are always logged in plaintext regardless of content"},
                {"id": "b", "text": "The credential could end up echoed into the model's context or output, and the tool's implementation should read it from server-side configuration instead"},
                {"id": "c", "text": "Models cannot process string arguments longer than a few characters"},
                {"id": "d", "text": "API keys must always be exactly 32 characters to work as tool arguments"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Building the authenticated request entirely inside the tool function, with the credential read from server-side config, ensures the credential is never visible to or constructible by the model.",
            "difficulty": "easy",
            "points": 1.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "multi_select",
            "prompt": "Which of the following are appropriate fallback strategies when an external API a tool depends on fails? Select all that apply.",
            "options": [
                {"id": "a", "text": "Serve cached/stale data with a clear 'as of' timestamp, if slightly outdated data is acceptable"},
                {"id": "b", "text": "Degrade gracefully by answering the parts of the question that don't depend on the failed source, and being explicit about what couldn't be checked"},
                {"id": "c", "text": "Surface the raw internal error message and hostname directly to the end user for transparency"},
                {"id": "d", "text": "Tell the user honestly, in plain non-technical language, that a specific capability is temporarily unavailable"},
            ],
            "correct_answer": {"choices": ["a", "b", "d"]},
            "explanation": "Stale-data fallback, graceful degradation, and honest plain-language failure messages are all appropriate. Surfacing raw internal error details (hostnames, stack traces) is a technical-detail leak that should never reach end users.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is a low similarity threshold risky for semantic LLM response caching?",
            "options": [
                {"id": "a", "text": "It makes the cache slower to query"},
                {"id": "b", "text": "It can confidently serve a cached answer to a query that's topically similar but meaningfully different in what it's actually asking, since the cache always returns the closest match above threshold"},
                {"id": "c", "text": "Low thresholds are not supported by vector databases"},
                {"id": "d", "text": "It disables exact-match caching entirely"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Unlike exact-match caching, a semantic cache can serve a confidently wrong answer if the threshold is too permissive, since embedding similarity doesn't guarantee the same answer genuinely applies.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "coding",
            "prompt": "Write a Python function `should_retry_task(exception, attempt, max_retries)` for a Celery-style task that returns True only if the exception is an instance of TransientError AND attempt < max_retries, and False otherwise (including for any other exception type).",
            "options": [],
            "correct_answer": {
                "expected_behavior": "Returns True only when isinstance(exception, TransientError) is True and attempt < max_retries; returns False for any other exception type or once max_retries is reached.",
                "sample_solution": "def should_retry_task(exception, attempt, max_retries):\n    return isinstance(exception, TransientError) and attempt < max_retries",
            },
            "explanation": "This encodes the principle from the queues module: only retry failures known to be transient, and only within a bounded retry budget — retrying a non-transient error (like a validation failure) wastes time on a request that will never succeed.",
            "difficulty": "medium",
            "points": 2.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "Why is using a raw `user_id` or `conversation_id` as a Prometheus metric label considered a serious anti-pattern?",
            "options": [
                {"id": "a", "text": "Prometheus does not allow string label values"},
                {"id": "b", "text": "Every unique label value combination creates a new time series, and unbounded identifiers can create millions of series, degrading or crashing the metrics backend (cardinality explosion)"},
                {"id": "c", "text": "user_id values are always considered PII and illegal to store anywhere"},
                {"id": "d", "text": "Labels can only contain numeric values"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "High-cardinality labels like user_id or conversation_id explode the number of tracked time series; such identifiers belong in logs and traces, while metric labels should stay to low-cardinality dimensions like specialist name or status.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "scenario",
            "prompt": "A service has a 99.5% success-rate SLO measured over 30 days. Over the last hour, the error rate has been 5% — twenty times the 0.5% error budget rate. The absolute number of failed requests this hour is small because traffic is currently low. Should this trigger an alert, and why?",
            "options": [],
            "correct_answer": {"expected": "Yes — this is a burn-rate alert situation: a burn rate of roughly 10-20x means the 30-day error budget would be exhausted in under two days at the current rate, which is a genuine risk to the SLO commitment even though the absolute failure count looks small right now due to low traffic. Burn-rate alerting is specifically designed to catch this kind of disproportionate-rate problem that a flat absolute-count threshold would miss."},
            "explanation": "Burn-rate alerting ties directly to whether the SLO commitment is actually at risk, catching problems that a flat threshold on absolute error counts could miss during low-traffic periods.",
            "difficulty": "hard",
            "points": 2.0,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "For a change that swaps the underlying LLM model version, why is canary deployment generally preferred over an immediate full blue-green cutover?",
            "options": [
                {"id": "a", "text": "Canary deployments are always cheaper to run than blue-green"},
                {"id": "b", "text": "Model swaps often cause subtle quality regressions rather than hard crashes, so limiting exposure to a small traffic percentage while monitoring quality metrics reduces blast radius on exactly the kind of regression that's easy to miss"},
                {"id": "c", "text": "Blue-green deployments cannot be used for any change involving a model version"},
                {"id": "d", "text": "Canary deployments do not require any traffic-splitting infrastructure"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Because model regressions are often subtle quality shifts rather than obvious failures, canary's gradual, metric-monitored rollout limits how many users are exposed to a regression before it's caught, compared to an all-at-once cutover.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "short_answer",
            "prompt": "In one or two sentences, explain the difference between rate limiting and load shedding, and describe a situation where a system would use both together.",
            "options": [],
            "correct_answer": {
                "expected": "Rate limiting controls how much any single caller can send, regardless of overall system load; load shedding deliberately refuses some requests when the system as a whole is overloaded, prioritizing which requests to keep serving. A system uses both together when, e.g., a caller within their normal rate limit still gets shed during a system-wide overload caused by many other callers combined.",
                "keywords": ["rate limiting", "per-caller", "load shedding", "system-wide", "overload"],
            },
            "explanation": "Rate limiting is a per-caller control independent of overall load; load shedding is a system-wide response to aggregate overload, and both can be necessary simultaneously since a caller can be well within their individual limit while the system overall is still overloaded by combined traffic.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
        {
            "question_type": "mcq",
            "prompt": "Under severe, sustained overload requiring load shedding, which prioritization approach best reflects the principles covered in this course?",
            "options": [
                {"id": "a", "text": "Shed requests randomly, since all requests are equally important"},
                {"id": "b", "text": "Prioritize paid customers over free tier, interactive requests over background batch work, and protect in-progress multi-step runs over brand-new requests, since abandoning in-progress work wastes resources already spent"},
                {"id": "c", "text": "Always shed the oldest requests first regardless of type"},
                {"id": "d", "text": "Shed all requests uniformly until the incident resolves itself"},
            ],
            "correct_answer": {"choice": "b"},
            "explanation": "Deliberate prioritization — by customer tier, by interactive-vs-batch, and by protecting sunk-cost in-progress work — produces a much better outcome under overload than random or uniform shedding.",
            "difficulty": "medium",
            "points": 1.5,
            "skill_slug": "production-ai",
        },
    ],
}
