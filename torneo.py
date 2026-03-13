import streamlit as st
import pandas as pd
import time
import json
from datetime import datetime, timedelta
import random

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
    font-size: 1rem !important;
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
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def get_default_blinds():
    return [
        {"level": 1,  "small": 25,   "big": 50,    "ante": 0,    "duration": 15},
        {"level": 2,  "small": 50,   "big": 100,   "ante": 0,    "duration": 15},
        {"level": 3,  "small": 75,   "big": 150,   "ante": 25,   "duration": 15},
        {"level": 4,  "small": 100,  "big": 200,   "ante": 25,   "duration": 15},
        {"level": 5,  "small": 150,  "big": 300,   "ante": 50,   "duration": 15},
        {"level": 6,  "small": 200,  "big": 400,   "ante": 50,   "duration": 15},
        {"level": 7,  "small": 300,  "big": 600,   "ante": 75,   "duration": 15},
        {"level": 8,  "small": 400,  "big": 800,   "ante": 100,  "duration": 15},
        {"level": 9,  "small": 500,  "big": 1000,  "ante": 100,  "duration": 20},
        {"level": 10, "small": 600,  "big": 1200,  "ante": 200,  "duration": 20},
        {"level": 11, "small": 800,  "big": 1600,  "ante": 200,  "duration": 20},
        {"level": 12, "small": 1000, "big": 2000,  "ante": 300,  "duration": 20},
        {"level": 13, "small": 1500, "big": 3000,  "ante": 400,  "duration": 20},
        {"level": 14, "small": 2000, "big": 4000,  "ante": 500,  "duration": 25},
        {"level": 15, "small": 3000, "big": 6000,  "ante": 1000, "duration": 25},
    ]

init_state()

# ─── HELPER FUNCTIONS ──────────────────────────────────────────────────────────
def get_active_players():
    return [p for p in st.session_state.players if p["status"] == "active"]

def get_eliminated_players():
    return [p for p in st.session_state.players if p["status"] == "eliminated"]

def total_prize_pool():
    total = sum(p["buy_ins"] * st.session_state.buy_in for p in st.session_state.players)
    total += sum(p["rebuys"] * st.session_state.rebuy_cost for p in st.session_state.players)
    return total

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
    if n_players == 2:
        return [
            {"place": 1, "pct": 70, "amount": int(prize_pool * 0.70)},
            {"place": 2, "pct": 30, "amount": int(prize_pool * 0.30)},
        ]
    if n_players <= 4:
        return [
            {"place": 1, "pct": 60, "amount": int(prize_pool * 0.60)},
            {"place": 2, "pct": 30, "amount": int(prize_pool * 0.30)},
            {"place": 3, "pct": 10, "amount": int(prize_pool * 0.10)},
        ]
    if n_players <= 8:
        return [
            {"place": 1, "pct": 50, "amount": int(prize_pool * 0.50)},
            {"place": 2, "pct": 30, "amount": int(prize_pool * 0.30)},
            {"place": 3, "pct": 20, "amount": int(prize_pool * 0.20)},
        ]
    return [
        {"place": 1, "pct": 45, "amount": int(prize_pool * 0.45)},
        {"place": 2, "pct": 25, "amount": int(prize_pool * 0.25)},
        {"place": 3, "pct": 15, "amount": int(prize_pool * 0.15)},
        {"place": 4, "pct": 10, "amount": int(prize_pool * 0.10)},
        {"place": 5, "pct": 5,  "amount": int(prize_pool * 0.05)},
    ]

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
    """Called every rerun to advance timer."""
    # Clear sound trigger from previous tick
    st.session_state.play_sound = None

    if st.session_state.timer_running and not st.session_state.break_active:
        now = time.time()
        delta = now - st.session_state.last_tick
        st.session_state.last_tick = now
        st.session_state.elapsed_seconds += delta
        st.session_state.total_elapsed_seconds = st.session_state.get("total_elapsed_seconds", 0) + delta

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
        now = time.time()
        delta = now - st.session_state.last_tick
        st.session_state.last_tick = now
        st.session_state.break_elapsed += delta
        break_remaining = st.session_state.break_duration * 60 - st.session_state.break_elapsed
        if break_remaining <= 0:
            st.session_state.break_active = False
            st.session_state.timer_running = True
            st.session_state.play_sound = "warning"
            add_alert("▶️ Descanso terminado — Continúa el juego!", "info")

