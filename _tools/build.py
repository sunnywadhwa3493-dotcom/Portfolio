#!/usr/bin/env python3
"""Build a job kit: tailored resume PDF + tailored portfolio page.

Usage:  python3 _tools/build.py <slug> [<slug> ...]   (or "all")
Reads   _tools/jobs/<slug>.json
Writes  jobs/<slug>/index.html and jobs/<slug>/<resume_file>.pdf
Needs   google-chrome (headless) on PATH.
"""
import html, json, os, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS = os.path.join(ROOT, "_tools")
BASE_URL = "https://sunnywadhwa3493-dotcom.github.io/Portfolio"
E = html.escape

NAME = "Dr. Sampreeth Singh Wadhwa"
EMAIL = "sampreethwadhwa@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/sampreethsingh/"
LOCATION = "Fort Erie, Ontario, Canada"

# ---------- shared resume blocks (facts only) ----------
OUTLIER = ("AI Evaluation (Freelance), Outlier", "Dec 2025 – Present", [
    "Write clinical prompts and expert reference answers, build scoring rubrics, and grade and compare ChatGPT, Gemini and Claude responses for clinical accuracy and task requirements.",
    "Design questions that challenge frontier models on clinical workflows and simulated scenarios, documenting where responses help and where they fail.",
])
ROOVERO_SHORT = ("Founder and Product Lead, Roovero", "Dec 2025 – Present", [
    "Took an AI content SaaS for small businesses from discovery to launch; now serving paying pilot clients and iterating on their feedback.",
    "Own requirements, AI architecture and the hands-on build (Flutter, Firebase, Next.js) using Claude Code and Codex, including billing and webhook integrations.",
])
ROOVERO_FULL = ("Founder and Product Lead, Roovero", "Dec 2025 – Present", [
    "Took an AI content platform for startups and small businesses from problem discovery through launch; now serving paying pilot clients and iterating on their feedback.",
    "Own strategy, requirements, AI architecture and hands-on build of the Flutter/Firebase app and Next.js site, using Claude Code and Codex to move from idea to working software quickly.",
    "Built website and PDF ingestion that generates brand profiles, plus 30-day content calendars with a user-approval step in the workflow.",
    "Integrated and routed multiple AI models (Claude Sonnet, Imagen, Veo, ElevenLabs) and Instagram Graph API publishing, comments and insights.",
    "Use performance data to iterate on model routing, prompts and content strategy; implemented subscription billing and webhooks and led go-to-market.",
])
PAWLENTINE = ("Founder, Pawlentine", "Pre-launch", [
    "Defined personas, user journeys and prioritisation for a pet social and matching app; building it hands-on with an analytics agent and event tracking.",
])
CLINICAL = [
    "<b>Senior Resident, Emergency Medicine, Aster CMI</b>, Bengaluru (Apr 2021 – Jul 2022): quaternary care, Level 1 trauma centre.",
    "<b>ICU Registrar, HBS Hospital</b>, Bengaluru (May 2020 – Jan 2021): COVID ICU; trained 12+ nurses.",
    "<b>Occupational Health Physician, Ranger OH Clinic</b> (Jan – Apr 2021): wrote SOPs; trained 500+ people in emergency and safety protocols.",
    "<b>Teleconsultation Doctor, TATA 1MG</b> and freelance physician, India (Nov 2020 – present): virtual and in-person consultations, chronic disease management.",
]
EDUCATION = ("MBBS, Kempegowda Institute of Medical Sciences (KIMS)", "2020 | Bengaluru, India")


def role_block(title, dates, bullets, keep=True):
    lis = "".join(f"<li>{E(b)}</li>" for b in bullets)
    cls = ' class="keep"' if keep else ""
    return (f'<div{cls}><div class="role"><span>{E(title)}</span><span>{E(dates)}</span></div>'
            f"<ul>{lis}</ul></div>")


def resume_html(job):
    page_url = f"{BASE_URL}/jobs/{job['slug']}/"
    greenway = ("Clinical Advisor, Greenway Health", "Aug 2022 – Oct 2026 | Remote", job["greenway_bullets"])
    order = {
        "impl": [greenway, OUTLIER, ROOVERO_SHORT],
        "product": [ROOVERO_FULL, greenway, OUTLIER, PAWLENTINE],
        "ai": [OUTLIER, greenway, ROOVERO_SHORT],
    }[job["variant"]]
    exp_title = {"impl": "Healthcare Software Experience", "product": "Product and AI Experience",
                 "ai": "AI and Healthcare Software Experience"}[job["variant"]]
    exp = "".join(role_block(t, d, b, keep=(len(b) <= 5)) for t, d, b in order)
    skills = "".join(f"<li><b>{E(k)}:</b> {E(v)}</li>" for k, v in job["skills"])
    clinical = "".join(f"<li>{c}</li>" for c in CLINICAL)
    css = open(os.path.join(TOOLS, "resume.css")).read()
    return f"""<!DOCTYPE html><html><head><meta charset="utf-8"><title>{E(NAME)} – Resume</title><style>{css}</style></head><body>
<h1>{E(NAME)}</h1>
<div class="title">{E(job['headline'])}</div>
<div class="contact">{E(LOCATION)} &nbsp;|&nbsp; {EMAIL} &nbsp;|&nbsp; <a href="{LINKEDIN}">linkedin.com/in/sampreethsingh</a> &nbsp;|&nbsp; <a href="{page_url}">Portfolio</a></div>
<h2>Summary</h2><p>{E(job['summary'])}</p>
<h2>Core Skills</h2><ul class="skills">{skills}</ul>
<h2>{exp_title}</h2>{exp}
<h2>Clinical Experience</h2><ul>{clinical}</ul>
<h2>Education</h2><div class="role"><span>{E(EDUCATION[0])}</span><span>{E(EDUCATION[1])}</span></div>
</body></html>"""


