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


NEW_JOBS = [
    (
        "Full-Stack Developer", "مطور فول ستاك", "web",
        "Build complete web applications end to end: responsive frontends, "
        "REST APIs and database layers, shipped with Git and Docker.",
        [
            ("HTML/CSS", 3), ("JavaScript", 3), ("REST APIs", 3), ("React", 2),
            ("Node.js", 2), ("SQL", 2), ("Git", 2), ("Testing", 2),
            ("TypeScript", 1), ("Docker", 1), ("UI/UX Design", 1),
        ],
    ),
    (
        "Mobile App Developer (Flutter)", "مطور تطبيقات موبايل", "mobile",
        "Design and ship Android and iOS apps from one codebase with Flutter "
        "and Dart. Work with REST APIs, Firebase and clean app architecture.",
        [
            ("Mobile Development", 3), ("Flutter", 3), ("Dart", 2), ("Firebase", 2),
            ("REST APIs", 2), ("OOP", 2), ("Git", 2), ("UI/UX Design", 1),
            ("Testing", 1), ("Problem Solving", 1),
        ],
    ),
    (
        "Cybersecurity Analyst", "محلل أمن سيبراني", "security",
        "Monitor systems for threats, investigate incidents and test defenses. "
        "Strong networking, Linux and security fundamentals with clear reporting.",
        [
            ("Cybersecurity", 3), ("Networking", 3), ("Linux", 2), ("Python", 2),
            ("Problem Solving", 2), ("English", 2), ("Report Writing", 1),
            ("Testing", 1),
        ],
    ),
    (
        "Data Engineer", "مهندس بيانات", "data",
        "Build and maintain data pipelines and warehouses so analysts and ML "
        "models get clean, reliable data. Strong SQL, Python and ETL on cloud.",
        [
            ("SQL", 3), ("Python", 3), ("ETL", 3), ("Data Warehousing", 2),
            ("Big Data", 2), ("Database Design", 2), ("Data Cleaning", 2),
            ("Cloud Computing", 2), ("Docker", 1), ("Git", 1),
        ],
    ),
    (
        "Cloud Engineer", "مهندس حوسبة سحابية", "cloud",
        "Design and run infrastructure on AWS/Azure, automate deployments with "
        "Terraform and containers, and keep systems reliable and cost-efficient.",
        [
            ("Cloud Computing", 3), ("AWS", 2), ("Azure", 2), ("Linux", 2),
            ("Docker", 2), ("Kubernetes", 2), ("Terraform", 2), ("Networking", 2),
            ("Git", 1), ("Problem Solving", 1),
        ],
    ),
    (
        "QA / Test Automation Engineer", "مهندس ضمان جودة", "software",
        "Own product quality: design test plans, automate regression suites "
        "with Selenium/Cypress and track bugs so releases ship with confidence.",
        [
            ("Testing", 3), ("Test Automation", 3), ("Problem Solving", 2),
            ("Git", 2), ("Communication", 2), ("Python", 1), ("SQL", 1),
            ("REST APIs", 1), ("Report Writing", 1),
        ],
    ),
    (
        "Digital Marketing Specialist", "أخصائي تسويق رقمي", "business",
        "Plan and run online campaigns across search and social, measure "
        "results with analytics and turn data into growth decisions.",
        [
            ("Digital Marketing", 3), ("Social Media Marketing", 3), ("SEO", 2),
            ("Content Marketing", 2), ("Google Analytics", 2), ("Communication", 2),
            ("English", 2), ("Data Analysis", 1), ("Report Writing", 1),
        ],
    ),
    (
        "AI Engineer", "مهندس ذكاء اصطناعي", "ai",
        "Build products on top of large language models and ML: prompts, "
        "evaluation, fine-tuning and integration into real applications.",
        [
            ("Generative AI", 3), ("Machine Learning", 3), ("Python", 3),
            ("Prompt Engineering", 2), ("NLP", 2), ("Deep Learning", 2),
            ("REST APIs", 1), ("Data Analysis", 1), ("Git", 1),
        ],
    ),
    (
        "ERP Developer (Odoo)", "مطور أنظمة ERP", "software",
        "Customize and develop ERP modules (Odoo/SAP) around business processes: "
        "accounting, inventory, HR. Python, PostgreSQL and business understanding.",
        [
            ("ERP", 3), ("Odoo", 3), ("Python", 2), ("PostgreSQL", 2), ("SQL", 2),
            ("Business Analysis", 1), ("Database Design", 1), ("Git", 1),
            ("Communication", 1),
        ],
    ),
    (
        "IT Support Engineer", "مهندس دعم فني", "it",
        "Keep people and systems running: troubleshoot hardware, software and "
        "network issues, and manage users and access on Windows environments.",
        [
            ("Technical Support", 3), ("Problem Solving", 3), ("Networking", 2),
            ("Active Directory", 2), ("Communication", 2), ("English", 1),
            ("Linux", 1), ("Cybersecurity", 1),
        ],
    ),
]

