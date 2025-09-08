from __future__ import annotations

import os
import sys
import textwrap
from typing import Any, Dict, List, Optional

import typer
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from .config import AppConfig, config_dir, config_path, data_dir
from .history import Message, SessionRecord, list_sessions, load_session, new_session_id, save_session
from .openai_client import build_client, chat_completion, list_models, stream_chat_completion
from .utils import build_user_content, read_text_file


console = Console()
app = typer.Typer(add_completion=False, no_args_is_help=True, help="AI Shell: Chat with OpenAI from your terminal.")


def _print_kv_table(title: str, data: Dict[str, Any]) -> None:
    table = Table(title=title)
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for k, v in data.items():
        table.add_row(str(k), str(v))
    console.print(table)


@app.command()
def path() -> None:
    """Show important paths."""
    _print_kv_table(
        "Paths",
        {
            "config_dir": config_dir(),
            "config_path": config_path(),
            "data_dir": data_dir(),
        },
    )


@app.command()
def models() -> None:
    """List available models (best-effort)."""
    client = build_client()
    ids = list_models(client)
    if not ids:
        console.print("[yellow]Could not list models (check network/API key).[/yellow]")
        return
    table = Table(title="Models")
    table.add_column("#")
    table.add_column("ID")
    for i, mid in enumerate(ids, start=1):
        table.add_row(str(i), mid)
    console.print(table)


@app.command()
def config(
    show: bool = typer.Option(True, help="Show current config values."),
    set: Optional[List[str]] = typer.Option(None, help="Set values as key=value, e.g., --set model=gpt-4.1-mini"),
) -> None:
    """View or set configuration stored in your user config directory."""
    cfg = AppConfig.load()
    if set:
        pairs: Dict[str, str] = {}
        for item in set:
            if "=" not in item:
                console.print(f"[red]Invalid --set '{item}', expected key=value[/red]")
                raise typer.Exit(2)
            k, v = item.split("=", 1)
            pairs[k.strip()] = v.strip()
        cfg.update_from_pairs(pairs)
        cfg.save()
        console.print("[green]Config updated.[/green]")
    if show:
        _print_kv_table("Config", cfg.to_dict())
        console.print(f"Path: [magenta]{config_path()}[/magenta]")


def _render_assistant_text(text: str) -> None:
    try:
        console.print(Markdown(text))
    except Exception:
        console.print(text)


