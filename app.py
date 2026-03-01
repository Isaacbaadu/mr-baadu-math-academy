"""
Mr. Baadu Math Academy — Full Website Portal (Streamlit)
========================================================

WHAT YOU GET (Everything you asked for):
- Dark blended "Offline Math Tool" background (NO white background)
- Catchy math symbols + equations overlay
- Left sidebar login/register like a real website portal
- Free + Paid model (Option 1: one subscription unlocks ALL paid content)
- Pages: WAEC / Cambridge / American
- Upload Lesson Notes + Solved Problems + Past Papers (Admin)
- Featured resources on Home
- External solved past papers hub (PastPaperPenguin + others) — links only
- Admin can add/remove external sites
- Payment links + manual payment reference submission
- Admin approves payments and upgrades users

DATA:
- SQLite DB: mba_portal.db
- Upload folder: uploads/
"""

import streamlit as st
import os
import sqlite3
from datetime import datetime
import bcrypt

# ------------------------------------------------------------
# 1) BRANDING
# ------------------------------------------------------------
APP_NAME = "Mr. Baadu Math Academy"
TAGLINE  = "Free + Paid Resources • WAEC • Cambridge • American Curriculum"
OPTION_1 = "One subscription unlocks all paid resources."

# ------------------------------------------------------------
# 2) PATHS
# ------------------------------------------------------------
DB_PATH = "mba_portal.db"
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ------------------------------------------------------------
# 3) SECRETS (for Streamlit Cloud)
# ------------------------------------------------------------
def get_secret(key: str, default=None):
    try:
        return st.secrets.get(key, default)
    except Exception:
        return default

ADMIN_EMAIL = str(get_secret("ADMIN_EMAIL", "admin@mba.com")).strip().lower()
ADMIN_DEFAULT_PASSWORD = str(get_secret("ADMIN_DEFAULT_PASSWORD", "admin1234"))

STRIPE_LINK = str(get_secret("STRIPE_LINK", "https://buy.stripe.com/your_link_here"))
PAYPAL_LINK = str(get_secret("PAYPAL_LINK", "https://www.paypal.com/paypalme/yourname"))
MOBILE_MONEY_LINK = str(get_secret("MOBILE_MONEY_LINK", "https://wa.me/220XXXXXXXX?text=Hello%20I%20want%20to%20pay%20for%20Paid%20Access"))

# ------------------------------------------------------------
# 4) STREAMLIT SETTINGS
# ------------------------------------------------------------
st.set_page_config(page_title=APP_NAME, layout="wide")

