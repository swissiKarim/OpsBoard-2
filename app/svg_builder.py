"""Server-side inline-SVG bar chart builder for OpsBoard.

Generates an SVG bar chart showing incident counts per day for the last N days.
No external chart library is used – all coordinates are computed here.
"""

from __future__ import annotations

from datetime import date, timedelta


def build_bar_chart(
    daily_counts: dict[str, int],
    days: int = 14,
    width: int = 560,
    height: int = 180,
    padding_left: int = 40,
    padding_right: int = 16,
    padding_top: int = 16,
    padding_bottom: int = 40,
) -> str:
    """Return an inline-SVG string for a bar chart of incidents per day.

    Parameters
    ----------
    daily_counts:
        Mapping of ISO-date string (``"YYYY-MM-DD"``) to incident count.
    days:
        Number of days to display (most recent N days ending today).
    width, height:
        Outer SVG dimensions in pixels.
    padding_*:
        Inner padding around the chart area.
    """
    today = date.today()
    labels: list[str] = []
    counts: list[int] = []
    for i in range(days - 1, -1, -1):
        d = today - timedelta(days=i)
        iso = d.isoformat()
        labels.append(d.strftime("%d"))
        counts.append(daily_counts.get(iso, 0))

    chart_w = width - padding_left - padding_right
    chart_h = height - padding_top - padding_bottom

    max_count = max(counts) if counts else 0
    # Avoid division by zero; always show at least a scale of 1
    scale = max_count if max_count > 0 else 1

    bar_total_w = chart_w / len(counts) if counts else chart_w
    bar_w = max(2, bar_total_w * 0.65)
    bar_gap = bar_total_w - bar_w

    parts: list[str] = []

    # --- SVG open tag --------------------------------------------------------
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" '
        f'aria-label="Incidents per day, last {days} days" '
        f'role="img">'
    )

    # --- Definitions (gradient) ----------------------------------------------
    parts.append(
        '<defs>'
        '<linearGradient id="bar-grad" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0%" stop-color="var(--color-accent, #4f6bed)"/>'
        '<stop offset="100%" stop-color="var(--color-accent-muted, #7b93f0)"/>'
        '</linearGradient>'
        '</defs>'
    )

    # --- Background ----------------------------------------------------------
    parts.append(
        f'<rect x="0" y="0" width="{width}" height="{height}" '
        f'fill="var(--color-surface, #fff)" rx="6"/>'
    )

    # --- Y-axis baseline -----------------------------------------------------
    baseline_y = padding_top + chart_h
    parts.append(
        f'<line x1="{padding_left}" y1="{padding_top}" '
        f'x2="{padding_left}" y2="{baseline_y}" '
        f'stroke="var(--color-border, #e2e8f0)" stroke-width="1"/>'
    )
    parts.append(
        f'<line x1="{padding_left}" y1="{baseline_y}" '
        f'x2="{padding_left + chart_w}" y2="{baseline_y}" '
        f'stroke="var(--color-border, #e2e8f0)" stroke-width="1"/>'
    )

    # --- Horizontal grid lines (3 levels) ------------------------------------
    for frac in (0.25, 0.5, 0.75, 1.0):
        gy = padding_top + chart_h - int(chart_h * frac)
        label_val = round(scale * frac)
        parts.append(
            f'<line x1="{padding_left}" y1="{gy}" '
            f'x2="{padding_left + chart_w}" y2="{gy}" '
            f'stroke="var(--color-border, #e2e8f0)" stroke-width="1" stroke-dasharray="3 3"/>'
        )
        parts.append(
            f'<text x="{padding_left - 4}" y="{gy + 4}" '
            f'text-anchor="end" font-size="9" '
            f'fill="var(--color-text-muted, #64748b)">{label_val}</text>'
        )

    # --- Bars -----------------------------------------------------------------
    for idx, (label, count) in enumerate(zip(labels, counts)):
        bar_h = int(chart_h * count / scale) if count > 0 else 0
        x = padding_left + idx * bar_total_w + bar_gap / 2
        y = baseline_y - bar_h

        # Bar rect
        parts.append(
            f'<rect '
            f'x="{x:.1f}" y="{y}" '
            f'width="{bar_w:.1f}" height="{bar_h}" '
            f'fill="url(#bar-grad)" rx="2" '
            f'data-date="{(today - timedelta(days=days - 1 - idx)).isoformat()}" '
            f'data-count="{count}">'
            f'<title>{count} incident{"s" if count != 1 else ""} on {label}</title>'
            f'</rect>'
        )

        # X-axis label (every other label to avoid crowding)
        if idx % 2 == 0 or days <= 7:
            lx = x + bar_w / 2
            parts.append(
                f'<text x="{lx:.1f}" y="{baseline_y + 14}" '
                f'text-anchor="middle" font-size="9" '
                f'fill="var(--color-text-muted, #64748b)">{label}</text>'
            )

    parts.append("</svg>")
    return "\n".join(parts)
