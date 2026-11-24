"""Trained-model skill extractor: loads model.joblib, predicts skills.

Runs fully offline (scikit-learn TF-IDF + logistic regression). If the model
file is missing or scikit-learn is not installed, prediction returns an empty
list and the dictionary extractor keeps working alone.
"""
import os

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.joblib")
THRESHOLD = 0.35

_model = None
_load_attempted = False


def _load():
    global _model, _load_attempted
    if _load_attempted:
        return _model
    _load_attempted = True
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        import joblib

        _model = joblib.load(MODEL_PATH)
    except Exception:
        _model = None
    return _model


def predict_skills(text, threshold=THRESHOLD):
    """Return [(skill_name, probability)] for model predictions above threshold."""
    bundle = _load()
    if bundle is None or not text or not text.strip():
        return []
    pipe = bundle["pipeline"]
    mlb = bundle["mlb"]
    try:
        probas = pipe.predict_proba([text])[0]
    except Exception:
        return []
    classes = list(mlb.classes_)
    out = [(classes[i], float(p)) for i, p in enumerate(probas) if p >= threshold]
    out.sort(key=lambda x: -x[1])
    return out


def reset():
    """Clear the cached model (used by tests)."""
    global _model, _load_attempted
    _model = None
    _load_attempted = False