@app.command()
def ask(
    prompt: List[str] = typer.Argument(..., help="Your prompt (use quotes for multi-word)."),
    model: Optional[str] = typer.Option(None, help="Model to use."),
    temperature: Optional[float] = typer.Option(None, help="Sampling temperature."),
    system: Optional[str] = typer.Option(None, help="Optional system prompt."),
    stream: Optional[bool] = typer.Option(None, help="Stream the response."),
    file: Optional[List[str]] = typer.Option(None, help="Attach file(s) to the prompt (text or image)."),
) -> None:
    """Ask a single question (non-interactive)."""
    cfg = AppConfig.load()
    if model is not None:
        cfg.model = model
    if temperature is not None:
        cfg.temperature = temperature
    if stream is not None:
        cfg.stream = stream
    if system is not None:
        cfg.system_prompt = system

    text = " ".join(prompt)
    image_paths = []
    text_parts: List[str] = []
    if file:
        for p in file:
            if not os.path.exists(p):
                console.print(f"[yellow]File not found: {p}[/yellow]")
                continue
            ext = os.path.splitext(p)[1].lower()
            if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp"):
                image_paths.append(p)
            else:
                content = read_text_file(p)
                text_parts.append(f"\n\n# File: {os.path.basename(p)}\n\n{content}")
    final_text = text + ("".join(text_parts) if text_parts else "")

    user_content = build_user_content(final_text, image_paths)
    messages: List[Dict[str, Any]] = []
    if cfg.system_prompt:
        messages.append({"role": "system", "content": cfg.system_prompt})
    messages.append({"role": "user", "content": user_content})

    client = build_client()

    if cfg.stream:
        try:
            stream_iter = stream_chat_completion(
                client,
                messages=messages,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            buffer = ""
            for chunk in stream_iter:
                delta = chunk.choices[0].delta
                if delta and getattr(delta, "content", None):
                    part = delta.content or ""
                    buffer += part
                    console.print(part, end="")
                    console.file.flush()
            console.print()
            if cfg.save_history:
                record = SessionRecord(
                    id=new_session_id(),
                    created_at="",
                    model=cfg.model,
                    system_prompt=cfg.system_prompt,
                    messages=[
                        Message(role="user", content=final_text),
                        Message(role="assistant", content=buffer),
                    ],
                )
                save_session(record)
        except Exception as e:
            console.print(f"[red]Streaming failed: {e}. Falling back to non-streaming.[/red]")
            cfg.stream = False

    if not cfg.stream:
        resp = chat_completion(
            client,
            messages=messages,
            model=cfg.model,
            temperature=cfg.temperature,
            max_tokens=cfg.max_tokens,
        )
        text = resp.choices[0].message.content
        _render_assistant_text(text)
        if cfg.save_history:
            record = SessionRecord(
                id=new_session_id(),
                created_at="",
                model=cfg.model,
                system_prompt=cfg.system_prompt,
                messages=[
                    Message(role="user", content=final_text),
                    Message(role="assistant", content=text),
                ],
            )
            save_session(record)


HELP_TEXT = """
Commands inside chat (prefix with :)
  :help                Show this help
  :model <name>        Change model for this session
  :temp <value>        Set temperature
  :system <text>       Set session system prompt
  :attach <path>       Queue a file to attach (text or image)
  :new                 Start a new conversation
  :save [id]           Save current session to history
  :load <id|path>      Load a previous session
  :history             List previous sessions
  :config              Show current config
  :exit                Exit chat
Multi-line: end input with a blank line.
""".strip()


@app.command()
def chat() -> None:
    """Start an interactive chat session."""
    cfg = AppConfig.load()
    client = build_client()

    session_id = new_session_id()
    messages: List[Message] = []
    pending_attachments: List[str] = []

    if cfg.system_prompt:
        messages.append(Message(role="system", content=cfg.system_prompt))

    console.print(Panel.fit("AI Shell - interactive chat. Type :help for commands.", title="AI Shell"))

    def _send_prompt(prompt_text: str) -> None:
        nonlocal messages
        user_content = build_user_content(prompt_text, pending_attachments)
        pending_attachments.clear()

        # Convert to API message structure
        api_messages: List[Dict[str, Any]] = []
        for m in messages:
            api_messages.append({"role": m.role, "content": m.content})
        api_messages.append({"role": "user", "content": user_content})

        if cfg.stream:
            buffer = ""
            try:
                for chunk in stream_chat_completion(
                    client,
                    messages=api_messages,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                ):
                    delta = chunk.choices[0].delta
                    if delta and getattr(delta, "content", None):
                        part = delta.content or ""
                        buffer += part
                        console.print(part, end="")
                        console.file.flush()
                console.print()
            except Exception as e:
                console.print(f"[red]Streaming failed: {e}. Falling back to non-streaming.[/red]")
                # Fallback non-streaming
                resp = chat_completion(
                    client,
                    messages=api_messages,
                    model=cfg.model,
                    temperature=cfg.temperature,
                    max_tokens=cfg.max_tokens,
                )
                buffer = resp.choices[0].message.content
                _render_assistant_text(buffer)
            # Update in-memory history
            messages.append(Message(role="user", content=user_content))
            messages.append(Message(role="assistant", content=buffer))
        else:
            resp = chat_completion(
                client,
                messages=api_messages,
                model=cfg.model,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
            )
            text = resp.choices[0].message.content
            _render_assistant_text(text)
            messages.append(Message(role="user", content=user_content))
            messages.append(Message(role="assistant", content=text))

    # REPL
    buf: List[str] = []
    while True:
        try:
            line = input("you> ")
        except (EOFError, KeyboardInterrupt):
            console.print("\n[cyan]Exiting.[/cyan]")
            break

        if not line.strip() and buf:
            # Submit multi-line input
            prompt_text = "\n".join(buf).strip()
            buf.clear()
            if prompt_text:
                _send_prompt(prompt_text)
            continue

        if line.startswith(":") and not buf:
            # Command
            parts = line[1:].strip().split()
            if not parts:
                continue
            cmd, *args = parts
            if cmd in ("exit", "quit", "q"):
                break
            elif cmd == "help":
                console.print(Panel.fit(HELP_TEXT, title=":help"))
            elif cmd == "model" and args:
                cfg.model = " ".join(args)
                console.print(f"[green]Model set to {cfg.model}[/green]")
            elif cmd == "temp" and args:
                try:
                    cfg.temperature = float(args[0])
                    console.print(f"[green]Temperature set to {cfg.temperature}[/green]")
                except ValueError:
                    console.print("[red]Invalid temperature[/red]")
            elif cmd == "system":
                cfg.system_prompt = " ".join(args) if args else ""
                console.print("[green]System prompt updated.[/green]")
            elif cmd == "attach" and args:
                path = " ".join(args)
                if not os.path.exists(path):
                    console.print(f"[red]File not found: {path}[/red]")
                else:
                    pending_attachments.append(path)
                    console.print(f"[green]Attached:[/green] {path}")
            elif cmd == "new":
                if messages and cfg.save_history:
                    rec = SessionRecord(
                        id=session_id,
                        created_at="",
                        model=cfg.model,
                        system_prompt=cfg.system_prompt,
                        messages=messages,
                    )
                    save_session(rec)
                    console.print(f"[green]Saved conversation {session_id}[/green]")
                session_id = new_session_id()
                messages = []
                if cfg.system_prompt:
                    messages.append(Message(role="system", content=cfg.system_prompt))
                console.print("[cyan]Started new conversation.[/cyan]")
            elif cmd == "save":
                if cfg.save_history:
                    rec = SessionRecord(
                        id=session_id,
                        created_at="",
                        model=cfg.model,
                        system_prompt=cfg.system_prompt,
                        messages=messages,
                    )
                    path = save_session(rec)
                    console.print(f"[green]Saved to {path}[/green]")
                else:
                    console.print("[yellow]History saving disabled in config.[/yellow]")
            elif cmd == "load" and args:
                rec = load_session(args[0])
                if not rec:
                    console.print("[red]Could not load session.[/red]")
                else:
                    session_id = rec.id or new_session_id()
                    messages = rec.messages
                    cfg.model = rec.model or cfg.model
                    cfg.system_prompt = rec.system_prompt or cfg.system_prompt
                    console.print(f"[green]Loaded session {session_id}[/green]")
            elif cmd == "history":
                files = list_sessions()
                if not files:
                    console.print("[yellow]No sessions found.[/yellow]")
                else:
                    for f in files[:50]:
                        console.print(f)
            elif cmd == "config":
                _print_kv_table("Config", cfg.to_dict())
            else:
                console.print("[yellow]Unknown command. Type :help[/yellow]")
            continue

        # Accumulate multi-line input (empty line submits)
        buf.append(line)

    # On exit: save
    if messages and cfg.save_history:
        rec = SessionRecord(
            id=session_id,
            created_at="",
            model=cfg.model,
            system_prompt=cfg.system_prompt,
            messages=messages,
        )
        save_session(rec)
        console.print(f"[green]Saved conversation {session_id}[/green]")


if __name__ == "__main__":
    app()
