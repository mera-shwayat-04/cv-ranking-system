from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import pdfplumber
import re
import numpy as np
import csv

app = FastAPI()

model = None
st_util = None

def get_model():
    global model, st_util
    if model is None:
        from sentence_transformers import SentenceTransformer, util
        model = SentenceTransformer("all-MiniLM-L6-v2")
        st_util = util
    return model, st_util


app.mount("/static", StaticFiles(directory="static"), name="static")

HR_EMAIL = "hr@example.com"
HR_PASSWORD = "123456"
is_logged_in = False
last_top_results = []
last_results_html = ""
shortlisted_candidates = []

SKILLS = [
    "python", "machine learning", "data analysis", "fastapi", "api", "apis",
    "pandas", "scikit-learn", "sklearn", "tensorflow", "pytorch", "nlp",
    "sql", "excel", "power bi", "tableau", "deep learning",
    "java", "javascript", "react", "html", "css", "backend", "frontend",
    "django", "flask", "numpy", "matplotlib", "git", "github",
    "بايثون", "تعلم الاله", "تحليل البيانات", "ذكاء اصطناعي",
    "معالجه اللغه الطبيعيه", "قواعد البيانات", "واجهات برمجيه"
]


@app.get("/")
def home():
    return RedirectResponse(url="/login")


@app.get("/login", response_class=HTMLResponse)
def login_page():
    return """
    <html>
    <head>
        <title>HR Login</title>
        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                height: 100vh;
                color: white;
                display: flex;
                align-items: center;
                justify-content: center;
                background:
                    linear-gradient(rgba(15, 23, 42, 0.78), rgba(15, 23, 42, 0.88)),
                    url('/static/logo.png') center/cover no-repeat;
            }

            .box {
                width: 430px;
                background: rgba(30, 41, 59, 0.82);
                padding: 38px;
                border-radius: 24px;
                box-shadow: 0 30px 80px rgba(0,0,0,0.65);
                text-align: center;
                border: 1px solid rgba(148, 163, 184, 0.25);
                backdrop-filter: blur(10px);
            }

            .robot {
                font-size: 58px;
                animation: float 2.5s infinite;
                margin-bottom: 10px;
            }

            @keyframes float {
                0%,100% { transform:translateY(0); }
                50% { transform:translateY(-10px); }
            }

            h2 {
                margin: 0;
                font-size: 28px;
            }

            p {
                color: #cbd5e1;
                margin-bottom: 25px;
            }

            input {
                width:100%;
                padding:14px;
                margin-top:15px;
                border-radius:14px;
                border:1px solid #475569;
                background:rgba(15, 23, 42, 0.9);
                color:white;
                outline: none;
            }

            input:focus {
                border-color: #8b5cf6;
                box-shadow: 0 0 0 3px rgba(139, 92, 246, 0.25);
            }

            button {
                width:100%;
                margin-top:25px;
                padding:14px;
                border:none;
                border-radius:14px;
                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                color:white;
                font-weight:bold;
                cursor:pointer;
                font-size: 16px;
                transition: 0.3s;
            }

            button:hover {
                transform: translateY(-2px);
                box-shadow: 0 12px 30px rgba(139, 92, 246, 0.4);
            }
        </style>
    </head>

    <body>
        <div class="box">
            <div class="robot">🧑‍💼</div>
            <h2>HR Login</h2>
            <p>Access the AI Resume Screening System</p>

            <form action="/login" method="post">
                <input type="email" name="email" placeholder="Email" required>
                <input type="password" name="password" placeholder="Password" required>
                <button>Login</button>
            </form>
        </div>
    </body>
    </html>
    """


@app.post("/login")
def login(email: str = Form(...), password: str = Form(...)):
    global is_logged_in

    if email == HR_EMAIL and password == HR_PASSWORD:
        is_logged_in = True
        return RedirectResponse(url="/upload", status_code=303)

    return HTMLResponse("""
    <body style="background:#0f172a;color:white;font-family:Arial;text-align:center;padding-top:100px;">
        <h2>Invalid email or password</h2>
        <a href="/login" style="color:#8b5cf6;">Try again</a>
    </body>
    """)


