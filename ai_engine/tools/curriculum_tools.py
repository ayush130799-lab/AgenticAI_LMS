"""Explicit, narrowly-scoped tools agents may use.

Per the product's AI-safety requirement, agent tools are explicit and
permissioned: each tool here operates ONLY on data the caller hands it
in-memory (a list/dict passed as an argument). No tool in this module
touches the filesystem, network, database, or executes code — an agent
wired up with these tools has no ambient access beyond what's explicitly
passed in.

Each function is a plain, directly-callable Python function (so agent
fallback/rule-based code can call it too) and is also exported wrapped with
LangChain's `@tool` so it can be bound to an LLM-backed agent/graph node.
"""

from __future__ import annotations

import re

from langchain_core.tools import tool

_WORD_RE = re.compile(r"[a-z0-9]+")


def search_curriculum(index: list[dict], query: str) -> list[dict]:
    """Keyword-search an in-memory curriculum index.

    `index`: a list of `{"title", "description", "id"}` items supplied by
    the caller (e.g. a flattened list of lessons/courses/projects).
    `query`: free-text search string.

    Returns the matching items (a subset of `index`, in original dict
    shape), ranked by number of keyword occurrences across title +
    description, highest first. Items with zero keyword matches are
    excluded. This function never fetches or looks up data on its own — it
    only searches the `index` it was given.
    """

    if not query or not index:
        return []

    keywords = [kw for kw in _WORD_RE.findall(query.lower()) if len(kw) > 1]
    if not keywords:
        return []

    scored: list[tuple[int, dict]] = []
    for item in index:
        if not isinstance(item, dict):
            continue
        haystack = f"{item.get('title', '')} {item.get('description', '')}".lower()
        score = sum(haystack.count(kw) for kw in keywords)
        if score > 0:
            scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [item for _, item in scored]


def get_skill_info(skills_index: dict, slug: str) -> dict | None:
    """Look up a skill's info by slug in an in-memory skills index.

    `skills_index`: a `{slug: {...skill fields...}}` dict supplied by the
    caller (e.g. built from the skill graph). `slug`: the skill slug to look
    up. Returns the skill dict, or `None` if `slug` isn't present. This
    function performs no lookup beyond the dict it was given (no DB/network).
    """

    if not skills_index or not slug:
        return None
    return skills_index.get(slug)


# LangChain-tool-wrapped versions, for binding into LLM-backed agents/graphs.
search_curriculum_tool = tool(search_curriculum)
get_skill_info_tool = tool(get_skill_info)
