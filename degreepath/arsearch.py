"""Arabic-aware search.

The catalog (courses, jobs) is mostly English, so an Arabic query has to be
understood twice: normalised Arabic (ا/أ/إ, ى/ي, ة/ه, diacritics, the "ال"
prefix) and translated through a small bilingual dictionary built from the
skill taxonomy plus common job and field words.

parse(query) returns a list of groups. Each group is the alternatives for one
search term. A row matches when every group has at least one alternative
inside the row's text (AND across terms, OR across alternatives).
"""
import re
import unicodedata

from .skills_data import SKILLS

_AR = re.compile(r"[\u0600-\u06FF]")
_TASHKEEL = re.compile(r"[\u064B-\u065F\u0670\u0640]")
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def norm(text):
    t = unicodedata.normalize("NFKC", text or "").lower().translate(_DIGITS)
    t = _TASHKEEL.sub("", t)
    t = re.sub("[أإآٱ]", "ا", t).replace("ى", "ي").replace("ة", "ه").replace("ؤ", "و").replace("ئ", "ي")
    t = re.sub(r"[,;:!؟?'\"()\[\]{}<>«»/\\|*_~`$%^&=،؛]", " ", t)
    return re.sub(r"\s+", " ", t).strip()


# Arabic phrase (any spelling) -> English words used in titles and summaries.
EXTRA = {
    "برمجه": ["programming", "coding", "developer", "software"],
    "مبرمج": ["programmer", "developer", "software engineer"],
    "مطور": ["developer", "development", "engineer"],
    "تطوير": ["development", "developer"],
    "كود": ["code", "coding"],
    "بيانات": ["data"],
    "تحليل": ["analysis", "analytics", "analyst"],
    "محلل": ["analyst", "analytics"],
    "تحليل بيانات": ["data analysis", "data analytics", "data analyst"],
    "علم البيانات": ["data science", "data scientist"],
    "ذكاء اصطناعي": ["artificial intelligence", "ai", "machine learning"],
    "الذكاء الاصطناعي": ["artificial intelligence", "ai"],
    "تعلم الي": ["machine learning"],
    "شبكات": ["network", "networking"],
    "امن سيبراني": ["cyber security", "cybersecurity", "security"],
    "امن المعلومات": ["information security", "cybersecurity", "security"],
    "حمايه": ["security"],
    "اختراق": ["penetration testing", "ethical hacking", "hacking"],
    "سحابه": ["cloud"],
    "موبايل": ["mobile", "android", "ios"],
    "تطبيقات": ["apps", "applications", "mobile"],
    "ويب": ["web"],
    "موقع": ["web", "website"],
    "مواقع": ["web", "website"],
    "تصميم": ["design", "designer"],
    "مصمم": ["designer", "design"],
    "جرافيك": ["graphic"],
    "تجربه المستخدم": ["ux", "user experience"],
    "فيديو": ["video"],
    "مونتاج": ["video editing", "editor"],
    "تسويق": ["marketing"],
    "تسويق رقمي": ["digital marketing"],
    "مبيعات": ["sales"],
    "بيع": ["sales"],
    "محاسبه": ["accounting", "accountant", "account"],
    "محاسب": ["accountant", "accounting"],
    "ماليه": ["finance", "financial"],
    "تمويل": ["finance"],
    "ضرائب": ["tax"],
    "مراجعه": ["audit"],
    "موارد بشريه": ["human resources", "hr", "recruiter"],
    "شؤون عاملين": ["hr", "human resources"],
    "اداره": ["management", "manager", "admin"],
    "مدير": ["manager", "management"],
    "مشاريع": ["project", "project management"],
    "ادارة مشاريع": ["project management"],
    "خدمه عملاء": ["customer service", "customer support", "support"],
    "دعم فني": ["technical support", "support", "help desk"],
    "هندسه": ["engineering", "engineer"],
    "مهندس": ["engineer", "engineering"],
    "ميكانيكا": ["mechanical"],
    "كهرباء": ["electrical"],
    "مدني": ["civil"],
    "معماري": ["architect", "architecture"],
    "انشاءات": ["construction"],
    "طب": ["medical", "doctor", "health"],
    "طبيب": ["doctor", "physician", "medical"],
    "تمريض": ["nurse", "nursing"],
    "ممرض": ["nurse"],
    "صيدله": ["pharmacy", "pharmacist"],
    "صيدلي": ["pharmacist", "pharmacy"],
    "اسنان": ["dental", "dentist"],
    "معلم": ["teacher", "instructor", "tutor"],
    "مدرس": ["teacher", "tutor", "instructor"],
    "تدريس": ["teaching", "teacher"],
    "تعليم": ["education", "teaching"],
    "مدرب": ["trainer", "coach"],
    "لوجستيات": ["logistics", "supply chain"],
    "مخازن": ["warehouse", "inventory"],
    "مشتريات": ["procurement", "purchasing"],
    "سكرتاريه": ["secretary", "assistant", "admin"],
    "قانون": ["legal", "law", "lawyer"],
    "محامي": ["lawyer", "legal"],
    "كتابه": ["writing", "content", "copywriting"],
    "محتوي": ["content"],
    "ترجمه": ["translation", "translator"],
    "لغه انجليزيه": ["english"],
    "انجليزي": ["english"],
    "اكسل": ["excel"],
    "رياضيات": ["math", "mathematics"],
    "احصاء": ["statistics", "statistical"],
    "اعمال": ["business"],
    "ريادة اعمال": ["entrepreneurship", "startup"],
    "اختبار": ["testing", "qa", "tester"],
    "جوده": ["quality", "qa"],
    "قواعد بيانات": ["database", "sql"],
    "قاعده بيانات": ["database", "sql"],
    "العاب": ["game", "games", "gaming"],
    "بلوك تشين": ["blockchain"],
    "انترنت الاشياء": ["iot", "internet of things"],
    "ادوات": ["tools"],
    "للمبتدئين": ["beginner", "beginners", "introduction", "intro", "fundamentals"],
    "مبتدئ": ["beginner", "introduction", "fundamentals"],
    "اساسيات": ["fundamentals", "basics", "introduction", "foundations"],
    "مقدمه": ["introduction", "intro", "fundamentals"],
    "متقدم": ["advanced"],
    "مصر": ["egypt", "cairo"],
    "القاهره": ["cairo", "egypt"],
    "عن بعد": ["remote"],
    "ريموت": ["remote"],
}

