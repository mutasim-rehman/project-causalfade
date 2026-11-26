"""Sanitize accidental Markdown formatting (**bold**, *italic*, `code`), \n inside \texttt, and unescaped prose '&' in chapter/appendix TeX files."""
from pathlib import Path
import re

RETRO = Path(__file__).resolve().parents[1]


def escape_code_inner(s: str) -> str:
    s = s.replace("\\n", "\\textbackslash n")
    s = re.sub(r"(?<!\\)_", r"\_", s)
    s = re.sub(r"(?<!\\)%", r"\%", s)
    s = re.sub(r"(?<!\\)&", r"\&", s)
    s = re.sub(r"(?<!\\)#", r"\#", s)
    return f"\\texttt{{{s}}}"


def process_text_segment(seg: str, in_tabular: bool) -> str:
    # Fix any broken split **...\textbf{...}...** artifacts first
    seg = re.sub(r"\*\*([^\n]*?)\\textbf\{([^\n]*?)\}([^\n]*?)\*\*", r"\\textbf{\1}\2\\textbf{\3}", seg)
    # Convert any remaining **bold** across inline math safely
    seg = re.sub(r"\*\*([^*\n]+)\*\*", r"\\textbf{\1}", seg)
    # Fix \n inside \texttt{...}
    seg = re.sub(r"(\\texttt\{[^}\n]*?)\\n([^}\n]*?\})", lambda m: m.group(0).replace("\\n", "\\textbackslash n"), seg)

    math_pattern = re.compile(
        r"(\$\$[\s\S]*?\$\$|\$[^$\n]+\$|\\\[[\s\S]*?\\\]|\\begin\{(?:equation|align|gather)\*?\}[\s\S]*?\\end\{(?:equation|align|gather)\*?\})"
    )
    parts = math_pattern.split(seg)
    out = []
    for idx, part in enumerate(parts):
        if idx % 2 == 1:
            out.append(part)
            continue
        part = re.sub(r"(?<!`)`([^`\n]+)`(?!`)", lambda m: escape_code_inner(m.group(1)), part)
        part = re.sub(r"(?<![\\A-Za-z}\^])\*([^*\n]+)\*", r"\\emph{\1}", part)
        if not in_tabular:
            part = re.sub(r"(?<!\\)&", r"\&", part)
        out.append(part)
    return "".join(out)


def sanitize_file(path: Path):
    raw = path.read_text(encoding="utf-8")
    lst_pattern = re.compile(r"(\\begin\{lstlisting\}[\s\S]*?\\end\{lstlisting\})")
    chunks = lst_pattern.split(raw)
    result = []
    tab_pattern = re.compile(r"(\\begin\{(?:tabular|tabularx|longtable)\}[\s\S]*?\\end\{(?:tabular|tabularx|longtable)\})")
    for i, ch in enumerate(chunks):
        if i % 2 == 1:
            result.append(ch)
            continue
        subchunks = tab_pattern.split(ch)
        for j, sub in enumerate(subchunks):
            result.append(process_text_segment(sub, in_tabular=(j % 2 == 1)))
    cleaned = "".join(result)
    cleaned = re.sub(r'\\texttt\{\{("[^"\n]+":\s*[^}\n]+)\}\}', r'\\texttt{\\{\1\\}}', cleaned)
    cleaned = re.sub(r'\\texttt\{([0-9a-f]{32,64}(?:\.\.\.)?)\}', r'\\nolinkurl{\1}', cleaned)
    if cleaned != raw:
        path.write_text(cleaned, encoding="utf-8")
        print(f"Updated {path.relative_to(RETRO)}")


if __name__ == "__main__":
    for folder in ["chapters", "appendices"]:
        for p in sorted((RETRO / folder).glob("*.tex")):
            sanitize_file(p)
            txt = re.sub(r"\\begin\{lstlisting\}[\s\S]*?\\end\{lstlisting\}", "", p.read_text(encoding="utf-8"))
            if "**" in txt:
                for ln, l in enumerate(txt.splitlines(), 1):
                    if "**" in l:
                        print(f"WARN remaining ** in {p.name}:{ln}: {l}")
    print("Sanitization complete.")
