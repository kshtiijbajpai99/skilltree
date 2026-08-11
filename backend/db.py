"""
Connection handling for CognoDB (openCypher over Bolt), via the official
Neo4j Python driver. Credentials are read from environment variables only —
never hardcoded and never committed.
"""

import os
import logging
from contextlib import contextmanager

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError, Neo4jError
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("skilltree.db")

COGNODB_URI = os.environ.get("COGNODB_URI")
COGNODB_USER = os.environ.get("COGNODB_USER", "cognodb")
COGNODB_PASSWORD = os.environ.get("COGNODB_PASSWORD")

_driver = None


class DatabaseUnavailableError(Exception):
    """Raised when the graph database cannot be reached or auth fails."""


def get_driver():
    """Lazily create a single shared driver instance for the app's lifetime."""
    global _driver
    if _driver is None:
        if not COGNODB_URI or not COGNODB_PASSWORD:
            raise DatabaseUnavailableError(
                "COGNODB_URI and COGNODB_PASSWORD must be set as environment "
                "variables. See .env.example."
            )
        try:
            _driver = GraphDatabase.driver(
                COGNODB_URI, auth=(COGNODB_USER, COGNODB_PASSWORD)
            )
            _driver.verify_connectivity()
        except AuthError as exc:
            _driver = None
            raise DatabaseUnavailableError(
                "Authentication with CognoDB failed. Check COGNODB_USER / "
                "COGNODB_PASSWORD."
            ) from exc
        except ServiceUnavailable as exc:
            _driver = None
            raise DatabaseUnavailableError(
                "Could not reach CognoDB at the configured URI. Check "
                "COGNODB_URI and that the instance is running."
            ) from exc
    return _driver


def close_driver():
    global _driver
    if _driver is not None:
        _driver.close()
        _driver = None


@contextmanager
def get_session():
    """Yield a Neo4j session, translating connection errors into a single
    application-level exception the API layer can turn into a clean 503."""
    driver = get_driver()
    session = driver.session()
    try:
        yield session
    except (ServiceUnavailable, AuthError) as exc:
        raise DatabaseUnavailableError(str(exc)) from exc
    except Neo4jError as exc:
        logger.error("Cypher query failed: %s", exc)
        raise
    finally:
        session.close()


def run_query(query: str, parameters: dict | None = None):
    """Run a single parameterized Cypher query and return a list of records
    as plain dicts. Always parameterized — never string-concatenated."""
    with get_session() as session:
        result = session.run(query, parameters or {})
        return [record.data() for record in result]


def run_write(query: str, parameters: dict | None = None):
    with get_session() as session:
        result = session.run(query, parameters or {})
        summary = result.consume()
        return summary
