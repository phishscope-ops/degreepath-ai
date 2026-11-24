"""Skill taxonomy: canonical skills with English and Arabic aliases.

Each entry: (canonical name, Arabic name, category, [aliases]).
The extractor matches aliases case-insensitively on word boundaries.
"""

SKILLS = [
    # Programming languages
    ("Python", "بايثون", "programming", ["python", "python3", "بايثون"]),
    ("SQL", "إس كيو إل", "databases", ["sql", "structured query language", "اس كيو ال", "إس كيو إل"]),
    ("Java", "جافا", "programming", ["java", "جافا"]),
    ("JavaScript", "جافا سكريبت", "programming", ["javascript", "js", "جافا سكريبت", "جافاسكريبت"]),
    ("TypeScript", "تايب سكريبت", "programming", ["typescript", "ts"]),
    ("C++", "سي بلس بلس", "programming", ["c++", "cpp", "سي بلس بلس"]),
    ("C#", "سي شارب", "programming", ["c#", "csharp", "c sharp", "سي شارب"]),
    ("R", "آر", "programming", ["r programming", "r language", "rstudio"]),
    ("PHP", "بي إتش بي", "programming", ["php", "بي اتش بي"]),
    ("HTML/CSS", "إتش تي إم إل / سي إس إس", "web", ["html", "css", "html5", "css3", "html/css", "اتش تي ام ال", "سي اس اس"]),
    # Data & analytics
    ("Data Analysis", "تحليل البيانات", "data", ["data analysis", "data analytics", "analyzing data", "statistical analysis", "data manipulation", "تحليل البيانات", "تحليل بيانات"]),
    ("Statistics", "إحصاء", "data", ["statistics", "statistical analysis", "statistical methods", "احصاء", "إحصاء", "تحليل احصائي", "تحليل إحصائي"]),
    ("Excel", "إكسل", "data", ["excel", "microsoft excel", "ms excel", "spreadsheet", "spreadsheets", "اكسل", "إكسل"]),
    ("Power BI", "باور بي آي", "data", ["power bi", "powerbi", "باور بي اي", "باور بي أي"]),
    ("Tableau", "تابلو", "data", ["tableau", "تابلو"]),
    ("Data Visualization", "عرض البيانات", "data", ["data visualization", "data visualisation", "visualization", "dashboards", "dashboard", "عرض البيانات", "تمثيل البيانات"]),
    ("Pandas", "بانداس", "data", ["pandas"]),
    ("NumPy", "نامباي", "data", ["numpy"]),
    ("Data Cleaning", "تنظيف البيانات", "data", ["data cleaning", "data cleansing", "data wrangling", "تنظيف البيانات"]),
    ("ETL", "إي تي إل", "data", ["etl", "extract transform load", "data pipeline", "data pipelines"]),
    ("Big Data", "البيانات الضخمة", "data", ["big data", "hadoop", "spark", "pyspark", "البيانات الضخمة"]),
    ("Machine Learning", "تعلم الآلة", "ai", ["machine learning", "ml", "تعلم الالة", "تعلم الآلة", "التعلم الآلي"]),
    ("Deep Learning", "التعلم العميق", "ai", ["deep learning", "neural networks", "neural network", "التعلم العميق", "الشبكات العصبية"]),
    ("NLP", "معالجة اللغة الطبيعية", "ai", ["nlp", "natural language processing", "text mining", "معالجة اللغة الطبيعية", "معالجة اللغات الطبيعية"]),
    ("TensorFlow", "تنسورفلو", "ai", ["tensorflow", "tf"]),
    ("PyTorch", "باي تورش", "ai", ["pytorch", "torch"]),
    ("Scikit-learn", "سايكيت ليرن", "ai", ["scikit-learn", "scikit learn", "sklearn"]),
    # Databases
    ("MySQL", "ماي إس كيو إل", "databases", ["mysql", "ماي اس كيو ال"]),
    ("PostgreSQL", "بوستجرس", "databases", ["postgresql", "postgres", "بوستجرس"]),
    ("MongoDB", "مونجو دي بي", "databases", ["mongodb", "mongo", "مونجو"]),
    ("Database Design", "تصميم قواعد البيانات", "databases", ["database design", "database schema", "data modeling", "er diagrams", "erd", "تصميم قواعد البيانات", "قواعد البيانات", "قاعدة بيانات"]),
    ("Database Administration", "إدارة قواعد البيانات", "databases", ["database administration", "database management", "dba", "backup and recovery", "ادارة قواعد البيانات", "إدارة قواعد البيانات"]),
    ("Oracle", "أوراكل", "databases", ["oracle", "oracle database", "pl/sql", "اوراكل", "أوراكل"]),
    # Web & software
    ("React", "ريآكت", "web", ["react", "react.js", "reactjs", "رياكت", "ريآكت"]),
    ("Node.js", "نود جي إس", "web", ["node.js", "nodejs", "node", "نود"]),
    ("Flask", "فلاسك", "web", ["flask", "فلاسك"]),
    ("Django", "جانغو", "web", ["django", "جانجو", "جانغو"]),
    ("REST APIs", "واجهات برمجية", "web", ["rest api", "rest apis", "restful", "api development", "apis", "واجهات برمجية"]),
    ("Git", "جيت", "tools", ["git", "github", "version control", "جيت", "جيت هب", "جيتهب"]),
    ("Docker", "دوكر", "tools", ["docker", "containers", "دوكر"]),
    ("Linux", "لينكس", "tools", ["linux", "bash", "shell scripting", "لينكس"]),
    ("Testing", "الاختبار", "software", ["unit testing", "testing", "qa", "test cases", "pytest", "اختبار", "الاختبار", "ضمان الجودة"]),
    ("OOP", "البرمجة كائنية التوجه", "software", ["oop", "object oriented", "object-oriented", "البرمجة كائنية التوجه", "كائنية التوجه"]),
    ("Data Structures", "هياكل البيانات", "software", ["data structures", "هياكل البيانات"]),
    ("Algorithms", "الخوارزميات", "software", ["algorithms", "algorithm design", "problem solving", "الخوارزميات", "حل المشكلات"]),
    ("System Design", "تصميم الأنظمة", "software", ["system design", "software architecture", "تصميم الأنظمة"]),
    # Cloud & security
    ("AWS", "أمازون ويب سيرفيسز", "cloud", ["aws", "amazon web services"]),
    ("Azure", "أزور", "cloud", ["azure", "microsoft azure"]),
    ("Cloud Computing", "الحوسبة السحابية", "cloud", ["cloud computing", "cloud services", "الحوسبة السحابية"]),
    ("Networking", "الشبكات", "it", ["networking", "network administration", "tcp/ip", "الشبكات"]),
    ("Cybersecurity", "الأمن السيبراني", "security", ["cybersecurity", "cyber security", "information security", "penetration testing", "الامن السيبراني", "الأمن السيبراني"]),
    # Business & soft
    ("Communication", "التواصل", "soft", ["communication", "communication skills", "presentation skills", "التواصل", "مهارات التواصل"]),
    ("Teamwork", "العمل الجماعي", "soft", ["teamwork", "team work", "collaboration", "العمل الجماعي", "العمل ضمن فريق"]),
    ("Problem Solving", "حل المشكلات", "soft", ["problem solving", "critical thinking", "analytical thinking", "حل المشكلات", "التفكير النقدي"]),
    ("Project Management", "إدارة المشاريع", "business", ["project management", "agile", "scrum", "ادارة المشاريع", "إدارة المشاريع"]),
    ("Business Analysis", "تحليل الأعمال", "business", ["business analysis", "requirements gathering", "business intelligence", "تحليل الاعمال", "تحليل الأعمال"]),
    ("UI/UX Design", "تصميم واجهات المستخدم", "design", ["ui/ux", "ui ux", "ux design", "ui design", "user experience", "user interface", "figma", "تصميم واجهات", "تجربة المستخدم"]),
    ("Digital Marketing", "التسويق الرقمي", "business", ["digital marketing", "seo", "social media marketing", "التسويق الرقمي", "التسويق الالكتروني", "التسويق الإلكتروني"]),
    ("English", "الإنجليزية", "soft", ["english", "english language", "الانجليزية", "الإنجليزية", "اللغة الانجليزية"]),
    ("Research", "البحث", "soft", ["research", "research skills", "literature review", "البحث", "مهارات البحث"]),
    ("Report Writing", "كتابة التقارير", "soft", ["report writing", "technical writing", "documentation", "كتابة التقارير", "التوثيق"]),
]

STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "has",
    "in", "is", "it", "its", "of", "on", "or", "that", "the", "to", "was",
    "were", "will", "with", "you", "your", "we", "our", "this", "these",
    "those", "they", "them", "their", "have", "had", "not", "but", "can",
    "course", "introduction", "intro", "fundamentals", "basics", "using",
    "use", "used", "including", "include", "includes", "students", "learn",
    "learning", "covers", "topics", "description", "requirements",
}
