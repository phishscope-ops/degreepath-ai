"""v1.11: security/business skills, new tracks grounded in public sources,
faculty course catalog for all four MTIS departments."""

# (name, name_ar, category, aliases)
SKILLS2 = [
    ("SIEM", "مراقبة الأمن (SIEM)", "security", ["siem", "splunk", "wazuh", "elastic security", "qradar", "security information and event management", "سيم"]),
    ("Log Analysis", "تحليل السجلات", "security", ["log analysis", "log management", "logs analysis", "log sources", "تحليل السجلات", "تحليل اللوجات"]),
    ("Incident Response", "الاستجابة للحوادث", "security", ["incident response", "incident handling", "incident management", "الاستجابة للحوادث", "الاستجابة للاختراق"]),
    ("Threat Intelligence", "استخبارات التهديدات", "security", ["threat intelligence", "cyber threat intelligence", "cti", "ioc", "indicators of compromise", "استخبارات التهديدات"]),
    ("Threat Hunting", "صيد التهديدات", "security", ["threat hunting", "threat hunter", "صيد التهديدات"]),
    ("Network Traffic Analysis", "تحليل حركة الشبكة", "security", ["network traffic analysis", "packet analysis", "wireshark", "pcap", "packet capture", "network forensics", "تحليل حركة الشبكة"]),
    ("MITRE ATT&CK", "إطار MITRE ATT&CK", "security", ["mitre att&ck", "mitre attack", "att&ck", "attack framework", "kill chain", "ttps"]),
    ("Phishing Analysis", "تحليل التصيد", "security", ["phishing analysis", "phishing", "email security", "email headers", "spf dkim dmarc", "التصيد الاحتيالي", "تحليل التصيد"]),
    ("Digital Forensics", "الأدلة الرقمية", "security", ["digital forensics", "forensics", "dfir", "memory forensics", "disk forensics", "evidence preservation", "الأدلة الرقمية", "الطب الشرعي الرقمي"]),
    ("Vulnerability Management", "إدارة الثغرات", "security", ["vulnerability management", "vulnerability assessment", "vulnerability scanning", "nessus", "openvas", "patch management", "cve", "إدارة الثغرات", "فحص الثغرات"]),
    ("Cryptography", "التشفير", "security", ["cryptography", "encryption", "pki", "tls", "hashing", "التشفير", "تشفير البيانات"]),
    ("Web Application Security", "أمن تطبيقات الويب", "security", ["web application security", "owasp", "owasp top 10", "web security", "sql injection", "xss", "أمن تطبيقات الويب"]),
    ("Malware Analysis", "تحليل البرمجيات الخبيثة", "security", ["malware analysis", "reverse engineering", "malware", "sandbox analysis", "تحليل البرمجيات الخبيثة"]),
    ("Security Frameworks", "أطر ومعايير الأمن", "security", ["nist", "iso 27001", "iso/iec 27001", "cis controls", "nist csf", "soc 2", "pci dss", "security frameworks", "security compliance", "أطر الأمن", "معايير الأمن"]),
    ("Identity & Access Management", "إدارة الهوية والصلاحيات", "security", ["iam", "identity and access management", "access control", "mfa", "single sign-on", "sso", "إدارة الهوية"]),
    ("Firewalls & IDS/IPS", "الجدران النارية وكشف التسلل", "security", ["firewall", "firewalls", "ids/ips", "intrusion detection", "intrusion prevention", "suricata", "snort", "الجدران النارية", "كشف التسلل"]),
    ("Cloud Security", "أمن السحابة", "security", ["cloud security", "aws security", "shared responsibility", "cspm", "أمن السحابة"]),
    ("Risk Management", "إدارة المخاطر", "security", ["risk management", "risk assessment", "risk register", "إدارة المخاطر", "تقييم المخاطر"]),
    ("Endpoint Security (EDR)", "أمن الأجهزة (EDR)", "security", ["edr", "endpoint detection", "endpoint security", "sysmon", "crowdstrike", "أمن الأجهزة"]),
    ("Windows", "ويندوز", "it", ["windows administration", "windows 10", "windows 11", "windows os", "powershell", "ويندوز", "باورشيل"]),
    ("Accounting", "المحاسبة", "finance", ["accounting", "bookkeeping", "financial statements", "journal entries", "general ledger", "ifrs", "gaap", "المحاسبة", "محاسبة", "القوائم المالية"]),
    ("Cost Accounting", "محاسبة التكاليف", "finance", ["cost accounting", "costing", "cost systems", "managerial accounting", "management accounting", "محاسبة التكاليف", "المحاسبة الإدارية", "المحاسبة الادارية"]),
    ("Auditing", "المراجعة", "finance", ["auditing", "audit", "internal audit", "internal controls", "المراجعة", "مراجعة"]),
    ("Taxation", "الضرائب", "finance", ["taxation", "tax accounting", "vat", "income tax", "tax returns", "الضرائب", "المحاسبة الضريبية"]),
    ("Financial Analysis", "التحليل المالي", "finance", ["financial analysis", "financial modeling", "financial management", "financial ratios", "budgeting", "forecasting", "valuation", "التحليل المالي", "الإدارة المالية", "الادارة المالية"]),
    ("Accounting Software", "برامج المحاسبة", "finance", ["accounting software", "quickbooks", "tally", "zoho books", "sage", "برامج المحاسبة"]),
    ("Marketing", "التسويق", "business", ["marketing", "marketing research", "market research", "brand management", "marketing strategy", "التسويق", "بحوث التسويق"]),
    ("Human Resources", "الموارد البشرية", "business", ["human resources", "hr management", "recruitment", "payroll", "hris", "labor law", "الموارد البشرية", "التوظيف"]),
    ("Supply Chain", "سلاسل الإمداد", "business", ["supply chain", "logistics", "inventory management", "procurement", "demand planning", "سلاسل الامداد", "سلاسل الإمداد", "المخزون"]),
    ("Entrepreneurship", "ريادة الأعمال", "business", ["entrepreneurship", "startup", "business plan", "feasibility study", "ريادة الأعمال", "دراسات الجدوى"]),
    ("Economics", "الاقتصاد", "business", ["economics", "microeconomics", "macroeconomics", "business economics", "الاقتصاد", "اقتصاديات"]),
    ("Business Law", "القانون التجاري", "business", ["business law", "commercial law", "contracts law", "القانون التجاري"]),
    ("Management", "الإدارة", "business", ["management principles", "organizational behavior", "strategic management", "business management", "الإدارة", "السلوك التنظيمي", "الادارة الاستراتيجية"]),
    ("CRM", "إدارة علاقات العملاء", "business", ["crm", "customer relationship management", "salesforce", "hubspot crm", "إدارة علاقات العملاء"]),
    ("Operations Research", "بحوث العمليات", "business", ["operations research", "linear programming", "optimization", "decision support", "بحوث العمليات"]),
    ("E-commerce", "التجارة الإلكترونية", "business", ["e-commerce", "ecommerce", "online store", "shopify", "التجارة الالكترونية", "التجارة الإلكترونية"]),
    ("Mathematics", "الرياضيات", "science", ["mathematics", "calculus", "linear algebra", "discrete mathematics", "probability", "الرياضيات", "تفاضل وتكامل", "الرياضيات المنفصلة"]),
    ("Software Engineering", "هندسة البرمجيات", "software", ["software engineering", "software development life cycle", "sdlc", "uml", "software requirements", "design patterns", "هندسة البرمجيات", "دورة حياة تطوير البرمجيات"]),
    ("Operating Systems", "نظم التشغيل", "it", ["operating systems", "operating system concepts", "process scheduling", "نظم التشغيل"]),
    ("Computer Vision", "الرؤية بالحاسب", "ai", ["computer vision", "opencv", "object detection", "image classification", "الرؤية بالحاسب", "رؤية الحاسب"]),
    ("Image Processing", "معالجة الصور", "ai", ["image processing", "digital image processing", "image filtering", "معالجة الصور", "معالجة الصور الرقمية"]),
    ("IoT", "إنترنت الأشياء", "iot", ["iot", "internet of things", "mqtt", "sensors", "raspberry pi", "esp32", "انترنت الاشياء", "إنترنت الأشياء"]),
    ("Embedded Systems", "النظم المدمجة", "iot", ["embedded systems", "embedded c", "microcontrollers", "arduino", "firmware", "النظم المدمجة"]),
    ("Signal Processing", "معالجة الإشارات", "science", ["signal processing", "digital signal processing", "dsp", "speech processing", "معالجة الإشارات", "معالجة الكلام"]),
    ("Virtual Reality", "الواقع الافتراضي", "game", ["virtual reality", "augmented reality", "vr", "ar/vr", "الواقع الافتراضي"]),
    ("Data Mining", "التنقيب عن البيانات", "data", ["data mining", "association rules", "clustering", "classification", "التنقيب عن البيانات"]),
    ("Knowledge-Based Systems", "نظم قواعد المعرفة", "ai", ["knowledge-based systems", "expert systems", "knowledge representation", "ontologies", "نظم قواعد المعرفة"]),
    ("UML & Systems Analysis", "تحليل النظم (UML)", "software", ["systems analysis", "system analysis", "uml diagrams", "use cases", "process mapping", "bpmn", "تحليل النظم", "تحليل وتصميم النظم"]),
    ("Information Retrieval", "استرجاع المعلومات", "data", ["information retrieval", "search engines", "indexing", "استرجاع المعلومات"]),
    ("Presentation Skills", "مهارات العرض", "soft", ["presentation skills", "public speaking", "negotiation", "negotiation skills", "مهارات العرض", "مهارات التفاوض"]),
]

