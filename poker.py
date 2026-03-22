import streamlit as st
import time
import json

st.set_page_config(
    page_title="Home Poker Tournament Manager",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Oswald:wght@300;400;600&family=Roboto:wght@300;400;500&display=swap');

:root {
    --bg: #000000; --bg2: #1a1a1a; --bg3: #2a2a2a; --bg4: #333333;
    --border: #444444; --text: #dddddd; --text-dim: #888888;
    --text-bright: #ffffff; --timer-bg: #d0d0d0; --timer-text: #111111;
    --next-bg: #555555;
}
html, body, [class*="css"] {
    font-family: 'Roboto', sans-serif !important;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0.5rem 1rem !important; max-width: 100% !important; }

.stButton > button {
    background: #3a3a3a !important; color: #ddd !important;
    border: 1px solid #555 !important; border-radius: 3px !important;
    font-family: 'Roboto', sans-serif !important; font-size: 0.8rem !important;
    padding: 0.25rem 0.7rem !important; box-shadow: none !important;
    font-weight: 400 !important;
}
.stButton > button:hover { background: #555 !important; transform: none !important; box-shadow: none !important; }

input, [data-testid="stNumberInput"] input {
    background: #2a2a2a !important; color: #ddd !important;
    border: 1px solid #555 !important; border-radius: 3px !important;
    font-family: 'Share Tech Mono', monospace !important;
}
.stTextInput > div > div > input { background: #2a2a2a !important; color: #ccc !important; border: 1px solid #555 !important; }
.stSelectbox > div > div { background: #2a2a2a !important; color: #ccc !important; }
.stCheckbox > label { color: #aaa !important; }
label { color: #999 !important; font-size: 0.82rem !important; }
h1,h2,h3 { color: #ccc !important; font-family: 'Oswald', sans-serif !important; }
hr { border-color: #333 !important; }
::-webkit-scrollbar { width: 5px; } ::-webkit-scrollbar-thumb { background: #444; }
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def _def(k, v):
    if k not in st.session_state: st.session_state[k] = v

_def("screen", "list")
_def("tournaments", {})
_def("selected_tourn", None)
_def("current_tourn", None)
_def("t", {})

DEFAULT_BLINDS = [
    {"sb":10,"bb":20,"ante":0,"min":20}, {"sb":15,"bb":30,"ante":0,"min":20},
    {"sb":25,"bb":50,"ante":0,"min":20}, {"sb":50,"bb":100,"ante":10,"min":20},
    {"sb":75,"bb":150,"ante":15,"min":20}, {"sb":100,"bb":200,"ante":25,"min":15},
    {"sb":150,"bb":300,"ante":25,"min":15}, {"sb":200,"bb":400,"ante":50,"min":15},
    {"sb":300,"bb":600,"ante":75,"min":12}, {"sb":400,"bb":800,"ante":100,"min":12},
    {"sb":500,"bb":1000,"ante":100,"min":10}, {"sb":750,"bb":1500,"ante":150,"min":10},
]

def new_cfg(name=""):
    return {"name":name,"buyin_cost":10,"buyin_chips":5000,"rebuy_cost":10,"rebuy_chips":5000,
            "addon_cost":10,"addon_chips":5000,"extra_cash":0,"paid_positions":3,
            "hide_zero_ante":False,"payout":[50,30,20],"blinds":[dict(b) for b in DEFAULT_BLINDS]}

def init_rt(cfg):
    return {"cfg":cfg,"level":0,"timer_running":False,
            "time_remaining":cfg["blinds"][0]["min"]*60,
            "timer_start_wall":None,"timer_start_rem":cfg["blinds"][0]["min"]*60,
            "entries":0,"players":0,"rebuys":0,"addons":0,
            "total_elapsed":0,"elapsed_start_wall":None}

def get_rem(t):
    if not t["timer_running"]: return t["time_remaining"]
    return max(0.0, t["timer_start_rem"] - (time.time() - t["timer_start_wall"]))

def fmt(s):
    s=int(s); h,r=divmod(s,3600); m,sec=divmod(r,60); return f"{h:02d}:{m:02d}:{sec:02d}"

def ttb(t):
    rem = get_rem(t)
    future = sum(t["cfg"]["blinds"][i]["min"]*60 for i in range(t["level"]+1, len(t["cfg"]["blinds"])))
    return rem + future

def get_elapsed(t):
    base = t.get("total_elapsed",0)
    if t.get("timer_running") and t.get("elapsed_start_wall"):
        return base + (time.time()-t["elapsed_start_wall"])
    return base

def total_prize(t):
    cfg=t["cfg"]
    return (t["entries"]*cfg["buyin_cost"] + t["rebuys"]*cfg["rebuy_cost"] +
            t["addons"]*cfg["addon_cost"] + cfg["extra_cash"])

def moon(p):
    return ["🌕","🌖","🌗","🌘","🌑"][min(int(p*5),4)]

# ══════════════════════════════════════════════════════════════════════════════
# LIST SCREEN
# ══════════════════════════════════════════════════════════════════════════════
if st.session_state.screen == "list":
    st.markdown("""<style>
    html,body,[class*="css"],.stApp{background:radial-gradient(ellipse at center,#3a0000 0%,#000 70%) !important;}
    </style>""", unsafe_allow_html=True)

    _, col, _ = st.columns([1,2,1])
    with col:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("## Tournaments")
        st.markdown("---")
        names = list(st.session_state.tournaments.keys())
        sel = None
        if names:
            default_idx = 0
            if st.session_state.selected_tourn in names:
                default_idx = names.index(st.session_state.selected_tourn)
            sel = st.radio("", names, index=default_idx, label_visibility="collapsed")
            st.session_state.selected_tourn = sel
        else:
            st.caption("No saved tournaments.")

        st.markdown("")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("Load selected", use_container_width=True, disabled=not sel):
                cfg = st.session_state.tournaments[sel]
                st.session_state.current_tourn = sel
                st.session_state.t = init_rt(cfg)
                st.session_state.screen = "tournament"
                st.rerun()
            if st.button("Create new tournament", use_container_width=True):
                st.session_state.draft_cfg = new_cfg()
                st.session_state.screen = "config"
                st.rerun()
        with c2:
            if st.button("Copy selected", use_container_width=True, disabled=not sel):
                orig = st.session_state.tournaments[sel]
                nn = sel+" (copy)"
                st.session_state.tournaments[nn] = json.loads(json.dumps(orig))
                st.session_state.tournaments[nn]["name"] = nn
                st.rerun()
            if st.button("Delete selected", use_container_width=True, disabled=not sel):
                del st.session_state.tournaments[sel]
                st.session_state.selected_tourn = None
                st.rerun()
        st.markdown("<br><span style='color:#333;font-size:0.7rem;'>v1.0.0</span>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIG SCREEN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "config":
    if "draft_cfg" not in st.session_state:
        st.session_state.draft_cfg = new_cfg()
    cfg = st.session_state.draft_cfg

    _, col, _ = st.columns([0.5, 3, 0.5])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        # Title row
        tc1, tc2, tc3 = st.columns([3,2,1])
        with tc1:
            cfg["name"] = st.text_input("Title", value=cfg["name"], placeholder="Enter text...", label_visibility="collapsed")
        with tc2:
            total_pct = sum(cfg["payout"])
            color = "#4caf50" if total_pct==100 else "#e53935"
            st.markdown(f"<div style='padding-top:0.55rem;color:{color};font-size:0.9rem;font-weight:500;'>Total: {total_pct}%</div>", unsafe_allow_html=True)
        with tc3:
            if st.button("✕", key="cfg_x"):
                del st.session_state.draft_cfg
                st.session_state.screen = "list"
                st.rerun()

        st.markdown("---")
        left, right = st.columns(2)

        with left:
            st.markdown("<span style='font-size:0.72rem;color:#666;'>Cost &nbsp;&nbsp;&nbsp; Chips</span>", unsafe_allow_html=True)
            for label, ck, chk in [("Buy-In","buyin_cost","buyin_chips"),
                                    ("Rebuy","rebuy_cost","rebuy_chips"),
                                    ("Addon","addon_cost","addon_chips")]:
                a, b = st.columns(2)
                with a: cfg[ck] = st.number_input(label, value=cfg[ck], min_value=0, step=1)
                with b: cfg[chk] = st.number_input(f"{label} chips", value=cfg[chk], min_value=0, step=100, label_visibility="collapsed")

            cfg["extra_cash"] = st.number_input("Extra cash", value=cfg["extra_cash"], min_value=0, step=1)
            new_n = st.number_input("# Paid positions", value=cfg["paid_positions"], min_value=1, max_value=20, step=1)
            if new_n != cfg["paid_positions"]:
                cfg["paid_positions"] = new_n
                while len(cfg["payout"]) < new_n: cfg["payout"].append(0)
                while len(cfg["payout"]) > new_n: cfg["payout"].pop()
            cfg["hide_zero_ante"] = st.checkbox("Hide zero ante", value=cfg["hide_zero_ante"])

        with right:
            st.markdown("<span style='font-size:0.72rem;color:#666;'>Position &nbsp; Percentage</span>", unsafe_allow_html=True)
            for i in range(cfg["paid_positions"]):
                pc1, pc2 = st.columns([1,2])
                with pc1: st.markdown(f"<div style='padding-top:0.55rem;color:#aaa;'>{i+1}</div>", unsafe_allow_html=True)
                with pc2: cfg["payout"][i] = st.number_input("pct", value=cfg["payout"][i], min_value=0, max_value=100, step=5, key=f"pct_{i}", label_visibility="collapsed")

        st.markdown("---")
        b1, _, b3, b4 = st.columns([2,1,1,1])
        with b1:
            if st.button("Blinds settings"):
                st.session_state.screen = "blinds"
                st.rerun()
        with b3:
            if st.button("💾 Save"):
                name = cfg["name"].strip() or "Unnamed"
                cfg["name"] = name
                st.session_state.tournaments[name] = json.loads(json.dumps(cfg))
                st.session_state.selected_tourn = name
                del st.session_state.draft_cfg
                st.session_state.screen = "list"
                st.rerun()
        with b4:
            if st.button("▶ Start"):
                name = cfg["name"].strip() or "Unnamed"
                cfg["name"] = name
                st.session_state.tournaments[name] = json.loads(json.dumps(cfg))
                st.session_state.current_tourn = name
                st.session_state.t = init_rt(cfg)
                del st.session_state.draft_cfg
                st.session_state.screen = "tournament"
                st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# BLINDS SCREEN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "blinds":
    if "draft_cfg" not in st.session_state:
        st.session_state.screen = "config"; st.rerun()
    cfg = st.session_state.draft_cfg
    blinds = cfg["blinds"]

    _, col, _ = st.columns([0.3,5,0.3])
    with col:
        st.markdown("<br>", unsafe_allow_html=True)
        hc1, hc2 = st.columns([5,1])
        with hc1: st.markdown("### Blinds Settings")
        with hc2:
            if st.button("← Back"):
                st.session_state.screen = "config"; st.rerun()

        st.markdown("---")
        h0,h1,h2,h3,h4,h5 = st.columns([0.4,1,1,1,1,0.5])
        for col_w, lbl in zip([h0,h1,h2,h3,h4,h5],["#","Small Blind","Big Blind","Ante","Minutes",""]):
            col_w.markdown(f"<span style='font-size:0.68rem;color:#666;text-transform:uppercase;'>{lbl}</span>", unsafe_allow_html=True)

        to_del = []
        for i, bl in enumerate(blinds):
            c0,c1,c2,c3,c4,c5 = st.columns([0.4,1,1,1,1,0.5])
            c0.markdown(f"<div style='padding-top:0.55rem;color:#555;font-size:0.82rem;'>{i+1}</div>", unsafe_allow_html=True)
            bl["sb"]   = c1.number_input("sb",   value=bl["sb"],   min_value=0, step=5,  key=f"sb_{i}",   label_visibility="collapsed")
            bl["bb"]   = c2.number_input("bb",   value=bl["bb"],   min_value=0, step=5,  key=f"bb_{i}",   label_visibility="collapsed")
            bl["ante"] = c3.number_input("ante", value=bl["ante"], min_value=0, step=5,  key=f"ante_{i}", label_visibility="collapsed")
            bl["min"]  = c4.number_input("min",  value=bl["min"],  min_value=1, step=1,  key=f"min_{i}",  label_visibility="collapsed")
            if c5.button("🗑", key=f"del_{i}"): to_del.append(i)

        for i in reversed(to_del): blinds.pop(i)
        if to_del: st.rerun()

        if st.button("➕ Add level"):
            last = blinds[-1] if blinds else {"sb":500,"bb":1000,"ante":100,"min":10}
            blinds.append({"sb":last["sb"]*2,"bb":last["bb"]*2,"ante":last["ante"]*2,"min":last["min"]})
            st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TOURNAMENT SCREEN
# ══════════════════════════════════════════════════════════════════════════════
elif st.session_state.screen == "tournament":
    t = st.session_state.t
    cfg = t["cfg"]
    blinds = cfg["blinds"]
    lvl = t["level"]

    rem = get_rem(t)
    if rem <= 0 and t["timer_running"]:
        t["time_remaining"] = 0; t["timer_running"] = False
        t["total_elapsed"] = get_total_elapsed(t) if hasattr(get_elapsed, '__call__') else get_elapsed(t)
        t["elapsed_start_wall"] = None

    if t["timer_running"]:
        time.sleep(1); st.rerun()

    rem = get_rem(t)
    bl = blinds[lvl]
    total_min = bl["min"]*60
    progress = 1-(rem/total_min) if total_min>0 else 1.0
    prize = total_prize(t)

    # ── Header ──
    st.markdown(f"""
    <div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.4rem;">
        <div style="font-family:'Oswald',sans-serif;font-size:1.5rem;font-weight:400;color:#fff;letter-spacing:0.05em;">
            {cfg['name']}
        </div>
        <div style="display:flex;gap:0;">
            <div style="border:1px solid #444;padding:0.1rem 0.5rem;text-align:center;min-width:80px;">
                <span style="display:block;font-size:0.6rem;color:#666;text-transform:uppercase;letter-spacing:0.08em;">Level</span>
                <span style="display:block;font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#fff;">{lvl+1}</span>
            </div>
            <div style="border:1px solid #444;border-left:none;padding:0.1rem 0.5rem;text-align:center;min-width:100px;">
                <span style="display:block;font-size:0.6rem;color:#666;text-transform:uppercase;letter-spacing:0.08em;">Time to break</span>
                <span style="display:block;font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#fff;">{fmt(ttb(t))}</span>
            </div>
            <div style="border:1px solid #444;border-left:none;padding:0.1rem 0.5rem;text-align:center;min-width:100px;">
                <span style="display:block;font-size:0.6rem;color:#666;text-transform:uppercase;letter-spacing:0.08em;">Total time</span>
                <span style="display:block;font-family:'Share Tech Mono',monospace;font-size:0.95rem;color:#fff;">{fmt(get_elapsed(t))}</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Current level row ──
    ante_display = "—" if (bl["ante"]==0 and cfg["hide_zero_ante"]) else str(bl["ante"])
    st.markdown(f"""
    <div style="background:#d0d0d0;display:flex;align-items:center;padding:0.35rem 0.8rem;border-radius:3px;margin-bottom:0.2rem;">
        <div style="font-family:'Share Tech Mono',monospace;font-size:2.6rem;font-weight:700;color:#111;min-width:190px;">{fmt(rem)}</div>
        <div style="font-size:2rem;color:#444;margin:0 0.8rem;">{moon(progress)}</div>
        <div style="flex:1;text-align:right;">
            <div style="font-size:0.65rem;color:#666;text-transform:uppercase;letter-spacing:0.1em;">Blinds</div>
            <div style="font-family:'Share Tech Mono',monospace;font-size:1.9rem;color:#111;font-weight:700;">{bl['sb']}/{bl['bb']}</div>
            <div style="font-size:0.7rem;color:#666;">Ante &nbsp; {ante_display}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Next level row ──
    if lvl+1 < len(blinds):
        nbl = blinds[lvl+1]
        nante = "—" if (nbl["ante"]==0 and cfg["hide_zero_ante"]) else str(nbl["ante"])
        st.markdown(f"""
        <div style="background:#555;display:flex;align-items:center;padding:0.25rem 0.8rem;border-radius:3px;margin-bottom:0.5rem;">
            <div style="font-family:'Share Tech Mono',monospace;font-size:1.35rem;color:#ddd;min-width:120px;">{fmt(nbl['min']*60)}</div>
            <div style="font-size:1.1rem;color:#999;margin:0 0.5rem;">🌑</div>
            <div style="flex:1;text-align:right;">
                <div style="font-size:0.58rem;color:#aaa;text-transform:uppercase;">Blinds</div>
                <div style="font-family:'Share Tech Mono',monospace;font-size:1.2rem;color:#ddd;">{nbl['sb']}/{nbl['bb']}</div>
                <div style="font-size:0.62rem;color:#aaa;">Ante &nbsp; {nante}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Info grid ──
    total_chips = (t["entries"]*cfg["buyin_chips"] + t["rebuys"]*cfg["rebuy_chips"] + t["addons"]*cfg["addon_chips"])
    avg_stack = total_chips//t["players"] if t["players"]>0 else 0
    ordinals = ["1st","2nd","3rd","4th","5th","6th","7th","8th","9th","10th"]
    payout_html = "".join(
        f"<div style='display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.1rem;'>"
        f"<span style='color:#888;'>{ordinals[i] if i<len(ordinals) else f'{i+1}th'}</span>"
        f"<span style='font-family:Share Tech Mono,monospace;color:#ddd;'>{round(prize*p/100)}</span></div>"
        for i,p in enumerate(cfg["payout"])
    )

    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1fr 1fr 1fr;border:1px solid #333;border-radius:3px;margin-bottom:0.5rem;">
        <div style="padding:0.35rem 0.6rem;border-right:1px solid #333;">
            <div style="font-size:0.65rem;color:#666;text-transform:uppercase;letter-spacing:0.1em;border-bottom:1px solid #333;padding-bottom:0.15rem;margin-bottom:0.25rem;">Status</div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.1rem;"><span style="color:#888;">Players</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{t['players']}/{t['entries']}</span></div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.1rem;"><span style="color:#888;">Re-buys</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{t['rebuys']}</span></div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;"><span style="color:#888;">Add-ons</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{t['addons']}</span></div>
        </div>
        <div style="padding:0.35rem 0.6rem;border-right:1px solid #333;">
            <div style="font-size:0.65rem;color:#666;text-transform:uppercase;letter-spacing:0.1em;border-bottom:1px solid #333;padding-bottom:0.15rem;margin-bottom:0.25rem;">Statistics</div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.1rem;"><span style="color:#888;">Average stack</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{avg_stack:,}</span></div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:0.1rem;"><span style="color:#888;">Total chips</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{total_chips:,}</span></div>
            <div style="display:flex;justify-content:space-between;font-size:0.82rem;"><span style="color:#888;">Total prize</span><span style="font-family:'Share Tech Mono',monospace;color:#ddd;">{prize}</span></div>
        </div>
        <div style="padding:0.35rem 0.6rem;">
            <div style="font-size:0.65rem;color:#666;text-transform:uppercase;letter-spacing:0.1em;border-bottom:1px solid #333;padding-bottom:0.15rem;margin-bottom:0.25rem;">Payout</div>
            {payout_html}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Control bar ──
    st.markdown("<hr style='margin:0.3rem 0;'>", unsafe_allow_html=True)
    st.markdown("<div style='display:flex;gap:1.5rem;align-items:center;flex-wrap:wrap;background:#1a1a1a;padding:0.4rem 0.5rem;border-radius:3px;'>", unsafe_allow_html=True)

    cc = st.columns([1,1,1,1,1,0.1,2,0.1,1])

    for col_w, label, km, kp, dec_key, inc_key, field, field2, cap in [
        (cc[0],"ENTRIES","ent_m","ent_p","entries","entries",None,None,True),
    ]:
        pass  # replaced below

    ctrl_defs = [
        ("ENTRIES",  "em", "ep",  lambda: setattr_minus("entries",  "players")),
        ("PLAYERS",  "pm", "pp",  None),
        ("RE-BUYS",  "rm", "rp",  None),
        ("ADD-ONS",  "am", "ap",  None),
        ("LEVEL",    "lm", "lp",  None),
    ]

    def ctrl_group(col, label, km, kp, on_minus, on_plus):
        with col:
            st.markdown(f"<div style='text-align:center;font-size:0.6rem;color:#666;text-transform:uppercase;margin-bottom:0.1rem;'>{label}</div>", unsafe_allow_html=True)
            ca, cb = st.columns(2)
            with ca:
                if st.button("−", key=km): on_minus()
            with cb:
                if st.button("+", key=kp): on_plus()

    def entries_minus():
        t["entries"] = max(0, t["entries"]-1)
        t["players"] = max(0, min(t["players"], t["entries"]))
        st.rerun()
    def entries_plus():
        t["entries"] += 1; t["players"] += 1; st.rerun()
    def players_minus():
        t["players"] = max(0, t["players"]-1); st.rerun()
    def players_plus():
        t["players"] = min(t["entries"], t["players"]+1); st.rerun()
    def rebuys_minus():
        t["rebuys"] = max(0, t["rebuys"]-1); st.rerun()
    def rebuys_plus():
        t["rebuys"] += 1; st.rerun()
    def addons_minus():
        t["addons"] = max(0, t["addons"]-1); st.rerun()
    def addons_plus():
        t["addons"] += 1; st.rerun()
    def level_minus():
        if t["level"]>0:
            t["level"] -= 1; nbl=blinds[t["level"]]
            t["time_remaining"]=nbl["min"]*60; t["timer_start_rem"]=nbl["min"]*60; t["timer_running"]=False; st.rerun()
    def level_plus():
        if t["level"]+1<len(blinds):
            t["level"] += 1; nbl=blinds[t["level"]]
            t["time_remaining"]=nbl["min"]*60; t["timer_start_rem"]=nbl["min"]*60; t["timer_running"]=False; st.rerun()

    ctrl_group(cc[0], "ENTRIES",  "em","ep", entries_minus, entries_plus)
    ctrl_group(cc[1], "PLAYERS",  "pm","pp", players_minus, players_plus)
    ctrl_group(cc[2], "RE-BUYS",  "rm","rp", rebuys_minus,  rebuys_plus)
    ctrl_group(cc[3], "ADD-ONS",  "am","ap", addons_minus,  addons_plus)
    ctrl_group(cc[4], "LEVEL",    "lm","lp", level_minus,   level_plus)

    with cc[6]:
        pb1, pb2 = st.columns([1,3])
        with pb1:
            if t["timer_running"]:
                if st.button("⏸", key="pause"):
                    t["time_remaining"] = get_rem(t)
                    t["total_elapsed"] = get_elapsed(t)
                    t["timer_running"] = False; t["elapsed_start_wall"] = None; st.rerun()
            else:
                if st.button("▶", key="play"):
                    t["timer_start_wall"] = time.time()
                    t["timer_start_rem"] = t["time_remaining"]
                    t["timer_running"] = True
                    if not t.get("elapsed_start_wall"): t["elapsed_start_wall"] = time.time()
                    st.rerun()
        with pb2:
            st.progress(min(1.0, max(0.0, progress)))

    with cc[8]:
        if st.button("✕ Exit"):
            t["timer_running"] = False
            st.session_state.screen = "list"; st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # Settings button
    st.markdown("")
    if st.button("⚙ Settings"):
        st.session_state.draft_cfg = json.loads(json.dumps(cfg))
        st.session_state.screen = "config"; st.rerun()