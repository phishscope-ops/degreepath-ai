"""Port Said University, Faculty of Management Technology and Information Systems (MTIS).
Course lists transcribed from the official bylaw tables (2023/2024), photos sent by the user.
Departments: ims, bis, bmt, act. Years 1-2 of bis/bmt/act share the common list ("gen").
Each row: (dept, level, semester, title). semester 3 = elective list of that level.
"""

DEPARTMENTS = [
    ("ims", "إدارة نظم المعلومات"),
    ("bis", "نظم معلومات الأعمال"),
    ("bmt", "تكنولوجيا الإدارة والأعمال"),
    ("act", "تكنولوجيا المحاسبة"),
]

def _rows(dept, level, sem, titles):
    return [(dept, level, sem, t) for t in titles]

IMS = (
    _rows("ims", 1, 1, ["مقدمة في الحاسبات", "الرياضيات المنفصلة", "حزم التطبيقات المكتبية", "مبادئ الإدارة", "مبادئ المحاسبة (1)", "مقدمة في البرمجة", "أساسيات تكنولوجيا المعلومات"])
    + _rows("ims", 1, 2, ["لغة إنجليزية (1)", "أسس التفكير الناقد والعلمي", "تفاضل وتكامل", "احتمالات وإحصاء", "أساسيات نظم المعلومات", "رياضيات الحاسب", "برمجة الحاسب (1)"])
    + _rows("ims", 2, 1, ["تحليل وتصميم نظم المعلومات", "مبادئ التسويق", "محاسبة متوسطة", "شبكات الحاسب (1)", "مقدمة في علم البيانات", "نظم التشغيل", "اختياري جامعة"])
    + _rows("ims", 2, 2, ["نظم معلومات الأعمال", "تطبيقات الخوارزميات", "تطبيقات في الأمن السيبراني", "برمجة الحاسب (2)", "تكنولوجيا الوسائط المتعددة", "تطبيقات الإنترنت", "اختياري جامعة"])
    + _rows("ims", 2, 3, ["مهارات التفاوض والاتصال", "الملكية الفكرية", "القضايا المجتمعية", "حقوق الإنسان", "علم الجودة", "التنمية الذاتية", "تقارير فنية باللغة الإنجليزية"])
    + _rows("ims", 3, 1, ["أخلاقيات المهنة", "قواعد البيانات", "إدارة الموارد البشرية", "أصول محاسبة التكاليف", "تعلم الآلة وتطبيقاتها", "شبكات الحاسب (2)"])
    + _rows("ims", 3, 2, ["الإدارة المالية", "هياكل البيانات", "معالجة الصور الرقمية وتطبيقاتها", "التنقيب عن البيانات", "هندسة البرمجيات وتطبيقاتها"])
    + _rows("ims", 3, 3, ["تطبيقات الحوسبة السحابية", "نظم الرسم بالحاسب", "تراسل البيانات", "التعلم العميق", "تشفير البيانات"])
    + _rows("ims", 4, 1, ["نظم حفظ واسترجاع المعلومات", "معالجة اللغات الطبيعية", "برمجة الذكاء الاصطناعي", "تطبيقات الموبايل", "انترنت الأشياء"])
    + _rows("ims", 4, 2, ["نظم قواعد المعرفة", "تطبيقات الذكاء الاصطناعي", "الواقع الافتراضي", "تكنولوجيا الانترنت", "مشروع التخرج"])
    + _rows("ims", 4, 3, ["معالجة الكلام", "البيانات الضخمة", "الرؤية بالحاسب", "تطبيقات بالنمذجة والمحاكاة", "معالجة الإشارات الرقمية", "أمن الشبكات"])
)

