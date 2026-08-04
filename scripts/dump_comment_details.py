import zipfile
import xml.etree.ElementTree as ET
import json

docx_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026.docx"
json_out_path = r"C:\Users\User\.gemini\antigravity\brain\bd3eae09-e8c2-40f6-841c-cbda65ee1f72\scratch\comments_metadata.json"

namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}

with zipfile.ZipFile(docx_path) as z:
    doc_xml = z.read("word/document.xml")
    comments_xml = z.read("word/comments.xml")

root_doc = ET.fromstring(doc_xml)
root_comm = ET.fromstring(comments_xml)

comments_map = {}
for c in root_comm.findall('.//w:comment', namespaces):
    cid = c.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
    text = "".join(t.text for t in c.findall('.//w:t', namespaces) if t.text)
    comments_map[cid] = text

# Traverse all elements in document order
elements = list(root_doc.iter())
comment_details = []
active_comments = {}

for el in elements:
    tag = el.tag
    if tag.endswith('commentRangeStart'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        active_comments[cid] = []
    elif tag.endswith('commentRangeEnd'):
        cid = el.get('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}id')
        if cid in active_comments:
            # Reconstruct original text from all collected runs
            original_text = ""
            for r in active_comments[cid]:
                for t in r.findall('.//w:t', namespaces):
                    if t.text:
                        original_text += t.text
            
            comment_details.append({
                "id": cid,
                "comment": comments_map.get(cid, "(No comment text)"),
                "original_text": original_text
            })
            del active_comments[cid]
    elif tag.endswith('r'):
        for cid in active_comments:
            active_comments[cid].append(el)

with open(json_out_path, "w", encoding="utf-8") as f:
    json.dump(comment_details, f, indent=2, ensure_ascii=False)

print(f"Dumped {len(comment_details)} comment details using flat traversal to {json_out_path}")
