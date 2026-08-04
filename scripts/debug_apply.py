import zipfile
import xml.etree.ElementTree as ET
import re

src_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026.docx"
dest_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026-Propuestas.docx"

namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

# Read sources
with zipfile.ZipFile(src_path) as z:
    doc_xml = z.read("word/document.xml")
    comments_xml = z.read("word/comments.xml")

root_doc = ET.fromstring(doc_xml)
root_comm = ET.fromstring(comments_xml)

parent_map = {c: p for p in root_doc.iter() for c in p}
elements = list(root_doc.iter())

active_comments = {}
comment_starts = {}
comment_ends = {}

# Pass 1: Identify all start/end elements and active ranges
for el in elements:
    tag = el.tag
    if tag.endswith('commentRangeStart'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        active_comments[cid] = []
        comment_starts[cid] = el
    elif tag.endswith('commentRangeEnd'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        comment_ends[cid] = el

print(f"Starts: {len(comment_starts)}, Ends: {len(comment_ends)}")

# Debug check first few entries
for cid in list(comment_ends.keys())[:5]:
    start_el = comment_starts.get(cid)
    end_el = comment_ends.get(cid)
    print(f"CID={cid}, HasStart={start_el is not None}, HasEnd={end_el is not None}")
    if end_el:
        parent = parent_map.get(end_el)
        print(f"Parent tag for End: {parent.tag if parent is not None else 'None'}")
