"""
All Cypher lives here, as parameterized queries called through db.run_query.
No string concatenation of user input into Cypher anywhere in this file.
"""

from db import run_query, run_write


# ---------------------------------------------------------------------------
# Seeding (write queries)
# ---------------------------------------------------------------------------

def clear_graph():
    run_write("MATCH (n) DETACH DELETE n")


def create_constraints():
    run_write(
        "CREATE CONSTRAINT skill_id_unique IF NOT EXISTS "
        "FOR (s:Skill) REQUIRE s.id IS UNIQUE"
    )
    run_write(
        "CREATE CONSTRAINT course_id_unique IF NOT EXISTS "
        "FOR (c:Course) REQUIRE c.id IS UNIQUE"
    )


def upsert_skill(skill: dict):
    run_write(
        """
        MERGE (s:Skill {id: $id})
        SET s.name = $name,
            s.category = $category,
            s.description = $description
        """,
        {
            "id": skill["id"],
            "name": skill["name"],
            "category": skill["category"],
            "description": skill["description"],
        },
    )


def link_prerequisite(skill_id: str, prereq_id: str):
    run_write(
        """
        MATCH (prereq:Skill {id: $prereq_id})
        MATCH (skill:Skill {id: $skill_id})
        MERGE (prereq)-[:PREREQUISITE_OF]->(skill)
        """,
        {"prereq_id": prereq_id, "skill_id": skill_id},
    )


def upsert_course(course: dict):
    run_write(
        """
        MERGE (c:Course {id: $id})
        SET c.title = $title,
            c.provider = $provider,
            c.level = $level,
            c.duration_hours = $duration_hours,
            c.description = $description
        """,
        {
            "id": course["id"],
            "title": course["title"],
            "provider": course["provider"],
            "level": course["level"],
            "duration_hours": course["duration_hours"],
            "description": course["description"],
        },
    )


def link_course_teaches(course_id: str, skill_id: str):
    run_write(
        """
        MATCH (c:Course {id: $course_id})
        MATCH (s:Skill {id: $skill_id})
        MERGE (c)-[:TEACHES]->(s)
        """,
        {"course_id": course_id, "skill_id": skill_id},
    )


def link_course_requires(course_id: str, skill_id: str):
    run_write(
        """
        MATCH (c:Course {id: $course_id})
        MATCH (s:Skill {id: $skill_id})
        MERGE (c)-[:REQUIRES]->(s)
        """,
        {"course_id": course_id, "skill_id": skill_id},
    )


# ---------------------------------------------------------------------------
# Reads (API-facing queries)
# ---------------------------------------------------------------------------

def get_health_counts():
    """Cheap connectivity + sanity check used by /api/health."""
    return run_query(
        "MATCH (s:Skill) WITH count(s) AS skills "
        "MATCH (c:Course) RETURN skills, count(c) AS courses"
    )


def get_full_skill_graph():
    """All skills and the PREREQUISITE_OF edges between them, for the
    interactive graph view."""
    return run_query(
        """
        MATCH (s:Skill)
        OPTIONAL MATCH (s)-[:PREREQUISITE_OF]->(dep:Skill)
        RETURN s.id AS id, s.name AS name, s.category AS category,
               s.description AS description,
               collect(DISTINCT dep.id) AS unlocks
        """
    )


def list_skills():
    return run_query(
        "MATCH (s:Skill) RETURN s.id AS id, s.name AS name, "
        "s.category AS category ORDER BY s.category, s.name"
    )


def get_skill_detail(skill_id: str):
    """Direct prerequisites, direct dependents, and courses that teach this
    skill — a single-hop neighborhood view for the detail panel."""
    return run_query(
        """
        MATCH (s:Skill {id: $skill_id})
        OPTIONAL MATCH (pre:Skill)-[:PREREQUISITE_OF]->(s)
        OPTIONAL MATCH (s)-[:PREREQUISITE_OF]->(post:Skill)
        OPTIONAL MATCH (c:Course)-[:TEACHES]->(s)
        RETURN s.id AS id, s.name AS name, s.category AS category,
               s.description AS description,
               collect(DISTINCT {id: pre.id, name: pre.name}) AS prerequisites,
               collect(DISTINCT {id: post.id, name: post.name}) AS unlocks,
               collect(DISTINCT {id: c.id, title: c.title, provider: c.provider}) AS courses
        """,
        {"skill_id": skill_id},
    )


