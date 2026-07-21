from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.text import Text
from rich.style import Style
from rich.columns import Columns
from rich.prompt import Prompt
from rich.layout import Layout
from rich.live import Live
from rich import box
from datetime import datetime
import shutil

console = Console()

THEME_COLORS = {
    "cyberpunk": "#00ffff",
    "matrix": "#00ff41",
    "fire": "#ff6400",
    "ocean": "#0096ff",
    "neon": "#ff00ff",
}

class HUD:
    def __init__(self, theme="cyberpunk"):
        self.theme = theme
        self.accent_color = THEME_COLORS.get(theme, "#00ffff")

    def header(self, title, subtitle=""):
        term = shutil.get_terminal_size().columns
        t = f"[bold {self.accent_color}]  {title}[/]"
        if subtitle:
            t += f"  [dim]{subtitle}[/]"
        console.rule(t, style=self.accent_color)

    def section(self, name):
        console.print(f"\n[bold #ffc800]▒ {name}[/]")
        console.rule(style="#444444")

    def info(self, label, value=""):
        if value:
            console.print(f"  [bold #ffff64]{label}:[/] {value}")
        else:
            console.print(f"  [#00ccff]{label}[/]")

    def success(self, msg):
        console.print(f"  [bold #00ff64]✓[/] [#00ff64]{msg}[/]")

    def error(self, msg):
        console.print(f"  [bold #ff3c3c]✗[/] [#ff3c3c]{msg}[/]")

    def warning(self, msg):
        console.print(f"  [bold #ffc800]⚠[/] [#ffc800]{msg}[/]")

    def status(self, msg):
        console.print(f"  [#00ccff]▶[/] {msg}")

    def divider(self):
        console.rule(style="#444444")

    def table(self, headers, rows, title=""):
        tb = Table(title=title, title_style=f"bold {self.accent_color}",
                   border_style=self.accent_color, header_style=f"bold {self.accent_color}",
                   box=box.ROUNDED)
        for h in headers:
            tb.add_column(h)
        for row in rows:
            tb.add_row(*[str(c) for c in row])
        console.print(tb)

    def panel(self, content, title=""):
        console.print(Panel(content, title=title, border_style=self.accent_color))

    def result_line(self, key, value, status=""):
        if status:
            sc = {"open": "green", "closed": "red", "found": "green", "missing": "yellow"}.get(status, "white")
            console.print(f"    [bold #ffff64]{key}[/]  {value}  [{sc}]{status}[/]")
        else:
            console.print(f"    [bold #ffff64]{key}[/]  {value}")

    def progress_bar(self, iterable, label="Processing..."):
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                      BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                      console=console) as prog:
            task = prog.add_task(label, total=len(iterable))
            for item in iterable:
                yield item
                prog.update(task, advance=1)

    def loading(self, message="Loading..."):
        with Progress(SpinnerColumn(), TextColumn(f"{{task.description}}"), console=console) as p:
            p.add_task(message, total=None)

    def prompt(self, text, default=""):
        return Prompt.ask(f"[{self.accent_color}]{text}[/]", default=default)

    def confirm(self, text):
        from rich.prompt import Confirm
        return Confirm.ask(f"[{self.accent_color}]{text}[/]")

    def clear(self):
        console.clear()

    def print(self, text, style=""):
        if style:
            console.print(Text(text, style=style))
        else:
            console.print(text)

    def rule(self):
        console.rule(style="#444444")