# words that carry no meaning in a catalog search
STOP = {"كورس", "كورسات", "دوره", "دورات", "وظيفه", "وظايف", "وظائف", "شغل", "عن", "في", "من", "علي", "الي",
        "ال", "و", "ب", "ل", "كل", "اي", "ابحث", "دور", "عايز", "اريد", "ابغي", "مجاني", "مجانيه", "مجانا",
        "تعلم", "اتعلم", "شرح", "دروس", "تدريب", "لل", "على"}
_STOPN = {norm(w) for w in STOP}

_DICT = None


def _build():
    d = {}
    for name, name_ar, _cat, aliases in SKILLS:
        names = {name.lower()}
        for a in aliases:
            if not _AR.search(a) and len(a) >= 4:
                names.add(a.lower())
        ar_keys = {norm(name_ar)} | {norm(a) for a in aliases if _AR.search(a)}
        for k in ar_keys:
            if k:
                d.setdefault(k, set()).update(names)
    for k, v in EXTRA.items():
        d.setdefault(norm(k), set()).update(x.lower() for x in v)
    return {k: sorted(v) for k, v in d.items()}


def dictionary():
    global _DICT
    if _DICT is None:
        _DICT = _build()
    return _DICT


def _strip_prefix(tok):
    """Remove common attached Arabic prefixes: ال, وال, بال, لل, كال, و."""
    out = [tok]
    for p in ("وال", "بال", "كال", "فال", "لل", "ال", "و", "ب", "ل"):
        if tok.startswith(p) and len(tok) - len(p) >= 3:
            out.append(tok[len(p):])
    return out


def parse(query):
    """Return a list of alternative-groups, or [] when there is nothing to search."""
    q = norm(query)
    if not q:
        return []
    toks = q.split(" ")
    d = dictionary()
    groups, i = [], 0
    while i < len(toks):
        hit = None
        for n in (3, 2, 1):
            if i + n > len(toks):
                continue
            chunk = toks[i:i + n]
            # try each prefix-stripped variant of the first word
            for first in _strip_prefix(chunk[0]):
                key = " ".join([first] + chunk[1:])
                if key in d:
                    hit = (n, key)
                    break
            if hit:
                break
        if hit:
            n, key = hit
            alts = [key] + d[key]
            # also keep the raw Arabic phrase so Arabic titles still match
            alts.append(" ".join(toks[i:i + n]))
            groups.append(sorted(set(alts)))
            i += n
            continue
        tok = toks[i]
        i += 1
        if tok in _STOPN:
            continue
        if _AR.search(tok):
            groups.append(sorted(set(_strip_prefix(tok))))
        else:
            groups.append([tok])
    return groups


def matches(groups, *texts):
    if not groups:
        return True
    hay = norm(" ".join(t or "" for t in texts))
    return all(any(_has(hay, a) for a in g) for g in groups)


def _has(hay, alt):
    # short Latin words (ai, hr, qa, ux) must match whole words, not "maintain"
    if len(alt) <= 3 and alt.isascii():
        return re.search(r"(?<![a-z0-9])" + re.escape(alt) + r"(?![a-z0-9])", hay) is not None
    return alt in hay