def advance_level(auto=False):
    if st.session_state.current_level < len(st.session_state.blind_levels) - 1:
        st.session_state.current_level += 1
        st.session_state.elapsed_seconds = 0
        st.session_state.last_tick = time.time()
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
        ["🕐 Torneo en Vivo", "👥 Jugadores", "💰 Apuestas", "🏆 Premios", "⚙️ Configuración", "📋 Historial"],
        label_visibility="collapsed"
    )

    st.divider()

    # Quick stats
    active = get_active_players()
    total_players = len(st.session_state.players)
    pool = total_prize_pool()

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
    if st.button("🔄 Actualizar", use_container_width=True):
        st.rerun()

    # Sound control
    st.divider()
    mute_label = "🔇 Sonido: OFF" if st.session_state.sound_muted else "🔔 Sonido: ON"
    if st.button(mute_label, use_container_width=True):
        st.session_state.sound_muted = not st.session_state.sound_muted
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

_logo_path = "poker.jpg"
_logo_b64 = ""
if os.path.exists(_logo_path):
    with open(_logo_path, "rb") as _f:
        _logo_b64 = base64.b64encode(_f.read()).decode()

if _logo_b64:
    st.markdown(f"""
    <div style="text-align:center; padding:0.8rem 0 0.4rem; border-bottom:2px solid #d4af37; margin-bottom:1.5rem;">
        <img src="data:image/jpeg;base64,{_logo_b64}"
             style="max-height:130px; max-width:100%; object-fit:contain;
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
    }

    js_code = scripts.get(sound_type, "")
    if js_code:
        import streamlit.components.v1 as components
        components.html(f"<script>{js_code}</script>", height=0)

# Fire sound if triggered this tick
play_sound_js(
    st.session_state.get("play_sound"),
    st.session_state.get("sound_muted", False)
)

# ════════════════════════════════════════════════════════════════════════════════
# TAB: TORNEO EN VIVO
# ════════════════════════════════════════════════════════════════════════════════
if nav == "🕐 Torneo en Vivo":
    remaining = time_remaining()
    total_secs = level_seconds()
    progress = 1.0 - (remaining / total_secs) if total_secs > 0 else 0

    # Alerts
    if remaining <= 30 and st.session_state.timer_running and not st.session_state.break_active:
        st.markdown('<div class="alert-banner">🚨 ¡CAMBIO DE CIEGAS EN MENOS DE 30 SEGUNDOS! 🚨</div>', unsafe_allow_html=True)
    elif remaining <= 60 and st.session_state.timer_running and not st.session_state.break_active:
        st.markdown('<div class="alert-banner" style="background: linear-gradient(90deg,#92400e,#f59e0b,#92400e);">⚠️ ÚLTIMO MINUTO — CAMBIO DE CIEGAS PRÓXIMO ⚠️</div>', unsafe_allow_html=True)

    if st.session_state.break_active:
        break_rem = st.session_state.break_duration * 60 - st.session_state.break_elapsed
        st.markdown(f'<div class="info-banner">☕ DESCANSO EN CURSO — {fmt_time(max(0, break_rem))} restantes</div>', unsafe_allow_html=True)

    # Main timer + blinds
    col_timer, col_blinds = st.columns([1, 1])

    with col_timer:
        st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
        b = current_blind()

        # Level
        st.markdown(f"""
        <div style="text-align:center; margin-bottom:0.3rem;">
            <span class="level-badge">NIVEL {b['level']}</span>
            <span style="font-family:'Rajdhani',sans-serif; color:#9ca3af; font-size:0.85rem; margin-left:0.5rem; letter-spacing:2px;">DE {len(st.session_state.blind_levels)}</span>
        </div>
        """, unsafe_allow_html=True)

        # Timer
        timer_class = "timer-display"
        if remaining <= 30 and st.session_state.timer_running:
            timer_class += " timer-critical"
        elif remaining <= 60 and st.session_state.timer_running:
            timer_class += " timer-warning"

        st.markdown(f'<div class="{timer_class}">{fmt_time(remaining)}</div>', unsafe_allow_html=True)

        # Progress bar
        st.progress(progress)

        # Controls
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            if st.session_state.timer_running and not st.session_state.break_active:
                if st.button("⏸ Pausa", use_container_width=True):
                    st.session_state.timer_running = False
                    add_alert("⏸ Torneo pausado")
                    st.rerun()
            else:
                label = "▶ Reanudar" if st.session_state.tournament_started else "▶ Iniciar"
                if st.button(label, use_container_width=True):
                    st.session_state.timer_running = True
                    st.session_state.tournament_started = True
                    st.session_state.last_tick = time.time()
                    if not st.session_state.break_active:
                        add_alert("▶️ Torneo iniciado/reanudado")
                    st.rerun()
        with c2:
            if st.button("⏭ Avanzar", use_container_width=True):
                advance_level()
                st.rerun()
        with c3:
            if st.button("⏮ Retroceder", use_container_width=True):
                if st.session_state.current_level > 0:
                    st.session_state.current_level -= 1
                    st.session_state.elapsed_seconds = 0
                    st.session_state.last_tick = time.time()
                    add_alert(f"⏮ Volviendo al nivel {st.session_state.current_level + 1}")
                    st.rerun()
        with c4:
            if st.button("☕ Descanso", use_container_width=True):
                st.session_state.break_active = True
                st.session_state.break_elapsed = 0
                st.session_state.timer_running = False
                st.session_state.last_tick = time.time()
                add_alert(f"☕ Descanso de {st.session_state.break_duration} minutos iniciado")
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

    with col_blinds:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">♠ ESTRUCTURA DE CIEGAS</div>', unsafe_allow_html=True)

        nb = next_blind()
        st.markdown(f"""
        <div class="blind-display">
            <div class="blind-box">
                <div class="blind-label">Small Blind</div>
                <div class="blind-value">{b['small']:,}</div>
            </div>
            <div class="blind-box">
                <div class="blind-label">Big Blind</div>
                <div class="blind-value">{b['big']:,}</div>
            </div>
            <div class="blind-box">
                <div class="blind-label">Ante</div>
                <div class="blind-value">{b['ante']:,}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if nb:
            st.markdown(f"""
            <div style="text-align:center; margin-top:0.5rem; padding:0.5rem; background:rgba(212,175,55,0.05); border:1px dashed #374151; border-radius:8px;">
                <span style="font-family:'Rajdhani',sans-serif; font-size:0.75rem; letter-spacing:2px; color:#9ca3af;">PRÓXIMO NIVEL</span><br>
                <span style="font-family:'Share Tech Mono',monospace; color:#9ca3af; font-size:0.9rem;">
                    SB: {nb['small']:,} | BB: {nb['big']:,} | Ante: {nb['ante']:,}
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

        # Metrics
        active_p = get_active_players()
        total_chips = sum(p["chips"] for p in active_p) if active_p else 0
        n_active = len(active_p)
        n_total = len(st.session_state.players)
        eliminated = n_total - n_active

        st.markdown(f"""
        <div class="metric-row">
            <div class="metric-card">
                <span class="metric-value">{n_active}</span>
                <div class="metric-label">Jugadores activos</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">{eliminated}</span>
                <div class="metric-label">Eliminados</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">{avg_stack():,}</span>
                <div class="metric-label">Stack Prom.</div>
            </div>
            <div class="metric-card">
                <span class="metric-value">${total_prize_pool():,}</span>
                <div class="metric-label">Prize Pool</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Chip leader
        leader = chip_leader()
        if leader:
            m = m_ratio(leader["chips"])
            m_color = "#22c55e" if m >= 20 else ("#f59e0b" if m >= 10 else "#ef4444")
            avg_m = m_ratio(avg_stack())
            avg_m_color = "#22c55e" if avg_m >= 20 else ("#f59e0b" if avg_m >= 10 else "#ef4444")
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#1e3a28,#0d1f14); border:1px solid #d4af37;
                        border-radius:10px; padding:0.7rem 1rem; margin-top:0.5rem;">
                <div style="font-family:'Bebas Neue',cursive; color:#d4af37; letter-spacing:2px; font-size:1rem;">
                    👑 CHIP LEADER
                </div>
                <div style="display:flex; justify-content:space-between; align-items:center; margin-top:0.3rem;">
                    <span style="font-family:'Rajdhani',sans-serif; font-size:1.1rem; font-weight:700; color:#f0ead6;">
                        {leader['name']}
                    </span>
                    <span style="font-family:'Share Tech Mono',monospace; color:#d4af37; font-size:1.1rem;">
                        {leader['chips']:,} chips
                    </span>
                </div>
                <div style="display:flex; gap:1rem; margin-top:0.4rem;">
                    <span style="font-size:0.78rem; color:#9ca3af;">
                        M-ratio líder: <span style="color:{m_color}; font-weight:700;">{m:.1f}</span>
                    </span>
                    <span style="font-size:0.78rem; color:#9ca3af;">
                        M-ratio prom: <span style="color:{avg_m_color}; font-weight:700;">{avg_m:.1f}</span>
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Blind levels table — custom HTML via components.html to avoid escaping issues
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
            row_style   = "background:linear-gradient(90deg,rgba(212,175,55,0.18),rgba(212,175,55,0.06) 60%,transparent); border-left:4px solid #d4af37; opacity:1;"
            lvl_color   = "#d4af37"
            num_color   = "#f0d060"
            ante_color  = "#f0d060"
            dur_color   = "#d4af37"
            badge       = '<span style="background:#d4af37;color:#000;font-size:0.65rem;font-weight:900;letter-spacing:1px;padding:2px 8px;border-radius:10px;">▶ ACTUAL</span>'
        elif is_past:
            row_style   = "background:transparent; border-left:4px solid #1f2937; opacity:0.4;"
            lvl_color   = "#374151"
            num_color   = "#374151"
            ante_color  = "#374151"
            dur_color   = "#374151"
            badge       = '<span style="color:#22c55e;font-size:1rem;">✓</span>'
        elif is_next:
            row_style   = "background:linear-gradient(90deg,rgba(37,99,235,0.12),transparent); border-left:4px solid #2563eb; opacity:0.92;"
            lvl_color   = "#93c5fd"
            num_color   = "#bfdbfe"
            ante_color  = "#93c5fd"
            dur_color   = "#93c5fd"
            badge       = '<span style="color:#3b82f6;font-size:0.68rem;letter-spacing:1px;">PRÓXIMO</span>'
        else:
            row_style   = "background:transparent; border-left:4px solid transparent; opacity:0.65;"
            lvl_color   = "#6b7280"
            num_color   = "#9ca3af"
            ante_color  = "#6b7280"
            dur_color   = "#6b7280"
            badge       = ""

        rows_html += (
            f'<tr style="{row_style}">'
            f'<td style="padding:8px 10px;color:{lvl_color};font-family:Bebas Neue,cursive;font-size:1.1rem;letter-spacing:2px;text-align:center;width:55px;">{bl["level"]}</td>'
            f'<td style="padding:8px 10px;text-align:center;width:80px;">{badge}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{num_color};font-size:1rem;text-align:right;">{bl["small"]:,}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{num_color};font-size:1rem;text-align:right;font-weight:700;">{bl["big"]:,}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{ante_color};font-size:0.95rem;text-align:right;">{ante_str}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{dur_color};font-size:0.85rem;text-align:center;width:80px;">{dur} min</td>'
            f'</tr>'
        )

    full_html = f"""
    <!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Rajdhani:wght@600&display=swap" rel="stylesheet">
    <style>
        body {{ margin:0; padding:0; background:transparent; }}
        .wrap {{ overflow-y:auto; max-height:330px; border-radius:8px;
                 border:1px solid #1f2937; background:#0a0a0a;
                 scrollbar-width:thin; scrollbar-color:#374151 #0a0a0a; }}
        table {{ width:100%; border-collapse:collapse; }}
        thead tr {{ position:sticky; top:0; background:#111827;
                    border-bottom:2px solid rgba(212,175,55,0.3); }}
        th {{ padding:8px 14px; font-family:Rajdhani,sans-serif; font-size:0.7rem;
              letter-spacing:2px; color:#6b7280; text-transform:uppercase; }}
        th:first-child {{ text-align:center; }}
        th:nth-child(3), th:nth-child(4), th:nth-child(5) {{ text-align:right; }}
        th:last-child {{ text-align:center; }}
        tr {{ transition:background 0.2s; }}
        td {{ border-bottom:1px solid rgba(255,255,255,0.04); }}
        .legend {{ display:flex; gap:20px; margin-top:8px; padding:0 4px;
                   font-family:Rajdhani,sans-serif; font-size:0.78rem; color:#6b7280; }}
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

    components.html(full_html, height=380, scrolling=False)
    st.markdown('</div>', unsafe_allow_html=True)

    # Auto-refresh if running
    if st.session_state.timer_running or st.session_state.break_active:
        time.sleep(1)
        st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB: JUGADORES
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "👥 Jugadores":
    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">➕ AGREGAR JUGADOR</div>', unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns([3, 2, 2, 1])
    with c1:
        new_name = st.text_input("Nombre del Jugador", placeholder="Ej: Juan García", key="new_player_name")
    with c2:
        new_seat = st.number_input("Mesa/Asiento", min_value=1, max_value=20, value=1, key="new_seat")
    with c3:
        new_chips = st.number_input("Chips iniciales", min_value=1000, value=st.session_state.starting_chips, step=1000, key="new_chips")
    with c4:
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
                    "rebuys": 0,
                    "position": None,
                    "bounty": 0,
                    "added_at": datetime.now().strftime("%H:%M"),
                })
                add_alert(f"👤 {new_name.strip()} se unió al torneo (Mesa {new_seat})")
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
                            "rebuys": 0,
                            "position": None,
                            "bounty": 0,
                            "added_at": datetime.now().strftime("%H:%M"),
                        })
                        count += 1
                add_alert(f"📂 {count} jugadores importados desde CSV")
                st.success(f"✅ {count} jugadores importados correctamente.")
                st.rerun()
            except Exception as e:
                st.error(f"Error al leer CSV: {e}")

    # Players table
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown(f'<div class="panel-title">👥 JUGADORES ({len(st.session_state.players)})</div>', unsafe_allow_html=True)

    if not st.session_state.players:
        st.info("No hay jugadores registrados. Agregá jugadores arriba.")
    else:
        # Sort: active first, then by chips desc
        sorted_players = sorted(st.session_state.players, key=lambda p: (0 if p["status"]=="active" else 1, -p["chips"]))

        for i, p in enumerate(sorted_players):
            row_bg = "rgba(26,122,66,0.1)" if p["status"] == "active" else "rgba(100,0,0,0.1)"
            status_color = "#22c55e" if p["status"] == "active" else "#ef4444"
            status_icon = "🟢" if p["status"] == "active" else "💀"
            rank = i + 1 if p["status"] == "active" else ""

            with st.container():
                c1, c2, c3, c4, c5, c6, c7, c8 = st.columns([0.5, 3, 1.5, 2, 1.5, 1.5, 1.5, 2])
                with c1:
                    st.markdown(f"<span style='font-size:1.2rem;'>{status_icon}</span>", unsafe_allow_html=True)
                with c2:
                    st.markdown(f"<span style='font-family:Rajdhani,sans-serif;font-size:1rem;font-weight:700;color:{'#f0ead6' if p['status']=='active' else '#6b7280'};'>{p['name']}</span>", unsafe_allow_html=True)
                with c3:
                    st.markdown(f"<span style='font-size:0.8rem;color:#9ca3af;'>Mesa {p['seat']}</span>", unsafe_allow_html=True)
                with c4:
                    if p["status"] == "active":
                        new_chips = st.number_input("", value=p["chips"], step=500, key=f"chips_{p['id']}", label_visibility="collapsed")
                        if new_chips != p["chips"]:
                            for pp in st.session_state.players:
                                if pp["id"] == p["id"]:
                                    pp["chips"] = new_chips
                    else:
                        st.markdown(f"<span style='color:#6b7280;font-family:Share Tech Mono,monospace;'>ELIMINADO</span>", unsafe_allow_html=True)
                with c5:
                    st.markdown(f"<span style='font-size:0.8rem;color:#9ca3af;'>Buy-ins: {p['buy_ins']}</span>", unsafe_allow_html=True)
                with c6:
                    st.markdown(f"<span style='font-size:0.8rem;color:#9ca3af;'>Rebuys: {p['rebuys']}</span>", unsafe_allow_html=True)
                with c7:
                    if p["status"] == "active" and st.session_state.rebuy_allowed:
                        if st.button("🔄 Rebuy", key=f"rebuy_{p['id']}", use_container_width=True):
                            for pp in st.session_state.players:
                                if pp["id"] == p["id"]:
                                    pp["chips"] += st.session_state.rebuy_chips
                                    pp["rebuys"] += 1
                            add_alert(f"🔄 {p['name']} hizo rebuy (+{st.session_state.rebuy_chips:,} chips)")
                            st.rerun()
                with c8:
                    if p["status"] == "active":
                        if st.button("💀 Eliminar", key=f"elim_{p['id']}", use_container_width=True):
                            n_active_before = len(get_active_players())
                            pos = n_active_before  # position = current count
                            for pp in st.session_state.players:
                                if pp["id"] == p["id"]:
                                    pp["status"] = "eliminated"
                                    pp["chips"] = 0
                                    pp["position"] = pos
                            add_alert(f"💀 {p['name']} eliminado en posición #{pos}")
                            st.rerun()
                    else:
                        if st.button("♻️ Restaurar", key=f"restore_{p['id']}", use_container_width=True):
                            for pp in st.session_state.players:
                                if pp["id"] == p["id"]:
                                    pp["status"] = "active"
                                    pp["chips"] = st.session_state.starting_chips
                                    pp["position"] = None
                            st.rerun()

            st.divider()

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
            rows.append({
                "Pos": medals[i] if i < 3 else f"#{i+1}",
                "Jugador": p["name"],
                "Mesa": p["seat"],
                "Chips": f"{p['chips']:,}",
                "M-ratio": mr_str,
                "Buy-ins": p["buy_ins"],
                "Rebuys": p["rebuys"],
            })

        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
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
            st.rerun()


# ════════════════════════════════════════════════════════════════════════════════
# TAB: PREMIOS
# ════════════════════════════════════════════════════════════════════════════════
elif nav == "🏆 Premios":
    pool = total_prize_pool()
    n_players = len(st.session_state.players)

    st.markdown('<div class="panel panel-gold">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">🏆 PREMIO POOL & DISTRIBUCIÓN</div>', unsafe_allow_html=True)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; background:rgba(212,175,55,0.1); border:1px solid #d4af37; border-radius:10px;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:2.5rem; color:#d4af37;">${pool:,}</div>
            <div style="font-size:0.75rem; letter-spacing:2px; color:#9ca3af; margin-top:0.3rem;">PRIZE POOL TOTAL</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        buy_in_total = sum(p["buy_ins"] * st.session_state.buy_in for p in st.session_state.players)
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; background:rgba(37,99,235,0.1); border:1px solid #2563eb; border-radius:10px;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:2.5rem; color:#60a5fa;">${buy_in_total:,}</div>
            <div style="font-size:0.75rem; letter-spacing:2px; color:#9ca3af; margin-top:0.3rem;">BUY-INS TOTALES</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        rebuy_total = sum(p["rebuys"] * st.session_state.rebuy_cost for p in st.session_state.players)
        st.markdown(f"""
        <div style="text-align:center; padding:1rem; background:rgba(220,38,38,0.1); border:1px solid #dc2626; border-radius:10px;">
            <div style="font-family:'Share Tech Mono',monospace; font-size:2.5rem; color:#f87171;">${rebuy_total:,}</div>
            <div style="font-size:0.75rem; letter-spacing:2px; color:#9ca3af; margin-top:0.3rem;">REBUYS TOTALES</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

    # Payout distribution
    st.markdown('<div class="panel">', unsafe_allow_html=True)
    st.markdown('<div class="panel-title">💵 DISTRIBUCIÓN DE PREMIOS</div>', unsafe_allow_html=True)

    payouts = calculate_payouts_fixed(pool, n_players)
    place_styles = ["prize-1st", "prize-2nd", "prize-3rd"]
    place_labels = ["🥇 1er Lugar", "🥈 2do Lugar", "🥉 3er Lugar", "4to Lugar", "5to Lugar"]

    for i, p in enumerate(payouts):
        style = place_styles[i] if i < 3 else "prize-other"
        label = place_labels[i] if i < len(place_labels) else f"{p['place']}to Lugar"
        st.markdown(f"""
        <div class="prize-row {style}">
            <span>{label}</span>
            <span style="color:#9ca3af;">{p['pct']}%</span>
            <span style="font-family:'Share Tech Mono',monospace; color:#d4af37; font-size:1.1rem;">${p['amount']:,}</span>
        </div>
        """, unsafe_allow_html=True)

    if pool == 0:
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
    tab1, tab2, tab3 = st.tabs(["🎮 Torneo", "🕐 Ciegas", "🔔 Alertas"])

    with tab1:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🎮 CONFIGURACIÓN DEL TORNEO</div>', unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Nombre del Torneo", value=st.session_state.tournament_name)
            if name != st.session_state.tournament_name:
                st.session_state.tournament_name = name

            buy_in = st.number_input("Buy-in ($)", min_value=1, value=st.session_state.buy_in, step=5)
            if buy_in != st.session_state.buy_in:
                st.session_state.buy_in = buy_in

            starting = st.number_input("Chips iniciales", min_value=1000, value=st.session_state.starting_chips, step=1000)
            if starting != st.session_state.starting_chips:
                st.session_state.starting_chips = starting

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

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Resetear Torneo Completo", use_container_width=True, type="secondary"):
                st.session_state.players = []
                st.session_state.bets = []
                st.session_state.current_level = 0
                st.session_state.timer_running = False
                st.session_state.elapsed_seconds = 0
                st.session_state.tournament_started = False
                st.session_state.alerts = []
                st.session_state.break_active = False
                st.session_state.player_id_counter = 1
                add_alert("🔄 Torneo reseteado")
                st.rerun()

    with tab2:
        st.markdown('<div class="panel">', unsafe_allow_html=True)
        st.markdown('<div class="panel-title">🕐 ESTRUCTURA DE CIEGAS</div>', unsafe_allow_html=True)

        st.markdown("**Editar niveles de ciegas:**")
        blinds_data = []
        for b in st.session_state.blind_levels:
            blinds_data.append({
                "Nivel": b["level"],
                "Small Blind": b["small"],
                "Big Blind": b["big"],
                "Ante": b["ante"],
                "Duración (min)": b.get("duration", st.session_state.level_duration),
            })

        df_blinds = pd.DataFrame(blinds_data)
        edited = st.data_editor(
            df_blinds,
            use_container_width=True,
            hide_index=True,
            key="blinds_editor"
        )

        if st.button("💾 Guardar Estructura de Ciegas", use_container_width=True):
            new_blinds = []
            for _, row in edited.iterrows():
                new_blinds.append({
                    "level": int(row["Nivel"]),
                    "small": int(row["Small Blind"]),
                    "big": int(row["Big Blind"]),
                    "ante": int(row["Ante"]),
                    "duration": int(row["Duración (min)"]),
                })
            st.session_state.blind_levels = new_blinds
            st.success("✅ Estructura de ciegas actualizada!")
            st.rerun()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("📋 Cargar Estructura Estándar", use_container_width=True):
                st.session_state.blind_levels = get_default_blinds()
                st.rerun()
        with c2:
            if st.button("⚡ Cargar Estructura Turbo", use_container_width=True):
                turbo = get_default_blinds()
                for b in turbo:
                    b["duration"] = 8
                st.session_state.blind_levels = turbo
                st.rerun()

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


# ════════════════════════════════════════════════════════════════════════════════
# TAB: HISTORIAL
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