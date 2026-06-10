"""Agente resgate de faltosos — contata pacientes que nao compareceram."""
from core import database as db, whatsapp as wa


def resgatar_faltosos(horas: int = 4) -> int:
    """Envia mensagem de resgate para quem faltou nas ultimas N horas."""
    faltosos = db.get_faltosos(horas)
    enviados = 0
    for row in faltosos:
        msg = (
            f"Ola {row['nome']}! Notamos que voce nao compareceu a sua consulta hoje. "
            "Ficou tudo bem? Podemos reagendar para um horario mais conveniente. "
            "E so me dizer!"
        )
        if wa.send_text(row["phone"], msg):
            db.marcar_faltou(row["id"])
            enviados += 1
    return enviados
