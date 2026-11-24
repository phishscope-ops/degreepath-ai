"""Course catalog transcribed from the Port Said University photo
(قسم إدارة نظم المعلومات وتكنولوجياها، اللائحة الجديدة 2023/2024).

NOTE: transcribed from a phone photo of the bylaws table; names should be
verified against the official document. Descriptions were written for the
project so the NLP extractor has text to work on.

Each entry: (title, level, semester, description)
"""

CATALOG = [
    # المستوى الأول
    ("مقدمة في الحاسبات", 1, 1, "Introduction to computers: hardware, software, operating systems, and basic problem solving."),
    ("الرياضيات المتقطعة", 1, 1, "Discrete mathematics: logic, sets, relations, and graph basics for computer science."),
    ("حزم التطبيقات المكتبية", 1, 1, "Office applications: Microsoft Excel spreadsheets, Word, and PowerPoint presentations."),
    ("مبادئ الإدارة", 1, 1, "Principles of management: planning, organizing, leadership, and project management basics."),
    ("مبادئ المحاسبة (1)", 1, 1, "Principles of accounting: financial statements, bookkeeping, and report writing."),
    ("أساسيات تكنولوجيا المعلومات", 1, 1, "Information technology fundamentals: networking basics, internet, and information systems."),
    ("لغة انجليزية (1)", 1, 2, "English language course: reading, writing, and communication skills in English."),
    ("أسس التفكير الناقد والعلمي", 1, 2, "Critical and scientific thinking: problem solving, research methods, and analytical thinking."),
    ("مبادئ نظم المعلومات", 1, 2, "Principles of information systems: databases, data analysis, and business systems."),
    ("برمجة الحاسب (1)", 1, 2, "Computer programming 1: Python programming basics, data structures, and algorithms."),
    ("إحصاء واحتمالات", 1, 2, "Statistics and probability: statistical analysis and data analysis methods."),
    ("تفاضل وتكامل", 1, 2, "Calculus: differentiation, integration, and mathematical problem solving."),
    ("رياضيات بحتة", 1, 2, "Pure mathematics: mathematical foundations, logic, and problem solving."),

    # المستوى الثاني
    ("تحليل وتصميم نظم المعلومات", 2, 1, "Systems analysis and design: requirements gathering, database design, and system design."),
    ("مبادئ التسويق", 2, 1, "Principles of marketing: digital marketing and communication skills."),
    ("تطبيقات في الأمن السيبراني", 2, 1, "Cybersecurity applications: information security, network security, and penetration testing basics."),
    ("شبكات الحاسب (1)", 2, 1, "Computer networks 1: networking, TCP/IP, and network administration."),
    ("محاسبة متوسطة", 2, 1, "Intermediate accounting: financial statements, Excel, and report writing."),
    ("تكنولوجيا الوسائط المتعددة", 2, 1, "Multimedia technology: image processing and digital media."),
    ("برمجة الحاسب (2)", 2, 1, "Computer programming 2: object oriented programming, data structures, and algorithms."),
    ("نظم معلومات الأعمال", 2, 2, "Business information systems: business analysis, databases, and reporting."),
    ("مهارات التفاوض والاتصال", 2, 2, "Negotiation and communication skills: communication, teamwork, and presentation skills."),
    ("مقدمة في علم البيانات", 2, 2, "Introduction to data science: data analysis, statistics, Python, and data visualization."),
    ("الفقه السيبراني", 2, 2, "Cyber law: legal aspects of cybersecurity and information technology."),

    # المستوى الثالث
    ("الإدارة المالية", 3, 1, "Financial management: business analysis, Excel, and report writing."),
    ("قواعد البيانات", 3, 1, "Databases: SQL, database design, and MySQL."),
    ("إدارة الموارد البشرية", 3, 1, "Human resources management: communication, teamwork, and project management."),
    ("أصول محاسبة التكاليف", 3, 1, "Cost accounting: Excel, statistics, and report writing."),
    ("شبكات الحاسب (2)", 3, 1, "Computer networks 2: advanced networking, network administration, and cybersecurity."),
    ("تطبيقات الحوسبة السحابية", 3, 1, "Cloud computing applications: cloud computing, AWS, and Docker basics."),
    ("هياكل البيانات", 3, 2, "Data structures: data structures, algorithms, and problem solving."),
    ("معالجة الصور الرقمية وتطبيقاتها", 3, 2, "Digital image processing and applications: Python, image processing, and algorithms."),
    ("التنقيب عن البيانات", 3, 2, "Data mining: data analysis, machine learning, statistics, and Python."),
    ("التعلم العميق", 3, 2, "Deep learning: neural networks, deep learning, Python, and TensorFlow."),
    ("هندسة البرمجيات وتطبيقاتها", 3, 2, "Software engineering and applications: system design, testing, Git, and project management."),

    # المستوى الرابع
    ("نظم حفظ واسترجاع المعلومات", 4, 1, "Information storage and retrieval: databases, SQL, and natural language processing basics."),
    ("معالجة اللغات الطبيعية", 4, 1, "Natural language processing: NLP, text mining, Python, and machine learning."),
    ("برمجة الذكاء الاصطناعي", 4, 1, "Artificial intelligence programming: machine learning, Python, and problem solving."),
    ("تطبيقات الموبايل", 4, 1, "Mobile applications: programming, REST APIs, and UI/UX design."),
    ("انترنت الأشياء", 4, 1, "Internet of Things: networking, embedded programming, and cloud computing."),
    ("مشروع التخرج", 4, 1, "Graduation project: project management, research, report writing, and presentation skills."),
    ("نظم قواعد المعرفة", 4, 2, "Knowledge-based systems: knowledge representation, reasoning, and artificial intelligence."),
    ("البيانات الضخمة", 4, 2, "Big data: big data, Spark, data pipelines, and ETL."),
    ("تطبيقات الذكاء الاصطناعي", 4, 2, "AI applications: machine learning, deep learning, and Python."),
    ("الواقع الافتراضي", 4, 2, "Virtual reality: 3D programming and UI/UX design."),
    ("تكنولوجيا الانترنت", 4, 2, "Internet technologies: HTML, CSS, JavaScript, REST APIs, and web development."),
    ("معالجة الإشارات الرقمية", 4, 2, "Digital signal processing: algorithms, mathematics, and Python."),
    ("أمن الشبكات", 4, 2, "Network security: cybersecurity, networking, and information security."),
]
