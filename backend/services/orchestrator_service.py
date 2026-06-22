import os
import shutil
import re
from datetime import datetime
from fpdf import FPDF
from fpdf.fonts import FontFace

def sanitizar_nombre(nombre: str) -> str:
    """Elimina caracteres especiales para crear carpetas seguras en cualquier SO"""
    if not nombre:
        return "Indicador_Desconocido"
    # Reemplaza cualquier cosa que no sea letra, número o espacio por nada
    sanitizado = re.sub(r'[^\w\s-]', '', nombre)
    # Reemplaza espacios por guiones bajos
    sanitizado = re.sub(r'[-\s]+', '_', sanitizado).strip('_')
    return sanitizado

def generar_reporte_pdf(dictamen: dict, ruta_salida: str, nombre_original: str):
    """
    Genera un reporte PDF profesional utilizando fpdf2 basado en el dictamen estructurado de la IA.
    """
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Título principal
    pdf.set_font("helvetica", style="B", size=16)
    pdf.cell(0, 10, "Reporte Oficial de Auditoría - CACES", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)
    
    # Metadatos del reporte
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Fecha:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.cell(0, 8, f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Documento Analizado:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 8, nombre_original, new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Indicador:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 8, dictamen.get("indicador_evaluado", "Desconocido"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Veredicto IA:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.cell(0, 8, dictamen.get("veredicto", "ERROR"), new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Cumplimiento:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.cell(0, 8, f"{dictamen.get('porcentaje_estimado', 0)}%", new_x="LMARGIN", new_y="NEXT")
    
    # Pertinencia a la Carrera
    pertenece = dictamen.get("pertenece_software", True)
    just_software = dictamen.get("justificacion_software", "No especificada.")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Pertinencia Carrera:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.cell(0, 8, "Sí" if pertenece else "No", new_x="LMARGIN", new_y="NEXT")
    
    pdf.set_font("helvetica", style="B", size=11)
    pdf.cell(45, 8, "Justif. Pertinencia:", new_x="RIGHT")
    pdf.set_font("helvetica", size=11)
    pdf.multi_cell(0, 8, just_software, new_x="LMARGIN", new_y="NEXT")
    
    if not pertenece:
        pdf.ln(2)
        pdf.set_font("helvetica", style="B", size=11)
        pdf.set_text_color(255, 0, 0)
        pdf.multi_cell(0, 8, "ATENCIÓN: Este documento fue descartado de la auditoría principal por no pertenecer a la carrera de Ingeniería de Software.", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        
    pdf.ln(8)
    
    # Sección de Análisis Libre
    analisis = dictamen.get("analisis_libre", dictamen.get("justificacion", ""))
    if analisis:
        pdf.set_font("helvetica", style="B", size=13)
        pdf.cell(0, 10, "1. Análisis General", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=11)
        pdf.multi_cell(0, 6, analisis, align="J", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(8)
    
    # Sección de Checklist (Tabla)
    checklist = dictamen.get("checklist", [])
    if checklist:
        pdf.set_font("helvetica", style="B", size=13)
        pdf.cell(0, 10, "2. Detalle de Requisitos (Checklist)", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)
        
        pdf.set_font("helvetica", size=9)
        with pdf.table(col_widths=(10, 55, 25, 100), text_align=("C", "L", "C", "L"), headings_style=FontFace(emphasis="B")) as table:
            # Cabecera
            headers = table.row()
            for header in ("N°", "Requisito", "Estado", "Justificación Fáctica"):
                headers.cell(header)
                
            # Filas
            for item in checklist:
                row = table.row()
                num = str(item.get("numero_elemento", ""))
                desc = str(item.get("descripcion", ""))
                estado = "Cumple" if item.get("cumple") else "No Cumple"
                just = str(item.get("justificacion", ""))
                
                row.cell(num)
                row.cell(desc)
                if not item.get("cumple"):
                    row.cell(estado, style=FontFace(emphasis="B"))
                else:
                    row.cell(estado)
                row.cell(just)
                
    # Guardar archivo
    pdf.output(ruta_salida)

def obtener_carpeta_indicador(indicador: str) -> str:
    ind_lower = indicador.lower()
    if "perfil" in ind_lower: return "Indicador_1_Perfil_de_egreso"
    if "malla" in ind_lower: return "Indicador_3_Malla_curricular"
    if "syllabus" in ind_lower or "sílabo" in ind_lower or "silabo" in ind_lower: return "Indicador_4_Syllabus"
    if "metodolog" in ind_lower: return "INDICADOR_5_Metodología_y_recursos_de_aprendizaje"
    if "tecnolog" in ind_lower or "tac" in ind_lower.split(): return "INDICADOR_7_Tecnologías_para_el_aprendizaje_y_conocimiento_TAC"
    if "evaluación" in ind_lower or "desempeño" in ind_lower: return "INDICADOR_10_Evaluación_integral_del_desempeño_del_personal_académico"
    return sanitizar_nombre(indicador)

def enrutar_documento(resultado_llm: dict, ruta_pdf_temporal: str, nombre_original: str) -> str:
    """
    Orquesta el movimiento del archivo PDF a su carpeta correspondiente 
    basándose en el veredicto de la IA.
    """
    # Puedes cambiar esta constante o recibirla desde tu core/config.py o del Frontend en el futuro
    BASE_DIR = "./Auditoria_CACES"
    
    # Extraer datos del JSON de forma segura
    veredicto = resultado_llm.get("veredicto", "ERROR").upper()
    indicador = resultado_llm.get("indicador_evaluado", "Indicador_Desconocido")
    
    # 1. Generar Timestamp para evitar sobreescrituras
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base, ext = os.path.splitext(nombre_original)
    nuevo_nombre_pdf = f"{nombre_base}_{timestamp}{ext}"
    nuevo_nombre_reporte = f"{nombre_base}_{timestamp}_Reporte.pdf"
    
    # 2. Lógica de Triage (Enrutamiento)
    pertenece = resultado_llm.get("pertenece_software", True)
    
    if not pertenece:
        # Si no pertenece a la carrera, se rechaza inmediatamente
        carpeta_destino = os.path.join(BASE_DIR, "11_Documentos_Rechazados")
        crear_reporte = True
    else:
        # Lógica de triage normal
        if "ERROR" in veredicto:
            carpeta_destino = os.path.join(BASE_DIR, "99_Descarte_Errores")
            crear_reporte = False
        elif "NO CUMPLE" in veredicto:
            carpeta_destino = os.path.join(BASE_DIR, "11_Documentos_Rechazados")
            crear_reporte = True
        else: 
            # "CUMPLE" o "CUMPLE PARCIALMENTE" van a la carpeta de su indicador oficial
            carpeta_destino = os.path.join(BASE_DIR, obtener_carpeta_indicador(indicador))
            crear_reporte = True
            
    os.makedirs(carpeta_destino, exist_ok=True)
    ruta_final_pdf = os.path.join(carpeta_destino, nuevo_nombre_pdf)
    ruta_final_reporte = os.path.join(carpeta_destino, nuevo_nombre_reporte)
    
    # 3. Mover/Copiar el PDF original
    # Usamos copy2 para mantener metadatos originales y permitir que el bloque 'finally'
    # de main.py elimine el archivo temporal tranquilamente sin dar error.
    if os.path.exists(ruta_pdf_temporal):
        shutil.copy2(ruta_pdf_temporal, ruta_final_pdf)
    
    # 4. Crear archivo PDF con el reporte (solo si aplica)
    if crear_reporte:
        generar_reporte_pdf(resultado_llm, ruta_final_reporte, nombre_original)
            
    return ruta_final_pdf
