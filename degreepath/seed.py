"""Seed data: skills taxonomy, jobs with required skills, free learning resources."""

from .skills_data import SKILLS

# job title, Arabic title, category, description, [(skill name, importance 1-3)]
JOBS = [
    (
        "Data Analyst", "محلل بيانات", "data",
        "Collect, clean and analyze data to help the business make decisions. "
        "Build dashboards and reports, write SQL queries, and present insights "
        "using Excel, Power BI and Python.",
        [
            ("SQL", 3), ("Excel", 3), ("Data Analysis", 3), ("Data Visualization", 3),
            ("Power BI", 2), ("Python", 2), ("Statistics", 2), ("Pandas", 2),
            ("Data Cleaning", 2), ("Communication", 1), ("Report Writing", 1),
        ],
    ),
    (
        "Python Developer", "مطور بايثون", "software",
        "Build backend services and scripts in Python. Work with REST APIs, "
        "databases and testing frameworks, using Git for version control.",
        [
            ("Python", 3), ("OOP", 3), ("Data Structures", 2), ("Algorithms", 2),
            ("REST APIs", 2), ("Flask", 2), ("SQL", 2), ("Git", 2),
            ("Testing", 2), ("Linux", 1), ("Docker", 1),
        ],
    ),
    (
        "Database Administrator", "مسؤول قواعد بيانات", "databases",
        "Design, secure and maintain databases. Own backups, performance tuning "
        "and user access for MySQL/PostgreSQL/Oracle systems.",
        [
            ("SQL", 3), ("Database Administration", 3), ("Database Design", 3),
            ("MySQL", 2), ("PostgreSQL", 2), ("Oracle", 2), ("Linux", 2),
            ("ETL", 1), ("Problem Solving", 1),
        ],
    ),
    (
        "Frontend Developer", "مطور واجهات", "web",
        "Build responsive user interfaces with HTML, CSS, JavaScript and React. "
        "Consume REST APIs and care about UI/UX quality.",
        [
            ("HTML/CSS", 3), ("JavaScript", 3), ("React", 3), ("UI/UX Design", 2),
            ("REST APIs", 2), ("Git", 2), ("TypeScript", 1), ("Testing", 1),
        ],
    ),
    (
        "Backend Developer", "مطور باك إند", "web",
        "Design and build server-side applications, REST APIs and database "
        "layers. Care about testing, security and deployment with Docker/Linux.",
        [
            ("REST APIs", 3), ("SQL", 3), ("OOP", 2), ("Python", 2),
            ("JavaScript", 1), ("Node.js", 2), ("Django", 1), ("Flask", 1),
            ("Database Design", 2), ("Git", 2), ("Testing", 2), ("Docker", 1), ("Linux", 1),
        ],
    ),
    (
        "Data Scientist", "عالم بيانات", "data",
        "Build statistical and machine learning models on real datasets. "
        "Strong Python, statistics and data wrangling; communicate findings clearly.",
        [
            ("Python", 3), ("Statistics", 3), ("Machine Learning", 3), ("Pandas", 2),
            ("NumPy", 2), ("Data Analysis", 2), ("Scikit-learn", 2), ("SQL", 2),
            ("Data Visualization", 1), ("Communication", 1), ("Research", 1),
        ],
    ),
    (
        "Machine Learning Engineer", "مهندس تعلم آلة", "ai",
        "Train, evaluate and deploy ML models in production. Strong Python, ML "
        "frameworks, data pipelines and software engineering basics.",
        [
            ("Machine Learning", 3), ("Python", 3), ("Deep Learning", 2),
            ("Scikit-learn", 2), ("TensorFlow", 2), ("PyTorch", 1), ("Statistics", 2),
            ("Data Structures", 2), ("Algorithms", 2), ("Docker", 1), ("Git", 2),
            ("SQL", 1),
        ],
    ),
    (
        "Business Analyst", "محلل أعمال", "business",
        "Bridge business and tech: gather requirements, analyze processes and "
        "data, and write clear reports for stakeholders.",
        [
            ("Business Analysis", 3), ("Communication", 3), ("Excel", 2),
            ("Data Analysis", 2), ("Report Writing", 2), ("SQL", 1),
            ("Power BI", 1), ("Project Management", 1), ("English", 1),
        ],
    ),
    (
        "UI/UX Designer", "مصمم واجهات وتجربة مستخدم", "design",
        "Design user flows, wireframes and prototypes in Figma. Run usability "
        "reviews and hand off clean specs to developers.",
        [
            ("UI/UX Design", 3), ("Communication", 2), ("Research", 2),
            ("HTML/CSS", 1), ("Teamwork", 2), ("Problem Solving", 1),
        ],
    ),
    (
        "DevOps Engineer", "مهندس ديف أوبس", "it",
        "Automate build/deploy pipelines, manage cloud infrastructure and keep "
        "systems reliable with Linux, Docker and CI/CD.",
        [
            ("Linux", 3), ("Docker", 3), ("Cloud Computing", 2), ("AWS", 2),
            ("Git", 2), ("Networking", 1), ("Python", 1), ("Testing", 1),
            ("Problem Solving", 2),
        ],
    ),
]