# Replace the required-skill list of these tracks (grounded in the sources below).
# (title) -> [(skill, importance)]  3 = core, 2 = middle, 1 = specialisation
TRACKS_REPLACE = {
    "Cybersecurity Analyst": [
        ("Networking", 3), ("Linux", 3), ("Windows", 2), ("Cybersecurity", 3), ("Log Analysis", 3),
        ("SIEM", 3), ("Incident Response", 3), ("Network Traffic Analysis", 2), ("Phishing Analysis", 2),
        ("MITRE ATT&CK", 2), ("Threat Intelligence", 2), ("Endpoint Security (EDR)", 2),
        ("Vulnerability Management", 2), ("Firewalls & IDS/IPS", 2), ("Python", 2), ("Report Writing", 2),
        ("Threat Hunting", 1), ("Digital Forensics", 1), ("Cloud Security", 1), ("Security Frameworks", 1),
        ("Cryptography", 1), ("Problem Solving", 1), ("Communication", 1), ("English", 1),
    ],
    "Penetration Tester": [
        ("Networking", 3), ("Linux", 3), ("Penetration Testing", 3), ("Cybersecurity", 3),
        ("Web Application Security", 3), ("Python", 2), ("Bash", 2), ("Vulnerability Management", 2),
        ("Windows", 2), ("Cryptography", 2), ("Report Writing", 2), ("Active Directory", 1),
        ("Malware Analysis", 1), ("Cloud Security", 1), ("Research", 1), ("Problem Solving", 1),
    ],
}