@app.get("/logout")
def logout():
    global is_logged_in
    is_logged_in = False
    return RedirectResponse(url="/login")


@app.get("/upload", response_class=HTMLResponse)
def upload_page():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    return """
    <html>
    <head>
        <title>CV Ranking System</title>
        <style>
            * { box-sizing: border-box; }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                min-height: 100vh;
            }

            .header {
                height: 220px;
                background:
                    linear-gradient(rgba(15,23,42,0.45), rgba(15,23,42,0.95)),
                    url('/static/logo.png') center/cover no-repeat;
                display: flex;
                align-items: center;
                justify-content: center;
                text-align: center;
                position: relative;
                border-bottom: 1px solid #334155;
            }

            .header h1 {
                font-size: 42px;
                margin: 0;
                text-shadow: 0 4px 18px rgba(0,0,0,0.7);
            }

            .header p {
                color: #cbd5e1;
                font-size: 17px;
                margin-top: 10px;
            }

            .logout {
                position: absolute;
                top: 18px;
                right: 28px;
                color: white;
                text-decoration: none;
                background: rgba(30,41,59,0.85);
                border: 1px solid #475569;
                padding: 10px 16px;
                border-radius: 12px;
            }

            .layout {
                width: 94%;
                max-width: 1280px;
                margin: 22px auto 45px;
                display: grid;
                grid-template-columns: 1fr 1.45fr 1fr;
                gap: 16px;
                align-items: stretch;
            }

            .card {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 22px;
                box-shadow: 0 18px 45px rgba(0,0,0,0.35);
                padding: 26px;
                animation: softFloat 4s ease-in-out infinite;
            }

            .card:nth-child(2) { animation-delay: .4s; }
            .card:nth-child(3) { animation-delay: .8s; }

            @keyframes softFloat {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-6px); }
            }

            .main-card { padding: 34px; }

            h2, h3 {
                margin-top: 0;
                color: white;
            }

            .muted {
                color: #94a3b8;
                line-height: 1.6;
            }

            .step {
                display: flex;
                gap: 12px;
                margin: 18px 0;
                align-items: flex-start;
            }

            .step-number {
                width: 34px;
                height: 34px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                display: flex;
                align-items: center;
                justify-content: center;
                font-weight: bold;
                flex-shrink: 0;
            }

            label {
                display: block;
                margin-top: 18px;
                color: #cbd5e1;
                font-weight: bold;
            }

            textarea {
                width: 100%;
                height: 135px;
                margin-top: 10px;
                padding: 14px;
                border-radius: 14px;
                border: 1px solid #475569;
                background: #0f172a;
                color: white;
                font-size: 14px;
                resize: none;
                outline: none;
            }

            input[type="file"] {
                width: 100%;
                margin-top: 10px;
                padding: 14px;
                border-radius: 14px;
                border: 2px dashed #6366f1;
                background: #0f172a;
                color: #cbd5e1;
            }

            button {
                width: 100%;
                margin-top: 26px;
                padding: 15px;
                border: none;
                border-radius: 14px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                color: white;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
            }

            .assistant { text-align: center; }

            .big-robot {
                font-size: 64px;
                animation: robotMove 2.5s ease-in-out infinite;
                margin-bottom: 10px;
            }

            .robot {
                position: fixed;
                bottom: 25px;
                right: 30px;
                font-size: 50px;
                animation: robotMove 2.5s ease-in-out infinite;
            }

            @keyframes robotMove {
                0%, 100% { transform: translateY(0); }
                50% { transform: translateY(-12px); }
            }

            .stat {
                background: #0f172a;
                border: 1px solid #334155;
                padding: 14px;
                border-radius: 14px;
                margin-top: 12px;
            }

            .stat strong {
                display: block;
                color: #a78bfa;
                font-size: 20px;
            }

            .loading {
                display: none;
                position: fixed;
                inset: 0;
                background: rgba(15,23,42,0.9);
                z-index: 999;
                align-items: center;
                justify-content: center;
                flex-direction: column;
            }

            .loader {
                width: 70px;
                height: 70px;
                border: 6px solid #334155;
                border-top: 6px solid #8b5cf6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                to { transform: rotate(360deg); }
            }
        </style>
    </head>

    <body>
        <div class="header">
            <a href="/logout" class="logout">Logout</a>
            <div>
                <h1>AI Resume Screening System</h1>
                <p>Smart CV Ranking & Candidate Matching</p>
            </div>
        </div>

        <div class="layout">
            <div class="card">
                <h3>How It Works</h3>
                <p class="muted">The system analyzes CVs and compares them with the job description.</p>

                <div class="step"><div class="step-number">1</div><div><strong>Upload CVs</strong><p class="muted">Add multiple PDF resumes.</p></div></div>
                <div class="step"><div class="step-number">2</div><div><strong>Extract Text</strong><p class="muted">The system reads resume content.</p></div></div>
                <div class="step"><div class="step-number">3</div><div><strong>AI Matching</strong><p class="muted">AI compares skills and job requirements.</p></div></div>
                <div class="step"><div class="step-number">4</div><div><strong>Top 10 Ranking</strong><p class="muted">Best candidates appear first.</p></div></div>
            </div>

            <div class="card main-card">
                <h2>Upload & Analyze CVs</h2>
                <p class="muted">Paste a job description, upload CVs, and get ranked results instantly.</p>

                <form action="/analyze" method="post" enctype="multipart/form-data" onsubmit="showLoading()">
                    <label>Job Description</label>
                    <textarea name="job_description" placeholder="Paste job description here..." required></textarea>

                    <label>Upload CV PDFs</label>
                    <input type="file" name="files" accept=".pdf" multiple required>

                    <button>Analyze CVs</button>
                </form>
            </div>

            <div class="card assistant">
                <div class="big-robot">🧑‍💼</div>
                <h3>AI Assistant</h3>
                <p class="muted">I will help you find the strongest candidates based on skills, relevance, and similarity.</p>

                <div class="stat"><strong>MiniLM</strong>Matching Model</div>
                <div class="stat"><strong>Top 10</strong>Ranked Candidates</div>
                <div class="stat"><strong>PDF</strong>Supported CV Format</div>
            </div>
        </div>

        <div class="robot">🧑‍💼</div>

        <div class="loading" id="loading">
            <div class="loader"></div>
            <p>Analyzing CVs with AI...</p>
        </div>

        <script>
            function showLoading() {
                document.getElementById("loading").style.display = "flex";
            }
        </script>
    </body>
    </html>
    """


