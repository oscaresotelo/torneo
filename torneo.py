import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import random
import os

# ─── FORCE DARK THEME ──────────────────────────────────────────────────────────
os.makedirs(".streamlit", exist_ok=True)
with open(".streamlit/config.toml", "w") as _f:
    _f.write("[theme]\nbase = \"dark\"\n")

# ─── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="♠ Poker Tournament Manager",
    page_icon="♠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── CUSTOM CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');

:root {
    --green: #0d5c2e;
    --green-felt: #1a7a42;
    --gold: #d4af37;
    --gold-light: #f0d060;
    --red: #c0392b;
    --dark: #0a0a0a;
    --surface: #111827;
    --surface2: #1f2937;
    --text: #f0ead6;
    --text-dim: #9ca3af;
    --border: #374151;
    --chip-blue: #2563eb;
    --chip-red: #dc2626;
    --chip-black: #1c1917;
}

/* Global */
html, body, [class*="css"] {
    font-family: 'Rajdhani', sans-serif;
    color: var(--text);
}

.stApp {
    background: radial-gradient(ellipse at top, #0d1f14 0%, #060d09 60%, #000 100%);
    background-attachment: fixed;
}

/* Header */
.poker-header {
    text-align: center;
    padding: 1.5rem 0 0.5rem;
    border-bottom: 2px solid var(--gold);
    margin-bottom: 1.5rem;
}

.poker-header h1 {
    font-family: 'Bebas Neue', cursive;
    font-size: 3.5rem;
    letter-spacing: 8px;
    color: var(--gold);
    text-shadow: 0 0 30px rgba(212,175,55,0.4);
    margin: 0;
    line-height: 1;
}

.poker-header p {
    font-family: 'Share Tech Mono', monospace;
    color: var(--text-dim);
    font-size: 0.85rem;
    letter-spacing: 3px;
    margin-top: 0.3rem;
}

/* Cards/Panels */
.panel {
    background: linear-gradient(135deg, #1a2a1e 0%, #111 100%);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1rem;
    box-shadow: 0 4px 20px rgba(0,0,0,0.5);
}

.panel-gold {
    border-color: var(--gold);
    box-shadow: 0 4px 20px rgba(212,175,55,0.15);
}

.panel-title {
    font-family: 'Bebas Neue', cursive;
    font-size: 1.4rem;
    letter-spacing: 3px;
    color: var(--gold);
    margin-bottom: 0.8rem;
    border-bottom: 1px solid #333;
    padding-bottom: 0.4rem;
}

/* Timer Display */
.timer-display {
    font-family: 'Share Tech Mono', monospace;
    font-size: 5rem;
    text-align: center;
    color: var(--gold-light);
    text-shadow: 0 0 20px rgba(240,208,96,0.5), 0 0 40px rgba(240,208,96,0.2);
    line-height: 1;
    padding: 0.5rem 0;
}

.timer-warning {
    color: #f97316 !important;
    text-shadow: 0 0 20px rgba(249,115,22,0.6) !important;
    animation: pulse 1s ease-in-out infinite;
}

.timer-critical {
    color: var(--red) !important;
    text-shadow: 0 0 25px rgba(192,57,43,0.8) !important;
    animation: pulse 0.5s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.6; }
}

/* Blind Level Display */
.blind-display {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin: 1rem 0;
}

.blind-box {
    text-align: center;
    background: linear-gradient(135deg, #1e3a28 0%, #0d1f14 100%);
    border: 1px solid var(--green-felt);
    border-radius: 10px;
    padding: 0.8rem 1.5rem;
    min-width: 120px;
}

.blind-label {
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.75rem;
    letter-spacing: 2px;
    color: var(--text-dim);
    text-transform: uppercase;
}

.blind-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 2rem;
    color: var(--gold);
    font-weight: bold;
}

.blind-next {
    font-size: 0.9rem !important;
    color: var(--text-dim) !important;
}

/* Level Badge */
.level-badge {
    display: inline-block;
    background: var(--gold);
    color: #000;
    font-family: 'Bebas Neue', cursive;
    font-size: 1rem;
    letter-spacing: 2px;
    padding: 0.2rem 0.8rem;
    border-radius: 20px;
}

/* Status Badge */
.status-active { color: #22c55e; }
.status-eliminated { color: var(--red); text-decoration: line-through; }
.status-busted { color: #6b7280; }

/* Metric Cards */
.metric-row {
    display: flex;
    gap: 0.8rem;
    flex-wrap: wrap;
    margin: 0.5rem 0;
}

.metric-card {
    flex: 1;
    min-width: 110px;
    background: linear-gradient(135deg, #1f2937 0%, #111827 100%);
    border: 1px solid #374151;
    border-radius: 10px;
    padding: 0.8rem;
    text-align: center;
}

.metric-value {
    font-family: 'Share Tech Mono', monospace;
    font-size: 1.6rem;
    color: var(--gold);
    display: block;
}

.metric-label {
    font-size: 0.7rem;
    letter-spacing: 1.5px;
    color: var(--text-dim);
    text-transform: uppercase;
    margin-top: 0.2rem;
}

/* Player Table */
.player-row-active { background: rgba(26, 122, 66, 0.08) !important; }
.player-row-out { opacity: 0.5; }

/* Buttons */
.stButton > button {
    font-family: 'Rajdhani', sans-serif;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    border-radius: 8px;
    transition: all 0.2s;
}

/* Alert Banner */
.alert-banner {
    background: linear-gradient(90deg, #7c2d12, #dc2626, #7c2d12);
    border: 1px solid #ef4444;
    border-radius: 8px;
    padding: 0.6rem 1rem;
    text-align: center;
    font-family: 'Bebas Neue', cursive;
    font-size: 1.3rem;
    letter-spacing: 3px;
    color: white;
    animation: pulse 1s ease-in-out infinite;
    margin-bottom: 0.5rem;
}

.info-banner {
    background: linear-gradient(90deg, #1e3a5f, #2563eb, #1e3a5f);
    border: 1px solid #3b82f6;
    border-radius: 8px;
    padding: 0.4rem 1rem;
    text-align: center;
    font-family: 'Rajdhani', sans-serif;
    font-size: 0.9rem;
    letter-spacing: 2px;
    color: #bfdbfe;
    margin-bottom: 0.5rem;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0d1f14 0%, #060d09 100%);
    border-right: 1px solid #1a3a24;
}

section[data-testid="stSidebar"] .stRadio label {
    color: var(--text) !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.35rem !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
}

section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 1.35rem !important;
    font-weight: 700 !important;
}

/* Prize pool */
.prize-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.4rem 0.6rem;
    border-radius: 6px;
    margin-bottom: 0.3rem;
    font-family: 'Rajdhani', sans-serif;
    font-size: 1rem;
    font-weight: 600;
}

.prize-1st { background: linear-gradient(90deg, rgba(212,175,55,0.2), transparent); border-left: 3px solid var(--gold); }
.prize-2nd { background: linear-gradient(90deg, rgba(192,192,192,0.15), transparent); border-left: 3px solid #9ca3af; }
.prize-3rd { background: linear-gradient(90deg, rgba(180,83,9,0.15), transparent); border-left: 3px solid #b45309; }
.prize-other { background: rgba(255,255,255,0.03); border-left: 3px solid #374151; }

/* Chip display */
.chip {
    display: inline-block;
    width: 20px; height: 20px;
    border-radius: 50%;
    border: 2px dashed;
    vertical-align: middle;
    margin-right: 4px;
}
.chip-blue { background: #1d4ed8; border-color: #93c5fd; }
.chip-red { background: #991b1b; border-color: #fca5a5; }
.chip-black { background: #1c1917; border-color: #78716c; }
.chip-green { background: #166534; border-color: #86efac; }

/* Input overrides */
.stNumberInput input, .stTextInput input, .stSelectbox select {
    background: #1f2937 !important;
    color: var(--text) !important;
    border-color: #374151 !important;
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.4rem !important;
}

/* Input labels */
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stFileUploader label, .stToggle label {
    font-family: 'Rajdhani', sans-serif !important;
    font-size: 1.2rem !important;
    font-weight: 700 !important;
    color: var(--text) !important;
    letter-spacing: 1px !important;
}

/* Button text */
.stButton > button {
    font-size: 1.15rem !important;
}

/* Divider */
.card-divider {
    border: none;
    border-top: 1px solid #1f2937;
    margin: 0.8rem 0;
}

/* Suit display */
.suits { font-size: 1.2rem; }
.suit-s { color: #e2e8f0; }
.suit-h { color: #dc2626; }
.suit-d { color: #dc2626; }
.suit-c { color: #e2e8f0; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: transparent;
    gap: 0.5rem;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Rajdhani', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 1.5px !important;
    text-transform: uppercase !important;
    color: var(--text-dim) !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
}

.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}

</style>
""", unsafe_allow_html=True)

# ─── SESSION STATE INIT ────────────────────────────────────────────────────────
def get_default_blind_templates():
    return {
        "EPL — 25 min (imagen)":   get_default_blinds(),
        "Turbo (8 min)":           [{**b, "duration": 8}  for b in get_default_blinds()],
        "Hyper (5 min)":           [{**b, "duration": 5}  for b in get_default_blinds()],
        "Deep Stack (30 min)":     [{**b, "duration": 30} for b in get_default_blinds()],
    }

def init_state():
    defaults = {
        "players": [],           # list of dicts
        "bets": [],              # list of dicts
        "blind_levels": get_default_blinds(),
        "current_level": 0,
        "timer_running": False,
        "timer_start": None,
        "elapsed_seconds": 0,
        "level_duration": 15,    # minutes per level
        "tournament_started": False,
        "tournament_name": "LV POKER ROOM",
        "buy_in": 50,
        "starting_chips": 10000,
        "rebuy_allowed": True,
        "rebuy_chips": 5000,
        "rebuy_cost": 30,
        "alerts": [],
        "hand_count": 0,
        "last_tick": time.time(),
        "sound_alerts": True,
        "break_active": False,
        "break_duration": 10,
        "break_elapsed": 0,
        "break_start": None,
        "player_id_counter": 1,
        "sound_muted": False,
        "tournament_start_time": None,
        "total_elapsed_seconds": 0,
        "play_sound": None,   # "warning" | "critical" | "level_up" | None
        "prize_percentages": get_default_prize_percentages(),
        "prize_pool_pct": 85,
        # ── Wall-clock timer
        "timer_wall_start": None,
        "elapsed_at_start": 0,
        "break_wall_start": None,
        "break_elapsed_at_start": 0,
        "total_at_start": 0,
        # ── Add-ons
        "addon_allowed": False,
        "addon_chips": 5000,
        "addon_cost": 30,
        "addon_level_limit": 6,
        "addon_period_active": True,
        # ── Player database
        "player_db": {},
        # ── Display ticker
        "display_ticker": "",
        "display_ticker_enabled": False,
        # ── Rotating views
        "display_views": ["timer", "blinds", "prizes"],
        "display_view_interval": 15,
        # ── Blind templates
        "blind_templates": {},
        # ── Tables
        "tables": [],
        "table_size": 9,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_default_prize_percentages():
    """
    Prize percentages based on EPL Main Event payout table.
    Key = max number of players in the range (inclusive).
    Ranges: 7-32, 33-40, 41-48, 49-56, 57-64, 65-72, 73-80, 81-88, 89-96, 97-104
    For fewer than 7 players we use simplified structures.
    """
    return {
        # Simplified small tables (< 7 players)
        "2":  [{"place": 1, "pct": 70.0}, {"place": 2, "pct": 30.0}],
        "4":  [
            {"place": 1, "pct": 60.0}, {"place": 2, "pct": 30.0},
            {"place": 3, "pct": 10.0},
        ],
        "6":  [
            {"place": 1, "pct": 50.0}, {"place": 2, "pct": 30.0},
            {"place": 3, "pct": 20.0},
        ],
        # EPL table — 7 to 32 players (4 paid)
        "32": [
            {"place": 1, "pct": 45.0},
            {"place": 2, "pct": 27.0},
            {"place": 3, "pct": 17.0},
            {"place": 4, "pct": 11.0},
        ],
        # 33-40 players (5 paid)
        "40": [
            {"place": 1, "pct": 41.0},
            {"place": 2, "pct": 25.0},
            {"place": 3, "pct": 15.0},
            {"place": 4, "pct": 11.0},
            {"place": 5, "pct": 8.0},
        ],
        # 41-48 players (6 paid)
        "48": [
            {"place": 1, "pct": 39.0},
            {"place": 2, "pct": 23.0},
            {"place": 3, "pct": 14.0},
            {"place": 4, "pct": 10.0},
            {"place": 5, "pct": 8.0},
            {"place": 6, "pct": 6.0},
        ],
        # 49-56 players (7 paid)
        "56": [
            {"place": 1, "pct": 37.0},
            {"place": 2, "pct": 22.0},
            {"place": 3, "pct": 13.5},
            {"place": 4, "pct": 9.5},
            {"place": 5, "pct": 7.5},
            {"place": 6, "pct": 6.0},
            {"place": 7, "pct": 4.5},
        ],
        # 57-64 players (8 paid)
        "64": [
            {"place": 1, "pct": 36.0},
            {"place": 2, "pct": 21.15},
            {"place": 3, "pct": 13.25},
            {"place": 4, "pct": 9.0},
            {"place": 5, "pct": 7.0},
            {"place": 6, "pct": 5.5},
            {"place": 7, "pct": 4.5},
            {"place": 8, "pct": 3.6},
        ],
        # 65-72 players (9 paid)
        "72": [
            {"place": 1, "pct": 35.0},
            {"place": 2, "pct": 20.0},
            {"place": 3, "pct": 12.25},
            {"place": 4, "pct": 8.75},
            {"place": 5, "pct": 6.75},
            {"place": 6, "pct": 5.25},
            {"place": 7, "pct": 4.5},
            {"place": 8, "pct": 4.0},
            {"place": 9, "pct": 3.5},
        ],
        # 73-80 players (10 paid)
        "80": [
            {"place": 1,  "pct": 34.0},
            {"place": 2,  "pct": 19.5},
            {"place": 3,  "pct": 12.2},
            {"place": 4,  "pct": 8.25},
            {"place": 5,  "pct": 6.25},
            {"place": 6,  "pct": 5.0},
            {"place": 7,  "pct": 4.4},
            {"place": 8,  "pct": 4.0},
            {"place": 9,  "pct": 3.4},
            {"place": 10, "pct": 3.0},
        ],
        # 81-88 players (11 paid)
        "88": [
            {"place": 1,  "pct": 32.25},
            {"place": 2,  "pct": 19.5},
            {"place": 3,  "pct": 12.125},
            {"place": 4,  "pct": 8.2},
            {"place": 5,  "pct": 6.25},
            {"place": 6,  "pct": 5.0},
            {"place": 7,  "pct": 4.15},
            {"place": 8,  "pct": 3.5},
            {"place": 9,  "pct": 3.225},
            {"place": 10, "pct": 3.0},
            {"place": 11, "pct": 2.8},
        ],
        # 89-96 players (12 paid)
        "96": [
            {"place": 1,  "pct": 31.725},
            {"place": 2,  "pct": 19.0},
            {"place": 3,  "pct": 12.0},
            {"place": 4,  "pct": 7.75},
            {"place": 5,  "pct": 6.0},
            {"place": 6,  "pct": 4.75},
            {"place": 7,  "pct": 4.0},
            {"place": 8,  "pct": 3.5},
            {"place": 9,  "pct": 3.173},
            {"place": 10, "pct": 2.9},
            {"place": 11, "pct": 2.7},
            {"place": 12, "pct": 2.502},
        ],
        # 97-104 players (13 paid)
        "104": [
            {"place": 1,  "pct": 30.5},
            {"place": 2,  "pct": 18.75},
            {"place": 3,  "pct": 11.5},
            {"place": 4,  "pct": 7.5},
            {"place": 5,  "pct": 5.85},
            {"place": 6,  "pct": 4.675},
            {"place": 7,  "pct": 3.975},
            {"place": 8,  "pct": 3.45},
            {"place": 9,  "pct": 3.05},
            {"place": 10, "pct": 2.75},
            {"place": 11, "pct": 2.75},
            {"place": 12, "pct": 2.75},
            {"place": 13, "pct": 2.5},
        ],
    }

def get_default_blinds():
    """Estructura EPL: 29 niveles de 40 min, BB Ante = Big Blind."""
    return [
        {"level":  1, "small": 100,     "big": 200,     "ante": 200,     "duration": 40},
        {"level":  2, "small": 200,     "big": 300,     "ante": 300,     "duration": 40},
        {"level":  3, "small": 200,     "big": 400,     "ante": 400,     "duration": 40},
        {"level":  4, "small": 300,     "big": 500,     "ante": 500,     "duration": 40},
        {"level":  5, "small": 300,     "big": 600,     "ante": 600,     "duration": 40},
        {"level":  6, "small": 400,     "big": 800,     "ante": 800,     "duration": 40},
        {"level":  7, "small": 500,     "big": 1000,    "ante": 1000,    "duration": 40},
        {"level":  8, "small": 600,     "big": 1200,    "ante": 1200,    "duration": 40},
        {"level":  9, "small": 1000,    "big": 1500,    "ante": 1500,    "duration": 40},
        {"level": 10, "small": 1000,    "big": 2000,    "ante": 2000,    "duration": 40},
        {"level": 11, "small": 1500,    "big": 2500,    "ante": 2500,    "duration": 40},
        {"level": 12, "small": 1500,    "big": 3000,    "ante": 3000,    "duration": 40},
        {"level": 13, "small": 2000,    "big": 4000,    "ante": 4000,    "duration": 40},
        {"level": 14, "small": 3000,    "big": 5000,    "ante": 5000,    "duration": 40},
        {"level": 15, "small": 3000,    "big": 6000,    "ante": 6000,    "duration": 40},
        {"level": 16, "small": 4000,    "big": 8000,    "ante": 8000,    "duration": 40},
        {"level": 17, "small": 5000,    "big": 10000,   "ante": 10000,   "duration": 40},
        {"level": 18, "small": 6000,    "big": 12000,   "ante": 12000,   "duration": 40},
        {"level": 19, "small": 10000,   "big": 15000,   "ante": 15000,   "duration": 40},
        {"level": 20, "small": 10000,   "big": 20000,   "ante": 20000,   "duration": 40},
        {"level": 21, "small": 15000,   "big": 25000,   "ante": 25000,   "duration": 40},
        {"level": 22, "small": 15000,   "big": 30000,   "ante": 30000,   "duration": 40},
        {"level": 23, "small": 20000,   "big": 40000,   "ante": 40000,   "duration": 40},
        {"level": 24, "small": 25000,   "big": 50000,   "ante": 50000,   "duration": 40},
        {"level": 25, "small": 30000,   "big": 60000,   "ante": 60000,   "duration": 40},
        {"level": 26, "small": 40000,   "big": 80000,   "ante": 80000,   "duration": 40},
        {"level": 27, "small": 50000,   "big": 100000,  "ante": 100000,  "duration": 40},
        {"level": 28, "small": 60000,   "big": 100000,  "ante": 100000,  "duration": 40},
        {"level": 29, "small": 100000,  "big": 150000,  "ante": 150000,  "duration": 40},
    ]

def get_epl_breaks():
    """Breaks de la estructura EPL: después de niveles 6, 12, 18 y 24."""
    return {6: 15, 12: 15, 18: 45, 24: 15}  # nivel: duración en minutos

init_state()

# ─── LOGIN ─────────────────────────────────────────────────────────────────────
_PASSWORD = "torneo123"

if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if not st.session_state["autenticado"]:
    st.markdown("""
    <div style="max-width:420px; margin:80px auto; text-align:center;">
        <div style="background:linear-gradient(135deg,#0d1f14,#0a0a0a);
                    border:2px solid #d4af37; border-radius:16px; padding:2.5rem 2rem;
                    box-shadow:0 0 40px rgba(212,175,55,0.2);">
            <div style="font-family:'Bebas Neue',cursive; font-size:3rem; letter-spacing:8px;
                        color:#d4af37; text-shadow:0 0 20px rgba(212,175,55,0.4); margin-bottom:0.3rem;">
                ♠ POKER MGR ♠
            </div>
            <div style="font-family:'Rajdhani',sans-serif; color:#9ca3af; font-size:1rem;
                        letter-spacing:3px; margin-bottom:1.5rem;">ACCESO AL SISTEMA</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    col = st.columns([1, 2, 1])[1]
    with col:
        pwd = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresá la contraseña")
        if st.button("INGRESAR", use_container_width=True, type="primary"):
            if pwd == _PASSWORD:
                st.session_state["autenticado"] = True
                st.rerun()
            else:
                st.error("❌ Contraseña incorrecta.")
    st.stop()

# ─── PERSISTENCIA ──────────────────────────────────────────────────────────────
SAVE_FILE = "torneo_data.json"

PERSIST_KEYS = [
    "players", "bets", "blind_levels", "current_level", "elapsed_seconds",
    "level_duration", "tournament_started", "tournament_name", "buy_in",
    "starting_chips", "rebuy_allowed", "rebuy_chips", "rebuy_cost",
    "alerts", "hand_count", "break_active", "break_duration", "break_elapsed",
    "player_id_counter", "sound_muted", "tournament_start_time",
    "total_elapsed_seconds", "prize_percentages", "prize_pool_pct",
    "timer_running", "timer_wall_start", "elapsed_at_start",
    "break_wall_start", "break_elapsed_at_start", "total_at_start",
    "addon_allowed", "addon_chips", "addon_cost", "addon_level_limit", "addon_period_active",
    "player_db", "display_ticker", "display_ticker_enabled",
    "display_views", "display_view_interval",
    "blind_templates", "tables", "table_size",
]

def save_state():
    data = {k: st.session_state[k] for k in PERSIST_KEYS if k in st.session_state}
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_state():
    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in data.items():
            st.session_state[k] = v
        st.session_state.last_tick = time.time()
        # timer_running se restaura del archivo, no se resetea
    except Exception:
        pass

def reset_tournament():
    for k in PERSIST_KEYS:
        if k in st.session_state:
            del st.session_state[k]
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)
    init_state()

if "state_loaded" not in st.session_state:
    load_state()
    st.session_state.state_loaded = True

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def get_active_players():
    return [p for p in st.session_state.players if p["status"] == "active"]

def get_eliminated_players():
    return [p for p in st.session_state.players if p["status"] == "eliminated"]

def total_prize_pool():
    total = sum(p.get("paid_amount", st.session_state.buy_in) for p in st.session_state.players)
    total += sum(sum(r["amount"] for r in p.get("rebuy_history", [])) for p in st.session_state.players)
    return total

def effective_prize_pool():
    """Prize pool real después de aplicar el porcentaje configurado."""
    pct = st.session_state.get("prize_pool_pct", 85)
    return int(total_prize_pool() * pct / 100)

def calculate_payouts(prize_pool, n_players):
    if n_players <= 0:
        return []
    if n_players == 1:
        return [{"place": 1, "pct": 100, "amount": prize_pool}]
    structure = []
    if n_players >= 2:
        structure = [
            {"place": 1, "pct": 50},
            {"place": 2, "pct": 30},
        ]
        if n_players >= 5:
            structure.append({"place": 3, "pct": 15})
            structure[0]["pct"] = 50
            structure[1]["pct": structure[1].update({"pct": 30}) or 30]
        if n_players >= 9:
            structure.append({"place": 4, "pct": 8})
            structure.append({"place": 5, "pct": 5})
    for s in structure:
        s["amount"] = int(prize_pool * s["pct"] / 100)
    return structure

def calculate_payouts_fixed(prize_pool, n_players):
    if n_players <= 0:
        return []
    if n_players == 1:
        return [{"place": 1, "pct": 100, "amount": prize_pool}]

    # Find the right bracket from configured percentages
    brackets = st.session_state.get("prize_percentages", get_default_prize_percentages())
    structure = None
    for key in sorted(brackets.keys(), key=lambda x: int(x)):
        if n_players <= int(key):
            structure = brackets[key]
            break
    if structure is None:
        # fallback: use the last bracket
        last_key = sorted(brackets.keys(), key=lambda x: int(x))[-1]
        structure = brackets[last_key]

    result = []
    for s in structure:
        result.append({
            "place": s["place"],
            "pct": s["pct"],
            "amount": int(prize_pool * s["pct"] / 100),
        })
    return result

def current_blind():
    idx = min(st.session_state.current_level, len(st.session_state.blind_levels) - 1)
    return st.session_state.blind_levels[idx]

def next_blind():
    idx = st.session_state.current_level + 1
    if idx < len(st.session_state.blind_levels):
        return st.session_state.blind_levels[idx]
    return None

def level_seconds():
    b = current_blind()
    dur = b.get("duration", st.session_state.level_duration)
    return dur * 60

def time_remaining():
    total = level_seconds()
    return max(0, total - st.session_state.elapsed_seconds)

def fmt_time(secs):
    m = int(secs) // 60
    s = int(secs) % 60
    return f"{m:02d}:{s:02d}"

def avg_stack():
    active = get_active_players()
    if not active:
        return 0
    total = sum(p["chips"] for p in active)
    return total // len(active)

def chip_leader():
    active = get_active_players()
    if not active:
        return None
    return max(active, key=lambda p: p["chips"])

def m_ratio(chips):
    b = current_blind()
    cost = b["small"] + b["big"] + b["ante"]
    if cost == 0:
        return 999
    return chips / cost

def tournament_total_time():
    """Returns total seconds since tournament started (pauses excluded)."""
    return st.session_state.get("total_elapsed_seconds", 0)

def add_alert(msg, kind="info"):
    st.session_state.alerts.append({
        "time": datetime.now().strftime("%H:%M:%S"),
        "msg": msg,
        "kind": kind
    })
    if len(st.session_state.alerts) > 20:
        st.session_state.alerts = st.session_state.alerts[-20:]

def tick_timer():
    """Timer basado en wall-clock — preciso sin importar el intervalo entre reruns."""
    st.session_state.play_sound = None
    now = time.time()

    if st.session_state.timer_running and not st.session_state.break_active:
        wall_start = st.session_state.get("timer_wall_start")
        base_elapsed = st.session_state.get("elapsed_at_start", 0)
        if wall_start is not None:
            st.session_state.elapsed_seconds = base_elapsed + (now - wall_start)
            total_base = st.session_state.get("total_at_start", 0)
            st.session_state.total_elapsed_seconds = total_base + (now - wall_start)
        remaining = time_remaining()
        if remaining <= 0:
            st.session_state.play_sound = "level_up"
            advance_level(auto=True)
        elif remaining <= 30 and remaining > 29:
            add_alert(f"🚨 30 segundos para cambio de ciegas!", "critical")
            st.session_state.play_sound = "critical"
        elif remaining <= 60 and remaining > 59:
            add_alert(f"⚠️ 1 minuto para cambio de ciegas — Nivel {st.session_state.current_level + 1}", "warning")
            st.session_state.play_sound = "warning"

    if st.session_state.break_active:
        break_wall = st.session_state.get("break_wall_start")
        break_base = st.session_state.get("break_elapsed_at_start", 0)
        if break_wall is not None:
            st.session_state.break_elapsed = break_base + (now - break_wall)
        break_remaining = st.session_state.break_duration * 60 - st.session_state.break_elapsed
        if break_remaining <= 0:
            st.session_state.break_active = False
            st.session_state.break_wall_start = None
            st.session_state.timer_running = True
            st.session_state.timer_wall_start = now
            st.session_state.elapsed_at_start = st.session_state.elapsed_seconds
            st.session_state.total_at_start = st.session_state.get("total_elapsed_seconds", 0)
            st.session_state.play_sound = "warning"
            add_alert("▶️ Descanso terminado — Continúa el juego!", "info")
            save_state()

def advance_level(auto=False):
    if st.session_state.current_level < len(st.session_state.blind_levels) - 1:
        st.session_state.current_level += 1
        st.session_state.elapsed_seconds = 0
        now = time.time()
        st.session_state.last_tick = now
        if st.session_state.timer_running:
            st.session_state.timer_wall_start = now
            st.session_state.elapsed_at_start = 0
            st.session_state.total_at_start = st.session_state.get("total_elapsed_seconds", 0)
        # Cerrar add-on period si superamos el nivel límite
        if st.session_state.current_level + 1 > st.session_state.get("addon_level_limit", 6):
            st.session_state.addon_period_active = False
        b = current_blind()
        add_alert(
            f"{'🔄 AUTO: ' if auto else ''}Nivel {b['level']} — SB: {b['small']:,} | BB: {b['big']:,} | Ante: {b['ante']:,}",
            "level_up"
        )
    else:
        add_alert("🏆 Último nivel de ciegas alcanzado!", "critical")

# ─── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding:1rem 0; border-bottom: 1px solid #1a3a24; margin-bottom:1rem;">
        <span style="font-family:'Bebas Neue',cursive; font-size:1.8rem; color:#d4af37; letter-spacing:4px;">♠ POKER MGR</span>
    </div>
    """, unsafe_allow_html=True)

    nav = st.radio(
        "NAVEGACIÓN",
        ["🕐 Torneo en Vivo", "👥 Jugadores", "💰 Apuestas", "🏆 Premios",
         "🪑 Mesas", "📊 Estadísticas", "⚙️ Configuración", "📋 Historial"],
        label_visibility="collapsed"
    )

    st.divider()
    if st.button("🔓 Cerrar sesión", use_container_width=True):
        st.session_state["autenticado"] = False
        st.rerun()

    # Quick stats
    active = get_active_players()
    total_players = len(st.session_state.players)
    pool = effective_prize_pool()

    st.markdown(f"""
    <div style="font-family:'Rajdhani',sans-serif; font-size:0.8rem; color:#9ca3af; letter-spacing:2px; margin-bottom:0.5rem;">ESTADO DEL TORNEO</div>
    <div style="background:#1a2a1e; border:1px solid #1a3a24; border-radius:8px; padding:0.8rem;">
        <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
            <span style="color:#9ca3af; font-size:0.85rem;">Jugadores activos</span>
            <span style="color:#22c55e; font-family:'Share Tech Mono',monospace; font-size:0.95rem;">{len(active)}/{total_players}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
            <span style="color:#9ca3af; font-size:0.85rem;">Prize Pool</span>
            <span style="color:#d4af37; font-family:'Share Tech Mono',monospace; font-size:0.95rem;">${pool:,}</span>
        </div>
        <div style="display:flex; justify-content:space-between; margin-bottom:0.3rem;">
            <span style="color:#9ca3af; font-size:0.85rem;">Nivel actual</span>
            <span style="color:#f0d060; font-family:'Share Tech Mono',monospace; font-size:0.95rem;">{st.session_state.current_level + 1}</span>
        </div>
        <div style="display:flex; justify-content:space-between;">
            <span style="color:#9ca3af; font-size:0.85rem;">Stack promedio</span>
            <span style="color:#60a5fa; font-family:'Share Tech Mono',monospace; font-size:0.95rem;">{avg_stack():,}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    if st.button("🔄 Sincronizar ahora", use_container_width=True):
        load_state()
        st.rerun()

    # Sound control
    st.divider()
    mute_label = "🔇 Sonido: OFF" if st.session_state.sound_muted else "🔔 Sonido: ON"
    if st.button(mute_label, use_container_width=True):
        st.session_state.sound_muted = not st.session_state.sound_muted
        save_state()
        st.rerun()

    # Total tournament time
    total_secs_played = int(st.session_state.get("total_elapsed_seconds", 0))
    th = total_secs_played // 3600
    tm = (total_secs_played % 3600) // 60
    ts = total_secs_played % 60
    st.markdown(f"""
    <div style="text-align:center; padding:0.5rem 0; font-family:'Share Tech Mono',monospace;
                font-size:0.85rem; color:#9ca3af; letter-spacing:1px;">
        ⏱ Tiempo total: {th:02d}:{tm:02d}:{ts:02d}
    </div>
    """, unsafe_allow_html=True)

# ─── MAIN HEADER ───────────────────────────────────────────────────────────────
import base64, os

_logo_path = "poker.png"
_logo_b64 = ""
if os.path.exists(_logo_path):
    with open(_logo_path, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()

if _logo_b64:
    st.markdown(f"""
    <div style="text-align:center; padding:0.8rem 0 0.4rem; border-bottom:2px solid #d4af37; margin-bottom:1.5rem;">
        <img src="data:image/png;base64,{_logo_b64}"
             style="max-height:220px; max-width:100%; object-fit:contain;
                    filter:drop-shadow(0 0 18px rgba(212,175,55,0.5));" />
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown(f"""
    <div class="poker-header">
        <h1>♠ {st.session_state.tournament_name} ♠</h1>
        <p><span class="suit-s">♠</span> <span class="suit-h">♥</span> POKER TOURNAMENT MANAGER <span class="suit-d">♦</span> <span class="suit-c">♣</span></p>
    </div>
    """, unsafe_allow_html=True)

# ─── TICK TIMER ────────────────────────────────────────────────────────────────
tick_timer()

# ─── AUDIO ENGINE ──────────────────────────────────────────────────────────────
def play_sound_js(sound_type: str, muted: bool):
    """Inject Web Audio API JS to play a loud siren/alarm in the browser."""
    if muted or not sound_type:
        return

    scripts = {
        # ── WARNING (1 min): sirena corta ascendente/descendente x2 ──
        "warning": """
        (function() {
            var ctx = new (window.AudioContext || window.webkitAudioContext)();

            // Compresor para maximizar volumen sin distorsión
            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -6;
            comp.knee.value = 3;
            comp.ratio.value = 20;
            comp.attack.value = 0.001;
            comp.release.value = 0.1;
            comp.connect(ctx.destination);

            // Ganancia maestra
            var master = ctx.createGain();
            master.gain.value = 2.5;
            master.connect(comp);

            function siren(startTime, duration) {
                var osc1 = ctx.createOscillator();
                var osc2 = ctx.createOscillator();
                var g = ctx.createGain();

                osc1.type = 'sawtooth';
                osc2.type = 'square';
                osc1.connect(g); osc2.connect(g); g.connect(master);

                // Barrido de frecuencia tipo sirena policial
                osc1.frequency.setValueAtTime(600, startTime);
                osc1.frequency.linearRampToValueAtTime(1200, startTime + duration * 0.5);
                osc1.frequency.linearRampToValueAtTime(600, startTime + duration);

                osc2.frequency.setValueAtTime(590, startTime);
                osc2.frequency.linearRampToValueAtTime(1190, startTime + duration * 0.5);
                osc2.frequency.linearRampToValueAtTime(590, startTime + duration);

                g.gain.setValueAtTime(0, startTime);
                g.gain.linearRampToValueAtTime(0.8, startTime + 0.05);
                g.gain.setValueAtTime(0.8, startTime + duration - 0.05);
                g.gain.linearRampToValueAtTime(0, startTime + duration);

                osc1.start(startTime); osc1.stop(startTime + duration);
                osc2.start(startTime); osc2.stop(startTime + duration);
            }

            var t = ctx.currentTime;
            siren(t,       0.6);
            siren(t + 0.7, 0.6);
        })();
        """,

        # ── CRITICAL (30 seg): sirena de emergencia agresiva x3 ──
        "critical": """
        (function() {
            var ctx = new (window.AudioContext || window.webkitAudioContext)();

            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -3;
            comp.knee.value = 1;
            comp.ratio.value = 20;
            comp.attack.value = 0.001;
            comp.release.value = 0.05;
            comp.connect(ctx.destination);

            var master = ctx.createGain();
            master.gain.value = 3.0;
            master.connect(comp);

            function alarm(startTime, duration) {
                var osc1 = ctx.createOscillator();
                var osc2 = ctx.createOscillator();
                var osc3 = ctx.createOscillator();
                var g = ctx.createGain();

                osc1.type = 'sawtooth';
                osc2.type = 'square';
                osc3.type = 'sawtooth';

                osc1.connect(g); osc2.connect(g); osc3.connect(g);
                g.connect(master);

                // Dos tonos alternados estilo alarma de emergencia
                osc1.frequency.setValueAtTime(900, startTime);
                osc1.frequency.linearRampToValueAtTime(1800, startTime + duration * 0.3);
                osc1.frequency.linearRampToValueAtTime(900, startTime + duration * 0.6);
                osc1.frequency.linearRampToValueAtTime(1800, startTime + duration);

                osc2.frequency.setValueAtTime(880, startTime);
                osc2.frequency.linearRampToValueAtTime(1760, startTime + duration * 0.3);
                osc2.frequency.linearRampToValueAtTime(880, startTime + duration * 0.6);
                osc2.frequency.linearRampToValueAtTime(1760, startTime + duration);

                // Sub-tono grave para cuerpo
                osc3.frequency.setValueAtTime(110, startTime);
                osc3.frequency.linearRampToValueAtTime(220, startTime + duration * 0.5);
                osc3.frequency.linearRampToValueAtTime(110, startTime + duration);

                g.gain.setValueAtTime(0, startTime);
                g.gain.linearRampToValueAtTime(0.9, startTime + 0.03);
                g.gain.setValueAtTime(0.9, startTime + duration - 0.03);
                g.gain.linearRampToValueAtTime(0, startTime + duration);

                osc1.start(startTime); osc1.stop(startTime + duration);
                osc2.start(startTime); osc2.stop(startTime + duration);
                osc3.start(startTime); osc3.stop(startTime + duration);
            }

            var t = ctx.currentTime;
            alarm(t,        0.45);
            alarm(t + 0.5,  0.45);
            alarm(t + 1.0,  0.45);
        })();
        """,

        # ── LEVEL UP: fanfarria triunfal potente ──
        "level_up": """
        (function() {
            var ctx = new (window.AudioContext || window.webkitAudioContext)();

            var comp = ctx.createDynamicsCompressor();
            comp.threshold.value = -6;
            comp.ratio.value = 12;
            comp.connect(ctx.destination);

            var master = ctx.createGain();
            master.gain.value = 2.5;
            master.connect(comp);

            function note(freq, start, dur) {
                var osc1 = ctx.createOscillator();
                var osc2 = ctx.createOscillator();
                var g = ctx.createGain();

                osc1.type = 'sawtooth'; osc1.frequency.value = freq;
                osc2.type = 'sine';     osc2.frequency.value = freq * 2;

                osc1.connect(g); osc2.connect(g); g.connect(master);

                g.gain.setValueAtTime(0, ctx.currentTime + start);
                g.gain.linearRampToValueAtTime(0.7, ctx.currentTime + start + 0.02);
                g.gain.setValueAtTime(0.7, ctx.currentTime + start + dur - 0.05);
                g.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + start + dur);

                osc1.start(ctx.currentTime + start); osc1.stop(ctx.currentTime + start + dur);
                osc2.start(ctx.currentTime + start); osc2.stop(ctx.currentTime + start + dur);
            }

            // Do-Mi-Sol-Do triunfal
            note(523,  0.0,  0.22);
            note(659,  0.22, 0.22);
            note(784,  0.44, 0.22);
            note(1047, 0.66, 0.50);
        })();
        """,
        # ── REBUY: reproduce fichas.mp3 embebido en base64 ──
        "rebuy": "__REBUY_PLACEHOLDER__",
    }

    # Cargar fichas.mp3 como base64 para el rebuy
    if sound_type == "rebuy":
        import base64, pathlib
        mp3_paths = [
            pathlib.Path("fichas.mp3"),
            pathlib.Path(__file__).parent / "fichas.mp3",
        ]
        mp3_b64 = None
        for p in mp3_paths:
            if p.exists():
                mp3_b64 = base64.b64encode(p.read_bytes()).decode()
                break
        if mp3_b64:
            js_code = f"""
            (function() {{
                var audio = new Audio('data:audio/mpeg;base64,{mp3_b64}');
                audio.volume = 1.0;
                audio.play().catch(function(e) {{ console.warn('fichas error:', e); }});
            }})();
            """
        else:
            js_code = ""
    else:
        js_code = scripts.get(sound_type, "")

    if js_code:
        import streamlit.components.v1 as components
        components.html(f"<script>{js_code}</script>", height=0)

# Fire sound if triggered this tick
play_sound_js(
    st.session_state.get("play_sound"),
    st.session_state.get("sound_muted", False)
)

# Fire rebuy sound — uses separate flag so tick_timer() never clears it
if st.session_state.get("play_rebuy_sound", False) and not st.session_state.get("sound_muted", False):
    st.session_state.play_rebuy_sound = False  # consume flag immediately
    import base64 as _b64, pathlib as _pl
    _mp3_b64 = None
    for _p in [_pl.Path("fichas.mp3"), _pl.Path(__file__).parent / "fichas.mp3"]:
        if _p.exists():
            _mp3_b64 = _b64.b64encode(_p.read_bytes()).decode()
            break
    if _mp3_b64:
        import streamlit.components.v1 as _components
        _components.html(
            f"<script>(function(){{var a=new Audio('data:audio/mpeg;base64,{_mp3_b64}');a.volume=1.0;a.play().catch(function(e){{console.warn(e);}});}})();</script>",
            height=0
        )

# ════════════════════════════════════════════════════════════════════════════════
# TAB: TORNEO EN VIVO
# ════════════════════════════════════════════════════════════════════════════════
if nav == "🕐 Torneo en Vivo":
    remaining = time_remaining()
    total_secs = level_seconds()
    progress = 1.0 - (remaining / total_secs) if total_secs > 0 else 0

    # ── ALERT BANNERS ──────────────────────────────────────────────────────────
    if remaining <= 30 and st.session_state.timer_running and not st.session_state.break_active:
        st.markdown('<div class="alert-banner">🚨 ¡CAMBIO DE CIEGAS EN MENOS DE 30 SEGUNDOS! 🚨</div>', unsafe_allow_html=True)
    elif remaining <= 60 and st.session_state.timer_running and not st.session_state.break_active:
        st.markdown('<div class="alert-banner" style="background: linear-gradient(90deg,#92400e,#f59e0b,#92400e);">⚠️ ÚLTIMO MINUTO — CAMBIO DE CIEGAS PRÓXIMO ⚠️</div>', unsafe_allow_html=True)

    if st.session_state.break_active:
        break_rem = st.session_state.break_duration * 60 - st.session_state.break_elapsed
        st.markdown(f'<div class="info-banner">☕ DESCANSO EN CURSO — {fmt_time(max(0, break_rem))} restantes</div>', unsafe_allow_html=True)

    b  = current_blind()
    nb = next_blind()
    active_p   = get_active_players()
    n_active   = len(active_p)
    n_total    = len(st.session_state.players)
    eliminated = n_total - n_active
    total_rebuys_live = sum(p.get("rebuys", 0) for p in st.session_state.players)
    eliminated_display = eliminated + total_rebuys_live

    # ── TIMER CLASS ────────────────────────────────────────────────────────────
    timer_class = "timer-display"
    if remaining <= 30 and st.session_state.timer_running:
        timer_class += " timer-critical"
    elif remaining <= 60 and st.session_state.timer_running:
        timer_class += " timer-warning"

    # ── ROW 1: NIVEL  |  TIMER  |  PRÓXIMAS CIEGAS ────────────────────────────
    col_lvl, col_timer, col_next = st.columns([1, 2, 1])

    with col_lvl:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);
                    border:1px solid #d4af37; border-radius:16px;
                    padding:1.5rem 1rem; text-align:center; height:100%;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.5rem;
                        letter-spacing:4px; color:#b0b8c8; margin-bottom:0.4rem; font-weight:700;">NIVEL</div>
            <div style="font-family:'Bebas Neue',cursive; font-size:5rem;
                        color:#d4af37; line-height:1;
                        text-shadow:0 0 30px rgba(212,175,55,0.5);">{b['level']}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.6rem;
                        color:#b0b8c8; letter-spacing:2px; margin-top:0.3rem;">
                DE {len(st.session_state.blind_levels)}
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_timer:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);
                    border:2px solid #d4af37; border-radius:16px;
                    padding:1.2rem 1rem 0.8rem; text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.5rem;
                        letter-spacing:4px; color:#b0b8c8; margin-bottom:0.2rem; font-weight:700;">TIEMPO RESTANTE</div>
            <div class="{timer_class}" style="font-size:7rem;">{fmt_time(remaining)}</div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(progress)

    with col_next:
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);
                    border:1px solid #374151; border-radius:16px;
                    padding:1.5rem 1rem; text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.5rem;
                        letter-spacing:4px; color:#b0b8c8; margin-bottom:0.6rem; font-weight:700;">JUGADORES</div>
            <div style="font-family:'Bebas Neue',cursive; font-size:4rem;
                        color:#22c55e; line-height:1;">{n_active}</div>
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.6rem;
                        color:#b0b8c8; letter-spacing:2px;">{eliminated_display} eliminados</div>
        </div>
        """, unsafe_allow_html=True)
        if nb:
            st.markdown(f"""
            <div style="margin-top:0.6rem; padding:0.6rem 0.8rem;
                        background:rgba(37,99,235,0.08); border:1px dashed #2563eb;
                        border-radius:10px; text-align:center;">
                <div style="font-family:'Rajdhani',sans-serif; font-size:1.44rem;
                            letter-spacing:2px; color:#b0b8c8; margin-bottom:0.3rem; font-weight:700;">PRÓXIMO NIVEL</div>
                <div style="font-family:'Share Tech Mono',monospace; color:#93c5fd; font-size:2rem; line-height:1.6;">
                    {nb['small']:,} / {nb['big']:,}<br>
                    <span style="font-size:1.7rem; color:#d1d5db;">Ante: {nb['ante']:,}</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # ── ROW 2: CIEGAS ACTUALES ─────────────────────────────────────────────────
    st.markdown("<div style='height:1rem;'></div>", unsafe_allow_html=True)

    col_sb, col_bb, col_ante, col_pool, col_avg = st.columns(5)

    def big_stat(label, value, color="#d4af37", sub=""):
        return f"""
        <div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);
                    border:1px solid #1f2937; border-radius:14px;
                    padding:1.2rem 0.8rem; text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif; font-size:1.5rem;
                        letter-spacing:3px; color:#b0b8c8; margin-bottom:0.3rem; font-weight:700;">{label}</div>
            <div style="font-family:'Share Tech Mono',monospace; font-size:2.8rem;
                        color:{color}; line-height:1;
                        text-shadow:0 0 20px {color}55;">{value}</div>
            {"" if not sub else f'<div style="font-size:1.5rem;color:#b0b8c8;margin-top:0.3rem;">{sub}</div>'}
        </div>
        """

    with col_sb:
        st.markdown(big_stat("SMALL BLIND", f"{b['small']:,}"), unsafe_allow_html=True)
    with col_bb:
        st.markdown(big_stat("BIG BLIND", f"{b['big']:,}", color="#f0d060"), unsafe_allow_html=True)
    with col_ante:
        ante_val = f"{b['ante']:,}" if b['ante'] > 0 else "—"
        st.markdown(big_stat("ANTE", ante_val, color="#f87171"), unsafe_allow_html=True)
    with col_pool:
        st.markdown(big_stat("PRIZE POOL", f"${effective_prize_pool():,}", color="#34d399"), unsafe_allow_html=True)
    with col_avg:
        st.markdown(big_stat("STACK PROM.", f"{avg_stack():,}", color="#a78bfa"), unsafe_allow_html=True)

    # ── ROW 3: CONTROLES ──────────────────────────────────────────────────────
    st.markdown("<div style='height:0.5rem;'></div>", unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.session_state.timer_running and not st.session_state.break_active:
            if st.button("⏸  Pausa", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_wall_start = None
                add_alert("⏸ Torneo pausado")
                save_state()
                st.rerun()
        else:
            label = "▶  Reanudar" if st.session_state.tournament_started else "▶  Iniciar"
            if st.button(label, use_container_width=True):
                now_btn = time.time()
                st.session_state.timer_running = True
                st.session_state.tournament_started = True
                st.session_state.timer_wall_start = now_btn
                st.session_state.elapsed_at_start = st.session_state.elapsed_seconds
                st.session_state.total_at_start = st.session_state.get("total_elapsed_seconds", 0)
                st.session_state.last_tick = now_btn
                if not st.session_state.break_active:
                    add_alert("▶️ Torneo iniciado/reanudado")
                save_state()
                st.rerun()
    with c2:
        if st.button("⏭  Avanzar nivel", use_container_width=True):
            advance_level()
            if st.session_state.timer_running:
                now_btn = time.time()
                st.session_state.timer_wall_start = now_btn
                st.session_state.elapsed_at_start = 0
                st.session_state.total_at_start = st.session_state.get("total_elapsed_seconds", 0)
            save_state()
            st.rerun()
    with c3:
        if st.button("⏮  Retroceder", use_container_width=True):
            if st.session_state.current_level > 0:
                st.session_state.current_level -= 1
                st.session_state.elapsed_seconds = 0
                now_btn = time.time()
                st.session_state.last_tick = now_btn
                if st.session_state.timer_running:
                    st.session_state.timer_wall_start = now_btn
                    st.session_state.elapsed_at_start = 0
                    st.session_state.total_at_start = st.session_state.get("total_elapsed_seconds", 0)
                add_alert(f"⏮ Volviendo al nivel {st.session_state.current_level + 1}")
                save_state()
                st.rerun()
    with c4:
        if st.button("☕  Descanso", use_container_width=True):
            now_btn = time.time()
            st.session_state.break_active = True
            st.session_state.break_elapsed = 0
            st.session_state.break_elapsed_at_start = 0
            st.session_state.break_wall_start = now_btn
            st.session_state.timer_running = False
            st.session_state.timer_wall_start = None
            st.session_state.last_tick = now_btn
            add_alert(f"☕ Descanso de {st.session_state.break_duration} minutos iniciado")
            save_state()
            st.rerun()

    # ── ROW 4: TABLA DE NIVELES ────────────────────────────────────────────────
    import streamlit.components.v1 as components

    st.markdown('<div class="panel" style="margin-top:1rem;">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📋 ESTRUCTURA COMPLETA DE NIVELES</div>', unsafe_allow_html=True)

    rows_html = ""
    for i, bl in enumerate(st.session_state.blind_levels):
        is_current = (i == st.session_state.current_level)
        is_past    = (i < st.session_state.current_level)
        is_next    = (i == st.session_state.current_level + 1)
        dur        = bl.get("duration", st.session_state.level_duration)
        ante_str   = f"{bl['ante']:,}" if bl["ante"] > 0 else "—"

        if is_current:
            row_style  = "background:linear-gradient(90deg,rgba(212,175,55,0.18),rgba(212,175,55,0.06) 60%,transparent); border-left:4px solid #d4af37; opacity:1;"
            lvl_color  = "#d4af37"; num_color = "#f0d060"; ante_color = "#f0d060"; dur_color = "#d4af37"
            badge      = '<span style="background:#d4af37;color:#000;font-size:0.65rem;font-weight:900;letter-spacing:1px;padding:2px 8px;border-radius:10px;">▶ ACTUAL</span>'
        elif is_past:
            row_style  = "background:transparent; border-left:4px solid #1f2937; opacity:0.35;"
            lvl_color  = "#374151"; num_color = "#374151"; ante_color = "#374151"; dur_color = "#374151"
            badge      = '<span style="color:#22c55e;font-size:1rem;">✓</span>'
        elif is_next:
            row_style  = "background:linear-gradient(90deg,rgba(37,99,235,0.12),transparent); border-left:4px solid #2563eb; opacity:0.92;"
            lvl_color  = "#93c5fd"; num_color = "#bfdbfe"; ante_color = "#93c5fd"; dur_color = "#93c5fd"
            badge      = '<span style="color:#3b82f6;font-size:0.68rem;letter-spacing:1px;">PRÓXIMO</span>'
        else:
            row_style  = "background:transparent; border-left:4px solid transparent; opacity:0.55;"
            lvl_color  = "#6b7280"; num_color = "#9ca3af"; ante_color = "#6b7280"; dur_color = "#6b7280"
            badge      = ""

        rows_html += (
            f'<tr style="{row_style}">'
            f'<td style="padding:10px 10px;color:{lvl_color};font-family:Bebas Neue,cursive;font-size:1.3rem;letter-spacing:2px;text-align:center;width:55px;">{bl["level"]}</td>'
            f'<td style="padding:10px 10px;text-align:center;width:80px;">{badge}</td>'
            f'<td style="padding:10px 14px;font-family:Share Tech Mono,monospace;color:{num_color};font-size:1.1rem;text-align:right;">{bl["small"]:,}</td>'
            f'<td style="padding:10px 14px;font-family:Share Tech Mono,monospace;color:{num_color};font-size:1.1rem;text-align:right;font-weight:700;">{bl["big"]:,}</td>'
            f'<td style="padding:10px 14px;font-family:Share Tech Mono,monospace;color:{ante_color};font-size:1rem;text-align:right;">{ante_str}</td>'
            f'<td style="padding:10px 14px;font-family:Share Tech Mono,monospace;color:{dur_color};font-size:0.95rem;text-align:center;width:80px;">{dur} min</td>'
            f'</tr>'
        )

    full_html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Rajdhani:wght@600&display=swap" rel="stylesheet">
    <style>
        body {{ margin:0; padding:0; background:transparent; }}
        .wrap {{ overflow-y:auto; max-height:340px; border-radius:8px;
                 border:1px solid #1f2937; background:#0a0a0a;
                 scrollbar-width:thin; scrollbar-color:#374151 #0a0a0a; }}
        table {{ width:100%; border-collapse:collapse; }}
        thead tr {{ position:sticky; top:0; background:#111827;
                    border-bottom:2px solid rgba(212,175,55,0.3); }}
        th {{ padding:10px 14px; font-family:Rajdhani,sans-serif; font-size:1.64rem;
              letter-spacing:2px; color:#b0b8c8; text-transform:uppercase; font-weight:700; }}
        th:first-child {{ text-align:center; }}
        th:nth-child(3), th:nth-child(4), th:nth-child(5) {{ text-align:right; }}
        th:last-child {{ text-align:center; }}
        td {{ border-bottom:1px solid rgba(255,255,255,0.04); }}
        .legend {{ display:flex; gap:20px; margin-top:8px; padding:0 4px;
                   font-family:Rajdhani,sans-serif; font-size:1.64rem; color:#b0b8c8; }}
    </style></head><body>
    <div class="wrap">
      <table>
        <thead><tr>
          <th style="width:55px;">LVL</th>
          <th style="width:80px;"></th>
          <th>Small Blind</th>
          <th>Big Blind</th>
          <th>Ante</th>
          <th style="width:80px;">Duración</th>
        </tr></thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <div class="legend">
      <span><span style="color:#22c55e;">✓</span> Completado</span>
      <span><span style="color:#d4af37;">▶</span> Actual</span>
      <span><span style="color:#3b82f6;">●</span> Próximo</span>
    </div>
    </body></html>
    """

    components.html(full_html, height=395, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    save_state()
    time.sleep(1)
    st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB: JUGADORES
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "👥 Jugadores":
    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">➕ AGREGAR JUGADOR</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5, c6 = st.columns([3, 1.5, 1.5, 2, 1.8, 1])
    with c1:
        new_name = st.text_input("Nombre del Jugador", placeholder="Ej: Juan García", key="new_player_name")
    with c2:
        new_seat = st.number_input("Mesa/Asiento", min_value=1, max_value=20, value=1, key="new_seat")
    with c3:
        new_paid = st.number_input("💵 Importe cobrado ($)", min_value=0, value=st.session_state.buy_in, step=10, key="new_paid")
    with c4:
        new_chips = st.number_input("Chips iniciales", min_value=1000, value=st.session_state.starting_chips, step=1000, key="new_chips")
    with c5:
        new_payment_method = st.selectbox("💳 Forma de pago", ["Efectivo", "Transferencia", "Tarjeta", "Otro"], key="new_payment_method")
    with c6:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Agregar", use_container_width=True):
            if new_name.strip():
                pid = st.session_state.player_id_counter
                st.session_state.player_id_counter += 1
                st.session_state.players.append({
                    "id": pid,
                    "name": new_name.strip(),
                    "seat": new_seat,
                    "chips": new_chips,
                    "status": "active",
                    "buy_ins": 1,
                    "paid_amount": new_paid,
                    "payment_method": new_payment_method,
                    "rebuys": 0,
                    "rebuy_history": [],
                    "position": None,
                    "bounty": 0,
                    "added_at": datetime.now().strftime("%H:%M"),
                })
                add_alert(f"👤 {new_name.strip()} se unió al torneo — Cobrado: ${new_paid:,} ({new_payment_method}) Mesa {new_seat}")
                save_state()
                st.rerun()
            else:
                st.error("Ingresá un nombre para el jugador.")

    st.markdown('</div>', unsafe_allow_html=True)

    # CSV bulk import
    with st.expander("📂 Importar jugadores desde CSV"):
        st.markdown("El CSV debe tener columnas: `nombre`, `mesa`, `chips`")
        uploaded = st.file_uploader("Subir CSV", type=["csv"], key="player_csv")
        if uploaded:
            try:
                df_import = pd.read_csv(uploaded)
                df_import.columns = [c.lower().strip() for c in df_import.columns]
                count = 0
                for _, row in df_import.iterrows():
                    name = str(row.get("nombre", row.get("name", ""))).strip()
                    if name:
                        pid = st.session_state.player_id_counter
                        st.session_state.player_id_counter += 1
                        st.session_state.players.append({
                            "id": pid,
                            "name": name,
                            "seat": int(row.get("mesa", row.get("seat", 1))),
                            "chips": int(row.get("chips", st.session_state.starting_chips)),
                            "status": "active",
                            "buy_ins": 1,
                            "paid_amount": int(row.get("importe", row.get("paid", st.session_state.buy_in))),
                            "rebuys": 0,
                            "rebuy_history": [],
                            "position": None,
                            "bounty": 0,
                            "added_at": datetime.now().strftime("%H:%M"),
                        })
                        count += 1
                add_alert(f"📂 {count} jugadores importados desde CSV")
                st.success(f"✅ {count} jugadores importados correctamente.")
                save_state()
                st.rerun()
            except Exception as e:
                st.error(f"Error al leer CSV: {e}")

    # Players table
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">👥 JUGADORES ({len(st.session_state.players)})</div>', unsafe_allow_html=True)

    if not st.session_state.players:
        st.info("No hay jugadores registrados. Agregá jugadores arriba.")
    else:
        # ── BUSCADOR ──────────────────────────────────────────────────────────
        sc1, sc2 = st.columns([3, 1])
        with sc1:
            search_query = st.text_input("🔍 Buscar jugador", placeholder="Escribí el nombre...", key="player_search", label_visibility="collapsed")
        with sc2:
            filter_status = st.selectbox("Estado", ["Todos", "🟢 Activos", "💀 Eliminados"], key="player_filter", label_visibility="collapsed")

        # Sort: active first, then by chips desc
        sorted_players = sorted(st.session_state.players, key=lambda p: (0 if p["status"]=="active" else 1, -p["chips"]))

        # Apply filters
        if search_query.strip():
            sorted_players = [p for p in sorted_players if search_query.strip().lower() in p["name"].lower()]
        if filter_status == "🟢 Activos":
            sorted_players = [p for p in sorted_players if p["status"] == "active"]
        elif filter_status == "💀 Eliminados":
            sorted_players = [p for p in sorted_players if p["status"] == "eliminated"]

        if not sorted_players:
            st.warning("No se encontraron jugadores con ese criterio.")
        else:

            for i, p in enumerate(sorted_players):
                row_bg = "rgba(26,122,66,0.1)" if p["status"] == "active" else "rgba(100,0,0,0.1)"
                status_color = "#22c55e" if p["status"] == "active" else "#ef4444"
                status_icon = "🟢" if p["status"] == "active" else "💀"
                rank = i + 1 if p["status"] == "active" else ""
    
                with st.container():
                    c1, c2, c3, c4, c5, c6, c7 = st.columns([0.5, 3, 1.5, 2, 1.2, 1.8, 2])
                    with c1:
                        st.markdown(f"<span style='font-size:1.8rem;'>{status_icon}</span>", unsafe_allow_html=True)
                    with c2:
                        st.markdown(f"<span style='font-family:Rajdhani,sans-serif;font-size:1.5rem;font-weight:700;color:{'#f0ead6' if p['status']=='active' else '#6b7280'};'>{p['name']}</span>", unsafe_allow_html=True)
                        paid = p.get("paid_amount", st.session_state.buy_in)
                        rebuy_total = sum(r["amount"] for r in p.get("rebuy_history", []))
                        paid_fmt = f"{paid:,}"
                        method = p.get("payment_method", "Efectivo")
                        method_icons = {"Efectivo": "💵", "Transferencia": "📲", "Tarjeta": "💳", "Otro": "🔖"}
                        method_icon = method_icons.get(method, "💵")
                        lines = [f"<span style='font-size:1.05rem;color:#34d399;'>{method_icon} Buy-in: &#36;{paid_fmt} <span style='color:#6b7280;font-size:0.85rem;'>({method})</span></span>"]
                        for ri, r in enumerate(p.get("rebuy_history", [])):
                            rm = r.get("payment_method", "Efectivo")
                            ri_icon = method_icons.get(rm, "💵")
                            lines.append(f"<span style='font-size:0.95rem;color:#f0d060;'>{ri_icon} Rebuy #{ri+1}: &#36;{r['amount']:,} <span style='color:#6b7280;font-size:0.8rem;'>({rm})</span></span>")
                        for ai, a in enumerate(p.get("addon_history", [])):
                            am = a.get("payment_method", "Efectivo")
                            ai_icon = method_icons.get(am, "💵")
                            lines.append(f"<span style='font-size:0.95rem;color:#34d399;'>{ai_icon} Add-on #{ai+1}: &#36;{a['amount']:,} <span style='color:#6b7280;font-size:0.8rem;'>({am})</span></span>")
                        st.markdown("<br>".join(lines), unsafe_allow_html=True)
                    with c3:
                        st.markdown(f"<span style='font-size:1.2rem;color:#b0b8c8;font-weight:600;'>Mesa {p['seat']}</span>", unsafe_allow_html=True)
                    with c4:
                        if p["status"] == "active":
                            new_chips = st.number_input("", value=p["chips"], step=500, key=f"chips_{p['id']}", label_visibility="collapsed")
                            if new_chips != p["chips"]:
                                for pp in st.session_state.players:
                                    if pp["id"] == p["id"]:
                                        pp["chips"] = new_chips
                        else:
                            st.markdown(f"<span style='font-size:1.2rem;color:#6b7280;font-family:Share Tech Mono,monospace;'>ELIMINADO</span>", unsafe_allow_html=True)
                    with c5:
                        st.markdown(f"<span style='font-size:1.1rem;color:#b0b8c8;font-weight:600;'>Rebuys: {p['rebuys']}</span>", unsafe_allow_html=True)
                    with c6:
                        if p["status"] == "active" and st.session_state.rebuy_allowed:
                            rebuy_amt = st.number_input(
                                "Monto rebuy",
                                min_value=0,
                                value=st.session_state.rebuy_cost,
                                step=10,
                                key=f"rebuy_amt_{p['id']}",
                                label_visibility="collapsed",
                            )
                            rebuy_method = st.selectbox(
                                "Forma de pago",
                                ["Efectivo", "Transferencia", "Tarjeta", "Otro"],
                                key=f"rebuy_method_{p['id']}",
                                label_visibility="collapsed",
                            )
                    with c7:
                        if p["status"] == "active" and st.session_state.rebuy_allowed:
                            if st.button("🔄 Rebuy", key=f"rebuy_{p['id']}", use_container_width=True):
                                for pp in st.session_state.players:
                                    if pp["id"] == p["id"]:
                                        pp["chips"] += st.session_state.rebuy_chips
                                        pp["rebuys"] += 1
                                        if "rebuy_history" not in pp:
                                            pp["rebuy_history"] = []
                                        pp["rebuy_history"].append({
                                            "amount": st.session_state[f"rebuy_amt_{p['id']}"],
                                            "chips": st.session_state.rebuy_chips,
                                            "time": datetime.now().strftime("%H:%M"),
                                            "level": st.session_state.current_level + 1,
                                            "payment_method": st.session_state[f"rebuy_method_{p['id']}"],
                                        })
                                _r_amt = st.session_state.get(f"rebuy_amt_{p['id']}", st.session_state.rebuy_cost)
                                _r_met = st.session_state.get(f"rebuy_method_{p['id']}", "Efectivo")
                                add_alert(f"🔄 {p['name']} hizo rebuy — ${_r_amt:,} ({_r_met}) +{st.session_state.rebuy_chips:,} chips")
                                st.session_state.play_rebuy_sound = True
                                save_state()
                                st.rerun()
                            # ── ADD-ON ─────────────────────────────────────
                            if (st.session_state.get("addon_allowed") and
                                    st.session_state.get("addon_period_active")):
                                addon_cost_val = st.session_state.get("addon_cost", 30)
                                addon_ch = st.session_state.get("addon_chips", 5000)
                                addon_method = st.selectbox(
                                    "Forma de pago add-on",
                                    ["Efectivo", "Transferencia", "Tarjeta", "Otro"],
                                    key=f"addon_method_{p['id']}",
                                    label_visibility="collapsed",
                                )
                                if st.button(f"➕ Add-On ${addon_cost_val}", key=f"addon_{p['id']}", use_container_width=True):
                                    for pp in st.session_state.players:
                                        if pp["id"] == p["id"]:
                                            pp["chips"] += addon_ch
                                            pp["addons"] = pp.get("addons", 0) + 1
                                            if "addon_history" not in pp:
                                                pp["addon_history"] = []
                                            pp["addon_history"].append({
                                                "amount": addon_cost_val,
                                                "chips": addon_ch,
                                                "time": datetime.now().strftime("%H:%M"),
                                                "level": st.session_state.current_level + 1,
                                                "payment_method": addon_method,
                                            })
                                    add_alert(f"➕ {p['name']} hizo add-on — ${addon_cost_val:,} ({addon_method}) +{addon_ch:,} chips")
                                    save_state()
                                    st.rerun()
                    with c7:
                        if p["status"] == "active":
                            col_elim, col_edit = st.columns(2)
                            if col_elim.button("💀 Elim.", key=f"elim_{p['id']}", use_container_width=True):
                                n_active_before = len(get_active_players())
                                pos = n_active_before  # position = current count
                                for pp in st.session_state.players:
                                    if pp["id"] == p["id"]:
                                        pp["status"] = "eliminated"
                                        pp["chips"] = 0
                                        pp["position"] = pos
                                add_alert(f"💀 {p['name']} eliminado en posición #{pos}")
                                save_state()
                                st.rerun()
                            if col_edit.button("✏️ Editar", key=f"editpago_{p['id']}", use_container_width=True):
                                st.session_state["editando_pago_id"] = p["id"]
                        else:
                            if st.button("♻️ Restaurar", key=f"restore_{p['id']}", use_container_width=True):
                                for pp in st.session_state.players:
                                    if pp["id"] == p["id"]:
                                        pp["status"] = "active"
                                        pp["chips"] = st.session_state.starting_chips
                                        pp["position"] = None
                                save_state()
                                st.rerun()

                # ── FORMULARIO DE EDICIÓN DE PAGOS ────────────────────────────
                if st.session_state.get("editando_pago_id") == p["id"]:
                    with st.form(f"form_edit_pago_{p['id']}"):
                        st.markdown(f"#### ✏️ Editar jugador **{p['name']}**")

                        # ── Nombre y mesa ──────────────────────────────────
                        en1, en2 = st.columns([3, 1])
                        with en1:
                            nuevo_nombre = st.text_input(
                                "✏️ Nombre",
                                value=p.get("name", ""),
                                key=f"edit_nombre_{p['id']}"
                            )
                        with en2:
                            nueva_mesa = st.number_input(
                                "🪑 Mesa",
                                min_value=1, max_value=20,
                                value=p.get("seat", 1),
                                step=1,
                                key=f"edit_mesa_{p['id']}"
                            )

                        # ── Buy-in ─────────────────────────────────────────
                        st.markdown("**💵 Buy-in**")
                        col_bi1, col_bi2 = st.columns(2)
                        with col_bi1:
                            nuevo_buyin = st.number_input(
                                "Importe ($)",
                                min_value=0,
                                value=p.get("paid_amount", st.session_state.buy_in),
                                step=10,
                                key=f"edit_buyin_{p['id']}"
                            )
                        with col_bi2:
                            metodos = ["Efectivo", "Transferencia", "Tarjeta", "Otro"]
                            cur_method = p.get("payment_method", "Efectivo")
                            idx_method = metodos.index(cur_method) if cur_method in metodos else 0
                            nuevo_metodo = st.selectbox(
                                "💳 Forma de pago",
                                metodos,
                                index=idx_method,
                                key=f"edit_metodo_{p['id']}"
                            )

                        # ── Rebuys ─────────────────────────────────────────
                        rebuy_hist = p.get("rebuy_history", [])
                        nuevos_importes = []
                        nuevos_metodos_rebuy = []
                        if rebuy_hist:
                            st.markdown("**🔄 Rebuys:**")
                            for ri, rebuy in enumerate(rebuy_hist):
                                rr1, rr2 = st.columns(2)
                                with rr1:
                                    nuevo_importe = st.number_input(
                                        f"Rebuy #{ri+1} — {rebuy.get('time','')} (Nv.{rebuy.get('level','')})",
                                        min_value=0,
                                        value=rebuy["amount"],
                                        step=10,
                                        key=f"edit_rebuy_{p['id']}_{ri}"
                                    )
                                    nuevos_importes.append(nuevo_importe)
                                with rr2:
                                    metodos_r = ["Efectivo", "Transferencia", "Tarjeta", "Otro"]
                                    cur_mr = rebuy.get("payment_method", "Efectivo")
                                    idx_mr = metodos_r.index(cur_mr) if cur_mr in metodos_r else 0
                                    nuevo_mr = st.selectbox(
                                        f"Forma de pago rebuy #{ri+1}",
                                        metodos_r,
                                        index=idx_mr,
                                        key=f"edit_rebuy_met_{p['id']}_{ri}"
                                    )
                                    nuevos_metodos_rebuy.append(nuevo_mr)

                        cg, cc = st.columns(2)
                        guardar  = cg.form_submit_button("💾 Guardar", use_container_width=True, type="primary")
                        cancelar = cc.form_submit_button("✕ Cancelar", use_container_width=True)

                        if guardar:
                            for pp in st.session_state.players:
                                if pp["id"] == p["id"]:
                                    if nuevo_nombre.strip():
                                        pp["name"] = nuevo_nombre.strip()
                                    pp["seat"]           = nueva_mesa
                                    pp["paid_amount"]    = nuevo_buyin
                                    pp["payment_method"] = nuevo_metodo
                                    for ri, rebuy in enumerate(pp.get("rebuy_history", [])):
                                        if ri < len(nuevos_importes):
                                            rebuy["amount"] = nuevos_importes[ri]
                                        if ri < len(nuevos_metodos_rebuy):
                                            rebuy["payment_method"] = nuevos_metodos_rebuy[ri]
                            add_alert(f"✏️ {nuevo_nombre.strip()} actualizado — Buy-in: ${nuevo_buyin:,} ({nuevo_metodo})")
                            del st.session_state["editando_pago_id"]
                            save_state()
                            st.rerun()
                        if cancelar:
                            del st.session_state["editando_pago_id"]
                            st.rerun()
    
                st.divider()

    st.markdown('</div>', unsafe_allow_html=True)

    # ── CAJA / RESUMEN FINANCIERO ──────────────────────────────────────────────
    if st.session_state.players:
        total_buyin_collected = sum(p.get("paid_amount", st.session_state.buy_in) for p in st.session_state.players)
        total_rebuy_collected = sum(sum(r["amount"] for r in p.get("rebuy_history", [])) for p in st.session_state.players)
        total_rebuys_count    = sum(p["rebuys"] for p in st.session_state.players)
        grand_total           = total_buyin_collected + total_rebuy_collected
        pct                   = st.session_state.get("prize_pool_pct", 85)
        para_premios          = int(grand_total * pct / 100)
        para_casa             = grand_total - para_premios

        st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">💵 RESUMEN DE CAJA</div>', unsafe_allow_html=True)
        ca, cb, cc, cd = st.columns(4)
        with ca:
            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem;">
                <div style="font-size:0.85rem; color:#b0b8c8; letter-spacing:2px; font-weight:700;">BUY-INS</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2rem; color:#34d399;">&#36;{total_buyin_collected:,}</div>
                <div style="font-size:0.8rem; color:#9ca3af;">{len(st.session_state.players)} jugadores</div>
            </div>""", unsafe_allow_html=True)
        with cb:
            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem;">
                <div style="font-size:0.85rem; color:#b0b8c8; letter-spacing:2px; font-weight:700;">REBUYS</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2rem; color:#f0d060;">&#36;{total_rebuy_collected:,}</div>
                <div style="font-size:0.8rem; color:#9ca3af;">{total_rebuys_count} recompras</div>
            </div>""", unsafe_allow_html=True)
        with cc:
            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem;">
                <div style="font-size:0.85rem; color:#b0b8c8; letter-spacing:2px; font-weight:700;">TOTAL RECAUDADO</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2rem; color:#d4af37;">&#36;{grand_total:,}</div>
                <div style="font-size:0.8rem; color:#9ca3af;">100% recaudado</div>
            </div>""", unsafe_allow_html=True)
        with cd:
            avg_paid = grand_total / len(st.session_state.players) if st.session_state.players else 0
            st.markdown(f"""
            <div style="text-align:center; padding:0.8rem;">
                <div style="font-size:0.85rem; color:#b0b8c8; letter-spacing:2px; font-weight:700;">PROMEDIO POR JUGADOR</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2rem; color:#a78bfa;">&#36;{avg_paid:,.0f}</div>
                <div style="font-size:0.8rem; color:#9ca3af;">buy-in + rebuys</div>
            </div>""", unsafe_allow_html=True)

        # Desglose premios vs organización
        st.markdown(f"""
        <div style="display:flex; gap:1rem; margin:0.8rem 0;">
            <div style="flex:1; background:linear-gradient(135deg,rgba(212,175,55,0.15),rgba(212,175,55,0.05));
                        border:1px solid #d4af37; border-radius:10px; padding:0.9rem 1.2rem; text-align:center;">
                <div style="font-size:0.85rem; color:#b0b8c8; font-weight:700; letter-spacing:2px; margin-bottom:0.3rem;">🏆 PARA PREMIOS ({pct}%)</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2.2rem; color:#d4af37; font-weight:700;">&#36;{para_premios:,}</div>
            </div>
            <div style="flex:1; background:linear-gradient(135deg,rgba(167,139,250,0.15),rgba(167,139,250,0.05));
                        border:1px solid #a78bfa; border-radius:10px; padding:0.9rem 1.2rem; text-align:center;">
                <div style="font-size:0.85rem; color:#b0b8c8; font-weight:700; letter-spacing:2px; margin-bottom:0.3rem;">🏠 PARA ORGANIZACIÓN ({100 - pct}%)</div>
                <div style="font-family:'Share Tech Mono',monospace; font-size:2.2rem; color:#a78bfa; font-weight:700;">&#36;{para_casa:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # ── DESGLOSE POR MÉTODO DE PAGO ──────────────────────────────────────
        METHOD_ICONS  = {"Efectivo": "💵", "Transferencia": "📲", "Tarjeta": "💳", "Otro": "🔖"}
        METHOD_COLORS = {"Efectivo": "#34d399", "Transferencia": "#60a5fa", "Tarjeta": "#f0d060", "Otro": "#a78bfa"}

        # Acumular: separar buy-ins, rebuys y add-ons por método
        breakdown = {}   # {method: {"buyin": X, "rebuy": Y, "addon": Z}}
        for p in st.session_state.players:
            # buy-in
            m = p.get("payment_method", "Efectivo")
            if m not in breakdown: breakdown[m] = {"buyin": 0, "rebuy": 0, "addon": 0}
            breakdown[m]["buyin"] += p.get("paid_amount", st.session_state.buy_in)
            # rebuys
            for r in p.get("rebuy_history", []):
                rm = r.get("payment_method", "Efectivo")
                if rm not in breakdown: breakdown[rm] = {"buyin": 0, "rebuy": 0, "addon": 0}
                breakdown[rm]["rebuy"] += r["amount"]
            # add-ons
            for a in p.get("addon_history", []):
                am = a.get("payment_method", "Efectivo")
                if am not in breakdown: breakdown[am] = {"buyin": 0, "rebuy": 0, "addon": 0}
                breakdown[am]["addon"] += a["amount"]

        if breakdown:
            cards_html = ""
            for m, vals in sorted(breakdown.items()):
                icon  = METHOD_ICONS.get(m, "🔖")
                color = METHOD_COLORS.get(m, "#f0ead6")
                total_m = vals["buyin"] + vals["rebuy"] + vals["addon"]
                sub_parts = []
                if vals["buyin"] > 0:  sub_parts.append(f"Buy-ins: ${vals['buyin']:,}")
                if vals["rebuy"] > 0:  sub_parts.append(f"Rebuys: ${vals['rebuy']:,}")
                if vals["addon"] > 0:  sub_parts.append(f"Add-ons: ${vals['addon']:,}")
                sub_html = " &nbsp;·&nbsp; ".join(
                    f"<span style='color:#9ca3af;font-size:0.85rem;'>{s}</span>" for s in sub_parts
                )
                cards_html += f"""
                <div style="flex:1;min-width:160px;background:linear-gradient(135deg,#1a2a1e,#0d1f14);
                            border:1px solid {color}44;border-radius:12px;padding:1rem 1.2rem;text-align:center;">
                    <div style="font-size:1.8rem;margin-bottom:0.2rem;">{icon}</div>
                    <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;
                                letter-spacing:2px;color:#b0b8c8;margin-bottom:0.3rem;">{m.upper()}</div>
                    <div style="font-family:'Share Tech Mono',monospace;font-size:2rem;
                                color:{color};font-weight:700;">&#36;{total_m:,}</div>
                    <div style="margin-top:0.3rem;">{sub_html}</div>
                </div>"""
            st.markdown(f"""
            <div style="margin:0.8rem 0;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:0.8rem;letter-spacing:2px;
                            color:#9ca3af;font-weight:700;margin-bottom:0.5rem;">💳 RECAUDADO POR FORMA DE PAGO</div>
                <div style="display:flex;gap:0.8rem;flex-wrap:wrap;">{cards_html}</div>
            </div>""", unsafe_allow_html=True)

        # ── DETALLE POR JUGADOR ───────────────────────────────────────────────
        with st.expander("📋 Ver detalle por jugador"):
            detail_rows = []
            for p in st.session_state.players:
                paid = p.get("paid_amount", st.session_state.buy_in)
                rebuy_total = sum(r["amount"] for r in p.get("rebuy_history", []))
                addon_total = sum(a["amount"] for a in p.get("addon_history", []))
                rebuy_detail = ", ".join(
                    f"${r['amount']:,} {METHOD_ICONS.get(r.get('payment_method','Efectivo'),'💵')} Nv.{r['level']} {r['time']}"
                    for r in p.get("rebuy_history", [])
                ) or "—"
                detail_rows.append({
                    "Jugador":       p["name"],
                    "Mesa":          p["seat"],
                    "Estado":        "🟢 Activo" if p["status"] == "active" else "💀 Eliminado",
                    "Buy-in $":      f"${paid:,}",
                    "Pago buy-in":   METHOD_ICONS.get(p.get("payment_method","Efectivo"),"💵") + " " + p.get("payment_method","Efectivo"),
                    "Rebuys":        p["rebuys"],
                    "$ Rebuys":      f"${rebuy_total:,}",
                    "Add-ons":       p.get("addons", 0),
                    "$ Add-ons":     f"${addon_total:,}",
                    "TOTAL $":       f"${paid + rebuy_total + addon_total:,}",
                    "Detalle rebuys": rebuy_detail,
                })
            st.dataframe(pd.DataFrame(detail_rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # Leaderboard
    if st.session_state.players:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🏅 LEADERBOARD</div>', unsafe_allow_html=True)

        active_sorted = sorted(get_active_players(), key=lambda x: -x["chips"])
        rows = []
        medals = ["🥇", "🥈", "🥉"]
        for i, p in enumerate(active_sorted):
            mr = m_ratio(p["chips"])
            mr_str = f"{mr:.1f}" if mr < 999 else "∞"
            paid = p.get("paid_amount", st.session_state.buy_in)
            rebuy_total = sum(r["amount"] for r in p.get("rebuy_history", []))
            rows.append({
                "Pos": medals[i] if i < 3 else f"#{i+1}",
                "Jugador": p["name"],
                "Mesa": p["seat"],
                "Chips": f"{p['chips']:,}",
                "M-ratio": mr_str,
                "Buy-in $": f"${paid:,}",
                "Rebuys": p["rebuys"],
                "Total cobrado $": f"${paid + rebuy_total:,}",
            })

        if rows:
            header_cols = list(rows[0].keys())
            th_html = "".join(f"<th>{c}</th>" for c in header_cols)
            rows_html = ""
            for row in rows:
                cells = "".join(f"<td>{v}</td>" for v in row.values())
                rows_html += f"<tr>{cells}</tr>"
            st.markdown(f"""
            <style>
            .lb-table {{ width:100%; border-collapse:collapse; font-family:'Rajdhani',sans-serif; }}
            .lb-table th {{
                font-size:1.15rem; font-weight:700; letter-spacing:2px; color:#b0b8c8;
                text-transform:uppercase; padding:10px 14px; border-bottom:2px solid rgba(212,175,55,0.3);
                background:#111827; text-align:left;
            }}
            .lb-table td {{
                font-size:1.25rem; font-weight:600; color:#f0ead6;
                padding:10px 14px; border-bottom:1px solid rgba(255,255,255,0.05);
                font-family:'Share Tech Mono',monospace;
            }}
            .lb-table tr:hover td {{ background:rgba(212,175,55,0.06); }}
            </style>
            <table class="lb-table">
              <thead><tr>{th_html}</tr></thead>
              <tbody>{rows_html}</tbody>
            </table>
            """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB: APUESTAS
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "💰 Apuestas":
    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">💰 REGISTRAR APUESTA / POT</div>', unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns([2, 2, 2, 2, 1])
    with c1:
        player_names = [p["name"] for p in get_active_players()]
        bet_player = st.selectbox("Jugador", ["-- Seleccionar --"] + player_names, key="bet_player")
    with c2:
        bet_type = st.selectbox("Tipo", ["Pre-flop", "Flop", "Turn", "River", "All-in", "Side Pot", "Bounty"], key="bet_type")
    with c3:
        bet_amount = st.number_input("Monto", min_value=0, value=0, step=100, key="bet_amount")
    with c4:
        bet_note = st.text_input("Nota", placeholder="Opcional...", key="bet_note")
    with c5:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ Registrar", use_container_width=True):
            if bet_player != "-- Seleccionar --" and bet_amount > 0:
                st.session_state.bets.append({
                    "time": datetime.now().strftime("%H:%M:%S"),
                    "player": bet_player,
                    "type": bet_type,
                    "amount": bet_amount,
                    "level": st.session_state.current_level + 1,
                    "note": bet_note,
                })
                # Deduct from player chips
                for p in st.session_state.players:
                    if p["name"] == bet_player:
                        p["chips"] = max(0, p["chips"] - bet_amount)
                add_alert(f"💰 {bet_player} apostó ${bet_amount:,} ({bet_type})")
                save_state()
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Pot calculator
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🎲 CALCULADORA DE POT</div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("**Pot actual por jugadores activos:**")
        active_bets = [b for b in st.session_state.bets]
        if active_bets:
            df_bets = pd.DataFrame(active_bets)[["time", "player", "type", "amount", "level", "note"]]
            df_bets.columns = ["Hora", "Jugador", "Tipo", "Monto ($)", "Nivel", "Nota"]
            st.dataframe(df_bets.tail(20), use_container_width=True, hide_index=True)
        else:
            st.info("No hay apuestas registradas aún.")

    with col_b:
        st.markdown("**Resumen por jugador:**")
        if st.session_state.bets:
            by_player = {}
            for b in st.session_state.bets:
                by_player[b["player"]] = by_player.get(b["player"], 0) + b["amount"]

            rows = sorted(by_player.items(), key=lambda x: -x[1])
            total_pot = sum(v for _, v in rows)
            st.markdown(f"**Total apostado: ${total_pot:,}**")
            df_sum = pd.DataFrame(rows, columns=["Jugador", "Total apostado ($)"])
            df_sum["Total apostado ($)"] = df_sum["Total apostado ($)"].apply(lambda x: f"${x:,}")
            st.dataframe(df_sum, use_container_width=True, hide_index=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Clear bets
    if st.session_state.bets:
        if st.button("🗑️ Limpiar historial de apuestas"):
            st.session_state.bets = []
            save_state()
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB: PREMIOS
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "🏆 Premios":
    eff_pool  = effective_prize_pool()
    n_players = len(st.session_state.players)

    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🏆 PRIZE POOL</div>', unsafe_allow_html=True)
    st.markdown(f"""
    <div style="text-align:center; padding:1.2rem; background:rgba(212,175,55,0.1);
                border:2px solid #d4af37; border-radius:12px; margin-bottom:0.5rem;">
        <div style="font-family:'Share Tech Mono',monospace; font-size:3.5rem;
                    color:#d4af37; text-shadow:0 0 30px rgba(212,175,55,0.5);">&#36;{eff_pool:,}</div>
        <div style="font-size:1rem; letter-spacing:3px; color:#b0b8c8; margin-top:0.3rem; font-weight:700;">TOTAL EN PREMIOS</div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Payout distribution
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">💵 DISTRIBUCIÓN DE PREMIOS</div>', unsafe_allow_html=True)

    payouts = calculate_payouts_fixed(eff_pool, n_players)
    place_styles = ["prize-1st", "prize-2nd", "prize-3rd"]
    place_labels = ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar", "4to Lugar", "5to Lugar"]

    for i, p in enumerate(payouts):
        style = place_styles[i] if i < 3 else "prize-other"
        label = place_labels[i] if i < len(place_labels) else f"{p['place']}to Lugar"
        st.markdown(f"""
        <div class="prize-row {style}">
            <span>{label}</span>
            <span style="color:#9ca3af;">{p['pct']}%</span>
            <span style="font-family:'Share Tech Mono',monospace; color:#d4af37; font-size:1.1rem;">&#36;{p['amount']:,}</span>
        </div>
        """, unsafe_allow_html=True)

    if eff_pool == 0:
        st.info("Agrega jugadores para calcular los premios.")

    st.markdown('</div>', unsafe_allow_html=True)

    # Detailed player financials
    if st.session_state.players:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📊 DETALLE POR JUGADOR</div>', unsafe_allow_html=True)

        rows = []
        for p in st.session_state.players:
            total_paid = p["buy_ins"] * st.session_state.buy_in + p["rebuys"] * st.session_state.rebuy_cost
            rows.append({
                "Jugador": p["name"],
                "Estado": "✅ Activo" if p["status"] == "active" else f"❌ Pos. #{p.get('position', '?')}",
                "Buy-ins": p["buy_ins"],
                "Rebuys": p["rebuys"],
                "Total Pagado": f"${total_paid:,}",
                "Chips": f"{p['chips']:,}" if p["status"] == "active" else "-",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════════
# TAB: CONFIGURACIÓN
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "⚙️ Configuración":
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["🎮 Torneo", "🕐 Ciegas", "🔔 Alertas", "💸 Premios", "➕ Add-On", "🖥️ Pantalla", "🧙 Wizards"])

    with tab1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🎮 CONFIGURACIÓN DEL TORNEO</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Nombre del Torneo", value=st.session_state.tournament_name)
            if name != st.session_state.tournament_name:
                st.session_state.tournament_name = name
                save_state()

            buy_in = st.number_input("Buy-in ($)", min_value=1, value=st.session_state.buy_in, step=5)
            if buy_in != st.session_state.buy_in:
                st.session_state.buy_in = buy_in
                save_state()

            starting = st.number_input("Chips iniciales", min_value=1000, value=st.session_state.starting_chips, step=1000)
            if starting != st.session_state.starting_chips:
                st.session_state.starting_chips = starting
                save_state()

            prize_pct = st.number_input(
                "🏆 % de recaudación para premios",
                min_value=1, max_value=100,
                value=st.session_state.get("prize_pool_pct", 85),
                step=1,
                help="Ej: 85 significa que el 85% de lo recaudado va a premios y el 15% restante es para gastos/organización."
            )
            if prize_pct != st.session_state.get("prize_pool_pct", 85):
                st.session_state.prize_pool_pct = prize_pct
                save_state()
            recaudado = total_prize_pool()
            para_premios = int(recaudado * prize_pct / 100)
            para_casa   = recaudado - para_premios
            st.markdown(f"""
            <div style="background:rgba(212,175,55,0.08); border:1px solid #d4af37;
                        border-radius:8px; padding:0.7rem 1rem; margin-top:0.3rem;">
                <div style="font-size:1rem; color:#b0b8c8; margin-bottom:0.3rem;">Con la recaudación actual de <strong style="color:#34d399;">&#36;{recaudado:,}</strong>:</div>
                <div style="font-size:1.1rem; color:#d4af37;">🏆 Para premios: <strong>&#36;{para_premios:,}</strong> ({prize_pct}%)</div>
                <div style="font-size:1.1rem; color:#a78bfa;">🏠 Para organización: <strong>&#36;{para_casa:,}</strong> ({100 - prize_pct}%)</div>
            </div>
            """, unsafe_allow_html=True)

        with c2:
            rebuy_allowed = st.toggle("Permitir Rebuys", value=st.session_state.rebuy_allowed)
            st.session_state.rebuy_allowed = rebuy_allowed

            if rebuy_allowed:
                rebuy_cost = st.number_input("Costo del Rebuy ($)", min_value=1, value=st.session_state.rebuy_cost, step=5)
                st.session_state.rebuy_cost = rebuy_cost

                rebuy_chips = st.number_input("Chips del Rebuy", min_value=1000, value=st.session_state.rebuy_chips, step=1000)
                st.session_state.rebuy_chips = rebuy_chips

            break_dur = st.number_input("Duración descanso (min)", min_value=1, max_value=30, value=st.session_state.break_duration)
            st.session_state.break_duration = break_dur

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="panel" style="border-color:#ef4444; margin-top:1rem;">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title" style="color:#ef4444;">⚠️ ZONA DE PELIGRO</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#9ca3af; font-size:1rem;'>Esta acción borrará <strong style='color:#ef4444;'>todos los datos del torneo</strong> de forma permanente: jugadores, chips, historial, caja y timer. No se puede deshacer.</p>", unsafe_allow_html=True)

        confirm = st.checkbox("✅ Confirmo que quiero resetear todo el torneo", key="confirm_reset")
        if st.button("🗑️ RESETEAR TORNEO COMPLETO", use_container_width=True, type="primary", disabled=not confirm):
            reset_tournament()
            st.success("✅ Torneo reseteado. Todos los datos fueron borrados.")
            save_state()
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🕐 ESTRUCTURA DE CIEGAS</div>', unsafe_allow_html=True)

        # ── Botones para agregar / eliminar niveles ────────────────────────
        ba1, ba2, ba3, ba4 = st.columns(4)
        with ba1:
            if st.button("➕ Agregar nivel al final", use_container_width=True, type="primary"):
                last = st.session_state.blind_levels[-1] if st.session_state.blind_levels else {"level": 0, "small": 25, "big": 50, "ante": 0, "duration": 15}
                st.session_state.blind_levels.append({
                    "level":    last["level"] + 1,
                    "small":    int(last["small"] * 1.5),
                    "big":      int(last["big"] * 1.5),
                    "ante":     int(last["ante"] * 1.5) if last["ante"] else 0,
                    "duration": last.get("duration", 15),
                })
                save_state()
                st.rerun()
        with ba2:
            if st.button("📋 Duplicar último nivel", use_container_width=True):
                if st.session_state.blind_levels:
                    last = st.session_state.blind_levels[-1].copy()
                    last["level"] = last["level"] + 1
                    st.session_state.blind_levels.append(last)
                    save_state()
                    st.rerun()
        with ba3:
            n_add = st.number_input("Cantidad a agregar", min_value=1, max_value=20, value=5, step=1, key="bulk_add_n", label_visibility="collapsed")
        with ba4:
            if st.button(f"➕ Agregar {n_add} niveles", use_container_width=True):
                last = st.session_state.blind_levels[-1] if st.session_state.blind_levels else {"level": 0, "small": 25, "big": 50, "ante": 0, "duration": 15}
                for _ in range(int(n_add)):
                    last = {
                        "level":    last["level"] + 1,
                        "small":    int(last["small"] * 1.4),
                        "big":      int(last["big"] * 1.4),
                        "ante":     int(last["ante"] * 1.4) if last["ante"] else 0,
                        "duration": last.get("duration", 15),
                    }
                    st.session_state.blind_levels.append(last)
                save_state()
                st.rerun()

        st.markdown(f"<p style='color:#9ca3af;font-size:0.85rem;margin:0.3rem 0 0.5rem;'>Total: <strong style='color:#d4af37;'>{len(st.session_state.blind_levels)} niveles</strong> — editá los valores directamente en la tabla y guardá.</p>", unsafe_allow_html=True)

        # ── Tabla editable ─────────────────────────────────────────────────
        blinds_data = []
        for b in st.session_state.blind_levels:
            blinds_data.append({
                "Nivel":          b["level"],
                "Small Blind":    b["small"],
                "Big Blind":      b["big"],
                "Ante":           b["ante"],
                "Duración (min)": b.get("duration", st.session_state.level_duration),
            })

        df_blinds = pd.DataFrame(blinds_data)
        edited = st.data_editor(
            df_blinds,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key="blinds_editor",
            column_config={
                "Nivel":          st.column_config.NumberColumn("Nivel",          min_value=1, step=1),
                "Small Blind":    st.column_config.NumberColumn("Small Blind",    min_value=0, step=25),
                "Big Blind":      st.column_config.NumberColumn("Big Blind",      min_value=0, step=50),
                "Ante":           st.column_config.NumberColumn("Ante",           min_value=0, step=25),
                "Duración (min)": st.column_config.NumberColumn("Duración (min)", min_value=1, max_value=120, step=1),
            }
        )

        sc1, sc2, sc3, sc4 = st.columns(4)
        with sc1:
            if st.button("💾 Guardar cambios", use_container_width=True, type="primary"):
                new_blinds = []
                for i, (_, row) in enumerate(edited.iterrows()):
                    new_blinds.append({
                        "level":    int(row["Nivel"]) if not pd.isna(row["Nivel"]) else i + 1,
                        "small":    int(row["Small Blind"]) if not pd.isna(row["Small Blind"]) else 0,
                        "big":      int(row["Big Blind"]) if not pd.isna(row["Big Blind"]) else 0,
                        "ante":     int(row["Ante"]) if not pd.isna(row["Ante"]) else 0,
                        "duration": int(row["Duración (min)"]) if not pd.isna(row["Duración (min)"]) else 15,
                    })
                st.session_state.blind_levels = new_blinds
                add_alert(f"📋 Estructura actualizada — {len(new_blinds)} niveles")
                st.success(f"✅ {len(new_blinds)} niveles guardados.")
                save_state()
                st.rerun()
        with sc2:
            if st.button("🗑️ Eliminar último nivel", use_container_width=True):
                if len(st.session_state.blind_levels) > 1:
                    st.session_state.blind_levels.pop()
                    save_state()
                    st.rerun()
        with sc3:
            if st.button("📋 Cargar EPL (imagen)", use_container_width=True):
                st.session_state.blind_levels = get_default_blinds()
                # Pre-cargar breaks EPL en la configuración
                st.session_state.break_duration = 15
                add_alert("📋 Estructura EPL cargada — Breaks: Nv.6 (15min), Nv.12 (15min), Nv.18 (45min), Nv.24 (15min)")
                save_state()
                st.rerun()
        with sc4:
            if st.button("⚡ Cargar Turbo (8 min)", use_container_width=True):
                turbo = [{**b, "duration": 8} for b in get_default_blinds()]
                st.session_state.blind_levels = turbo
                save_state()
                st.rerun()

        # ── Info de breaks EPL ─────────────────────────────────────────────
        st.markdown("""
        <div style="background:rgba(37,99,235,0.08);border:1px solid #2563eb33;border-radius:8px;
                    padding:0.6rem 1rem;margin-top:0.5rem;font-size:0.88rem;color:#9ca3af;">
            ☕ <strong style="color:#60a5fa;">Breaks EPL (manuales):</strong>
            después del <strong>Nivel 6</strong> → 15 min &nbsp;|&nbsp;
            después del <strong>Nivel 12</strong> → 15 min &nbsp;|&nbsp;
            después del <strong>Nivel 18</strong> → 45 min (Dinner) &nbsp;|&nbsp;
            después del <strong>Nivel 24</strong> → 15 min
            <br><span style="color:#6b7280;">Usá el botón ☕ Descanso en la pantalla principal para iniciarlos en el momento correcto.</span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🔔 CONFIGURACIÓN DE ALERTAS</div>', unsafe_allow_html=True)

        st.toggle("Alertas visuales de tiempo", value=True, key="visual_alerts")
        st.toggle("Auto-avanzar nivel al terminar el tiempo", value=True, key="auto_advance")

        mute_state = "🔇 SILENCIADO" if st.session_state.sound_muted else "🔔 ACTIVO"
        mute_color = "#ef4444" if st.session_state.sound_muted else "#22c55e"
        st.markdown(f"""
        <div style="background:rgba(37,99,235,0.1); border:1px solid #374151; border-radius:8px; padding:1rem; margin-top:0.5rem;">
            <p style="color:#9ca3af; font-size:0.85rem; margin:0 0 0.5rem 0;">
                🔊 <strong>Estado del sonido:</strong>
                <span style="color:{mute_color}; font-weight:700;">{mute_state}</span>
                <br><small style="color:#6b7280;">(Controlá el sonido desde el botón en la barra lateral)</small>
            </p>
            <p style="color:#9ca3af; font-size:0.85rem; margin:0;">
                💡 <strong>Alertas automáticas:</strong><br>
                • ⚠️ <strong>1 minuto</strong> antes → 2 beeps agudos (tono suave)<br>
                • 🚨 <strong>30 segundos</strong> antes → 3 beeps urgentes (tono cuadrado)<br>
                • 🔄 <strong>Cambio de nivel</strong> → fanfarria ascendente (4 notas)<br>
                • ☕ <strong>Fin del descanso</strong> → 2 beeps de aviso<br>
                • 💀 <strong>Al eliminar jugador</strong> → Registro en historial
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">💸 TABLA DE PAGOS — PORCENTAJES POR RANGO</div>', unsafe_allow_html=True)

        st.markdown("""
        <p style="color:#9ca3af; font-size:0.9rem; margin-bottom:1rem;">
        El sistema detecta automáticamente el rango según la cantidad de jugadores inscriptos y aplica
        los porcentajes correspondientes. Editá la tabla y guardá los cambios. Cada rango debe sumar 100%.
        </p>
        """, unsafe_allow_html=True)

        brackets = st.session_state.prize_percentages
        bracket_keys = sorted(brackets.keys(), key=lambda x: int(x))

        bracket_labels = {
            "2":   "hasta 2 jugadores",
            "4":   "3 – 4 jugadores",
            "6":   "5 – 6 jugadores",
            "32":  "7 – 32 jugadores",
            "40":  "33 – 40 jugadores",
            "48":  "41 – 48 jugadores",
            "56":  "49 – 56 jugadores",
            "64":  "57 – 64 jugadores",
            "72":  "65 – 72 jugadores",
            "80":  "73 – 80 jugadores",
            "88":  "81 – 88 jugadores",
            "96":  "89 – 96 jugadores",
            "104": "97 – 104 jugadores",
        }

        # Show current player count hint
        n_now = len(st.session_state.players)
        active_key = None
        for key in bracket_keys:
            if n_now <= int(key):
                active_key = key
                break
        if active_key is None and bracket_keys:
            active_key = bracket_keys[-1]

        if n_now > 0 and active_key:
            st.markdown(f"""
            <div style="background:rgba(212,175,55,0.1); border:1px solid #d4af37; border-radius:8px;
                        padding:0.5rem 1rem; margin-bottom:1rem; font-size:0.9rem; color:#d4af37;">
                🎯 Con <strong>{n_now} jugadores</strong> actuales se aplicará el rango:
                <strong>{bracket_labels.get(active_key, active_key)}</strong>
                ({len(brackets[active_key])} lugares pagados)
            </div>
            """, unsafe_allow_html=True)

        # Build combined view table (read-only overview)
        st.markdown("#### 📊 Vista general — todos los rangos")
        all_places = list(range(1, 14))
        overview_data = {"Lugar": [f"{p}°" for p in all_places]}
        for key in bracket_keys:
            col_label = bracket_labels.get(key, f"≤{key}P")
            pct_map = {r["place"]: r["pct"] for r in brackets[key]}
            overview_data[col_label] = [
                f"{pct_map[p]:.3f}%" if p in pct_map else "—"
                for p in all_places
            ]
        df_overview = pd.DataFrame(overview_data)
        st.dataframe(df_overview, use_container_width=True, hide_index=True)

        st.markdown("<hr style='border-color:#1f2937; margin:1rem 0;'>", unsafe_allow_html=True)

        # Editable section — select range
        st.markdown("#### ✏️ Editar rango")
        selected_label = st.selectbox(
            "Seleccioná el rango a editar:",
            options=bracket_keys,
            format_func=lambda k: bracket_labels.get(k, f"Hasta {k} jugadores"),
            key="prize_bracket_select"
        )

        rows = brackets[selected_label]
        df_edit = pd.DataFrame([
            {"Lugar": f"{r['place']}°", "Porcentaje (%)": float(r["pct"])}
            for r in rows
        ])

        edited_df = st.data_editor(
            df_edit,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Lugar": st.column_config.TextColumn("Lugar", disabled=True),
                "Porcentaje (%)": st.column_config.NumberColumn(
                    "Porcentaje (%)",
                    min_value=0.0,
                    max_value=100.0,
                    step=0.025,
                    format="%.3f",
                ),
            },
            key=f"prize_editor_{selected_label}"
        )

        total_pct = edited_df["Porcentaje (%)"].sum()
        diff = abs(total_pct - 100.0)
        if diff < 0.05:
            st.markdown(f"<span style='color:#22c55e; font-size:0.9rem; font-weight:700;'>✅ Total: {total_pct:.3f}% — OK</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='color:#ef4444; font-size:0.9rem; font-weight:700;'>❌ Total: {total_pct:.3f}% — Debe sumar exactamente 100%</span>", unsafe_allow_html=True)

        col_save, col_reset_one, col_reset_all = st.columns(3)
        with col_save:
            if st.button("💾 Guardar este rango", use_container_width=True, type="primary", disabled=(diff >= 0.05)):
                new_rows = [
                    {"place": i + 1, "pct": float(edited_df.iloc[i]["Porcentaje (%)"])}
                    for i in range(len(edited_df))
                ]
                updated = dict(st.session_state.prize_percentages)
                updated[selected_label] = new_rows
                st.session_state.prize_percentages = updated
                add_alert(f"💸 Porcentajes actualizados — rango {bracket_labels.get(selected_label, selected_label)}")
                st.success("✅ Rango guardado!")
                save_state()
                st.rerun()
        with col_reset_one:
            if st.button("↩️ Reset este rango", use_container_width=True):
                defaults = get_default_prize_percentages()
                if selected_label in defaults:
                    updated = dict(st.session_state.prize_percentages)
                    updated[selected_label] = defaults[selected_label]
                    st.session_state.prize_percentages = updated
                    save_state()
                    st.rerun()
        with col_reset_all:
            if st.button("🔄 Reset todos", use_container_width=True):
                st.session_state.prize_percentages = get_default_prize_percentages()
                add_alert("🔄 Tabla de pagos reseteada a valores EPL por defecto")
                save_state()
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 5: ADD-ON ─────────────────────────────────────────────────────────
    with tab5:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">➕ CONFIGURACIÓN DE ADD-ON</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#9ca3af;font-size:0.9rem;'>El <strong>add-on</strong> es una compra opcional de fichas que se ofrece al final del período de rebuy, independientemente del stack.</p>", unsafe_allow_html=True)

        addon_on = st.toggle("Habilitar Add-Ons", value=st.session_state.get("addon_allowed", False), key="addon_toggle_cfg")
        if addon_on != st.session_state.get("addon_allowed", False):
            st.session_state.addon_allowed = addon_on
            save_state()

        if addon_on:
            ac1, ac2, ac3 = st.columns(3)
            with ac1:
                addon_cost = st.number_input("Costo del Add-On ($)", min_value=1, value=st.session_state.get("addon_cost", 30), step=5, key="aoc")
                if addon_cost != st.session_state.get("addon_cost", 30):
                    st.session_state.addon_cost = addon_cost; save_state()
            with ac2:
                addon_chips = st.number_input("Chips del Add-On", min_value=500, value=st.session_state.get("addon_chips", 5000), step=500, key="aoch")
                if addon_chips != st.session_state.get("addon_chips", 5000):
                    st.session_state.addon_chips = addon_chips; save_state()
            with ac3:
                addon_limit = st.number_input("Disponible hasta nivel Nº", min_value=1, max_value=35, value=st.session_state.get("addon_level_limit", 6), step=1, key="aol")
                if addon_limit != st.session_state.get("addon_level_limit", 6):
                    st.session_state.addon_level_limit = addon_limit; save_state()

            cur_lvl = st.session_state.current_level + 1
            if cur_lvl <= addon_limit:
                st.success(f"✅ Período de add-on ACTIVO (nivel {cur_lvl} ≤ límite {addon_limit})")
            else:
                st.error(f"🚫 Período de add-on CERRADO (nivel {cur_lvl} > límite {addon_limit})")

            col_open, col_close = st.columns(2)
            with col_open:
                if st.button("🔓 Abrir período add-on", use_container_width=True, key="aop_open"):
                    st.session_state.addon_period_active = True
                    add_alert("🔓 Período de add-on abierto manualmente"); save_state(); st.rerun()
            with col_close:
                if st.button("🔒 Cerrar período add-on", use_container_width=True, key="aop_close"):
                    st.session_state.addon_period_active = False
                    add_alert("🔒 Período de add-on cerrado manualmente"); save_state(); st.rerun()

            total_addons = sum(p.get("addons", 0) for p in st.session_state.players)
            total_addon_money = sum(sum(a["amount"] for a in p.get("addon_history", [])) for p in st.session_state.players)
            st.markdown(f"""
            <div style="background:rgba(52,211,153,0.08);border:1px solid #34d399;border-radius:8px;
                        padding:0.8rem 1rem;margin-top:0.8rem;display:flex;gap:2rem;">
                <div><span style="color:#9ca3af;">Add-ons realizados:</span>
                     <strong style="color:#34d399;font-size:1.2rem;margin-left:0.5rem;">{total_addons}</strong></div>
                <div><span style="color:#9ca3af;">Recaudado:</span>
                     <strong style="color:#d4af37;font-size:1.2rem;margin-left:0.5rem;">${total_addon_money:,}</strong></div>
            </div>""", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 6: PANTALLA ───────────────────────────────────────────────────────
    with tab6:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🖥️ CONFIGURACIÓN DE PANTALLA INFORMATIVA</div>', unsafe_allow_html=True)

        st.markdown("#### 📢 Ticker / Mensaje en pantalla")
        ticker_enabled = st.toggle("Mostrar ticker en pantalla", value=st.session_state.get("display_ticker_enabled", False), key="ticker_tog")
        if ticker_enabled != st.session_state.get("display_ticker_enabled", False):
            st.session_state.display_ticker_enabled = ticker_enabled; save_state()

        ticker_text = st.text_input("Texto del ticker", value=st.session_state.get("display_ticker", ""),
                                     placeholder="Ej: ♠ Próximo torneo el sábado — inscripciones abiertas ♠", key="ticker_txt")
        if ticker_text != st.session_state.get("display_ticker", ""):
            st.session_state.display_ticker = ticker_text; save_state()

        if ticker_enabled and ticker_text:
            st.markdown(f"""
            <div style="background:linear-gradient(90deg,#1e3a5f,#2563eb,#1e3a5f);border:1px solid #3b82f6;
                        border-radius:8px;padding:0.6rem 1rem;text-align:center;font-family:'Bebas Neue',cursive;
                        font-size:1.4rem;letter-spacing:3px;color:#bfdbfe;margin-top:0.5rem;">
                {ticker_text}
            </div>""", unsafe_allow_html=True)

        st.markdown("<hr style='border-color:#1f2937;margin:1rem 0;'>", unsafe_allow_html=True)
        st.markdown("#### 🔄 Vistas rotativas (display.py)")
        st.markdown("<p style='color:#9ca3af;font-size:0.9rem;'>Seleccioná qué vistas rotar en el proyector y cada cuántos segundos.</p>", unsafe_allow_html=True)

        available_views = {
            "timer":  "⏱ Timer principal (nivel + cronómetro + ciegas)",
            "blinds": "📋 Estructura completa de niveles",
            "prizes": "💰 Tabla de premios",
        }
        current_views = st.session_state.get("display_views", ["timer", "blinds", "prizes"])
        selected_views = []
        for vk, vl in available_views.items():
            if st.checkbox(vl, value=(vk in current_views), key=f"vw_{vk}"):
                selected_views.append(vk)
        if not selected_views:
            selected_views = ["timer"]
        if selected_views != current_views:
            st.session_state.display_views = selected_views; save_state()

        view_interval = st.slider("Segundos por vista", min_value=5, max_value=60,
                                   value=st.session_state.get("display_view_interval", 15), step=5, key="vi_sl")
        if view_interval != st.session_state.get("display_view_interval", 15):
            st.session_state.display_view_interval = view_interval; save_state()

        st.markdown('</div>', unsafe_allow_html=True)

    # ── TAB 7: WIZARDS ────────────────────────────────────────────────────────
    with tab7:
        wiz1, wiz2, wiz3 = st.tabs(["🧙 Estructura", "💸 Pagos", "👤 Base de Jugadores"])

        with wiz1:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">🧙 WIZARD DE ESTRUCTURA DE CIEGAS</div>', unsafe_allow_html=True)
            w1, w2 = st.columns(2)
            with w1:
                wiz_players = st.number_input("Jugadores", min_value=2, max_value=200, value=20, step=1, key="wzp")
                wiz_hours   = st.number_input("Duración deseada (horas)", min_value=1.0, max_value=12.0, value=4.0, step=0.5, key="wzh")
                wiz_stack   = st.number_input("Stack inicial", min_value=1000, max_value=500000, value=10000, step=1000, key="wzs")
            with w2:
                wiz_style   = st.selectbox("Estilo", ["Normal", "Turbo", "Hyper", "Deep Stack"], key="wzst")
                wiz_antes   = st.toggle("Incluir antes (desde nivel 3)", value=True, key="wzante")
                wiz_rebuy_n = st.number_input("Niveles con rebuy period", min_value=0, max_value=10, value=4, step=1, key="wzrb")

            if st.button("⚡ Generar estructura automáticamente", use_container_width=True, type="primary", key="wiz_gen"):
                import math as _math
                total_min  = wiz_hours * 60
                est_levels = max(12, min(35, int(_math.ceil(_math.log2(max(wiz_players, 2)) * 3.5))))
                level_dur  = max(5, int(total_min / est_levels))
                if wiz_style == "Turbo":    level_dur = max(5, level_dur // 2)
                elif wiz_style == "Hyper":  level_dur = max(3, level_dur // 3)
                elif wiz_style == "Deep Stack": level_dur = int(level_dur * 1.4)
                mult = {"Normal": 1.25, "Turbo": 1.4, "Hyper": 1.6, "Deep Stack": 1.2}.get(wiz_style, 1.25)
                generated, sb = [], max(25, wiz_stack // 400)
                for i in range(est_levels):
                    ante = int(round(sb / 25) * 25) if wiz_antes and i >= 2 else 0
                    generated.append({"level": i+1, "small": int(round(sb/25)*25) or 25,
                                       "big": int(round(sb*2/25)*25) or 50,
                                       "ante": ante, "duration": level_dur})
                    sb = int(sb * mult)
                st.session_state.blind_levels = generated
                add_alert(f"🧙 Estructura generada: {est_levels} niveles × {level_dur} min")
                save_state()
                st.success(f"✅ {est_levels} niveles de {level_dur} min generados. Podés editarlos en tab Ciegas.")
                st.rerun()

            st.markdown("<hr style='border-color:#1f2937;margin:1rem 0;'>", unsafe_allow_html=True)
            st.markdown("#### 📁 Plantillas guardadas")
            templates = st.session_state.get("blind_templates", get_default_blind_templates())
            if not templates:
                templates = get_default_blind_templates()
            tc1, tc2 = st.columns([3, 1])
            with tc1:
                sel_tpl = st.selectbox("Plantilla", list(templates.keys()), key="tpl_sel")
            with tc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("📂 Cargar", use_container_width=True, key="tpl_load"):
                    st.session_state.blind_levels = list(templates[sel_tpl])
                    add_alert(f"📂 Plantilla '{sel_tpl}' cargada"); save_state(); st.rerun()
            sc1, sc2 = st.columns([3, 1])
            with sc1:
                new_tpl_name = st.text_input("Guardar estructura actual como plantilla", placeholder="Nombre de la plantilla...", key="tpl_new_name")
            with sc2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("💾 Guardar", use_container_width=True, key="tpl_save"):
                    if new_tpl_name.strip():
                        templates[new_tpl_name.strip()] = list(st.session_state.blind_levels)
                        st.session_state.blind_templates = templates
                        save_state(); st.success(f"✅ Guardada"); st.rerun()
            # Delete template
            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                del_tpl = st.selectbox("Eliminar plantilla", list(templates.keys()), key="tpl_del_sel")
            with del_col2:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🗑️ Eliminar", use_container_width=True, key="tpl_del"):
                    if del_tpl in templates:
                        del templates[del_tpl]
                        st.session_state.blind_templates = templates
                        save_state(); st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with wiz2:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">💸 WIZARD DE DISTRIBUCIÓN DE PREMIOS</div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#9ca3af;font-size:0.9rem;'>Indicá cuántos jugadores pagan y el sistema propone porcentajes. Podés editarlos después en la tab Premios.</p>", unsafe_allow_html=True)

            pw1, pw2 = st.columns(2)
            with pw1:
                n_now = len(st.session_state.players)
                payout_n = st.number_input("Lugares pagados", min_value=1, max_value=max(1, n_now), value=min(3, max(1, n_now)), step=1, key="pwn")
            with pw2:
                payout_style = st.selectbox("Estilo de distribución", ["Top Heavy (más para 1°)", "Gradual (estándar)", "Plana (igualitaria)"], key="pwst")

            if st.button("💡 Proponer distribución", use_container_width=True, type="primary", key="pw_prop"):
                import math as _math
                n = int(payout_n)
                exp = {"Top Heavy (más para 1°)": 1.8, "Gradual (estándar)": 1.3, "Plana (igualitaria)": 0.7}.get(payout_style, 1.3)
                weights = [1 / (i+1)**exp for i in range(n)]
                total_w = sum(weights)
                pcts = [round(w/total_w*100, 3) for w in weights]
                pcts[0] = round(pcts[0] + (100.0 - sum(pcts)), 3)
                brackets = st.session_state.prize_percentages
                bracket_keys = sorted(brackets.keys(), key=lambda x: int(x))
                best_key = bracket_keys[-1]
                for key in bracket_keys:
                    if n_now <= int(key): best_key = key; break
                updated = dict(st.session_state.prize_percentages)
                updated[best_key] = [{"place": i+1, "pct": pcts[i]} for i in range(n)]
                st.session_state.prize_percentages = updated
                save_state()
                eff_pool = effective_prize_pool()
                st.success(f"✅ Distribución para {n} lugares aplicada:")
                for i, pct in enumerate(pcts):
                    medals = ["🥇", "🥈", "🥉"]
                    label = medals[i] if i < 3 else f"{i+1}°"
                    st.markdown(f"**{label}** — {pct:.1f}% → **${int(eff_pool*pct/100):,}**")
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        with wiz3:
            st.markdown('<div class="panel">', unsafe_allow_html=True)
            st.markdown('<div class="panel-title">👤 BASE DE JUGADORES — PERFILES HISTÓRICOS</div>', unsafe_allow_html=True)
            st.markdown("<p style='color:#9ca3af;font-size:0.9rem;'>Perfiles persistentes entre torneos. Al agregar jugadores con el mismo nombre, se vinculan automáticamente.</p>", unsafe_allow_html=True)

            player_db = st.session_state.get("player_db", {})

            if st.session_state.players:
                if st.button("📥 Registrar resultados de este torneo", use_container_width=True, type="primary", key="reg_res"):
                    eff_pool_db = effective_prize_pool()
                    sorted_active_db = sorted([p for p in st.session_state.players if p["status"] == "active"], key=lambda x: -x["chips"])
                    elim_sorted_db   = sorted([p for p in st.session_state.players if p["status"] == "eliminated"], key=lambda x: x.get("position", 999))
                    all_sorted_db = sorted_active_db + list(reversed(elim_sorted_db))
                    payouts_db = calculate_payouts_fixed(eff_pool_db, len(st.session_state.players))
                    payout_map_db = {p["place"]: p["amount"] for p in payouts_db}
                    for pos, player in enumerate(all_sorted_db):
                        name = player["name"]
                        if name not in player_db:
                            player_db[name] = {"torneos": 0, "wins": 0, "final_tables": 0, "sum_positions": 0, "total_won": 0}
                        db_e = player_db[name]
                        db_e["torneos"]       = db_e.get("torneos", 0) + 1
                        db_e["sum_positions"] = db_e.get("sum_positions", 0) + (pos + 1)
                        if pos == 0: db_e["wins"] = db_e.get("wins", 0) + 1
                        if pos < 3:  db_e["final_tables"] = db_e.get("final_tables", 0) + 1
                        db_e["total_won"] = db_e.get("total_won", 0) + payout_map_db.get(pos+1, 0)
                    st.session_state.player_db = player_db
                    save_state()
                    st.success(f"✅ {len(st.session_state.players)} jugadores registrados."); st.rerun()

            st.markdown("<hr style='border-color:#1f2937;margin:0.8rem 0;'>", unsafe_allow_html=True)
            if player_db:
                search_db = st.text_input("🔍 Buscar en la base", placeholder="Nombre...", key="db_srch")
                rows_db = []
                for name, stats in player_db.items():
                    if search_db.strip().lower() and search_db.strip().lower() not in name.lower(): continue
                    t = stats.get("torneos", 0)
                    rows_db.append({
                        "Jugador": name, "Torneos": t,
                        "Ganados": stats.get("wins", 0),
                        "Final Tables": stats.get("final_tables", 0),
                        "Pos. Prom.": f"{stats.get('sum_positions',0)/t:.1f}" if t else "—",
                        "Total ganado": f"${stats.get('total_won',0):,}",
                    })
                rows_db.sort(key=lambda x: x["Ganados"], reverse=True)
                if rows_db:
                    st.dataframe(pd.DataFrame(rows_db), use_container_width=True, hide_index=True)
                if st.button("🗑️ Limpiar base de jugadores", key="db_clear"):
                    st.session_state.player_db = {}; save_state(); st.rerun()
            else:
                st.info("Base vacía. Completá torneos y registrá resultados para generar historial.")
            st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB: MESAS
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "🪑 Mesas":
    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🪑 GESTIÓN DE MESAS</div>', unsafe_allow_html=True)
    active_players = [p for p in st.session_state.players if p["status"] == "active"]
    n_active = len(active_players)
    table_size = st.session_state.get("table_size", 9)
    mc1, mc2, mc3 = st.columns(3)
    with mc1:
        new_ts = st.number_input("Jugadores por mesa", min_value=2, max_value=10, value=table_size, step=1, key="ts_inp")
        if new_ts != table_size:
            st.session_state.table_size = new_ts; save_state()
    with mc2:
        n_tables = max(1, -(-n_active // table_size)) if n_active > 0 else 0
        st.metric("Mesas necesarias", n_tables)
    with mc3:
        seats_free = n_tables * table_size - n_active if n_active > 0 else 0
        st.metric("Asientos libres", seats_free)
    st.markdown('</div>', unsafe_allow_html=True)

    if not active_players:
        st.info("No hay jugadores activos.")
    else:
        import random as _rnd
        ba1, ba2 = st.columns(2)
        with ba1:
            if st.button("🎲 Asignar mesas aleatoriamente", use_container_width=True, type="primary", key="mesa_rnd"):
                shuffled = _rnd.sample(active_players, len(active_players))
                for i, p in enumerate(shuffled):
                    for pp in st.session_state.players:
                        if pp["id"] == p["id"]: pp["seat"] = (i // table_size) + 1
                add_alert(f"🎲 Mesas asignadas aleatoriamente — {n_tables} mesas"); save_state(); st.rerun()
        with ba2:
            if st.button("⚖️ Balancear mesas", use_container_width=True, key="mesa_bal"):
                sorted_p_m = sorted(active_players, key=lambda x: x["seat"])
                for i, p in enumerate(sorted_p_m):
                    for pp in st.session_state.players:
                        if pp["id"] == p["id"]: pp["seat"] = (i % n_tables) + 1
                add_alert("⚖️ Mesas balanceadas"); save_state(); st.rerun()

        tables_dict = {}
        for p in active_players:
            tables_dict.setdefault(p.get("seat", 1), []).append(p)

        for tnum in sorted(tables_dict.keys()):
            pts = tables_dict[tnum]
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:1px solid #d4af37;
                        border-radius:12px;padding:1rem 1.2rem;margin-bottom:0.8rem;">
                <div style="font-family:'Bebas Neue',cursive;font-size:1.3rem;color:#d4af37;letter-spacing:3px;margin-bottom:0.6rem;">
                    🪑 MESA {tnum} — {len(pts)} jugadores
                </div>""", unsafe_allow_html=True)
            pcols = st.columns(min(len(pts), 5))
            for i, p in enumerate(pts):
                with pcols[i % 5]:
                    mr = m_ratio(p["chips"])
                    mr_color = "#22c55e" if mr >= 10 else "#f97316" if mr >= 5 else "#ef4444"
                    st.markdown(f"""
                    <div style="background:#111827;border:1px solid #374151;border-radius:8px;
                                padding:0.5rem 0.4rem;text-align:center;margin-bottom:0.3rem;">
                        <div style="font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;
                                    color:#f0ead6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{p['name']}</div>
                        <div style="font-family:'Share Tech Mono',monospace;font-size:0.9rem;color:#a78bfa;">{p['chips']:,}</div>
                        <div style="font-size:0.75rem;color:{mr_color};">M={mr:.1f}</div>
                    </div>""", unsafe_allow_html=True)
                    new_seat = st.number_input("→Mesa", min_value=1, max_value=20, value=p["seat"],
                                               key=f"mv_{p['id']}", label_visibility="collapsed")
                    if new_seat != p["seat"]:
                        for pp in st.session_state.players:
                            if pp["id"] == p["id"]: pp["seat"] = new_seat
                        add_alert(f"↔️ {p['name']} → Mesa {new_seat}"); save_state(); st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
# TAB: ESTADÍSTICAS
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "📊 Estadísticas":
    import math as _math
    active_players = [p for p in st.session_state.players if p["status"] == "active"]
    elim_players   = [p for p in st.session_state.players if p["status"] == "eliminated"]
    n_active = len(active_players)

    total_secs_p = int(st.session_state.get("total_elapsed_seconds", 0))
    th_s = total_secs_p // 3600
    tm_s = (total_secs_p % 3600) // 60
    ts_s = total_secs_p % 60

    future_lvls = st.session_state.blind_levels[st.session_state.current_level:]
    avg_lvl_dur = sum(b.get("duration", 15) for b in future_lvls) / max(len(future_lvls), 1) if future_lvls else 15
    remaining_lvls = len(future_lvls)
    est_min = remaining_lvls * avg_lvl_dur
    est_end = datetime.now() + timedelta(minutes=est_min)

    def stat_box_s(label, value, color="#d4af37", sub=""):
        return f"""<div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:1px solid #1f2937;
                    border-radius:12px;padding:1rem;text-align:center;">
            <div style="font-size:0.75rem;letter-spacing:2px;color:#b0b8c8;font-weight:700;margin-bottom:0.3rem;">{label}</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:1.8rem;color:{color};">{value}</div>
            {"" if not sub else f'<div style="font-size:0.8rem;color:#6b7280;margin-top:0.2rem;">{sub}</div>'}
        </div>"""

    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📊 ESTADÍSTICAS DEL TORNEO</div>', unsafe_allow_html=True)
    s1,s2,s3,s4,s5 = st.columns(5)
    total_rebuys_s = sum(p.get("rebuys",0) for p in st.session_state.players)
    total_addons_s = sum(p.get("addons",0) for p in st.session_state.players)
    with s1: st.markdown(stat_box_s("ACTIVOS", n_active, "#22c55e"), unsafe_allow_html=True)
    with s2: st.markdown(stat_box_s("ELIMINADOS", len(elim_players), "#ef4444"), unsafe_allow_html=True)
    with s3: st.markdown(stat_box_s("REBUYS / ADD-ONS", f"{total_rebuys_s} / {total_addons_s}", "#f0d060"), unsafe_allow_html=True)
    with s4: st.markdown(stat_box_s("TIEMPO JUGADO", f"{th_s:02d}:{tm_s:02d}:{ts_s:02d}", "#60a5fa"), unsafe_allow_html=True)
    with s5: st.markdown(stat_box_s("FIN ESTIMADO", est_end.strftime("%H:%M"), "#34d399", sub=f"~{int(est_min)} min"), unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    if active_players:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📈 DISTRIBUCIÓN DE STACKS</div>', unsafe_allow_html=True)
        sorted_p_s = sorted(active_players, key=lambda x: -x["chips"])
        total_chips = sum(p["chips"] for p in active_players)
        avg_s_v = total_chips // n_active if n_active else 0
        max_s_v = sorted_p_s[0]["chips"] if sorted_p_s else 0
        min_s_v = sorted_p_s[-1]["chips"] if sorted_p_s else 0
        med_s_v = sorted_p_s[len(sorted_p_s)//2]["chips"] if sorted_p_s else 0
        sc1,sc2,sc3,sc4,sc5 = st.columns(5)
        with sc1: st.markdown(stat_box_s("CHIPS EN JUEGO", f"{total_chips:,}", "#d4af37"), unsafe_allow_html=True)
        with sc2: st.markdown(stat_box_s("STACK MÁX.", f"{max_s_v:,}", "#22c55e"), unsafe_allow_html=True)
        with sc3: st.markdown(stat_box_s("PROMEDIO", f"{avg_s_v:,}", "#a78bfa"), unsafe_allow_html=True)
        with sc4: st.markdown(stat_box_s("MEDIANA", f"{med_s_v:,}", "#60a5fa"), unsafe_allow_html=True)
        with sc5: st.markdown(stat_box_s("STACK MÍN.", f"{min_s_v:,}", "#f97316"), unsafe_allow_html=True)

        chart_rows = []
        for p in sorted_p_s[:15]:
            pct = (p["chips"] / max_s_v * 100) if max_s_v > 0 else 0
            mr = m_ratio(p["chips"])
            mr_c = "#22c55e" if mr >= 10 else "#f97316" if mr >= 5 else "#ef4444"
            chart_rows.append(f"""
            <div style="display:flex;align-items:center;gap:0.8rem;margin-bottom:0.4rem;">
                <div style="width:130px;font-family:'Rajdhani',sans-serif;font-size:1rem;font-weight:700;
                            color:#f0ead6;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">{p['name']}</div>
                <div style="flex:1;background:#1f2937;border-radius:4px;height:22px;">
                    <div style="width:{pct:.1f}%;background:linear-gradient(90deg,#d4af37,#f0d060);
                                height:100%;border-radius:4px;min-width:4px;"></div>
                </div>
                <div style="width:90px;font-family:'Share Tech Mono',monospace;font-size:0.9rem;color:#a78bfa;text-align:right;">{p['chips']:,}</div>
                <div style="width:55px;font-size:0.8rem;color:{mr_c};text-align:right;">M={mr:.1f}</div>
            </div>""")
        st.markdown("".join(chart_rows), unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    player_db_s = st.session_state.get("player_db", {})
    if player_db_s:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🏅 RANKING HISTÓRICO</div>', unsafe_allow_html=True)
        rank_rows = []
        for name, stats in player_db_s.items():
            t = stats.get("torneos", 0)
            if t == 0: continue
            rank_rows.append({
                "Jugador": name, "Torneos": t,
                "Ganados": stats.get("wins", 0),
                "Final Tables": stats.get("final_tables", 0),
                "Pos. Prom.": f"{stats.get('sum_positions',0)/t:.1f}",
                "Total ganado": f"${stats.get('total_won',0):,}",
            })
        rank_rows.sort(key=lambda x: x["Ganados"], reverse=True)
        if rank_rows:
            st.dataframe(pd.DataFrame(rank_rows), use_container_width=True, hide_index=True)
        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════════
elif nav == "📋 Historial":
    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">📋 LOG DE EVENTOS DEL TORNEO</div>', unsafe_allow_html=True)

    if not st.session_state.alerts:
        st.info("No hay eventos registrados aún.")
    else:
        for alert in reversed(st.session_state.alerts):
            kind = alert.get("kind", "info")
            colors = {
                "info":     ("#1e3a5f", "#60a5fa"),
                "warning":  ("#3d2406", "#f59e0b"),
                "critical": ("#3d0606", "#ef4444"),
                "level_up": ("#1e3a28", "#22c55e"),
            }
            bg, fg = colors.get(kind, colors["info"])
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:0.8rem; background:{bg}; border:1px solid {fg}33;
                        border-left:3px solid {fg}; border-radius:6px; padding:0.5rem 0.8rem; margin-bottom:0.4rem;">
                <span style="font-family:'Share Tech Mono',monospace; font-size:0.75rem; color:#6b7280; white-space:nowrap;">{alert['time']}</span>
                <span style="font-family:'Rajdhani',sans-serif; font-size:0.95rem; color:{fg};">{alert['msg']}</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state.alerts:
        if st.button("🗑️ Limpiar historial"):
            st.session_state.alerts = []
            save_state()
            st.rerun()

    # Export
    if st.session_state.players or st.session_state.bets:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">📤 EXPORTAR DATOS</div>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.session_state.players:
                df_exp = pd.DataFrame(st.session_state.players)
                csv_players = df_exp.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Exportar Jugadores (CSV)",
                    data=csv_players,
                    file_name=f"jugadores_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with c2:
            if st.session_state.bets:
                df_bets_exp = pd.DataFrame(st.session_state.bets)
                csv_bets = df_bets_exp.to_csv(index=False).encode("utf-8")
                st.download_button(
                    "⬇️ Exportar Apuestas (CSV)",
                    data=csv_bets,
                    file_name=f"apuestas_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        st.markdown('</div>', unsafe_allow_html=True)