"""Evolution API — envio e recebimento de mensagens WhatsApp."""
import os
import urllib.request
import urllib.error
import json
import logging

log = logging.getLogger("whatsapp")

EVOLUTION_URL = os.getenv("EVOLUTION_URL", "http://localhost:8080")
EVOLUTION_INSTANCE = os.getenv("EVOLUTION_INSTANCE", "clinica")
EVOLUTION_KEY = os.getenv("EVOLUTION_API_KEY", "")


def _headers() -> dict:
    return {"Content-Type": "application/json", "apikey": EVOLUTION_KEY}


def send_text(phone: str, text: str) -> bool:
    """Envia mensagem de texto para o numero (formato: 5585999990000)."""
    url = f"{EVOLUTION_URL}/message/sendText/{EVOLUTION_INSTANCE}"
    payload = json.dumps({"number": phone, "text": text}).encode()
    req = urllib.request.Request(url, data=payload, headers=_headers(), method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            log.info("Mensagem enviada para %s — status %s", phone, r.status)
            return True
    except urllib.error.HTTPError as e:
        log.error("Erro ao enviar para %s: %s", phone, e)
        return False


def parse_webhook(body: dict) -> dict | None:
    """Extrai {phone, name, message} de um webhook da Evolution API."""
    try:
        data = body.get("data", {})
        key = data.get("key", {})
        phone = key.get("remoteJid", "").split("@")[0]
        name = data.get("pushName", phone)
        msg = data.get("message", {})
        text = (
            msg.get("conversation")
            or msg.get("extendedTextMessage", {}).get("text")
            or ""
        )
        if not phone or not text:
            return None
        return {"phone": phone, "name": name, "message": text.strip()}
    except Exception as e:
        log.warning("Falha ao parsear webhook: %s", e)
        return None
