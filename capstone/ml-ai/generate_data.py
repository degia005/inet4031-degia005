#!/usr/bin/env python3
"""Generate a labeled, synthetic incident dataset for the ML & AI capstone track.

Every row is made up. Titles are built from templates, and the category and
severity come from rules I wrote (which subject the title is about, and how bad
the problem words sound). Some rows get extra words or a "noisy" label on
purpose so the model can't just memorize keywords.

Same seed in = same file out, byte for byte.

Usage: python3 generate_data.py --seed 4031 --rows 6000 --out data/incidents.csv
"""
import argparse
import csv
import random
from datetime import datetime, timedelta

# What the incident is about -> category
SUBJECTS = {
    "Network": ["wifi", "network", "internet", "VPN", "router", "network switch",
                "connection", "hotspot"],
    "Devices": ["handheld scanner", "label printer", "barcode scanner", "tablet",
                "dock terminal", "printer", "receipt printer"],
    "Access": ["login", "password", "account", "badge reader", "MFA code",
               "permissions", "SSO sign-in"],
    "Vehicles": ["truck", "forklift", "delivery van", "trailer", "reefer unit",
                 "lift gate", "pallet jack"],
    "Shipments": ["shipment", "order", "pallet count", "manifest", "delivery",
                  "tracking number", "pickup"],
}

# How bad it sounds -> severity
PROBLEMS = {
    "Critical": ["is down for the whole depot", "outage, nobody can work",
                 "completely down at every dock", "down and trucks can't leave",
                 "failed for all dispatchers", "stopped working site wide"],
    "High": ["is not working", "keeps failing", "won't connect", "is broken",
             "failing for several drivers", "stopped working on one dock"],
    "Medium": ["is slow", "drops sometimes", "has intermittent errors",
               "works but is laggy", "needs a restart a few times a day",
               "is acting up"],
    "Low": ["question", "small display glitch", "request to update",
            "how do I reset it", "minor typo", "nice to have change"],
}

# Rough share of each severity (most incidents are not emergencies)
SEVERITY_WEIGHTS = {"Low": 30, "Medium": 35, "High": 25, "Critical": 10}
SEVERITY_ORDER = ["Low", "Medium", "High", "Critical"]

# Made-up places only, no real names
PLACES = ["North depot", "South depot", "East yard", "West yard", "Dock 4",
          "Dock 9", "Cross-dock", "Night shift", "Depot 7", "Main office"]

TEMPLATES = [
    "{subject} {problem}",
    "{place}: {subject} {problem}",
    "{subject} {problem} ({place})",
    "Driver reports {subject} {problem}",
]
LOW_TEMPLATES = [
    "{problem} about the {subject}",
    "{place}: {problem} for the {subject}",
    "{subject}: {problem}",
]

NOISE_RATE = 0.07      # share of rows whose label is changed on purpose
MIXED_RATE = 0.12      # share of titles that also mention a second subject


def make_row(rng, row_id, start):
    category = rng.choice(sorted(SUBJECTS))
    severity = rng.choices(list(SEVERITY_WEIGHTS), weights=list(SEVERITY_WEIGHTS.values()))[0]
    subject = rng.choice(SUBJECTS[category])
    problem = rng.choice(PROBLEMS[severity])
    templates = LOW_TEMPLATES if severity == "Low" else TEMPLATES
    title = rng.choice(templates).format(subject=subject, problem=problem, place=rng.choice(PLACES))

    # Harder titles: mention a second subject, like "scanner can't reach wifi"
    if rng.random() < MIXED_RATE:
        other = rng.choice([c for c in SUBJECTS if c != category])
        title += f", maybe the {rng.choice(SUBJECTS[other])} too"

    # Noisy labels: real people mislabel things sometimes
    if rng.random() < NOISE_RATE:
        category = rng.choice([c for c in SUBJECTS if c != category])
    if rng.random() < NOISE_RATE:
        i = SEVERITY_ORDER.index(severity)
        severity = SEVERITY_ORDER[max(0, min(3, i + rng.choice([-1, 1])))]

    # Spread over 90 days, busier during day shifts
    day = rng.randrange(90)
    hour = rng.choices(range(24), weights=[1] * 6 + [4] * 12 + [2] * 6)[0]
    created = start + timedelta(days=day, hours=hour, minutes=rng.randrange(60))
    title = title[0].upper() + title[1:]
    return [row_id, title, category, severity, created.strftime("%Y-%m-%d %H:%M")]


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--seed", type=int, default=4031)
    parser.add_argument("--rows", type=int, default=6000)
    parser.add_argument("--out", default="data/incidents.csv")
    args = parser.parse_args()

    rng = random.Random(args.seed)
    start = datetime(2026, 8, 1)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f, lineterminator="\n")
        writer.writerow(["id", "title", "category", "severity", "created_at"])
        for row_id in range(1, args.rows + 1):
            writer.writerow(make_row(rng, row_id, start))
    print(f"wrote {args.rows} rows to {args.out} (seed {args.seed})")


if __name__ == "__main__":
    main()
