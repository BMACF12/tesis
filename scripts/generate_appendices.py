import json
import os
from fpdf import FPDF
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.section import WD_ORIENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

# XML helper to remove vertical borders and format tables APA-style in Word
def set_table_borders_apa(table):
    tblPr = table._tbl.tblPr
    # Remove existing borders if any
    for child in tblPr:
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
            
    tblBorders = OxmlElement('w:tblBorders')
    
    # Top border (thick)
    top = OxmlElement('w:top')
    top.set(qn('w:val'), 'single')
    top.set(qn('w:sz'), '12') # 1.5 pt
    top.set(qn('w:space'), '0')
    top.set(qn('w:color'), '000000')
    tblBorders.append(top)
    
    # Bottom border (thick)
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), '000000')
    tblBorders.append(bottom)
    
    # Inside horizontal border (thin)
    insideH = OxmlElement('w:insideH')
    insideH.set(qn('w:val'), 'single')
    insideH.set(qn('w:sz'), '4') # 0.5 pt
    insideH.set(qn('w:space'), '0')
    insideH.set(qn('w:color'), '888888')
    tblBorders.append(insideH)
    
    # Clear left, right and inside vertical borders
    for border_name in ['left', 'right', 'insideV']:
        b = OxmlElement(f'w:{border_name}')
        b.set(qn('w:val'), 'none')
        tblBorders.append(b)
        
    tblPr.append(tblBorders)

