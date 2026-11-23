#!/usr/bin/env python3
"""Train and evaluate the category and severity models, and save metrics.json.

- Splits the dataset 80/20 with a fixed random_state (the 20% is never trained on)
- Baseline: DummyClassifier that always predicts the most common label
- Model: TF-IDF on the title + logistic regression, one pipeline per target
- Writes metrics.json (baseline and model, accuracy and macro F1) and the
  two model files with joblib

Usage: python3 train.py --data data/incidents.csv --models models --metrics metrics.json
"""
import argparse
import csv
import hashlib
import json
import os

import joblib
from sklearn.dummy import DummyClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

SEED = 4031
TARGETS = ["category", "severity"]
SEVERITY_TARGET = 0.80


def scores(y_true, y_pred):
    return {"accuracy": round(accuracy_score(y_true, y_pred), 4),
            "macro_f1": round(f1_score(y_true, y_pred, average="macro"), 4)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default="data/incidents.csv")
    parser.add_argument("--models", default="models")
    parser.add_argument("--metrics", default="metrics.json")
    args = parser.parse_args()

    with open(args.data, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    with open(args.data, "rb") as f:
        data_hash = hashlib.sha256(f.read()).hexdigest()

    titles = [r["title"] for r in rows]
    train_idx, test_idx = train_test_split(
        list(range(len(rows))), test_size=0.2, random_state=SEED,
        stratify=[r["severity"] for r in rows])

    metrics = {
        "dataset": {"file": args.data, "rows": len(rows), "sha256": data_hash},
        "split": {"train": len(train_idx), "test": len(test_idx),
                  "test_size": 0.2, "random_state": SEED},
        "baseline": {}, "model": {},
    }
    os.makedirs(args.models, exist_ok=True)

    for target in TARGETS:
        labels = [r[target] for r in rows]
        x_train = [titles[i] for i in train_idx]
        x_test = [titles[i] for i in test_idx]
        y_train = [labels[i] for i in train_idx]
        y_test = [labels[i] for i in test_idx]

        baseline = DummyClassifier(strategy="most_frequent").fit(x_train, y_train)
        metrics["baseline"][target] = scores(y_test, baseline.predict(x_test))
        metrics["baseline"][target]["always_predicts"] = str(baseline.predict(x_test[:1])[0])

        model = Pipeline([
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2)),
            ("clf", LogisticRegression(max_iter=1000, random_state=SEED)),
        ]).fit(x_train, y_train)
        predicted = model.predict(x_test)
        metrics["model"][target] = scores(y_test, predicted)
        joblib.dump(model, os.path.join(args.models, f"{target}.joblib"))

        print(f"\n== {target}: baseline vs model (held-out test set, {len(y_test)} rows) ==")
        print(f"baseline accuracy {metrics['baseline'][target]['accuracy']:.3f}  "
              f"macro F1 {metrics['baseline'][target]['macro_f1']:.3f}  "
              f"(always says {metrics['baseline'][target]['always_predicts']})")
        print(f"model    accuracy {metrics['model'][target]['accuracy']:.3f}  "
              f"macro F1 {metrics['model'][target]['macro_f1']:.3f}")
        print(classification_report(y_test, predicted, digits=3))

    acc = metrics["model"]["severity"]["accuracy"]
    metrics["severity_accuracy_target"] = SEVERITY_TARGET
    metrics["meets_severity_target"] = acc >= SEVERITY_TARGET
    with open(args.metrics, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
        f.write("\n")
    print(f"severity accuracy {acc:.3f} (target {SEVERITY_TARGET}) -> "
          f"{'MEETS' if acc >= SEVERITY_TARGET else 'BELOW'} target; wrote {args.metrics}")


if __name__ == "__main__":
    main()
