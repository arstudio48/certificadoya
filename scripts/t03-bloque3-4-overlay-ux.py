#!/usr/bin/env python3
"""
T0.3 Bloques 3+4: Menú overlay mejorado + UX móvil.
- B3: Animación overlay, buscador SVG roto, cierre mejorado
- B4: Hero móvil, CTA, header, tipografía responsive
"""
import glob, os, re

web_root = '/home/arturo/certificadoya'

# ─── SVG PATH FIX ───────────────────────────────────────────────────
BROKEN_SVG = '<path d="m21 21-4.60-29.35"/>'
FIXED_SVG  = '<path d="M21 21l-4.35-4.35"/>'

# ─── ACORDEON JS MEJORADO — animación suave ─────────────────────────
ACCORDION_JS = '''

/* Acordeon overlay con animación suave */
function toggleSection(id){
  var c=document.getElementById('accordion-'+id);
  var b=document.querySelector('[onclick*="'+id+'"]');
  if(!c||!b)return;
  var o=c.style.display!=='none';
  if(o){
    c.style.height=c.scrollHeight+'px';
    requestAnimationFrame(function(){
      c.style.height='0';
      c.style.opacity='0';
    });
    setTimeout(function(){c.style.display='none';c.style.height='';c.style.opacity='';},220);
    b.setAttribute('aria-expanded','false');
    var a=b.querySelector('.accordion-arrow');
    if(a)a.textContent='\\u25B8';
  }else{
    c.style.display='block';
    c.style.height='0';
    c.style.opacity='0';
    requestAnimationFrame(function(){
      c.style.height=c.scrollHeight+'px';
      c.style.opacity='1';
    });
    setTimeout(function(){c.style.height='';c.style.opacity='';},220);
    b.setAttribute('aria-expanded','true');
    var a=b.querySelector('.accordion-arrow');
    if(a)a.textContent='\\u25BE';
  }
}'''

ACCORDION_CSS = '''
  /* Acordeon overlay movil — animado */
  .accordion-toggle{display:flex;align-items:center;justify-content:space-between;width:100%;padding:.8rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border:none;border-bottom:1px solid #f0f0f0;background:none;cursor:pointer;text-align:left;font-family:inherit}
  .accordion-toggle:hover{background:#f5f9f0}
  .accordion-toggle strong{margin:0;padding:0;border:none;display:inline;font-size:inherit;color:inherit;text-transform:inherit;letter-spacing:inherit}
  .accordion-arrow{font-size:.7rem;color:#9aab8a;transition:transform .2s ease}
  .accordion-content{overflow:hidden;transition:height .2s ease,opacity .2s ease}'''

# ─── MEJORAS CSS MOBILE ────────────────────────────────────────────
MOBILE_CSS = '''

/* B4: UX móvil mejorada — hero, CTA, header */
@media (max-width:480px){
  .hero-content h1{font-size:1.3rem !important;line-height:1.3}
  .hero-content p{font-size:.85rem !important;line-height:1.4}
  .btn-cta{padding:.7rem 1rem !important;font-size:.85rem !important;min-height:44px}
  .header-inner{padding:0 .75rem !important;min-height:56px}
  .mobile-overlay-panel{width:100vw !important;max-width:320px}
  .mobile-overlay-nav a{padding:.75rem 1rem !important;font-size:1rem !important;min-height:44px;display:flex;align-items:center}
  .presupuesto-card-v2{padding:1rem 1rem 5rem !important}
  .precio-destacado{margin-bottom:.6rem !important}
  .resultado-box{padding:.75rem !important}
  footer{padding:1.5rem 1rem !important}
  .footer-grid{grid-template-columns:1fr !important;gap:1rem}
}
@media (max-width:600px){
  .mobile-overlay-close{width:40px;height:40px;font-size:1.2rem}
  .mobile-overlay-nav{margin-top:3.5rem}
  .mobile-overlay-panel{padding-bottom:env(safe-area-inset-bottom,1rem)}
}'''

