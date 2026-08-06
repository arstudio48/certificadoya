#!/usr/bin/env python3
"""
Inyecta el CSS del menú overlay en archivos que ya tienen mobile-overlay
pero aún no tienen el CSS (mobileFadeIn).
"""
import glob
import re

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
  }
  .mobile-overlay-close {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 36px;
    height: 36px;
    border: none;
    background: #f5f5f5;
    border-radius: 50%;
    font-size: 1.1rem;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 2;
  }
  .mobile-overlay-nav {
    margin-top: 3rem;
    display: flex;
    flex-direction: column;
  }
  .mobile-overlay-nav a {
    display: block;
    padding: 0.8rem 1.2rem;
    color: #333;
    text-decoration: none;
    font-size: 0.95rem;
    border-bottom: 1px solid #f0f0f0;
  }
  .mobile-overlay-nav a:hover {
    background: #f5f9f0;
  }
  .mobile-overlay-nav strong {
    display: block;
    padding: 0.6rem 1.2rem;
    font-size: 0.82rem;
    color: #9aab8a;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    border-bottom: 1px solid #f0f0f0;
  }
  .mobile-overlay-nav .buscador-wrapper {
    padding: 0.8rem 1.2rem;
    border-bottom: 1px solid #f0f0f0;
  }
  .mobile-overlay-nav .buscador-wrapper input {
    width: 100%;
    padding: 0.6rem 0.8rem;
    border: 1px solid #ddd;
    border-radius: 8px;
    font-size: 0.9rem;
    font-family: inherit;
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

def inject_css(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Ya tiene el CSS?
    if 'mobileFadeIn' in html:
        return False
    
    # Tiene el overlay HTML?
    if 'mobile-overlay' not in html:
        return False
    
    # Insertar antes de </head>
    head_end = html.find('</head>')
    if head_end == -1:
        return False
    
    html = html[:head_end] + '  <style>' + OVERLAY_CSS + '  </style>\n' + html[head_end:]
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html)
    return True

if __name__ == '__main__':
    htmls = glob.glob('**/*.html', recursive=True)
    count = 0
    for f in sorted(htmls):
        if inject_css(f):
            count += 1
    print(f'✅ CSS inyectado en {count} archivos')