# ------------------------------------------------------------
# 5) BEAUTIFUL OFFLINE-MATH-TOOL THEME (ZERO WHITE BACKGROUND)
# ------------------------------------------------------------
CSS = r"""
<style>
/* ==============
   Color system
   ============== */
:root{
  --bg0:#050712;
  --bg1:#070b18;
  --bg2:#0b122a;
  --ink:#eaf0ff;
  --muted: rgba(234,240,255,.74);

  --glass: rgba(255,255,255,.055);
  --glass2: rgba(255,255,255,.085);
  --border: rgba(255,255,255,.14);

  --a1:#6ea8ff;     /* blue */
  --a2:#7cf0d6;     /* teal */
  --a3:#f7d36b;     /* gold */
  --a4:#ff6bd6;     /* pink */
}

/* Remove any default white/gray */
html, body, [class*="css"]{
  background: transparent !important;
  color: var(--ink) !important;
}

/* Force Streamlit app background to dark gradient */
.stApp{
  background:
    radial-gradient(1200px 800px at 10% 0%, rgba(110,168,255,.22) 0%, rgba(5,7,18,0) 55%),
    radial-gradient(900px 600px at 90% 10%, rgba(124,240,214,.16) 0%, rgba(5,7,18,0) 60%),
    radial-gradient(700px 500px at 50% 95%, rgba(247,211,107,.10) 0%, rgba(5,7,18,0) 60%),
    linear-gradient(180deg, var(--bg2), var(--bg1), var(--bg0)) !important;
}

/* Wider layout */
.block-container{
  max-width: 1280px;
  padding-top: 1rem;
  padding-bottom: 3rem;
}

/* Glow overlay (makes it catchy) */
.stApp::after{
  content:"";
  position: fixed;
  inset: -140px;
  pointer-events:none;
  background:
    radial-gradient(650px 380px at 18% 22%, rgba(110,168,255,.14), transparent 62%),
    radial-gradient(560px 340px at 80% 25%, rgba(255,107,214,.10), transparent 64%),
    radial-gradient(560px 340px at 55% 88%, rgba(124,240,214,.10), transparent 64%);
  filter: blur(18px);
  opacity: .95;
}

/* Math wallpaper overlay */
.stApp::before{
  content:"";
  position: fixed;
  inset: 0;
  pointer-events: none;
  opacity: .18;
  background-image:url("data:image/svg+xml;utf8,\
<svg xmlns='http://www.w3.org/2000/svg' width='980' height='560'>\
<defs>\
<linearGradient id='g' x1='0' y1='0' x2='1' y2='1'>\
<stop offset='0' stop-color='%236ea8ff' stop-opacity='0.85'/>\
<stop offset='0.55' stop-color='%237cf0d6' stop-opacity='0.75'/>\
<stop offset='1' stop-color='%23f7d36b' stop-opacity='0.75'/>\
</linearGradient>\
</defs>\
<rect width='100%25' height='100%25' fill='none'/>\
<g fill='url(%23g)' font-family='Segoe UI, Arial' font-size='30' opacity='0.95'>\
<text x='22' y='62'>∫</text><text x='98' y='62'>Σ</text><text x='176' y='62'>π</text><text x='254' y='62'>√</text>\
<text x='332' y='62'>∞</text><text x='410' y='62'>Δ</text><text x='488' y='62'>θ</text><text x='566' y='62'>∀</text>\
<text x='644' y='62'>∃</text><text x='722' y='62'>≈</text><text x='800' y='62'>≠</text>\
</g>\
<g fill='%23eaf0ff' font-family='Cambria Math, Times New Roman' font-size='19' opacity='0.88'>\
<text x='30' y='155'>f(x)=ax²+bx+c</text>\
<text x='335' y='155'>limₓ→0 sinx/x = 1</text>\
<text x='700' y='155'>a²+b²=c²</text>\
<text x='30' y='240'>P(A|B)=P(A∩B)/P(B)</text>\
<text x='470' y='240'>y=mx+c</text>\
<text x='705' y='240'>e^{iπ}+1=0</text>\
<text x='30' y='325'>∫₀¹ x dx = 1/2</text>\
<text x='370' y='325'>sin²θ+cos²θ=1</text>\
<text x='705' y='325'>y′=dy/dx</text>\
<text x='30' y='410'>mean = Σx/n</text>\
<text x='360' y='410'>Var(X)=E[X²]−(E[X])²</text>\
<text x='740' y='410'>y=1/x</text>\
</g>\
</svg>");
  background-repeat: repeat;
  background-size: 980px 560px;
}

/* Cards (dark glass, not white) */
.mba-card{
  border: 1px solid rgba(255,255,255,.16);
  background: linear-gradient(180deg, rgba(255,255,255,.10), rgba(255,255,255,.05));
  border-radius: 22px;
  padding: 18px;
  box-shadow: 0 18px 55px rgba(0,0,0,.38), 0 0 0 1px rgba(110,168,255,.08) inset;
}
.mba-card2{
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.05);
  border-radius: 20px;
  padding: 16px;
  box-shadow: 0 10px 28px rgba(0,0,0,.30), 0 0 0 1px rgba(124,240,214,.06) inset;
}

.mba-muted{ color: var(--muted); }
.mba-badge{
  display:inline-block;
  padding:7px 12px;
  border-radius:999px;
  border:1px solid rgba(255,255,255,.22);
  background: rgba(255,255,255,.06);
  color: var(--muted);
  font-size: 13px;
  margin-right: 8px;
}
.mba-highlight{ color: var(--a3); font-weight: 900; }

/* Buttons */
.stButton > button, .stDownloadButton > button{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.20) !important;
  background: linear-gradient(90deg, rgba(110,168,255,.98), rgba(124,240,214,.92)) !important;
  color: #061023 !important;
  font-weight: 900 !important;
  box-shadow: 0 10px 26px rgba(0,0,0,.28) !important;
}
.stButton > button:hover, .stDownloadButton > button:hover{
  transform: translateY(-1px);
  filter: brightness(1.06);
}

/* Inputs (typing must be visible) */
.stTextInput input, .stTextArea textarea{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.24) !important;
  background: rgba(6,10,24,.75) !important;
  color: #ffffff !important;
  caret-color: #ffffff !important;
  box-shadow: 0 0 0 1px rgba(110,168,255,.06) inset;
}
.stTextInput input::placeholder, .stTextArea textarea::placeholder{
  color: rgba(255,255,255,.65) !important;
}

/* Selectbox */
div[data-baseweb="select"] > div{
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,.24) !important;
  background: rgba(6,10,24,.75) !important;
  color: #ffffff !important;
}

/* Sidebar (no white) */
section[data-testid="stSidebar"]{
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03)) !important;
  border-right: 1px solid rgba(255,255,255,.12);
}
section[data-testid="stSidebar"]::before{
  content:"";
  position:absolute;
  inset:0;
  pointer-events:none;
  background:
    radial-gradient(520px 280px at 28% 0%, rgba(110,168,255,.14), transparent 60%),
    radial-gradient(520px 280px at 70% 18%, rgba(124,240,214,.10), transparent 65%);
  opacity: .95;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ------------------------------------------------------------
# 6) DATABASE
# ------------------------------------------------------------
def db():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        password_hash BLOB NOT NULL,
        is_paid INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS resources(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        curriculum TEXT NOT NULL,        -- WAEC / Cambridge / American
        resource_type TEXT NOT NULL,     -- Lesson Notes / Solved Problems / Past Papers / Other
        access_level TEXT NOT NULL,      -- Free / Paid
        file_path TEXT,
        external_link TEXT,
        is_featured INTEGER NOT NULL DEFAULT 0,
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS payment_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT NOT NULL,
        method TEXT NOT NULL,
        reference TEXT NOT NULL,
        note TEXT,
        status TEXT NOT NULL DEFAULT 'Pending',
        created_at TEXT NOT NULL
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS external_sites(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,          -- Cambridge / WAEC / American / General
        focus TEXT NOT NULL,
        url TEXT NOT NULL,
        is_active INTEGER NOT NULL DEFAULT 1,
        created_at TEXT NOT NULL
    )
    """)

    con.commit()

    # Seed admin if missing (admin always paid)
    cur.execute("SELECT email FROM users WHERE email=?", (ADMIN_EMAIL,))
    if cur.fetchone() is None:
        pw_hash = bcrypt.hashpw(ADMIN_DEFAULT_PASSWORD.encode("utf-8"), bcrypt.gensalt())
        cur.execute(
            "INSERT INTO users(email,name,password_hash,is_paid,created_at) VALUES(?,?,?,?,?)",
            (ADMIN_EMAIL, "Admin", pw_hash, 1, datetime.now().isoformat())
        )
        con.commit()

    # Seed external links if empty
    cur.execute("SELECT COUNT(*) FROM external_sites")
    if cur.fetchone()[0] == 0:
        defaults = [
            ("PastPaperPenguin", "Cambridge", "Worked solutions", "https://pastpaperpenguin.com/"),
            ("Maths Genie", "General", "Worked solutions + videos", "https://www.mathsgenie.co.uk/papers.php"),
            ("ExamSolutions", "General", "Video worked solutions", "https://www.examsolutions.net/examlevel/a-level/"),
            ("Physics & Maths Tutor", "General", "Past papers + mark schemes", "https://www.physicsandmathstutor.com/past-papers/"),
            ("Save My Exams", "General", "Past papers (some paid)", "https://www.savemyexams.com/past-papers/"),
            ("Revision World", "General", "Past papers", "https://revisionworld.com/gcse-revision/gcse-exam-past-papers"),
            ("CheetahWAEC", "WAEC", "Past questions + solutions (claims)", "https://cheetahwaec.com/past-papers"),
        ]
        now = datetime.now().isoformat()
        cur.executemany(
            "INSERT INTO external_sites(name,category,focus,url,is_active,created_at) VALUES(?,?,?,?,?,?)",
            [(n,c,f,u,1,now) for (n,c,f,u) in defaults]
        )
        con.commit()

    con.close()

