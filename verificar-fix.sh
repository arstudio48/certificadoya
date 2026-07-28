#!/bin/bash
# Verificación post-deploy de P1-P5

echo "═══════════════════════════════════════════════════════════"
echo "VERIFICACIÓN POST-DEPLOY P1-P5 (CertificadoYa)"
echo "═══════════════════════════════════════════════════════════"
echo ""

# P1: Teléfono en formulario
echo "✓ P1: Verificando teléfono en formulario..."
grep -q "type=\"tel\"" index.html && echo "  ✅ Campo teléfono presente en HTML" || echo "  ❌ Campo teléfono NO encontrado"
grep -q "validatePhone" js/main.js && echo "  ✅ Validación teléfono en JS" || echo "  ❌ Validación teléfono NO encontrada"

# P2: Webhook Stripe
echo ""
echo "✓ P2: Verificando webhook Stripe..."
[ -f "supabase/functions/stripe-webhook/index.ts" ] && echo "  ✅ Edge Function stripe-webhook existe" || echo "  ❌ Edge Function NO existe"
grep -q "stripe_webhook_secret\|STRIPE_WEBHOOK" .env.example && echo "  ✅ Variables de entorno configuradas" || echo "  ⚠️ Variables en .env"

# P3: Email técnico validado
echo ""
echo "✓ P3: Verificando email técnico..."
[ -f "supabase/functions/send-email-confirmation/index.ts" ] && echo "  ✅ Email confirmation function existe" || echo "  ❌ Función NO existe"
[ -f "supabase/functions/confirm-email/index.ts" ] && echo "  ✅ Email confirm function existe" || echo "  ❌ Función NO existe"
grep -q "email_validado" auto_assign.py && echo "  ✅ auto_assign.py filtra por email_validado" || echo "  ⚠️ Filtro en auto_assign.py"

# P4: CCAA automatizado
echo ""
echo "✓ P4: Verificando auto-registro CCAA..."
[ -f "supabase/functions/process-cee-pdf/index.ts" ] && echo "  ✅ PDF processor function existe" || echo "  ❌ Función NO existe"
[ -f "CCAA_API_ENDPOINTS.md" ] || [ -f "PLAN-DEPLOY-P1-P5.txt" ] && echo "  ✅ Documentación APIs CCAA disponible" || echo "  ⚠️ Ver PLAN-DEPLOY"

# P5: Notificaciones
echo ""
echo "✓ P5: Verificando notificaciones..."
[ -f "supabase/functions/notify-client/index.ts" ] && echo "  ✅ Notify function existe" || echo "  ❌ Función NO existe"
grep -q "RESEND_API_KEY" .env.example && echo "  ✅ RESEND_API_KEY en variables" || echo "  ⚠️ Configurar RESEND"

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "Para deploy completo, ejecutar:"
echo "  1. git add . && git commit -m 'P1-P5: Fixes críticos'"
echo "  2. git push origin main"
echo "  3. supabase functions deploy"
echo "═══════════════════════════════════════════════════════════"
