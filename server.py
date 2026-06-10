"""FastAPI — webhook Evolution API + scheduler de rotinas."""
from __future__ import annotations
import os
import threading
import time
import logging
from pathlib import Path

from dotenv import load_dotenv
load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env")

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from core import database as db
from core import whatsapp as wa
from agents import recepcionista, confirmador, resgate, avaliacao, painel

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("server")

app = FastAPI(title="Agente Clinica WhatsApp")

ALUNO_TOKEN = os.getenv("ALUNO_TOKEN", "trocar-em-producao")
PHONE_DONO = os.getenv("PHONE_DONO", "")


# ── Webhook ─────────────────────────────────────────────────────────────────

@app.post("/webhook")
async def webhook(request: Request) -> JSONResponse:
    body = await request.json()
    msg = wa.parse_webhook(body)
    if not msg:
        return JSONResponse({"ok": True})

    phone, name, message = msg["phone"], msg["name"], msg["message"]
    log.info("Mensagem de %s (%s): %s", name, phone, message[:80])

    # Respostas de confirmacao de consulta
    msg_lower = message.lower()
    if any(w in msg_lower for w in ("sim", "nao", "confirmo", "cancelar")):
        confirmador.processar_resposta(phone, message)
    else:
        recepcionista.handle(phone, name, message)

    return JSONResponse({"ok": True})


# ── Endpoints de gerenciamento ───────────────────────────────────────────────

def _check_token(request: Request) -> None:
    token = request.headers.get("X-Token", "")
    if token != ALUNO_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/rotinas/confirmacoes")
async def rotina_confirmacoes(request: Request) -> JSONResponse:
    _check_token(request)
    n = confirmador.confirmar_amanha()
    return JSONResponse({"enviados": n})


@app.post("/rotinas/resgates")
async def rotina_resgates(request: Request) -> JSONResponse:
    _check_token(request)
    n = resgate.resgatar_faltosos()
    return JSONResponse({"enviados": n})


@app.post("/rotinas/avaliacoes")
async def rotina_avaliacoes(request: Request) -> JSONResponse:
    _check_token(request)
    n = avaliacao.solicitar_avaliacao()
    return JSONResponse({"enviados": n})


@app.post("/rotinas/relatorio")
async def rotina_relatorio(request: Request) -> JSONResponse:
    _check_token(request)
    if not PHONE_DONO:
        raise HTTPException(status_code=400, detail="PHONE_DONO nao configurado")
    painel.enviar_relatorio_diario(PHONE_DONO)
    return JSONResponse({"ok": True})


# ── Scheduler interno simples ────────────────────────────────────────────────

def _scheduler() -> None:
    import datetime
    log.info("Scheduler iniciado")
    while True:
        now = datetime.datetime.now()
        h, m = now.hour, now.minute

        if h == 9 and m == 0:
            n = confirmador.confirmar_amanha()
            log.info("Confirmacoes enviadas: %d", n)

        if h == 10 and m == 0:
            n = resgate.resgatar_faltosos()
            log.info("Resgates enviados: %d", n)

        if h == 18 and m == 0:
            n = avaliacao.solicitar_avaliacao()
            log.info("Solicitacoes avaliacao: %d", n)

        if h == 20 and m == 0 and PHONE_DONO:
            painel.enviar_relatorio_diario(PHONE_DONO)
            log.info("Relatorio diario enviado para %s", PHONE_DONO)

        time.sleep(60)


@app.on_event("startup")
def startup() -> None:
    db.init_db()
    t = threading.Thread(target=_scheduler, daemon=True)
    t.start()
    log.info("Agente Clinica WhatsApp pronto na porta %s", os.getenv("PORT", "8800"))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=int(os.getenv("PORT", "8800")), reload=False)