init_db()

# ------------------------------------------------------------
# 7) AUTH HELPERS
# ------------------------------------------------------------
def get_user(email: str):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT email,name,password_hash,is_paid FROM users WHERE email=?", (email,))
    row = cur.fetchone()
    con.close()
    return row

def create_user(email: str, name: str, password: str):
    pw_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    con = db()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO users(email,name,password_hash,is_paid,created_at) VALUES(?,?,?,?,?)",
        (email, name, pw_hash, 0, datetime.now().isoformat())
    )
    con.commit()
    con.close()

def verify_password(password: str, pw_hash: bytes) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), pw_hash)

def set_paid(email: str, paid: bool):
    con = db()
    cur = con.cursor()
    cur.execute("UPDATE users SET is_paid=? WHERE email=?", (1 if paid else 0, email))
    con.commit()
    con.close()

def is_admin() -> bool:
    return st.session_state.get("auth_email") == ADMIN_EMAIL

def logout():
    for k in ["auth_email", "auth_name", "auth_paid"]:
        st.session_state.pop(k, None)

# ------------------------------------------------------------
# 8) RESOURCES HELPERS
# ------------------------------------------------------------
def add_resource(title, description, curriculum, rtype, access, file_path, link, featured):
    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO resources(title,description,curriculum,resource_type,access_level,file_path,external_link,is_featured,created_at)
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (title, description, curriculum, rtype, access, file_path, link, 1 if featured else 0, datetime.now().isoformat()))
    con.commit()
    con.close()

