from __future__ import annotations

import textwrap
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

try:
    import matplotlib

    matplotlib.use("Agg", force=True)
    from matplotlib.backends.backend_pdf import PdfPages
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - dependency-free fallback
    PdfPages = None  # type: ignore
    plt = None  # type: ignore

from app.tools.file_tools import ensure_dir


def markdown_table(columns: list[str], rows: list[list[object]]) -> str:
    header = "| " + " | ".join(columns) + " |"
    divider = "| " + " | ".join(["---"] * len(columns)) + " |"
    body = ["| " + " | ".join(str(cell) for cell in row) + " |" for row in rows]
    return "\n".join([header, divider, *body])


def markdown_to_simple_pdf(markdown: str, output_path: str | Path, title: str) -> Path:
    target = Path(output_path)
    ensure_dir(target.parent)
    if PdfPages is None or plt is None:
        _write_minimal_pdf(target, f"{title}\n\n{markdown}")
        return target
    paragraphs = markdown.replace("\n\n", "\n").splitlines()
    pages: list[list[str]] = []
    current: list[str] = []
    for line in paragraphs:
        wrapped = textwrap.wrap(line, width=92) or [""]
        for wrapped_line in wrapped:
            current.append(wrapped_line)
            if len(current) >= 42:
                pages.append(current)
                current = []
    if current:
        pages.append(current)

    with PdfPages(target) as pdf:
        for page_no, lines in enumerate(pages, start=1):
            fig = plt.figure(figsize=(8.27, 11.69))
            fig.patch.set_facecolor("white")
            plt.axis("off")
            y = 0.96
            if page_no == 1:
                plt.text(0.5, y, title, ha="center", va="top", fontsize=15, weight="bold")
                y -= 0.05
            for line in lines:
                size = 11
                weight = "normal"
                if line.startswith("#"):
                    size = 13
                    weight = "bold"
                    line = line.lstrip("# ").strip()
                plt.text(0.06, y, line, ha="left", va="top", fontsize=size, weight=weight, family="DejaVu Sans")
                y -= 0.021
            plt.text(0.5, 0.025, f"Page {page_no}", ha="center", fontsize=9)
            pdf.savefig(fig, bbox_inches="tight")
            plt.close(fig)
    return target


def _pdf_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _write_minimal_pdf(path: Path, text: str) -> None:
    lines: list[str] = []
    for raw in text.replace("\n\n", "\n").splitlines():
        lines.extend(textwrap.wrap(raw, width=92) or [""])
    pages = [lines[idx : idx + 48] for idx in range(0, len(lines), 48)] or [[]]

    objects: list[bytes] = []
    font_id = 3 + (2 * len(pages))
    page_ids = [3 + (idx * 2) for idx in range(len(pages))]
    content_ids = [4 + (idx * 2) for idx in range(len(pages))]

    objects.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    objects.append(f"<< /Type /Pages /Kids [{kids}] /Count {len(pages)} >>".encode("ascii"))

    for page_id, content_id, page_lines in zip(page_ids, content_ids, pages):
        page = f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {font_id} 0 R >> >> /Contents {content_id} 0 R >>"
        objects.append(page.encode("ascii"))
        stream_lines = ["BT", "/F1 9 Tf", "50 800 Td", "12 TL"]
        for line in page_lines:
            stream_lines.append(f"({_pdf_escape(line[:110])}) Tj")
            stream_lines.append("T*")
        stream_lines.append("ET")
        stream = "\n".join(stream_lines).encode("latin-1", errors="replace")
        objects.append(b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream")

    objects.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for idx, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf.extend(f"{idx} 0 obj\n".encode("ascii"))
        pdf.extend(obj)
        pdf.extend(b"\nendobj\n")
    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(objects) + 1}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_start}\n%%EOF\n".encode("ascii")
    )
    path.write_bytes(bytes(pdf))
