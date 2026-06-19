import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2.39.0?target=deno'

const supabaseUrl = Deno.env.get('SUPABASE_URL') || ''
const supabaseServiceKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') || ''
const supabase = createClient(supabaseUrl, supabaseServiceKey)

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

// IVA/IGIC/IPSI según zona
function getImpuesto(zona: string): { nombre: string; pct: number } {
  const canarias = ['las-palmas', 'tenerife', 'santa-cruz-de-tenerife'];
  const ceutaMelilla = ['ceuta', 'melilla'];
  if (canarias.includes(zona)) return { nombre: 'IGIC', pct: 7 };
  if (ceutaMelilla.includes(zona)) return { nombre: 'IPSI', pct: 4 };
  return { nombre: 'IVA', pct: 21 };
}

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  const url = new URL(req.url)
  const action = url.searchParams.get('action') || ''

  try {
    // ============================================================
    // GET /?action=pdf&id=XXX — Generar HTML imprimible de factura
    // ============================================================
    if (req.method === 'GET' && action === 'pdf') {
      const facturaId = url.searchParams.get('id')
      if (!facturaId) {
        return new Response(JSON.stringify({ error: 'ID de factura requerido' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const { data: factura, error } = await supabase
        .from('facturas')
        .select('*')
        .eq('id', facturaId)
        .maybeSingle()

      if (error || !factura) {
        return new Response(JSON.stringify({ error: 'Factura no encontrada' }), {
          status: 404,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const html = generarFacturaHTML(factura)

      return new Response(html, {
        status: 200,
        headers: {
          'Content-Type': 'text/html; charset=utf-8',
          'Access-Control-Allow-Origin': '*',
        }
      })
    }

    // Only POST for the rest
    if (req.method !== 'POST') {
      return new Response(JSON.stringify({ error: 'Method not allowed' }), {
        status: 405,
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    const body = await req.json()

    // ============================================================
    // ACTION: crear — Crear una factura
    // ============================================================
    if (action === 'crear') {
      const {
        tipo,       // 'cliente' | 'tecnico' | 'agencia'
        cliente_nombre,
        cliente_email,
        cliente_cif,
        concepto,
        direccion,
        base_imponible,
        lead_id,
        tecnico_id,
        inmobiliaria_id,
      } = body

      // Validaciones
      if (!tipo || !['cliente', 'tecnico', 'agencia'].includes(tipo)) {
        return new Response(JSON.stringify({ error: 'Tipo inválido. Valores: cliente, tecnico, agencia' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      if (!cliente_nombre || !concepto) {
        return new Response(JSON.stringify({ error: 'cliente_nombre y concepto son requeridos' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const base = parseFloat(base_imponible) || 0
      const zona = reqBody.zona || ''
      const impuesto = getImpuesto(zona)
      const iva = Math.round((base * impuesto.pct) / 100 * 100) / 100
      const total = base + iva

      // Generar número de factura
      const { data: seqResult } = await supabase.rpc('generar_num_factura')
      let numFactura: string
      if (seqResult) {
        numFactura = seqResult
      } else {
        // Fallback si la función no existe
        const year = new Date().getFullYear()
        const { data: maxFactura } = await supabase
          .from('facturas')
          .select('num_factura')
          .order('id', { ascending: false })
          .limit(1)
          .maybeSingle()

        let nextNum = 1
        if (maxFactura?.num_factura) {
          const parts = maxFactura.num_factura.split('-')
          nextNum = (parseInt(parts[parts.length - 1]) || 0) + 1
        }
        numFactura = `INV-${year}-${String(nextNum).padStart(4, '0')}`
      }

      const { data: factura, error: insertError } = await supabase
        .from('facturas')
        .insert({
          num_factura: numFactura,
          tipo,
          cliente_nombre,
          cliente_email: cliente_email || null,
          cliente_cif: cliente_cif || '',
          concepto,
          direccion: direccion || '',
          base_imponible: base,
          iva,
          total,
          lead_id: lead_id || null,
          tecnico_id: tecnico_id || null,
          inmobiliaria_id: inmobiliaria_id || null,
        })
        .select()
        .single()

      if (insertError) {
        console.error('Error creating invoice:', insertError)
        return new Response(JSON.stringify({ error: 'Error al crear factura' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({
        success: true,
        factura,
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: listar — Listar facturas con filtros
    // ============================================================
    if (action === 'listar') {
      const {
        tipo,
        cliente_email,
        tecnico_id,
        inmobiliaria_id,
        lead_id,
        limite = 50,
      } = body

      let query = supabase
        .from('facturas')
        .select('*')
        .order('created_at', { ascending: false })
        .limit(Math.min(limite, 200))

      if (tipo) query = query.eq('tipo', tipo)
      if (cliente_email) query = query.eq('cliente_email', cliente_email)
      if (tecnico_id) query = query.eq('tecnico_id', tecnico_id)
      if (inmobiliaria_id) query = query.eq('inmobiliaria_id', inmobiliaria_id)
      if (lead_id) query = query.eq('lead_id', lead_id)

      const { data: facturas, error } = await query

      if (error) {
        console.error('Error listing invoices:', error)
        return new Response(JSON.stringify({ error: 'Error al listar facturas' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({
        success: true,
        facturas: facturas || [],
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // ACTION: pdf-email — Generar factura HTML filtrada por email
    // ============================================================
    if (action === 'pdf-email') {
      const { cliente_email } = body
      if (!cliente_email) {
        return new Response(JSON.stringify({ error: 'Email requerido' }), {
          status: 400,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      const { data: facturas, error } = await supabase
        .from('facturas')
        .select('*')
        .eq('cliente_email', cliente_email)
        .order('created_at', { ascending: false })

      if (error) {
        return new Response(JSON.stringify({ error: 'Error al buscar facturas' }), {
          status: 500,
          headers: { ...corsHeaders, 'Content-Type': 'application/json' }
        })
      }

      return new Response(JSON.stringify({
        success: true,
        facturas: facturas || [],
      }), {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      })
    }

    // ============================================================
    // Unknown action
    // ============================================================
    return new Response(JSON.stringify({
      error: `Acción desconocida: "${action}". Acciones válidas: crear, listar, pdf, pdf-email`
    }), {
      status: 400,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })

  } catch (error) {
    console.error('Error en gestion-facturas:', error)
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    })
  }
})

function generarFacturaHTML(factura: any): string {
  const zona = String(factura.zona || '')
  const impuestoFactura = getImpuesto(zona)
  const fecha = factura.created_at
    ? new Date(factura.created_at).toLocaleDateString('es-ES', {
        day: 'numeric', month: 'long', year: 'numeric'
      })
    : '—'

  return `<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Factura ${factura.num_factura} — CertificadoYa</title>
<style>
  @page { margin: 2cm; }
  *, *::before, *::after { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family: 'DM Sans', -apple-system, sans-serif;
    color: #20201f;
    line-height: 1.5;
    padding: 2rem;
    max-width: 800px;
    margin: 0 auto;
  }
  .invoice-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 2rem;
    padding-bottom: 1.5rem;
    border-bottom: 2px solid #16a34a;
  }
  .invoice-header .brand h1 {
    font-size: 1.4rem;
    color: #16a34a;
    font-weight: 700;
  }
  .invoice-header .brand p {
    font-size: .85rem;
    color: #6b7280;
    margin-top: .2rem;
  }
  .invoice-num {
    text-align: right;
  }
  .invoice-num h2 {
    font-size: 1.2rem;
    font-weight: 700;
    color: #20201f;
  }
  .invoice-num .fecha {
    color: #6b7280;
    font-size: .85rem;
    margin-top: .25rem;
  }
  .invoice-info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.5rem;
    margin-bottom: 2rem;
  }
  .invoice-info h3 {
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: .05em;
    color: #9ca3af;
    margin-bottom: .4rem;
  }
  .invoice-info p {
    font-size: .92rem;
    color: #20201f;
  }
  table {
    width: 100%;
    border-collapse: collapse;
    margin-bottom: 2rem;
  }
  th {
    background: #f0f2ef;
    text-align: left;
    padding: .7rem .85rem;
    font-size: .78rem;
    text-transform: uppercase;
    letter-spacing: .03em;
    color: #6b7280;
    font-weight: 600;
  }
  td {
    padding: .7rem .85rem;
    border-bottom: 1px solid #e5e7eb;
    font-size: .88rem;
  }
  .totals {
    margin-left: auto;
    width: 300px;
  }
  .totals table { margin-bottom: 0; }
  .totals td {
    border: none;
    padding: .4rem .85rem;
    font-size: .88rem;
  }
  .totals .total-row td {
    font-weight: 700;
    font-size: 1.1rem;
    color: #16a34a;
    border-top: 2px solid #16a34a;
    padding-top: .6rem;
  }
  .footer-note {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
    font-size: .78rem;
    color: #9ca3af;
    text-align: center;
  }
  @media print {
    body { padding: 0; }
    .no-print { display: none; }
  }
  .btn-print {
    display: inline-block;
    background: #16a34a;
    color: white;
    border: none;
    padding: .6rem 1.2rem;
    border-radius: 8px;
    font-family: 'DM Sans', sans-serif;
    font-size: .85rem;
    font-weight: 600;
    cursor: pointer;
    margin-bottom: 1rem;
  }
  .btn-print:hover { background: #15803d; }
</style>
</head>
<body>
  <div class="no-print" style="text-align:center;margin-bottom:1rem">
    <button class="btn-print" onclick="window.print()">🖨️ Imprimir / Guardar PDF</button>
  </div>

  <div class="invoice-header">
    <div class="brand">
      <h1>CertificadoYa</h1>
      <p>CIF pendiente<br>Calle Ejemplo, 28001 Madrid<br>info@certificadoya.es</p>
    </div>
    <div class="invoice-num">
      <h2>FACTURA ${factura.num_factura}</h2>
      <p class="fecha">${fecha}</p>
    </div>
  </div>

  <div class="invoice-info">
    <div>
      <h3>Cliente</h3>
      <p><strong>${factura.cliente_nombre}</strong></p>
      ${factura.cliente_cif ? `<p>CIF: ${factura.cliente_cif}</p>` : ''}
      ${factura.cliente_email ? `<p>${factura.cliente_email}</p>` : ''}
      ${factura.direccion ? `<p>${factura.direccion}</p>` : ''}
    </div>
    <div>
      <h3>Datos de la factura</h3>
      <p>Nº: ${factura.num_factura}</p>
      <p>Fecha: ${fecha}</p>
    </div>
  </div>

  <table>
    <thead>
      <tr>
        <th>Concepto</th>
        <th style="text-align:right">Base Imponible</th>
        <th style="text-align:right">IVA</th>
        <th style="text-align:right">Total</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>${factura.concepto}</td>
        <td style="text-align:right">${Number(factura.base_imponible).toFixed(2)} €</td>
        <td style="text-align:right">${Number(factura.iva).toFixed(2)} €</td>
        <td style="text-align:right"><strong>${Number(factura.total).toFixed(2)} €</strong></td>
      </tr>
    </tbody>
  </table>

  <div class="totals">
    <table>
      <tr>
        <td>Base Imponible</td>
        <td style="text-align:right">${Number(factura.base_imponible).toFixed(2)} €</td>
      </tr>
      <tr>
        <td>${impuestoFactura.nombre} ${impuestoFactura.pct}%</td>
        <td style="text-align:right">${Number(factura.iva).toFixed(2)} €</td>
      </tr>
      <tr class="total-row">
        <td>TOTAL</td>
        <td style="text-align:right">${Number(factura.total).toFixed(2)} €</td>
      </tr>
    </table>
  </div>

  <div class="footer-note">
    <p>CertificadoYa — ArtStudio · ${fecha}</p>
    <p style="margin-top:.3rem">Gracias por confiar en nosotros.</p>
  </div>
</body>
</html>`
}
