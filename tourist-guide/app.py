"""Online Tourist Guide System - Flask + SQLite (BSc CS mini project)."""
import math
import os
import sqlite3
from functools import wraps

from flask import (Flask, abort, flash, g, redirect, render_template,
                   request, session, url_for)
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "tourist.db")

CATEGORIES = ["Heritage", "Nature", "Adventure", "Culture", "Beach", "Spiritual"]
ICONS = {"Heritage": "🏰", "Nature": "🌿", "Adventure": "🧗", "Culture": "🎭",
         "Beach": "🏖️", "Spiritual": "🛕"}
REVIEW_KINDS = ["Destination", "Hotel", "Restaurant"]

SEED = [
    ("Taj Mahal", "Agra", "Uttar Pradesh", "Heritage", "Iconic white-marble mausoleum built by Shah Jahan, a UNESCO World Heritage Site.", "Oct - Mar", 2500, 27.1751, 78.0421, 98),
    ("Gateway of India", "Mumbai", "Maharashtra", "Heritage", "Arch monument on the Mumbai waterfront, starting point for Elephanta Caves ferries.", "Nov - Feb", 2000, 18.9220, 72.8347, 90),
    ("Amer Fort", "Jaipur", "Rajasthan", "Heritage", "Hilltop fort-palace of red sandstone and marble with the stunning Sheesh Mahal.", "Oct - Mar", 2200, 26.9855, 75.8513, 88),
    ("Munnar Tea Gardens", "Munnar", "Kerala", "Nature", "Rolling hills covered in tea plantations, mist and waterfalls.", "Sep - Mar", 2800, 10.0889, 77.0595, 85),
    ("Rishikesh", "Rishikesh", "Uttarakhand", "Adventure", "Yoga capital of the world with river rafting, bungee jumping and Ganga aarti.", "Sep - Nov, Mar - May", 2400, 30.0869, 78.2676, 87),
    ("Baga Beach", "Goa", "Goa", "Beach", "Lively beach with water sports, shacks, seafood and nightlife.", "Nov - Feb", 3500, 15.5524, 73.7517, 92),
    ("Varanasi Ghats", "Varanasi", "Uttar Pradesh", "Spiritual", "Ancient riverside ghats on the Ganga, famous for sunrise boat rides and evening aarti.", "Oct - Mar", 1800, 25.3109, 83.0107, 84),
    ("Hampi", "Hampi", "Karnataka", "Heritage", "Ruins of the Vijayanagara empire spread across a boulder-strewn landscape.", "Oct - Feb", 1800, 15.3350, 76.4600, 80),
    ("Leh Ladakh", "Leh", "Ladakh", "Adventure", "High-altitude desert with monasteries, Pangong Lake and epic road trips.", "Jun - Sep", 4000, 34.1526, 77.5771, 91),
    ("Golden Temple", "Amritsar", "Punjab", "Spiritual", "Holiest Sikh shrine with a golden sanctum and a free community kitchen (langar).", "Oct - Mar", 1500, 31.6200, 74.8765, 93),
    ("Lonavala & Khandala", "Lonavala", "Maharashtra", "Nature", "Monsoon hill station near Mumbai/Pune with waterfalls, caves and viewpoints.", "Jun - Sep", 1800, 18.7546, 73.4062, 78),
    ("City Palace Udaipur", "Udaipur", "Rajasthan", "Culture", "Grand palace complex on Lake Pichola, the 'City of Lakes'.", "Sep - Mar", 2600, 24.5764, 73.6835, 86),
    ("Ajanta & Ellora Caves", "Aurangabad", "Maharashtra", "Culture", "Rock-cut Buddhist, Hindu and Jain cave temples, UNESCO World Heritage Sites.", "Oct - Mar", 1800, 20.5519, 75.7033, 82),
    ("Qutub Minar", "Delhi", "Delhi", "Heritage", "A towering 12th-century minaret and UNESCO World Heritage Site surrounded by historic monuments.", "Oct - Mar", 2200, 28.5245, 77.1855, 83),
    ("Red Fort", "Delhi", "Delhi", "Heritage", "Historic Mughal fort complex and a major landmark of India's capital.", "Oct - Mar", 2400, 28.6562, 77.2410, 86),
    ("Kaziranga National Park", "Kohora", "Assam", "Nature", "Wildlife reserve known for the Indian one-horned rhinoceros and grassland safaris.", "Nov - Apr", 4200, 26.5775, 93.1711, 76),
    ("Sundarbans", "Gosaba", "West Bengal", "Nature", "Vast mangrove forest and delta ecosystem with boat-based wildlife experiences.", "Nov - Feb", 3500, 21.9497, 88.8890, 73),
    ("Darjeeling", "Darjeeling", "West Bengal", "Nature", "Himalayan hill town famous for tea gardens, mountain views and its heritage railway.", "Mar - May, Oct - Dec", 3000, 27.0360, 88.2627, 84),
    ("Shillong", "Shillong", "Meghalaya", "Nature", "Hill city with waterfalls, viewpoints and access to Meghalaya's living-root-bridge region.", "Oct - Apr", 2800, 25.5788, 91.8933, 79),
    ("Living Root Bridges", "Cherrapunji", "Meghalaya", "Adventure", "Remarkable bridges grown from living tree roots, reached by scenic hikes.", "Oct - Apr", 3200, 25.2702, 91.7300, 80),
    ("Jaisalmer Fort", "Jaisalmer", "Rajasthan", "Heritage", "Golden sandstone fort with narrow lanes, historic havelis and desert culture.", "Nov - Feb", 2600, 26.9124, 70.9126, 82),
    ("Ranthambore National Park", "Sawai Madhopur", "Rajasthan", "Nature", "Tiger reserve with guided jeep and canter safaris; sightings are never guaranteed.", "Oct - Apr", 5000, 26.0173, 76.5026, 81),
    ("Khajuraho Temples", "Khajuraho", "Madhya Pradesh", "Heritage", "Medieval temple complex renowned for intricate stone carvings and architecture.", "Oct - Mar", 2200, 24.8318, 79.9199, 77),
    ("Sanchi Stupa", "Sanchi", "Madhya Pradesh", "Spiritual", "Ancient Buddhist monument and UNESCO World Heritage Site.", "Oct - Mar", 1800, 23.4793, 77.7397, 72),
    ("Konark Sun Temple", "Konark", "Odisha", "Heritage", "13th-century temple designed as a monumental stone chariot dedicated to the Sun God.", "Oct - Feb", 2200, 19.8876, 86.0945, 78),
    ("Puri Beach", "Puri", "Odisha", "Beach", "Popular Bay of Bengal coastline close to the Jagannath Temple and local seafood.", "Oct - Feb", 2500, 19.7983, 85.8249, 80),
    ("Havelock Island", "Swaraj Dweep", "Andaman and Nicobar Islands", "Beach", "Island destination known for clear water, beaches, snorkelling and diving.", "Nov - Apr", 6000, 11.9674, 92.9876, 89),
    ("Kovalam Beach", "Thiruvananthapuram", "Kerala", "Beach", "Curved sandy beaches, lighthouse views and coastal resorts.", "Oct - Mar", 3200, 8.4004, 76.9787, 79),
    ("Meenakshi Amman Temple", "Madurai", "Tamil Nadu", "Spiritual", "Historic temple complex known for its colourful gopurams and detailed sculpture.", "Oct - Mar", 2000, 9.9195, 78.1193, 87),
    ("Ooty", "Ooty", "Tamil Nadu", "Nature", "Nilgiri hill station with gardens, lakes, tea estates and a heritage mountain railway.", "Oct - Jun", 3000, 11.4102, 76.6950, 83),
    ("Mysore Palace", "Mysuru", "Karnataka", "Culture", "Ornate royal palace famous for Indo-Saracenic architecture and illuminated evenings.", "Oct - Mar", 2200, 12.3052, 76.6552, 85),
    ("Coorg", "Kodagu", "Karnataka", "Nature", "Green coffee-growing hills, waterfalls, forest trails and homestays.", "Oct - Mar", 3000, 12.3375, 75.8069, 81),
    ("Mahabalipuram Shore Temple", "Mahabalipuram", "Tamil Nadu", "Heritage", "Seaside Pallava-era temple and stone monuments on the Coromandel Coast.", "Nov - Feb", 2200, 12.6169, 80.1927, 75),
    ("Tirupati", "Tirupati", "Andhra Pradesh", "Spiritual", "Major pilgrimage destination in the Tirumala hills; darshan rules and booking may apply.", "Sep - Feb", 2500, 13.6833, 79.3470, 90),
    ("Charminar", "Hyderabad", "Telangana", "Culture", "Iconic four-minaret monument in Hyderabad's historic market district.", "Oct - Feb", 2300, 17.3616, 78.4747, 81),
    ("Statue of Unity", "Kevadia", "Gujarat", "Culture", "Large monument near the Narmada River with viewing and visitor attractions.", "Oct - Feb", 3000, 21.8380, 73.7191, 80),
    ("Somnath Temple", "Prabhas Patan", "Gujarat", "Spiritual", "Coastal temple complex and pilgrimage site overlooking the Arabian Sea.", "Oct - Mar", 2200, 20.8880, 70.4012, 79),
    ("Mahabaleshwar", "Mahabaleshwar", "Maharashtra", "Nature", "Western Ghats hill station with viewpoints, forest walks and strawberry farms.", "Oct - Jun", 2800, 17.9307, 73.6477, 82),
    ("Elephanta Caves", "Mumbai Harbour", "Maharashtra", "Culture", "Island cave temples with monumental rock-cut sculpture, reached by ferry from Mumbai.", "Nov - Feb", 2200, 18.9633, 72.9315, 78),
]


