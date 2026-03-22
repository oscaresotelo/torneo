import streamlit as st
import pandas as pd
import json
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import date, datetime, timedelta
import os

# ── Configuración de página ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Gestor de Vencimientos",
    page_icon="📅",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS personalizado ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Syne', sans-serif !important;
}

/* Header principal */
.main-header {
    background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 2rem;
    color: white;
    position: relative;
    overflow: hidden;
}
.main-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(100,100,255,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.main-header h1 {
    font-size: 2.2rem;
    font-weight: 800;
    margin: 0;
    letter-spacing: -1px;
}
.main-header p {
    margin: 0.3rem 0 0;
    opacity: 0.7;
    font-size: 1rem;
}

/* Tarjetas de servicio */
.service-card {
    background: white;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin: 0.5rem 0;
    border-left: 4px solid #302b63;
    box-shadow: 0 2px 12px rgba(0,0,0,0.07);
    display: flex;
    align-items: center;
    justify-content: space-between;
    transition: all 0.2s ease;
}
.service-card:hover {
    box-shadow: 0 4px 20px rgba(0,0,0,0.12);
    transform: translateY(-1px);
}
.service-card.vence-hoy {
    border-left-color: #e74c3c;
    background: #fff5f5;
}
.service-card.vence-pronto {
    border-left-color: #f39c12;
    background: #fffbf0;
}
.service-card.ok {
    border-left-color: #27ae60;
}

/* Badges de estado */
.badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    font-family: 'Syne', sans-serif;
}
.badge-danger  { background: #fde8e8; color: #c0392b; }
.badge-warning { background: #fef3cd; color: #856404; }
.badge-success { background: #d4edda; color: #155724; }

/* Métricas */
.metric-box {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border-radius: 12px;
    padding: 1.2rem;
    text-align: center;
}
.metric-box .number {
    font-family: 'Syne', sans-serif;
    font-size: 2.5rem;
    font-weight: 800;
    line-height: 1;
}
.metric-box .label {
    font-size: 0.85rem;
    opacity: 0.85;
    margin-top: 0.3rem;
}

/* Botón principal */
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #302b63, #24243e) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    letter-spacing: 0.5px;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #f8f7ff;
}

/* Emojis de servicio */
.service-icon {
    font-size: 1.8rem;
    margin-right: 0.8rem;
}

/* Tabla de destinatarios */
.recipient-tag {
    display: inline-block;
    background: #e8e6ff;
    color: #302b63;
    border-radius: 20px;
    padding: 0.2rem 0.7rem;
    font-size: 0.82rem;
    margin: 0.15rem;
    font-weight: 500;
}

div[data-testid="stExpander"] {
    border: 1px solid #e8e6ff;
    border-radius: 10px;
    overflow: hidden;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers de persistencia ──────────────────────────────────────────────────
DATA_FILE = "vencimientos_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "servicios": [],
        "destinatarios": [],
        "config_email": {
            "smtp_server": "smtp.gmail.com",
            "smtp_port": 587,
            "email_from": "",
            "password": "",
            "dias_anticipacion": 3,
        }
    }

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ── Íconos por servicio ──────────────────────────────────────────────────────
SERVICE_ICONS = {
    "Electricidad": "⚡",
    "Gas": "🔥",
    "Agua": "💧",
    "Internet": "🌐",
    "Teléfono": "📱",
    "Alquiler": "🏠",
    "Seguro": "🛡️",
    "Tarjeta de crédito": "💳",
    "Otro": "📋",
}

def get_estado(fecha_venc_str, dias_anticipacion):
    hoy = date.today()
    try:
        fv = datetime.strptime(fecha_venc_str, "%Y-%m-%d").date()
    except Exception:
        return "desconocido", "—"
    delta = (fv - hoy).days
    if delta < 0:
        return "vencido", f"Venció hace {abs(delta)} día(s)"
    elif delta == 0:
        return "vence-hoy", "⚠️ Vence HOY"
    elif delta <= dias_anticipacion:
        return "vence-pronto", f"Vence en {delta} día(s)"
    else:
        return "ok", f"Vence en {delta} día(s)"

# ── Envío de email ────────────────────────────────────────────────────────────
def send_email_alert(config, destinatarios, servicio, fecha_venc, estado_label):
    if not config["email_from"] or not config["password"]:
        return False, "Configurá el email en la barra lateral."

    subject = f"📅 Vencimiento: {servicio['nombre']} — {fecha_venc}"
    html = f"""
    <html><body style="font-family: Arial, sans-serif; max-width:600px; margin:auto; padding:20px;">
      <div style="background:linear-gradient(135deg,#302b63,#24243e);border-radius:12px;padding:24px;color:white;text-align:center;">
        <h1 style="margin:0;font-size:1.8rem;">📅 Alerta de Vencimiento</h1>
        <p style="opacity:.8;margin:6px 0 0;">Sistema de Gestión de Vencimientos</p>
      </div>
      <div style="border:1px solid #e0e0e0;border-radius:12px;padding:24px;margin-top:16px;">
        <h2 style="color:#302b63;">{SERVICE_ICONS.get(servicio['tipo'],'📋')} {servicio['nombre']}</h2>
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:8px 0;color:#666;width:140px;">Tipo de servicio:</td>
              <td style="padding:8px 0;font-weight:600;">{servicio['tipo']}</td></tr>
          <tr><td style="padding:8px 0;color:#666;">Fecha de vencimiento:</td>
              <td style="padding:8px 0;font-weight:600;color:#e74c3c;">{fecha_venc}</td></tr>
          <tr><td style="padding:8px 0;color:#666;">Estado:</td>
              <td style="padding:8px 0;">{estado_label}</td></tr>
          {'<tr><td style="padding:8px 0;color:#666;">Monto:</td><td style="padding:8px 0;font-weight:600;">$' + str(servicio.get("monto","")) + '</td></tr>' if servicio.get("monto") else ""}
          {'<tr><td style="padding:8px 0;color:#666;">Notas:</td><td style="padding:8px 0;">' + servicio.get("notas","") + '</td></tr>' if servicio.get("notas") else ""}
        </table>
      </div>
      <p style="text-align:center;color:#aaa;font-size:0.8rem;margin-top:16px;">
        Enviado automáticamente por el Gestor de Vencimientos
      </p>
    </body></html>
    """

    errors = []
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(config["smtp_server"], int(config["smtp_port"])) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(config["email_from"], config["password"])
            for dest in destinatarios:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"]    = config["email_from"]
                msg["To"]      = dest["email"]
                msg.attach(MIMEText(html, "html"))
                server.sendmail(config["email_from"], dest["email"], msg.as_string())
    except Exception as e:
        return False, str(e)
    return True, f"Email enviado a {len(destinatarios)} destinatario(s)."

# ── Carga de datos ────────────────────────────────────────────────────────────
data = load_data()

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuración de Email")

    with st.expander("📧 Cuenta de envío", expanded=False):
        cfg = data["config_email"]
        cfg["email_from"]  = st.text_input("Email remitente", cfg.get("email_from",""), placeholder="oscaresotelo@gmail.com")
        cfg["password"]    = st.text_input("Contraseña / App Password", cfg.get("password",""), type="password")
        cfg["smtp_server"] = st.text_input("Servidor SMTP", cfg.get("smtp_server","smtp.gmail.com"))
        cfg["smtp_port"]   = st.number_input("Puerto", value=int(cfg.get("smtp_port",587)), step=1)
        cfg["dias_anticipacion"] = st.number_input(
            "Días de anticipación para alertas", 
            min_value=1, max_value=30, 
            value=int(cfg.get("dias_anticipacion",3))
        )
        if st.button("💾 Guardar configuración"):
            data["config_email"] = cfg
            save_data(data)
            st.success("✅ Guardado")

    st.markdown("---")
    st.markdown("### 👥 Destinatarios")
    with st.expander("Agregar destinatario", expanded=False):
        dn_nombre = st.text_input("Nombre", key="dn_nom")
        dn_email  = st.text_input("Email",  key="dn_email")
        if st.button("➕ Agregar", key="btn_dest"):
            if dn_email and "@" in dn_email:
                data["destinatarios"].append({"nombre": dn_nombre, "email": dn_email})
                save_data(data)
                st.success(f"Agregado: {dn_email}")
                st.rerun()
            else:
                st.error("Email inválido")

    if data["destinatarios"]:
        st.markdown("**Lista actual:**")
        for i, d in enumerate(data["destinatarios"]):
            col1, col2 = st.columns([4,1])
            col1.markdown(f"<span class='recipient-tag'>📩 {d['nombre'] or d['email']}</span>", unsafe_allow_html=True)
            if col2.button("✕", key=f"del_d_{i}"):
                data["destinatarios"].pop(i)
                save_data(data)
                st.rerun()
    else:
        st.info("No hay destinatarios aún.")

    st.markdown("---")
    st.markdown("### 🔔 Verificar alertas ahora")
    if st.button("📨 Enviar alertas pendientes", use_container_width=True):
        hoy = date.today()
        enviados = 0
        dias_ant = int(data["config_email"].get("dias_anticipacion", 3))
        for s in data["servicios"]:
            try:
                fv = datetime.strptime(s["fecha_vencimiento"], "%Y-%m-%d").date()
                delta = (fv - hoy).days
                if 0 <= delta <= dias_ant:
                    estado_lbl = "⚠️ Vence HOY" if delta == 0 else f"Vence en {delta} día(s)"
                    ok, msg = send_email_alert(
                        data["config_email"],
                        data["destinatarios"],
                        s, s["fecha_vencimiento"], estado_lbl
                    )
                    if ok:
                        enviados += 1
            except Exception:
                pass
        if enviados:
            st.success(f"✅ {enviados} alerta(s) enviada(s).")
        else:
            st.info("No hay vencimientos próximos en este momento.")

# ── MAIN ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="main-header">
  <h1>📅 Gestor de Vencimientos</h1>
  <p>Controlá tus servicios y recibí alertas automáticas por email</p>
</div>
""", unsafe_allow_html=True)

# Métricas rápidas
hoy = date.today()
dias_ant = int(data["config_email"].get("dias_anticipacion", 3))
total = len(data["servicios"])
vence_hoy   = sum(1 for s in data["servicios"] if datetime.strptime(s["fecha_vencimiento"],"%Y-%m-%d").date() == hoy)
vence_pronto = sum(1 for s in data["servicios"] if 0 < (datetime.strptime(s["fecha_vencimiento"],"%Y-%m-%d").date() - hoy).days <= dias_ant)
vencidos     = sum(1 for s in data["servicios"] if (datetime.strptime(s["fecha_vencimiento"],"%Y-%m-%d").date() - hoy).days < 0)

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""<div class="metric-box" style="background:linear-gradient(135deg,#667eea,#764ba2)">
        <div class="number">{total}</div><div class="label">Total servicios</div></div>""", unsafe_allow_html=True)
with c2:
    st.markdown(f"""<div class="metric-box" style="background:linear-gradient(135deg,#f43b47,#453a94)">
        <div class="number">{vence_hoy}</div><div class="label">Vencen hoy</div></div>""", unsafe_allow_html=True)
with c3:
    st.markdown(f"""<div class="metric-box" style="background:linear-gradient(135deg,#f7971e,#ffd200)">
        <div class="number">{vence_pronto}</div><div class="label">Vencen pronto</div></div>""", unsafe_allow_html=True)
with c4:
    st.markdown(f"""<div class="metric-box" style="background:linear-gradient(135deg,#11998e,#38ef7d)">
        <div class="number">{len(data['destinatarios'])}</div><div class="label">Destinatarios</div></div>""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Tabs principales
tab1, tab2 = st.tabs(["📋 Mis Servicios", "➕ Agregar / Editar Servicio"])

# ────────────────────────────────────────────────────────────────────────────
with tab1:
    if not data["servicios"]:
        st.info("🌟 No tenés servicios cargados. Usá la pestaña **Agregar / Editar Servicio** para comenzar.")
    else:
        # Filtros
        col_f1, col_f2 = st.columns([2,2])
        filtro_tipo   = col_f1.multiselect("Filtrar por tipo", list(SERVICE_ICONS.keys()), default=[])
        filtro_estado = col_f2.multiselect("Filtrar por estado", ["vence-hoy","vence-pronto","ok","vencido"], default=[])

        for i, s in enumerate(data["servicios"]):
            estado_key, estado_label = get_estado(s["fecha_vencimiento"], dias_ant)

            if filtro_tipo   and s["tipo"]   not in filtro_tipo:   continue
            if filtro_estado and estado_key  not in filtro_estado: continue

            card_class = estado_key if estado_key in ["vence-hoy","vence-pronto"] else "ok"
            badge_class = {"vence-hoy":"badge-danger","vence-pronto":"badge-warning","ok":"badge-success","vencido":"badge-danger"}.get(estado_key,"badge-success")

            with st.container():
                col_info, col_acc = st.columns([5, 2])
                with col_info:
                    icon = SERVICE_ICONS.get(s["tipo"], "📋")
                    fv_fmt = datetime.strptime(s["fecha_vencimiento"],"%Y-%m-%d").strftime("%d/%m/%Y")
                    monto_str = f" — <strong>${s['monto']}</strong>" if s.get("monto") else ""
                    st.markdown(f"""
                    <div class="service-card {card_class}">
                      <div>
                        <span class="service-icon">{icon}</span>
                        <strong style="font-size:1.05rem">{s['nombre']}</strong>
                        <span style="color:#888;font-size:0.85rem;margin-left:6px">({s['tipo']})</span>
                        {monto_str}
                        <br>
                        <span style="color:#555;font-size:0.9rem;margin-left:2.6rem">📅 {fv_fmt} — {estado_label}</span>
                        {'<br><span style="color:#888;font-size:0.82rem;margin-left:2.6rem">📝 ' + s.get('notas','') + '</span>' if s.get('notas') else ''}
                      </div>
                      <span class="badge {badge_class}">{estado_label}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_acc:
                    st.markdown("<br>", unsafe_allow_html=True)
                    btn_email, btn_del = st.columns(2)
                    if btn_email.button("📧", key=f"email_{i}", help="Enviar email ahora"):
                        ok, msg = send_email_alert(
                            data["config_email"], data["destinatarios"],
                            s, s["fecha_vencimiento"], estado_label
                        )
                        st.success(msg) if ok else st.error(msg)
                    if btn_del.button("🗑️", key=f"del_{i}", help="Eliminar"):
                        data["servicios"].pop(i)
                        save_data(data)
                        st.rerun()

# ────────────────────────────────────────────────────────────────────────────
with tab2:
    st.markdown("### Nuevo Servicio")
    with st.form("form_servicio", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del servicio *", placeholder="Ej: Edenor Febrero")
            tipo   = st.selectbox("Tipo de servicio *", list(SERVICE_ICONS.keys()))
            monto  = st.text_input("Monto (opcional)", placeholder="Ej: 15000")
        with col2:
            fecha_venc  = st.date_input("Fecha de vencimiento *", min_value=date.today())
            repeticion  = st.selectbox("Repetición", ["Sin repetición", "Mensual", "Bimestral", "Trimestral", "Anual"])
            notas       = st.text_area("Notas (opcional)", height=80, placeholder="Número de cuenta, proveedor...")

        submitted = st.form_submit_button("✅ Agregar servicio", use_container_width=True, type="primary")

        if submitted:
            if not nombre:
                st.error("El nombre es obligatorio.")
            else:
                nuevo = {
                    "nombre": nombre,
                    "tipo": tipo,
                    "fecha_vencimiento": fecha_venc.strftime("%Y-%m-%d"),
                    "monto": monto,
                    "repeticion": repeticion,
                    "notas": notas,
                }
                data["servicios"].append(nuevo)
                save_data(data)
                st.success(f"✅ Servicio **{nombre}** agregado correctamente.")
                st.rerun()

    # Tabla resumen
    if data["servicios"]:
        st.markdown("---")
        st.markdown("### 📊 Tabla resumen")
        rows = []
        for s in data["servicios"]:
            estado_key, estado_label = get_estado(s["fecha_vencimiento"], dias_ant)
            fv_fmt = datetime.strptime(s["fecha_vencimiento"],"%Y-%m-%d").strftime("%d/%m/%Y")
            rows.append({
                "Servicio": s["nombre"],
                "Tipo": s["tipo"],
                "Vencimiento": fv_fmt,
                "Monto": s.get("monto","—"),
                "Estado": estado_label,
                "Repetición": s.get("repeticion","—"),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)

        # Exportar CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Exportar CSV",
            data=csv,
            file_name="vencimientos.csv",
            mime="text/csv",
        )