def fetch_resources(curriculum=None, access=None, rtype=None, query=None, featured_only=False, limit=200):
    con = db()
    cur = con.cursor()
    sql = """
      SELECT id,title,description,curriculum,resource_type,access_level,file_path,external_link,is_featured,created_at
      FROM resources WHERE 1=1
    """
    params = []

    if curriculum:
        sql += " AND curriculum=?"
        params.append(curriculum)
    if access:
        sql += " AND access_level=?"
        params.append(access)
    if rtype and rtype != "All":
        sql += " AND resource_type=?"
        params.append(rtype)
    if featured_only:
        sql += " AND is_featured=1"
    if query:
        sql += " AND (LOWER(title) LIKE ? OR LOWER(description) LIKE ?)"
        q = f"%{query.lower()}%"
        params.extend([q, q])

    sql += " ORDER BY is_featured DESC, id DESC LIMIT ?"
    params.append(int(limit))

    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    con.close()
    return rows

def delete_resource(res_id: int):
    con = db()
    cur = con.cursor()
    cur.execute("SELECT file_path FROM resources WHERE id=?", (res_id,))
    row = cur.fetchone()
    if row and row[0]:
        try:
            os.remove(row[0])
        except Exception:
            pass
    cur.execute("DELETE FROM resources WHERE id=?", (res_id,))
    con.commit()
    con.close()

def toggle_feature(res_id: int, on: bool):
    con = db()
    cur = con.cursor()
    cur.execute("UPDATE resources SET is_featured=? WHERE id=?", (1 if on else 0, res_id))
    con.commit()
    con.close()

