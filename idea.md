# VoiceComment

**Record voice and insert as inline code comments across any language and IDE.**

Turn your spoken thoughts into well-formatted code comments with a single command. Works with Python, JavaScript, TypeScript, Go, Rust, Java, and more.

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Status](https://img.shields.io/badge/status-alpha-yellow.svg)

## Features

- 🎤 **Voice Recording**: Local microphone input with silence detection
- 🧠 **Transcription**: Support for Whisper (local) and OpenAI API
- 📝 **Smart Comment Insertion**: Language-aware parser with proper indentation
- 🌍 **Multi-Language Support**: Python, JavaScript, TypeScript, Go, Rust, Java, C#, Ruby
- 🔌 **Pluggable Backends**: Swap recorders, transcribers, and parsers easily
- 🎯 **Flexible API**: CLI, Python package, and programmatic access
- ⚡ **Production-Ready**: Type hints, error handling, and comprehensive logging

## Installation

### Prerequisites
- Python 3.9+
- PortAudio (for audio recording)

### macOS
```bash
brew install portaudio
```

### Ubuntu/Debian
```bash
sudo apt-get install portaudio19-dev
```

### Windows
PortAudio is typically bundled. If not, download from [PortAudio Downloads](http://www.portaudio.com/download.html).

### Install Package

```bash
pip install voicecomment
```

Or from GitHub (development):
```bash
git clone https://github.com/yourusername/voicecomment
cd voicecomment
pip install -e .
```

## Quick Start

### Command Line

```bash
# Record and insert comment at line 42
voicecomment record myfile.py 42

# With fixed duration (5 seconds)
voicecomment record myfile.py 42 --duration 5

# Transcribe without modifying file
voicecomment transcribe
```

### Python API

```python
from voicecomment import VoiceCommenter

# Auto-detect language from file extension
commenter = VoiceCommenter()
commenter.record_and_insert('myfile.py', line_number=42)

# Or specify language explicitly
commenter = VoiceCommenter(language='python')
commenter.record_and_insert('main.py', line_number=15)

# Transcribe only
text = commenter.transcribe_only()
print(text)  # "This function calculates factorial recursively"

# Insert into code string (no file I/O)
code = """
def factorial(n):
    return n * factorial(n - 1) if n > 1 else 1
"""
updated = commenter.insert_comment_to_string(
    code, 
    "Base case for recursion", 
    line_number=3
)
print(updated)
```

### Jupyter Notebook

```python
from voicecomment import VoiceCommenter

commenter = VoiceCommenter(language='python')

# Record and modify cell code
code_str = """
def process_data(df):
    return df.dropna()
"""

updated = commenter.insert_comment_to_string(
    code_str,
    "Remove rows with missing values",
    line_number=2
)
print(updated)
```

## Architecture

### Core Components

#### 1. **AudioRecorder** (`recorder.py`)
- `LocalAudioRecorder`: Captures audio from system microphone
- Supports fixed duration or silence detection
- Configurable sample rate, channels, and format

#### 2. **Transcriber** (`transcriber.py`)
Pluggable backends:
- `WhisperTranscriber`: Local OpenAI Whisper model (no API key needed)
- `OpenAITranscriber`: OpenAI Whisper API
- `MockTranscriber`: For testing without audio hardware

```python
# Use local Whisper
from voicecomment.transcriber import WhisperTranscriber
transcriber = WhisperTranscriber(model_size="base")

# Or OpenAI API
from voicecomment.transcriber import OpenAITranscriber
transcriber = OpenAITranscriber(api_key="sk-...")
```

#### 3. **CodeParser** (`parser.py`)
Language-specific parsers:
- `PythonParser`: Uses AST for intelligent insertion
- `JavaScriptParser`: Handles indentation and scoping
- `GenericParser`: Regex-based fallback for unsupported languages

#### 4. **VoiceCommenter** (`commenter.py`)
Main orchestration class that ties everything together.

## Advanced Usage

### Custom Transcriber

```python
from voicecomment import VoiceCommenter
from voicecomment.transcriber import TranscriberBase
import numpy as np

class CustomLLMTranscriber(TranscriberBase):
    def transcribe(self, audio: np.ndarray, sample_rate: int = 16000) -> str:
        # Your LLM logic here
        return "custom transcription"

commenter = VoiceCommenter(transcriber=CustomLLMTranscriber())
commenter.record_and_insert('file.py', line_number=10)
```

### Custom Audio Config

```python
from voicecomment import VoiceCommenter
from voicecomment.recorder import AudioConfig

config = AudioConfig(
    sample_rate=44100,  # High-quality audio
    channels=2,         # Stereo
)

commenter = VoiceCommenter(audio_config=config)
```

### Integration with IDE Extensions

The Python package can be called from:
- **VS Code Extension**: Via subprocess or Node.js child process
- **Vim Plugin**: Via Python 3 interface
- **Neovim**: Via Python plugin host
- **Emacs**: Via `python-shell`

Example VS Code extension (snippet):
```typescript
const { spawn } = require('child_process');

const proc = spawn('voicecomment', ['record', filepath, lineNumber.toString()]);
proc.on('close', (code) => {
  if (code === 0) {
    vscode.window.showInformationMessage('Comment inserted!');
  }
});
```

## Development

### Setup

```bash
git clone https://github.com/yourusername/voicecomment
cd voicecomment
pip install -e ".[dev]"
```

### Testing

```bash
pytest
pytest --cov  # With coverage
```

### Code Quality

```bash
black .
ruff check .
mypy voicecomment/
```

## Portfolio Impact

This project demonstrates:

1. **Production AI/ML System Design**
   - Modular architecture with pluggable backends
   - Multiple transcription strategies (local vs. API)
   - Graceful fallbacks and error handling

2. **Language Agnostics & Parsing**
   - AST-based analysis (Python)
   - Regex-based parsing (fallback)
   - Support for 8+ languages out of the box

3. **Tool Development**
   - CLI design with Typer
   - Type hints throughout
   - Comprehensive documentation

4. **Integration Design**
   - Package-first approach (not IDE-locked)
   - Easy embedding in VS Code, Vim, Emacs
   - Jupyter notebook support

5. **DevOps & Distribution**
   - Modern `pyproject.toml` setup
   - PyPI publishing-ready
   - CI/CD hooks included

## Roadmap

- [ ] Vs Code Extension (official)
- [ ] Vim/Neovim plugin
- [ ] Watch mode for automated comment markers
- [ ] Voice activity detection (VAD)
- [ ] Conversation-aware transcription (context from file)
- [ ] Custom prompt engineering for comment style
- [ ] Analytics dashboard (tracking comment patterns)
- [ ] Langchain integration for LLM-powered comments

## Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT License - see [LICENSE](LICENSE)

## Citation

If you use VoiceComment in your work, please cite:

```bibtex
@software{voicecomment2024,
  author = {Your Name},
  title = {VoiceComment: Voice-to-code commenting for any language and IDE},
  year = {2024},
  url = {https://github.com/yourusername/voicecomment}
}
```

---

**Built by a production ML engineer who believed code comments should be as natural as talking.**