# New tracks: (title, title_ar, category, description, reqs)
NEW_TRACKS = [
    ("SOC Analyst", "محلل مركز عمليات الأمن (SOC)", "security",
     "Watch alerts in a Security Operations Center, triage them, investigate suspicious activity and escalate real incidents.",
     [("Networking", 3), ("Linux", 2), ("Windows", 3), ("Log Analysis", 3), ("SIEM", 3), ("Incident Response", 3),
      ("Phishing Analysis", 3), ("MITRE ATT&CK", 2), ("Threat Intelligence", 2), ("Endpoint Security (EDR)", 2),
      ("Network Traffic Analysis", 2), ("Firewalls & IDS/IPS", 2), ("Cybersecurity", 2), ("Report Writing", 2),
      ("Communication", 2), ("Threat Hunting", 1), ("Python", 1), ("Digital Forensics", 1)]),
    ("Digital Forensics & Incident Response Analyst", "محلل أدلة رقمية واستجابة للحوادث (DFIR)", "security",
     "Investigate cyber incidents, collect and analyze evidence from endpoints, memory, logs and network, and help recover safely.",
     [("Digital Forensics", 3), ("Incident Response", 3), ("Windows", 3), ("Linux", 2), ("Networking", 2), ("Log Analysis", 3),
      ("Malware Analysis", 2), ("Network Traffic Analysis", 2), ("Endpoint Security (EDR)", 2), ("Python", 2),
      ("Report Writing", 3), ("MITRE ATT&CK", 2), ("Threat Intelligence", 1), ("Cloud Security", 1), ("Cryptography", 1)]),
    ("GRC / Compliance Analyst", "محلل حوكمة ومخاطر وامتثال (GRC)", "security",
     "Run risk assessments, map controls to frameworks like ISO 27001 and NIST, collect evidence for audits and write security policies.",
     [("Security Frameworks", 3), ("Risk Management", 3), ("Cybersecurity", 3), ("Report Writing", 3), ("Auditing", 2),
      ("Identity & Access Management", 2), ("Communication", 3), ("Excel", 2), ("Business Analysis", 1),
      ("Vulnerability Management", 1), ("Cloud Security", 1), ("English", 2)]),
    ("Cloud Security Engineer", "مهندس أمن السحابة", "security",
     "Secure cloud accounts and workloads: identity and access, network controls, logging and detection on AWS or Azure.",
     [("Cloud Computing", 3), ("AWS", 3), ("Identity & Access Management", 3), ("Networking", 3), ("Linux", 2),
      ("Cloud Security", 3), ("Cybersecurity", 2), ("Python", 2), ("Terraform", 1), ("Docker", 1), ("Kubernetes", 1),
      ("Log Analysis", 2), ("Cryptography", 1), ("Git", 1)]),
    ("Accountant", "محاسب", "finance",
     "Keep financial records accurate and on time: journal entries, reconciliations, financial statements and tax filings, using accounting software and Excel.",
     [("Accounting", 3), ("Excel", 3), ("Accounting Software", 3), ("Taxation", 2), ("Cost Accounting", 2),
      ("Financial Analysis", 2), ("Auditing", 1), ("Report Writing", 2), ("Communication", 1), ("English", 1), ("ERP", 1)]),
    ("Auditor", "مراجع حسابات", "finance",
     "Plan and perform audits, test internal controls, document work papers and report findings, increasingly with data analytics.",
     [("Auditing", 3), ("Accounting", 3), ("Excel", 3), ("Risk Management", 2), ("Data Analysis", 2), ("Taxation", 1),
      ("Report Writing", 3), ("Communication", 2), ("Accounting Software", 1), ("English", 1), ("Security Frameworks", 1)]),
    ("Financial Analyst", "محلل مالي", "finance",
     "Study financial statements and trends, build forecasts and models in Excel, and present recommendations for decisions.",
     [("Financial Analysis", 3), ("Accounting", 3), ("Excel", 3), ("Data Analysis", 2), ("Statistics", 2), ("Economics", 2),
      ("Power BI", 1), ("SQL", 1), ("Report Writing", 2), ("Communication", 2), ("English", 1)]),
    ("HR Specialist", "أخصائي موارد بشرية", "business",
     "Handle recruitment, employee records, payroll inputs, policies and labor-law compliance, using an HRIS.",
     [("Human Resources", 3), ("Communication", 3), ("Excel", 2), ("Business Law", 2), ("Management", 2),
      ("Report Writing", 1), ("Teamwork", 2), ("English", 2), ("Data Analysis", 1)]),
    ("Supply Chain Analyst", "محلل سلاسل إمداد", "business",
     "Analyze inventory, demand and supplier data from the ERP, forecast demand and improve delivery and stock levels.",
     [("Supply Chain", 3), ("Excel", 3), ("ERP", 2), ("Data Analysis", 3), ("Operations Research", 2), ("SQL", 1),
      ("Power BI", 1), ("Statistics", 2), ("Communication", 2), ("Report Writing", 1), ("English", 1)]),
    ("Systems Analyst", "محلل نظم", "business",
     "Turn business needs into system requirements: interviews, process maps, UML models and testing with developers and users.",
     [("Business Analysis", 3), ("UML & Systems Analysis", 3), ("Database Design", 2), ("SQL", 2), ("Communication", 3),
      ("Project Management", 2), ("Testing", 2), ("Agile/Scrum", 2), ("Problem Solving", 2), ("Software Engineering", 2),
      ("Report Writing", 1), ("English", 1)]),
    ("IoT Engineer", "مهندس إنترنت الأشياء", "iot",
     "Build connected devices: firmware on microcontrollers, sensors, MQTT messaging and dashboards in the cloud.",
     [("Embedded Systems", 3), ("IoT", 3), ("C++", 3), ("Networking", 2), ("Python", 2), ("Linux", 2),
      ("Cloud Computing", 2), ("Cybersecurity", 1), ("Firebase", 1), ("Problem Solving", 2), ("Git", 1)]),
    ("Computer Vision Engineer", "مهندس رؤية بالحاسب", "ai",
     "Train and deploy models that understand images and video: classification, detection and segmentation.",
     [("Python", 3), ("Computer Vision", 3), ("Image Processing", 3), ("Deep Learning", 3), ("Machine Learning", 3),
      ("Mathematics", 2), ("NumPy", 2), ("PyTorch", 2), ("TensorFlow", 1), ("Docker", 1), ("Git", 1), ("Statistics", 2)]),
    ("Marketing Specialist", "أخصائي تسويق", "business",
     "Plan campaigns, run market research, manage brand and customer relationships and measure results.",
     [("Marketing", 3), ("Digital Marketing", 2), ("Communication", 3), ("CRM", 2), ("Data Analysis", 2), ("Google Analytics", 1),
      ("Content Marketing", 2), ("Economics", 1), ("Presentation Skills", 2), ("English", 1), ("Excel", 1)]),
    ("E-commerce Specialist", "أخصائي تجارة إلكترونية", "business",
     "Run an online store: catalog, orders, payments, SEO and ads, and sales analytics.",
     [("E-commerce", 3), ("Digital Marketing", 2), ("SEO", 2), ("Google Analytics", 2), ("Excel", 2), ("Supply Chain", 1),
      ("Social Media Marketing", 2), ("Communication", 2), ("CRM", 1), ("English", 1)]),
    ("BI Developer", "مطور ذكاء أعمال (BI)", "data",
     "Build data models, ETL pipelines and dashboards that turn company data into reports for decision makers.",
     [("SQL", 3), ("Power BI", 3), ("Data Visualization", 3), ("Data Warehousing", 3), ("ETL", 2), ("Data Analysis", 2),
      ("Excel", 2), ("Business Analysis", 2), ("Database Design", 2), ("Python", 1), ("Communication", 2)]),
    ("ERP Functional Consultant", "مستشار ERP وظيفي", "business",
     "Map business processes, configure ERP modules (finance, supply chain, HR), train users and close gaps between needs and the system.",
     [("ERP", 3), ("Business Analysis", 3), ("Accounting", 2), ("Supply Chain", 2), ("Human Resources", 1), ("UML & Systems Analysis", 2),
      ("SQL", 1), ("Odoo", 1), ("Communication", 3), ("Project Management", 2), ("Testing", 1), ("English", 2)]),
    ("Tax Accountant", "محاسب ضرائب", "finance",
     "Prepare tax returns and VAT filings, compute taxes owed and keep the company compliant with tax rules.",
     [("Taxation", 3), ("Accounting", 3), ("Excel", 3), ("Accounting Software", 2), ("Business Law", 2), ("Financial Analysis", 1),
      ("Report Writing", 1), ("Communication", 1), ("English", 1)]),
    ("Cost Accountant", "محاسب تكاليف", "finance",
     "Set standard costs, analyze material, labor and overhead variances, value inventory and report product profitability.",
     [("Cost Accounting", 3), ("Accounting", 3), ("Excel", 3), ("ERP", 2), ("Financial Analysis", 2), ("Data Analysis", 1),
      ("Accounting Software", 1), ("Report Writing", 2), ("Communication", 1)]),
    ("Procurement Specialist", "أخصائي مشتريات", "business",
     "Source and qualify suppliers, manage purchase orders and contracts, and analyze cost across the procure-to-pay process.",
     [("Supply Chain", 3), ("Excel", 2), ("ERP", 2), ("Business Law", 2), ("Presentation Skills", 3), ("Financial Analysis", 1),
      ("Communication", 3), ("Data Analysis", 1), ("English", 1)]),
]

