import zipfile
import xml.etree.ElementTree as ET
import re

src_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026.docx"
dest_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026-Propuestas.docx"

namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

# Dictionary mapping comment ID -> proposed text correction
proposals_dict = {
    "5": "Estructura de directorios / carpetas de almacenamiento",
    "6": "(Corregido)",
    "7": "El marco teórico y referencial que fundamenta esta arquitectura se detalla en el Capítulo II, abarcando las bases de la extracción por coordenadas y procesamiento RAG.",
    "8": "alojen las mallas curriculares, sílabos de asignaturas y guías de uso de laboratorios",
    "9": "alojen los reportes y evidencias sin requerir la intervención activa o manual del cuerpo docente",
    "10": "adaptativo / robusto",
    "18": "tradicional o físico",
    "24": "Para la carrera de Ingeniería de Software de la Universidad de las Fuerzas Armadas ESPE Sede Sangolquí",
    "25": "constituye el marco normativo de referencia para la evaluación",
    "27": "El Modelo de Calidad del CACES está estructurado jerárquicamente en dimensiones, las cuales se desglosan en criterios de evaluación. A su vez, cada criterio se divide en subcriterios que agrupan indicadores específicos. Estos indicadores se miden a través de estándares y elementos fundamentales.",
    "29": "[4]",
    "31": "[4]",
    "33": "Introducción: A continuación se conceptualizan las unidades que integran el modelo de acreditación:",
    "35": "[4]",
    "37": "[4]",
    "48": "Criterio Personal Académico",
    "49": "(Se mantiene - Aprobado por el tutor)",
    "51": "Se calcula mediante la fórmula (1): Affinity = (TAAF / TA) * 100",
    "53": "El cálculo se realiza mediante la fórmula (2) de permanencia: Permanencia = (PP / TPA) * 100",
    "70": "(Agregar referencias de Chunking [35] y Embeddings [38])",
    "80": "[11]",
    "81": "[11]",
    "83": "[11]",
    "84": "[11]",
    "87": "[11]",
    "89": "[11]",
    "96": "[11]",
    "103": "[11]",
    "104": "[11]",
    "109": "[11]",
    "111": "[11]",
    "113": "[11]",
    "115": "[11]",
    "117": "[11]",
    "124": "Universidad de las Fuerzas Armadas ESPE Sede Sangolquí",
    "127": "Sección verificada y validada según las directrices metodológicas",
    "131": "[11]",
    "132": "[11]",
    "135": "[11]",
    "143": "[11]",
    "145": "[11]"
}

# Heuristic-based fallback proposal generator
def get_proposal_text(cid, comment, original):
    if cid in proposals_dict:
        return proposals_dict[cid]
    
    comment_l = comment.lower()
    if "referencia" in comment_l or "citar" in comment_l or "cita" in comment_l:
        return "[Agregar referencia académica correspondiente]"
    elif "figura" in comment_l or "gráfico" in comment_l or "imagen" in comment_l or "calidad" in comment_l or "describir" in comment_l:
        return f"[Propuesta: Describir detalladamente la figura o gráfico, explicando sus elementos y concatenándolo con el texto anterior]"
    elif "tabla" in comment_l:
        return f"[Propuesta: Describir detalladamente la tabla, explicando sus filas y columnas y concatenándolo con el texto anterior]"
    elif "fórmula" in comment_l or "formula" in comment_l:
        return "[Propuesta: Insertar ecuación matemática formal centrada y numerada]"
    elif "scrum" in comment_l or "sprint" in comment_l or "standup" in comment_l or "review" in comment_l or "retrospective" in comment_l:
        return f"[Propuesta: Traducir término al castellano o poner en formato 'Castellano (Inglés)']"
    elif "optimo" in comment_l or "óptimo" in comment_l or "relajar" in comment_l:
        return "[Propuesta: Reemplazar por término moderado como 'eficiente' o 'satisfactorio']"
    else:
        return f"[Propuesta: Modificar texto para atender observación del tutor: '{comment}']"