# ------------------------------------------------------------
# 9) PAYMENTS (manual approval)
# ------------------------------------------------------------
def create_payment_request(user_email, method, reference, note):
    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO payment_requests(user_email,method,reference,note,status,created_at)
        VALUES(?,?,?,?,?,?)
    """, (user_email, method, reference, note, "Pending", datetime.now().isoformat()))
    con.commit()
    con.close()

def list_payment_requests(limit=200):
    con = db()
    cur = con.cursor()
    cur.execute("""
        SELECT id,user_email,method,reference,note,status,created_at
        FROM payment_requests ORDER BY id DESC LIMIT ?
    """, (int(limit),))
    rows = cur.fetchall()
    con.close()
    return rows

def set_payment_status(req_id: int, status: str):
    con = db()
    cur = con.cursor()
    cur.execute("UPDATE payment_requests SET status=? WHERE id=?", (status, req_id))
    con.commit()
    con.close()

# ------------------------------------------------------------
# 10) EXTERNAL SITES (links only)
# ------------------------------------------------------------
def list_sites(active_only=True, category="All", query=None, limit=300):
    con = db()
    cur = con.cursor()
    sql = "SELECT id,name,category,focus,url,is_active,created_at FROM external_sites WHERE 1=1"
    params = []
    if active_only:
        sql += " AND is_active=1"
    if category and category != "All":
        sql += " AND category=?"
        params.append(category)
    if query:
        sql += " AND (LOWER(name) LIKE ? OR LOWER(focus) LIKE ? OR LOWER(category) LIKE ?)"
        q = f"%{query.lower()}%"
        params.extend([q, q, q])
    sql += " ORDER BY category ASC, name ASC LIMIT ?"
    params.append(int(limit))
    cur.execute(sql, tuple(params))
    rows = cur.fetchall()
    con.close()
    return rows

def add_site(name, category, focus, url, active=True):
    con = db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO external_sites(name,category,focus,url,is_active,created_at)
        VALUES(?,?,?,?,?,?)
    """, (name, category, focus, url, 1 if active else 0, datetime.now().isoformat()))
    con.commit()
    con.close()

def set_site_active(site_id: int, active: bool):
    con = db()
    cur = con.cursor()
    cur.execute("UPDATE external_sites SET is_active=? WHERE id=?", (1 if active else 0, site_id))
    con.commit()
    con.close()

def delete_site(site_id: int):
    con = db()
    cur = con.cursor()
    cur.execute("DELETE FROM external_sites WHERE id=?", (site_id,))
    con.commit()
    con.close()

