"""Training data generation for the skill classifier.

Sources (all project-owned, free, offline):
1. Synthetic sentences built from the skill taxonomy aliases (gold labels by
   construction): each alias appears in several English and Arabic templates,
   alone and in combinations of 2-3 skills.
2. The seeded course catalog descriptions and job descriptions, labeled by the
   dictionary extractor (silver labels).

This is documented in the README: the model learns the taxonomy's vocabulary,
so its held-out metrics measure generalization to new phrasings of the same
skills, not to an arbitrary unseen domain.
"""
import random

from .skills_data import SKILLS

EN_TEMPLATES = [
    "This course covers {s}.",
    "Students will learn {s}.",
    "Introduction to {s}.",
    "An advanced course in {s}.",
    "The student studied {s} last semester.",
    "Topics include {s} and practical exercises.",
    "We are looking for someone with strong {s} skills.",
    "Experience with {s} is required.",
    "Hands-on practice in {s}.",
    "{s} fundamentals and applications.",
    "By the end of the course you will master {s}.",
    "The exam focuses on {s}.",
]

AR_TEMPLATES = [
    "مادة {s}.",
    "المادة بتغطي {s}.",
    "الطالب درس {s} الترم ده.",
    "مقرر يهدف إلى تعليم {s}.",
    "يتضمن المقرر {s} وتطبيقات عملية.",
    "مطلوب خبرة في {s}.",
    "الوظيفة دي محتاجة {s}.",
    "كورس عملي في {s}.",
]

COMBO_TEMPLATES_EN = [
    "This course covers {s1}, {s2} and {s3}.",
    "Students will learn {s1} and {s2}.",
    "Experience with {s1}, {s2} is a plus.",
    "Topics include {s1}, {s2}, and hands-on {s3}.",
]

COMBO_TEMPLATES_AR = [
    "المادة بتغطي {s1} و {s2}.",
    "مقرر في {s1} و {s2} و {s3}.",
    "مطلوب {s1} و {s2} للوظيفة دي.",
]

NEGATIVES = [
    "The student had lunch with friends after the exam.",
    "الطالب راح الجامعة الصبح بدري.",
    "This semester has eight weeks of lectures and two weeks of exams.",
    "المحاضرة اتأجلت لبكرة.",
    "He forgot his umbrella at the library yesterday.",
    "مواعيد التسجيل من السبت للخميس.",
    "The library opens at nine in the morning.",
]


def build_dataset(db=None):
    """Return (texts, labels) where labels are sets of canonical skill names."""
    rng = random.Random(42)
    samples = []  # (text, set(skill names))

    for name, name_ar, category, aliases in SKILLS:
        terms = list(dict.fromkeys([name, name_ar] + [a for a in aliases if len(a) > 2]))
        terms = [t for t in terms if t.strip()]
        if not terms:
            continue
        for tpl in EN_TEMPLATES:
            for term in rng.sample(terms, min(3, len(terms))):
                samples.append((tpl.format(s=term), {name}))
        for tpl in AR_TEMPLATES:
            for term in rng.sample(terms, min(2, len(terms))):
                samples.append((tpl.format(s=term), {name}))

    names = [s[0] for s in SKILLS]
    ar_names = {s[0]: s[1] for s in SKILLS}
    for _ in range(400):
        picked = rng.sample(names, 3)
        tpl = rng.choice(COMBO_TEMPLATES_EN)
        samples.append((tpl.format(s1=picked[0], s2=picked[1], s3=picked[2]), set(picked)))
    for _ in range(250):
        picked = rng.sample(names, 3)
        tpl = rng.choice(COMBO_TEMPLATES_AR)
        samples.append(
            (
                tpl.format(
                    s1=ar_names[picked[0]] or picked[0],
                    s2=ar_names[picked[1]] or picked[1],
                    s3=ar_names[picked[2]] or picked[2],
                ),
                set(picked),
            )
        )

    for neg in NEGATIVES:
        samples.append((neg, set()))

    if db is not None:
        from .nlp import extract_skills_named

        for row in db.execute("SELECT title, description FROM course_catalog").fetchall():
            skills = extract_skills_named(f"{row['title']}. {row['description']}", db)
            if skills:
                samples.append((f"{row['title']}. {row['description']}", {s["name"] for s in skills}))
        for row in db.execute("SELECT id, title, description FROM jobs").fetchall():
            reqs = db.execute(
                "SELECT s.name FROM job_skills js JOIN skills s ON s.id = js.skill_id WHERE js.job_id = ?",
                (row["id"],),
            ).fetchall()
            if reqs:
                samples.append((f"{row['title']}. {row['description']}", {r["name"] for r in reqs}))

    rng.shuffle(samples)
    return [t for t, _ in samples], [l for _, l in samples]
