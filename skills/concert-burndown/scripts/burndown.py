#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "matplotlib>=3.8",
# ]
# ///
"""
Concert burndown chart generator.

Reads:
  <burndown-config.json> — passed as first positional arg
  <csv_path> from config — daily sales-log.csv

Writes:
  <output_png> — latest chart
  <output_png parent>/<latest date>.png — dated copy
  stdout — text summary

Usage:
  burndown.py <path-to-burndown-config.json> [--text-only]
"""
from __future__ import annotations
import csv
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path


def parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def load_log(csv_path: Path):
    rows = []
    with csv_path.open() as f:
        for r in csv.DictReader(f):
            rows.append(
                {
                    "date": parse_date(r["date"]),
                    "paid": int(r["paid_tickets"]),
                    "revenue": float(r["revenue_eur"]),
                    "notes": r.get("notes", ""),
                }
            )
    rows.sort(key=lambda x: x["date"])
    return rows


def build_summary(rows, cfg) -> str:
    today = rows[-1]["date"]
    launch = parse_date(cfg["launch_date"])
    event = parse_date(cfg["event_date"])
    days_total = (event - launch).days
    days_elapsed = (today - launch).days
    days_left = (event - today).days

    paid = rows[-1]["paid"]
    revenue = rows[-1]["revenue"]
    min_target = cfg["min_target_paid"]
    stretch = cfg["stretch_target_paid"]

    ideal_pace = min_target / days_total if days_total else 0
    expected_today = ideal_pace * days_elapsed
    pace_ratio = paid / expected_today if expected_today else 0
    needed_per_day = (min_target - paid) / max(days_left, 1)

    if len(rows) >= 2:
        prev = rows[-2]
        delta_t = (today - prev["date"]).days or 1
        recent_pace = (paid - prev["paid"]) / delta_t
    else:
        recent_pace = 0

    projected_at_recent = paid + recent_pace * days_left
    recent_window = (today - rows[-2]["date"]).days if len(rows) >= 2 else 0

    lines = [
        f"{cfg['event_name']} burndown — {today.isoformat()} (T-{days_left} days)",
        f"  Sold: {paid} paid · €{revenue:.2f} revenue",
        f"  Min target: {min_target} ({paid/min_target*100:.0f}%) · Stretch: {stretch} ({paid/stretch*100:.0f}%)",
        f"  Ideal pace to min: {ideal_pace:.1f}/day · expected today: {expected_today:.0f} · actual/expected: {pace_ratio:.2f}x",
        f"  Recent pace ({recent_window}d): {recent_pace:.1f}/day · projected at min: {projected_at_recent:.0f}",
        f"  Needed pace from today: {needed_per_day:.1f}/day to hit min target",
    ]
    return "\n".join(lines)


