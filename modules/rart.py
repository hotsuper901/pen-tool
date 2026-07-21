import pyfiglet
from rich.text import Text
from rich.console import Console

console = Console()

def render(text, font="slant", style="bold #00ffff"):
    try:
        fig = pyfiglet.Figlet(font=font)
        return fig.renderText(text)
    except:
        return text + "\n\n"

def colorized(text, font="slant", gradient=None):
    art = render(text, font)
    if gradient:
        lines = art.split("\n")
        out = []
        colors = gradient if len(gradient) > 1 else [gradient[0], gradient[0]]
        steps = max(len(lines) - 1, 1)
        for i, line in enumerate(lines):
            if not line.strip():
                out.append("")
                continue
            ratio = i / steps
            idx = min(int(ratio * (len(colors) - 1)), len(colors) - 2)
            c1, c2 = colors[idx], colors[idx + 1]
            styled = Text(line, style=c1)
            out.append(styled)
        return out
    return Text(art, style="bold #00ffff")

def banner(title="PENTEST", subtitle=""):
    art = render(title, "slant")
    t = Text()
    t.append(art, style="bold #00ffff")
    if subtitle:
        t.append(f"\n{subtitle}\n", style="italic #666666")
    return t

def section_header(text, style="bold #ffc800"):
    return Text(f"\n  ▒ {text}\n", style=style)

def result(label, value, label_style="bold #ffff64", value_style=""):
    return Text(f"    {label}: {value}", style=label_style)

def status(msg, style="#00ccff"):
    return Text(f"  {msg}", style=style)