# ---------- database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db = sqlite3.connect(DB_PATH)
    db.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL, password TEXT NOT NULL, is_admin INTEGER DEFAULT 0);
    CREATE TABLE IF NOT EXISTS destinations(
        id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, city TEXT, state TEXT,
        category TEXT, description TEXT, best_time TEXT, budget_per_day INTEGER,
        lat REAL, lng REAL, popularity INTEGER DEFAULT 50);
    CREATE TABLE IF NOT EXISTS reviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT, dest_id INTEGER, user_id INTEGER,
        kind TEXT, rating INTEGER, comment TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP);
    CREATE TABLE IF NOT EXISTS itinerary(
        id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, dest_id INTEGER, day INTEGER);
    """)
    # Add any new sample destinations without duplicating records in an existing database.
    existing = {row[0] for row in db.execute("SELECT name FROM destinations").fetchall()}
    for item in SEED:
        if item[0] not in existing:
            db.execute("""INSERT INTO destinations(name,city,state,category,description,
                best_time,budget_per_day,lat,lng,popularity) VALUES(?,?,?,?,?,?,?,?,?,?)""", item)
    if db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        db.execute("INSERT INTO users(name,email,password,is_admin) VALUES(?,?,?,1)",
                   ("Admin", "admin@tourist.com", generate_password_hash("admin123")))
    db.commit()
    db.close()


# ---------- auth helpers ----------
@app.before_request
def load_user():
    g.user = None
    if "user_id" in session:
        g.user = get_db().execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if not g.user:
            flash("Please log in first.", "warn")
            return redirect(url_for("login", next=request.path))
        return f(*a, **kw)
    return wrapper


def admin_required(f):
    @wraps(f)
    @login_required
    def wrapper(*a, **kw):
        if not g.user["is_admin"]:
            abort(403)
        return f(*a, **kw)
    return wrapper


@app.context_processor
def inject_globals():
    return dict(CATEGORIES=CATEGORIES, ICONS=ICONS, REVIEW_KINDS=REVIEW_KINDS)


def haversine(lat1, lng1, lat2, lng2):
    r = 6371
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = p2 - p1, math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


# ---------- public pages ----------
@app.route("/")
def index():
    db = get_db()
    top = db.execute("SELECT * FROM destinations ORDER BY popularity DESC LIMIT 6").fetchall()
    return render_template("index.html", top=top)


@app.route("/destinations")
def destinations():
    q = request.args.get("q", "").strip()
    cat = request.args.get("category", "")
    state = request.args.get("state", "")
    min_budget = request.args.get("min_budget", type=int)
    max_budget = request.args.get("max_budget", type=int)
    sort = request.args.get("sort", "popularity")
    sql, args = """SELECT d.*, ROUND(AVG(r.rating),1) AS avg_rating, COUNT(r.id) AS n_reviews
                   FROM destinations d LEFT JOIN reviews r ON r.dest_id=d.id WHERE 1=1""", []
    if q:
        sql += " AND (d.name LIKE ? OR d.city LIKE ? OR d.state LIKE ? OR d.description LIKE ? OR d.category LIKE ?)"
        args += [f"%{q}%"] * 5
    if cat:
        sql += " AND d.category=?"
        args.append(cat)
    if state:
        sql += " AND d.state=?"
        args.append(state)
    if min_budget is not None:
        sql += " AND d.budget_per_day>=?"
        args.append(min_budget)
    if max_budget is not None:
        sql += " AND d.budget_per_day<=?"
        args.append(max_budget)
    order = {"popularity": "d.popularity DESC", "budget": "d.budget_per_day ASC",
             "name": "d.name ASC"}.get(sort, "d.popularity DESC")
    rows = get_db().execute(sql + f" GROUP BY d.id ORDER BY {order}", args).fetchall()
    states = [r[0] for r in get_db().execute(
        "SELECT DISTINCT state FROM destinations WHERE state IS NOT NULL AND state!='' ORDER BY state"
    ).fetchall()]
    return render_template("destinations.html", rows=rows, q=q, cat=cat, state=state,
                           states=states, min_budget=min_budget if min_budget is not None else "",
                           max_budget=max_budget if max_budget is not None else "", sort=sort)


@app.route("/destination/<int:did>")
def destination(did):
    db = get_db()
    d = db.execute("SELECT * FROM destinations WHERE id=?", (did,)).fetchone() or abort(404)
    reviews = db.execute("""SELECT r.*, u.name FROM reviews r JOIN users u ON u.id=r.user_id
                            WHERE dest_id=? ORDER BY r.id DESC""", (did,)).fetchall()
    avg = round(sum(r["rating"] for r in reviews) / len(reviews), 1) if reviews else None
    return render_template("destination.html", d=d, reviews=reviews, avg=avg)


@app.route("/destination/<int:did>/review", methods=["POST"])
@login_required
def add_review(did):
    rating = request.form.get("rating", type=int)
    comment = request.form.get("comment", "").strip()
    kind = request.form.get("kind", "Destination")
    if not rating or not 1 <= rating <= 5 or not comment or kind not in REVIEW_KINDS:
        flash("Give a rating (1-5) and a comment.", "warn")
    else:
        get_db().execute("INSERT INTO reviews(dest_id,user_id,kind,rating,comment) VALUES(?,?,?,?,?)",
                         (did, g.user["id"], kind, rating, comment[:500]))
        get_db().commit()
        flash("Review posted. Thanks!", "ok")
    return redirect(url_for("destination", did=did))


# ---------- auth ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        pw = request.form["password"]
        if not name or "@" not in email or len(pw) < 6:
            flash("Enter a name, valid email and a password of 6+ characters.", "warn")
        else:
            try:
                get_db().execute("INSERT INTO users(name,email,password) VALUES(?,?,?)",
                                 (name, email, generate_password_hash(pw)))
                get_db().commit()
                flash("Account created. Please log in.", "ok")
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                flash("That email is already registered.", "warn")
    return render_template("auth.html", mode="register")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        u = get_db().execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        if u and check_password_hash(u["password"], request.form["password"]):
            session["user_id"] = u["id"]
            nxt = request.args.get("next", "")
            return redirect(nxt if nxt.startswith("/") else url_for("index"))
        flash("Wrong email or password.", "warn")
    return render_template("auth.html", mode="login")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ---------- itinerary ----------
@app.route("/itinerary")
@login_required
def itinerary():
    travellers = max(1, request.args.get("travellers", 1, type=int))
    items = get_db().execute("""SELECT i.id AS item_id, i.day, d.* FROM itinerary i
        JOIN destinations d ON d.id=i.dest_id WHERE i.user_id=? ORDER BY i.day, i.id""",
        (g.user["id"],)).fetchall()
    days, legs, total_km = {}, [], 0.0
    for it in items:
        days.setdefault(it["day"], []).append(it)
    for a, b in zip(items, items[1:]):
        km = haversine(a["lat"], a["lng"], b["lat"], b["lng"])
        total_km += km
        legs.append((a["name"], b["name"], round(km)))
    per_person = sum(it["budget_per_day"] for it in items)
    return render_template("itinerary.html", days=days, legs=legs, total_km=round(total_km),
                           per_person=per_person, total=per_person * travellers,
                           travellers=travellers, items=items,
                           pts=[[i["lat"], i["lng"]] for i in items],
                           names=[i["name"] for i in items])


@app.route("/itinerary/add/<int:did>", methods=["POST"])
@login_required
def itinerary_add(did):
    day = min(max(request.form.get("day", 1, type=int), 1), 15)
    get_db().execute("INSERT INTO itinerary(user_id,dest_id,day) VALUES(?,?,?)", (g.user["id"], did, day))
    get_db().commit()
    flash(f"Added to Day {day} of your itinerary.", "ok")
    return redirect(url_for("itinerary"))


@app.route("/itinerary/remove/<int:item_id>", methods=["POST"])
@login_required
def itinerary_remove(item_id):
    get_db().execute("DELETE FROM itinerary WHERE id=? AND user_id=?", (item_id, g.user["id"]))
    get_db().commit()
    return redirect(url_for("itinerary"))


# ---------- admin ----------
@app.route("/admin")
@admin_required
def admin():
    db = get_db()
    stats = {t: db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
             for t in ("users", "destinations", "reviews", "itinerary")}
    dests = db.execute("SELECT * FROM destinations ORDER BY id DESC").fetchall()
    reviews = db.execute("""SELECT r.*, u.name AS uname, d.name AS dname FROM reviews r
        JOIN users u ON u.id=r.user_id JOIN destinations d ON d.id=r.dest_id
        ORDER BY r.id DESC LIMIT 30""").fetchall()
    return render_template("admin.html", stats=stats, dests=dests, reviews=reviews)


@app.route("/admin/destination/new", methods=["GET", "POST"])
@app.route("/admin/destination/<int:did>/edit", methods=["GET", "POST"])
@admin_required
def admin_destination(did=None):
    db = get_db()
    d = db.execute("SELECT * FROM destinations WHERE id=?", (did,)).fetchone() if did else None
    if request.method == "POST":
        f = request.form
        vals = (f["name"], f["city"], f["state"], f["category"], f["description"], f["best_time"],
                f.get("budget_per_day", 0, type=int), f.get("lat", 0, type=float),
                f.get("lng", 0, type=float), f.get("popularity", 50, type=int))
        if did:
            db.execute("""UPDATE destinations SET name=?,city=?,state=?,category=?,description=?,
                best_time=?,budget_per_day=?,lat=?,lng=?,popularity=? WHERE id=?""", vals + (did,))
        else:
            db.execute("""INSERT INTO destinations(name,city,state,category,description,best_time,
                budget_per_day,lat,lng,popularity) VALUES(?,?,?,?,?,?,?,?,?,?)""", vals)
        db.commit()
        flash("Destination saved.", "ok")
        return redirect(url_for("admin"))
    return render_template("admin_form.html", d=d)


@app.route("/admin/destination/<int:did>/delete", methods=["POST"])
@admin_required
def admin_delete_destination(did):
    db = get_db()
    for sql in ("DELETE FROM reviews WHERE dest_id=?", "DELETE FROM itinerary WHERE dest_id=?",
                "DELETE FROM destinations WHERE id=?"):
        db.execute(sql, (did,))
    db.commit()
    flash("Destination deleted.", "ok")
    return redirect(url_for("admin"))


@app.route("/admin/review/<int:rid>/delete", methods=["POST"])
@admin_required
def admin_delete_review(rid):
    get_db().execute("DELETE FROM reviews WHERE id=?", (rid,))
    get_db().commit()
    flash("Review removed.", "ok")
    return redirect(url_for("admin"))


init_db()

if __name__ == "__main__":
    app.run(debug=True)
