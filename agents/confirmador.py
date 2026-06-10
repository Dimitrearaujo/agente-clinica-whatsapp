"""Agente confirmador de vespera — envia lembrete e confirma presenca."""
from core import database as db, whatsapp as wa
from datetime import datetime, timedelta


def _formatar_data(data_hora: str) -> str:
    try:
        dt = datetime.fromisoformat(data_hora)
        return dt.strftime("%d/%m as %H:%M")
    except Exception:
        return data_hora


def confirmar_amanha() -> int:
    """Envia confirmacoes para consultas de amanha. Retorna qtd enviada."""
    amanha = (datetime.now() + timedelta(days=1)).date()
    enviados = 0
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT c.*, p.nome FROM consultas c "
            "JOIN pacientes p ON c.phone = p.phone "
            "WHERE c.status='agendada' "
            "AND date(c.data_hora) = ?",
            (str(amanha),),
        ).fetchall()

    for row in rows:
        data_fmt = _formatar_data(row["data_hora"])
        msg = (
            f"Ola {row['nome']}! Lembramos que voce tem consulta amanha "
            f"{data_fmt}. Confirma sua presenca? Responda *SIM* ou *NAO*."
        )
        if wa.send_text(row["phone"], msg):
            enviados += 1
    return enviados


def processar_resposta(phone: str, message: str) -> None:
    """Processa SIM/NAO do paciente apos lembrete."""
    msg_lower = message.strip().lower()
    if "sim" in msg_lower or "confirmo" in msg_lower:
        wa.send_text(phone, "Otimo! Consulta confirmada. Te esperamos amanha.")
    elif "nao" in msg_lower or "nao" in msg_lower or "cancelar" in msg_lower:
        wa.send_text(
            phone,
            "Entendido! Vamos cancelar. Quer reagendar para outra data?",
        )
        with db.connect() as conn:
            conn.execute(
                "UPDATE consultas SET status='cancelada' "
                "WHERE phone=? AND status='agendada' "
                "AND date(data_hora) > date('now')",
                (phone,),
            )