MORE_JOBS = [
    (
        "Game Developer (Unity)", "مطور ألعاب (Unity)", "games",
        "Design and build games with Unity and C#: gameplay mechanics, physics, "
        "UI and publishing for mobile and PC.",
        [
            ("C#", 3), ("Unity", 3), ("Game Design", 2), ("OOP", 2),
            ("Problem Solving", 2), ("Git", 1), ("UI/UX Design", 1), ("Testing", 1),
        ],
    ),
    (
        "Network Engineer", "مهندس شبكات", "it",
        "Design, install and support company networks: routing, switching, "
        "firewalls and connectivity for branches and data centers.",
        [
            ("Networking", 3), ("Cisco (CCNA)", 3), ("Linux", 2),
            ("Windows Server", 2), ("Active Directory", 1), ("Cybersecurity", 1),
            ("Problem Solving", 1), ("Technical Support", 1),
        ],
    ),
    (
        "Penetration Tester", "مختبر اختراق", "security",
        "Test systems and applications for weaknesses before attackers find them: "
        "reconnaissance, exploitation and clear reporting.",
        [
            ("Penetration Testing", 3), ("Cybersecurity", 3), ("Networking", 2),
            ("Linux", 2), ("Python", 1), ("Bash", 1), ("Research", 1),
            ("Report Writing", 1),
        ],
    ),
    (
        "System Administrator", "مسؤول أنظمة", "it",
        "Run and secure company servers: Linux and Windows administration, "
        "user management, backups and automation with scripts.",
        [
            ("Linux", 3), ("Windows Server", 3), ("Active Directory", 2),
            ("Networking", 2), ("Bash", 2), ("Cybersecurity", 1),
            ("Problem Solving", 1),
        ],
    ),
    (
        "Blockchain Developer", "مطور بلوكتشين", "web3",
        "Build smart contracts and decentralized apps: Solidity on Ethereum, "
        "Web3 tooling and secure contract design.",
        [
            ("Blockchain", 3), ("Solidity", 3), ("JavaScript", 2), ("OOP", 2),
            ("Git", 2), ("REST APIs", 1), ("Data Structures", 1),
            ("Problem Solving", 1),
        ],
    ),
    (
        "iOS Developer", "مطور تطبيقات iOS", "mobile",
        "Build iPhone and iPad apps with Swift and SwiftUI: clean UI, REST API "
        "integration, push notifications and App Store publishing.",
        [
            ("Swift", 3), ("SwiftUI", 3), ("Mobile Development", 3), ("OOP", 2),
            ("Git", 2), ("Firebase", 1), ("REST APIs", 1), ("UI/UX Design", 1),
            ("Testing", 1),
        ],
    ),
    (
        "Product Manager", "مدير منتج", "business",
        "Own the product direction: understand users, prioritize features with "
        "the team, and follow delivery with Agile methods and data.",
        [
            ("Product Management", 3), ("Communication", 3), ("Agile/Scrum", 2),
            ("Business Analysis", 2), ("Project Management", 2), ("Data Analysis", 1),
            ("UI/UX Design", 1), ("English", 1),
        ],
    ),
    (
        "Graphic Designer", "مصمم جرافيك", "design",
        "Create visual identities, social media designs and marketing material "
        "with Photoshop and Illustrator, from concept to final artwork.",
        [
            ("Graphic Design", 3), ("Adobe Photoshop", 3), ("Adobe Illustrator", 2),
            ("UI/UX Design", 1), ("Communication", 1), ("Research", 1),
            ("Teamwork", 1),
        ],
    ),
    (
        "Motion Graphics Designer", "مصمم موشن جرافيك", "design",
        "Animate logos, ads and explainer videos: motion principles, After "
        "Effects, and editing short videos for social media.",
        [
            ("Motion Graphics", 3), ("Video Editing", 2), ("Graphic Design", 2),
            ("Communication", 1), ("Research", 1),
        ],
    ),
    (
        "Technical Writer", "كاتب تقني", "business",
        "Write clear documentation, user guides and API references for software "
        "products, working closely with engineers.",
        [
            ("Technical Writing", 3), ("English", 3), ("Report Writing", 2),
            ("Communication", 2), ("Research", 2),
        ],
    ),
]