# ---------- portfolio case-study library ----------
CASES = {
"impl": """<article class="panel"><div class="meta">Greenway Health · 2022 – 2026</div>
<h3>EHR implementations, from discovery to adoption</h3>
<p style="font-size:16px">For two strategic client practices I ran discovery on their pain points, configured practice-specific workflows and widgets, supported setup and trained 200+ providers, NPs, nurses and medical assistants. Recurring friction became feature requests, and many of them shipped.</p>
<div class="loopsteps"><span>Discovery</span><span>Configure</span><span>Train 200+</span><span>Shipped</span></div></article>""",
"training": """<article class="panel"><div class="meta">Across my career</div>
<h3>Training that sticks</h3>
<div class="nums"><div><b>200+</b><span>EHR users trained at Greenway</span></div><div><b>500+</b><span>people trained in occupational health</span></div><div><b>12+</b><span>ICU nurses trained during COVID</span></div></div>
<p style="font-size:16px;margin-top:14px">I build training around each role's real day, from physicians to medical assistants, and I write the SOPs that keep it consistent.</p></article>""",
"safety": """<article class="panel"><div class="meta">Greenway Patient Safety Committee · Outlier</div>
<h3>Quality and safety before go-live</h3>
<ul><li>Triaged defects and patient safety issues from detection through stage-gate release.</li>
<li>Reviewed clinical literature for EHR content on the Clinical Content Team.</li>
<li>Grade frontier AI models on clinical accuracy with rubrics I design.</li></ul></article>""",
"aieval": """<article class="panel"><div class="meta">Outlier · Dec 2025 – present</div>
<h3>Testing medical AI for clinical accuracy</h3>
<ul><li>Write clinical prompts and expert reference answers.</li>
<li>Build scoring rubrics; grade and compare ChatGPT, Gemini and Claude.</li>
<li>Document where answers are plausible but clinically wrong.</li></ul></article>""",
"aiehr": """<article class="panel wide"><div class="meta">Clinical lead · Greenway Health · Aug 2025 – Oct 2026</div>
<h3>An AI-first EHR, designed from the clinician's day</h3>
<p style="font-size:16px">Defined provider personas and user goals, mapped end-to-end clinical workflows, scoped where agentic automation could take routine work off clinicians, and built React prototypes before engineering handoff.</p>
<div class="flow"><div class="step"><span class="mono">Before</span><b>Scheduling</b></div><div class="step auto"><span class="mono">Automate</span><b>Intake</b></div><div class="step"><span class="mono">Clinician</span><b>Visit</b></div><div class="step auto"><span class="mono">Automate</span><b>Documentation</b></div><div class="step auto"><span class="mono">Assist</span><b>Orders</b></div><div class="step"><span class="mono">After</span><b>Follow-up</b></div></div>
<div class="legend"><span><i class="r"></i>Where AI can help</span><span><i></i>Clinician-owned</span><span>Illustrative; real designs are confidential.</span></div></article>""",
"roovero": """<article class="panel wide"><div class="meta">Founder · Roovero · Dec 2025 – present</div>
<h3>Roovero: an AI product taken to paying pilot clients</h3>
<div class="pipeline"><div class="stage"><span class="mono">01 Ingest</span><h4>Read the business</h4><p>Website or PDFs in.</p></div><div class="stage"><span class="mono">02 Profile</span><h4>Build the brand</h4><p>Voice, colours, goals.</p></div><div class="stage"><span class="mono">03 Plan</span><h4>30-day calendar</h4><p>Posts, carousels, reels.</p></div><div class="stage"><span class="mono">04 Approve</span><h4>Customer in control</h4><p>Nothing ships unapproved.</p></div><div class="stage"><span class="mono">05 Learn</span><h4>Publish and measure</h4><p>Insights feed iteration.</p></div></div>
<p style="font-size:16px;margin-top:14px">I owned strategy, requirements and AI architecture and built it myself with Claude Code and Codex. It is live with paying pilot clients.</p></article>""",
}

