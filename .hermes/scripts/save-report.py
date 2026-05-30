#!/usr/bin/env python3
"""Save SEO report data for next comparison."""
import json, os

report = {
    "timestamp": "2026-05-30T12:00:20.418493",
    "score": 100,
    "speed": {
        "Home": {"time_s": 0.065, "size_kb": 54.9},
        "Blog": {"time_s": 0.210, "size_kb": 50.7},
        "Articulo": {"time_s": 0.174, "size_kb": 25.0},
        "Provincia": {"time_s": 0.054, "size_kb": 31.0}
    },
    "sitemap": {"urls": 154, "size_kb": 23.7},
    "ssl": "ok",
    "meta": {"checked": 5, "errors": []},
    "links": {"checked": 20, "broken": []},
    "blog_coverage": {"sitemap_blog": 30, "blog_index": 29},
    "sc_totals": {
        "impressions": 466,
        "clicks": 16,
        "ctr": 16/466,
        "position": 58.8
    }
}

with open(os.path.expanduser("~/.hermes/home/seo-report-last.json"), "w") as f:
    json.dump(report, f, indent=2)

print("Report saved to seo-report-last.json")