# Sources actually read for each track (label, url). Shown on the track page.
TRACK_SOURCES = {
    "Cybersecurity Analyst": [("roadmap.sh: Cyber Security", "https://roadmap.sh/cyber-security"),
        ("CyberA4U: SOC Analyst roadmap", "https://www.cybera4u.com/roadmaps/soc-analyst"),
        ("Hack The Box: 13 skills for SOC analysts", "https://www.hackthebox.com/blog/13-essential-skills-for-soc-analysts"),
        ("ITlearn360: SOC Analyst roadmap", "https://www.itlearn360.com/career-paths/soc-analyst/")],
    "SOC Analyst": [("CyberA4U: SOC Analyst roadmap", "https://www.cybera4u.com/roadmaps/soc-analyst"),
        ("Hack The Box: 13 skills for SOC analysts", "https://www.hackthebox.com/blog/13-essential-skills-for-soc-analysts"),
        ("ITlearn360: SOC Analyst roadmap", "https://www.itlearn360.com/career-paths/soc-analyst/")],
    "Penetration Tester": [("roadmap.sh: Cyber Security", "https://roadmap.sh/cyber-security"),
        ("PortSwigger Web Security Academy", "https://portswigger.net/web-security")],
    "Digital Forensics & Incident Response Analyst": [("SANS: DFIR course roadmap", "https://www.sans.org/blog/sans-dfir-course-roadmap-and-job-role-matrix"),
        ("Canadian Cyber Security Skills Framework: Digital Forensics Analyst", "https://www.cyber.gc.ca/en/education-community/academic-outreach-cyber-skills-development/canadian-cyber-security-skills-framework/digital-forensics-analyst"),
        ("SecByte: DFIR Analyst roadmap", "https://learn.secbyte.org/roadmaps/dfir-analyst-6ew")],
    "GRC / Compliance Analyst": [("GRC with Gaurav: GRC analyst roadmap", "https://grcwithgaurav.com/learn/grc-analyst-career-roadmap"),
        ("NHIMG: GRC analyst career guide", "https://nhimg.org/grc-analyst-career-guide"),
        ("Noblerworks: GRC analyst certification roadmap", "https://security.noblerworks.com/resources/certification-roadmap-grc-analyst/")],
    "Cloud Security Engineer": [("AWS Builder: cloud security engineer roadmap", "https://builder.aws.com/content/3Jxi3JyQBeGKAcCc8mcCpokRbbP/from-zero-to-cloud-security-engineer-a-practical-aws-roadmap"),
        ("ShieldSync: cloud security engineer roadmap", "https://shieldsyncsecurity.com/blog/cloud-security-engineer-roadmap"),
        ("AWS: Security Engineering on AWS course outline", "https://d1.awsstatic.com/training-and-certification/classroom-training/security-engineering-on-aws.pdf")],
    "Accountant": [("SkillDrift: accountant roadmap", "https://www.skilldrift.ai/career-roadmap/accountant"),
        ("KSCPA: roadmap to an accounting career", "https://www.kscpa.org/ignite-blog/a-roadmap-to-a-successful-accounting-career"),
        ("Intuit Academy: accounting skills", "https://academy.intuit.com/blog/job-readiness/accounting/accounting-skills/")],
    "Auditor": [("The IIA: Internal Auditing Competency Framework", "https://www.theiia.org/globalassets/site/content/guidance/recommended/supplemental/practice-guides/global-practice-guide-internal-auditing-competency-framework/gpg_internal_auditing_competency_framework_english.pdf"),
        ("The IIA: Global Model Internal Audit Curriculum", "https://www.theiia.org/globalassets/site/about-us/academic-alliance/global-model-internal-audit-curriculum.pdf")],
    "Financial Analyst": [("Kaplan: financial analyst skills", "https://www.kaplanfinancial.com/resources/getting-started/financial-analyst-skills"),
        ("Santa Clara University: how to become a financial analyst", "https://www.scu.edu/business/blog/careers/how-to-become-a-financial-analyst/"),
        ("CFA Institute: why Excel skills matter in finance", "https://www.cfainstitute.org/insights/articles/why-excel-skills-matter-in-finance")],
    "HR Specialist": [("Workable: HR specialist job description", "https://resources.workable.com/hr-specialist-job-description"),
        ("HR University: HR generalist skills", "https://hr.university/career/hr-generalist/hr-generalist-skills/"),
        ("O*NET: Human Resources Specialists", "https://www.onetonline.org/link/details/13-1071.00")],
    "Supply Chain Analyst": [("Rework: supply chain analyst job description", "https://resources.rework.com/libraries/job-description-templates/supply-chain-analyst"),
        ("TE Connectivity: Supply Chain Analyst posting", "https://careers.te.com/job/SUPPLY-CHAIN-ANALYST-III-%28GLOBAL-DC-PLANNER%29/159945-en_US/")],
    "Systems Analyst": [("Adaface: skills required for a system analyst", "https://www.adaface.com/blog/skills-required-for-system-analyst/"),
        ("O*NET: Computer Systems Analysts", "https://www.onetonline.org/link/summary/15-1211.00"),
        ("Training.gov.au: ICTPRG444 Analyse software requirements", "https://training.gov.au/training/details/ICTPRG444/uoc")],
    "IoT Engineer": [("Sefism: embedded and IoT roadmap", "https://www.sefism.com/resources/sefism-embedded-iot-roadmap/"),
        ("BeInCareer: IoT engineer roadmap", "https://beincareer.com/iot-engineer-roadmap-2026/"),
        ("EmbedSkills: learning roadmap", "https://embeddskills.com/learning-roadmap/")],
    "Computer Vision Engineer": [("OpenCV: computer vision engineer roadmap", "https://opencv.org/computer-vision-engineer-roadmap/"),
        ("Roadmap Creator: computer vision engineer roadmap", "https://www.roadmap-creator.com/blog/computer-vision-engineer-roadmap"),
        ("CV Handbook roadmap", "https://jayanthappalla.com/cv-handbook/roadmap/")],
    "BI Developer": [("BCS: how to become a BI developer", "https://www.bcs.org/articles-opinion-and-research/how-to-become-a-business-intelligence-developer/"),
        ("NC State: BI developer/architect skills in job postings", "https://online-distance.ncsu.edu/career/business-intelligence-developer-architect/"),
        ("University of San Diego: BI developer skills", "https://onlinedegrees.sandiego.edu/business-intelligence-developer/")],
    "ERP Functional Consultant": [("InfoQI: skills map for an ERP functional consultant", "https://www.infoqi.com/a-complete-skills-map-for-an-erp-functional-consultant/"),
        ("Robert Half: ERP functional consultant", "https://www.roberthalf.com/gb/en/job-details/erp-functional-consultant"),
        ("Kore1: ERP consultant career guide", "https://www.kore1.com/erp-consultant-career-guide/")],
    "Tax Accountant": [("Robert Half: tax accountant", "https://www.roberthalf.com/gb/en/job-details/tax-accountant"),
        ("O*NET: Tax Preparers", "https://www.onetonline.org/link/summary/13-2082.00")],
    "Cost Accountant": [("4 Corner Resources: cost accountant", "https://www.4cornerresources.com/job-descriptions/cost-accountant/"),
        ("Robert Half: cost accountant", "https://www.roberthalf.com/nz/en/job-details/cost-accountant"),
        ("ACCA: FMA syllabus (standard costing, variances)", "https://www.accaglobal.com/content/dam/acca/global/PDF-students/fia/studyguides/MA.FMA%20S25-A26%20syllabus%20and%20study%20guide%20-%20final.pdf")],
    "Procurement Specialist": [("GESG: procurement specialist skills", "https://gesg.com/career-roadmaps/supply-chain-demand-planning/procurement-specialist/"),
        ("CIPS: procurement specialist profile", "https://www.cips.org/careers/job-profiles/procurement-specialist")],
    "Data Analyst": [("roadmap.sh: Data Analyst", "https://roadmap.sh/data-analyst")],
    "Frontend Developer": [("roadmap.sh: Frontend", "https://roadmap.sh/frontend")],
    "Backend Developer": [("roadmap.sh: Backend", "https://roadmap.sh/backend")],
    "DevOps Engineer": [("roadmap.sh: DevOps", "https://roadmap.sh/devops")],
    "Data Scientist": [("roadmap.sh: AI and Data Scientist", "https://roadmap.sh/ai-data-scientist")],
    "Full-Stack Developer": [("roadmap.sh: Full Stack", "https://roadmap.sh/full-stack")],
}

