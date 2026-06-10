#!/usr/bin/env python3
"""
Aplica menú overlay moderno a todos los HTML del sitio.
Reemplaza el viejo dropdown .mobile-menu por un overlay off-canvas desde la derecha.
"""
import glob
import re
import os

# ── CSS a inyectar en <head> ──
OVERLAY_CSS = """
/* Menú overlay móvil */
@media (max-width: 600px) {
  .mobile-overlay {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 1000;
  }
  .mobile-overlay.open {
    display: flex;
  }
  .mobile-overlay-bg {
    position: absolute;
    inset: 0;
    background: rgba(0,0,0,0.5);
    animation: mobileFadeIn 0.2s ease;
  }
  .mobile-overlay-panel {
    position: absolute;
    top: 0;
    right: 0;
    bottom: 0;
    width: min(85vw, 320px);
    background: #fff;
    overflow-y: auto;
    animation: mobileSlideIn 0.25s ease;
    padding: 1.2rem 0;
    box-shadow: -4px 0 20px rgba(0,0,0,0.1);
  }
  .mobile-overlay-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 36px;
    height: 36px;
    border: none;
    background: #f0f0f0;
    border-radius: 50%;
    font-size: 1.2rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
    color: #555;
    transition: background 0.15s;
  }
  .mobile-overlay-close:hover {
    background: #e0e0e0;
  }
  .mobile-overlay-nav {
    margin-top: 3rem;
    display: flex;
    flex-direction: column;
  }
  .mobile-overlay-nav a {
    display: block;
    padding: 0.7rem 1.2rem;
    color: #333;
    text-decoration: none;
    font-size: 0.95rem;
    border-bottom: 1px solid #f0f0f0;
    transition: background 0.15s;
  }
  .mobile-overlay-nav a:hover {
    background: #f5f9f0;
    color: #547c24;
  }
  .mobile-overlay-nav a.btn-overlay {
    margin: 0.5rem 1rem;
    padding: 0.7rem 1rem;
    background: #547c24;
    color: #fff;
    border-radius: 10px;
    text-align: center;
    font-weight: 600;
    border: none;
  }
  .mobile-overlay-nav a.btn-overlay:hover {
    background: #43691e;
  }
  .mobile-overlay-nav strong {
    display: block;
    padding: 0.6rem 1.2rem;
    font-size: 0.82rem;
    color: #9aab8a;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #f0f0f0;
    margin-top: 0.5rem;
  }
  @keyframes mobileFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
  }
  @keyframes mobileSlideIn {
    from { transform: translateX(100%); }
    to { transform: translateX(0); }
  }
}
"""

# ── Nuevo JS para overlay ──
OVERLAY_JS = """<!-- Menú overlay JS -->
<script>
(function(){
  var btn = document.getElementById('hamburger-btn');
  var overlay = document.getElementById('mobile-overlay');
  var panel = document.getElementById('mobile-overlay-panel');
  var bg = document.getElementById('mobile-overlay-bg');
  var closeBtn = document.getElementById('mobile-overlay-close');
  if (!btn || !overlay) return;
  function openM(){
    overlay.classList.add('open');
    btn.classList.add('active');
    btn.setAttribute('aria-expanded', 'true');
    document.body.style.overflow = 'hidden';
  }
  function closeM(){
    overlay.classList.remove('open');
    btn.classList.remove('active');
    btn.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
  }
  btn.onclick = function(e){
    e.stopPropagation();
    overlay.classList.contains('open') ? closeM() : openM();
  };
  if (bg) bg.onclick = closeM;
  if (closeBtn) closeBtn.onclick = closeM;
  overlay.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click', closeM);
  });
  document.addEventListener('keydown', function(e){
    if (e.key === 'Escape' && overlay.classList.contains('open')) closeM();
  });
})();
</script>"""


def find_mobile_menu_content(html):
    """
    Encuentra el bloque mobile-menu y extrae su contenido interior.
    Devuelve (inner_content, old_block) o (None, None) si no hay match.
    """
    # Patrón para encontrar la apertura (con whitespace flexible)
    m = re.search(r'<div class="mobile-menu" id="mobile-menu">', html)
    if not m:
        return None, None
    
    start = m.end()
    idx = start
    depth = 1
    
    # Escanea carácter a carácter buscando <div y </div> equilibrados
    while idx < len(html) and depth > 0:
        # Buscar próxima etiqueta <
        tag_start = html.find('<', idx)
        if tag_start == -1:
            break
        
        # Ver si es <div o </div>
        if html[tag_start:tag_start+5] == '<div ' or html[tag_start:tag_start+5] == '<div>':
            depth += 1
            idx = tag_start + 5
        elif html[tag_start:tag_start+6] == '</div>':
            depth -= 1
            if depth == 0:
                # end es después del </div> completo
                inner = html[start:tag_start].strip()
                old_block = html[m.start():tag_start+6]
                return inner, old_block
            idx = tag_start + 6
        else:
            idx = tag_start + 1
    
    return None, None