JOBS = JOBS + NEW_JOBS + MORE_JOBS

# Free learning resources per skill: (skill name, title, url, kind)
RESOURCES = [
    ("SQL", "SQLBolt - Interactive SQL lessons", "https://sqlbolt.com/", "course"),
    ("SQL", "Mode SQL Tutorial", "https://mode.com/sql-tutorial/", "course"),
    ("Excel", "Microsoft Excel training (free)", "https://support.microsoft.com/en-us/excel", "docs"),
    ("Excel", "Excel Practice Online", "https://excel-practice-online.com/", "practice"),
    ("Python", "Python official tutorial", "https://docs.python.org/3/tutorial/", "docs"),
    ("Python", "freeCodeCamp Python (YouTube)", "https://www.youtube.com/watch?v=rfscVS0vtbw", "video"),
    ("Data Analysis", "Kaggle Learn: Data Analysis", "https://www.kaggle.com/learn", "course"),
    ("Data Analysis", "freeCodeCamp: Data Analysis with Python (free)", "https://www.freecodecamp.org/learn/data-analysis-with-python/", "course"),
    ("Data Visualization", "Kaggle Learn: Data Visualization", "https://www.kaggle.com/learn/data-visualization", "course"),
    ("Power BI", "Microsoft Power BI learning path", "https://learn.microsoft.com/training/powerplatform/power-bi", "course"),
    ("Tableau", "Tableau free training videos", "https://www.tableau.com/learn/training", "video"),
    ("Statistics", "Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "course"),
    ("Pandas", "Kaggle Learn: Pandas", "https://www.kaggle.com/learn/pandas", "course"),
    ("NumPy", "NumPy quickstart", "https://numpy.org/doc/stable/user/quickstart.html", "docs"),
    ("Data Cleaning", "Kaggle Learn: Data Cleaning", "https://www.kaggle.com/learn/data-cleaning", "course"),
    ("Machine Learning", "Kaggle Learn: Intro to Machine Learning", "https://www.kaggle.com/learn/intro-to-machine-learning", "course"),
    ("Machine Learning", "Google Machine Learning Crash Course (free)", "https://developers.google.com/machine-learning/crash-course", "course"),
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
    ("UI/UX Design", "web.dev Learn Design (free)", "https://web.dev/learn/design", "course"),
    ("UI/UX Design", "Figma free tutorials", "https://help.figma.com/hc/en-us/categories/360002051613", "video"),
    ("Communication", "Toastmasters resources", "https://www.toastmasters.org/resources", "docs"),
    ("Project Management", "Atlassian Project Management guide (free)", "https://www.atlassian.com/agile/project-management", "course"),
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
    ("Flutter", "Flutter official docs + codelabs", "https://docs.flutter.dev/get-started", "docs"),
    ("Dart", "Dart language tour", "https://dart.dev/language", "docs"),
    ("Kotlin", "Kotlin official docs", "https://kotlinlang.org/docs/home.html", "docs"),
    ("Mobile Development", "Android Basics with Compose (Google, free)", "https://developer.android.com/courses", "course"),
    ("Firebase", "Firebase documentation", "https://firebase.google.com/docs", "docs"),
    ("Test Automation", "Test Automation University (free)", "https://testautomationu.applitools.com/", "course"),
    ("Test Automation", "Selenium documentation", "https://www.selenium.dev/documentation/", "docs"),
    ("Data Warehousing", "Data engineering path (Microsoft Learn)", "https://learn.microsoft.com/training/browse/?terms=data%20engineer", "course"),
    ("Kubernetes", "Kubernetes official tutorials", "https://kubernetes.io/docs/tutorials/", "docs"),
    ("Terraform", "HashiCorp Terraform tutorials", "https://developer.hashicorp.com/terraform/tutorials", "course"),
    ("SEO", "Google Search Central docs", "https://developers.google.com/search/docs", "docs"),
    ("SEO", "Ahrefs Academy (free courses)", "https://ahrefs.com/academy", "course"),
    ("Social Media Marketing", "Meta Blueprint (free lessons)", "https://www.facebook.com/business/learn", "course"),
    ("Content Marketing", "HubSpot Academy (free certifications)", "https://academy.hubspot.com/", "course"),
    ("Google Analytics", "Google Skillshop - Analytics", "https://skillshop.docebosaas.com/", "course"),
    ("ERP", "Odoo eLearning (free)", "https://www.odoo.com/slides", "course"),
    ("Odoo", "Odoo documentation", "https://www.odoo.com/documentation", "docs"),
    ("Generative AI", "DeepLearning.AI short courses (free)", "https://www.deeplearning.ai/short-courses/", "course"),
    ("Prompt Engineering", "ChatGPT Prompt Engineering for Developers (free)", "https://www.deeplearning.ai/short-courses/chatgpt-prompt-engineering-for-developers/", "course"),
    ("Active Directory", "Active Directory on Microsoft Learn", "https://learn.microsoft.com/training/browse/?terms=active%20directory", "course"),
    ("Technical Support", "Professor Messer free CompTIA A+ videos", "https://www.professormesser.com/free-a-plus-training/", "video"),
    ("Unity", "Unity Learn (official free courses)", "https://learn.unity.com/", "course"),
    ("Game Design", "Harvard CS50 Introduction to Game Development (free)", "https://cs50.harvard.edu/games/", "course"),
    ("Cisco (CCNA)", "Cisco Networking Academy (free courses)", "https://www.netacad.com/", "course"),
    ("Penetration Testing", "TryHackMe (free rooms)", "https://tryhackme.com/", "practice"),
    ("Penetration Testing", "HackTheBox Academy (free tier)", "https://academy.hackthebox.com/", "course"),
    ("Windows Server", "Windows Server on Microsoft Learn", "https://learn.microsoft.com/training/browse/?terms=windows%20server", "course"),
    ("Bash", "Learn Shell (interactive, free)", "https://www.learnshell.org/", "practice"),
    ("Bash", "GNU Bash manual", "https://www.gnu.org/software/bash/manual/", "docs"),
    ("Solidity", "CryptoZombies (learn Solidity by building)", "https://cryptozombies.io/", "course"),
    ("Solidity", "Solidity official docs", "https://docs.soliditylang.org/", "docs"),
    ("Blockchain", "Ethereum.org Learn Hub (free)", "https://ethereum.org/en/learn/", "course"),
    ("SwiftUI", "Apple SwiftUI tutorials (official)", "https://developer.apple.com/tutorials/swiftui", "docs"),
    ("Product Management", "Mind the Product (articles & guides)", "https://www.mindtheproduct.com/", "docs"),
    ("Agile/Scrum", "Atlassian Agile Coach", "https://www.atlassian.com/agile", "course"),
    ("Agile/Scrum", "The Scrum Guide (official)", "https://scrumguides.org/", "docs"),
    ("Graphic Design", "Canva Design School (free)", "https://www.canva.com/designschool/", "course"),
    ("Adobe Photoshop", "Adobe Photoshop tutorials (official)", "https://helpx.adobe.com/photoshop/tutorials.html", "video"),
    ("Adobe Illustrator", "Adobe Illustrator tutorials (official)", "https://helpx.adobe.com/illustrator/tutorials.html", "video"),
    ("Video Editing", "DaVinci Resolve free training", "https://www.blackmagicdesign.com/products/davinciresolve/training", "course"),
    ("Motion Graphics", "After Effects tutorials (official)", "https://helpx.adobe.com/after-effects/tutorials.html", "video"),
    ("Technical Writing", "Google Technical Writing Courses (free)", "https://developers.google.com/tech-writing", "course"),
]


def seed_if_empty(db):
    """Ensure the taxonomy, jobs, catalog and resources exist.

    Idempotent: safe to run at every startup. Existing databases pick up new
    jobs/skills/resources added in later versions without a wipe, so the seed
    keeps working if the app moves to a persistent external database.
    """
    skill_id = {}
    for name, name_ar, category, aliases in SKILLS:
        db.execute(
            "INSERT OR IGNORE INTO skills (name, name_ar, category) VALUES (?, ?, ?)",
            (name, name_ar, category),
        )
        sid = db.execute("SELECT id FROM skills WHERE name = ?", (name,)).fetchone()["id"]
        skill_id[name] = sid
        for alias in set(aliases + [name]):
            db.execute(
                "INSERT OR IGNORE INTO skill_aliases (alias, skill_id) VALUES (?, ?)",
                (alias, sid),
            )

    for title, title_ar, category, desc, reqs in JOBS:
        row = db.execute("SELECT id FROM jobs WHERE title = ?", (title,)).fetchone()
        if row:
            jid = row["id"]
        else:
            cur = db.execute(
                "INSERT INTO jobs (title, title_ar, category, description) VALUES (?, ?, ?, ?)",
                (title, title_ar, category, desc),
            )
            jid = cur.lastrowid
        for skill_name, importance in reqs:
            db.execute(
                "INSERT OR IGNORE INTO job_skills (job_id, skill_id, importance) VALUES (?, ?, ?)",
                (jid, skill_id[skill_name], importance),
            )

    from .catalog_data import CATALOG

    if not db.execute("SELECT COUNT(*) AS c FROM course_catalog").fetchone()["c"]:
        for title, level, semester, desc in CATALOG:
            db.execute(
                "INSERT INTO course_catalog (title, level, semester, description) VALUES (?, ?, ?, ?)",
                (title, level, semester, desc),
            )

    # Coursera is only free for a trial period; drop any old rows that point to it.
    db.execute("DELETE FROM resources WHERE url LIKE '%coursera.org%'")

    for skill_name, title, url, kind in RESOURCES:
        sid = skill_id.get(skill_name)
        if not sid:
            continue
        exists = db.execute(
            "SELECT 1 FROM resources WHERE skill_id = ? AND url = ?", (sid, url)
        ).fetchone()
        if not exists:
            db.execute(
                "INSERT INTO resources (skill_id, title, url, kind) VALUES (?, ?, ?, ?)",
                (sid, title, url, kind),
            )

    db.commit()