def render_chart(rows, cfg, out_png: Path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.dates import DateFormatter, DayLocator

    launch = parse_date(cfg["launch_date"])
    event = parse_date(cfg["event_date"])
    today = rows[-1]["date"]
    min_target = cfg["min_target_paid"]
    stretch = cfg["stretch_target_paid"]

    fig, ax = plt.subplots(figsize=(11, 6.5))
    fig.patch.set_facecolor("#0e1116")
    ax.set_facecolor("#0e1116")

    ax.plot(
        [launch, event], [0, min_target],
        color="#5eead4", linewidth=1.6, linestyle="--",
        label=f"Ideal → min target ({min_target})", alpha=0.85,
    )
    ax.plot(
        [launch, event], [0, stretch],
        color="#a78bfa", linewidth=1.2, linestyle=":",
        label=f"Ideal → stretch ({stretch})", alpha=0.7,
    )

    tier_dates = [launch] + [parse_date(t["date"]) for t in cfg["tier_milestones"]]
    tier_targets = [0] + [t["cumulative_target"] for t in cfg["tier_milestones"]]
    ax.plot(
        tier_dates, tier_targets,
        color="#f59e0b", linewidth=1.4, linestyle="-",
        marker="o", markersize=5, alpha=0.55,
        label="Tier milestones",
    )

    xs = [r["date"] for r in rows]
    ys = [r["paid"] for r in rows]
    ax.plot(
        xs, ys,
        color="#ef4444", linewidth=2.6,
        marker="o", markersize=7,
        label=f"Actual ({ys[-1]} paid)", zorder=5,
    )

    ax.annotate(
        f"{ys[-1]}", xy=(xs[-1], ys[-1]),
        xytext=(8, 10), textcoords="offset points",
        color="#ef4444", fontsize=11, fontweight="bold",
    )

    ax.axvline(today, color="#ffffff", linewidth=0.6, linestyle=":", alpha=0.4)
    ax.axvline(event, color="#ffffff", linewidth=0.6, linestyle=":", alpha=0.4)

    ax.set_xlim(launch - timedelta(days=1), event + timedelta(days=1))
    ax.set_ylim(0, stretch * 1.05)
    ax.xaxis.set_major_formatter(DateFormatter("%b %d"))
    ax.xaxis.set_major_locator(DayLocator(interval=3))
    plt.setp(ax.get_xticklabels(), rotation=30, ha="right", color="#cbd5e1")
    plt.setp(ax.get_yticklabels(), color="#cbd5e1")
    ax.tick_params(colors="#cbd5e1")
    for spine in ax.spines.values():
        spine.set_color("#334155")
    ax.grid(True, color="#1e293b", linewidth=0.6)

    days_left = (event - today).days
    paid = ys[-1]
    revenue = rows[-1]["revenue"]
    title = f"{cfg['event_name']} burndown · {today.isoformat()} · T-{days_left}d"
    ax.set_title(title, color="#f8fafc", fontsize=14, pad=14, fontweight="bold")
    ax.set_xlabel("Date", color="#cbd5e1")
    ax.set_ylabel("Cumulative paid tickets", color="#cbd5e1")

    subtitle = f"{paid} paid · €{revenue:.0f} revenue · min {min_target} · stretch {stretch}"
    ax.text(
        0.01, 0.97, subtitle,
        transform=ax.transAxes,
        color="#94a3b8", fontsize=10, va="top",
    )

    ax.legend(
        loc="upper left", bbox_to_anchor=(0.01, 0.93),
        facecolor="#0e1116", edgecolor="#334155",
        labelcolor="#e2e8f0", fontsize=9, framealpha=0.9,
    )

    out_png.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(out_png, dpi=140, facecolor=fig.get_facecolor())
    plt.close(fig)


def main():
    if len(sys.argv) < 2:
        print("Usage: burndown.py <path-to-config.json> [--text-only]", file=sys.stderr)
        sys.exit(1)

    config_path = Path(sys.argv[1]).expanduser().resolve()
    cfg = json.loads(config_path.read_text())

    raw_csv = Path(cfg["csv_path"]).expanduser()
    if raw_csv.is_absolute():
        csv_path = raw_csv
    else:
        # Try relative to config file first, then relative to CWD
        candidate = config_path.parent / raw_csv
        csv_path = candidate if candidate.exists() else Path.cwd() / raw_csv
        if not csv_path.exists():
            print(f"Error: csv_path not found. Tried: {candidate} and {Path.cwd() / raw_csv}", file=sys.stderr)
            sys.exit(1)

    text_only = "--text-only" in sys.argv
    rows = load_log(csv_path)
    print(build_summary(rows, cfg))
    if text_only:
        return

    out_latest = Path(cfg["output_png"]).expanduser()
    out_dated = out_latest.parent / f"{rows[-1]['date'].isoformat()}.png"
    render_chart(rows, cfg, out_latest)
    render_chart(rows, cfg, out_dated)
    print(f"\nChart: {out_latest}")
    print(f"Dated: {out_dated}")


if __name__ == "__main__":
    main()