def find_hamburger_js_block(html):
    """
    Busca el bloque JS hamburger (desde <!-- Hamburger + ... hasta </script>)
    """
    # Buscar el comentario que indica el bloque
    m = re.search(r'<!-- Hamburger.*?-->', html)
    if m:
        # Desde ese comentario hasta el </script> que cierra
        script_end = html.find('</script>', m.end())
        if script_end != -1:
            return html[m.start():script_end + 9]  # +9 for </script>
    
    # Fallback: buscar el patrón específico del JS
    m2 = re.search(r"var btn = document\.getElementById\('hamburger-btn'\)", html)
    if m2:
        # Buscar el <script> más cercano antes de esto
        script_start = html.rfind('<script', 0, m2.start())
        if script_start == -1:
            return None
        script_end = html.find('</script>', m2.start())
        if script_end == -1:
            return None
        return html[script_start:script_end + 9]
    
    return None


def add_overlay_css(html):
    """
    Agrega el CSS del overlay dentro del <head> si no existe ya.
    """
    if 'mobileFadeIn' in html:
        return html  # ya tiene el CSS
    
    # Insertar antes del </head>
    head_end = html.find('</head>')
    if head_end == -1:
        return html
    
    return html[:head_end] + '\n  <style>' + OVERLAY_CSS + '  </style>\n' + html[head_end:]


def process_file(filepath):
    """Procesa un archivo HTML, aplicando todas las transformaciones."""
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    original = html
    modified = False
    
    # 1. Extraer contenido del mobile-menu actual
    inner, old_block = find_mobile_menu_content(html)
    if inner is None:
        print(f"  ✗ No se encontró mobile-menu en {filepath}")
        return False
    
    # 2. Reemplazar el bloque mobile-menu por overlay
    new_overlay = f"""    <!-- Overlay menú móvil -->
    <div class="mobile-overlay" id="mobile-overlay">
      <div class="mobile-overlay-bg" id="mobile-overlay-bg"></div>
      <div class="mobile-overlay-panel" id="mobile-overlay-panel">
        <button class="mobile-overlay-close" id="mobile-overlay-close" aria-label="Cerrar menú">✕</button>
        <nav class="mobile-overlay-nav">
{inner}
        </nav>
      </div>
    </div>"""
    
    html = html.replace(old_block, new_overlay, 1)
    
    # 3. Reemplazar JS hamburger por nuevo JS overlay
    old_js = find_hamburger_js_block(html)
    if old_js is not None:
        html = html.replace(old_js, OVERLAY_JS, 1)
    else:
        # Si no hay JS block, añadirlo antes de </body>
        body_end = html.find('</body>')
        if body_end != -1:
            html = html[:body_end] + '\n' + OVERLAY_JS + '\n' + html[body_end:]
    
    # 4. Añadir CSS overlay al head
    html = add_overlay_css(html)
    
    # 5. Limpiar buscador-wrapper duplicado dentro del overlay (si existía en old mobile-menu y ahora está dentro del nav)
    # Esto es un fix para index.html que tiene .buscador-wrapper dentro del mobile-menu
    # Ahora está dentro de .mobile-overlay-nav, el CSS se aplica igual
    
    if html != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"  ✓ {filepath}")
        return True
    else:
        print(f"  ~ Sin cambios en {filepath}")
        return False


def main():
    # Buscar todos los HTMLs en la raíz y subdirectorios
    files = []
    for root, dirs, fnames in os.walk('/home/arturo/certificadoya'):
        # Saltar node_modules, .git, scripts
        skip = {'node_modules', '.git', '__pycache__', '.hermes'}
        dirs[:] = [d for d in dirs if d not in skip]
        
        for fname in fnames:
            if fname.endswith('.html'):
                files.append(os.path.join(root, fname))
    
    print(f"📁 Archivos HTML encontrados: {len(files)}")
    
    count = 0
    for fp in sorted(files):
        try:
            if process_file(fp):
                count += 1
        except Exception as e:
            print(f"  ✗ Error en {fp}: {e}")
    
    print(f"\n✅ Archivos modificados: {count}/{len(files)}")


if __name__ == '__main__':
    main()
