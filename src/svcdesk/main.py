# ai-generated: 95% - rebuilt to match the course contract and persisted ticket lifecycle

import os
import sqlite3
from datetime import datetime, time, timedelta, timezone
from json import JSONDecodeError
from uuid import uuid4
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field
from starlette.exceptions import HTTPException as StarletteHTTPException

from svcdesk.dora import calculate_metrics

app = FastAPI(title="svcdesk")

TZ = ZoneInfo("Europe/Warsaw")
DB_PATH = os.environ.get("SVCDESK_DB", "/data/svcdesk.db")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def parse_rfc3339(value: str) -> datetime:
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        raise ValueError("timestamp is missing timezone information")
    return dt.astimezone(timezone.utc)


def request_now(request: Request) -> datetime:
    env_value = os.getenv("SVCDESK_TEST_CLOCK", "1").strip().lower()
    header_value = request.headers.get("X-Test-Clock")

    if header_value is not None and env_value not in {"0", "false"}:
        try:
            return parse_rfc3339(header_value)
        except ValueError as exc:
            raise HTTPException(
                status_code=400,
                detail={"error": {"code": "validation", "message": "invalid X-Test-Clock"}},
            ) from exc

    return utc_now()


def json_error(code: str, message: str, status_code: int):
    return HTTPException(status_code=status_code, detail={"error": {"code": code, "message": message}})


