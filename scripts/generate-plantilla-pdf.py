#!/usr/bin/env python3
"""Genera un PDF profesional de la Plantilla de Informe de Certificación Energética
con certificadoya.es destacado en la portada.
"""

from fpdf import FPDF
import os

class CertificadoPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "B", 8)
            self.set_text_color(84, 124, 36)
            self.cell(0, 6, "CertificadoYa - Plantilla profesional CEE", align="L")
            self.set_font("Helvetica", "", 7)
            self.set_text_color(140, 170, 140)
            self.cell(0, 6, "certificadoya.es", align="R", new_x="LMARGIN", new_y="NEXT")
            self.line(10, 14, 200, 14)
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(140, 170, 140)
        self.cell(0, 10, f"Plantilla profesional de CertificadoYa - certificadoya.es  |  Página {self.page_no()}/{{nb}}", align="C")

    def section_title(self, title):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(67, 99, 29)
        self.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(84, 124, 36)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def sub_title(self, title):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(32, 32, 31)
        self.cell(0, 7, title, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def field_table(self, fields, col_widths=None):
        if col_widths is None:
            col_widths = [55, 135]
        self.set_font("Helvetica", "", 9)
        for label, value in fields:
            self.set_fill_color(243, 249, 235)
            self.set_text_color(32, 32, 31)
            self.set_font("Helvetica", "B", 9)
            x, y = self.get_x(), self.get_y()
            self.cell(col_widths[0], 7, f"  {label}", fill=False, new_x="RIGHT")
            self.set_font("Helvetica", "", 9)
            self.set_text_color(100, 120, 100)
            self.cell(col_widths[1], 7, f"  {value}", new_x="LMARGIN", new_y="NEXT")
            self.ln(0.5)

    def check_row(self, label, options):
        self.set_font("Helvetica", "", 9)
        self.set_text_color(32, 32, 31)
        self.cell(55, 7, f"  {label}")
        self.set_text_color(100, 100, 100)
        self.cell(135, 7, options, new_x="LMARGIN", new_y="NEXT")
        self.ln(0.5)

    def measure_box(self, title, desc="", cost="", ahorro="", mejora_letra=""):
        self.set_fill_color(243, 249, 235)
        y_start = self.get_y()
        self.set_draw_color(84, 124, 36)
        self.rect(10, y_start, 190, 22, style="D")
        self.set_x(13)
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(67, 99, 29)
        self.cell(0, 5, title, new_x="LMARGIN", new_y="NEXT")
        self.set_x(13)
        self.set_font("Helvetica", "", 8)
        self.set_text_color(32, 32, 31)
        self.cell(0, 4, desc, new_x="LMARGIN", new_y="NEXT")
        self.set_x(13)
        self.cell(0, 4, f"Coste: {cost}  |  Ahorro: {ahorro}", new_x="LMARGIN", new_y="NEXT")
        if mejora_letra:
            self.set_x(13)
            self.cell(0, 4, f"Mejora de letra: {mejora_letra}", new_x="LMARGIN", new_y="NEXT")
        self.ln(2)


def generate():
    pdf = CertificadoPDF()
    pdf.alias_nb_pages()
    pdf.set_auto_page_break(auto=True, margin=20)

    # ═══════════════ PORTADA ═══════════════
    pdf.add_page()
    pdf.set_font("Helvetica", "", 10)

    # Barra superior verde
    pdf.set_fill_color(84, 124, 36)
    pdf.rect(0, 0, 210, 4, style="F")
    pdf.ln(15)

    # Logo + marca
    pdf.ln(25)
    pdf.set_xy(10, 45)
    pdf.set_fill_color(84, 124, 36)
    pdf.rect(85, 45, 40, 40, style="F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 36)
    pdf.set_xy(85, 48)
    pdf.cell(40, 35, "C", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(84, 124, 36)
    pdf.cell(0, 10, "CertificadoYa", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(140, 170, 140)
    pdf.cell(0, 6, "certificacion energetica de edificios existentes (CEE)", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_draw_color(84, 124, 36)
    pdf.set_line_width(0.5)
    pdf.line(70, pdf.get_y(), 140, pdf.get_y())
    pdf.ln(3)

    # Destacado: URL de la web
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(32, 32, 31)
    pdf.cell(0, 8, "www.certificadoya.es", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(3)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(140, 170, 140)
    pdf.cell(0, 6, "Tu certificado energetico rapido, facil y al mejor precio", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(32, 32, 31)
    pdf.cell(0, 10, "Informe de Certificacion", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, "de Eficiencia Energetica", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(2)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(100, 120, 100)
    pdf.cell(0, 6, "RD 390/2021  .  Directiva 2010/31/UE", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(10)

    # Caja de referencia
    x_center = 45
    pdf.set_x(x_center)
    pdf.set_draw_color(200, 210, 200)
    pdf.set_fill_color(248, 250, 245)
    pdf.rect(x_center, pdf.get_y(), 120, 40, style="DF")
    pdf.set_x(x_center + 5)
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(32, 32, 31)
    ref_items = [
        ("Inmueble:", "_____________________________"),
        ("Direccion:", "_____________________________"),
        ("Ref. catastral:", "_____________________________"),
        ("Fecha emision:", "____/____/________"),
        ("Expediente:", "CEE-________/________"),
    ]
    y0 = pdf.get_y() + 3
    for i, (label, value) in enumerate(ref_items):
        pdf.set_xy(x_center + 5, y0 + i * 7)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_text_color(32, 32, 31)
        pdf.cell(35, 6, label)
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(120, 140, 120)
        pdf.cell(75, 6, value)

    pdf.ln(45)

    # Pie de portada
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(180, 200, 180)
    pdf.cell(0, 6, "Generado con la plantilla profesional de CertificadoYa  |  certificadoya.es", align="C", new_x="LMARGIN", new_y="NEXT")

    # ═══════════════ PÁGINA 2: DATOS TÉCNICO ═══════════════
    pdf.add_page()
    pdf.section_title("1. Datos del tecnico certificador")
    pdf.field_table([
        ("Nombre completo", "_____________________________"),
        ("Titulacion", "_____________________________"),
        ("No colegiado", "_____________________________"),
        ("Colegio profesional", "_____________________________"),
        ("Telefono", "_____________________________"),
        ("Email", "_____________________________"),
    ])
    pdf.ln(3)

    pdf.section_title("2. Datos del cliente")
    pdf.field_table([
        ("Nombre / Razon social", "_____________________________"),
        ("DNI / CIF", "_____________________________"),
        ("Telefono", "_____________________________"),
        ("Email", "_____________________________"),
    ])
    pdf.ln(3)

    pdf.section_title("3. Descripcion del inmueble")
    pdf.check_row("Tipo de inmueble", "[ ] Vivienda unifamiliar  [ ] Piso  [ ] Local comercial  [ ] Oficina")
    pdf.check_row("Uso", "[ ] Vivienda habitual  [ ] Alquiler  [ ] Venta  [ ] Otro: _______")
    pdf.field_table([
        ("Ano construccion", "________________"),
        ("Superficie util (m2)", "________________"),
        ("Superficie construida (m2)", "________________"),
        ("No de plantas", "________________"),
        ("Orientacion principal", "________________"),
        ("Zona climatica", "________________"),
    ])
    pdf.ln(3)

    pdf.section_title("4. Sistemas energeticos")
    # Simple table
    sistemas = [
        ("Calefaccion", "_____________________________"),
        ("Refrigeracion", "_____________________________"),
        ("Agua caliente (ACS)", "_____________________________"),
        ("Ventilacion", "_____________________________"),
        ("Iluminacion", "_____________________________"),
        ("Energias renovables", "_____________________________"),
    ]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(243, 249, 235)
    pdf.set_text_color(67, 99, 29)
    pdf.cell(50, 7, "  Sistema", fill=True)
    pdf.cell(0, 7, "  Descripcion", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(32, 32, 31)
    for label, val in sistemas:
        pdf.cell(50, 7, f"  {label}")
        pdf.set_text_color(100, 120, 100)
        pdf.cell(0, 7, f"  {val}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(32, 32, 31)
        pdf.ln(0.3)
    pdf.ln(3)

    pdf.section_title("5. Envolvente termica")
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(243, 249, 235)
    pdf.set_text_color(67, 99, 29)
    pdf.cell(50, 7, "  Elemento", fill=True)
    pdf.cell(0, 7, "  Material / Composicion", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(32, 32, 31)
    for label in ["Fachada", "Cubierta", "Suelo", "Ventanas", "Puertas exteriores", "Puentes termicos"]:
        pdf.cell(50, 7, f"  {label}")
        pdf.set_text_color(100, 120, 100)
        pdf.cell(0, 7, "  _____________________________", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(32, 32, 31)
        pdf.ln(0.3)

    # ═══════════════ PÁGINA 3: CALIFICACIÓN ═══════════════
    pdf.add_page()
    pdf.section_title("6. Calificacion energetica obtenida")
    pdf.set_font("Helvetica", "", 9)
    pdf.field_table([
        ("Software utilizado", "_____________________________"),
    ])
    pdf.ln(1)

    # Etiqueta energética visual
    pdf.set_fill_color(84, 124, 36)
    pdf.rect(80, pdf.get_y(), 50, 60, style="F")
    y_label = pdf.get_y()
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 48)
    pdf.set_xy(80, y_label + 5)
    pdf.cell(50, 30, "__", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(80)
    pdf.set_font("Helvetica", "", 8)
    pdf.cell(50, 6, "Calificacion", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(80)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(50, 6, "__ kWh/m2.ano", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 7)
    pdf.set_x(80)
    pdf.cell(50, 5, "Consumo energia primaria", align="C")

    pdf.set_y(y_label + 65)
    pdf.set_font("Helvetica", "", 9)
    pdf.ln(2)

    # Tabla indicadores
    headers = ["Indicador", "Valor", "Limite reglamentario"]
    data = [
        ["Demanda calefaccion", "________ kWh/m2.ano", "________"],
        ["Demanda refrigeracion", "________ kWh/m2.ano", "________"],
    ]
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(243, 249, 235)
    pdf.set_text_color(67, 99, 29)
    col_w = [60, 65, 65]
    for i, h in enumerate(headers):
        pdf.cell(col_w[i], 7, f"  {h}", fill=True)
    pdf.ln()
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(32, 32, 31)
    for row in data:
        for i, val in enumerate(row):
            pdf.set_text_color(100, 120, 100)
            pdf.cell(col_w[i], 6, f"  {val}")
        pdf.ln()

    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 170, 140)
    pdf.cell(0, 5, "Nota: Adjuntar la etiqueta energetica oficial generada por el software reconocido (CE3X, HULC, CYPETHERM, etc.).")
    pdf.ln(8)

    pdf.section_title("7. Medidas de mejora recomendadas")
    pdf.measure_box("Medida 1", "Descripcion: _____________________________", "______ EUR", "______ kWh/ano", "de ___ a ___")
    pdf.measure_box("Medida 2", "Descripcion: _____________________________", "______ EUR", "______ kWh/ano", "de ___ a ___")
    pdf.measure_box("Medida 3 (opcional)", "Descripcion: _____________________________", "______ EUR", "______ kWh/ano")

    pdf.ln(2)
    pdf.set_fill_color(243, 249, 235)
    pdf.set_draw_color(84, 124, 36)
    y_tip = pdf.get_y()
    pdf.rect(10, y_tip, 190, 12, style="DF")
    pdf.set_xy(13, y_tip + 1.5)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(67, 99, 29)
    pdf.multi_cell(184, 4, "Consejo: Incluye al menos 2 medidas de mejora. Una combinacion de aislamiento termico + cambio de sistema de climatizacion suele dar el mejor resultado coste/beneficio.")
    pdf.ln(8)

    pdf.section_title("8. Observaciones y notas del tecnico")
    pdf.set_draw_color(200, 210, 200)
    y_obs = pdf.get_y()
    pdf.rect(10, y_obs, 190, 50, style="D")
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(200, 200, 200)
    for i in range(6):
        pdf.set_xy(13, y_obs + 3 + i * 8)
        pdf.cell(0, 6, "____________________________________________________________________________________")

    pdf.set_y(y_obs + 55)

    pdf.section_title("9. Firmas")
    pdf.ln(5)
    # Firma técnico
    pdf.line(25, pdf.get_y(), 85, pdf.get_y())
    pdf.line(115, pdf.get_y(), 175, pdf.get_y())
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(32, 32, 31)
    pdf.set_xy(25, pdf.get_y() + 1)
    pdf.cell(60, 5, "Tecnico certificador", align="C")
    pdf.set_xy(115, pdf.get_y())
    pdf.cell(60, 5, "Propietario / Solicitante", align="C")
    pdf.ln(8)
    pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(100, 120, 100)
    pdf.set_x(25)
    pdf.cell(60, 4, "No colegiado: ________________", align="C")
    pdf.set_x(115)
    pdf.cell(60, 4, "DNI: ________________", align="C")

    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(140, 170, 140)
    pdf.cell(0, 5, "El presente informe se emite conforme al RD 390/2021 y la Directiva 2010/31/UE.", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 5, "El certificado debe registrarse en el organo competente de la comunidad autonoma correspondiente.", align="C", new_x="LMARGIN", new_y="NEXT")

    # Guardar
    os.makedirs(os.path.join(os.path.dirname(__file__), "..", "descargables"), exist_ok=True)
    output_path = os.path.join(os.path.dirname(__file__), "..", "descargables", "plantilla-informe-energetico.pdf")
    pdf.output(output_path)
    print(f"PDF generado: {output_path}")
    print(f"Paginas: {pdf.page_no()}")
    return output_path

if __name__ == "__main__":
    generate()
