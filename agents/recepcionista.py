"""Agente recepcionista 24/7 — responde duvidas e agenda consultas."""
from core import database as db, whatsapp as wa, llm

SYSTEM = """Voce e a recepcionista virtual da clinica. Responda de forma simpatica,
objetiva e profissional. Ajude o paciente a agendar consultas, tirar duvidas sobre
horarios, especialidades e valores. Se nao souber algo, diga que vai verificar.
Responda SEMPRE em portugues brasileiro, de forma curta (max 3 linhas por mensagem)."""


def handle(phone: str, name: str, message: str) -> None:
    db.upsert_paciente(phone, name)
    historico = db.get_historico(phone)
    historico.append({"role": "user", "content": message})
    db.add_historico(phone, "user", message)

    resposta = llm.chat(SYSTEM, historico)
    db.add_historico(phone, "assistant", resposta)
    wa.send_text(phone, resposta)
