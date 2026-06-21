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
    porcentaje = resultado_llm.get("porcentaje_estimado", "0")
    justificacion = resultado_llm.get("justificacion", "")
    
    # 1. Generar Timestamp para evitar sobreescrituras
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_base, ext = os.path.splitext(nombre_original)
    nuevo_nombre_pdf = f"{nombre_base}_{timestamp}{ext}"
    nuevo_nombre_reporte = f"{nombre_base}_{timestamp}_Reporte.pdf"
    
    # 2. Lógica de Triage (Enrutamiento)
    if "ERROR" in veredicto:
        carpeta_destino = os.path.join(BASE_DIR, "99_Descarte_Errores")
        crear_reporte = False # No generar reporte detallado para errores
    elif "NO CUMPLE" in veredicto:
        carpeta_destino = os.path.join(BASE_DIR, "11_Documentos_Rechazados")
        crear_reporte = True
    elif "CUMPLE PARCIALMENTE" in veredicto:
        nombre_carpeta = sanitizar_nombre(indicador)
        carpeta_destino = os.path.join(BASE_DIR, nombre_carpeta)
        crear_reporte = True
    else: # "CUMPLE"
        nombre_carpeta = sanitizar_nombre(indicador)
        carpeta_destino = os.path.join(BASE_DIR, nombre_carpeta)
        crear_reporte = False # Ahorro de almacenamiento
        
    # Crear carpeta destino siempre (exist_ok=True evita el FileExistsError)
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