# Free resources for the new skills (verified reachable before release).
RESOURCES2 = [
    ("SIEM", "Wazuh documentation (free, open source SIEM)", "https://documentation.wazuh.com/current/getting-started/index.html", "course"),
    ("SIEM", "Elastic Security documentation", "https://www.elastic.co/guide/en/security/current/index.html", "course"),
    ("Log Analysis", "NIST SP 800-92: Guide to Computer Security Log Management", "https://csrc.nist.gov/pubs/sp/800/92/final", "course"),
    ("Incident Response", "NIST SP 800-61 Rev. 3: Incident Response Recommendations", "https://csrc.nist.gov/pubs/sp/800/61/r3/final", "course"),
    ("Incident Response", "CISA incident and vulnerability response playbooks", "https://www.cisa.gov/resources-tools/resources/federal-government-cybersecurity-incident-and-vulnerability-response-playbooks", "course"),
    ("Threat Intelligence", "MISP open source threat intelligence platform", "https://www.misp-project.org/documentation/", "course"),
    ("MITRE ATT&CK", "MITRE ATT&CK training (free)", "https://attack.mitre.org/resources/learn-more-about-attack/training/", "course"),
    ("Phishing Analysis", "CISA phishing guidance", "https://www.cisa.gov/resources-tools/resources/phishing-guidance-stopping-attack-cycle-phase-one", "course"),
    ("Network Traffic Analysis", "Wireshark documentation", "https://www.wireshark.org/docs/", "course"),
    ("Network Traffic Analysis", "Malware-Traffic-Analysis.net tutorials", "https://www.malware-traffic-analysis.net/tutorials/index.html", "practice"),
    ("Digital Forensics", "CyberDefenders blue team labs (free tier)", "https://cyberdefenders.org/", "practice"),
    ("Vulnerability Management", "Greenbone (OpenVAS) documentation", "https://greenbone.github.io/docs/latest/", "course"),
    ("Cryptography", "Khan Academy: Cryptography", "https://www.khanacademy.org/computing/computer-science/cryptography", "course"),
    ("Web Application Security", "OWASP Top 10", "https://owasp.org/www-project-top-ten/", "course"),
    ("Web Application Security", "PortSwigger Web Security Academy (free)", "https://portswigger.net/web-security", "course"),
    ("Malware Analysis", "Malware Unicorn: Reverse Engineering 101", "https://malwareunicorn.org/workshops/re101.html", "course"),
    ("Security Frameworks", "NIST Cybersecurity Framework", "https://www.nist.gov/cyberframework", "course"),
    ("Security Frameworks", "CIS Critical Security Controls", "https://www.cisecurity.org/controls", "course"),
    ("Cloud Security", "Cloud Security Alliance: Security Guidance", "https://cloudsecurityalliance.org/research/guidance", "course"),
    ("Risk Management", "NIST SP 800-30: Guide for Conducting Risk Assessments", "https://csrc.nist.gov/pubs/sp/800/30/r1/final", "course"),
    ("Firewalls & IDS/IPS", "Suricata documentation", "https://docs.suricata.io/", "course"),
    ("Endpoint Security (EDR)", "Microsoft Sysinternals: Sysmon", "https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon", "course"),
    ("Windows", "Microsoft Learn: Windows Server administration", "https://learn.microsoft.com/en-us/training/browse/?products=windows-server", "course"),
    ("Accounting", "OpenStax: Principles of Financial Accounting (free book)", "https://openstax.org/details/books/principles-financial-accounting", "course"),
    ("Cost Accounting", "OpenStax: Principles of Managerial Accounting (free book)", "https://openstax.org/details/books/principles-managerial-accounting", "course"),
    ("Marketing", "OpenStax: Principles of Marketing (free book)", "https://openstax.org/details/books/principles-marketing", "course"),
    ("Management", "OpenStax: Principles of Management (free book)", "https://openstax.org/details/books/principles-management", "course"),
    ("Human Resources", "OpenStax: Principles of Management, HR chapters (free book)", "https://openstax.org/details/books/principles-management", "course"),
    ("Entrepreneurship", "OpenStax: Entrepreneurship (free book)", "https://openstax.org/details/books/entrepreneurship", "course"),
    ("Economics", "OpenStax: Principles of Economics (free book)", "https://openstax.org/details/books/principles-economics-3e", "course"),
    ("Business Law", "OpenStax: Business Law I Essentials (free book)", "https://openstax.org/details/books/business-law-i-essentials", "course"),
    ("Mathematics", "Khan Academy: Linear Algebra", "https://www.khanacademy.org/math/linear-algebra", "course"),
    ("Operating Systems", "Operating Systems: Three Easy Pieces (free book)", "https://pages.cs.wisc.edu/~remzi/OSTEP/", "course"),
    ("Computer Vision", "OpenCV University: free OpenCV course", "https://opencv.org/university/free-opencv-course/", "course"),
    ("Image Processing", "OpenCV University: free OpenCV course", "https://opencv.org/university/free-opencv-course/", "course"),
    ("IoT", "MQTT: getting started", "https://mqtt.org/getting-started/", "course"),
    ("Embedded Systems", "Arduino documentation: Learn", "https://docs.arduino.cc/learn/", "course"),
    ("Virtual Reality", "Unity Learn (free)", "https://learn.unity.com/", "course"),
    ("Signal Processing", "MIT OCW: Signals and Systems", "https://ocw.mit.edu/courses/6-003-signals-and-systems-fall-2011/", "course"),
    ("Operations Research", "MIT OCW: Optimization Methods in Management Science", "https://ocw.mit.edu/courses/15-053-optimization-methods-in-management-science-spring-2013/", "course"),
    ("CRM", "HubSpot Academy (free courses)", "https://academy.hubspot.com/", "course"),
    ("E-commerce", "HubSpot Academy: e-commerce marketing (free)", "https://academy.hubspot.com/", "course"),
    ("Information Retrieval", "Stanford: Introduction to Information Retrieval (free book)", "https://nlp.stanford.edu/IR-book/", "course"),
    ("Data Mining", "Stanford: Mining of Massive Datasets (free book)", "http://www.mmds.org/", "course"),
    ("UML & Systems Analysis", "UML Diagrams guide (free)", "https://www.uml-diagrams.org/", "course"),
    ("Taxation", "Egyptian Tax Authority", "https://eta.gov.eg/", "course"),
]