# ------------------------------------------------------------
# 11) HEADER
# ------------------------------------------------------------
left, right = st.columns([3, 2])
with left:
    st.markdown(
        f"""
        <div class="mba-card">
          <h1 style="margin:0">{APP_NAME}</h1>
          <div class="mba-muted" style="margin-top:6px">{TAGLINE}</div>
          <div class="mba-muted" style="margin-top:8px">
            <span class="mba-badge">Option 1</span> <span class="mba-highlight">{OPTION_1}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        """
        <div class="mba-card">
          <div class="mba-badge">∫</div><div class="mba-badge">Σ</div><div class="mba-badge">√</div>
          <div class="mba-badge">π</div><div class="mba-badge">∞</div><div class="mba-badge">Δ</div>
          <div class="mba-muted" style="margin-top:10px">
            Learn smarter. Solve faster. Think deeper.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

st.write("")

# ------------------------------------------------------------
# 12) SIDEBAR LOGIN / REGISTER (Portal feel)
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(f"## {APP_NAME}")
    st.markdown(f"<div class='mba-muted'>{TAGLINE}</div>", unsafe_allow_html=True)
    st.markdown("---")

    if "auth_email" not in st.session_state:
        st.markdown("### 🔐 Member Access")

        mode = st.radio("Choose:", ["Login", "Register"], horizontal=True)

        if mode == "Login":
            email = st.text_input("Email", key="login_email").strip().lower()
            pw = st.text_input("Password", type="password", key="login_pw")
            if st.button("Login", use_container_width=True):
                u = get_user(email)
                if not u:
                    st.error("No account found. Please register.")
                else:
                    _, name, pw_hash, paid = u
                    if verify_password(pw, pw_hash):
                        st.session_state["auth_email"] = email
                        st.session_state["auth_name"] = name
                        st.session_state["auth_paid"] = bool(paid)
                        st.success("Logged in ✅")
                        st.rerun()
                    else:
                        st.error("Incorrect password.")

        if mode == "Register":
            name2 = st.text_input("Full name", key="reg_name").strip()
            email2 = st.text_input("Email address", key="reg_email").strip().lower()
            pw2 = st.text_input("Create password", type="password", key="reg_pw")
            if st.button("Create account", use_container_width=True):
                if not (name2 and email2 and pw2):
                    st.error("Please fill all fields.")
                else:
                    try:
                        create_user(email2, name2, pw2)
                        st.success("Account created ✅ Now login.")
                    except Exception:
                        st.error("This email may already exist. Try logging in.")

        st.markdown("---")
        st.info("Login/register to access WAEC/Cambridge/American pages.")
    else:
        st.markdown("### ✅ Logged in")
        st.write(st.session_state.get("auth_name"))
        st.caption(st.session_state.get("auth_email"))
        st.write(f"**Plan:** {'PAID ✅' if st.session_state.get('auth_paid') else 'FREE'}")

        if st.button("Logout", use_container_width=True):
            logout()
            st.rerun()

        st.markdown("---")

# ------------------------------------------------------------
# 13) NAVIGATION
# ------------------------------------------------------------
if "auth_email" not in st.session_state:
    page = "Home"
else:
    pages = ["Home", "WAEC", "Cambridge", "American", "External Solved Past Papers", "Upgrade to Paid"]
    if is_admin():
        pages.append("Admin Dashboard")
    page = st.sidebar.radio("📌 Navigation", pages)

# ------------------------------------------------------------
# 14) UI BLOCKS
# ------------------------------------------------------------
def render_resource_card(row):
    rid, title, desc, cur, rtype, acc, fp, ext, feat, created = row
    st.markdown("<div class='mba-card2'>", unsafe_allow_html=True)
    st.markdown(f"### {title}")
    st.caption(f"{cur} • {rtype} • Access: {acc} • {created[:10]} {'• ⭐ Featured' if feat else ''}")
    if desc:
        st.write(desc)

    c1, c2, c3 = st.columns([1, 1, 3])
    with c1:
        if fp and os.path.exists(fp):
            with open(fp, "rb") as f:
                st.download_button("⬇️ Download", f, file_name=os.path.basename(fp), use_container_width=True)
    with c2:
        if ext:
            st.link_button("🌍 Open link", ext, use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.write("")

def show_curriculum_page(curriculum_name: str):
    st.markdown(
        f"<div class='mba-card'><h2 style='margin:0'>{curriculum_name} Resources</h2>"
        f"<div class='mba-muted'>Lesson Notes • Solved Problems • Past Papers • Other</div></div>",
        unsafe_allow_html=True
    )
    st.write("")

    q = st.text_input("Search (title/description)", key=f"q_{curriculum_name}").strip()
    rtype = st.selectbox("Filter by type", ["All", "Lesson Notes", "Solved Problems", "Past Papers", "Other"],
                         key=f"rtype_{curriculum_name}")

    st.markdown("## ✅ Free Section")
    free_rows = fetch_resources(curriculum=curriculum_name, access="Free", rtype=rtype, query=q if q else None)
    if not free_rows:
        st.info("No free resources yet.")
    for row in free_rows:
        render_resource_card(row)

    st.markdown("## 🔒 Paid Section")
    if not st.session_state.get("auth_paid"):
        st.warning("Paid resources are locked. Go to **Upgrade to Paid** to unlock everything.")
        return

    paid_rows = fetch_resources(curriculum=curriculum_name, access="Paid", rtype=rtype, query=q if q else None)
    if not paid_rows:
        st.info("No paid resources yet.")
    for row in paid_rows:
        render_resource_card(row)

def show_external_hub():
    st.markdown(
        "<div class='mba-card'><h2 style='margin:0'>External Solved Past Papers</h2>"
        "<div class='mba-muted'>Links only (we do not copy files). Admin can add/remove sites.</div></div>",
        unsafe_allow_html=True
    )
    st.write("")

    cat = st.selectbox("Category", ["All", "Cambridge", "WAEC", "American", "General"])
    q = st.text_input("Search sites").strip()

    rows = list_sites(active_only=True, category=cat, query=q if q else None)
    if not rows:
        st.info("No sites available yet.")
        return

    for _id, name, category, focus, url, is_active, created in rows:
        st.markdown("<div class='mba-card2'>", unsafe_allow_html=True)
        st.markdown(f"### {name}")
        st.caption(f"Category: {category} • Focus: {focus}")
        st.link_button("Open site", url, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        st.write("")

# ------------------------------------------------------------
# 15) MAIN PAGES
# ------------------------------------------------------------
if page == "Home":
    st.markdown(
        """
        <div class="mba-card">
          <h2 style="margin:0">Welcome 👋</h2>
          <div class="mba-muted" style="margin-top:10px">
            A beautiful learning portal designed to help students master Mathematics.
            <br><br>
            <b>Inside:</b> lesson notes, solved problems, past papers, and trusted external solved-paper sites.
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")

    st.markdown("## ⭐ Featured Resources")
    featured = fetch_resources(
        curriculum=None,
        access=None if st.session_state.get("auth_paid") else "Free",
        rtype=None,
        query=None,
        featured_only=True,
        limit=12
    )
    if not featured:
        st.info("No featured resources yet. (Admin can mark resources as Featured.)")
    else:
        for row in featured:
            render_resource_card(row)

elif page in ["WAEC", "Cambridge", "American"]:
    show_curriculum_page(page)

elif page == "External Solved Past Papers":
    show_external_hub()

elif page == "Upgrade to Paid":
    st.markdown(
        "<div class='mba-card'><h2 style='margin:0'>Upgrade to Paid 🔓</h2>"
        "<div class='mba-muted'>Option 1: One subscription unlocks ALL paid resources.</div></div>",
        unsafe_allow_html=True
    )
    st.write("")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>Stripe</h3><div class='mba-muted'>Pay securely with Stripe.</div></div>", unsafe_allow_html=True)
        st.link_button("Pay with Stripe", STRIPE_LINK, use_container_width=True)
    with c2:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>PayPal</h3><div class='mba-muted'>Pay via PayPal.</div></div>", unsafe_allow_html=True)
        st.link_button("Pay with PayPal", PAYPAL_LINK, use_container_width=True)
    with c3:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>Mobile Money</h3><div class='mba-muted'>Instruction link (WhatsApp).</div></div>", unsafe_allow_html=True)
        st.link_button("Pay via Mobile Money", MOBILE_MONEY_LINK, use_container_width=True)

    st.markdown("---")
    st.markdown("### Submit payment reference")
    st.caption("After payment, enter transaction/reference ID. Admin will approve and your account becomes PAID.")

    method = st.selectbox("Method used", ["Stripe", "PayPal", "Mobile Money"])
    reference = st.text_input("Payment reference / transaction ID").strip()
    note = st.text_area("Optional note").strip()

    if st.button("Submit for activation", use_container_width=True):
        if not reference:
            st.error("Please enter the payment reference / transaction ID.")
        else:
            create_payment_request(st.session_state["auth_email"], method, reference, note)
            st.success("Submitted ✅ Admin will verify and upgrade your account.")
            st.info("After approval, log out and log in again if it still shows FREE.")

elif page == "Admin Dashboard" and is_admin():
    st.markdown(
        "<div class='mba-card'><h2 style='margin:0'>Admin Dashboard 🛠️</h2>"
        "<div class='mba-muted'>Upload resources • Mark Featured • Approve payments • Manage external sites</div></div>",
        unsafe_allow_html=True
    )
    st.write("")

    tab1, tab2, tab3, tab4 = st.tabs(["📤 Upload Resources", "⭐ Manage Resources", "💳 Payment Requests", "🔗 External Sites"])

    with tab1:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>Upload Lesson Notes & Solved Problems</h3></div>", unsafe_allow_html=True)
        st.write("")
        title = st.text_input("Title", key="up_title").strip()
        curriculum = st.selectbox("Curriculum", ["WAEC", "Cambridge", "American"], key="up_curr")
        rtype = st.selectbox("Resource type", ["Lesson Notes", "Solved Problems", "Past Papers", "Other"], key="up_type")
        access = st.selectbox("Access level", ["Free", "Paid"], key="up_access")
        featured = st.checkbox("⭐ Mark as Featured (shows on Home)", value=False, key="up_feat")
        desc = st.text_area("Description (optional)", key="up_desc").strip()
        link = st.text_input("External link (optional)", key="up_link").strip()
        upfile = st.file_uploader("Upload file (PDF/docx/images)", key="up_file")

        if st.button("Upload now", use_container_width=True):
            if not title:
                st.error("Title is required.")
            else:
                file_path = ""
                if upfile is not None:
                    safe = upfile.name.replace("/", "_").replace("\\", "_")
                    file_path = os.path.join(UPLOAD_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe}")
                    with open(file_path, "wb") as f:
                        f.write(upfile.getbuffer())
                add_resource(title, desc, curriculum, rtype, access, file_path, link, featured)
                st.success("Uploaded ✅")

    with tab2:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>Manage Uploaded Resources</h3></div>", unsafe_allow_html=True)
        st.write("")
        cur_filter = st.selectbox("Filter curriculum", ["WAEC", "Cambridge", "American"], key="m_curr")
        q = st.text_input("Search resources", key="m_q").strip()
        rows = fetch_resources(curriculum=cur_filter, query=q if q else None, limit=200)

        if not rows:
            st.info("No resources yet.")
        for row in rows:
            rid, title, desc, cur, rtype, acc, fp, ext, feat, created = row
            st.markdown("<div class='mba-card2'>", unsafe_allow_html=True)
            st.write(f"**[{acc}] {title}** — {rtype} • {created[:10]} {'• ⭐ Featured' if feat else ''}")

            cA, cB, cC = st.columns([1, 1, 6])
            with cA:
                if st.button("⭐ Toggle", key=f"tog_{rid}", use_container_width=True):
                    toggle_feature(rid, not bool(feat))
                    st.rerun()
            with cB:
                if st.button("Delete", key=f"del_{rid}", use_container_width=True):
                    delete_resource(rid)
                    st.rerun()
            with cC:
                if desc: st.caption(desc)
                if ext: st.caption(f"Link: {ext}")

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

    with tab3:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>Payment Requests</h3></div>", unsafe_allow_html=True)
        st.write("")
        reqs = list_payment_requests(limit=200)
        if not reqs:
            st.info("No payment requests yet.")
        for rid, email, method, ref, note, status, created in reqs:
            st.markdown("<div class='mba-card2'>", unsafe_allow_html=True)
            st.write(f"**{email}** • {method} • Ref: `{ref}`")
            st.caption(f"Status: {status} • Date: {created[:10]}")
            if note: st.caption(note)

            c1, c2, c3 = st.columns([1, 1, 6])
            with c1:
                if st.button("Approve", key=f"ap_{rid}", use_container_width=True):
                    set_payment_status(rid, "Approved")
                    set_paid(email, True)
                    st.success("Approved ✅ user is now PAID.")
                    st.rerun()
            with c2:
                if st.button("Reject", key=f"rj_{rid}", use_container_width=True):
                    set_payment_status(rid, "Rejected")
                    st.warning("Rejected.")
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

    with tab4:
        st.markdown("<div class='mba-card2'><h3 style='margin-top:0'>External Solved Past Papers Hub</h3>"
                    "<div class='mba-muted'>Links only. Add/remove sites here.</div></div>", unsafe_allow_html=True)
        st.write("")
        st.markdown("### Add a new site")

        name = st.text_input("Site name", key="s_name").strip()
        category = st.selectbox("Category", ["Cambridge", "WAEC", "American", "General"], key="s_cat")
        focus = st.text_input("Focus (e.g., Worked solutions / Mark schemes)", key="s_focus").strip()
        url = st.text_input("URL", key="s_url").strip()

        if st.button("Add site", use_container_width=True):
            if not (name and focus and url):
                st.error("Fill name, focus, and url.")
            else:
                add_site(name, category, focus, url, active=True)
                st.success("Added ✅")
                st.rerun()

        st.markdown("---")
        st.markdown("### Manage sites")
        rows = list_sites(active_only=False, category="All", query=None, limit=400)

        for site_id, nm, cat, fc, u, active, created in rows:
            st.markdown("<div class='mba-card2'>", unsafe_allow_html=True)
            st.write(f"**{nm}** • {cat} • {fc}")
            st.caption(u)

            a, b, c = st.columns([1, 1, 1])
            with a:
                if st.button("Activate", key=f"act_{site_id}", use_container_width=True):
                    set_site_active(site_id, True)
                    st.rerun()
            with b:
                if st.button("Disable", key=f"dis_{site_id}", use_container_width=True):
                    set_site_active(site_id, False)
                    st.rerun()
            with c:
                if st.button("Delete", key=f"ds_{site_id}", use_container_width=True):
                    delete_site(site_id)
                    st.rerun()

            st.markdown("</div>", unsafe_allow_html=True)
            st.write("")

