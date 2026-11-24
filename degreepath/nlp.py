"""NLP pipeline: preprocessing + skill extraction from free text.

Approach (documented for the team): normalization, tokenization, stopword
removal, then alias matching against the skill taxonomy with word-boundary
rules, longest-alias-first. No paid APIs, no external models.
"""
import re
import unicodedata

from .skills_data import STOPWORDS

_TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9+#.\-]*|[؀-ۿ]+")
_WORD_BOUNDARY = r"(?<![\w+#.]){}(?![\w+#.])"


def normalize(text):
    """Lowercase, strip diacritics/punctuation noise, collapse whitespace."""
    text = unicodedata.normalize("NFKC", text or "")
    text = text.lower()
    # Normalize Arabic letter variants
    text = text.replace("أ", "ا").replace("إ", "ا").replace("آ", "ا")
    text = text.replace("ى", "ي").replace("ة", "ه")
    # A period separates words unless it sits inside a token (node.js, react.js)
    text = re.sub(r"(?<![A-Za-z0-9])\.|\.(?![A-Za-z0-9])", " ", text)
    text = re.sub(r"[,;:!؟?'\"()\[\]{}<>«»/\\|*_~`$%^&=+]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def tokenize(text):
    return _TOKEN_RE.findall(normalize(text))


def remove_stopwords(tokens):
    return [t for t in tokens if t not in STOPWORDS and len(t) > 1]


def preprocess(text):
    """Full preprocessing: returns cleaned tokens (person 9's stage)."""
    return remove_stopwords(tokenize(text))


def build_alias_index(db):
    """Return [(normalized_alias, skill_id)] sorted longest alias first."""
    rows = db.execute("SELECT alias, skill_id FROM skill_aliases").fetchall()
    pairs = [(normalize(r["alias"]), r["skill_id"]) for r in rows]
    pairs = [(a, s) for a, s in pairs if a]
    pairs.sort(key=lambda p: -len(p[0]))
    compiled = [(re.compile(_WORD_BOUNDARY.format(re.escape(a))), s) for a, s in pairs]
    return compiled


def extract_skills(text, alias_index):
    """Extract canonical skill IDs mentioned in free text."""
    norm = normalize(text)
    found = []
    seen = set()
    for pattern, skill_id in alias_index:
        if skill_id not in seen and pattern.search(norm):
            seen.add(skill_id)
            found.append(skill_id)
    return found


def extract_skills_named(text, db):
    """Extract skills and return them as [{id, name, name_ar, category}]."""
    alias_index = build_alias_index(db)
    ids = extract_skills(text, alias_index)
    if not ids:
        return []
    q = "SELECT id, name, name_ar, category FROM skills WHERE id IN ({})".format(
        ",".join("?" * len(ids))
    )
    rows = db.execute(q, ids).fetchall()
    by_id = {r["id"]: dict(r) for r in rows}
    return [by_id[i] for i in ids if i in by_id]