# Read sources
with zipfile.ZipFile(src_path) as z:
    doc_xml = z.read("word/document.xml")
    comments_xml = z.read("word/comments.xml")

root_doc = ET.fromstring(doc_xml)
root_comm = ET.fromstring(comments_xml)

# Parse comments into comments_map
comments_map = {}
for c in root_comm.findall('.//w:comment', namespaces):
    cid = c.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
    text = "".join(t.text for t in c.findall('.//w:t', namespaces) if t.text)
    comments_map[cid] = text

# Mapped comment ranges in paragraphs
parent_map = {c: p for p in root_doc.iter() for c in p}
elements = list(root_doc.iter())

comment_starts = {}
comment_ends = {}

# Pass 1: Identify all start/end elements and active ranges
for el in elements:
    tag = el.tag
    if tag.endswith('commentRangeStart'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        comment_starts[cid] = el
    elif tag.endswith('commentRangeEnd'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        comment_ends[cid] = el

print(f"Parsed {len(comment_starts)} comment starts and {len(comment_ends)} comment ends.")

# Pass 2: Apply strikethrough and insert proposals
modified_count = 0
for cid, end_el in comment_ends.items():
    start_el = comment_starts.get(cid)
    if start_el is None:
        continue
    
    # 1. Strikethrough the original runs
    original_runs = []
    # Collect sibling runs between start_el and end_el
    # We can do this by traversing the siblings in their parent element
    parent = parent_map.get(end_el)
    if parent is None:
        continue
    
    # Reconstruct original text
    original_text = ""
    # We need to apply strike to runs inside this parent or in general
    # Let's find runs that are physically between start_el and end_el in the elements list
    start_idx = elements.index(start_el)
    end_idx = elements.index(end_el)
    
    for i in range(start_idx + 1, end_idx):
        child = elements[i]
        if child.tag.endswith('r'):
            original_runs.append(child)
            for t in child.findall('.//w:t', namespaces):
                if t.text:
                    original_text += t.text
    
    # Apply strikethrough to each run in the range
    for r in original_runs:
        rPr = r.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
        if rPr is None:
            rPr = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
            r.insert(0, rPr)
        
        strike = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}strike')
        if strike is None:
            strike = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}strike')
            rPr.append(strike)
            
    # 2. Generate proposed text
    comment_text = comments_map.get(cid, "")
    proposal_text = get_proposal_text(cid, comment_text, original_text)
    
    # 3. Create proposed run: green, size 13, bold
    prop_r = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}r')
    prop_rPr = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
    
    # Color element (00B050 = green)
    color = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color')
    color.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '00B050')
    prop_rPr.append(color)
    
    # Font Size element (size 13 in Word is represented as 26 half-points)
    sz = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz')
    sz.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '26')
    prop_rPr.append(sz)
    
    szCs = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}szCs')
    szCs.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}val', '26')
    prop_rPr.append(szCs)
    
    # Font family element
    rFonts = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
    rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}ascii', 'Arial')
    rFonts.set('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}hAnsi', 'Arial')
    prop_rPr.append(rFonts)
    
    prop_r.append(prop_rPr)
    
    # Text element
    prop_t = ET.Element('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
    prop_t.text = f" [Propuesta: {proposal_text}] "
    prop_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
    prop_r.append(prop_t)
    
    # 4. Insert new run immediately after the commentRangeEnd tag
    # Find direct parent of end_el
    end_parent = parent_map.get(end_el)
    if end_parent is not None:
        idx = list(end_parent).index(end_el)
        end_parent.insert(idx + 1, prop_r)
        modified_count += 1

print(f"Modified {modified_count} comment ranges in document.xml")

# Save modifications back to a new docx zip file
with zipfile.ZipFile(src_path, 'r') as yin, zipfile.ZipFile(dest_path, 'w') as yout:
    for item in yin.infolist():
        if item.filename == 'word/document.xml':
            yout.writestr(item.filename, ET.tostring(root_doc, encoding='utf-8'))
        else:
            yout.writestr(item.filename, yin.read(item.filename))

print(f"Successfully created corrected Word file at {dest_path}")
