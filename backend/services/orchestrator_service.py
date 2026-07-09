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
    # Función interna para limpiar caracteres unicode que rompen la fuente helvetica
    def sanitizar_texto_pdf(texto):
        if not isinstance(texto, str): return texto
        reemplazos = {'–': '-', '—': '-', '“': '"', '”': '"', '‘': "'", '’': "'", '…': '...', '\u200b': '', '•': '-'}
        for malo, bueno in reemplazos.items(): 
            texto = texto.replace(malo, bueno)
        return texto.encode('latin-1', errors='ignore').decode('latin-1')

    # Limpiar el dictamen para evitar FPDFUnicodeEncodingException
    for k, v in dictamen.items():
        if isinstance(v, str):
            dictamen[k] = sanitizar_texto_pdf(v)
        elif isinstance(v, list) and k == "checklist":
            for item in v:
                for sub_k, sub_v in item.items():
                    if isinstance(sub_v, str):
                        item[sub_k] = sanitizar_texto_pdf(sub_v)
        elif isinstance(v, list):
            dictamen[k] = [sanitizar_texto_pdf(x) if isinstance(x, str) else x for x in v]
                        
    nombre_original = sanitizar_texto_pdf(nombre_original)
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
        
    # Campos sin llenar: es lo que el responsable necesita saber para corregir.
    vacios = dictamen.get("campos_vacios") or []
    if vacios:
        pdf.ln(4)
        pdf.set_font("helvetica", style="B", size=11)
        pdf.cell(0, 8, f"Campos sin llenar ({len(vacios)})", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("helvetica", size=10)
        pdf.multi_cell(0, 6, "; ".join(vacios), new_x="LMARGIN", new_y="NEXT")

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
    if "proyecto curricular" in ind_lower or "diseño curricular" in ind_lower: return "Indicador_2_Proyecto_curricular"
    if "malla" in ind_lower: return "Indicador_3_Malla_curricular"
    if "syllabus" in ind_lower or "sílabo" in ind_lower or "silabo" in ind_lower: return "Indicador_4_Syllabus"
    if "metodolog" in ind_lower: return "INDICADOR_5_Metodología_y_recursos_de_aprendizaje"
    if ("práctica" in ind_lower or "practica" in ind_lower
            or "escenario" in ind_lower or "laboratorio" in ind_lower):
        return "Indicador_6_Escenarios_de_practicas_formativas"
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
    
    # Recortar el nombre base a máximo 50 caracteres para evitar el error de MAX_PATH de Windows (260 chars)
    nombre_base = nombre_base[:50]
    
    nuevo_nombre_pdf = f"{nombre_base}_{timestamp}{ext}"
    nuevo_nombre_reporte = f"{nombre_base}_{timestamp}_Reporte.pdf"
    
    # 2. Lógica de Triage (Enrutamiento)
    # El orden importa: un error de lectura no lleva veredicto de pertinencia fiable,
    # así que se resuelve antes de mirar 'pertenece_software'.
    pertenece = resultado_llm.get("pertenece_software", True)

    if "ERROR_CUOTA" in veredicto:
        # El documento no tiene nada malo: se quedó sin cuota de API. Se aparta para
        # volver a subirlo cuando el límite se recargue.
        carpeta_destino = os.path.join(BASE_DIR, "98_Pendientes_Por_Cuota")
        crear_reporte = False
    elif "ERROR" in veredicto:
        carpeta_destino = os.path.join(BASE_DIR, "99_Descarte_Errores")
        crear_reporte = False
    elif "PLANTILLA NO RECONOCIDA" in veredicto:
        # No es la plantilla oficial: es un problema distinto de un documento mal llenado.
        carpeta_destino = os.path.join(BASE_DIR, "12_Plantilla_No_Reconocida")
        crear_reporte = True
    elif not pertenece:
        carpeta_destino = os.path.join(BASE_DIR, "11_Documentos_Rechazados")
        crear_reporte = True
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
