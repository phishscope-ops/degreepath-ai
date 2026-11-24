"""NLP tests: preprocessing and skill extraction (persons 9-11 acceptance)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from degreepath import create_app
from degreepath.db import get_db
from degreepath import nlp


@pytest.fixture()
def app(tmp_path):
    app = create_app({"DATABASE": str(tmp_path / "test.sqlite3"), "TESTING": True})
    yield app


def test_preprocess_tokenizes_and_removes_stopwords():
    tokens = nlp.preprocess("The course covers Python and SQL for students")
    assert "python" in tokens
    assert "sql" in tokens
    assert "the" not in tokens
    assert "and" not in tokens


def test_normalize_arabic_variants():
    # ة -> ه, أ -> ا
    assert nlp.normalize("البرمجة") == nlp.normalize("البرمجه")


def test_extract_from_english_course_description(app):
    with app.app_context():
        db = get_db()
        skills = nlp.extract_skills_named(
            "Python Programming and Statistical Analysis", db
        )
        names = {s["name"] for s in skills}
        assert "Python" in names
        assert "Statistics" in names
        assert "Data Analysis" in names


def test_extract_from_job_description(app):
    with app.app_context():
        db = get_db()
        skills = nlp.extract_skills_named(
            "We need a data analyst with strong SQL, Excel, Power BI and data visualization skills.",
            db,
        )
        names = {s["name"] for s in skills}
        assert {"SQL", "Excel", "Power BI", "Data Visualization"} <= names


def test_extract_from_arabic_text(app):
    with app.app_context():
        db = get_db()
        skills = nlp.extract_skills_named(
            "مادة تحليل البيانات بتغطي الإحصاء واستخدام بايثون وقواعد البيانات", db
        )
        names = {s["name"] for s in skills}
        assert "Data Analysis" in names
        assert "Python" in names


def test_no_false_positive_on_unrelated_text(app):
    with app.app_context():
        db = get_db()
        skills = nlp.extract_skills_named("I had lunch with my friend yesterday.", db)
        assert skills == []
