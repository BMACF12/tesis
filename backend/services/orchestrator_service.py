import os
import shutil
import re
from datetime import datetime

def sanitizar_nombre(nombre: str) -> str:
    """Elimina caracteres especiales para crear carpetas seguras en cualquier SO"""
    if not nombre:
        return "Indicador_Desconocido"
    # Reemplaza cualquier cosa que no sea letra, número o espacio por nada
    sanitizado = re.sub(r'[^\w\s-]', '', nombre)
    # Reemplaza espacios por guiones bajos
    sanitizado = re.sub(r'[-\s]+', '_', sanitizado).strip('_')
    return sanitizado

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
    nuevo_nombre_txt = f"{nombre_base}_{timestamp}_Dictamen.txt"
    
    # 2. Lógica de Triage (Enrutamiento)
    if "NO CUMPLE" in veredicto:
        carpeta_destino = os.path.join(BASE_DIR, "11_Documentos_Rechazados")
        crear_txt = True
    elif "CUMPLE PARCIALMENTE" in veredicto:
        nombre_carpeta = sanitizar_nombre(indicador)
        carpeta_destino = os.path.join(BASE_DIR, nombre_carpeta)
        crear_txt = True
    else: # "CUMPLE"
        nombre_carpeta = sanitizar_nombre(indicador)
        carpeta_destino = os.path.join(BASE_DIR, nombre_carpeta)
        crear_txt = False # Ahorro de almacenamiento
        
    # Crear carpeta destino siempre (exist_ok=True evita el FileExistsError)
    os.makedirs(carpeta_destino, exist_ok=True)
    
    ruta_final_pdf = os.path.join(carpeta_destino, nuevo_nombre_pdf)
    ruta_final_txt = os.path.join(carpeta_destino, nuevo_nombre_txt)
    
    # 3. Mover/Copiar el PDF
    # Usamos copy2 para mantener metadatos originales y permitir que el bloque 'finally'
    # de main.py elimine el archivo temporal tranquilamente sin dar error.
    if os.path.exists(ruta_pdf_temporal):
        shutil.copy2(ruta_pdf_temporal, ruta_final_pdf)
    
    # 4. Crear archivo TXT con el reporte (solo si aplica)
    if crear_txt:
        with open(ruta_final_txt, "w", encoding="utf-8") as f:
            f.write(f"=== DICTAMEN OFICIAL DE AUDITORÍA CACES ===\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Documento Analizado: {nombre_original}\n")
            f.write(f"Regla/Indicador: {indicador}\n")
            f.write(f"Veredicto IA: {veredicto}\n")
            f.write(f"Porcentaje Estimado: {porcentaje}%\n")
            f.write(f"-"*50 + "\n")
            f.write(f"JUSTIFICACIÓN TÉCNICA:\n")
            f.write(f"{justificacion}\n")
            
    return ruta_final_pdf
