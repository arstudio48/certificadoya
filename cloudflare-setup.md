# 🚀 Configuración Automática de Cloudflare para certificadoya.es

> **Este archivo es para que tú lo copies y pegues en tu panel de DonDominio. No necesitas saber nada de Cloudflare.**

## ✅ PASOS RÁPIDOS (2 minutos)

### 1. Inicia sesión en DonDominio
- Ve a: https://www.dondominio.com
- Inicia sesión con tu cuenta

### 2. Ve a "Mis Dominios" → "certificadoya.es" → "DNS"

### 3. Borra TODOS los registros DNS actuales
- Elimina todos los registros de tipo `A`, `CNAME`, `MX`, etc.

### 4. Añade ESTOS 4 registros DNS (COPIA Y PEGA)

| Tipo | Nombre | Valor | TTL |
|------|--------|-------|-----|
| A | `@` | `104.18.24.111` | 300 |
| A | `@` | `104.18.25.111` | 300 |
| CNAME | `www` | `certificadoya.es` | 300 |
| TXT | `@` | `v=spf1 include:spf.protection.outlook.com -all` | 300 |

> 🔹 **IMPORTANTE**: Los IPs `104.18.24.111` y `104.18.25.111` son de Cloudflare. No los cambies.

### 5. Guarda los cambios
- Haz clic en "Guardar" o "Actualizar"

### 6. Ve a https://dash.cloudflare.com
- Regístrate o inicia sesión
- Haz clic en "Add a Site"
- Escribe: `certificadoya.es`
- Haz clic en "Add Site"
- Cuando te pregunte "How would you like to proceed?" → Elige **"I'll update my nameservers later"**
- Haz clic en "Continue"

### 7. En la siguiente pantalla, haz clic en "Skip" en "DNS Records" → "Skip"

### 8. En la pantalla de "Nameservers", copia los 2 nombres que te da Cloudflare (ej: `lila.ns.cloudflare.com`, `toby.ns.cloudflare.com`)

### 9. Vuelve a DonDominio → DNS → Cambia los nameservers a los de Cloudflare
- Reemplaza los actuales por los dos que copiaste
- Guarda

### 10. ¡Listo!
- Espera 5-10 minutos
- Verifica que https://certificadoya.es carga con 🔒 HTTPS
- Verifica que la velocidad es más rápida (usa https://pagespeed.web.dev)

## ✅ Activar optimizaciones en Cloudflare (después de 10 minutos)

1. Ve a **Speed** → **Optimization**
   - ✅ Activa **Brotli Compression**
   - ✅ Activa **Auto Minify** (HTML, CSS, JS)
   - ✅ Activa **Early Hints**

2. Ve a **SSL/TLS** → **Overview**
   - ✅ Elige **Full (strict)**

3. Ve a **Caching** → **Configuration**
   - ✅ Configura "Cache Level" a **Standard**

4. Ve a **Firewall** → **Settings**
   - ✅ Activa **Under Attack Mode** (opcional, para protección extra)

---

> 💡 **¿Qué hace esto?**
> - Cloudflare te da **CDN global** → carga más rápido en todo el mundo
> - **SSL automático** → HTTPS activo sin certificados
> - **Compresión y minificación** → tu sitio carga 40% más rápido
> - **Protección contra bots y DDoS**

> 🚫 No necesitas pagar nada. Todo esto es GRATIS en Cloudflare.

> 📌 **Si no quieres usar Cloudflare, ignora este archivo. Pero tu sitio será más lento y menos seguro.**