def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def clean_text(text):
    text = str(text).lower()

    text = re.sub(r"[إأآا]", "ا", text)
    text = re.sub(r"ى", "ي", text)
    text = re.sub(r"ؤ", "و", text)
    text = re.sub(r"ئ", "ي", text)
    text = re.sub(r"ة", "ه", text)

    text = re.sub(r"[\u064B-\u065F\u0670]", "", text)
    text = re.sub(r"ـ", "", text)

    text = re.sub(r"[^\w\s\u0600-\u06FF]", " ", text)
    text = re.sub(r"\d+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    return text


def split_text_into_chunks(text, size=100):
    words = str(text).split()
    chunks = []

    for i in range(0, len(words), size):
        chunk = " ".join(words[i:i + size])
        if chunk.strip():
            chunks.append(chunk)

    return chunks


def normalize_experience(exp, max_exp=5):
    if exp is None:
        return 0
    return min(exp / max_exp, 1)


def extract_experience_years(text):
    text = str(text).lower()

    patterns = [
        r"(\d+)\s+years",
        r"(\d+)\s+year",
        r"(\d+)\s+yrs",
        r"(\d+)\s+سنوات",
        r"(\d+)\s+سنه",
        r"(\d+)\s+سنة"
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))

    return 0


def extract_email(text):
    match = re.search(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", text)
    return match.group(0) if match else "Not found"


def extract_phone(text):
    match = re.search(r"(\+?\d[\d\s\-()]{7,}\d)", text)
    return match.group(0) if match else "Not found"


def detect_language(text):
    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", str(text)))
    english_chars = len(re.findall(r"[A-Za-z]", str(text)))

    if arabic_chars > 0 and english_chars > 0:
        return "Mixed"
    elif arabic_chars > 0:
        return "Arabic"
    elif english_chars > 0:
        return "English"
    else:
        return "Unknown"


def get_required_skills(job_text):
    job_text = clean_text(job_text)
    return [skill for skill in SKILLS if skill in job_text]


def get_found_skills(required_skills, cv_text):
    return [skill for skill in required_skills if skill in cv_text]


def get_missing_skills(required_skills, cv_text):
    return [skill for skill in required_skills if skill not in cv_text]


def get_match_level(score):
    if score >= 75:
        return "High Match"
    elif score >= 55:
        return "Medium Match"
    return "Low Match"


def generate_ai_explanation(found_skills, missing_skills, score, language):
    if found_skills:
        top_skills = ", ".join(found_skills[:3])
    else:
        top_skills = "limited required skills"

    if score >= 75:
        strength = "Strong candidate"
    elif score >= 55:
        strength = "Potential candidate"
    else:
        strength = "Weak candidate"

    if missing_skills:
        missing_text = ", ".join(missing_skills[:2])
        return f"{strength}: matched {top_skills}. Missing: {missing_text}. Language: {language}."

    return f"{strength}: matched {top_skills} with no major missing required skills. Language: {language}."


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(job_description: str = Form(...), files: list[UploadFile] = File(...)):
    global last_top_results, last_results_html, shortlisted_candidates
    shortlisted_candidates = []

    if not is_logged_in:
        return RedirectResponse(url="/login")

    job_clean = clean_text(job_description)

    model, util = get_model()

    job_emb = model.encode(job_clean, convert_to_tensor=True)

    required_skills = get_required_skills(job_description)

    temp_data = []
    all_sim_scores = []

    for i, file in enumerate(files):
        try:
            path = f"temp_{i}.pdf"

            with open(path, "wb") as f:
                f.write(await file.read())

            raw_text = extract_text_from_pdf(path)
            cv_text = clean_text(raw_text)

            email = extract_email(raw_text)
            phone = extract_phone(raw_text)
            language = detect_language(raw_text)

            chunks = split_text_into_chunks(cv_text, size=100)

            chunk_sims = []
            if chunks:
                chunk_embs = model.encode(chunks, convert_to_tensor=True)
                sims = util.cos_sim(chunk_embs, job_emb).cpu().numpy().flatten().tolist()
                chunk_sims.extend(sims)
                all_sim_scores.extend(sims)

            exp_years = extract_experience_years(raw_text)
            exp = normalize_experience(exp_years)

            temp_data.append({
                "filename": file.filename,
                "text": cv_text,
                "chunk_sims": chunk_sims,
                "experience": exp,
                "email": email,
                "phone": phone,
                "language": language
            })

        except Exception as e:
            temp_data.append({
                "filename": file.filename,
                "text": "",
                "chunk_sims": [],
                "experience": 0,
                "email": "Not found",
                "phone": "Not found",
                "language": "Unknown",
                "error": str(e)
            })

    results = []

    for item in temp_data:
        if item.get("error"):
            results.append({
                "filename": item["filename"],
                "score": 0,
                "match_level": "Error",
                "found": "-",
                "missing": item["error"],
                "email": item.get("email", "Not found"),
                "phone": item.get("phone", "Not found"),
                "language": item.get("language", "Unknown"),
                "ai_explanation": "Could not analyze this CV because an error occurred."
            })
            continue

        if not item["chunk_sims"]:
            continue

        found_skills = get_found_skills(required_skills, item["text"])
        missing_skills = get_missing_skills(required_skills, item["text"])

        skill_match_ratio = len(found_skills) / len(required_skills) if required_skills else 0

        sim = max(item["chunk_sims"])
        exp = item["experience"]
        interaction = sim * exp

        final_score = (
            0.55 * sim +
            0.30 * skill_match_ratio +
            0.10 * exp +
            0.05 * interaction
        )
        if not missing_skills:
            final_score += 0.10
        final_score = min(final_score, 1.0)


        final_score_percent = round(final_score * 100, 2)

        results.append({
            "filename": item["filename"],
            "score": final_score_percent,
            "match_level": get_match_level(final_score_percent),
            "found": ", ".join(found_skills) if found_skills else "None",
            "missing": ", ".join(missing_skills) if missing_skills else "None",
            "email": item.get("email", "Not found"),
            "phone": item.get("phone", "Not found"),
            "language": item.get("language", "Unknown"),
            "ai_explanation": generate_ai_explanation(
                found_skills,
                missing_skills,
                final_score_percent,
                item.get("language", "Unknown")
            )
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]
    last_top_results = results

    rows = ""

    for rank, result in enumerate(results, 1):
        score_color = "#22c55e" if result["score"] >= 75 else "#f59e0b" if result["score"] >= 55 else "#ef4444"

        rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{result["filename"]}</td>
            <td style="color:{score_color}; font-weight:bold;">{result["score"]}%</td>
            <td>{result["match_level"]}</td>
            <td class="good">{result["found"]}</td>
            <td class="bad">{result["missing"]}</td>
            <td>{result.get("ai_explanation", "-")}</td>
            <td><a href="/shortlist/add/{rank-1}">Shortlist</a></td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="8">No CV results available.</td>
        </tr>
        """

    last_results_html = f"""
    <html>
    <head>
        <title>Top 10 CV Results</title>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                padding: 40px;
            }}

            .box {{
                width: 96%;
                margin: auto;
                background: #1e293b;
                padding: 30px;
                border-radius: 22px;
                border: 1px solid #334155;
                box-shadow: 0 25px 70px rgba(0,0,0,0.45);
            }}

            h2 {{
                text-align: center;
                margin-bottom: 25px;
                font-size: 30px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: #0f172a;
                border-radius: 16px;
                overflow: hidden;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #334155;
                text-align: center;
                font-size: 14px;
            }}

            th {{
                background: #6366f1;
                color: white;
            }}

            tr:hover {{
                background: #1e293b;
            }}

            .good {{
                color: #22c55e;
                font-weight: bold;
            }}

            .bad {{
                color: #f87171;
                font-weight: bold;
            }}

            a {{
                display: inline-block;
                margin-top: 25px;
                color: white;
                text-decoration: none;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                padding: 12px 20px;
                border-radius: 12px;
            }}
        </style>
    </head>

    <body>
        <div class="box">
            <h2>Top 10 CV Results</h2>

            <table>
                <tr>
                    <th>Rank</th>
                    <th>Filename</th>
                    <th>Score</th>
                    <th>Match Level</th>
                    <th>Matched Skills</th>
                    <th>Missing Skills</th>
                    <th>AI Explanation</th>
                    <th>Action</th>
                </tr>
                {rows}
            </table>

            <a href="/upload">Analyze More CVs</a>
            <a href="/contacts" style="margin-left:10px;">View Contact Info</a>
            <a href="/analytics" style="margin-left:10px;">View Analytics</a>
            <a href="/shortlist" style="margin-left:10px;">View Shortlist</a>
            <a href="/export-report" style="margin-left:10px;">Export Report</a>
            <a href="/logout" style="margin-left:10px;">Logout</a>
        </div>
    </body>
    </html>
    """

    return last_results_html


@app.get("/results", response_class=HTMLResponse)
def results_page():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    if not last_results_html:
        return RedirectResponse(url="/upload")

    return last_results_html



@app.get("/shortlist/add/{idx}", response_class=HTMLResponse)
def add_to_shortlist(idx: int):
    if not is_logged_in:
        return RedirectResponse(url="/login")

    if idx < 0 or idx >= len(last_top_results):
        return RedirectResponse(url="/results")

    candidate = last_top_results[idx]

    exists = any(item.get("filename") == candidate.get("filename") for item in shortlisted_candidates)

    if not exists:
        shortlisted_candidates.append(candidate)

    return RedirectResponse(url="/shortlist")


@app.get("/shortlist", response_class=HTMLResponse)
def shortlist_page():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    rows = ""

    for rank, result in enumerate(shortlisted_candidates, 1):
        rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{result.get("filename", "-")}</td>
            <td>{result.get("score", 0)}%</td>
            <td>{result.get("match_level", "-")}</td>
            <td>{result.get("email", "Not found")}</td>
            <td>{result.get("phone", "Not found")}</td>
            <td>{result.get("ai_explanation", "-")}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="7">No shortlisted candidates yet.</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Shortlisted Candidates</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                padding: 40px;
            }}

            .box {{
                width: 96%;
                margin: auto;
                background: #1e293b;
                padding: 30px;
                border-radius: 22px;
                border: 1px solid #334155;
                box-shadow: 0 25px 70px rgba(0,0,0,0.45);
            }}

            h2 {{
                text-align: center;
                margin-bottom: 25px;
                font-size: 30px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: #0f172a;
                border-radius: 16px;
                overflow: hidden;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #334155;
                text-align: center;
                font-size: 14px;
            }}

            th {{
                background: #6366f1;
                color: white;
            }}

            a {{
                display: inline-block;
                margin-top: 25px;
                color: white;
                text-decoration: none;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                padding: 12px 20px;
                border-radius: 12px;
            }}
        </style>
    </head>

    <body>
        <div class="box">
            <h2>Shortlisted Candidates</h2>

            <table>
                <tr>
                    <th>#</th>
                    <th>Filename</th>
                    <th>Score</th>
                    <th>Match Level</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>AI Explanation</th>
                </tr>
                {rows}
            </table>

            <a href="/results">Back to Results</a>
            <a href="/export-report" style="margin-left:10px;">Export Report</a>
            <a href="/logout" style="margin-left:10px;">Logout</a>
        </div>
    </body>
    </html>
    """


