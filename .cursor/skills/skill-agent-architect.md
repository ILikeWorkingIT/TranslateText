---
name: skill-agent-architect
description: >-
  Router for the architect agent. Opens existing /nft /ddd /data-dictionary
  /openai skills. Does not duplicate their algorithms.
disable-model-invocation: true
owner: architect
---

# Скилл агента architect

Открой и выполни точечный скилл.

| Задача | Команда | Скилл |
| --- | --- | --- |
| Нефункциональные требования | `/nft` | `.cursor/skills/skill-nft.md` |
| Доменная модель | `/ddd` | `.cursor/skills/skill-ddd.md` |
| Словарь данных | `/data-dictionary` | `.cursor/skills/skill-data-dictionary.md` |
| OpenAPI | `/openai` | `.cursor/skills/skill-openai.md` |

`openapi.yaml` не создавай, если в `reports/project-config.md` своего HTTP API нет.
