### Что должно быть:

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
___
Всё перечисленное работает и в других агентах (Codex CLI, Cursor, Gemini CLI, Cline, OpenCode), просто менее удобно и быстро, + subagents, hooks от claude code не переносятся напрямую, также как и некоторые скиллы, но перенести руками не сложно - все open source.
z 