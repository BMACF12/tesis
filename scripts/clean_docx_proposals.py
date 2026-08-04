import zipfile
import xml.etree.ElementTree as ET
import os

file_path = r"Documentos para la tesis\00_manuscrito\TESIS V1.0 FLORES_MORALES completo-Rev-JLCM-27-07.2026-Propuestas.docx"
temp_file = file_path + ".tmp"

namespaces = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
}
ET.register_namespace('w', 'http://schemas.openxmlformats.org/wordprocessingml/2006/main')

with zipfile.ZipFile(file_path, 'r') as z:
    doc_xml = z.read("word/document.xml")

root = ET.fromstring(doc_xml)

# Traverse all elements
elements = list(root.iter())
parent_map = {c: p for p in root.iter() for c in p}

# 1. Find all runs with strikethrough (strike element inside rPr)
to_remove = []
for el in elements:
    if el.tag.endswith('r'):
        rPr = el.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
        if rPr is not None:
            strike = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}strike')
            if strike is not None:
                # This is a struck-through run, remove it!
                to_remove.append(el)

# 2. Find our proposed runs and clean them up
cleaned_count = 0
for el in elements:
    if el.tag.endswith('r') and el not in to_remove:
        # Check if it has a text element containing " [Propuesta: "
        t_el = el.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t')
        if t_el is not None and t_el.text and " [Propuesta: " in t_el.text:
            # Clean up the text: remove " [Propuesta: " and trailing " ] "
            cleaned_text = t_el.text.replace(" [Propuesta: ", "").strip()
            if cleaned_text.endswith(" ]"):
                cleaned_text = cleaned_text[:-2]
            elif cleaned_text.endswith("]"):
                cleaned_text = cleaned_text[:-1]
            
            t_el.text = cleaned_text
            
            # Clean up formatting: remove green color, custom size, custom font
            rPr = el.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rPr')
            if rPr is not None:
                color = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}color')
                if color is not None:
                    rPr.remove(color)
                
                sz = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}sz')
                if sz is not None:
                    rPr.remove(sz)
                
                szCs = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}szCs')
                if szCs is not None:
                    rPr.remove(szCs)
                
                rFonts = rPr.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}rFonts')
                if rFonts is not None:
                    rPr.remove(rFonts)
            
            cleaned_count += 1

# 3. Find and remove comment start, end, and reference elements
comments_removed = 0
for el in elements:
    tag = el.tag
    if tag.endswith('commentRangeStart') or tag.endswith('commentRangeEnd'):
        to_remove.append(el)
        comments_removed += 0.5 # since there's start and end, each is 0.5
    elif tag.endswith('r'):
        ref = el.find('{http://schemas.openxmlformats.org/wordprocessingml/2006/main}commentReference')
        if ref is not None:
            to_remove.append(el)
            comments_removed += 1

print(f"Original struck-through runs marked for deletion: {len(to_remove)}")
print(f"Proposals cleaned and integrated: {cleaned_count}")
print(f"Comments structural elements marked for deletion: {int(comments_removed)}")

# 4. Remove all elements marked for removal
removed_count = 0
for el in to_remove:
    parent = parent_map.get(el)
    if parent is not None:
        try:
            parent.remove(el)
            removed_count += 1
        except ValueError:
            pass

print(f"Actually removed {removed_count} XML elements.")

# Write modified XML back to the file
with zipfile.ZipFile(file_path, 'r') as yin, zipfile.ZipFile(temp_file, 'w') as yout:
    for item in yin.infolist():
        if item.filename == 'word/document.xml':
            yout.writestr(item.filename, ET.tostring(root, encoding='utf-8'))
        else:
            yout.writestr(item.filename, yin.read(item.filename))

os.replace(temp_file, file_path)
print("Finished successfully")