def init_db() -> None:
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tickets (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                reporter_name TEXT NOT NULL,
                reporter_email TEXT,
                reporter_vip INTEGER NOT NULL DEFAULT 0,
                impact INTEGER NOT NULL,
                urgency INTEGER NOT NULL,
                priority TEXT NOT NULL,
                state TEXT NOT NULL,
                created_at TEXT NOT NULL,
                acknowledged_at TEXT,
                resolved_at TEXT,
                closed_at TEXT,
                related_to TEXT,
                ack_due_at TEXT NOT NULL,
                resolve_due_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


class Reporter(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    name: str = Field(..., min_length=1, max_length=100)
    email: str | None = None
    vip: bool = False


class TicketCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="ignore")

    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(default="", max_length=4000)
    reporter: Reporter
    impact: int = Field(..., ge=1, le=3)
    urgency: int = Field(..., ge=1, le=3)
    related_to: str | None = None


class TicketResponse(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="ignore",
        json_encoders={datetime: lambda value: value.astimezone(timezone.utc).isoformat()},
    )

    id: str
    title: str
    description: str
    reporter: Reporter
    impact: int
    urgency: int
    priority: str
    state: str
    created_at: datetime
    acknowledged_at: datetime | None = None
    resolved_at: datetime | None = None
    closed_at: datetime | None = None
    related_to: str | None = None
    sla: dict[str, datetime]


def compute_priority(impact: int, urgency: int, vip: bool) -> str:
    matrix = {
        1: {1: "P1", 2: "P2", 3: "P3"},
        2: {1: "P2", 2: "P3", 3: "P4"},
        3: {1: "P3", 2: "P4", 3: "P4"},
    }
    priority = matrix[impact][urgency]
    if vip and priority in {"P3", "P4"}:
        return "P2"
    return priority


def next_business_open(local_dt: datetime) -> datetime:
    local = local_dt.astimezone(TZ)
    cursor = local.date()
    if local.weekday() < 5 and local.time() < time(8, 0):
        return datetime.combine(cursor, time(8, 0), tzinfo=TZ)

    cursor += timedelta(days=1)
    while cursor.weekday() >= 5:
        cursor += timedelta(days=1)
    return datetime.combine(cursor, time(8, 0), tzinfo=TZ)


def normalize_business_cursor(local_dt: datetime) -> datetime:
    if local_dt.weekday() >= 5:
        return next_business_open(local_dt)
    if local_dt.time() < time(8, 0):
        return local_dt.replace(hour=8, minute=0, second=0, microsecond=0)
    if local_dt.time() >= time(16, 0):
        return next_business_open(local_dt)
    return local_dt

def compute_business_due(created_at_utc: datetime, duration: timedelta) -> datetime:
    cursor = normalize_business_cursor(created_at_utc.astimezone(TZ))
    remaining = duration
    while remaining > timedelta(0):
        if cursor.weekday() >= 5:
            cursor = next_business_open(cursor)
            continue
        if cursor.time() < time(8, 0):
            cursor = cursor.replace(hour=8, minute=0, second=0, microsecond=0)
            continue
        if cursor.time() >= time(16, 0):
            cursor = next_business_open(cursor)
            continue

        window_end = cursor.replace(hour=16, minute=0, second=0, microsecond=0)
        window_remaining = window_end - cursor
        if remaining < window_remaining:
            result = cursor + remaining
            return result.astimezone(timezone.utc)
        if remaining == window_remaining:
            return window_end.astimezone(timezone.utc)

        remaining -= window_remaining
        cursor = next_business_open(window_end)

    return cursor.astimezone(timezone.utc)


def uses_business_clock(priority: str) -> bool:
    return priority != "P1"


def compute_sla(created_at_utc: datetime, priority: str) -> dict[str, datetime]:
    due = {
        "P1": {"ack": timedelta(minutes=15), "resolve": timedelta(hours=4)},
        "P2": {"ack": timedelta(hours=1), "resolve": timedelta(hours=8)},
        "P3": {"ack": timedelta(hours=4), "resolve": timedelta(hours=24)},
        "P4": {"ack": timedelta(hours=8), "resolve": timedelta(hours=72)},
    }
    if uses_business_clock(priority):
        return {
            "ack_due_at": compute_business_due(created_at_utc, due[priority]["ack"]),
            "resolve_due_at": compute_business_due(created_at_utc, due[priority]["resolve"]),
        }
    return {
        "ack_due_at": created_at_utc + due[priority]["ack"],
        "resolve_due_at": created_at_utc + due[priority]["resolve"],
    }


def row_to_ticket(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "description": row["description"],
        "reporter": {
            "name": row["reporter_name"],
            "email": row["reporter_email"],
            "vip": bool(row["reporter_vip"]),
        },
        "impact": row["impact"],
        "urgency": row["urgency"],
        "priority": row["priority"],
        "state": row["state"],
        "created_at": parse_rfc3339(row["created_at"]),
        "acknowledged_at": parse_rfc3339(row["acknowledged_at"]) if row["acknowledged_at"] else None,
        "resolved_at": parse_rfc3339(row["resolved_at"]) if row["resolved_at"] else None,
        "closed_at": parse_rfc3339(row["closed_at"]) if row["closed_at"] else None,
        "related_to": row["related_to"],
        "sla": {
            "ack_due_at": parse_rfc3339(row["ack_due_at"]),
            "resolve_due_at": parse_rfc3339(row["resolve_due_at"]),
        },
    }


def fetch_ticket(ticket_id: str) -> dict:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        row = conn.execute("SELECT * FROM tickets WHERE id = ?", (ticket_id,)).fetchone()
    if row is None:
        raise KeyError(ticket_id)
    return row_to_ticket(row)


def list_tickets(state: str | None = None, priority: str | None = None) -> list[dict]:
    query = "SELECT * FROM tickets WHERE 1=1"
    params: list[str] = []
    if state is not None:
        query += " AND state = ?"
        params.append(state.lower())
    if priority is not None:
        query += " AND priority = ?"
        params.append(priority.upper())
    query += " ORDER BY created_at ASC"
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(query, params).fetchall()
    return [row_to_ticket(row) for row in rows]


def insert_ticket(payload: TicketCreate, now: datetime) -> dict:
    ticket_id = str(uuid4())
    priority = compute_priority(payload.impact, payload.urgency, bool(payload.reporter.vip))
    sla = compute_sla(now, priority)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """
            INSERT INTO tickets (
                id, title, description, reporter_name, reporter_email, reporter_vip,
                impact, urgency, priority, state, created_at,
                acknowledged_at, resolved_at, closed_at, related_to,
                ack_due_at, resolve_due_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                payload.title,
                payload.description,
                payload.reporter.name,
                payload.reporter.email,
                int(bool(payload.reporter.vip)),
                payload.impact,
                payload.urgency,
                priority,
                "new",
                now.isoformat().replace("+00:00", "Z"),
                None,
                None,
                None,
                payload.related_to,
                sla["ack_due_at"].isoformat().replace("+00:00", "Z"),
                sla["resolve_due_at"].isoformat().replace("+00:00", "Z"),
            ),
        )
        conn.commit()
    return fetch_ticket(ticket_id)


def apply_transition(ticket_id: str, action: str, now: datetime) -> dict:
    ticket = fetch_ticket(ticket_id)
    state = ticket["state"]
    if action == "ack":
        if state != "new":
            raise json_error("invalid_transition", "ticket cannot be acknowledged from this state", 409)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE tickets SET state = ?, acknowledged_at = ? WHERE id = ?",
                ("acknowledged", now.isoformat().replace("+00:00", "Z"), ticket_id),
            )
            conn.commit()
        return fetch_ticket(ticket_id)
    if action == "start":
        if state != "acknowledged":
            raise json_error("invalid_transition", "ticket cannot be started from this state", 409)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("UPDATE tickets SET state = ? WHERE id = ?", ("in_progress", ticket_id))
            conn.commit()
        return fetch_ticket(ticket_id)
    if action == "resolve":
        if state != "in_progress":
            raise json_error("invalid_transition", "ticket cannot be resolved from this state", 409)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE tickets SET state = ?, resolved_at = ? WHERE id = ?",
                ("resolved", now.isoformat().replace("+00:00", "Z"), ticket_id),
            )
            conn.commit()
        return fetch_ticket(ticket_id)
    if action == "close":
        if state != "resolved":
            raise json_error("invalid_transition", "ticket cannot be closed from this state", 409)
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute(
                "UPDATE tickets SET state = ?, closed_at = ? WHERE id = ?",
                ("closed", now.isoformat().replace("+00:00", "Z"), ticket_id),
            )
            conn.commit()
        return fetch_ticket(ticket_id)
    if action == "reopen":
        if state == "resolved":
            resolved_at = ticket["resolved_at"]
            if now > resolved_at + timedelta(days=7):
                raise json_error("reopen_window_expired", "ticket cannot be reopened outside the 7-day window", 409)
            with sqlite3.connect(DB_PATH) as conn:
                conn.execute(
                    "UPDATE tickets SET state = ?, resolved_at = NULL, closed_at = NULL WHERE id = ?",
                    ("in_progress", ticket_id),
                )
                conn.commit()
            return fetch_ticket(ticket_id)
        if state == "closed":
            raise json_error("invalid_transition", "closed tickets are immutable", 409)
        raise json_error("invalid_transition", "ticket cannot be reopened from this state", 409)
    raise json_error("invalid_transition", "unsupported action", 409)


def is_business_hours(now_utc: datetime) -> bool:
    local = now_utc.astimezone(TZ)
    return local.weekday() < 5 and time(8, 0) <= local.timetz() < time(16, 0)


def ticket_paused(ticket: dict, now_utc: datetime) -> bool:
    if ticket["state"] in {"resolved", "closed"}:
        return False
    if ticket["priority"] == "P1":
        return False
    return not is_business_hours(now_utc)


def ticket_breach(ticket: dict, field: str, now_utc: datetime) -> bool:
    if field == "ack":
        ack_due = ticket["sla"]["ack_due_at"]
        if ticket["acknowledged_at"] is None:
            return now_utc > ack_due
        return ticket["acknowledged_at"] > ack_due
    if field == "resolve":
        resolve_due = ticket["sla"]["resolve_due_at"]
        if ticket["resolved_at"] is None:
            return now_utc > resolve_due
        return ticket["resolved_at"] > resolve_due
    return False


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    detail = exc.errors()[0] if exc.errors() else {}
    message = detail.get("msg") or "validation error"
    return JSONResponse(status_code=422, content={"error": {"code": "validation", "message": message}})


@app.exception_handler(StarletteHTTPException)
async def starlette_http_exception_handler(_request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    if exc.status_code == 404:
        return JSONResponse(status_code=404, content={"error": {"code": "not_found", "message": "not found"}})
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "http_error", "message": str(detail)}})


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        return JSONResponse(status_code=exc.status_code, content=detail)
    return JSONResponse(status_code=exc.status_code, content={"error": {"code": "error", "message": str(detail)}})


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "service": "svcdesk"}


@app.post("/dora/metrics")
async def dora_metrics(request: Request) -> dict[str, object]:
    try:
        payload = await request.json()
    except (JSONDecodeError, UnicodeDecodeError) as exc:
        raise json_error("validation", "request body must be valid JSON", 400) from exc
    try:
        return calculate_metrics(payload)
    except ValueError as exc:
        raise json_error("validation", str(exc), 422) from exc


@app.get("/dora/ticket-events")
def dora_ticket_events() -> list[dict[str, str]]:
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            """
            SELECT id, priority, state, created_at, acknowledged_at, resolved_at, closed_at
            FROM tickets
            """
        ).fetchall()

    phases = (
        ("created", "created_at", "new"),
        ("acknowledged", "acknowledged_at", "acknowledged"),
        ("resolved", "resolved_at", "resolved"),
        ("closed", "closed_at", "closed"),
    )
    ordered: list[tuple[datetime, str, dict[str, str]]] = []
    for row in rows:
        for phase, timestamp_column, state in phases:
            timestamp = row[timestamp_column]
            if timestamp is None:
                continue
            at = parse_rfc3339(timestamp)
            ordered.append(
                (
                    at,
                    row["id"],
                    {
                        "ticket_id": row["id"],
                        "at": at.isoformat().replace("+00:00", "Z"),
                        "phase": phase,
                        "priority": row["priority"],
                        "state": state,
                    },
                )
            )

    ordered.sort(key=lambda item: (item[0], item[1]))
    return [event for _, _, event in ordered]


@app.post("/tickets", response_model=TicketResponse, status_code=201)
def create_ticket(request: Request, payload: TicketCreate):
    now = request_now(request)
    ticket = insert_ticket(payload, now)
    return ticket


@app.get("/tickets", response_model=list[TicketResponse])
def list_tickets_endpoint(
    state: str | None = Query(default=None),
    priority: str | None = Query(default=None),
):
    return list_tickets(state=state, priority=priority)


@app.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(ticket_id: str):
    try:
        return fetch_ticket(ticket_id)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


@app.get("/tickets/{ticket_id}/sla")
def get_sla(ticket_id: str, request: Request):
    ticket = fetch_ticket(ticket_id)
    now = request_now(request)
    return {
        "priority": ticket["priority"],
        "ack_due_at": ticket["sla"]["ack_due_at"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "resolve_due_at": ticket["sla"]["resolve_due_at"].astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "ack_breached": ticket_breach(ticket, "ack", now),
        "resolve_breached": ticket_breach(ticket, "resolve", now),
        "paused": ticket_paused(ticket, now),
    }


@app.post("/tickets/{ticket_id}/ack")
def ack_ticket(ticket_id: str, request: Request):
    now = request_now(request)
    try:
        return apply_transition(ticket_id, "ack", now)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


@app.post("/tickets/{ticket_id}/start")
def start_ticket(ticket_id: str, request: Request):
    now = request_now(request)
    try:
        return apply_transition(ticket_id, "start", now)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


@app.post("/tickets/{ticket_id}/resolve")
def resolve_ticket(ticket_id: str, request: Request):
    now = request_now(request)
    try:
        return apply_transition(ticket_id, "resolve", now)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


@app.post("/tickets/{ticket_id}/close")
def close_ticket(ticket_id: str, request: Request):
    now = request_now(request)
    try:
        return apply_transition(ticket_id, "close", now)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


@app.post("/tickets/{ticket_id}/reopen")
def reopen_ticket(ticket_id: str, request: Request):
    now = request_now(request)
    try:
        return apply_transition(ticket_id, "reopen", now)
    except KeyError as exc:
        raise json_error("not_found", "ticket not found", 404) from exc


init_db()
