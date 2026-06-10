"""Agente de retorno e avaliacao Google — coleta NPS e pede review."""
from core import database as db, whatsapp as wa
from datetime import datetime, timedelta

GOOGLE_REVIEW_URL = "https://g.page/r/COLE_SEU_LINK_AQUI"


def solicitar_avaliacao(horas_pos_consulta: int = 2) -> int:
    """Solicita avaliacao para consultas realizadas N horas atras."""
    limite = (datetime.now() - timedelta(hours=horas_pos_consulta)).isoformat()
    with db.connect() as conn:
        rows = conn.execute(
            "SELECT c.*, p.nome FROM consultas c "
            "JOIN pacientes p ON c.phone = p.phone "
            "WHERE c.status='realizada' "
            "AND c.data_hora BETWEEN datetime('now', ? || ' hours') AND ?",
            (f"-{horas_pos_consulta + 1}", limite),
        ).fetchall()

    enviados = 0
    for row in rows:
        msg = (
            f"Ola {row['nome']}! Esperamos que tenha gostado do atendimento. "
            "Poderia nos avaliar no Google? Leva menos de 1 minuto e ajuda muito! "
            f"{GOOGLE_REVIEW_URL}"
        )
        if wa.send_text(row["phone"], msg):
            enviados += 1
            with db.connect() as conn:
                conn.execute(
                    "UPDATE consultas SET status='avaliado' WHERE id=?", (row["id"],)
                )
    return enviados


def processar_nps(phone: str, nota: int) -> None:
    """Registra nota NPS e responde adequadamente."""
    if nota >= 9:
        wa.send_text(
            phone,
            f"Que otimo! Fico feliz que tenha gostado. "
            f"Sua avaliacao e muito importante para nos: {GOOGLE_REVIEW_URL}",
        )
    elif nota >= 7:
        wa.send_text(phone, "Obrigado pelo feedback! O que podemos melhorar?")
    else:
        wa.send_text(
            phone,
            "Lamentamos que a experiencia nao tenha sido ideal. "
            "Pode nos contar o que aconteceu? Queremos melhorar.",
        )
