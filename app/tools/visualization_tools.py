from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/matplotlib")

try:
    import matplotlib

    matplotlib.use("Agg", force=True)
    import matplotlib.pyplot as plt
except Exception:  # pragma: no cover - dependency-free fallback
    plt = None  # type: ignore

from app.tools.file_tools import ensure_dir, write_text


def save_mermaid(path: str | Path, title: str, code: str) -> Path:
    content = f"# {title}\n\n```mermaid\n{code.strip()}\n```\n"
    return write_text(path, content)


def save_box_diagram(
    path: str | Path,
    title: str,
    nodes: list[tuple[str, str, float, float]],
    edges: list[tuple[str, str, str]],
) -> Path:
    """Create a simple publication-friendly architecture/workflow diagram."""
    target = Path(path)
    ensure_dir(target.parent)
    node_lookup = {node_id: (label, x, y) for node_id, label, x, y in nodes}
    if plt is None:
        width, height = 900, 560
        pieces = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
            '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="7" refY="3" orient="auto"><path d="M0,0 L0,6 L7,3 z" fill="#334"/></marker></defs>',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<text x="40" y="38" font-size="20" font-weight="bold">{title}</text>',
        ]
        for src, dst, label in edges:
            _, x1, y1 = node_lookup[src]
            _, x2, y2 = node_lookup[dst]
            pieces.append(f'<line x1="{x1*width}" y1="{y1*height}" x2="{x2*width}" y2="{y2*height}" stroke="#334" stroke-width="2" marker-end="url(#arrow)"/>')
            if label:
                pieces.append(f'<text x="{((x1+x2)/2)*width}" y="{((y1+y2)/2)*height - 8}" font-size="11" fill="#334">{label}</text>')
        for node_id, label, x, y in nodes:
            cx, cy = x * width, y * height
            pieces.append(f'<rect x="{cx-76}" y="{cy-24}" rx="8" ry="8" width="152" height="48" fill="#2F6F73" stroke="#1D3F42"/>')
            pieces.append(f'<text x="{cx}" y="{cy+5}" text-anchor="middle" font-size="12" fill="white">{label}</text>')
        pieces.append("</svg>")
        return write_text(target.with_suffix(".svg"), "".join(pieces))

    fig, ax = plt.subplots(figsize=(9.5, 5.8))
    ax.set_title(title, fontsize=14, weight="bold", pad=14)
    ax.axis("off")
    colors = ["#2F6F73", "#4D6C8B", "#6A7FDB", "#88A550", "#D08C60", "#C25A5A"]
    for idx, (node_id, label, x, y) in enumerate(nodes):
        ax.text(
            x,
            y,
            label,
            ha="center",
            va="center",
            color="white",
            fontsize=9.5,
            weight="bold",
            bbox={
                "boxstyle": "round,pad=0.42,rounding_size=0.12",
                "fc": colors[idx % len(colors)],
                "ec": "#263238",
                "lw": 1.1,
            },
        )
    for src, dst, label in edges:
        _, x1, y1 = node_lookup[src]
        _, x2, y2 = node_lookup[dst]
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={"arrowstyle": "->", "lw": 1.6, "color": "#263238", "shrinkA": 22, "shrinkB": 22},
        )
        if label:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.025, label, ha="center", fontsize=8, color="#263238")
    fig.tight_layout()
    fig.savefig(target, dpi=180)
    plt.close(fig)
    return target


