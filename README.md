# Agente Clinica WhatsApp

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
