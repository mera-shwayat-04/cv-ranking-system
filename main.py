from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import pdfplumber
from sentence_transformers import SentenceTransformer, util
import re
import numpy as np

app = FastAPI()
model = None
def get_model():
    global model
    if model is None:
        model = SentenceTransformer("all-MiniLM-L6-v2")
    return model

app.mount("/static", StaticFiles(directory="static"), name="static")

HR_EMAIL = "hr@example.com"
HR_PASSWORD = "123456"
is_logged_in = False

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
            body {
                margin:0;
                font-family: Arial, sans-serif;
                background:#0f172a;
                color:white;
                height:100vh;
                display:flex;
                align-items:center;
                justify-content:center;
            }

            .box {
                width:420px;
                background:#1e293b;
                padding:35px;
                border-radius:20px;
                box-shadow:0 25px 70px rgba(0,0,0,0.6);
                text-align:center;
            }

            input {
                width:100%;
                padding:14px;
                margin-top:15px;
                border-radius:12px;
                border:1px solid #475569;
                background:#0f172a;
                color:white;
            }

            button {
                width:100%;
                margin-top:25px;
                padding:14px;
                border:none;
                border-radius:12px;
                background:linear-gradient(135deg,#6366f1,#8b5cf6);
                color:white;
                font-weight:bold;
                cursor:pointer;
            }

            .robot {
                font-size:55px;
                animation: float 2.5s infinite;
            }

            @keyframes float {
                0%,100% { transform:translateY(0); }
                50% { transform:translateY(-10px); }
            }
        </style>
    </head>

    <body>
        <div class="box">
            <div class="robot">🤖</div>
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
                <div class="big-robot">🤖</div>
                <h3>AI Assistant</h3>
                <p class="muted">I will help you find the strongest candidates based on skills, relevance, and similarity.</p>

                <div class="stat"><strong>MiniLM</strong>Matching Model</div>
                <div class="stat"><strong>Top 10</strong>Ranked Candidates</div>
                <div class="stat"><strong>PDF</strong>Supported CV Format</div>
            </div>
        </div>

        <div class="robot">🤖</div>

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


@app.post("/analyze", response_class=HTMLResponse)
async def analyze(job_description: str = Form(...), files: list[UploadFile] = File(...)):
    if not is_logged_in:
        return RedirectResponse(url="/login")

    job_clean = clean_text(job_description)
    model = get_model()
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

            chunks = split_text_into_chunks(cv_text, size=100)

            chunk_sims = []

            for chunk in chunks:
                chunk_emb = model.encode(chunk, convert_to_tensor=True)
                sim = util.cos_sim(job_emb, chunk_emb).item()
                chunk_sims.append(sim)
                all_sim_scores.append(sim)

            exp_years = extract_experience_years(raw_text)
            exp = normalize_experience(exp_years)

            temp_data.append({
                "filename": file.filename,
                "text": cv_text,
                "chunk_sims": chunk_sims,
                "experience": exp
            })

        except Exception as e:
            temp_data.append({
                "filename": file.filename,
                "text": "",
                "chunk_sims": [],
                "experience": 0,
                "error": str(e)
            })

    threshold = np.percentile(all_sim_scores, 60) if all_sim_scores else 0

    results = []

    for item in temp_data:
        if item.get("error"):
            results.append({
                "filename": item["filename"],
                "score": 0,
                "match_level": "Error",
                "found": "-",
                "missing": item["error"]
            })
            continue

        if not item["chunk_sims"]:
            continue

        sim = max(item["chunk_sims"])

        sim = max(item["chunk_sims"])
        exp = item["experience"]
        interaction = sim * exp

        final_score = (
            0.65 * sim +
            0.20 * exp +
            0.05 * interaction
            )


        exp = item["experience"]
        interaction = sim * exp

        final_score = (
            0.65 * sim +
            0.20 * exp +
            0.05 * interaction
        )

        final_score_percent = round(final_score * 100, 2)

        found_skills = get_found_skills(required_skills, item["text"])
        missing_skills = get_missing_skills(required_skills, item["text"])

        results.append({
            "filename": item["filename"],
            "score": final_score_percent,
            "match_level": get_match_level(final_score_percent),
            "found": ", ".join(found_skills) if found_skills else "None",
            "missing": ", ".join(missing_skills) if missing_skills else "None"
        })

    results = sorted(results, key=lambda x: x["score"], reverse=True)[:10]

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
        </tr>
        """

    if not rows:
        rows = """
        <tr>
            <td colspan="6">No CVs passed the ranking threshold.</td>
        </tr>
        """

    return f"""
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
                </tr>
                {rows}
            </table>

            <a href="/upload">Analyze More CVs</a>
            <a href="/logout" style="margin-left:10px;">Logout</a>
        </div>
    </body>
    </html>
    """