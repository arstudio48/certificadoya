#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Monitor BOPA de ayudas al alquiler
Detecta nuevas publicaciones oficiales relacionadas con ayudas al alquiler,
busca los códigos SB137971951 o AYUD202547272 (con normalización robusta),
descarga el PDF, extrae texto (con fallback a OCR) y envía una única alerta
por Telegram y correo electrónico.
"""

import os
import re
import sys
import json
import hashlib
import sqlite3
import logging
import datetime
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

# PDF extraction
try:
    from pdfminer.high_level import extract_text as pdfminer_extract
except ImportError:
    pdfminer_extract = None

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

# OCR
try:
    import pytesseract
    from PIL import Image
except ImportError:
    pytesseract = None
    Image = None

# Configuración desde variables de entorno (se asume que .env ya está cargado por Hermes)
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', '308824075')  # chat_id del usuario
EMAIL_SMTP_SERVER = os.getenv('EMAIL_SMTP_SERVER')
EMAIL_SMTP_PORT = int(os.getenv('EMAIL_SMTP_PORT', '587'))
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
EMAIL_TO = os.getenv('EMAIL_TO', EMAIL_USER)

# Base del BOPA (Boletín Oficial del Principado de Asturias)
BOPA_BASE = 'https://www.sast.juntaes.es'
BOPA_SEARCH_URL = urljoin(BOPA_BASE, '/bopa/search')  # ajustar si el endpoint es distinto

# Palabras clave para filtrar
KEYWORDS = [
    'ayudas al alquiler',
    'alquiler de vivienda',
    'AYUD0302T05',
    'programa de ayudas al alquiler'
]

# Códigos objetivo (sin separadores)
CODIGOS_OBJETIVO = {
    'SB137971951',
    'AYUD202547272'
}

# Base de datos de estado
DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'bofa_monitor.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# Logging
LOG_PATH = os.path.join(os.path.dirname(__file__), '..', 'logs', 'bofa_monitor.log')
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
logging.basicConfig(
    filename=LOG_PATH,
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def normalizar(texto: str) -> str:
    """Elimina todo lo que no sea A-Z0-9 y pasa a mayúsculas."""
    return re.sub(r'[^A-Z0-9]', '', texto.upper())

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS avisos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE,
            hash TEXT,
            titulo TEXT,
            fecha_publicacion TEXT,
            codigo_detectado TEXT,
            fecha_primera_deteccion TEXT,
            notificado_telegram INTEGER DEFAULT 0,
            notificado_email INTEGER DEFAULT 0,
            estado_extraccion TEXT,
            error TEXT
        )
    ''')
    conn.commit()
    conn.close()

def obtener_listado_bopa():
    """
    Intenta obtener listado de disposiciones recientes del BOPA.
    Si no hay RSS, se hace una búsqueda genérica por palabras clave.
    Devuelve lista de dicts con url, titulo, fecha.
    """
    # Intentamos RSS primero (ejemplo genérico)
    rss_url = urljoin(BOPA_BASE, '/bopa/rss')
    try:
        r = requests.get(rss_url, timeout=15)
        if r.status_code == 200 and '<rss' in r.text.lower():
            soup = BeautifulSoup(r.content, 'xml')
            items = []
            for item in soup.find_all('item'):
                titulo = item.title.text if item.title else ''
                link = item.link.text if item.link else ''
                pubdate = item.pubDate.text if item.pubDate else ''
                items.append({
                    'titulo': titulo.strip(),
                    'url': link.strip(),
                    'fecha': pubdate.strip()
                })
            return items
    except Exception as e:
        logging.warning(f'RSS no disponible: {e}')

    # Fallback: búsqueda en el sitio con palabras clave
    resultados = []
    for kw in KEYWORDS:
        try:
            params = {'q': kw, 'sort': 'date', 'order': 'desc'}
            r = requests.get(BOPA_SEARCH_URL, params=params, timeout=15)
            if r.status_code != 200:
                continue
            soup = BeautifulSoup(r.text, 'html.parser')
            # Asumimos que cada resultado está en <article> o <div class="resultado">
            for tag in soup.find_all(['article', 'div'], class_=re.compile('resultado|item|entry', re.I)):
                titulo_tag = tag.find(['h2', 'h3', 'a'])
                titulo = titulo_tag.get_text(strip=True) if titulo_tag else ''
                link_tag = tag.find('a', href=True)
                url = urljoin(BOPA_BASE, link_tag['href']) if link_tag else ''
                # Intentamos extraer fecha
                fecha_tag = tag.find(text=re.compile(r'\d{2}/\d{2}/\d{4}'))
                fecha = fecha_tag.strip() if fecha_tag else ''
                if titulo and url:
                    resultados.append({
                        'titulo': titulo,
                        'url': url,
                        'fecha': fecha
                    })
        except Exception as e:
            logging.warning(f'Error en búsqueda BOPA para "{kw}": {e}')
    # Eliminar duplicados por URL
    visto = set()
    unicos = []
    for r in resultados:
        if r['url'] not in visto:
            visto.add(r['url'])
            unicos.append(r)
    return unicos

def descargar_pdf(url):
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        return r.content
    except Exception as e:
        logging.error(f'Error descargando PDF {url}: {e}')
        return None

def extraer_texto_pdf(pdf_bytes):
    texto = ''
    # Intentamos pdfminer
    if pdfminer_extract:
        try:
            texto = pdfminer_extract(pdf_bytes)
        except Exception as e:
            logging.warning(f'pdfminer falló: {e}')
    # Si aún no hay suficiente texto, probamos PyMuPDF
    if (not texto or len(texto.strip()) < 100) and fitz:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            texto = "\n".join([page.get_text() for page in doc])
            doc.close()
        except Exception as e:
            logging.warning(f'PyMuPDF falló: {e}')
    # Si sigue insuficiente y OCR disponible, usamos OCR
    if (not texto or len(texto.strip()) < 100) and pytesseract and Image:
        try:
            doc = fitz.open(stream=pdf_bytes, filetype='pdf')
            texto_ocr = []
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                texto_ocr.append(pytesseract.image_to_string(img, lang='spa'))
            doc.close()
            texto = "\n".join(texto_ocr)
        except Exception as e:
            logging.warning(f'OCR falló: {e}')
    return texto

def buscar_codigos(texto):
    """Devuelve conjunto de códigos encontrados tras normalización."""
    encontrados = set()
    for linea in texto.splitlines():
        norm = normalizar(linea)
        for codigo in CODIGOS_OBJETIVO:
            if codigo in norm:
                encontrados.add(codigo)
    return encontrados

def enviar_telegram(mensaje):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error('Credenciales de Telegram no configuradas')
        return False
    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {
        'chat_id': TELEGRAM_CHAT_ID,
        'text': mensaje,
        'parse_mode': 'HTML'
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        logging.info('Alerta enviada a Telegram')
        return True
    except Exception as e:
        logging.error(f'Error enviando a Telegram: {e}')
        return False

def enviar_email(asunto, cuerpo):
    if not (EMAIL_SMTP_SERVER and EMAIL_USER and EMAIL_PASSWORD and EMAIL_TO):
        logging.error('Credenciales de email no configuradas')
        return False
    import smtplib
    from email.message import EmailMessage
    msg = EmailMessage()
    msg['Subject'] = asunto
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_TO
    msg.set_content(cuerpo)
    try:
        with smtplib.SMTP(EMAIL_SMTP_SERVER, EMAIL_SMTP_PORT) as smtp:
            smtp.starttls()
            smtp.login(EMAIL_USER, EMAIL_PASSWORD)
            smtp.send_message(msg)
        logging.info('Alerta enviada por email')
        return True
    except Exception as e:
        logging.error(f'Error enviando email: {e}')
        return False

def procesar_documento(doc):
    url = doc['url']
    titulo = doc['titulo']
    fecha_pub = doc['fecha']
    logging.info(f'Procesando: {titulo} - {url}')
    pdf_bytes = descargar_pdf(url)
    if pdf_bytes is None:
        estado = 'error_descarga'
        error = 'No se pudo descargar el PDF'
        guardar_estado(url, titulo, fecha_pub, None, estado, error)
        return
    hash_doc = hashlib.sha256(pdf_bytes).hexdigest()
    texto = extraer_texto_pdf(pdf_bytes)
    if not texto or len(texto.strip()) < 20:
        estado = 'extraccion_insuficiente'
        error = 'Texto extraído insuficiente (posible PDF escaneado sin OCR)'
        guardar_estado(url, titulo, fecha_pub, hash_doc, estado, error)
        return
    codigos = buscar_codigos(texto)
    if not codigos:
        estado = 'sin_codigo'
        error = ''
        guardar_estado(url, titulo, fecha_pub, hash_doc, estado, error)
        return
    # Ya tenemos coincidencia
    codigo_detectado = ','.join(sorted(codigos))
    estado = 'exito'
    error = ''
    # Verificar si ya fue notificado
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, notificado_telegram, notificado_email FROM avisos WHERE url=?', (url,))
    fila = c.fetchone()
    if fila:
        aviso_id, tel_sent, email_sent = fila
        # Si ya fue notificado por ambos canales, no volver a enviar
        if tel_sent and email_sent:
            logging.info(f'Documento ya notificado completamente: {url}')
            conn.close()
            return
        # Actualizar hash y códigos si cambió
        c.execute('''UPDATE avisos SET hash=?, codigo_detectado=?, fecha_primera_deteccion=COALESCE(fecha_primera_deteccion, ?),
                     estado_extraccion=?, error=? WHERE id=?''',
                  (hash_doc, codigo_detectado, datetime.datetime.now().isoformat(),
                   estado, error, aviso_id))
        conn.commit()
        conn.close()
    else:
        # Insertar nuevo registro
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute('''INSERT INTO avisos
                     (url, hash, titulo, fecha_publicacion, codigo_detectado,
                      fecha_primera_deteccion, estado_extraccion, error)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (url, hash_doc, titulo, fecha_pub, codigo_detectado,
                   datetime.datetime.now().isoformat(), estado, error))
        aviso_id = c.lastrowid
        conn.commit()
        conn.close()
    # Preparar mensaje
    mensaje = (f'🚨 <b>Nueva ayuda al alquiler detectada</b>\n'
               f'<b>Título:</b> {titulo}\n'
               f'<b>URL:</b> {url}\n'
               f'<b>Fecha publicación:</b> {fecha_pub}\n'
               f'<b>Código(s) encontrado(s):</b> {codigo_detectado}\n'
               f'<b>Hash documento:</b> {hash_doc[:16]}...')
    # Enviar Telegram
    tel_ok = enviar_telegram(mensaje)
    # Enviar Email
    asunto = f'Alerta BOPA: {titulo}'
    cuerpo = f'''Se ha detectado una nueva publicación del BOPA relacionada con ayudas al alquiler.

Título: {titulo}
URL: {url}
Fecha publicación: {fecha_pub}
Código(s) encontrado(s): {codigo_detectado}
Hash documento: {hash_doc}

Este mensaje se envía automáticamente por el monitor BOPA de ayudas al alquiler.
'''
    email_ok = enviar_email(asunto, cuerpo)
    # Actualizar estado de notificación
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    updates = []
    params = []
    if tel_ok:
        updates.append('notificado_telegram=1')
        params.append(1)
    else:
        updates.append('notificado_telegram=0')
        params.append(0)
    if email_ok:
        updates.append('notificado_email=1')
        params.append(1)
    else:
        updates.append('notificado_email=0')
        params.append(0)
    set_clause = ', '.join(updates)
    c.execute(f'UPDATE avisos SET {set_clause} WHERE id=?', (*params, aviso_id))
    conn.commit()
    conn.close()

def main():
    init_db()
    logging.info('=== Inicio de ejecución del monitor BOPA ===')
    documentos = obtener_listado_bopa()
    logging.info(f'Encontrados {len(documentos)} documentos candidatos')
    for doc in documentos:
        procesar_documento(doc)
    logging.info('=== Fin de ejecución ===')

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logging.exception(f'Error inesperado en el monitor: {e}')
        sys.exit(1)