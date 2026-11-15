"""Curated skill taxonomy (80+ skills) and extraction.

Simple idea: we keep a known list of tech skills. We search the
(lowercased) resume/JD text for each skill. Word-boundary aware, so
"Java" does not falsely match inside "JavaScript".
"""
import re

# Canonical name -> list of aliases seen in resumes/JDs
SKILL_TAXONOMY = {
    "Python": ["python"],
    "Java": ["java"],
    "JavaScript": ["javascript", "js"],
    "TypeScript": ["typescript"],
    "C++": ["c++", "cpp"],
    "C#": ["c#", "csharp"],
    "Go": ["golang"],
    "Rust": ["rust"],
    "SQL": ["sql"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3"],
    "React": ["react", "react.js", "reactjs"],
    "Angular": ["angular"],
    "Vue.js": ["vue", "vue.js", "vuejs"],
    "Node.js": ["node.js", "nodejs", "node"],
    "Express": ["express", "express.js"],
    "FastAPI": ["fastapi"],
    "Django": ["django"],
    "Flask": ["flask"],
    "Spring Boot": ["spring boot", "springboot"],
    "Spring": ["spring framework"],
    ".NET": [".net", "dotnet"],
    "PostgreSQL": ["postgresql", "postgres"],
    "MySQL": ["mysql"],
    "MongoDB": ["mongodb", "mongo"],
    "Redis": ["redis"],
    "SQLite": ["sqlite"],
    "Elasticsearch": ["elasticsearch"],
    "Machine Learning": ["machine learning", "ml"],
    "Deep Learning": ["deep learning"],
    "NLP": ["nlp", "natural language processing"],
    "TensorFlow": ["tensorflow"],
    "PyTorch": ["pytorch"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "Pandas": ["pandas"],
    "NumPy": ["numpy"],
    "Sentence Transformers": ["sentence transformers", "sentence-transformers"],
    "spaCy": ["spacy"],
    "Data Analysis": ["data analysis"],
    "Data Science": ["data science"],
    "Docker": ["docker"],
    "Kubernetes": ["kubernetes", "k8s"],
    "AWS": ["aws", "amazon web services"],
    "Azure": ["azure"],
    "GCP": ["gcp", "google cloud"],
    "Git": ["git"],
    "GitHub": ["github"],
    "CI/CD": ["ci/cd", "cicd"],
    "Jenkins": ["jenkins"],
    "Linux": ["linux"],
    "REST API": ["rest api", "restful", "rest apis"],
    "GraphQL": ["graphql"],
    "Microservices": ["microservices", "micro services"],
    "Kafka": ["kafka"],
    "RabbitMQ": ["rabbitmq"],
    "Testing": ["testing", "unit testing"],
    "Pytest": ["pytest"],
    "JUnit": ["junit"],
    "Selenium": ["selenium"],
    "Agile": ["agile", "scrum"],
    "System Design": ["system design"],
    "Data Structures": ["data structures", "dsa"],
    "Algorithms": ["algorithms"],
    "OOP": ["oop", "object oriented", "object-oriented programming"],
    "Power BI": ["power bi"],
    "Tableau": ["tableau"],
    "Excel": ["excel"],
    "Spark": ["spark", "apache spark"],
    "Hadoop": ["hadoop"],
    "Airflow": ["airflow"],
    "ETL": ["etl"],
    "Statistics": ["statistics"],
    "A/B Testing": ["a/b testing"],
    "Firebase": ["firebase"],
    "React Native": ["react native"],
    "Flutter": ["flutter"],
    "Android": ["android"],
    "iOS": ["ios"],
    "Kotlin": ["kotlin"],
    "Swift": ["swift"],
    "PHP": ["php"],
    "Laravel": ["laravel"],
    "Ruby": ["ruby"],
    "Rails": ["rails", "ruby on rails"],
    "Cybersecurity": ["cybersecurity", "cyber security"],
    "DevOps": ["devops"],
    "Terraform": ["terraform"],
    "Ansible": ["ansible"],
}


def extract_skills(text: str) -> list[str]:
    """Return sorted list of canonical skills found in text."""
    if not text:
        return []
    low = " " + re.sub(r"\s+", " ", text.lower()) + " "
    found = []
    for canonical, aliases in SKILL_TAXONOMY.items():
        for alias in aliases:
            # Boundary check: alias must not be glued to letters/digits on either side.
            # '+' '#' '.' are allowed inside aliases themselves.
            pattern = r"(?<![a-z0-9])" + re.escape(alias) + r"(?![a-z0-9])"
            if re.search(pattern, low):
                found.append(canonical)
                break
    return sorted(found)
