"""
Loads backend/data/skills.json and backend/data/courses.json into CognoDB.

Usage:
    python seed_data.py            # load data (idempotent, safe to re-run)
    python seed_data.py --reset    # wipe the graph first, then load

Reads connection details from environment variables (see .env.example).
"""

import argparse
import json
import sys
from pathlib import Path

import queries
from db import DatabaseUnavailableError

DATA_DIR = Path(__file__).parent / "data"


def load_json(name: str):
    with open(DATA_DIR / name, encoding="utf-8") as f:
        return json.load(f)


def seed(reset: bool = False):
    skills = load_json("skills.json")
    courses = load_json("courses.json")

    if reset:
        print("Clearing existing graph...")
        queries.clear_graph()

    print("Creating uniqueness constraints...")
    queries.create_constraints()

    print(f"Upserting {len(skills)} skills...")
    for skill in skills:
        queries.upsert_skill(skill)

    print("Linking skill prerequisites...")
    prereq_edges = 0
    for skill in skills:
        for prereq_id in skill.get("prerequisites", []):
            queries.link_prerequisite(skill["id"], prereq_id)
            prereq_edges += 1

    print(f"Upserting {len(courses)} courses...")
    for course in courses:
        queries.upsert_course(course)

    print("Linking course TEACHES / REQUIRES relationships...")
    teaches_edges = 0
    requires_edges = 0
    for course in courses:
        for skill_id in course.get("teaches", []):
            queries.link_course_teaches(course["id"], skill_id)
            teaches_edges += 1
        for skill_id in course.get("requires", []):
            queries.link_course_requires(course["id"], skill_id)
            requires_edges += 1

    print(
        f"Done. {len(skills)} skills, {len(courses)} courses, "
        f"{prereq_edges} PREREQUISITE_OF, {teaches_edges} TEACHES, "
        f"{requires_edges} REQUIRES edges."
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the Skilltree graph.")
    parser.add_argument(
        "--reset", action="store_true", help="Delete all nodes/edges first."
    )
    args = parser.parse_args()

    try:
        seed(reset=args.reset)
    except DatabaseUnavailableError as exc:
        print(f"\nCould not connect to CognoDB: {exc}", file=sys.stderr)
        print(
            "Check COGNODB_URI / COGNODB_USER / COGNODB_PASSWORD in your "
            "environment (see .env.example).",
            file=sys.stderr,
        )
        sys.exit(1)
