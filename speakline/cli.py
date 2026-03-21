"""Command-line interface for SpeakLine."""

from typing import Optional
import logging
import sys

import typer
from rich.console import Console
from rich.logging import RichHandler

from .commenter import VoiceCommenter, VoiceCommenterError
from .recorder import AudioConfig
from .transcriber import WhisperTranscriber, OpenAITranscriber, MockTranscriber
from .formatter import get_formatter

# Set up rich console
console = Console()

# Create Typer app
app = typer.Typer(
    name="speakline",
    help="Record voice and insert as inline code comments.",
    add_completion=False,
)


def setup_logging(verbose: bool = False) -> None:
    """Configure logging with rich handler."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)],
    )


@app.command()
def record(
    filepath: str = typer.Argument(..., help="Path to the source file to modify"),
    line_number: int = typer.Argument(..., help="Line number to insert comment at (1-indexed)"),
    duration: Optional[float] = typer.Option(
        None,
        "--duration",
        "-d",
        help="Fixed recording duration in seconds (maximum 60). Uses silence detection if not set.",
    ),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Programming language (auto-detected from file extension if not set)",
    ),
    backend: str = typer.Option(
        "whisper",
        "--backend",
        "-b",
        help="Transcription backend: whisper, openai, or mock",
    ),
    model_size: str = typer.Option(
        "base",
        "--model-size",
        "-m",
        help="Whisper model size: tiny, base, small, medium, large",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="OpenAI API key (for openai backend). Use OPENAI_API_KEY env var instead",
        envvar="OPENAI_API_KEY",
        hidden=True,
    ),
    format_mode: str = typer.Option(
        "rules",
        "--format",
        "-f",
        help="Comment formatting: 'llm' (OpenAI cleanup), 'rules' (local), 'none' (raw)",
    ),
    preview: bool = typer.Option(
        False,
        "--preview",
        "-p",
        help="Show what would be inserted without modifying the file",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Record voice and insert as comment in a source file.

    Records audio from your microphone, transcribes it using the specified
    backend, and inserts the transcribed text as a comment at the specified
    line number in the source file.

    Examples:
        speakline record myfile.py 42
        speakline record main.js 15 --duration 60
        speakline record code.go 10 --backend openai
        speakline record myfile.py 42 --preview
        speakline record myfile.py 42 --format llm
    """
    setup_logging(verbose)

    # Validate duration maximum
    if duration is not None and duration > 60:
        console.print(
            "[bold red]Error:[/bold red] Duration cannot exceed 60 seconds. "
            f"Got {duration}s instead."
        )
        raise typer.Exit(code=1)

    # Create transcriber
    transcriber = _create_transcriber(backend, model_size, api_key)

    # Create formatter
    formatter = get_formatter(format_mode, api_key=api_key)

    # Create commenter
    commenter = VoiceCommenter(
        language=language,
        transcriber=transcriber,
        formatter=formatter,
    )

    console.print(f"[bold blue]Recording for {filepath}:{line_number}[/bold blue]")

    if duration:
        console.print(f"[dim]Recording for {duration} seconds...[/dim]")
    else:
        console.print("[dim]Recording... (speak, then pause to stop)[/dim]")

    try:
        # Get transcribed comment first
        comment = commenter.transcribe_only(duration=duration)

        if preview:
            # Show preview without modifying file
            import os
            if not os.path.exists(filepath):
                console.print(f"[bold red]Error:[/bold red] File not found: {filepath}")
                raise typer.Exit(code=1)

            with open(filepath, "r") as f:
                original_code = f.read()

            parser = commenter._get_parser(filepath)
            preview_code = parser.insert_comment(original_code, comment, line_number)

            console.print("\n[bold yellow]PREVIEW MODE (file not modified)[/bold yellow]")
            console.print(f"\n[bold cyan]Transcribed comment:[/bold cyan]\n{comment}\n")
            console.print("[bold cyan]File preview (first 500 chars):[/bold cyan]")
            preview_text = preview_code[:500]
            if len(preview_code) > 500:
                preview_text += "\n[dim]...(truncated)[/dim]"
            console.print("[dim]" + preview_text + "[/dim]")
            console.print("\n[bold green]Ready to commit![/bold green]")
            console.print("[dim]Run again without --preview to write to the file.[/dim]")
        else:
            # Original behavior: write to file
            commenter.insert_comment_to_file(
                filepath=filepath,
                comment=comment,
                line_number=line_number,
            )
            console.print(f"[bold green]Comment inserted:[/bold green] {comment}")

    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except VoiceCommenterError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def transcribe(
    duration: Optional[float] = typer.Option(
        None,
        "--duration",
        "-d",
        help="Fixed recording duration in seconds (maximum 60). Uses silence detection if not set.",
    ),
    backend: str = typer.Option(
        "whisper",
        "--backend",
        "-b",
        help="Transcription backend: whisper, openai, or mock",
    ),
    model_size: str = typer.Option(
        "base",
        "--model-size",
        "-m",
        help="Whisper model size: tiny, base, small, medium, large",
    ),
    api_key: Optional[str] = typer.Option(
        None,
        "--api-key",
        help="OpenAI API key (for openai backend). Use OPENAI_API_KEY env var instead",
        envvar="OPENAI_API_KEY",
        hidden=True,
    ),
    format_mode: str = typer.Option(
        "rules",
        "--format",
        "-f",
        help="Comment formatting: 'llm' (OpenAI cleanup), 'rules' (local), 'none' (raw)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Record and transcribe voice without modifying any files.

    Records audio from your microphone, transcribes it, and prints the
    result to stdout.

    Examples:
        speakline transcribe
        speakline transcribe --duration 60
        speakline transcribe --backend openai
        speakline transcribe --format llm
    """
    setup_logging(verbose)

    # Validate duration maximum
    if duration is not None and duration > 60:
        console.print(
            "[bold red]Error:[/bold red] Duration cannot exceed 60 seconds. "
            f"Got {duration}s instead."
        )
        raise typer.Exit(code=1)

    # Create transcriber
    transcriber = _create_transcriber(backend, model_size, api_key)

    # Create formatter
    formatter = get_formatter(format_mode, api_key=api_key)

    # Create commenter
    commenter = VoiceCommenter(transcriber=transcriber, formatter=formatter)

    if duration:
        console.print(f"[dim]Recording for {duration} seconds...[/dim]")
    else:
        console.print("[dim]Recording... (speak, then pause to stop)[/dim]")

    try:
        text = commenter.transcribe_only(duration=duration)
        console.print(f"[bold green]Transcription:[/bold green] {text}")
    except VoiceCommenterError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def insert(
    filepath: str = typer.Argument(..., help="Path to the source file to modify"),
    line_number: int = typer.Argument(..., help="Line number to insert comment at (1-indexed)"),
    comment: str = typer.Argument(..., help="Comment text to insert"),
    language: Optional[str] = typer.Option(
        None,
        "--language",
        "-l",
        help="Programming language (auto-detected from file extension if not set)",
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
) -> None:
    """Insert a text comment into a source file (no recording).

    Directly inserts the provided comment text at the specified line number.
    Useful for testing or scripted usage.

    Examples:
        speakline insert myfile.py 42 "This is my comment"
        speakline insert main.js 15 "TODO: refactor this"
    """
    setup_logging(verbose)

    commenter = VoiceCommenter(language=language)

    try:
        commenter.insert_comment_to_file(filepath, comment, line_number)
        console.print(f"[bold green]Comment inserted at {filepath}:{line_number}[/bold green]")
    except FileNotFoundError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)
    except VoiceCommenterError as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command()
def version() -> None:
    """Show the version of speakline."""
    from . import __version__

    console.print(f"speakline {__version__}")


def _create_transcriber(
    backend: str,
    model_size: str,
    api_key: Optional[str],
) -> "TranscriberBase":
    """Create transcriber based on backend selection."""
    if backend == "whisper":
        return WhisperTranscriber(model_size=model_size)
    elif backend == "openai":
        if not api_key:
            console.print(
                "[bold red]Error:[/bold red] OpenAI API key required. "
                "Set OPENAI_API_KEY or use --api-key"
            )
            raise typer.Exit(code=1)
        return OpenAITranscriber(api_key=api_key)
    elif backend == "mock":
        return MockTranscriber()
    else:
        console.print(f"[bold red]Error:[/bold red] Unknown backend: {backend}")
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    app()


if __name__ == "__main__":
    main()
