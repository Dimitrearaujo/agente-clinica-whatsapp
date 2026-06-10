"""Painel da dona — relatorios e metricas via WhatsApp."""
from core import database as db, whatsapp as wa
from datetime import datetime, timedelta


def enviar_relatorio_diario(phone_dono: str) -> None:
    """Envia resumo do dia para o numero da dona da clinica."""
    hoje = datetime.now().date()

    with db.connect() as conn:
        agendadas = conn.execute(
            "SELECT COUNT(*) FROM consultas WHERE date(data_hora)=? AND status='agendada'",
            (str(hoje),),
        ).fetchone()[0]

        realizadas = conn.execute(
            "SELECT COUNT(*) FROM consultas WHERE date(data_hora)=? AND status='realizada'",
            (str(hoje),),
        ).fetchone()[0]

        faltosos = conn.execute(
            "SELECT COUNT(*) FROM consultas WHERE date(data_hora)=? AND status='faltou'",
            (str(hoje),),
        ).fetchone()[0]

        total_pacientes = conn.execute(
            "SELECT COUNT(*) FROM pacientes",
        ).fetchone()[0]

    taxa_comparecimento = (
        f"{round(realizadas / (realizadas + faltosos) * 100)}%"
        if (realizadas + faltosos) > 0
        else "N/A"
    )

    msg = (
        f"*Relatorio do dia {hoje.strftime('%d/%m/%Y')}*\n\n"
        f"Agendadas hoje: {agendadas}\n"
        f"Realizadas: {realizadas}\n"
        f"Faltosos: {faltosos}\n"
        f"Taxa comparecimento: {taxa_comparecimento}\n"
        f"Total pacientes cadastrados: {total_pacientes}"
    )
    wa.send_text(phone_dono, msg)
