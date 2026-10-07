async def test_tutor_chat_grounds_in_lesson_content(client, seeded_rag_chunk, auth_headers):
    resp = await client.post("/api/tutor/chat", json={
        "message": "What is Test Skill?", "lesson_id": str(seeded_rag_chunk["lesson_id"]),
    }, headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["reply"]
    assert "conversation_id" in body


async def test_tutor_chat_continues_conversation(client, seeded_rag_chunk, auth_headers):
    resp = await client.post("/api/tutor/chat", json={"message": "Explain Test Skill."}, headers=auth_headers)
    conversation_id = resp.json()["conversation_id"]

    resp = await client.post("/api/tutor/chat", json={
        "message": "Can you give an example?", "conversation_id": conversation_id,
    }, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["conversation_id"] == conversation_id

    resp = await client.get(f"/api/tutor/conversations/{conversation_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert len(resp.json()["messages"]) == 4  # 2 user + 2 assistant


async def test_tutor_requires_auth(client):
    resp = await client.post("/api/tutor/chat", json={"message": "hello"})
    assert resp.status_code == 401


async def test_retriever_ranks_the_lesson_that_matches_the_topic_first(client):
    """Hybrid retrieval must surface the topical chunk for a keyword question, not just a vaguely similar one."""
    from app.db.session import AsyncSessionLocal
    from app.models.rag import DocumentChunk

    from ai_engine.rag.embedder import embed_text
    from ai_engine.rag.retriever import retrieve_relevant_chunks

    topical = "Chunking splits long documents into smaller passages so each passage can be embedded and retrieved on its own."
    unrelated = "Gradient descent iteratively adjusts model weights to minimise a loss function during training."
    async with AsyncSessionLocal() as db:
        db.add_all([
            DocumentChunk(source_type="test", title="Text Chunking Basics", chunk_index=0, content=topical, embedding=embed_text(topical)),
            DocumentChunk(source_type="test", title="Optimisation Basics", chunk_index=0, content=unrelated, embedding=embed_text(unrelated)),
        ])
        await db.commit()

        results = await retrieve_relevant_chunks(db, "What is chunking and why does it matter?", k=3)

    assert results and results[0]["title"] == "Text Chunking Basics"
    assert all(0.0 <= r["score"] <= 1.0 for r in results)