@app.get("/export-report")
def export_report():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    report_rows = shortlisted_candidates if shortlisted_candidates else last_top_results

    if not report_rows:
        return HTMLResponse("""
        <body style="background:#0f172a;color:white;font-family:Arial;text-align:center;padding-top:80px;">
            <h2>No results available to export.</h2>
            <a href="/upload" style="color:white;background:#6366f1;padding:12px 20px;border-radius:10px;text-decoration:none;">Back to Dashboard</a>
        </body>
        """)

    file_path = "cv_ranking_report.csv"

    fieldnames = [
        "filename",
        "score",
        "match_level",
        "found",
        "missing",
        "email",
        "phone",
        "language",
        "ai_explanation"
    ]

    with open(file_path, "w", newline="", encoding="utf-8-sig") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for result in report_rows:
            writer.writerow({
                "filename": result.get("filename", ""),
                "score": result.get("score", ""),
                "match_level": result.get("match_level", ""),
                "found": result.get("found", ""),
                "missing": result.get("missing", ""),
                "email": result.get("email", ""),
                "phone": result.get("phone", ""),
                "language": result.get("language", ""),
                "ai_explanation": result.get("ai_explanation", "")
            })

    return FileResponse(file_path, filename="cv_ranking_report.csv", media_type="text/csv")


