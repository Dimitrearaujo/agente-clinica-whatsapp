# Agente Clinica WhatsApp

![CI](https://github.com/Dimitrearaujo/agente-clinica-whatsapp/actions/workflows/ci.yml/badge.svg)

Sistema de automacao WhatsApp para clinicas (veterinarias, odontologicas, esteticas) com 5 agentes IA operando 24/7.

## Agentes

| Agente | Funcao |
|---|---|
| Recepcionista 24/7 | Responde duvidas, agenda consultas via IA (Claude) |
| Confirmador de vespera | Lembrete automatico D-1 + coleta confirmacao |
| Resgate de faltosos | Contata paciente que nao compareceu |
| Retorno + Avaliacao Google | NPS pos-consulta + solicitacao de review |
| Painel da dona | Relatorio diario no WhatsApp da gestora |

## Arquitetura

```
Evolution API (WhatsApp)
        |
        v
   server.py (FastAPI)
        |
   +----+----+----+----+
   |    |    |    |    |
  rec conf res ava painel
   |    |    |    |
  llm.py (Claude Haiku)
        |
   database.py (SQLite)
```

## Instalacao

```bash
git clone https://github.com/Dimitrearaujo/agente-clinica-whatsapp
cd agente-clinica-whatsapp
pip install -r requirements.txt

cp .env.example .env
# Edite .env com suas chaves
```

**Pre-requisitos:**
- Evolution API rodando com instancia conectada ao WhatsApp
- Chave Anthropic (Claude Haiku — custo ~$0.01/1000 msgs)

## Uso

```bash
# Iniciar servidor
python server.py

# Configurar webhook na Evolution API:
# POST http://localhost:8080/webhook/set/<instancia>
# URL: http://SEU_IP:8800/webhook
```

## Rotinas automaticas

O scheduler interno dispara diariamente:

| Horario | Rotina |
|---|---|
| 09:00 | Confirmacoes de consulta (D+1) |
| 10:00 | Resgate de faltosos do dia anterior |
| 18:00 | Solicitacao de avaliacao Google |
| 20:00 | Relatorio diario para a dona |

Ou trigger manual via API:

```bash
curl -X POST http://localhost:8800/rotinas/confirmacoes \
  -H "X-Token: SEU_TOKEN"
```

## Estrutura

```
agente-clinica-whatsapp/
   agents/
      recepcionista.py   # IA conversacional
      confirmador.py     # Lembretes D-1
      resgate.py         # Faltosos
      avaliacao.py       # NPS + Google Review
      painel.py          # Relatorio gestora
   core/
      llm.py             # Wrapper Claude API
      whatsapp.py        # Evolution API
      database.py        # SQLite
   server.py             # FastAPI + scheduler
```

## Licenca

MIT

---

<details>
<summary>🇺🇸 English</summary>

# Clinic WhatsApp Agent

![CI](https://github.com/Dimitrearaujo/agente-clinica-whatsapp/actions/workflows/ci.yml/badge.svg)

WhatsApp automation system for clinics (veterinary, dental, aesthetic) with 5 AI agents operating 24/7.

## Agents

| Agent | Function |
|---|---|
| 24/7 Receptionist | Answers questions, schedules appointments via AI (Claude) |
| Day-before Confirmation | Automated D-1 reminder + confirmation collection |
| No-show Recovery | Contacts patients who missed their appointment |
| Return + Google Review | Post-appointment NPS + review request |
| Manager Dashboard | Daily report sent to the clinic owner via WhatsApp |

## Architecture

```
Evolution API (WhatsApp)
        |
        v
   server.py (FastAPI)
        |
   +----+----+----+----+
   |    |    |    |    |
  rec conf  res  ava panel
   |    |    |    |
  llm.py (Claude Haiku)
        |
   database.py (SQLite)
```

## Installation

```bash
git clone https://github.com/Dimitrearaujo/agente-clinica-whatsapp
cd agente-clinica-whatsapp
pip install -r requirements.txt

cp .env.example .env
# Edit .env with your keys
```

**Prerequisites:**
- Evolution API running with a connected WhatsApp instance
- Anthropic API key (Claude Haiku — cost ~$0.01/1000 messages)

## Usage

```bash
# Start server
python server.py

# Configure webhook on Evolution API:
# POST http://localhost:8080/webhook/set/<instance>
# URL: http://YOUR_IP:8800/webhook
```

## Automated routines

The internal scheduler runs daily:

| Time | Routine |
|---|---|
| 09:00 | Appointment confirmations (D+1) |
| 10:00 | Recovery of previous day's no-shows |
| 18:00 | Google review request |
| 20:00 | Daily report for the owner |

Or manual trigger via API:

```bash
curl -X POST http://localhost:8800/rotinas/confirmacoes \
  -H "X-Token: YOUR_TOKEN"
```

## Structure

```
agente-clinica-whatsapp/
   agents/
      recepcionista.py   # Conversational AI
      confirmador.py     # D-1 reminders
      resgate.py         # No-shows
      avaliacao.py       # NPS + Google Review
      painel.py          # Manager report
   core/
      llm.py             # Claude API wrapper
      whatsapp.py        # Evolution API
      database.py        # SQLite
   server.py             # FastAPI + scheduler
```

## License

MIT

</details>

---

[← Back to profile](https://github.com/Dimitrearaujo)
