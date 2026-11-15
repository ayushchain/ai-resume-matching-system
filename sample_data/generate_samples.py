"""Generate 12 synthetic resumes (PDF) + 1 sample JD (TXT).

All people below are fictional. Run:
    python generate_samples.py        (needs: reportlab)
Output: resumes/*.pdf and sample_jd.txt in this folder.
"""
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "resumes")
os.makedirs(OUT, exist_ok=True)

JD = """Senior Backend Developer - Python (Sample JD)

We are hiring a Backend Developer with 3+ years of experience building
web applications and REST APIs.

Required skills: Python, FastAPI, SQL, PostgreSQL, Docker, Git, REST API,
Testing, Linux, Redis.

Nice to have: AWS, Kubernetes, Machine Learning, Pandas, CI/CD, Kafka,
Microservices, System Design.

Qualifications: Bachelor's degree in Computer Science or a related field.
The candidate will design microservices, write unit testing with Pytest,
deploy with Docker on AWS, and work in an Agile team.
"""

RESUMES = [
    # name, email, exp-years-line, skills-line, summary
    ("Aarav Sharma", "aarav.sharma@example.com", "5 years of experience",
     "Python, FastAPI, PostgreSQL, SQL, Docker, Redis, AWS, Kubernetes, Pytest, Git, Linux, REST API, Microservices, Kafka, CI/CD",
     "Senior backend engineer. Built FastAPI microservices with PostgreSQL and Redis, deployed on AWS with Docker and Kubernetes. Strong testing culture with Pytest."),
    ("Priya Nair", "priya.nair@example.com", "4 years of experience",
     "Python, FastAPI, SQL, PostgreSQL, Docker, Git, REST API, Testing, Linux, Pandas, Machine Learning",
     "Backend developer working on Python APIs and data pipelines. Uses FastAPI, PostgreSQL, Docker daily; also builds ML features with Pandas."),
    ("Rohan Verma", "rohan.verma@example.com", "3 years of experience",
     "Python, Django, SQL, PostgreSQL, Docker, Git, REST API, Linux, Redis",
     "Backend developer with Django and PostgreSQL experience, REST API design, Docker deployments and Redis caching."),
    ("Sneha Kulkarni", "sneha.k@example.com", "3 years of experience",
     "Python, Flask, SQL, MySQL, Git, REST API, Testing, Linux",
     "Python developer building Flask APIs with MySQL. Comfortable with Git, Linux and writing tests."),
    ("Arjun Mehta", "arjun.mehta@example.com", "2 years of experience",
     "Python, FastAPI, SQL, Git, REST API, Docker",
     "Junior backend developer, FastAPI and SQL basics, Docker for local development."),
    ("Kavya Reddy", "kavya.reddy@example.com", "4 years of experience",
     "Java, Spring Boot, SQL, MySQL, Docker, Git, REST API, Linux, Microservices, Kafka",
     "Java backend engineer with Spring Boot microservices. Strong SQL, Docker and Kafka; new to Python."),
    ("Vikram Singh", "vikram.singh@example.com", "6 years of experience",
     "Python, Django, PostgreSQL, SQL, Docker, AWS, Git, REST API, Testing, Linux, Redis, Celery, System Design, Microservices",
     "Senior Python engineer, system design and microservices on AWS. Django, PostgreSQL, Redis, Docker, full testing practice. Note: Celery is not in our taxonomy on purpose."),
    ("Ananya Iyer", "ananya.iyer@example.com", "3 years of experience",
     "Data Science, Machine Learning, Python, Pandas, NumPy, scikit-learn, SQL, Statistics, Tableau",
     "Data scientist: machine learning models, Pandas analysis, SQL queries and dashboards. Limited backend API experience."),
    ("Rahul Patil", "rahul.patil@example.com", "2 years of experience",
     "JavaScript, React, Node.js, HTML, CSS, MongoDB, Git, REST API",
     "Frontend-leaning full stack developer with React and Node.js. Some REST API work, little Python."),
    ("Divya Menon", "divya.menon@example.com", "1 years of experience",
     "Python, SQL, Excel, Data Analysis, Pandas",
     "Recent graduate with internship experience in Python and data analysis using Pandas and Excel."),
    ("Karan Malhotra", "karan.m@example.com", "5 years of experience",
     "DevOps, Docker, Kubernetes, AWS, Linux, Terraform, Ansible, Jenkins, CI/CD, Git, Python",
     "DevOps engineer: Docker, Kubernetes, AWS, CI/CD pipelines. Writes Python automation scripts."),
    ("Meera Joshi", "meera.joshi@example.com", "0 years of experience",
     "HTML, CSS, JavaScript, Excel, Power BI",
     "Fresher with web basics and reporting tools. No backend or Python experience yet."),
]


def make_pdf(path, name, email, exp_line, skills, summary):
    c = canvas.Canvas(path, pagesize=A4)
    y = 800
    def line(txt, dy=18, size=11):
        nonlocal y
        c.setFont("Helvetica", size)
        # crude word wrap at 95 chars
        while len(txt) > 95:
            cut = txt.rfind(" ", 0, 95)
            c.drawString(50, y, txt[:cut]); y -= dy; txt = txt[cut + 1:]
        c.drawString(50, y, txt); y -= dy
    line(name, 20, 16)
    line(f"Email: {email} | Phone: +91 9000000000")
    line("")
    line("Professional Summary", 20, 13)
    line(summary)
    line("")
    line("Experience", 20, 13)
    line(f"Software Engineer — {exp_line} in software development roles.")
    line("")
    line("Skills", 20, 13)
    line(skills)
    line("")
    line("Education", 20, 13)
    line("B.Tech in Computer Science")
    c.save()


def main():
    with open(os.path.join(HERE, "sample_jd.txt"), "w") as f:
        f.write(JD)
    for i, (name, email, exp, skills, summary) in enumerate(RESUMES, 1):
        fname = f"{i:02d}_{name.replace(' ', '_')}.pdf"
        make_pdf(os.path.join(OUT, fname), name, email, exp, skills, summary)
        print("wrote", fname)
    print("wrote sample_jd.txt")


if __name__ == "__main__":
    main()