# Free learning resources per skill: (skill name, title, url, kind)
RESOURCES = [
    ("SQL", "SQLBolt - Interactive SQL lessons", "https://sqlbolt.com/", "course"),
    ("SQL", "Mode SQL Tutorial", "https://mode.com/sql-tutorial/", "course"),
    ("Excel", "Microsoft Excel training (free)", "https://support.microsoft.com/en-us/excel", "docs"),
    ("Excel", "Excel Practice Online", "https://excel-practice-online.com/", "practice"),
    ("Python", "Python official tutorial", "https://docs.python.org/3/tutorial/", "docs"),
    ("Python", "freeCodeCamp Python (YouTube)", "https://www.youtube.com/watch?v=rfscVS0vtbw", "video"),
    ("Data Analysis", "Kaggle Learn: Data Analysis", "https://www.kaggle.com/learn", "course"),
    ("Data Analysis", "Google Data Analytics (audit free on Coursera)", "https://www.coursera.org/professional-certificates/google-data-analytics", "course"),
    ("Data Visualization", "Kaggle Learn: Data Visualization", "https://www.kaggle.com/learn/data-visualization", "course"),
    ("Power BI", "Microsoft Power BI learning path", "https://learn.microsoft.com/training/powerplatform/power-bi", "course"),
    ("Tableau", "Tableau free training videos", "https://www.tableau.com/learn/training", "video"),
    ("Statistics", "Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "course"),
    ("Pandas", "Kaggle Learn: Pandas", "https://www.kaggle.com/learn/pandas", "course"),
    ("NumPy", "NumPy quickstart", "https://numpy.org/doc/stable/user/quickstart.html", "docs"),
    ("Data Cleaning", "Kaggle Learn: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning", "course"),
    ("Machine Learning", "Kaggle Learn: Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning", "course"),
    ("Machine Learning", "Andrew Ng ML Specialization (audit free)", "https://www.coursera.org/specializations/machine-learning-introduction", "course"),
    ("Deep Learning", "fast.ai Practical Deep Learning", "https://course.fast.ai/", "course"),
    ("Scikit-learn", "scikit-learn user guide", "https://scikit-learn.org/stable/user_guide.html", "docs"),
    ("TensorFlow", "TensorFlow tutorials", "https://www.tensorflow.org/tutorials", "docs"),
    ("PyTorch", "PyTorch tutorials", "https://pytorch.org/tutorials/", "docs"),
    ("NLP", "Kaggle Learn: NLP", "https://www.kaggle.com/learn/natural-language-processing", "course"),
    ("HTML/CSS", "freeCodeCamp Responsive Web Design", "https://www.freecodecamp.org/learn/2022/responsive-web-design/", "course"),
    ("HTML/CSS", "MDN Web Docs: HTML & CSS", "https://developer.mozilla.org/en-US/docs/Learn", "docs"),
    ("JavaScript", "freeCodeCamp JavaScript Algorithms", "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures/", "course"),
    ("JavaScript", "javascript.info", "https://javascript.info/", "docs"),
    ("TypeScript", "TypeScript handbook", "https://www.typescriptlang.org/docs/handbook/", "docs"),
    ("React", "React official tutorial", "https://react.dev/learn", "docs"),
    ("Node.js", "Node.js guides", "https://nodejs.org/en/learn", "docs"),
    ("Flask", "Flask official tutorial", "https://flask.palletsprojects.com/en/latest/tutorial/", "docs"),
    ("Django", "Django official tutorial", "https://docs.djangoproject.com/en/stable/intro/tutorial01/", "docs"),
    ("REST APIs", "REST API tutorial (restfulapi.net)", "https://restfulapi.net/", "docs"),
    ("Git", "Git official book (Pro Git, free)", "https://git-scm.com/book/en/v2", "docs"),
    ("Git", "GitHub Skills", "https://skills.github.com/", "practice"),
    ("Docker", "Docker getting started", "https://docs.docker.com/get-started/", "docs"),
    ("Linux", "Linux Journey", "https://linuxjourney.com/", "course"),
    ("MySQL", "MySQL tutorial (w3schools)", "https://www.w3schools.com/mysql/", "course"),
    ("PostgreSQL", "PostgreSQL tutorial", "https://www.postgresqltutorial.com/", "course"),
    ("Oracle", "Oracle Live SQL (practice)", "https://livesql.oracle.com/", "practice"),
    ("MongoDB", "MongoDB University (free)", "https://learn.mongodb.com/", "course"),
    ("Database Design", "Database design course (CMU, YouTube)", "https://www.youtube.com/@CMUDatabaseGroup", "video"),
    ("Database Administration", "PostgreSQL DBA docs", "https://www.postgresql.org/docs/current/admin.html", "docs"),
    ("ETL", "Kaggle Learn: Data Cleaning + pipelines", "https://www.kaggle.com/learn", "course"),
    ("Big Data", "Spark documentation", "https://spark.apache.org/docs/latest/", "docs"),
    ("AWS", "AWS Skill Builder (free tier)", "https://skillbuilder.aws/", "course"),
    ("Azure", "Microsoft Learn Azure fundamentals", "https://learn.microsoft.com/training/azure/", "course"),
    ("Cloud Computing", "Google Cloud skills boost (free courses)", "https://www.cloudskillsboost.google/", "course"),
    ("Networking", "Cisco Networking Academy (free courses)", "https://www.netacad.com/", "course"),
    ("Cybersecurity", "TryHackMe (free rooms)", "https://tryhackme.com/", "practice"),
    ("OOP", "Python OOP (Real Python)", "https://realpython.com/python3-object-oriented-programming/", "docs"),
    ("Data Structures", "freeCodeCamp Data Structures (YouTube)", "https://www.youtube.com/watch?v=RBSGKlAvoiM", "video"),
    ("Algorithms", "NeetCode practice", "https://neetcode.io/", "practice"),
    ("System Design", "System Design Primer (GitHub)", "https://github.com/donnemartin/system-design-primer", "docs"),
    ("Testing", "pytest documentation", "https://docs.pytest.org/", "docs"),
    ("UI/UX Design", "Google UX Design (audit free on Coursera)", "https://www.coursera.org/professional-certificates/google-ux-design", "course"),
    ("UI/UX Design", "Figma free tutorials", "https://help.figma.com/hc/en-us/categories/360002051613", "video"),
    ("Communication", "Toastmasters resources", "https://www.toastmasters.org/resources", "docs"),
    ("Project Management", "Google Project Management (audit free)", "https://www.coursera.org/professional-certificates/google-project-management", "course"),
    ("Business Analysis", "IIBA free resources", "https://www.iiba.org/", "docs"),
    ("Digital Marketing", "Google Digital Garage (free)", "https://learndigital.withgoogle.com/", "course"),
    ("English", "BBC Learning English", "https://www.bbc.co.uk/learningenglish", "course"),
    ("Research", "Google Scholar", "https://scholar.google.com/", "practice"),
    ("Report Writing", "Purdue OWL writing lab", "https://owl.purdue.edu/", "docs"),
    ("Teamwork", "Atlassian teamwork guides", "https://www.atlassian.com/agile/teams", "docs"),
    ("Problem Solving", "LeetCode (free problems)", "https://leetcode.com/", "practice"),
    ("C++", "learncpp.com", "https://www.learncpp.com/", "course"),
    ("C#", "Microsoft Learn C#", "https://learn.microsoft.com/dotnet/csharp/", "course"),
    ("Java", "Hyperskill Java (free track)", "https://hyperskill.org/", "course"),
    ("PHP", "PHP official manual", "https://www.php.net/manual/en/", "docs"),
    ("R", "R for Data Science (free book)", "https://r4ds.hadley.nz/", "course"),
]


def seed_if_empty(db):
    if db.execute("SELECT COUNT(*) AS c FROM skills").fetchone()["c"]:
        return

    skill_id = {}
    for name, name_ar, category, aliases in SKILLS:
        cur = db.execute(
            "INSERT INTO skills (name, name_ar, category) VALUES (?, ?, ?)",
            (name, name_ar, category),
        )
        sid = cur.lastrowid
        skill_id[name] = sid
        for alias in set(aliases + [name]):
            db.execute(
                "INSERT OR IGNORE INTO skill_aliases (alias, skill_id) VALUES (?, ?)",
                (alias, sid),
            )

    for title, title_ar, category, desc, reqs in JOBS:
        cur = db.execute(
            "INSERT INTO jobs (title, title_ar, category, description) VALUES (?, ?, ?, ?)",
            (title, title_ar, category, desc),
        )
        jid = cur.lastrowid
        for skill_name, importance in reqs:
            db.execute(
                "INSERT INTO job_skills (job_id, skill_id, importance) VALUES (?, ?, ?)",
                (jid, skill_id[skill_name], importance),
            )

    from .catalog_data import CATALOG

    for title, level, semester, desc in CATALOG:
        db.execute(
            "INSERT INTO course_catalog (title, level, semester, description) VALUES (?, ?, ?, ?)",
            (title, level, semester, desc),
        )

    for skill_name, title, url, kind in RESOURCES:
        sid = skill_id.get(skill_name)
        if sid:
            db.execute(
                "INSERT INTO resources (skill_id, title, url, kind) VALUES (?, ?, ?, ?)",
                (sid, title, url, kind),
            )

    db.commit()