@app.get("/contacts", response_class=HTMLResponse)
def contacts_page():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    rows = ""

    for rank, result in enumerate(last_top_results, 1):
        email = result.get("email", "Not found")
        phone = result.get("phone", "Not found")

        email_button = f'<a href="mailto:{email}">Email</a>' if email != "Not found" else "-"
        phone_button = f'<a href="tel:{phone}">Call</a>' if phone != "Not found" else "-"

        rows += f"""
        <tr>
            <td>{rank}</td>
            <td>{result["filename"]}</td>
            <td>{result["score"]}%</td>
            <td>{email}</td>
            <td>{phone}</td>
            <td>{email_button}</td>
            <td>{phone_button}</td>
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="7">No contact results available. Please analyze CVs first.</td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Top 10 Contact Info</title>
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                padding: 40px;
            }}

            .box {{
                width: 96%;
                margin: auto;
                background: #1e293b;
                padding: 30px;
                border-radius: 22px;
                border: 1px solid #334155;
                box-shadow: 0 25px 70px rgba(0,0,0,0.45);
            }}

            h2 {{
                text-align: center;
                margin-bottom: 25px;
            }}

            table {{
                width: 100%;
                border-collapse: collapse;
                background: #0f172a;
                border-radius: 16px;
                overflow: hidden;
            }}

            th, td {{
                padding: 14px;
                border-bottom: 1px solid #334155;
                text-align: center;
            }}

            th {{
                background: #6366f1;
                color: white;
            }}

            a {{
                display: inline-block;
                color: white;
                text-decoration: none;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                padding: 10px 16px;
                border-radius: 10px;
            }}

            .back {{
                margin-top: 25px;
            }}
        </style>
    </head>

    <body>
        <div class="box">
            <h2>Top 10 Contact Information</h2>

            <table>
                <tr>
                    <th>Rank</th>
                    <th>Filename</th>
                    <th>Score</th>
                    <th>Email</th>
                    <th>Phone</th>
                    <th>Email Candidate</th>
                    <th>Call Candidate</th>
                </tr>
                {rows}
            </table>

            <a href="/results" class="back">Back to Results</a>
            <a href="/shortlist" class="back" style="margin-left:10px;">View Shortlist</a>
            <a href="/export-report" class="back" style="margin-left:10px;">Export Report</a>
            <a href="/logout" class="back" style="margin-left:10px;">Logout</a>
        </div>
    </body>
    </html>
    """

