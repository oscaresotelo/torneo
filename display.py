"""
display.py  —  Pantalla del proyector / pantalla informativa
Ejecutar con:  streamlit run display.py --server.port 8502
Pantalla de control:  http://localhost:8501
Pantalla proyector:   http://localhost:8502
"""

import streamlit as st
import json, os, time, base64
from datetime import datetime

st.set_page_config(page_title="♠ POKER — Pantalla", page_icon="♠",
                   layout="wide", initial_sidebar_state="collapsed")

SAVE_FILE = "torneo_data.json"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Rajdhani:wght@400;600;700&family=Share+Tech+Mono&display=swap');
:root { --gold:#d4af37; --gold-light:#f0d060; --text:#f0ead6; --text-dim:#b0b8c8; }
html,body,[class*="css"] { font-family:'Rajdhani',sans-serif; color:var(--text); }
.stApp { background:radial-gradient(ellipse at top,#0d1f14 0%,#060d09 60%,#000 100%); background-attachment:fixed; }
section[data-testid="stSidebar"],header[data-testid="stHeader"],#MainMenu,footer { display:none !important; }
.block-container { padding-top:1.2rem !important; padding-bottom:0 !important; }
.timer-display { font-family:'Share Tech Mono',monospace; font-size:9rem; text-align:center;
    color:var(--gold-light); text-shadow:0 0 30px rgba(240,208,96,0.5),0 0 60px rgba(240,208,96,0.2); line-height:1; }
.timer-warning  { color:#f97316 !important; text-shadow:0 0 30px rgba(249,115,22,0.7) !important; animation:pulse 1s ease-in-out infinite; }
.timer-critical { color:#ef4444 !important; text-shadow:0 0 35px rgba(239,68,68,0.9) !important; animation:pulse 0.5s ease-in-out infinite; }
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.55} }
.alert-banner { background:linear-gradient(90deg,#7c2d12,#dc2626,#7c2d12); border:1px solid #ef4444;
    border-radius:8px; padding:0.7rem 1rem; text-align:center; font-family:'Bebas Neue',cursive;
    font-size:1.8rem; letter-spacing:4px; color:white; animation:pulse 1s ease-in-out infinite; margin-bottom:0.6rem; }
.warning-banner { background:linear-gradient(90deg,#92400e,#f59e0b,#92400e); border:1px solid #f59e0b;
    border-radius:8px; padding:0.7rem 1rem; text-align:center; font-family:'Bebas Neue',cursive;
    font-size:1.8rem; letter-spacing:4px; color:#000; animation:pulse 1s ease-in-out infinite; margin-bottom:0.6rem; }
.break-banner { background:linear-gradient(90deg,#1e3a5f,#2563eb,#1e3a5f); border:1px solid #3b82f6;
    border-radius:8px; padding:0.7rem 1rem; text-align:center; font-family:'Bebas Neue',cursive;
    font-size:2.2rem; letter-spacing:4px; color:#bfdbfe; margin-bottom:0.6rem; }
.ticker-bar { background:linear-gradient(90deg,#1e3a5f,#2563eb,#1e3a5f); border:1px solid #3b82f6;
    border-radius:8px; padding:0.5rem 1rem; text-align:center; font-family:'Bebas Neue',cursive;
    font-size:1.4rem; letter-spacing:3px; color:#bfdbfe; margin-top:0.5rem; }
</style>
""", unsafe_allow_html=True)

def load_data():
    if not os.path.exists(SAVE_FILE): return None
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return None

def fmt_time(secs):
    secs = max(0, int(secs))
    return f"{secs//60:02d}:{secs%60:02d}"

def big_stat(label, value, color="#d4af37"):
    return f"""<div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:1px solid #1f2937;
        border-radius:14px;padding:1.2rem 0.6rem;text-align:center;">
        <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;letter-spacing:2px;
            color:var(--text-dim);margin-bottom:0.3rem;font-weight:700;">{label}</div>
        <div style="font-family:'Share Tech Mono',monospace;font-size:2.8rem;color:{color};line-height:1;
            text-shadow:0 0 15px {color}55;">{value}</div></div>"""

data = load_data()

if data is None:
    st.markdown("""<div style="text-align:center;margin-top:15vh;">
        <div style="font-family:'Bebas Neue',cursive;font-size:4rem;color:#d4af37;letter-spacing:8px;">
            ♠ POKER TOURNAMENT ♠</div>
        <div style="font-family:'Rajdhani',sans-serif;color:#6b7280;font-size:1.4rem;margin-top:1rem;">
            Esperando datos del torneo…</div></div>""", unsafe_allow_html=True)
    time.sleep(1); st.rerun()

# ── Extract fields ──────────────────────────────────────────────────────────
players       = data.get("players", [])
blind_levels  = data.get("blind_levels", [])
cur_idx       = data.get("current_level", 0)
elapsed_secs  = data.get("elapsed_seconds", 0)
level_dur     = data.get("level_duration", 15)
timer_running = data.get("timer_running", False)
break_active  = data.get("break_active", False)
break_elapsed = data.get("break_elapsed", 0)
break_dur     = data.get("break_duration", 10)
t_name        = data.get("tournament_name", "LV POKER ROOM")
pct_pool      = data.get("prize_pool_pct", 85)
ticker_on     = data.get("display_ticker_enabled", False)
ticker_txt    = data.get("display_ticker", "")
view_interval = data.get("display_view_interval", 15)
prize_pcts    = data.get("prize_percentages", {})

# ── Wall-clock time ─────────────────────────────────────────────────────────
now = time.time()
if timer_running and not break_active:
    ws = data.get("timer_wall_start")
    eb = data.get("elapsed_at_start", elapsed_secs)
    if ws: elapsed_secs = eb + (now - ws)
if break_active:
    bw = data.get("break_wall_start")
    bb = data.get("break_elapsed_at_start", break_elapsed)
    if bw: break_elapsed = bb + (now - bw)

# ── Blind data ──────────────────────────────────────────────────────────────
idx = min(cur_idx, len(blind_levels)-1)
b   = blind_levels[idx] if blind_levels else {"level":1,"small":0,"big":0,"ante":0,"duration":level_dur}
nb  = blind_levels[idx+1] if idx+1 < len(blind_levels) else None
level_secs = b.get("duration", level_dur) * 60
remaining  = max(0, level_secs - elapsed_secs)
progress   = 1.0 - (remaining/level_secs) if level_secs > 0 else 0

# ── Players (counts only) ───────────────────────────────────────────────────
active_p   = [p for p in players if p.get("status") == "active"]
n_active   = len(active_p)
n_total    = len(players)
eliminated = n_total - n_active
total_rebuys = sum(p.get("rebuys",0) for p in players)
elim_display = eliminated + total_rebuys
avg_stack  = (sum(p["chips"] for p in active_p)//n_active) if n_active else 0

# ── Prize pool ──────────────────────────────────────────────────────────────
total_pool  = sum(p.get("paid_amount",0) for p in players)
total_pool += sum(sum(r["amount"] for r in p.get("rebuy_history",[])) for p in players)
total_pool += sum(sum(a["amount"] for a in p.get("addon_history",[])) for p in players)
eff_pool    = int(total_pool * pct_pool / 100)

# ── Rotating view logic ─────────────────────────────────────────────────────
# Vista siempre fija en timer
current_view = "timer"

# ── Alert banners ───────────────────────────────────────────────────────────
if break_active:
    brk_rem = max(0, break_dur*60 - break_elapsed)
    st.markdown(f'<div class="break-banner">☕ DESCANSO — {fmt_time(brk_rem)} RESTANTES</div>', unsafe_allow_html=True)
elif remaining <= 30 and timer_running:
    st.markdown('<div class="alert-banner">🚨 ¡CAMBIO DE CIEGAS EN MENOS DE 30 SEGUNDOS! 🚨</div>', unsafe_allow_html=True)
elif remaining <= 60 and timer_running:
    st.markdown('<div class="warning-banner">⚠️ ÚLTIMO MINUTO — CAMBIO DE CIEGAS PRÓXIMO ⚠️</div>', unsafe_allow_html=True)

# ── Header ──────────────────────────────────────────────────────────────────
_logo_b64 = ""
if os.path.exists("poker.png"):
    with open("poker.png","rb") as _f: _logo_b64 = base64.b64encode(_f.read()).decode()

if _logo_b64:
    st.markdown(f'''<div style="text-align:center;padding:0.4rem 0 0.6rem;border-bottom:2px solid #d4af37;margin-bottom:0.8rem;">
        <img src="data:image/png;base64,{_logo_b64}" style="max-height:110px;max-width:100%;object-fit:contain;
             filter:drop-shadow(0 0 18px rgba(212,175,55,0.5));"/></div>''', unsafe_allow_html=True)
else:
    st.markdown(f'''<div style="text-align:center;padding:0.3rem 0;border-bottom:2px solid #d4af37;margin-bottom:0.8rem;">
        <span style="font-family:'Bebas Neue',cursive;font-size:2.5rem;color:#d4af37;letter-spacing:8px;">
        ♠ {t_name} ♠</span></div>''', unsafe_allow_html=True)

# ── VIEW: TIMER (principal) ─────────────────────────────────────────────────
if current_view == "timer" or break_active:
    timer_class = "timer-display"
    if remaining <= 30 and timer_running and not break_active: timer_class += " timer-critical"
    elif remaining <= 60 and timer_running and not break_active: timer_class += " timer-warning"

    col_lvl, col_timer, col_players = st.columns([1, 2.2, 1])
    with col_lvl:
        st.markdown(f'''<div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:1px solid #d4af37;
            border-radius:16px;padding:1.5rem 1rem;text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;letter-spacing:4px;
                color:var(--text-dim);margin-bottom:0.3rem;font-weight:700;">NIVEL</div>
            <div style="font-family:'Bebas Neue',cursive;font-size:7rem;color:#d4af37;line-height:1;
                text-shadow:0 0 30px rgba(212,175,55,0.5);">{b['level']}</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;color:var(--text-dim);
                letter-spacing:2px;margin-top:0.3rem;">DE {len(blind_levels)}</div></div>''', unsafe_allow_html=True)

    with col_timer:
        if break_active:
            brk_rem = max(0, break_dur*60 - break_elapsed)
            t_html = f'<div class="timer-display" style="font-size:9rem;color:#60a5fa;text-shadow:0 0 30px rgba(96,165,250,0.5);">{fmt_time(brk_rem)}</div>'
        else:
            t_html = f'<div class="{timer_class}">{fmt_time(remaining)}</div>'
        st.markdown(f'''<div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:2px solid #d4af37;
            border-radius:16px;padding:1.2rem 1rem 0.8rem;text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;letter-spacing:4px;
                color:var(--text-dim);margin-bottom:0.2rem;font-weight:700;">
                {'DESCANSO' if break_active else 'TIEMPO RESTANTE'}</div>
            {t_html}</div>''', unsafe_allow_html=True)
        st.progress((break_elapsed/(break_dur*60)) if break_active and break_dur>0 else progress)

    with col_players:
        st.markdown(f'''<div style="background:linear-gradient(135deg,#1a2a1e,#0d1f14);border:1px solid #374151;
            border-radius:16px;padding:1.5rem 1rem;text-align:center;">
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.6rem;letter-spacing:4px;
                color:var(--text-dim);margin-bottom:0.3rem;font-weight:700;">JUGADORES</div>
            <div style="font-family:'Bebas Neue',cursive;font-size:6rem;color:#22c55e;line-height:1;">{n_active}</div>
            <div style="font-family:'Rajdhani',sans-serif;font-size:1.5rem;color:var(--text-dim);
                letter-spacing:2px;">{elim_display} eliminados</div></div>''', unsafe_allow_html=True)
        if nb:
            st.markdown(f'''<div style="margin-top:0.6rem;padding:0.7rem 0.8rem;background:rgba(37,99,235,0.08);
                border:1px dashed #2563eb;border-radius:10px;text-align:center;">
                <div style="font-family:'Rajdhani',sans-serif;font-size:1.4rem;letter-spacing:2px;
                    color:var(--text-dim);margin-bottom:0.3rem;font-weight:700;">PRÓXIMO NIVEL</div>
                <div style="font-family:'Share Tech Mono',monospace;color:#93c5fd;font-size:2rem;line-height:1.6;">
                    {nb['small']:,} / {nb['big']:,}<br>
                    <span style="font-size:1.6rem;color:#d1d5db;">Ante: {nb['ante']:,}</span></div></div>''', unsafe_allow_html=True)

    # Stats row
    st.markdown("<div style='height:0.8rem;'></div>", unsafe_allow_html=True)
    ante_val = f"{b['ante']:,}" if b.get('ante',0) > 0 else "—"
    c1,c2,c3,c4,c5 = st.columns(5)
    with c1: st.markdown(big_stat("SMALL BLIND", f"{b['small']:,}"), unsafe_allow_html=True)
    with c2: st.markdown(big_stat("BIG BLIND",   f"{b['big']:,}",  "#f0d060"), unsafe_allow_html=True)
    with c3: st.markdown(big_stat("ANTE",         ante_val,           "#f87171"), unsafe_allow_html=True)
    with c4: st.markdown(big_stat("PRIZE POOL",  f"${eff_pool:,}",    "#34d399"), unsafe_allow_html=True)
    with c5: st.markdown(big_stat("STACK PROM.", f"{avg_stack:,}",    "#a78bfa"), unsafe_allow_html=True)

# ── VIEW: BLINDS (estructura completa) ─────────────────────────────────────
elif current_view == "blinds":
    st.markdown('<div style="font-family:''Bebas Neue'',cursive;font-size:2rem;color:#d4af37;letter-spacing:6px;text-align:center;margin-bottom:1rem;">📋 ESTRUCTURA DE NIVELES</div>', unsafe_allow_html=True)
    rows_html = ""
    for i, bl in enumerate(blind_levels):
        is_cur  = (i == cur_idx)
        is_past = (i < cur_idx)
        is_next = (i == cur_idx + 1)
        dur = bl.get("duration", level_dur)
        ante_str = f"{bl['ante']:,}" if bl["ante"] > 0 else "—"
        if is_cur:
            rs = "background:linear-gradient(90deg,rgba(212,175,55,0.18),rgba(212,175,55,0.06) 60%,transparent);border-left:4px solid #d4af37;"
            nc, vc = "#d4af37", "#f0d060"
            badge = '<span style="background:#d4af37;color:#000;font-size:0.65rem;font-weight:900;padding:2px 8px;border-radius:10px;">▶ ACTUAL</span>'
        elif is_past:
            rs = "background:transparent;border-left:4px solid #1f2937;opacity:0.35;"
            nc, vc = "#374151", "#374151"
            badge = '<span style="color:#22c55e;font-size:1rem;">✓</span>'
        elif is_next:
            rs = "background:linear-gradient(90deg,rgba(37,99,235,0.12),transparent);border-left:4px solid #2563eb;opacity:0.92;"
            nc, vc = "#93c5fd", "#bfdbfe"
            badge = '<span style="color:#3b82f6;font-size:0.68rem;letter-spacing:1px;">PRÓXIMO</span>'
        else:
            rs = "background:transparent;border-left:4px solid transparent;opacity:0.55;"
            nc, vc = "#6b7280", "#9ca3af"
            badge = ""
        rows_html += (f'<tr style="{rs}">'
            f'<td style="padding:8px 10px;color:{nc};font-family:Bebas Neue,cursive;font-size:1.3rem;text-align:center;width:55px;">{bl["level"]}</td>'
            f'<td style="padding:8px 10px;text-align:center;width:80px;">{badge}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{vc};font-size:1.1rem;text-align:right;">{bl["small"]:,}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{vc};font-size:1.1rem;text-align:right;font-weight:700;">{bl["big"]:,}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{nc};font-size:1rem;text-align:right;">{ante_str}</td>'
            f'<td style="padding:8px 14px;font-family:Share Tech Mono,monospace;color:{nc};font-size:0.95rem;text-align:center;width:80px;">{dur} min</td>'
            f'</tr>')
    import streamlit.components.v1 as _comp
    _comp.html(f"""<!DOCTYPE html><html><head>
    <link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Share+Tech+Mono&family=Rajdhani:wght@600&display=swap" rel="stylesheet">
    <style>body{{margin:0;padding:0;background:transparent;}}
    .wrap{{overflow-y:auto;max-height:500px;border-radius:8px;border:1px solid #1f2937;background:#0a0a0a;}}
    table{{width:100%;border-collapse:collapse;}}
    thead tr{{position:sticky;top:0;background:#111827;border-bottom:2px solid rgba(212,175,55,0.3);}}
    th{{padding:10px 14px;font-family:Rajdhani,sans-serif;font-size:1.5rem;letter-spacing:2px;
        color:#b0b8c8;text-transform:uppercase;font-weight:700;}}
    th:nth-child(3),th:nth-child(4),th:nth-child(5){{text-align:right;}}
    th:last-child{{text-align:center;}} td{{border-bottom:1px solid rgba(255,255,255,0.04);}}</style></head><body>
    <div class="wrap"><table><thead><tr>
    <th style="width:55px;">LVL</th><th style="width:80px;"></th>
    <th>Small Blind</th><th>Big Blind</th><th>Ante</th><th style="width:80px;">Dur.</th>
    </tr></thead><tbody>{rows_html}</tbody></table></div></body></html>""", height=540, scrolling=False)

# ── VIEW: PRIZES ────────────────────────────────────────────────────────────
elif current_view == "prizes":
    st.markdown('<div style="font-family:''Bebas Neue'',cursive;font-size:2rem;color:#d4af37;letter-spacing:6px;text-align:center;margin-bottom:1rem;">💰 TABLA DE PREMIOS</div>', unsafe_allow_html=True)
    st.markdown(f'''<div style="text-align:center;padding:1rem;background:rgba(212,175,55,0.1);border:2px solid #d4af37;
        border-radius:12px;margin-bottom:1rem;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:3rem;color:#d4af37;">&#36;{eff_pool:,}</div>
        <div style="font-size:1rem;letter-spacing:3px;color:#b0b8c8;font-weight:700;">TOTAL EN PREMIOS</div>
    </div>''', unsafe_allow_html=True)
    # Calculate payouts
    n_players = len(players)
    brackets = prize_pcts
    if brackets and n_players > 0:
        bracket_keys = sorted(brackets.keys(), key=lambda x: int(x))
        structure = None
        for key in bracket_keys:
            if n_players <= int(key): structure = brackets[key]; break
        if structure is None and bracket_keys: structure = brackets[bracket_keys[-1]]
        if structure:
            place_labels = ["🥇 1er Lugar","🥈 2do Lugar","🥉 3er Lugar"]
            prize_styles = [
                "background:linear-gradient(90deg,rgba(212,175,55,0.2),transparent);border-left:3px solid #d4af37;",
                "background:linear-gradient(90deg,rgba(192,192,192,0.15),transparent);border-left:3px solid #9ca3af;",
                "background:linear-gradient(90deg,rgba(180,83,9,0.15),transparent);border-left:3px solid #b45309;",
            ]
            for i, s in enumerate(structure):
                amount = int(eff_pool * s["pct"] / 100)
                label  = place_labels[i] if i < 3 else f"{s['place']}° Lugar"
                style  = prize_styles[i] if i < 3 else "background:rgba(255,255,255,0.03);border-left:3px solid #374151;"
                st.markdown(f'''<div style="display:flex;justify-content:space-between;align-items:center;
                    padding:0.6rem 1rem;border-radius:6px;margin-bottom:0.4rem;
                    font-family:'Rajdhani',sans-serif;font-size:1.3rem;font-weight:600;{style}">
                    <span>{label}</span>
                    <span style="color:#9ca3af;">{s['pct']}%</span>
                    <span style="font-family:'Share Tech Mono',monospace;color:#d4af37;font-size:1.4rem;">&#36;{amount:,}</span>
                </div>''', unsafe_allow_html=True)

# ── Ticker ──────────────────────────────────────────────────────────────────
if ticker_on and ticker_txt:
    st.markdown(f'<div class="ticker-bar">{ticker_txt}</div>', unsafe_allow_html=True)

# ── Auto-refresh ─────────────────────────────────────────────────────────────
time.sleep(1)
st.rerun()