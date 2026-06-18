#!/usr/bin/env python3
"""
Elimina el CSS duplicado del menú móvil de todos los archivos HTML del repositorio.

El CSS duplicado está dentro de etiquetas <style> y ya existe en css/style.css.
Se eliminan SOLO las reglas CSS del menú móvil, sin tocar el resto del CSS ni el HTML.
Si un bloque <style> se queda vacío, se elimina también la etiqueta.
"""

import re
import os

REPO_DIR = r'C:\Users\artur\repos\certificadoya'
D = re.DOTALL
M = re.MULTILINE

# ── Step 1: Remove the full mobile overlay CSS block ──
# Pattern: .mobile-overlay{display:none} ... @media ... @keyframes mobileSlideIn ... }
FULL_OVERLAY = re.compile(
    r'\.mobile-overlay\{display:none\}\s*'
    r'(?:/\*[^*]*\*/\s*)?'
    r'@media\s*\(\s*max-width\s*:\s*600px\s*\)\s*\{'
    r'[\s\S]*?@keyframes\s+mobileSlideIn\s*\{[^}]*\}[^}]*\}\s*',
    D
)

# ── Step 2: Remove individual CSS rules matching mobile menu selectors ──
# These handle both single-line (minified) and multi-line CSS rules
SELECTOR_BASES = [
    r'\.mobile-overlay',
    r'\.mobile-overlay-bg',
    r'\.mobile-overlay-panel',
    r'\.mobile-overlay-close',
    r'\.mobile-overlay-nav',
    r'\.accordion-toggle',
    r'\.accordion-content',
    r'\.accordion-arrow',
    r'\.buscador-resultados',
    r'\.buscador-wrapper',
    r'\.buscador-icono',
    r'\.buscador-input',
    r'\.hamburger',
    r'\.mobile-menu',
    r'@keyframes\s+mobileFadeIn',
    r'@keyframes\s+mobileSlideIn',
]

# Allow any CSS selector characters after the base: letters, digits, dots, hyphens,
# underscores, colons, parentheses, spaces, >, +, ~, commas, #
SEL_CHARS = r'[a-zA-Z0-9._\-\:\(\)\s>+~,#]'

RULE_PATTERNS = []
for base in SELECTOR_BASES:
    pat_str = base + SEL_CHARS + r'*\{[\s\S]*?\}'
    RULE_PATTERNS.append(re.compile(pat_str, D))

# ── Step 3: @media blocks containing hamburger/nav mobile menu ──
# These are blocks like:
# @media(max-width:600px){.hamburger{display:flex}.nav>a,.nav>.buscador-wrapper,.nav>.btn-nav{display:none}.header-inner{position:relative}}
# We match @media followed by { then any content that includes .hamburger then } at the end
# The key is we match from @media through the FINAL } that closes the @media block
HAMBURGER_MEDIA = re.compile(
    r'@media\s*\(\s*max-width\s*:\s*600px\s*\)\s*\{'
    r'[\s\S]*?\.hamburger'
    r'[\s\S]*?\}',
    D
)

# Also handle remaining @media blocks that only contain .nav rules
# These come after the hamburger rules have been removed
NAV_MEDIA = re.compile(
    r'@media\s*\(\s*max-width\s*:\s*600px\s*\)\s*\{'
    r'[\s\S]*?\.nav'
    r'[\s\S]*?\}',
    D
)

# ── Step 4: Cleanup ──

# Empty @media blocks
EMPTY_MEDIA = re.compile(
    r'@media\s*\([^)]*\)\s*\{[\s\n]*\}',
    D
)

# Menu-related comments
MENU_COMMENT = re.compile(
    r'/\*[^*]*Hamburguesa[^*]*\*/', D
)
OVERLAY_COMMENT = re.compile(
    r'/\*[^*]*Men' + '\u00fa' + r'[^*]*overlay[^*]*\*/', D
)

# Stray close-braces from incomplete removal (a line with just `}` or `}}`)
STRAY_BRACES = re.compile(r'^[\s]*\}[\s]*$', M)

# Trailing `}}` at end of CSS rule line: .header-inner{position:relative}} → .header-inner{position:relative}
DOUBLE_BRACE_END = re.compile(r'\}\}\s*$', M)

# `@` followed by nothing meaningful (leftover from @@media)
# e.g. "    @}" or "    @ "
STRAY_AT = re.compile(r'^\s*@[\}\s].*$', M)

# Empty style tag
EMPTY_STYLE = re.compile(r'<style>\s*</style>', D)

# Cleanup whitespace
MULTI_BLANK = re.compile(r'\n\s*\n\s*\n+')


def process_style_content(text):
    """Remove duplicate mobile menu CSS rules from style block content."""
    if not text or not text.strip():
        return text
    
    # Step 1: Remove full overlay block
    text = FULL_OVERLAY.sub('', text)
    
    # Step 2: Remove individual CSS rules
    for pat in RULE_PATTERNS:
        while True:
            new_text = pat.sub('', text, count=1)
            if new_text == text:
                break
            text = new_text
    
    # Step 3: Remove @media blocks with hamburger/nav
    text = HAMBURGER_MEDIA.sub('', text)
    
    # Step 4: Remove any remaining @media blocks with .nav (after hamburger removal)
    text = NAV_MEDIA.sub('', text)
    
    # Step 5: Cleanup
    text = MENU_COMMENT.sub('', text)
    text = OVERLAY_COMMENT.sub('', text)
    text = EMPTY_MEDIA.sub('', text)
    text = STRAY_BRACES.sub('', text)
    text = STRAY_AT.sub('', text)
    
    # Fix double braces at end of lines
    text = DOUBLE_BRACE_END.sub(r'}', text)
    
    text = MULTI_BLANK.sub('\n\n', text)
    
    return text.strip()


def process_file(filepath):
    """Process a single HTML file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        print(f"  Cannot read {filepath}: {e}")
        return False

    original = content
    
    # Find all <style> blocks
    style_blocks = list(re.finditer(r'<style[^>]*>(.*?)</style>', content, D))
    
    for match in reversed(style_blocks):
        full_match = match.group(0)
        style_content = match.group(1)
        new_content = process_style_content(style_content)
        
        if new_content != style_content:
            if new_content:
                new_full = '<style>\n' + new_content + '\n</style>'
            else:
                new_full = ''
            content = content[:match.start()] + new_full + content[match.end():]
    
    # Remove empty style tags
    content = EMPTY_STYLE.sub('', content)
    
    if content != original:
        try:
            with open(filepath, 'w', encoding='utf-8', newline='') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"  Cannot write {filepath}: {e}")
            return False
    
    return False


def main():
    html_files = []
    for root, dirs, files in os.walk(REPO_DIR):
        if '.git' in os.path.normpath(root).split(os.sep):
            continue
        dirname = os.path.basename(root)
        if dirname in ('.git', 'node_modules', '__pycache__'):
            dirs[:] = []
            continue
        for f in files:
            if f.endswith('.html'):
                html_files.append(os.path.join(root, f))
    
    print(f"Found {len(html_files)} HTML files to process")
    
    modified = 0
    errors = 0
    
    for filepath in sorted(html_files):
        try:
            if process_file(filepath):
                relpath = os.path.relpath(filepath, REPO_DIR)
                print(f"  MODIFIED: {relpath}")
                modified += 1
        except Exception as e:
            relpath = os.path.relpath(filepath, REPO_DIR)
            print(f"  ERROR: {relpath}: {e}")
            errors += 1
    
    print(f"\nDone! Modified: {modified}, Errors: {errors}")


if __name__ == '__main__':
    main()