@app.get("/analytics", response_class=HTMLResponse)
def analytics_page():
    if not is_logged_in:
        return RedirectResponse(url="/login")

    if not last_top_results:
        return """
        <html>
        <body style="background:#0f172a;color:white;font-family:Arial;text-align:center;padding-top:80px;">
            <h2>No analytics available</h2>
            <p>Please analyze CVs first.</p>
            <a href="/upload" style="color:white;background:#6366f1;padding:12px 20px;border-radius:10px;text-decoration:none;">Back to Dashboard</a>
        </body>
        </html>
        """

    total = len(last_top_results)
    avg_score = round(sum(r.get("score", 0) for r in last_top_results) / total, 2)
    highest_score = max(r.get("score", 0) for r in last_top_results)

    high_count = sum(1 for r in last_top_results if r.get("match_level") == "High Match")
    medium_count = sum(1 for r in last_top_results if r.get("match_level") == "Medium Match")
    low_count = sum(1 for r in last_top_results if r.get("match_level") == "Low Match")

    language_counts = {}
    skill_counts = {}

    for result in last_top_results:
        lang = result.get("language", "Unknown")
        language_counts[lang] = language_counts.get(lang, 0) + 1

        found = result.get("found", "None")
        if found != "None":
            for skill in found.split(","):
                skill = skill.strip()
                if skill:
                    skill_counts[skill] = skill_counts.get(skill, 0) + 1

    top_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:8]

    def percent(value):
        return round((value / total) * 100, 2) if total else 0

    skill_rows = ""
    for skill, count in top_skills:
        width = percent(count)
        skill_rows += f"""
        <div class="chart-row">
            <div class="label">{skill}</div>
            <div class="bar-bg">
                <div class="bar-fill" style="width:{width}%"></div>
            </div>
            <div class="value">{count}</div>
        </div>
        """

    if not skill_rows:
        skill_rows = "<p class='muted'>No matched skills found.</p>"

    language_rows = ""
    for lang, count in language_counts.items():
        width = percent(count)
        language_rows += f"""
        <div class="chart-row">
            <div class="label">{lang}</div>
            <div class="bar-bg">
                <div class="bar-fill language" style="width:{width}%"></div>
            </div>
            <div class="value">{count}</div>
        </div>
        """

    distribution_rows = f"""
    <div class="chart-row">
        <div class="label">High Match</div>
        <div class="bar-bg"><div class="bar-fill high" style="width:{percent(high_count)}%"></div></div>
        <div class="value">{high_count}</div>
    </div>

    <div class="chart-row">
        <div class="label">Medium Match</div>
        <div class="bar-bg"><div class="bar-fill medium" style="width:{percent(medium_count)}%"></div></div>
        <div class="value">{medium_count}</div>
    </div>

    <div class="chart-row">
        <div class="label">Low Match</div>
        <div class="bar-bg"><div class="bar-fill low" style="width:{percent(low_count)}%"></div></div>
        <div class="value">{low_count}</div>
    </div>
    """

    return f"""
    <html>
    <head>
        <title>CV Analytics</title>
        <style>
            * {{
                box-sizing: border-box;
            }}

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #0f172a;
                color: white;
                padding: 40px;
            }}

            .box {{
                width: 96%;
                margin: auto;
                background: #1e293b;
                padding: 30px;
                border-radius: 22px;
                border: 1px solid #334155;
                box-shadow: 0 25px 70px rgba(0,0,0,0.45);
            }}

            h2 {{
                text-align: center;
                margin-bottom: 28px;
                font-size: 30px;
            }}

            .stats {{
                display: grid;
                grid-template-columns: repeat(3, 1fr);
                gap: 16px;
                margin-bottom: 25px;
            }}

            .stat-card {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 18px;
                padding: 20px;
                text-align: center;
            }}

            .stat-card strong {{
                display: block;
                color: #a78bfa;
                font-size: 28px;
                margin-bottom: 6px;
            }}

            .grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 18px;
            }}

            .panel {{
                background: #0f172a;
                border: 1px solid #334155;
                border-radius: 18px;
                padding: 22px;
            }}

            .panel h3 {{
                margin-top: 0;
                margin-bottom: 18px;
            }}

            .chart-row {{
                display: grid;
                grid-template-columns: 150px 1fr 40px;
                gap: 12px;
                align-items: center;
                margin: 14px 0;
            }}

            .label {{
                color: #e2e8f0;
                font-size: 14px;
            }}

            .bar-bg {{
                height: 13px;
                background: #334155;
                border-radius: 20px;
                overflow: hidden;
            }}

            .bar-fill {{
                height: 100%;
                border-radius: 20px;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
            }}

            .bar-fill.high {{
                background: #22c55e;
            }}

            .bar-fill.medium {{
                background: #f59e0b;
            }}

            .bar-fill.low {{
                background: #ef4444;
            }}

            .bar-fill.language {{
                background: linear-gradient(135deg, #06b6d4, #8b5cf6);
            }}

            .value {{
                color: #cbd5e1;
                text-align: center;
                font-weight: bold;
            }}

            .muted {{
                color: #94a3b8;
            }}

            a {{
                display: inline-block;
                margin-top: 25px;
                color: white;
                text-decoration: none;
                background: linear-gradient(135deg, #6366f1, #8b5cf6);
                padding: 12px 20px;
                border-radius: 12px;
            }}

            @media (max-width: 900px) {{
                .stats, .grid {{
                    grid-template-columns: 1fr;
                }}

                .chart-row {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>

    <body>
        <div class="box">
            <h2>CV Analytics Dashboard</h2>

            <div class="stats">
                <div class="stat-card">
                    <strong>{total}</strong>
                    Top Candidates
                </div>

                <div class="stat-card">
                    <strong>{avg_score}%</strong>
                    Average Score
                </div>

                <div class="stat-card">
                    <strong>{highest_score}%</strong>
                    Highest Score
                </div>
            </div>

            <div class="grid">
                <div class="panel">
                    <h3>Top Matched Skills</h3>
                    {skill_rows}
                </div>

                <div class="panel">
                    <h3>Score Distribution</h3>
                    {distribution_rows}
                </div>

                <div class="panel">
                    <h3>Language Detection</h3>
                    {language_rows}
                </div>

                <div class="panel">
                    <h3>Quick Insight</h3>
                    <p class="muted">This dashboard summarizes the Top 10 candidates based on score, detected language, match level distribution, and the most frequent matched skills.</p>
                </div>
            </div>

            <a href="/results">Back to Results</a>
            <a href="/contacts" style="margin-left:10px;">View Contact Info</a>
            <a href="/shortlist" style="margin-left:10px;">View Shortlist</a>
            <a href="/export-report" style="margin-left:10px;">Export Report</a>
            <a href="/logout" style="margin-left:10px;">Logout</a>
        </div>
    </body>
    </html>
    """