EXTRA_CSS = """
.panel.wide{grid-column:1/-1}
.fit{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}
.fit div{border-top:3px solid var(--pulse);padding-top:12px}
.fit .mono{color:var(--soft);font-size:11px}
.fit b{display:block;font-family:var(--display);font-weight:700;font-size:18px;line-height:1.25;margin:6px 0}
.fit p{font-size:15px;color:var(--soft);margin:0}
.nums{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:12px}
.nums b{display:block;font-family:var(--display);font-stretch:118%;font-weight:850;font-size:34px;color:var(--pulse);line-height:1}
.nums span{font-size:13px;color:var(--soft)}
.pipeline .stage{min-height:0}
.hero h1.job{font-size:clamp(38px,6.4vw,84px)}
@media (max-width:900px){.fit{grid-template-columns:1fr}}
"""


def portfolio_html(job):
    css = open(os.path.join(TOOLS, "site.css")).read() + EXTRA_CSS
    fit = "".join(f'<div><span class="mono">{E(r)}</span><b>{E(h)}</b><p>{E(p)}</p></div>'
                  for r, h, p in job["why_fit"])
    cases = "".join(CASES[c] for c in job["cases"])
    pdf = job["resume_file"]
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Sampreeth Wadhwa for {E(job['company'])}</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@100..125,400..900&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&family=JetBrains+Mono:wght@500&display=swap" rel="stylesheet">
<style>{css}</style></head><body>
<header class="hero"><div class="wrap">
<div class="topbar mono"><span><span class="dot"></span>Sampreeth Singh Wadhwa, MBBS</span><span>For {E(job['company'])} · {E(job['role'])}</span></div>
<h1 class="job">{job['thesis_html']}</h1></div>
<svg class="trace" viewBox="0 0 1440 120" preserveAspectRatio="none" aria-hidden="true"><path class="draw" d="M0 80 H260 L280 80 L292 64 L304 80 L330 80 L344 18 L360 112 L374 80 L410 80 L428 66 L446 80 H620 L640 80 L652 64 L664 80 L690 80 L704 18 L720 112 L734 80 L770 80 L788 66 L806 80 H900 L960 70 L1020 74 L1080 58 L1140 62 L1200 44 L1260 48 L1320 30 L1380 34 L1440 18"/></svg>
<div class="wrap"><div class="hero-foot"><div><p class="lede">{E(job['summary'])}</p>
<div class="cta"><a class="btn solid" href="{E(pdf)}">Resume (PDF)</a><a class="btn" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{LINKEDIN}">LinkedIn</a></div></div>
<div class="facts">{''.join(f'<div><b>{E(a)}</b><span>{E(b)}</span></div>' for a, b in job['facts'])}</div></div></div></header>
<main>
<section><div class="wrap"><div class="shead"><span class="mono">Why this role</span><h2>What {E(job['company'])} needs, and where I've done it.</h2></div><div class="fit">{fit}</div></div></section>
<section><div class="wrap"><div class="shead"><span class="mono">Evidence</span><h2>Work that maps to this job.</h2></div><div class="twoup">{cases}</div></div></section>
<section><div class="wrap"><div class="shead"><span class="mono">The patient side</span><p class="quote">I've delivered care in emergency, ICU and over a screen. I know what clinicians and patients need from software.</p></div>
<div class="clin"><div><b>Emergency Medicine</b><span>Aster CMI, Bengaluru. Level 1 trauma centre.</span></div><div><b>ICU Registrar</b><span>HBS Hospital. COVID ICU; trained nurses.</span></div><div><b>Occupational Health</b><span>Wrote SOPs; trained 500+ people.</span></div><div><b>MBBS</b><span>Kempegowda Institute of Medical Sciences, 2020.</span></div></div></div></section>
</main>
<footer><div class="wrap"><p class="big">Let's talk about <em>{E(job['company'])}</em>.</p>
<div class="cta"><a class="btn solid" href="mailto:{EMAIL}">{EMAIL}</a><a class="btn" href="{E(pdf)}">Resume (PDF)</a></div>
<p class="fine">{E(LOCATION)} · Client names, screens and proprietary designs are omitted to respect confidentiality.</p></div></footer>
</body></html>"""


def build(slug):
    job = json.load(open(os.path.join(TOOLS, "jobs", f"{slug}.json")))
    job["slug"] = slug
    out = os.path.join(ROOT, "jobs", slug)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "index.html"), "w") as f:
        f.write(portfolio_html(job))
    with tempfile.TemporaryDirectory() as tmp:
        src = os.path.join(tmp, "resume.html")
        with open(src, "w") as f:
            f.write(resume_html(job))
        pdf = os.path.join(out, job["resume_file"])
        subprocess.run(["google-chrome", "--headless", "--no-sandbox", "--disable-gpu",
                        "--no-pdf-header-footer", f"--print-to-pdf={pdf}", src],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pages = subprocess.run(["pdfinfo", pdf], capture_output=True, text=True).stdout
    n = [l.split()[-1] for l in pages.splitlines() if l.startswith("Pages")]
    print(f"{slug}: {BASE_URL}/jobs/{slug}/  resume pages={n[0] if n else '?'}")


if __name__ == "__main__":
    slugs = sys.argv[1:]
    if slugs == ["all"]:
        slugs = sorted(f[:-5] for f in os.listdir(os.path.join(TOOLS, "jobs")) if f.endswith(".json"))
    for s in slugs:
        build(s)
