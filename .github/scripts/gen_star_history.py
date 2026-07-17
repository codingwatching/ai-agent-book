#!/usr/bin/env python3
"""Generate a self-hosted star-history chart for this repository.

Fetches stargazer timestamps from the GitHub API and renders a cumulative
star-count-over-time line chart as an SVG that GitHub can display inline in
the README (no external service at render time, so it never breaks).

Usage:
    python gen_star_history.py <owner/repo> [output.svg]

Environment:
    GITHUB_TOKEN  Optional. Raises the API rate limit from 60 to 5000 req/h
                  and is required for repos with many stargazers.
"""

import os
import sys
import json
import datetime as dt
from urllib.request import Request, urlopen
from urllib.error import HTTPError

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Neutral palette that reads on both GitHub light and dark themes.
LINE_COLOR = "#2f81f7"   # GitHub accent blue
FILL_COLOR = "#2f81f7"
GRID_COLOR = "#8b949e"
TEXT_COLOR = "#8b949e"


def gh_get(url, token):
    headers = {
        "Accept": "application/vnd.github.star+json",
        "User-Agent": "star-history-generator",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = Request(url, headers=headers)
    resp = urlopen(req, timeout=30)
    body = json.loads(resp.read().decode("utf-8"))
    link = resp.headers.get("Link", "")
    next_url = None
    for part in link.split(","):
        if 'rel="next"' in part:
            next_url = part[part.find("<") + 1 : part.find(">")]
    return body, next_url


def fetch_starred_at(repo, token):
    """Return a sorted list of datetimes when each star was added."""
    url = f"https://api.github.com/repos/{repo}/stargazers?per_page=100"
    times = []
    while url:
        try:
            page, url = gh_get(url, token)
        except HTTPError as e:
            print(f"GitHub API error {e.code}: {e.reason}", file=sys.stderr)
            if e.code in (403, 401):
                print("Hint: set GITHUB_TOKEN to raise the rate limit.", file=sys.stderr)
            raise
        for entry in page:
            ts = entry.get("starred_at")
            if ts:
                times.append(dt.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ"))
    times.sort()
    return times


def render(repo, times, out_path):
    fig, ax = plt.subplots(figsize=(8, 4), dpi=100)
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)

    if times:
        counts = list(range(1, len(times) + 1))
        # Add a leading point so the line starts at zero, and a trailing point
        # at "now" so it extends to today.
        now = dt.datetime.utcnow()
        xs = [times[0]] + times + [now]
        ys = [0] + counts + [counts[-1]]
        ax.plot(xs, ys, color=LINE_COLOR, linewidth=2.2, solid_capstyle="round")
        ax.fill_between(xs, ys, color=FILL_COLOR, alpha=0.08)
        ax.set_ylim(bottom=0)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m"))
    else:
        ax.text(0.5, 0.5, "No stars yet", ha="center", va="center",
                color=TEXT_COLOR, transform=ax.transAxes)

    ax.set_title(f"Star History — {repo}", color=TEXT_COLOR, fontsize=13, pad=12)
    ax.set_ylabel("GitHub Stars", color=TEXT_COLOR)
    ax.tick_params(colors=TEXT_COLOR)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for spine in ("left", "bottom"):
        ax.spines[spine].set_color(GRID_COLOR)
    ax.grid(True, color=GRID_COLOR, alpha=0.2, linewidth=0.8)
    fig.autofmt_xdate()
    fig.tight_layout()

    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fig.savefig(out_path, format="svg", transparent=True)
    plt.close(fig)
    print(f"Wrote {out_path} ({len(times)} stars)")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    repo = sys.argv[1]
    out_path = sys.argv[2] if len(sys.argv) > 2 else "assets/star-history.svg"
    token = os.environ.get("GITHUB_TOKEN", "")
    times = fetch_starred_at(repo, token)
    render(repo, times, out_path)


if __name__ == "__main__":
    main()