GEN = ["bis", "bmt", "act"]
_GEN_ROWS = (
    [(1, 1, t) for t in ["مقدمة في الحاسبات", "لغة إنجليزية (1)", "مبادئ الاقتصاد (1)", "أساسيات تكنولوجيا المعلومات", "حزم التطبيقات المكتبية", "مبادئ الإدارة", "مبادئ المحاسبة (1)"]]
    + [(1, 2, t) for t in ["أسس التفكير النقدي والعلمي", "مبادئ الاقتصاد (2)", "مبادئ إحصاء", "أساسيات نظم المعلومات", "مبادئ البرمجة للأعمال", "السلوك التنظيمي", "مبادئ المحاسبة (2)"]]
    + [(2, 1, t) for t in ["نقود وبنوك", "إحصاء تطبيقي", "نظم التشغيل", "تحليل وتصميم نظم المعلومات", "مبادئ التسويق", "محاسبة متوسطة (1)", "اختياري جامعة"]]
    + [(2, 2, t) for t in ["تطبيقات الإنترنت", "نظم معلومات الأعمال", "لغات البرمجة للأعمال (1)", "التجارة الإلكترونية", "إدارة الإنتاج في بيئة التشغيل الإلكتروني", "محاسبة متوسطة (2)", "اختياري جامعة"]]
    + [(2, 3, t) for t in ["مهارات التفاوض والاتصال", "الملكية الفكرية", "القضايا المجتمعية", "حقوق الإنسان", "علم الجودة", "التنمية الذاتية", "لغة إنجليزية (2)", "القانون التجاري", "الإعلام"]]
)

BIS = (
    _rows("bis", 3, 1, ["أخلاقيات المهنة", "شبكات الحاسب (1)", "مقدمة في علم البيانات", "إدارة الموارد البشرية", "أصول محاسبة التكاليف", "قواعد البيانات"])
    + _rows("bis", 3, 2, ["الإدارة المالية", "لغات البرمجة للأعمال (2)", "أمن بيانات الأعمال", "قواعد البيانات المتقدمة", "تطبيقات بحوث العمليات في التخصص"])
    + _rows("bis", 3, 3, ["نظم دعم القرار", "تجارة إلكترونية متقدمة", "موضوعات مختارة في نظم معلومات الأعمال", "إدارة الملفات"])
    + _rows("bis", 4, 1, ["نظم حفظ واسترجاع المعلومات", "تطبيقات نظم معلومات الأعمال", "تحليل بيانات الأعمال", "نظم المعلومات الذكية", "مستودعات البيانات"])
    + _rows("bis", 4, 2, ["تطبيقات الذكاء الاصطناعي", "تطبيقات الموبايل في التخصص", "إدارة مشروعات البرمجيات", "نظم معلومات البنوك", "مشروع التخرج"])
    + _rows("bis", 4, 3, ["لغات البرمجة المتقدمة (1)", "تحليل البيانات المتقدمة", "لغات البرمجة المتقدمة (2)", "تطبيقات نظم معلومات الأعمال المتقدمة"])
)
ACT = (
    _rows("act", 3, 1, ["أخلاقيات المهنة", "قواعد البيانات", "إدارة الموارد البشرية", "أصول محاسبة التكاليف", "محاسبة الموارد البشرية", "مبادئ المراجعة", "تطبيقات محاسبية باستخدام الجداول الإلكترونية"])
    + _rows("act", 3, 2, ["الإدارة المالية", "محاسبة إدارية", "نظم المعلومات المحاسبية", "تحليل القوائم المالية باستخدام الحاسب", "تطبيقات بحوث العمليات في التخصص", "نظم التكاليف الرقمية"])
    + _rows("act", 4, 1, ["تحليل بيانات الأعمال", "محاسبة دولية", "المراجعة الإلكترونية لنظم المحاسبة", "محاسبة المنشآت الخدمية", "المحاسبة الضريبية الإلكترونية (1)"])
    + _rows("act", 4, 2, ["تطبيقات الموبايل في المحاسبة", "نظم المحاسبة الإلكترونية", "المحاسبة الإدارية المتقدمة", "المحاسبة الضريبية الإلكترونية (2)", "مشروع التخرج"])
    + _rows("act", 4, 3, ["مراجعة متقدمة", "موضوعات مختارة في تكنولوجيا المحاسبة", "المحاسبة في التنمية المستدامة", "نظم تكاليف البرمجيات"])
)
BMT = (
    _rows("bmt", 3, 1, ["أخلاقيات المهنة", "قواعد البيانات", "أصول محاسبة التكاليف", "إدارة الموارد البشرية", "تكنولوجيا التسويق الرقمي", "إدارة الأعمال الدولية", "إدارة سلاسل الإمداد"])
    + _rows("bmt", 3, 2, ["محاسبة إدارية", "الإدارة المالية", "ريادة الأعمال", "الإدارة الإلكترونية لعلاقات العملاء", "بحوث التسويق", "تطبيقات بحوث العمليات في التخصص"])
    + _rows("bmt", 4, 1, ["اقتصاديات الأعمال", "تحليل بيانات الأعمال", "الإدارة الاستراتيجية", "دراسات جدوى المشروعات", "الاتصالات الإدارية الرقمية"])
    + _rows("bmt", 4, 2, ["موضوعات مختارة في التخصص", "تطبيقات الموبايل في التخصص", "التسويق الدولي", "تحليل الأسواق المالية", "مشروع التخرج"])
    + _rows("bmt", 4, 3, ["التنمية المستدامة", "التطوير التنظيمي", "موضوعات معاصرة في التسويق", "الإبداع وتصميم المنتجات الجديدة"])
)

