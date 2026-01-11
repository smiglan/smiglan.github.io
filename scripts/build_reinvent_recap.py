from __future__ import annotations

import re
from pathlib import Path

import markdown


def _fix_reference_lists(md_text: str) -> str:
    lines = md_text.splitlines()
    out: list[str] = []
    for idx, line in enumerate(lines):
        out.append(line)
        next_line = lines[idx + 1] if idx + 1 < len(lines) else ""

        stripped = line.strip()
        # Accept both "**Label**:" and "**Label:**" styles.
        is_bold_label = bool(
            re.match(r"^\*\*.+\*\*:\s*$", stripped) or re.match(r"^\*\*.+:\*\*\s*$", stripped)
        )
        next_is_list_item = next_line.lstrip().startswith("- ")
        if is_bold_label and next_is_list_item:
            out.append("")

    return "\n".join(out) + ("\n" if md_text.endswith("\n") else "")


def _linkify_bare_urls(md_text: str) -> str:
    url_re = re.compile(r"(?<!<)(?<!\()https?://[^\s>]+")

    def repl(match: re.Match[str]) -> str:
        url = match.group(0)
        trailing = ""
        while url and url[-1] in ".,);]":
            trailing = url[-1] + trailing
            url = url[:-1]
        return f"<{url}>{trailing}"

    return url_re.sub(repl, md_text)


def build() -> None:
    repo_root = Path(__file__).resolve().parents[2]
    src = repo_root / "blogs/aws-reinvent-2025/reinvent_recap.md"
    out = repo_root / "smiglan.github.io/notes/aws-reinvent-2025/reinvent-2025-recap.html"

    md_text = src.read_text(encoding="utf-8")
    md_text = _fix_reference_lists(md_text)
    md_text = _linkify_bare_urls(md_text)

    html_body = markdown.markdown(
        md_text,
        extensions=["extra", "admonition", "sane_lists", "smarty", "toc"],
        extension_configs={"toc": {"permalink": True}},
    )

    title = "AWS re:Invent 2025 Recap"
    for line in md_text.splitlines():
        if line.startswith("# "):
            title = line[2:].strip()
            break

    description = (
        "A technical recap of AWS re:Invent 2025: Agent Core, retrieval tiering (OpenSearch + S3 Vectors), "
        "Nova Act, and what this means for building production agents."
    )

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(
        f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title} | Shubham Miglani</title>
  <meta name="description" content="{description}">

  <meta property="og:type" content="article">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://smiglan.github.io/notes/aws-reinvent-2025/reinvent-2025-recap.html">

  <link rel="canonical" href="https://smiglan.github.io/notes/aws-reinvent-2025/reinvent-2025-recap.html">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Source+Serif+4:opsz,wght@8..60,500;8..60,600&display=swap" rel="stylesheet">

  <link rel="stylesheet" href="/css/post.css">
</head>
<body>
  <main class="post">
    <header class="post-header">
      <a class="home" href="/">&larr; Home</a>
      <h1>{title}</h1>
      <p class="subtitle">Published notes and synthesis from AWS re:Invent 2025.</p>
    </header>

    <article class="post-body">
{html_body}
    </article>

    <footer class="post-footer">
      <p>Back to <a href="/">smiglan.github.io</a>.</p>
    </footer>
  </main>
</body>
</html>
""",
        encoding="utf-8",
    )


if __name__ == "__main__":
    build()
