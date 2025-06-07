import streamlit as st

# Page config
st.set_page_config(page_title="Sports Bet Evaluator", layout="centered")
st.title("📊 Sports Bet Evaluator")

# --------------------------
# Initialize session state
# --------------------------
for key, default in {
    "bet_name": "",
    "last5": 50,
    "last10": 50,
    "last20": 50,
    "h2h": 50,
    "season": 50,
    "prev_season": 50,
    "ai_conf": 50,
    "best_odds": 100,
    "selected_sportsbook": ""
}.items():
    st.session_state.setdefault(key, default)

# --------------------------
# Inputs
# --------------------------
bet_name = st.text_input("📝 Enter Bet Name", value=st.session_state.bet_name, key="bet_name")

st.subheader("📈 Success Rate Inputs (%)")
last_5 = st.slider("Last 5 Games", 0, 100, st.session_state.last5, key="last5")
last_10 = st.slider("Last 10 Games", 0, 100, st.session_state.last10, key="last10")
last_20 = st.slider("Last 20 Games", 0, 100, st.session_state.last20, key="last20")
h2h = st.slider("H2H Matchups", 0, 100, st.session_state.h2h, key="h2h")
season = st.slider("Current Season", 0, 100, st.session_state.season, key="season")
prev_season = st.slider("Previous Season", 0, 100, st.session_state.prev_season, key="prev_season")
ai_conf = st.slider("🤖 AI Confidence Score (1–100)", 1, 100, st.session_state.ai_conf, key="ai_conf")

# --------------------------
# Estimated Win Probability
# --------------------------
weights = {
    "last_5": 0.10,
    "last_10": 0.20,
    "last_20": 0.05,
    "h2h": 0.15,
    "season": 0.25,
    "prev_season": 0.05,
    "ai_conf": 0.20
}

est_win_prob = (
    last_5 * weights["last_5"] +
    last_10 * weights["last_10"] +
    last_20 * weights["last_20"] +
    h2h * weights["h2h"] +
    season * weights["season"] +
    prev_season * weights["prev_season"] +
    ai_conf * weights["ai_conf"]
) / sum(weights.values())

st.markdown(f"### 🎯 Estimated Win Probability: `{round(est_win_prob, 2)}%`")

# --------------------------
# Odds Input + EV Calculation
# --------------------------
st.subheader("💰 Enter Best Sportsbook Odds")
best_odds = st.number_input("American Odds (e.g. +120 or -135)", value=st.session_state.best_odds, key="best_odds")
selected_sportsbook = st.selectbox("🏦 Select Sportsbook", ["DraftKings", "FanDuel", "BetMGM", "Caesars", "PointsBet", "NoVig"], key="selected_sportsbook")

# Calculate implied probability
if best_odds > 0:
    implied_prob = 100 / (best_odds + 100)
else:
    implied_prob = abs(best_odds) / (abs(best_odds) + 100)

# Adjust EV by AI confidence factor
ai_conf_factor = ai_conf / 100
raw_ev = est_win_prob / 100 - implied_prob
plus_ev = raw_ev * ai_conf_factor
plus_ev_percent = round(plus_ev * 100, 2)

st.metric("📈 +EV %", f"{plus_ev_percent}%")

# --------------------------
# Grade Assignment (with AI influence)
# --------------------------
if plus_ev_percent >= 15:
    grade = "A+"
elif plus_ev_percent >= 10:
    grade = "A"
elif plus_ev_percent >= 5:
    grade = "B"
elif plus_ev_percent >= 0:
    grade = "C"
else:
    grade = "D"

# Modify grade based on AI confidence
if ai_conf >= 85 and grade in ["B", "C"]:
    grade = "A" if grade == "B" else "B"
elif ai_conf <= 40 and grade in ["A+", "A", "B"]:
    grade = "C" if grade == "B" else "B"

# --------------------------
# Star Rating (Optional)
# --------------------------
if ai_conf >= 90:
    stars = "⭐⭐⭐⭐⭐"
elif ai_conf >= 75:
    stars = "⭐⭐⭐⭐"
elif ai_conf >= 60:
    stars = "⭐⭐⭐"
elif ai_conf >= 40:
    stars = "⭐⭐"
else:
    stars = "⭐"

st.markdown(f"### 🏅 Bet Grade: `{grade}`   {stars}")

# --------------------------
# Save Evaluation
# --------------------------
if "saved_bets" not in st.session_state:
    st.session_state.saved_bets = []

if st.button("💾 Save Evaluation") and bet_name:
    st.session_state.saved_bets.append({
        "Bet": bet_name,
        "Win Probability": f"{round(est_win_prob, 2)}%",
        "+EV %": f"{plus_ev_percent}%",
        "Grade": grade,
        "AI Confidence": f"{ai_conf}/100",
        "Sportsbook": selected_sportsbook
    })

# --------------------------
# Display Saved Bets
# --------------------------
if st.session_state.saved_bets:
    st.subheader("📋 Saved Evaluations")
    st.table(st.session_state.saved_bets)

# --------------------------
# Clear Inputs Button
# --------------------------
if st.button("🧹 Clear All Inputs"):
    for key in ["bet_name", "last5", "last10", "last20", "h2h", "season", "prev_season", "ai_conf", "best_odds", "selected_sportsbook"]:
        st.session_state[key] = "" if isinstance(st.session_state[key], str) else 50 if key == "ai_conf" else 100 if key == "best_odds" else 50
    st.experimental_rerun()