class AppendixPDF(FPDF):
    def __init__(self, orientation='P', unit='mm', format='A4'):
        super().__init__(orientation=orientation, unit=unit, format=format)
        self.set_margins(15, 15, 15)
        self.set_auto_page_break(auto=True, margin=15)
        
    def header(self):
        pass
        
    def footer(self):
        self.set_y(-15)
        self.set_font('helvetica', 'I', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Página {self.page_no()}', align='C')

# ==================== PDF GENERATION ====================

def create_appendix_4_pdf(records, promedio_global):
    pdf = AppendixPDF(orientation='L')
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 6, "Apéndice 4", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "EP-03: Calidad de Extracción y Fiabilidad Estructural (Métrica de Jaccard)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font('helvetica', '', 8.5)
    description_text = (
        "Descripción: En el Apéndice 4 se presentan los resultados detallados del Índice de Jaccard obtenidos al evaluar "
        "la calidad de extracción de texto y la fiabilidad estructural en el corpus de pruebas del sistema. Se analizan "
        f"un total de {len(records)} documentos (perfiles de egreso, proyectos curriculares, sílabos, mallas curriculares y "
        "guías de laboratorio) en contraste con el texto extraído por el motor OCR de la plataforma. Los resultados demuestran "
        f"que el sistema alcanza un Promedio Global de Jaccard de {promedio_global} (sobre un óptimo de 1000,00), lo cual valida "
        "la alta precisión de la capa defensiva inicial frente a la documentación de la carrera de Ingeniería de Software."
    )
    pdf.multi_cell(0, 4.2, description_text, align='J', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    col_widths = [142, 50, 40, 35]
    headers = ["ID Documento", "Tipo de Formato", "Índice de Jaccard", "Estado de Extracción"]
    
    x_start = pdf.get_x()
    y_start = pdf.get_y()
    pdf.set_line_width(0.6)
    pdf.line(x_start, y_start, x_start + sum(col_widths), y_start)
    pdf.line(x_start, y_start + 0.8, x_start + sum(col_widths), y_start + 0.8)
    pdf.ln(1.5)
    
    pdf.set_font('helvetica', 'B', 7.5)
    for w, h_text in zip(col_widths, headers):
        align_col = 'C' if w in [40, 35] else 'L'
        pdf.cell(w, 4.5, h_text, border=0, align=align_col)
    pdf.ln(4.5)
    
    y_curr = pdf.get_y()
    pdf.set_line_width(0.3)
    pdf.line(x_start, y_curr, x_start + sum(col_widths), y_curr)
    pdf.ln(1)
    
    pdf.set_font('helvetica', '', 7)
    row_height = 3.3
    
    for r in records:
        file_id = r["id"]
        if len(file_id) > 85:
            ext = ""
            name_part = file_id
            if file_id.endswith(".pdf"):
                ext = ".pdf"
                name_part = file_id[:-4]
            file_id = name_part[:80] + "..." + ext
            
        j_val = r["jaccard"]
        orig_status = r["estado"].lower()
        estado = "Deficiente" if "deficiente" in orig_status else "Óptimo"
        
        pdf.cell(col_widths[0], row_height, file_id, border=0, align='L')
        pdf.cell(col_widths[1], row_height, r["tipo"], border=0, align='L')
        pdf.cell(col_widths[2], row_height, j_val, border=0, align='C')
        pdf.cell(col_widths[3], row_height, estado, border=0, align='C')
        pdf.ln(row_height)
        
    y_end = pdf.get_y()
    pdf.set_line_width(0.4)
    pdf.line(x_start, y_end, x_start + sum(col_widths), y_end)
    
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 4.pdf")
    pdf.output(output_path)
    print(f"Created Apéndice 4 PDF: {output_path}")

def create_appendix_5_pdf(docs_data):
    pdf = AppendixPDF(orientation='L')
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 6, "Apéndice 5", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "EP-04: Matriz de Confusión General Granulada (Evaluación Multietiqueta)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(3)
    
    pdf.set_font('helvetica', '', 8.5)
    description_text = (
        "Descripción: En el Apéndice 5 se detalla la matriz de confusión general granulada y las métricas de rendimiento "
        "asociadas a la evaluación multietiqueta aplicada a los documentos del corpus de pruebas. Para cada documento "
        "(sílabos, mallas curriculares, guías de laboratorio, proyectos curriculares y perfiles de egreso), se contrastan "
        "las decisiones de la Inteligencia Artificial frente a la validación de un experto humano en las diferentes "
        "secciones cognitivas y secciones esenciales para la acreditación. Este desglose permite medir la precisión y "
        "exactitud granular del sistema, identificando áreas de ambigüedad semántica y confirmando la ausencia de "
        "falsos positivos en las clasificaciones."
    )
    pdf.multi_cell(0, 4.2, description_text, align='J', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    col_widths = [68, 16, 14, 34, 54, 16, 14, 34, 17]
    headers = [
        "Secciones del Documento", "Hum.", "IA", "Resultado de la Matriz",
        "Secciones Esenciales", "Hum.", "IA", "Resultado de la Matriz", "Estado"
    ]
    
    for doc_idx, doc in enumerate(docs_data):
        doc_name = doc["doc_name"]
        estado_final = doc["estado_final"]
        accuracy = doc["accuracy"]
        precision = doc["precision"]
        matrix = doc["matrix"]
        rows = doc["rows"]
        
        space_left = pdf.h - pdf.get_y() - 15
        needed_height = 36 + len(rows) * 4
        
        if doc_idx > 0 and space_left < needed_height:
            pdf.add_page()
            
        pdf.set_font('helvetica', 'B', 8)
        pdf.set_fill_color(235, 235, 235)
        pdf.cell(0, 5, f"Documento: {doc_name}", border=0, align='L', fill=True, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        
        x_start = pdf.get_x()
        y_start = pdf.get_y()
        pdf.set_line_width(0.4)
        pdf.line(x_start, y_start, x_start + sum(col_widths), y_start)
        pdf.ln(0.8)
        
        pdf.set_font('helvetica', 'B', 7)
        for w, h_text in zip(col_widths, headers):
            align_col = 'C' if w in [16, 14, 17] else 'L'
            pdf.cell(w, 4.5, h_text, border=0, align=align_col)
        pdf.ln(4.5)
        
        y_curr = pdf.get_y()
        pdf.set_line_width(0.2)
        pdf.line(x_start, y_curr, x_start + sum(col_widths), y_curr)
        pdf.ln(0.8)
        
        pdf.set_font('helvetica', '', 6.5)
        row_height = 3.6
        
        for r_idx, r in enumerate(rows):
            est = estado_final if r_idx == 0 else ""
            
            sec_doc_txt = r[0]
            if len(sec_doc_txt) > 55:
                sec_doc_txt = sec_doc_txt[:52] + "..."
            pdf.cell(col_widths[0], row_height, sec_doc_txt, border=0, align='L')
            
            hum_d = r[1]
            ia_d = r[2]
            res_d = r[3].replace("Verdadero Positivo", "VP").replace("Falso Negativo", "FN").replace("Verdadero Negativo", "VN").replace("Falso Positivo", "FP")
            
            pdf.cell(col_widths[1], row_height, hum_d, border=0, align='C')
            pdf.cell(col_widths[2], row_height, ia_d, border=0, align='C')
            pdf.cell(col_widths[3], row_height, res_d, border=0, align='L')
            
            sec_ess_txt = r[4]
            if len(sec_ess_txt) > 42:
                sec_ess_txt = sec_ess_txt[:39] + "..."
            pdf.cell(col_widths[4], row_height, sec_ess_txt, border=0, align='L')
            
            hum_e = r[5]
            ia_e = r[6]
            res_e = r[7].replace("Verdadero Positivo", "VP").replace("Falso Negativo", "FN").replace("Verdadero Negativo", "VN").replace("Falso Positivo", "FP") if len(r) > 7 else ""
            
            pdf.cell(col_widths[5], row_height, hum_e, border=0, align='C')
            pdf.cell(col_widths[6], row_height, ia_e, border=0, align='C')
            pdf.cell(col_widths[7], row_height, res_e, border=0, align='L')
            
            if est == "APROBADO" or est == "DESCARTADO":
                pdf.set_font('helvetica', 'B', 6.5)
            
            pdf.cell(col_widths[8], row_height, est, border=0, align='C')
            pdf.set_font('helvetica', '', 6.5)
            
            pdf.ln(row_height)
            
        y_end = pdf.get_y()
        pdf.set_line_width(0.3)
        pdf.line(x_start, y_end, x_start + sum(col_widths), y_end)
        pdf.ln(1)
        
        m_widths = [25, 20, 20]
        
        pdf.set_font('helvetica', 'B', 6)
        pdf.cell(m_widths[0], 3, "Matriz de Confusión", border=0, align='L')
        pdf.cell(m_widths[1], 3, "Pred. Positiva", border=0, align='C')
        pdf.cell(m_widths[2], 3, "Pred. Negativa", border=0, align='C')
        
        pdf.set_x(x_start + sum(m_widths) + 20)
        pdf.cell(50, 3, "Métricas de Rendimiento", border=0, align='L')
        pdf.ln(3)
        
        y_sub = pdf.get_y()
        pdf.set_line_width(0.15)
        pdf.line(x_start, y_sub, x_start + sum(m_widths), y_sub)
        pdf.line(x_start + sum(m_widths) + 20, y_sub, x_start + sum(m_widths) + 80, y_sub)
        pdf.ln(0.8)
        
        pdf.set_font('helvetica', '', 6)
        pdf.cell(m_widths[0], 3, "Real Positivo", border=0, align='L')
        pdf.cell(m_widths[1], 3, f"{matrix['vp']} (VP)", border=0, align='C')
        pdf.cell(m_widths[2], 3, f"{matrix['fn']} (FN)", border=0, align='C')
        
        pdf.set_x(x_start + sum(m_widths) + 20)
        pdf.cell(35, 3, "Exactitud (Accuracy):", border=0, align='L')
        pdf.set_font('helvetica', 'B', 6)
        pdf.cell(25, 3, accuracy, border=0, align='L')
        pdf.ln(3)
        
        pdf.set_font('helvetica', '', 6)
        pdf.cell(m_widths[0], 3, "Real Negativo", border=0, align='L')
        pdf.cell(m_widths[1], 3, f"{matrix['fp']} (FP)", border=0, align='C')
        pdf.cell(m_widths[2], 3, f"{matrix['vn']} (VN)", border=0, align='C')
        
        pdf.set_x(x_start + sum(m_widths) + 20)
        pdf.cell(35, 3, "Precisión (Precision):", border=0, align='L')
        pdf.set_font('helvetica', 'B', 6)
        pdf.cell(25, 3, precision, border=0, align='L')
        pdf.ln(3)
        
        y_sub_end = pdf.get_y()
        pdf.set_line_width(0.15)
        pdf.line(x_start, y_sub_end, x_start + sum(m_widths), y_sub_end)
        pdf.line(x_start + sum(m_widths) + 20, y_sub_end, x_start + sum(m_widths) + 80, y_sub_end)
        
        pdf.ln(5)
        
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 5.pdf")
    pdf.output(output_path)
    print(f"Created Apéndice 5 PDF: {output_path}")

def create_appendix_6_pdf(qa_data):
    pdf = AppendixPDF(orientation='P')
    pdf.add_page()
    
    pdf.set_font('helvetica', 'B', 12)
    pdf.cell(0, 6, "Apéndice 6", align='C', new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font('helvetica', 'B', 10)
    pdf.cell(0, 6, "EP-05: Evaluación de Satisfacción y Validación del Stakeholder (Encuesta de Satisfacción)", align='C', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)
    
    pdf.set_font('helvetica', '', 9)
    description_text = (
        "Descripción: En el Apéndice 6 se consolidan las respuestas obtenidas en el instrumento de evaluación de "
        "satisfacción y validación del stakeholder, aplicado al Ing. Javier Montaluisa, Director de la Carrera de "
        "Ingeniería de Software de la Universidad de las Fuerzas Armadas ESPE Sede Latacunga, con fecha 28 de julio de 2026. "
        "El instrumento valora el impacto del 'Sistema automatizado de gestión y ordenamiento de evidencias para la "
        "acreditación de una carrera universitaria' en aspectos clave como la mitigación de errores humanos, el apoyo a "
        "auditorías externas, la claridad de los reportes generados y la eficiencia en la reducción del tiempo y la carga "
        "administrativa de los docentes."
    )
    pdf.multi_cell(0, 4.5, description_text, align='J', new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 5, "DATOS GENERALES DE LA EVALUACIÓN", border=0, align='L', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(1)
    
    info_col1_w = 40
    info_col2_w = 140
    info_rows = [
        ("Evaluador:", "Ing. Javier Montaluisa"),
        ("Cargo:", "Director de la Carrera de Ingeniería de Software"),
        ("Institución:", "Universidad de las Fuerzas Armadas ESPE Sede Latacunga"),
        ("Fecha:", "28/07/2026"),
        ("Objetivo:", "Conocer el nivel de satisfacción del Stakeholder respecto al 'Sistema automatizado de gestión y ordenamiento de evidencias para la acreditación de una carrera universitaria'")
    ]
    
    for label, val in info_rows:
        pdf.set_font('helvetica', 'B', 8)
        pdf.cell(info_col1_w, 4.5, label, border=0, align='L')
        pdf.set_font('helvetica', '', 8)
        pdf.multi_cell(info_col2_w, 4.5, val, align='L', new_x="LMARGIN", new_y="NEXT")
        
    pdf.ln(5)
    
    pdf.set_font('helvetica', 'B', 9)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(0, 5, "CUESTIONARIO Y VALORACIONES", border=0, align='L', fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2.5)
    
    for q_idx, item in enumerate(qa_data):
        q = item["question"]
        opts = item["options"]
        ans = item["answer"]
        
        pdf.set_font('helvetica', 'B', 8)
        pdf.multi_cell(0, 4.2, f"{q_idx+1}. {q}", border=0, align='L', new_x="LMARGIN", new_y="NEXT")
        pdf.ln(1)
        
        pdf.set_font('helvetica', '', 7.5)
        for opt in opts:
            is_selected = (opt == ans)
            chk = "[X]" if is_selected else "[ ]"
            
            if is_selected:
                pdf.set_font('helvetica', 'B', 7.5)
            else:
                pdf.set_font('helvetica', '', 7.5)
                
            pdf.cell(12, 3.8, f"   {chk}", border=0, align='L')
            pdf.cell(0, 3.8, opt, border=0, align='L', new_x="LMARGIN", new_y="NEXT")
            
        pdf.ln(2.5)
        
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 6.pdf")
    pdf.output(output_path)
    print(f"Created Apéndice 6 PDF: {output_path}")


# ==================== DOCX (WORD) GENERATION ====================

def format_docx_run(run, font_name="Arial", size_pt=9, bold=False, italic=False, color_rgb=(0,0,0)):
    run.font.name = font_name
    run.font.size = Pt(size_pt)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = RGBColor(*color_rgb)

def create_appendix_4_docx(records, promedio_global):
    doc = docx.Document()
    
    # Page setup to Landscape
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    new_width, new_height = section.page_height, section.page_width
    section.page_width = new_width
    section.page_height = new_height
    # Margins (0.5 inch = 12.7mm)
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Apéndice 4")
    format_docx_run(r, size_pt=12, bold=True)
    
    # Subtitle
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("EP-03: Calidad de Extracción y Fiabilidad Estructural (Métrica de Jaccard)")
    format_docx_run(r2, size_pt=10.5, bold=True)
    
    # Description
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    desc_txt = (
        "Descripción: En el Apéndice 4 se presentan los resultados detallados del Índice de Jaccard obtenidos al evaluar "
        "la calidad de extracción de texto y la fiabilidad estructural en el corpus de pruebas del sistema. Se analizan "
        f"un total de {len(records)} documentos (perfiles de egreso, proyectos curriculares, sílabos, mallas curriculares y "
        "guías de laboratorio) en contraste con el texto extraído por el motor OCR de la plataforma. Los resultados demuestran "
        f"que el sistema alcanza un Promedio Global de Jaccard de {promedio_global} (sobre un óptimo de 1000,00), lo cual valida "
        "la alta precisión de la capa defensiva inicial frente a la documentación de la carrera de Ingeniería de Software."
    )
    r_desc = p_desc.add_run(desc_txt)
    format_docx_run(r_desc, size_pt=9, italic=False)
    
    # Add Table
    table = doc.add_table(rows=1 + len(records), cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    
    # Formatter for headers
    headers = ["ID Documento", "Tipo de Formato", "Índice de Jaccard", "Estado de Extracción"]
    hdr_row = table.rows[0]
    for col_idx, text_h in enumerate(headers):
        cell = hdr_row.cells[col_idx]
        p_cell = cell.paragraphs[0]
        # Align center for Jaccard and Status columns
        if col_idx in [2, 3]:
            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
        else:
            p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run_h = p_cell.add_run(text_h)
        format_docx_run(run_h, size_pt=8, bold=True)
        
    # Data rows
    for r_idx, record in enumerate(records):
        row = table.rows[1 + r_idx]
        
        orig_status = record["estado"].lower()
        estado = "Deficiente" if "deficiente" in orig_status else "Óptimo"
        
        vals = [record["id"], record["tipo"], record["jaccard"], estado]
        for col_idx, val in enumerate(vals):
            cell = row.cells[col_idx]
            p_cell = cell.paragraphs[0]
            if col_idx in [2, 3]:
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p_cell.alignment = WD_ALIGN_PARAGRAPH.LEFT
            run_val = p_cell.add_run(str(val))
            format_docx_run(run_val, size_pt=7.5)
            
    # Set APA table styles
    set_table_borders_apa(table)
    
    # Adjust column widths
    col_widths = [Inches(5.0), Inches(2.0), Inches(1.5), Inches(1.5)]
    for row in table.rows:
        for i, w in enumerate(col_widths):
            row.cells[i].width = w
            
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 4.docx")
    doc.save(output_path)
    print(f"Created Apéndice 4 Word: {output_path}")

def create_appendix_5_docx(docs_data):
    doc = docx.Document()
    
    # Page setup to Landscape
    section = doc.sections[0]
    section.orientation = WD_ORIENT.LANDSCAPE
    new_width, new_height = section.page_height, section.page_width
    section.page_width = new_width
    section.page_height = new_height
    section.top_margin = Inches(0.5)
    section.bottom_margin = Inches(0.5)
    section.left_margin = Inches(0.5)
    section.right_margin = Inches(0.5)
    
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Apéndice 5")
    format_docx_run(r, size_pt=12, bold=True)
    
    # Subtitle
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("EP-04: Matriz de Confusión General Granulada (Evaluación Multietiqueta)")
    format_docx_run(r2, size_pt=10.5, bold=True)
    
    # Description
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    desc_txt = (
        "Descripción: En el Apéndice 5 se detalla la matriz de confusión general granulada y las métricas de rendimiento "
        "asociadas a la evaluación multietiqueta aplicada a los documentos del corpus de pruebas. Para cada documento "
        "(sílabos, mallas curriculares, guías de laboratorio, proyectos curriculares y perfiles de egreso), se contrastan "
        "las decisiones de la Inteligencia Artificial frente a la validación de un experto humano en las diferentes "
        "secciones cognitivas y secciones esenciales para la acreditación. Este desglose permite medir la precisión y "
        "exactitud granular del sistema, identificando áreas de ambigüedad semántica y confirmando la ausencia de "
        "falsos positivos en las clasificaciones."
    )
    r_desc = p_desc.add_run(desc_txt)
    format_docx_run(r_desc, size_pt=9)
    
    # Render all 16 documents
    for doc_idx, doc_item in enumerate(docs_data):
        doc_name = doc_item["doc_name"]
        estado_final = doc_item["estado_final"]
        accuracy = doc_item["accuracy"]
        precision = doc_item["precision"]
        matrix = doc_item["matrix"]
        rows = doc_item["rows"]
        
        # Section Header for Document
        p_doc = doc.add_paragraph()
        p_doc.paragraph_format.space_before = Pt(12)
        r_doc = p_doc.add_run(f"Documento: {doc_name}")
        format_docx_run(r_doc, size_pt=9, bold=True, color_rgb=(50, 50, 50))
        
        # Add main table
        # Columns:
        # Secciones, Hum., IA, Res. Matriz, Secciones Esenciales, Hum., IA, Res. Matriz, Estado
        table = doc.add_table(rows=1 + len(rows), cols=9)
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        headers = ["Secciones del Documento", "Hum.", "IA", "Resultado de la Matriz", "Secciones Esenciales", "Hum.", "IA", "Resultado de la Matriz", "Estado"]
        hdr_row = table.rows[0]
        for col_idx, text_h in enumerate(headers):
            cell = hdr_row.cells[col_idx]
            p_cell = cell.paragraphs[0]
            p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [1, 2, 5, 6, 8] else WD_ALIGN_PARAGRAPH.LEFT
            run_h = p_cell.add_run(text_h)
            format_docx_run(run_h, size_pt=7, bold=True)
            
        # Rows
        for r_idx, r_val in enumerate(rows):
            row = table.rows[1 + r_idx]
            est = estado_final if r_idx == 0 else ""
            res_d = r_val[3].replace("Verdadero Positivo", "VP").replace("Falso Negativo", "FN").replace("Verdadero Negativo", "VN").replace("Falso Positivo", "FP")
            res_e = r_val[7].replace("Verdadero Positivo", "VP").replace("Falso Negativo", "FN").replace("Verdadero Negativo", "VN").replace("Falso Positivo", "FP") if len(r_val) > 7 else ""
            
            vals = [r_val[0], r_val[1], r_val[2], res_d, r_val[4], r_val[5], r_val[6], res_e, est]
            
            for col_idx, val in enumerate(vals):
                cell = row.cells[col_idx]
                p_cell = cell.paragraphs[0]
                p_cell.alignment = WD_ALIGN_PARAGRAPH.CENTER if col_idx in [1, 2, 5, 6, 8] else WD_ALIGN_PARAGRAPH.LEFT
                run_val = p_cell.add_run(str(val))
                
                # Check bold for Estado Final
                is_bold = True if (col_idx == 8 and val != "") else False
                format_docx_run(run_val, size_pt=7, bold=is_bold)
                
        set_table_borders_apa(table)
        
        # Widths: Secciones=2.2", Hum/IA=0.5", Res=1.2", Essentials=1.8", Hum/IA=0.5", Res=1.2", Estado=0.7"
        # Total Landscape available: ~10"
        widths = [Inches(2.2), Inches(0.4), Inches(0.4), Inches(1.1), Inches(1.8), Inches(0.4), Inches(0.4), Inches(1.1), Inches(0.8)]
        for row in table.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = w
                
        # Sub-tables (Confusion Matrix and Metrics side by side)
        # We can simulate this using a table of 1 row, 2 columns with no borders
        sub_layout_table = doc.add_table(rows=1, cols=2)
        sub_layout_table.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Left cell: Matrix Table
        cell_left = sub_layout_table.rows[0].cells[0]
        p_cl = cell_left.paragraphs[0]
        # Clear default paragraph
        p_cl.text = ""
        
        matrix_table = cell_left.add_table(rows=3, cols=3)
        matrix_table.alignment = WD_TABLE_ALIGNMENT.LEFT
        set_table_borders_apa(matrix_table)
        
        m_headers = ["Matriz de Confusión", "Pred. Positiva", "Pred. Negativa"]
        for c_idx, m_text in enumerate(m_headers):
            cell_m = matrix_table.rows[0].cells[c_idx]
            p_m = cell_m.paragraphs[0]
            p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
            r_m = p_m.add_run(m_text)
            format_docx_run(r_m, size_pt=6.5, bold=True)
            
        m_rows = [
            ("Real Positivo", f"{matrix['vp']} (VP)", f"{matrix['fn']} (FN)"),
            ("Real Negativo", f"{matrix['fp']} (FP)", f"{matrix['vn']} (VN)")
        ]
        for r_idx, r_m_val in enumerate(m_rows):
            row_m = matrix_table.rows[1 + r_idx]
            for c_idx, val_m in enumerate(r_m_val):
                cell_m = row_m.cells[c_idx]
                p_m = cell_m.paragraphs[0]
                p_m.alignment = WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT
                r_m = p_m.add_run(str(val_m))
                format_docx_run(r_m, size_pt=6.5)
                
        # Widths for matrix sub-table
        m_widths = [Inches(1.2), Inches(0.9), Inches(0.9)]
        for row in matrix_table.rows:
            for i, w in enumerate(m_widths):
                row.cells[i].width = w
                
        # Right cell: Metrics block
        cell_right = sub_layout_table.rows[0].cells[1]
        p_cr = cell_right.paragraphs[0]
        p_cr.text = ""
        
        metrics_table = cell_right.add_table(rows=3, cols=2)
        metrics_table.alignment = WD_TABLE_ALIGNMENT.LEFT
        set_table_borders_apa(metrics_table)
        
        # Header
        hdr_met = metrics_table.rows[0]
        r_met1 = hdr_met.cells[0].paragraphs[0].add_run("Métricas de Rendimiento")
        format_docx_run(r_met1, size_pt=6.5, bold=True)
        r_met2 = hdr_met.cells[1].paragraphs[0].add_run("")
        
        # Row 1: Accuracy
        row_acc = metrics_table.rows[1]
        r_acc_lbl = row_acc.cells[0].paragraphs[0].add_run("Exactitud (Accuracy):")
        format_docx_run(r_acc_lbl, size_pt=6.5)
        r_acc_val = row_acc.cells[1].paragraphs[0].add_run(accuracy)
        format_docx_run(r_acc_val, size_pt=6.5, bold=True)
        
        # Row 2: Precision
        row_prec = metrics_table.rows[2]
        r_prec_lbl = row_prec.cells[0].paragraphs[0].add_run("Precisión (Precision):")
        format_docx_run(r_prec_lbl, size_pt=6.5)
        r_prec_val = row_prec.cells[1].paragraphs[0].add_run(precision)
        format_docx_run(r_prec_val, size_pt=6.5, bold=True)
        
        # Widths for metrics sub-table
        met_widths = [Inches(1.5), Inches(1.0)]
        for row in metrics_table.rows:
            for i, w in enumerate(met_widths):
                row.cells[i].width = w
                
        # Layout table spacing: remove borders of the container table
        for r_container in sub_layout_table.rows:
            for c_container in r_container.cells:
                # Remove border elements
                tcPr = c_container._tc.get_or_add_tcPr()
                tcBorders = OxmlElement('w:tcBorders')
                for b_name in ['top', 'left', 'bottom', 'right']:
                    b_el = OxmlElement(f'w:{b_name}')
                    b_el.set(qn('w:val'), 'none')
                    tcBorders.append(b_el)
                tcPr.append(tcBorders)
                
        # Adjust layout table columns
        sub_layout_table.rows[0].cells[0].width = Inches(4.0)
        sub_layout_table.rows[0].cells[1].width = Inches(4.0)
        
        # Small space after document block
        doc.add_paragraph().paragraph_format.space_before = Pt(6)
        
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 5.docx")
    doc.save(output_path)
    print(f"Created Apéndice 5 Word: {output_path}")

def create_appendix_6_docx(qa_data):
    doc = docx.Document()
    
    # Portrait Page setup
    section = doc.sections[0]
    section.orientation = WD_ORIENT.PORTRAIT
    section.top_margin = Inches(0.7)
    section.bottom_margin = Inches(0.7)
    section.left_margin = Inches(0.7)
    section.right_margin = Inches(0.7)
    
    # Title
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Apéndice 6")
    format_docx_run(r, size_pt=12, bold=True)
    
    # Subtitle
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r2 = p2.add_run("EP-05: Evaluación de Satisfacción y Validación del Stakeholder (Encuesta de Satisfacción)")
    format_docx_run(r2, size_pt=10.5, bold=True)
    
    # Description
    p_desc = doc.add_paragraph()
    p_desc.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    desc_txt = (
        "Descripción: En el Apéndice 6 se consolidan las respuestas obtenidas en el instrumento de evaluación de "
        "satisfacción y validación del stakeholder, aplicado al Ing. Javier Montaluisa, Director de la Carrera de "
        "Ingeniería de Software de la Universidad de las Fuerzas Armadas ESPE Sede Latacunga, con fecha 28 de julio de 2026. "
        "El instrumento valora el impacto del 'Sistema automatizado de gestión y ordenamiento de evidencias para la "
        "acreditación de una carrera universitaria' en aspectos clave como la mitigación de errores humanos, el apoyo a "
        "auditorías externas, la claridad de los reportes generados y la eficiencia en la reducción del tiempo y la carga "
        "administrativa de los docentes."
    )
    r_desc = p_desc.add_run(desc_txt)
    format_docx_run(r_desc, size_pt=9)
    
    # Title Datos Generales
    p_dg = doc.add_paragraph()
    p_dg.paragraph_format.space_before = Pt(8)
    r_dg = p_dg.add_run("DATOS GENERALES DE LA EVALUACIÓN")
    format_docx_run(r_dg, size_pt=9, bold=True)
    
    # Info list
    info_rows = [
        ("Evaluador:", "Ing. Javier Montaluisa"),
        ("Cargo:", "Director de la Carrera de Ingeniería de Software"),
        ("Institución:", "Universidad de las Fuerzas Armadas ESPE Sede Latacunga"),
        ("Fecha:", "28/07/2026"),
        ("Objetivo:", "Conocer el nivel de satisfacción del Stakeholder respecto al 'Sistema automatizado de gestión y ordenamiento de evidencias para la acreditación de una carrera universitaria'")
    ]
    
    for lbl, val in info_rows:
        p_info = doc.add_paragraph()
        p_info.paragraph_format.space_after = Pt(2)
        r_lbl = p_info.add_run(f"{lbl} ")
        format_docx_run(r_lbl, size_pt=8.5, bold=True)
        r_val = p_info.add_run(val)
        format_docx_run(r_val, size_pt=8.5)
        
    # Title Cuestionario
    p_q_title = doc.add_paragraph()
    p_q_title.paragraph_format.space_before = Pt(12)
    r_qt = p_q_title.add_run("CUESTIONARIO Y VALORACIONES")
    format_docx_run(r_qt, size_pt=9, bold=True)
    
    for q_idx, item in enumerate(qa_data):
        q = item["question"]
        opts = item["options"]
        ans = item["answer"]
        
        p_q = doc.add_paragraph()
        p_q.paragraph_format.space_before = Pt(6)
        p_q.paragraph_format.space_after = Pt(2)
        r_q = p_q.add_run(f"{q_idx+1}. {q}")
        format_docx_run(r_q, size_pt=8.5, bold=True)
        
        for opt in opts:
            p_opt = doc.add_paragraph()
            p_opt.paragraph_format.left_indent = Inches(0.4)
            p_opt.paragraph_format.space_after = Pt(1)
            
            is_selected = (opt == ans)
            chk = "[X]" if is_selected else "[ ]"
            
            r_chk = p_opt.add_run(f"{chk} ")
            format_docx_run(r_chk, size_pt=8, bold=is_selected)
            r_opt = p_opt.add_run(opt)
            format_docx_run(r_opt, size_pt=8, bold=is_selected)
            
    output_dir = r"c:\Users\User\Desktop\tesis\Documentos para la tesis\Aprendices"
    output_path = os.path.join(output_dir, "Apéndice 6.docx")
    doc.save(output_path)
    print(f"Created Apéndice 6 Word: {output_path}")


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    # Load Jaccard data
    with open(r"C:\Users\User\.gemini\antigravity\brain\2461d326-2935-45be-800e-feddcdd9fe86\scratch\jaccard_parsed.json", "r", encoding="utf-8") as f:
        jaccard_data = json.load(f)
    promedio_global = jaccard_data["promedio_global"]
    jaccard_records = jaccard_data["records"]
    
    # Load Confusion matrix data
    with open(r"C:\Users\User\.gemini\antigravity\brain\2461d326-2935-45be-800e-feddcdd9fe86\scratch\confusion_parsed_final.json", "r", encoding="utf-8") as f:
        confusion_data = json.load(f)
        
    # Define Survey QA data
    qa_data = [
        {
            "question": "¿Considera que la barrera defensiva de preprocesamiento (detección de plantillas inválidas, inconsistencias en mallas y nombres de archivos) mitiga de manera efectiva el error humano?",
            "options": ["Totalmente en desacuerdo", "En desacuerdo", "Neutral", "De acuerdo", "Totalmente de acuerdo"],
            "answer": "Totalmente de acuerdo"
        },
        {
            "question": "¿Considera que la creación autónoma de la jerarquía de carpetas y el enrutamiento automático apoya a las auditorías de evaluación externa?",
            "options": ["No, no garantiza trazabilidad", "Sí, garantiza trazabilidad"],
            "answer": "Sí, garantiza trazabilidad"
        },
        {
            "question": "¿Considera que los informes individuales (específicos) y los reportes consolidados (generales) que genera el sistema son claros y fáciles de entender?",
            "options": ["Sí", "No"],
            "answer": "Sí"
        },
        {
            "question": "¿Qué nivel de confianza le inspiran los dictámenes automatizados?",
            "options": ["Muy baja confianza", "Baja confianza", "Neutral", "Alta confianza", "Muy alta confianza"],
            "answer": "Muy alta confianza"
        },
        {
            "question": "¿Considera que el sistema reduce significativamente la carga administrativa y el tiempo que los docentes destinan semestralmente a revisar, clasificar y archivar evidencias?",
            "options": ["No reduce el tiempo", "2", "3", "4", "Reduce significativamente el tiempo"],
            "answer": "Reduce significativamente el tiempo"
        },
        {
            "question": "¿Sería beneficioso para la universidad conectar esta herramienta directamente con las plataformas y repositorios institucionales (Drive, entornos virtuales)?",
            "options": ["Sí", "No"],
            "answer": "Sí"
        },
        {
            "question": "¿Recomendaría el uso de esta herramienta a otras carreras del departamento o de la universidad?",
            "options": ["Sí", "No"],
            "answer": "Sí"
        }
    ]
    
    # Generate PDFs
    create_appendix_4_pdf(jaccard_records, promedio_global)
    create_appendix_5_pdf(confusion_data)
    create_appendix_6_pdf(qa_data)
    
    # Generate Word Document copies
    create_appendix_4_docx(jaccard_records, promedio_global)
    create_appendix_5_docx(confusion_data)
    create_appendix_6_docx(qa_data)
    
    print("All PDF and Word appendices generated successfully.")
