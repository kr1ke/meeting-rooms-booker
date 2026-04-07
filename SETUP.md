## Что должно быть:

**Claude Code** — запускать командой `claude --model claude-opus-4-6 --effort max --dangerously-skip-permissions`
- `Opus 4.6` — последняя модель
- `effort max` — максимальный уровень reasoning
- `dangerously-skip-permissions` — чтобы агент не требовал подтверждения каждого действия, можно оставить автономно на часы

В процессе работы claude будет автоматически подбирать модель под заадчу, чтобы экономить токены.

**MCP**

- [**Context7**](https://github.com/upstash/context7) — актуальная документация библиотек/фреймворков для агентов, запрашивает сам либо по требованию
- [**Chrome DevTools**](https://github.com/ChromeDevTools/chrome-devtools-mcp) — управление браузером и доступ к девтулзам: network, console, lighthouse, performance traces, скриншоты, эмуляция устройств
- **Figma MCP** (если требуется) — есть [официальный, требующий подписку фигмы](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server), есть [open-source бесплатный](https://github.com/GLips/Figma-Context-MCP). Позволяет получать данные из фигмы и менять макет. Важно: официальный плагин `figma` в Claude Code устанавливает не только MCP, но и набор скиллов от Anthropic для работы с дизайном — должно работать лучше

**Плагины из официального маркетплейса Anthropic**

Маркетплейс `claude-plugins-official` встроен в Claude Code, добавлять его не нужно. Все плагины ставятся командой `/plugin install <name>@claude-plugins-official`. MCP-серверы выше тоже ставятся через этот маркетплейс одноимёнными плагинами (`context7`, `chrome-devtools-mcp`, `figma`).

- [**Superpowers**](https://github.com/obra/superpowers) — основной воркфлоу-каркас от Jesse Vincent: brainstorming, writing-plans, executing-plans, TDD, systematic-debugging, code-review, git-worktrees, parallel agents. Anthropic тянет его прямо из репо `obra/superpowers`
- [**frontend-design**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/frontend-design) — официальный дизайн-скилл от Anthropic для production-grade интерфейсов
- [**commit-commands**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/commit-commands) — команды git-воркфлоу: `/commit`, `/commit-push-pr`, `/clean_gone`
- [**code-review**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-review) — команда `/code-review` для PR, мульти-агентный с confidence scoring против ложных срабатываний
- [**code-simplifier**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) — агент, упрощающий и причёсывающий код для читаемости и поддерживаемости, фокусируется на недавно изменённых файлах
- [**security-guidance**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/security-guidance) — хук, предупреждающий о потенциальных проблемах безопасности при правках (command injection, XSS, небезопасные паттерны)
- [**typescript-lsp**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/typescript-lsp) / [**pyright-lsp**](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/pyright-lsp) — LSP для TS и Python, точные типы и переходы по символам

**Плагины из сторонних маркетплейсов**

Каждый требует сначала добавить marketplace командой `/plugin marketplace add <repo>`, затем установить плагин.

- [**Impeccable**](https://impeccable.style/) — 20 команд для фронт-дизайна (`/polish`, `/critique`, `/audit`, `/animate`, `/typeset`, `/distill` и др.). Дизайнерский словарь и библиотека антипаттернов. Расширяет `frontend-design` от Anthropic, может предлагать варианты на выбор. Маркетплейс: `pbakaus/impeccable`
- [**Understand-Anything**](https://github.com/Lum1104/Understand-Anything) (если нужно) — knowledge graph по кодбейсу с веб-дашбордом, онбордингом и объяснением файлов. Маркетплейс: `Lum1104/Understand-Anything`

**CLAUDE.md в корне репо** — правила, которые агент читает в начале каждой сессии (стек, требования к коду, ограничения, язык общения). Может также называться `AGENTS.md` — это кросс-агентный стандарт, который понимают Codex, Cursor, Gemini CLI и другие. 

Пример CLAUDE.md / AGENTS.md:

```markdown
Запускай и тестируй проект в Docker.
Используй chrome devtools mcp для тестирования в браузере.
Используй frontend-design-skill и impeccable skills для фронтенда и дизайна.
Делай ревью дизайна с помощью impeccable skills, давай варианты выбора.
Комментарии в коде должны быть на русском.
Общайся со мной на русском.
```

Всё перечисленное работает и в других агентах (Codex CLI, Cursor, Gemini CLI, Cline, OpenCode), просто менее удобно и быстро, + subagents, hooks от claude code не переносятся напрямую, также как и некоторые скиллы, но перенести руками не сложно - все open source.
___
## Workflow

Superpowers-скиллы автотриггерятся по описанию задачи. Чтобы вызвать вручную: `"используй brainstorming superpowers skill"`


Срабатывает на «давай сделаем X / запили фичу Y». Дальше все идет по superpowers flow:

1. **brainstorming** — опрос по задаче, уточнения, ресерч. Формирует спеку, чтобы понимать что агент будет делать, потом ее удобно ревьювить и использоваться как источник правды: `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
2. **using-git-worktrees** — запускается после аппрува дизайна. Создаёт новую ветку.
3. **writing-plans** — запускается при наличии утверждённого дизайна. Разбивает работу на мелкие таски (2–5 минут каждый). В каждом таске — точные пути к файлам, полный код, шаги верификации. Генерирует план: `docs/superpowers/plans/YYYY-MM-DD-<feature>.md`. В конце спрашивает: subagent-driven (рекомендуется) или executing-plans.
4. **subagent-driven-development** *(или `executing-plans` как inline-альтернатива)* — либо делегирует каждый таск отдельному субагенту, либо выполняет батчами с чекпоинтами для человека (на выбор). Сабагентам **никогда не даётся читать сам план** — задача передаётся текстом, чтобы избежать загрязнения контекста.
5. **test-driven-development** — запускается в процессе имплементации. Жёстко форсит RED-GREEN-REFACTOR: пишем падающий тест, убеждаемся что падает, пишем минимальный код, убеждаемся что проходит, коммитим
6. **requesting-code-review → receiving-code-review** — Task-сабагент `superpowers:code-reviewer` после выполнения каждого таска (не в самом конце, а между тасками) агент запускает код-ревью. Он сверяет написанный код с планом из шага 3 — всё ли сделано как задумано. Найденные проблемы ранжируются по критичности. Если находится критичный баг или отклонение от спеки — работа дальше не идёт, пока не пофиксят
7. **finishing-a-development-branch** — Запускается когда все таски выполнены. Проверяет тесты, предлагает варианты (merge / PR / оставить / выкинуть), чистит worktree.

### Скиллы которые могут тригерятся сами по требованию

Срабатывают сами на свои триггеры, но можно и вызывать вручную под задачу:

- **systematic-debugging** — на любой *bug / failing test / build fail / unexpected behavior*. 4 фазы: Root Cause → Pattern Analysis → Hypothesis & Minimal Test → Implementation. Фикс без понимания причины запрещён, после 3+ фейленых фиксов форсит остановку и пересмотр архитектуры. Ловит любой баг-репорт
- **dispatching-parallel-agents** — когда есть 2+ независимых задач без shared state (например, 3+ упавших файла теста с разными причинами), запустит агентов параллельно
- **verification-before-completion** — перед тем как сказать «готово», прогоняет финальную проверку
- **using-superpowers** (мета) — запускается при старте сессии, заставляет проверять применимость скиллов перед каждым ответом

### Что нужно вызывать руками

- `/code-review`
- `code-simplifier` Opus-сабагент, причёсывает недавно изменённые файлы для читаемости и поддерживаемости. Это **subagent**, а не скилл — вызов: `"используй code-simplifier agent"` 
- **`/commit`, `/commit-push-pr`, `/clean_gone`** (плагин `commit-commands`) — слэш-команды git-воркфлоу
- **Impeccable**-команды (`/polish`, `/critique`, `/audit`, `/animate`, `/typeset`, `/distill`, `/overdrive`, `/bolder`, `/quieter`, `/colorize`, `/arrange`, `/normalize`, `/extract`, `/delight`, `/adapt`, `/harden`, `/clarify`, `/optimize`, `/onboard` и др.) — могут в auto-trigger, но удобнее звать явно: «давай polish этого экрана», «critique главной страницы». Расширяют `frontend-design` от Anthropic, могут предлагать варианты на выбор
