# Online Tourist Guide System

A web-based platform for destination discovery and trip planning (BSc Computer Science project).
Built with **Python Flask + SQLite**, HTML/CSS/JS, and **Leaflet / OpenStreetMap** maps.

## Features
- User registration & login (hashed passwords)
- Destination search across name, city, state, category and description\n- Filters for category, state, minimum/maximum daily budget, and sorting\n- 39 starter destinations across India (editable via the admin dashboard)\n- Interactive trip cost estimator by days, travellers and budget style (illustrative estimates)
- Destination details with map and Google Maps directions link
- Day-wise itinerary planner with budget estimator and route distance
- Reviews & ratings for destinations, hotels and restaurants
- Admin dashboard: add / edit / delete destinations, moderate reviews

## Run locally
```bash
git clone <your-repo-url>
cd tourist-guide
python -m venv venv
venv\Scripts\activate        # Windows  (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 (the database is created automatically on first run).

**Demo admin login:** `admin@tourist.com` / `admin123` (change this before any real deployment).

## Project structure
```
app.py            # routes, database, logic
templates/        # HTML pages (Jinja2)
static/style.css  # styling
requirements.txt
```

## Push to GitHub
```bash
git init
git add .
git commit -m "Online Tourist Guide System"
git branch -M main
git remote add origin https://github.com/<username>/tourist-guide.git
git push -u origin main
```

## Future enhancements
AI recommendations, hotel/transport booking, offline mode, multi-language, chatbot.

\n## Budget estimate note
\nDestination daily budgets and the budget/standard/premium multipliers are illustrative planning estimates, not live quotes. They can vary with season, transport, accommodation and activities. Confirm current prices before booking.
\n