def _skill_ids(db):
    return {r["name"]: r["id"] for r in db.execute("SELECT id, name FROM skills").fetchall()}


def apply_v2(db, _unused=None):
    """Idempotent: safe at every startup, never touches user data."""
    for name, name_ar, category, aliases in SKILLS2:
        db.execute("INSERT OR IGNORE INTO skills (name, name_ar, category) VALUES (?, ?, ?)",
                   (name, name_ar, category))
        sid = db.execute("SELECT id FROM skills WHERE name = ?", (name,)).fetchone()["id"]
        for alias in set(aliases + [name]):
            db.execute("INSERT OR IGNORE INTO skill_aliases (alias, skill_id) VALUES (?, ?)", (alias, sid))
    sid = _skill_ids(db)

    def job_id(title):
        r = db.execute("SELECT id FROM jobs WHERE title = ?", (title,)).fetchone()
        return r["id"] if r else None

    def set_reqs(jid, reqs):
        want = {sid[n]: imp for n, imp in reqs}
        have = {r["skill_id"]: r["importance"] for r in db.execute(
            "SELECT skill_id, importance FROM job_skills WHERE job_id = ?", (jid,)).fetchall()}
        if want == have:
            return
        db.execute("DELETE FROM job_skills WHERE job_id = ?", (jid,))
        for k, imp in want.items():
            db.execute("INSERT INTO job_skills (job_id, skill_id, importance) VALUES (?, ?, ?)", (jid, k, imp))

    for title, reqs in TRACKS_REPLACE.items():
        jid = job_id(title)
        if jid:
            set_reqs(jid, reqs)
    for title, title_ar, category, desc, reqs in NEW_TRACKS:
        jid = job_id(title)
        if jid is None:
            jid = db.execute("INSERT INTO jobs (title, title_ar, category, description) VALUES (?, ?, ?, ?)",
                             (title, title_ar, category, desc)).lastrowid
        set_reqs(jid, reqs)
    for title, srcs in TRACK_SOURCES.items():
        jid = job_id(title)
        if not jid:
            continue
        for label, url in srcs:
            db.execute("INSERT OR IGNORE INTO job_sources (job_id, label, url) VALUES (?, ?, ?)", (jid, label, url))
    for skill_name, title, url, kind in RESOURCES2:
        k = sid.get(skill_name)
        if k and not db.execute("SELECT 1 FROM resources WHERE skill_id = ? AND url = ?", (k, url)).fetchone():
            db.execute("INSERT INTO resources (skill_id, title, url, kind) VALUES (?, ?, ?, ?)", (k, title, url, kind))

    # Faculty catalog (all four departments). Replaces the old single-department list once.
    from .catalog2 import DESC, ROWS
    have = db.execute("SELECT COUNT(*) AS c FROM course_catalog WHERE department = 'bmt'").fetchone()["c"]
    if not have:
        db.execute("DELETE FROM course_catalog")
        for dept, level, sem, title in ROWS:
            kind = "elective" if sem == 3 or title.startswith("اختياري") else "core"
            db.execute(
                "INSERT INTO course_catalog (title, level, semester, description, department, kind) VALUES (?, ?, ?, ?, ?, ?)",
                (title, level, sem, DESC.get(title, ""), dept, kind))