def fix_svg_path(filepath):
    """FIX 1: Reparar SVG del buscador roto"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if BROKEN_SVG not in content:
        return False
    
    content = content.replace(BROKEN_SVG, FIXED_SVG)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def inject_mobile_css(filepath):
    """FIX 2: Inyectar CSS mobile mejorado en el <style> de la cabecera"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if '/* B4: UX móvil mejorada' in content:
        return False
    
    # Buscar último </style> antes de </head>
    head_close = content.find('</head>')
    style_end = content.rfind('</style>', 0, head_close)
    if style_end == -1:
        return False
    
    content = content[:style_end] + MOBILE_CSS + '\n' + content[style_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def upgrade_accordion_js(filepath):
    """FIX 3: Reemplazar toggleSection por versión con animación"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'accordion-overlay-animado' in content:
        return False
    
    # Buscar la función toggleSection actual
    old_js = 'function toggleSection'
    
    # Encontrar si existe la vieja
    idx = content.find('function toggleSection')
    if idx == -1:
        return False
    
    # Encontrar dónde termina (siguiente function o </script> o fin)
    rest = content[idx:]
    # La actual es minificada: function toggleSection(id){...}
    brace_count = 0
    end_idx = idx
    for i, ch in enumerate(rest):
        if ch == '{':
            brace_count += 1
        elif ch == '}':
            brace_count -= 1
            if brace_count == 0:
                end_idx = idx + i + 1
                break
    
    if end_idx == idx:
        return False
    
    old_func = content[idx:end_idx]
    content = content.replace(old_func, ACCORDION_JS.strip(), 1)
    
    # Actualizar CSS accordion si existe la vieja versión
    # (la animada necesita el transition en .accordion-content)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def upgrade_accordion_css(filepath):
    """FIX 4: Actualizar CSS del accordion para incluir transiciones"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'transition:height .2s' in content:
        return False
    
    # Reemplazar el CSS viejo del accordion
    old_css = '.accordion-toggle{display:flex;align-items:center;justify-content:space-between;width:100%;padding:.8rem 1.2rem;font-size:.82rem;color:#9aab8a;text-transform:uppercase;letter-spacing:.05em;border:none;border-bottom:1px solid #f0f0f0;background:none;cursor:pointer;text-align:left;font-family:inherit}'
    
    if old_css not in content:
        return False
    
    # Reemplazar el viejo CSS por el nuevo (con transiciones)
    # Nota: mantenemos el mismo bloque base pero actualizamos .accordion-content y .accordion-arrow
    content = content.replace('.accordion-arrow{font-size:.7rem;color:#9aab8a}', '.accordion-arrow{font-size:.7rem;color:#9aab8a;transition:transform .2s ease}')
    content = content.replace('.accordion-content{overflow:hidden}', '.accordion-content{overflow:hidden;transition:height .2s ease,opacity .2s ease}')
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True


def process_all():
    html_files = glob.glob(os.path.join(web_root, '**/*.html'), recursive=True)
    
    counts = {'svg_fixed': 0, 'css_mobile': 0, 'accordion_js': 0, 'accordion_css': 0, 'errors': []}
    
    for fpath in sorted(html_files):
        if 'node_modules' in fpath:
            continue
        rel = os.path.relpath(fpath, web_root)
        
        try:
            if fix_svg_path(fpath):
                print(f"  ✓ SVG  {rel}")
                counts['svg_fixed'] += 1
        except Exception as e:
            print(f"  ✗ SVG {rel}: {e}")
            counts['errors'].append(rel)
        
        try:
            if inject_mobile_css(fpath):
                print(f"  ✓ CSSm {rel}")
                counts['css_mobile'] += 1
        except Exception as e:
            print(f"  ✗ CSSm {rel}: {e}")
            counts['errors'].append(rel)
        
        try:
            if upgrade_accordion_js(fpath):
                print(f"  ✓ JSac {rel}")
                counts['accordion_js'] += 1
        except Exception as e:
            print(f"  ✗ JSac {rel}: {e}")
            counts['errors'].append(rel)
        
        try:
            if upgrade_accordion_css(fpath):
                print(f"  ✓ CSac {rel}")
                counts['accordion_css'] += 1
        except Exception as e:
            print(f"  ✗ CSac {rel}: {e}")
            counts['errors'].append(rel)
    
    print(f"\n=== RESUMEN B3+B4 ===")
    print(f"  SVG reparados:  {counts['svg_fixed']}")
    print(f"  CSS mobile:     {counts['css_mobile']}")
    print(f"  Accordion JS:   {counts['accordion_js']}")
    print(f"  Accordion CSS:  {counts['accordion_css']}")
    if counts['errors']:
        print(f"  Errores:        {len(counts['errors'])}")
        for e in counts['errors'][:10]:
            print(f"    - {e}")
    print(f"===================")


if __name__ == '__main__':
    process_all()
