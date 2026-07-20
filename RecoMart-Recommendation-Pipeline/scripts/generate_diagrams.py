"""
Generate architecture and DAG flow diagrams for the RecoMart pipeline.

Uses matplotlib only (no external Graphviz binary required) so it runs
reliably in any environment with the project's Python dependencies
installed.

Outputs:
    docs/diagrams/architecture_diagram.png
    docs/diagrams/dag_flow_diagram.png
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.lines import Line2D

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "docs" / "diagrams"


def _box(ax, xy, width, height, text, facecolor, edgecolor="#333333", fontsize=10, fontweight="normal", textcolor="#111111"):
    x, y = xy
    box = FancyBboxPatch(
        (x, y), width, height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        linewidth=1.4,
        edgecolor=edgecolor,
        facecolor=facecolor,
    )
    ax.add_patch(box)
    ax.text(
        x + width / 2, y + height / 2, text,
        ha="center", va="center",
        fontsize=fontsize, fontweight=fontweight, color=textcolor,
        wrap=True,
    )
    return box


def _arrow(ax, start, end, color="#444444"):
    arrow = FancyArrowPatch(
        start, end,
        arrowstyle="-|>", mutation_scale=16,
        linewidth=1.6, color=color, shrinkA=2, shrinkB=2,
    )
    ax.add_patch(arrow)


def generate_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis("off")
    ax.set_title(
        "RecoMart Recommendation Pipeline — System Architecture",
        fontsize=15, fontweight="bold", pad=14,
    )

    layers = [
        {
            "label": "ORCHESTRATION LAYER\nApache Airflow DAG (recom_pipeline)\nWeekly schedule • retries • task groups",
            "y": 13.2, "color": "#dbe9ff",
        },
        {
            "label": "DATA SOURCES\nMovieLens CSVs (movies, ratings, links, tags)  •  DummyJSON REST API",
            "y": 11.6, "color": "#fff2cc",
        },
        {
            "label": "MEMBER 1 — INGESTION\nsrc/ingestion  →  data/raw/{csv,api}/{dataset}/{timestamp}/\nMetadata: data/metadata/ingestion_metadata.json",
            "y": 10.0, "color": "#d9ead3",
        },
        {
            "label": "MEMBER 2 — VALIDATION & PREPARATION\nsrc/validation, src/preparation  →  schema/missing/duplicate/type checks\nQuality reports: data/reports/DataQualityReport_*.pdf  →  data/processed/",
            "y": 8.2, "color": "#d0e0e3",
        },
        {
            "label": "MEMBER 3 — FEATURE ENGINEERING & FEATURE STORE\nsrc/features  →  user/item/interaction features (data/features/)\nVersioned registry: feature_store/registry.json (schema.sql, features_metadata_v1.json)",
            "y": 6.2, "color": "#ead1dc",
        },
        {
            "label": "MEMBER 4 — MODEL TRAINING & EVALUATION\nsrc/models/train.py — TruncatedSVD collaborative filtering  →  models/svd_recommender.pkl\nsrc/models/__init__.py — train_model() runs the same SVD model (DAG default)\nBaseline LinearRegression kept as an explicit model_type=\"baseline\" fallback\nMetrics: reports/evaluation_report.md (Precision@10, Recall@10, NDCG@10)",
            "y": 3.9, "color": "#f4cccc",
        },
        {
            "label": "MEMBER 5 — MONITORING, ALERTING & DOCS\nairflow/monitoring.py (structured JSON logs, task callbacks)\nairflow/alerts.py (email/Slack)  •  docs/ + reports/ documentation",
            "y": 1.9, "color": "#fce5cd",
        },
        {
            "label": "VERSIONING & TRACKING\nDVC (per-file data/processed/*.csv.dvc, local remote)  •  MLflow experiment tracking (mlruns/)",
            "y": 0.2, "color": "#e2e2e2",
        },
    ]

    box_h = 1.15
    box_w = 9.0
    box_x = 0.5

    for i, layer in enumerate(layers):
        _box(ax, (box_x, layer["y"]), box_w, box_h, layer["label"], layer["color"], fontsize=9.3)
        if i < len(layers) - 1:
            top_y = layer["y"]
            bottom_y = layers[i + 1]["y"] + box_h
            _arrow(ax, (box_x + box_w / 2, top_y), (box_x + box_w / 2, bottom_y))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "architecture_diagram.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return out_path


def generate_dag_flow_diagram():
    # Mirrors the actual linear task dependency chain in
    # airflow/dags/recom_pipeline.py:
    #   start >> ingestion_layer >> validation_layer >> preparation_layer
    #   >> engineer_features >> setup_feature_store >> train_model >> end
    fig, ax = plt.subplots(figsize=(16, 4.2))
    ax.set_xlim(0, 16)
    ax.set_ylim(0, 3.2)
    ax.axis("off")
    ax.set_title(
        "Airflow DAG — recom_pipeline Task Flow",
        fontsize=15, fontweight="bold", pad=14,
    )

    node_defs = [
        ("start", "pipeline_start", "#cfe2f3"),
        ("ingest", "ingestion_layer\ningest_data", "#d9ead3"),
        ("validate", "validation_layer\nvalidate_data", "#d0e0e3"),
        ("prepare", "preparation_layer\nprepare_data", "#d0e0e3"),
        ("engineer", "feature_layer\nengineer_features", "#ead1dc"),
        ("fstore", "feature_layer\nsetup_feature_store", "#ead1dc"),
        ("train", "model_layer\ntrain_model", "#f4cccc"),
        ("end", "pipeline_end", "#cfe2f3"),
    ]

    n = len(node_defs)
    box_w, box_h, gap = 1.7, 1.1, 0.28
    total_w = n * box_w + (n - 1) * gap
    start_x = (16 - total_w) / 2
    y = 1.4

    nodes = []
    for i, (node_id, label, color) in enumerate(node_defs):
        x = start_x + i * (box_w + gap)
        nodes.append({"id": node_id, "x": x, "y": y, "w": box_w, "h": box_h})
        _box(ax, (x, y), box_w, box_h, label, color, fontsize=8.6)

    for a, b in zip(nodes[:-1], nodes[1:]):
        start_pt = (a["x"] + a["w"], a["y"] + a["h"] / 2)
        end_pt = (b["x"], b["y"] + b["h"] / 2)
        _arrow(ax, start_pt, end_pt)

    legend_elems = [
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#cfe2f3", markersize=14, label="Control"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#d9ead3", markersize=14, label="Ingestion (M1)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#d0e0e3", markersize=14, label="Validation/Prep (M2)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#ead1dc", markersize=14, label="Features (M3)"),
        Line2D([0], [0], marker="s", color="w", markerfacecolor="#f4cccc", markersize=14, label="Training (M4)"),
    ]
    ax.legend(handles=legend_elems, loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(0.5, -0.08), fontsize=8.5)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / "dag_flow_diagram.png"
    fig.tight_layout()
    fig.savefig(out_path, dpi=170, bbox_inches="tight")
    plt.close(fig)
    return out_path


if __name__ == "__main__":
    arch_path = generate_architecture_diagram()
    dag_path = generate_dag_flow_diagram()
    print(f"written {arch_path} exists={arch_path.exists()} size={arch_path.stat().st_size}")
    print(f"written {dag_path} exists={dag_path.exists()} size={dag_path.stat().st_size}")
