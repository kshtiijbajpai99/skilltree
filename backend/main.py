import logging
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import queries
from db import DatabaseUnavailableError, close_driver
from pathing import build_learning_path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("skilltree.api")

app = FastAPI(title="Skilltree API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.exception_handler(DatabaseUnavailableError)
async def db_unavailable_handler(request, exc: DatabaseUnavailableError):
    logger.error("Database unavailable: %s", exc)
    return JSONResponse(
        status_code=503,
        content={
            "error": "database_unavailable",
            "message": (
                "Skilltree can't reach the graph database right now. "
                "If you're running this locally, check that CognoDB is "
                "reachable and your .env credentials are correct."
            ),
        },
    )


def _split_ids(raw: Optional[str]) -> list[str]:
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


@app.get("/api/health")
def health():
    try:
        result = queries.get_health_counts()
        counts = result[0] if result else {"skills": 0, "courses": 0}
        return {"status": "ok", **counts}
    except DatabaseUnavailableError:
        raise
    except Exception as exc:  # noqa: BLE001 - surface as a clean 503
        raise DatabaseUnavailableError(str(exc)) from exc


@app.get("/api/skills")
def skills():
    return queries.list_skills()


@app.get("/api/graph")
def graph():
    return queries.get_full_skill_graph()


@app.get("/api/skill/{skill_id}")
def skill_detail(skill_id: str):
    rows = queries.get_skill_detail(skill_id)
    if not rows:
        raise HTTPException(status_code=404, detail="Skill not found")
    row = rows[0]
    row["prerequisites"] = [p for p in row["prerequisites"] if p.get("id")]
    row["unlocks"] = [u for u in row["unlocks"] if u.get("id")]
    row["courses"] = [c for c in row["courses"] if c.get("id")]
    return row


@app.get("/api/skill/{skill_id}/chain")
def skill_chain(skill_id: str):
    return queries.get_prerequisite_chain(skill_id)


@app.get("/api/next")
def next_skills(known: Optional[str] = Query(default="")):
    known_ids = _split_ids(known)
    return queries.get_frontier_skills(known_ids)


@app.get("/api/path")
def learning_path(
    known: Optional[str] = Query(default=""),
    target: str = Query(...),
):
    known_ids = _split_ids(known)
    subgraph = queries.get_missing_prereq_subgraph(known_ids, target)
    try:
        ordered = build_learning_path(subgraph["nodes"], subgraph["edges"])
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    steps = []
    for skill in ordered:
        course_rows = queries.get_best_course_for_skill(skill["id"], known_ids)
        course = course_rows[0] if course_rows else None
        steps.append({"skill": skill, "course": course})

    return {"target": target, "already_known": target in known_ids, "steps": steps}


@app.get("/api/common-ancestors")
def common_ancestors(a: str, b: str):
    return queries.get_common_ancestors(a, b)


@app.on_event("shutdown")
def shutdown():
    close_driver()


# --- Serve the frontend (single deployable service) -----------------------
FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
if FRONTEND_DIR.exists():
    app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