def save_bar_chart(path: str | Path, title: str, labels: list[str], values: list[float], ylabel: str) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    if plt is None:
        target = target.with_suffix(".svg")
        max_value = max(values) if values else 1
        bars = []
        for idx, (label, value) in enumerate(zip(labels, values)):
            width = 520 * (value / max_value)
            y = 70 + idx * 42
            bars.append(f'<text x="20" y="{y + 18}" font-size="13">{label}</text><rect x="170" y="{y}" width="{width:.1f}" height="24" fill="#2F6F73"/><text x="{180 + width:.1f}" y="{y + 18}" font-size="12">{value:g}</text>')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="760" height="{120 + len(labels) * 42}"><rect width="100%" height="100%" fill="white"/><text x="20" y="35" font-size="18" font-weight="bold">{title}</text>{"".join(bars)}<text x="170" y="{100 + len(labels) * 42}" font-size="12">{ylabel}</text></svg>'
        return write_text(target, svg)
    fig, ax = plt.subplots(figsize=(8, 4.8))
    colors = ["#2F6F73", "#D08C60", "#6A7FDB", "#88A550", "#C25A5A", "#4D6C8B"]
    ax.bar(labels, values, color=colors[: len(labels)])
    ax.set_title(title, fontsize=13, weight="bold")
    ax.set_ylabel(ylabel)
    ax.set_ylim(0, max(values) * 1.25 if values else 1)
    ax.grid(axis="y", alpha=0.25)
    plt.xticks(rotation=20, ha="right")
    fig.tight_layout()
    fig.savefig(target, dpi=180)
    plt.close(fig)
    return target


def save_radar_chart(path: str | Path, labels: list[str], values: list[float], title: str) -> Path:
    import math

    target = Path(path)
    ensure_dir(target.parent)
    if plt is None:
        target = target.with_suffix(".svg")
        rows = "".join(f'<text x="40" y="{70 + i * 28}" font-size="13">{label}: {value:g}</text>' for i, (label, value) in enumerate(zip(labels, values)))
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="280"><rect width="100%" height="100%" fill="white"/><text x="40" y="35" font-size="18" font-weight="bold">{title}</text>{rows}</svg>'
        return write_text(target, svg)
    angles = [i / float(len(labels)) * 2 * math.pi for i in range(len(labels))]
    angles += angles[:1]
    vals = values + values[:1]
    fig = plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, vals, linewidth=2, color="#2F6F73")
    ax.fill(angles, vals, color="#2F6F73", alpha=0.22)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_ylim(0, 100)
    ax.set_title(title, y=1.08, fontsize=13, weight="bold")
    fig.tight_layout()
    fig.savefig(target, dpi=180)
    plt.close(fig)
    return target


def save_conceptual_pipeline(path: str | Path) -> Path:
    target = Path(path)
    ensure_dir(target.parent)
    if plt is None:
        target = target.with_suffix(".svg")
        labels = ["Question", "Evidence", "Analysis", "Critique", "Report"]
        nodes = []
        for idx, label in enumerate(labels):
            x = 80 + idx * 150
            nodes.append(f'<circle cx="{x}" cy="120" r="45" fill="#2F6F73"/><text x="{x}" y="125" fill="white" font-size="13" text-anchor="middle">{label}</text>')
            if idx < len(labels) - 1:
                nodes.append(f'<line x1="{x + 50}" y1="120" x2="{x + 100}" y2="120" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>')
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="820" height="260"><defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L6,3 z" fill="#333"/></marker></defs><rect width="100%" height="100%" fill="white"/>{"".join(nodes)}<text x="410" y="215" text-anchor="middle" font-size="13">Grounded synthesis from question to evidence-backed report</text></svg>'
        return write_text(target, svg)
    fig, ax = plt.subplots(figsize=(9, 4.6))
    ax.axis("off")
    labels = ["Question", "Evidence", "Analysis", "Critique", "Report"]
    xs = [0.08, 0.29, 0.50, 0.71, 0.90]
    for idx, (x, label) in enumerate(zip(xs, labels)):
        ax.add_patch(plt.Circle((x, 0.55), 0.075, color=["#2F6F73", "#D08C60", "#6A7FDB", "#88A550", "#C25A5A"][idx]))
        ax.text(x, 0.55, label, color="white", ha="center", va="center", fontsize=10, weight="bold")
        if idx < len(xs) - 1:
            ax.annotate("", xy=(xs[idx + 1] - 0.09, 0.55), xytext=(x + 0.09, 0.55), arrowprops={"arrowstyle": "->", "lw": 2})
    ax.text(0.5, 0.18, "Grounded decision intelligence: every recommendation must trace back to evidence, critique, and citation checks.", ha="center", fontsize=11)
    fig.tight_layout()
    fig.savefig(target, dpi=180)
    plt.close(fig)
    return target
