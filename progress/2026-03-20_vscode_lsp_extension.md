# VS Code Extension + LSP Sidecar + Context-Aware Formatting — 2026-03-20

## What was built

### LSP Server (`speakline/lsp/`)
- `server.py` — pygls-based Language Server Protocol server
- Communicates via stdio (default) or TCP
- Commands: recordAtCursor, recordAtCursorPreview, transcribeOnly, insertComment
- Handles 0-indexed (VS Code) to 1-indexed (SpeakLine) line conversion
- Thread-safe recording lock prevents concurrent recordings
- Auto-detects language from file extension

### VS Code Extension (`vscode-extension/`)
- `src/extension.ts` — main extension entry point
- Spawns LSP server as child process (stdio) or connects via TCP
- Auto-detects cursor position — no manual line number needed
- Keybindings: Ctrl+Shift+V (record+insert), Ctrl+Shift+Alt+V (preview)
- Status bar indicator with recording state
- Preview mode: shows comment, user picks Insert/Discard
- Transcribe-only copies to clipboard
- Manual insert via input box

### Config additions
- `pyproject.toml`: added `pygls`, `lsprotocol` deps + `speakline-lsp` entry point
- `.gitignore`: extension build artifacts

## Architecture
```
VS Code Extension (TypeScript)
  ↕ LSP (stdio/TCP)
SpeakLine LSP Server (Python/pygls)
  ↕ Direct import
SpeakLine Core (commenter, recorder, transcriber, parser)
```

### Context-Aware Comment Formatter (`speakline/formatter.py`)
- **RuleBasedFormatter** (default) — removes filler words, condenses phrasing, no API needed
- **LLMFormatter** — OpenAI GPT-3.5 post-processing, transforms verbose speech into concise comments
  - Reads surrounding code context (5 lines above/below) for smarter formatting
  - Falls back to rule-based if API fails
- **PassthroughFormatter** — raw transcription, no changes
- CLI flag: `--format llm|rules|none`
- Wired into both `record_and_insert()` and `transcribe_only()` in VoiceCommenter
- Example: "uh this function basically like takes the input and then returns the factorial recursively"
  → Rule-based: "Takes the input, returns the factorial recursively"
  → LLM: "Recursively computes factorial of n"

### Exports added
- `speakline/__init__.py`: FormatterBase, RuleBasedFormatter, LLMFormatter, PassthroughFormatter, FormatterError, get_formatter

## How to use
1. `pip install -e .` (installs pygls + lsprotocol)
2. `cd vscode-extension && npm install && npm run compile`
3. Open in VS Code, F5 to launch Extension Development Host
4. Ctrl+Shift+V at any cursor position to record + insert comment