ROWS = list(IMS)
for d in GEN:
    ROWS += [(d, lv, sm, t) for lv, sm, t in _GEN_ROWS]
ROWS += BIS + ACT + BMT

# English descriptions so the skill extractor has text to work with (keywords match the skill taxonomy).
DESC = {
 "مقدمة في الحاسبات": "Introduction to computers: hardware, software, operating systems and problem solving.",
 "الرياضيات المنفصلة": "Discrete mathematics: logic, sets, relations, graphs and probability for computer science.",
 "حزم التطبيقات المكتبية": "Office applications: Microsoft Excel spreadsheets, Word and PowerPoint presentation skills.",
 "مبادئ الإدارة": "Principles of management: planning, organizing, leadership and business management.",
 "مبادئ المحاسبة (1)": "Principles of accounting: bookkeeping, journal entries, general ledger and financial statements.",
 "مبادئ المحاسبة (2)": "Principles of accounting 2: financial statements, accounting cycle, bookkeeping and Excel.",
 "مقدمة في البرمجة": "Introduction to programming: Python basics, algorithms and problem solving.",
 "أساسيات تكنولوجيا المعلومات": "Information technology fundamentals: networking basics, internet, operating systems and technical support.",
 "لغة إنجليزية (1)": "English language: reading, writing and communication skills in English.",
 "لغة إنجليزية (2)": "English language 2: English writing, communication skills and report writing.",
 "أسس التفكير الناقد والعلمي": "Critical and scientific thinking: problem solving, research skills and analytical thinking.",
 "أسس التفكير النقدي والعلمي": "Critical and scientific thinking: problem solving, research skills and analytical thinking.",
 "تفاضل وتكامل": "Calculus: differentiation, integration and mathematics for problem solving.",
 "احتمالات وإحصاء": "Probability and statistics: statistics, statistical analysis and data analysis methods.",
 "مبادئ إحصاء": "Principles of statistics: statistics, statistical analysis and data analysis.",
 "إحصاء تطبيقي": "Applied statistics: statistical analysis, data analysis and Excel.",
 "أساسيات نظم المعلومات": "Fundamentals of information systems: databases, business systems and data analysis.",
 "رياضيات الحاسب": "Computer mathematics: linear algebra, mathematics and algorithms.",
 "برمجة الحاسب (1)": "Computer programming 1: Python programming, data structures and algorithms.",
 "برمجة الحاسب (2)": "Computer programming 2: object oriented programming, data structures and algorithms.",
 "تحليل وتصميم نظم المعلومات": "Systems analysis and design: systems analysis, UML diagrams, use cases, requirements gathering, database design and system design.",
 "مبادئ التسويق": "Principles of marketing: marketing, marketing research, digital marketing and communication skills.",
 "محاسبة متوسطة": "Intermediate accounting: accounting, financial statements, Excel and report writing.",
 "محاسبة متوسطة (1)": "Intermediate accounting 1: accounting, financial statements, Excel and report writing.",
 "محاسبة متوسطة (2)": "Intermediate accounting 2: accounting, financial statements, IFRS and report writing.",
 "شبكات الحاسب (1)": "Computer networks 1: networking, TCP/IP and network administration.",
 "شبكات الحاسب (2)": "Computer networks 2: advanced networking, routing and switching, network administration and firewalls.",
 "مقدمة في علم البيانات": "Introduction to data science: data analysis, statistics, Python, data cleaning and data visualization.",
 "نظم التشغيل": "Operating systems: operating systems, process scheduling, Linux and Windows administration.",
 "نظم معلومات الأعمال": "Business information systems: business analysis, databases, ERP and reporting.",
 "تطبيقات الخوارزميات": "Algorithm applications: algorithms, data structures and problem solving.",
 "تطبيقات في الأمن السيبراني": "Cybersecurity applications: cybersecurity, information security, cryptography, firewalls, intrusion detection and penetration testing basics.",
 "تكنولوجيا الوسائط المتعددة": "Multimedia technology: image processing, video editing and graphic design basics.",
 "تطبيقات الإنترنت": "Internet applications: HTML, CSS, JavaScript, REST APIs and web development.",
 "تكنولوجيا الانترنت": "Internet technologies: HTML, CSS, JavaScript, REST APIs and web development.",
 "مهارات التفاوض والاتصال": "Negotiation and communication skills: negotiation, communication, teamwork and presentation skills.",
 "الملكية الفكرية": "Intellectual property: copyright, patents and business law.",
 "القضايا المجتمعية": "Societal issues: communication and critical thinking.",
 "حقوق الإنسان": "Human rights: law and communication.",
 "علم الجودة": "Quality science: quality management, testing and process improvement.",
 "التنمية الذاتية": "Self development: communication, teamwork and time management.",
 "تقارير فنية باللغة الإنجليزية": "Technical reports in English: technical writing, report writing and English.",
 "أخلاقيات المهنة": "Professional ethics: ethics, communication and teamwork.",
 "قواعد البيانات": "Databases: SQL, database design, MySQL and data modeling.",
 "إدارة الموارد البشرية": "Human resources management: human resources, recruitment, communication and teamwork.",
 "أصول محاسبة التكاليف": "Cost accounting: cost accounting, costing, Excel and report writing.",
 "تعلم الآلة وتطبيقاتها": "Machine learning and applications: machine learning, Python, statistics and scikit-learn.",
 "الإدارة المالية": "Financial management: financial analysis, budgeting, forecasting, accounting and Excel.",
 "هياكل البيانات": "Data structures: data structures, algorithms and problem solving.",
 "معالجة الصور الرقمية وتطبيقاتها": "Digital image processing: image processing, Python, OpenCV and algorithms.",
 "التنقيب عن البيانات": "Data mining: data mining, clustering, classification, machine learning, statistics and Python.",
 "هندسة البرمجيات وتطبيقاتها": "Software engineering: software engineering, UML, software requirements, design patterns, testing, Git and project management.",
 "تطبيقات الحوسبة السحابية": "Cloud computing applications: cloud computing, AWS, cloud security and Docker basics.",
 "نظم الرسم بالحاسب": "Computer graphics systems: computer graphics, 3D programming and image processing.",
 "تراسل البيانات": "Data communications: networking, TCP/IP, network traffic analysis and signal transmission.",
 "التعلم العميق": "Deep learning: deep learning, neural networks, Python, TensorFlow and PyTorch.",
 "تشفير البيانات": "Data encryption: cryptography, encryption, PKI, hashing and cybersecurity.",
 "نظم حفظ واسترجاع المعلومات": "Information storage and retrieval: information retrieval, search engines, indexing, databases and SQL.",
 "معالجة اللغات الطبيعية": "Natural language processing: NLP, text mining, Python and machine learning.",
 "برمجة الذكاء الاصطناعي": "Artificial intelligence programming: machine learning, Python and problem solving.",
 "تطبيقات الموبايل": "Mobile applications: mobile development, Flutter, Firebase, REST APIs and UI/UX design.",
 "انترنت الأشياء": "Internet of Things: IoT, MQTT, sensors, embedded systems, Raspberry Pi and cloud computing.",
 "نظم قواعد المعرفة": "Knowledge-based systems: knowledge-based systems, expert systems, knowledge representation and artificial intelligence.",
 "تطبيقات الذكاء الاصطناعي": "AI applications: machine learning, deep learning, NLP and Python.",
 "الواقع الافتراضي": "Virtual reality: virtual reality, augmented reality, Unity, 3D programming and UI/UX design.",
 "مشروع التخرج": "Graduation project: project management, research, report writing, teamwork and presentation skills.",
 "معالجة الكلام": "Speech processing: speech processing, signal processing, machine learning and Python.",
 "البيانات الضخمة": "Big data: big data, Spark, Hadoop, data pipelines and ETL.",
 "الرؤية بالحاسب": "Computer vision: computer vision, OpenCV, object detection, image processing and deep learning.",
 "تطبيقات بالنمذجة والمحاكاة": "Modeling and simulation applications: simulation, mathematics, statistics and algorithms.",
 "معالجة الإشارات الرقمية": "Digital signal processing: signal processing, mathematics, algorithms and Python.",
 "أمن الشبكات": "Network security: cybersecurity, networking, firewalls, intrusion detection, network traffic analysis and cryptography.",
 "نقود وبنوك": "Money and banking: economics, banking, financial analysis and accounting.",
 "مبادئ الاقتصاد (1)": "Principles of economics 1: economics, microeconomics and analytical thinking.",
 "مبادئ الاقتصاد (2)": "Principles of economics 2: economics, macroeconomics and analytical thinking.",
 "مبادئ البرمجة للأعمال": "Programming for business: programming basics, algorithms and business problem solving.",
 "السلوك التنظيمي": "Organizational behavior: organizational behavior, management, teamwork and communication.",
 "لغات البرمجة للأعمال (1)": "Business programming languages 1: programming, SQL and object oriented programming.",
 "لغات البرمجة للأعمال (2)": "Business programming languages 2: programming, SQL, REST APIs and object oriented programming.",
 "التجارة الإلكترونية": "E-commerce: e-commerce, online store, digital marketing and payments.",
 "إدارة الإنتاج في بيئة التشغيل الإلكتروني": "Production management in electronic operating environment: supply chain, inventory management, ERP and operations research.",
 "القانون التجاري": "Commercial law: business law, commercial law and contracts law.",
 "الإعلام": "Media: communication, content creation and social media.",
 "أمن بيانات الأعمال": "Business data security: cybersecurity, information security, access control, cryptography and risk management.",
 "قواعد البيانات المتقدمة": "Advanced databases: SQL, database design, database administration, PostgreSQL and data warehousing.",
 "تطبيقات بحوث العمليات في التخصص": "Operations research applications: operations research, linear programming, optimization and decision support.",
 "نظم دعم القرار": "Decision support systems: decision support, data analysis, data visualization and business intelligence.",
 "تجارة إلكترونية متقدمة": "Advanced e-commerce: e-commerce, digital marketing, SEO and Google Analytics.",
 "موضوعات مختارة في نظم معلومات الأعمال": "Selected topics in business information systems: ERP, business analysis and data analysis.",
 "إدارة الملفات": "File management: databases, information retrieval and data organization.",
 "تطبيقات نظم معلومات الأعمال": "Business information systems applications: ERP, Odoo, business analysis and SQL.",
 "تحليل بيانات الأعمال": "Business data analytics: data analysis, data visualization, Power BI, Excel, SQL and statistics.",
 "نظم المعلومات الذكية": "Intelligent information systems: machine learning, artificial intelligence, data mining and databases.",
 "مستودعات البيانات": "Data warehouses: data warehousing, dimensional modeling, ETL and SQL.",
 "تطبيقات الموبايل في التخصص": "Mobile applications in the specialty: mobile development, REST APIs and UI/UX design.",
 "إدارة مشروعات البرمجيات": "Software project management: project management, Agile, Scrum and software engineering.",
 "نظم معلومات البنوك": "Banking information systems: banking, databases, information security and financial analysis.",
 "لغات البرمجة المتقدمة (1)": "Advanced programming languages 1: object oriented programming, Java, C# and algorithms.",
 "لغات البرمجة المتقدمة (2)": "Advanced programming languages 2: advanced programming, design patterns and testing.",
 "تحليل البيانات المتقدمة": "Advanced data analysis: data analysis, statistics, machine learning and Python.",
 "تطبيقات نظم معلومات الأعمال المتقدمة": "Advanced business information systems applications: ERP, business analysis, data warehousing and project management.",
 "محاسبة الموارد البشرية": "Human resources accounting: human resources, payroll, accounting and Excel.",
 "مبادئ المراجعة": "Principles of auditing: auditing, internal audit, internal controls and report writing.",
 "تطبيقات محاسبية باستخدام الجداول الإلكترونية": "Accounting applications with spreadsheets: Excel, accounting, financial statements and data analysis.",
 "محاسبة إدارية": "Management accounting: management accounting, cost accounting, budgeting and Excel.",
 "نظم المعلومات المحاسبية": "Accounting information systems: accounting software, accounting, databases and internal controls.",
 "تحليل القوائم المالية باستخدام الحاسب": "Financial statement analysis with computers: financial analysis, financial ratios, Excel and accounting.",
 "نظم التكاليف الرقمية": "Digital costing systems: cost accounting, costing, ERP and Excel.",
 "محاسبة دولية": "International accounting: IFRS, accounting, financial statements and English.",
 "المراجعة الإلكترونية لنظم المحاسبة": "Electronic auditing of accounting systems: auditing, internal controls, data analysis and information security.",
 "محاسبة المنشآت الخدمية": "Accounting for service entities: accounting, cost accounting and financial statements.",
 "المحاسبة الضريبية الإلكترونية (1)": "Electronic tax accounting 1: taxation, VAT, income tax and tax returns.",
 "المحاسبة الضريبية الإلكترونية (2)": "Electronic tax accounting 2: taxation, tax accounting, VAT and accounting software.",
 "تطبيقات الموبايل في المحاسبة": "Mobile applications in accounting: mobile development, accounting software and accounting.",
 "نظم المحاسبة الإلكترونية": "Electronic accounting systems: accounting software, ERP, accounting and databases.",
 "المحاسبة الإدارية المتقدمة": "Advanced management accounting: management accounting, cost accounting, budgeting and financial analysis.",
 "مراجعة متقدمة": "Advanced auditing: auditing, internal audit, risk management and data analysis.",
 "موضوعات مختارة في تكنولوجيا المحاسبة": "Selected topics in accounting technology: accounting software, accounting and data analysis.",
 "المحاسبة في التنمية المستدامة": "Accounting for sustainable development: accounting, report writing and research.",
 "نظم تكاليف البرمجيات": "Software costing systems: cost accounting, software engineering and project management.",
 "تكنولوجيا التسويق الرقمي": "Digital marketing technology: digital marketing, SEO, social media marketing, content marketing and Google Analytics.",
 "إدارة الأعمال الدولية": "International business management: management, economics, marketing and communication.",
 "إدارة سلاسل الإمداد": "Supply chain management: supply chain, logistics, inventory management and procurement.",
 "ريادة الأعمال": "Entrepreneurship: entrepreneurship, business plan, startup and feasibility study.",
 "الإدارة الإلكترونية لعلاقات العملاء": "Electronic customer relationship management: CRM, customer relationship management, marketing and data analysis.",
 "بحوث التسويق": "Marketing research: marketing research, statistics, data analysis and report writing.",
 "اقتصاديات الأعمال": "Business economics: economics, microeconomics, financial analysis and data analysis.",
 "الإدارة الاستراتيجية": "Strategic management: strategic management, business analysis and project management.",
 "دراسات جدوى المشروعات": "Project feasibility studies: feasibility study, financial analysis, business plan and Excel.",
 "الاتصالات الإدارية الرقمية": "Digital managerial communications: communication, presentation skills and teamwork.",
 "موضوعات مختارة في التخصص": "Selected topics in the specialty: research, report writing and presentation skills.",
 "التسويق الدولي": "International marketing: marketing, marketing strategy, economics and communication.",
 "تحليل الأسواق المالية": "Financial markets analysis: financial analysis, economics, statistics and Excel.",
 "التنمية المستدامة": "Sustainable development: research, management and report writing.",
 "التطوير التنظيمي": "Organizational development: organizational behavior, management and human resources.",
 "موضوعات معاصرة في التسويق": "Contemporary topics in marketing: marketing, social media marketing and content marketing.",
 "الإبداع وتصميم المنتجات الجديدة": "Creativity and new product design: product management, marketing and UI/UX design.",
 "اختياري جامعة": "University elective: communication skills.",
}
