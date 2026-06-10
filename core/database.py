"""SQLite — pacientes, consultas e estado dos agentes."""
import sqlite3
from datetime import datetime
from pathlib import Path

DB_PATH = Path.home() / ".clinica-ia" / "clinica.db"


def connect() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with connect() as conn:
        conn.executescript("""
        CREATE TABLE IF NOT EXISTS pacientes (
            phone       TEXT PRIMARY KEY,
            nome        TEXT,
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS consultas (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            data_hora   TEXT,
            especialidade TEXT,
            status      TEXT DEFAULT 'agendada',
            created_at  TEXT DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS historico (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            phone       TEXT NOT NULL,
            role        TEXT NOT NULL,
            content     TEXT NOT NULL,
            created_at  TEXT DEFAULT (datetime('now'))
        );
        """)


def upsert_paciente(phone: str, nome: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO pacientes (phone, nome) VALUES (?, ?) "
            "ON CONFLICT(phone) DO UPDATE SET nome=excluded.nome",
            (phone, nome),
        )


def get_historico(phone: str, limit: int = 10) -> list[dict]:
    with connect() as conn:
        rows = conn.execute(
            "SELECT role, content FROM historico WHERE phone=? "
            "ORDER BY id DESC LIMIT ?", (phone, limit)
        ).fetchall()
    return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]


def add_historico(phone: str, role: str, content: str) -> None:
    with connect() as conn:
        conn.execute(
            "INSERT INTO historico (phone, role, content) VALUES (?, ?, ?)",
            (phone, role, content),
        )


def get_proxima_consulta(phone: str) -> sqlite3.Row | None:
    with connect() as conn:
        return conn.execute(
            "SELECT * FROM consultas WHERE phone=? AND status='agendada' "
            "AND data_hora > datetime('now') ORDER BY data_hora LIMIT 1",
            (phone,),
        ).fetchone()


def get_faltosos(horas: int = 48) -> list[sqlite3.Row]:
    """Retorna pacientes que faltaram nas ultimas N horas."""
    with connect() as conn:
        return conn.execute(
            "SELECT c.*, p.nome FROM consultas c "
            "JOIN pacientes p ON c.phone = p.phone "
            "WHERE c.status='agendada' "
            "AND c.data_hora < datetime('now') "
            "AND c.data_hora > datetime('now', ? || ' hours')",
            (f"-{horas}",),
        ).fetchall()


def marcar_faltou(consulta_id: int) -> None:
    with connect() as conn:
        conn.execute(
            "UPDATE consultas SET status='faltou' WHERE id=?", (consulta_id,)
        )