def get_prerequisite_chain(skill_id: str):
    """Full multi-hop ancestor chain for a target skill: every skill that
    must eventually be learned before this one, at any depth."""
    return run_query(
        """
        MATCH (target:Skill {id: $skill_id})
        MATCH path = (ancestor:Skill)-[:PREREQUISITE_OF*1..8]->(target)
        WITH ancestor, min(length(path)) AS depth
        RETURN ancestor.id AS id, ancestor.name AS name,
               ancestor.category AS category, depth
        ORDER BY depth
        """,
        {"skill_id": skill_id},
    )


def get_frontier_skills(known_ids: list[str]):
    """'What can I learn next': skills the learner doesn't know yet, where
    every direct prerequisite is already known. This is a graph-native
    pattern — an anti-join across a variable number of relationships per
    node — that a relational schema would need a correlated subquery (or a
    join fanned out per candidate) to express."""
    return run_query(
        """
        MATCH (s:Skill)
        WHERE NOT s.id IN $known
          AND NOT EXISTS {
                MATCH (p:Skill)-[:PREREQUISITE_OF]->(s)
                WHERE NOT p.id IN $known
              }
        OPTIONAL MATCH (c:Course)-[:TEACHES]->(s)
        RETURN s.id AS id, s.name AS name, s.category AS category,
               s.description AS description,
               collect(DISTINCT {id: c.id, title: c.title})[0..3] AS courses
        ORDER BY s.category, s.name
        """,
        {"known": known_ids},
    )


def get_missing_prereq_subgraph(known_ids: list[str], target_id: str):
    """All skills still needed to reach `target_id`, plus the
    PREREQUISITE_OF edges between exactly those skills. The app topologically
    sorts this subgraph in Python to produce an ordered learning path. Finding
    this variable-depth 'still missing' set is the multi-hop traversal a
    relational schema would need a recursive CTE (and still awkward set
    subtraction) to reproduce."""
    nodes = run_query(
        """
        MATCH (target:Skill {id: $target_id})
        OPTIONAL MATCH (anc:Skill)-[:PREREQUISITE_OF*1..8]->(target)
        WITH target, collect(DISTINCT anc) AS ancestors
        WITH [n IN ancestors WHERE n IS NOT NULL AND NOT n.id IN $known] +
             (CASE WHEN target.id IN $known THEN [] ELSE [target] END) AS missing
        UNWIND missing AS m
        RETURN DISTINCT m.id AS id, m.name AS name, m.category AS category
        """,
        {"target_id": target_id, "known": known_ids},
    )
    node_ids = [n["id"] for n in nodes]
    if not node_ids:
        return {"nodes": nodes, "edges": []}
    edges = run_query(
        """
        MATCH (a:Skill)-[:PREREQUISITE_OF]->(b:Skill)
        WHERE a.id IN $node_ids AND b.id IN $node_ids
        RETURN a.id AS source, b.id AS target
        """,
        {"node_ids": node_ids},
    )
    return {"nodes": nodes, "edges": edges}


def get_best_course_for_skill(skill_id: str, known_ids: list[str]):
    """Prefer a course whose own REQUIRES set is already fully satisfied by
    known skills; fall back to any course that teaches the skill."""
    return run_query(
        """
        MATCH (c:Course)-[:TEACHES]->(s:Skill {id: $skill_id})
        OPTIONAL MATCH (c)-[:REQUIRES]->(req:Skill)
        WITH c, collect(req.id) AS reqs
        RETURN c.id AS id, c.title AS title, c.provider AS provider,
               c.level AS level, c.duration_hours AS duration_hours,
               reqs,
               ALL(r IN reqs WHERE r IN $known) AS ready
        ORDER BY ready DESC, c.duration_hours ASC
        LIMIT 1
        """,
        {"skill_id": skill_id, "known": known_ids},
    )


def get_common_ancestors(skill_id_a: str, skill_id_b: str):
    """Skills that are prerequisites (at any depth) of BOTH target skills —
    useful for 'what should I learn if I might go either direction'. A
    set-intersection over two variable-length traversals: natural in Cypher,
    painful as a self-joined recursive query in SQL."""
    return run_query(
        """
        MATCH (a:Skill {id: $a})
        MATCH (b:Skill {id: $b})
        MATCH (ancA:Skill)-[:PREREQUISITE_OF*1..8]->(a)
        WITH b, collect(DISTINCT ancA) AS ancestorsA
        MATCH (ancB:Skill)-[:PREREQUISITE_OF*1..8]->(b)
        WITH ancestorsA, collect(DISTINCT ancB) AS ancestorsB
        UNWIND ancestorsA AS x
        WITH x, ancestorsB
        WHERE x IN ancestorsB
        RETURN DISTINCT x.id AS id, x.name AS name, x.category AS category
        """,
        {"a": skill_id_a, "b": skill_id_b},
    )
