# 📅 Gestor de Vencimientos

Aplicación Streamlit para gestionar vencimientos de servicios (luz, gas, agua, internet, etc.) y enviar alertas automáticas por email.

## 🚀 Instalación

```bash
pip install -r requirements.txt
streamlit run app.py
```

## ⚙️ Configuración de Email (Gmail)

Para usar Gmail necesitás una **App Password** (no tu contraseña normal):

1. Activá la verificación en dos pasos en tu cuenta Google
2. Ingresá a: https://myaccount.google.com/apppasswords
3. Generá una contraseña para "Mail" en "Otro dispositivo"
4. Copiá esa contraseña (16 caracteres) y pegala en la app

**Configuración SMTP:**
- Servidor: `smtp.gmail.com`
- Puerto: `587`

## 📋 Funcionalidades

- ✅ Alta/baja de servicios con fecha de vencimiento
- ✅ Tipos: Electricidad, Gas, Agua, Internet, Teléfono, Alquiler, Seguro, Tarjeta, Otro
- ✅ Alertas visuales: vence hoy / próximamente / vencido
- ✅ Múltiples destinatarios de email
- ✅ Envío manual o automático al verificar alertas
- ✅ Monto, notas y repetición opcional por servicio
- ✅ Exportar tabla a CSV
- ✅ Persistencia en archivo JSON local
