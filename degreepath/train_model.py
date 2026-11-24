"""Train the offline skill classifier and report honest metrics.

Run: python -m degreepath.train_model
Outputs: degreepath/model.joblib + degreepath/model_metrics.json
"""
import json
import os
import sqlite3

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.multiclass import OneVsRestClassifier
from sklearn.pipeline import FeatureUnion, Pipeline
from sklearn.preprocessing import MultiLabelBinarizer

from .ml_dataset import build_dataset

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
METRICS_PATH = os.path.join(os.path.dirname(__file__), "model_metrics.json")


def train(db_path=None):
    db = None
    if db_path is not None:
        db = sqlite3.connect(db_path)
        db.row_factory = sqlite3.Row
    texts, labels = build_dataset(db)

    all_skills = sorted({s for ls in labels for s in ls})
    mlb = MultiLabelBinarizer(classes=all_skills)
    Y = mlb.fit_transform(labels)

    X_train, X_test, Y_train, Y_test = train_test_split(
        texts, Y, test_size=0.2, random_state=42
    )

    pipe = Pipeline(
        [
            (
                "features",
                FeatureUnion(
                    [
                        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=1, lowercase=True)),
                        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)),
                    ]
                ),
            ),
            ("clf", OneVsRestClassifier(LogisticRegression(max_iter=1000, C=4.0))),
        ]
    )
    pipe.fit(X_train, Y_train)

    pred = pipe.predict(X_test)
    p_micro, r_micro, f_micro, _ = precision_recall_fscore_support(
        Y_test, pred, average="micro", zero_division=0
    )
    p_macro, r_macro, f_macro, _ = precision_recall_fscore_support(
        Y_test, pred, average="macro", zero_division=0
    )

    joblib.dump({"pipeline": pipe, "mlb": mlb}, MODEL_PATH)

    metrics = {
        "model": "OneVsRest LogisticRegression over TF-IDF (word 1-2g + char 3-5g)",
        "training_samples": len(texts),
        "test_samples": len(X_test),
        "labels": len(all_skills),
        "held_out": {
            "micro_precision": round(float(p_micro), 4),
            "micro_recall": round(float(r_micro), 4),
            "micro_f1": round(float(f_micro), 4),
            "macro_precision": round(float(p_macro), 4),
            "macro_recall": round(float(r_macro), 4),
            "macro_f1": round(float(f_macro), 4),
        },
        "note": (
            "Data is taxonomy-derived synthetic sentences plus seed catalog/job "
            "descriptions; metrics measure generalization to new phrasings of the "
            "same skill vocabulary, not to an arbitrary unseen domain."
        ),
    }
    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print(json.dumps(metrics, ensure_ascii=False, indent=2))
    return metrics


if __name__ == "__main__":
    db_path = os.environ.get("DEGREEPATH_DB")
    if db_path is None:
        # default: project instance db so catalog/job silver labels are included
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "degreepath.sqlite3")
        if not os.path.exists(db_path):
            db_path = None
    train(db_path)
