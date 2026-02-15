#!/usr/bin/env python3
import sys
sys.path.insert(0, '/Users/johannwaldherr/.config/opencode/skills/docx')

from scripts.document import Document

doc = Document('unpacked')

# Find the paragraph after "Berechnung:" 
target_para = doc["word/document.xml"].get_node(tag="w:p", contains="Berechnung:", line_number=range(168, 178))

# Insert new paragraphs after "Berechnung:"
new_paras = [
    '<w:p w:rsidR="E3858870" w:rsidP="E3858870" w:rsidRDefault="E3858870"><w:pPr><w:rPr/></w:pPr><w:r><w:t xml:space="preserve">Offene Punkte:</w:t></w:r></w:p>',
    '<w:p w:rsidR="E3858870" w:rsidP="E3858870" w:rsidRDefault="E3858870"><w:pPr><w:rPr/></w:pPr><w:r><w:t xml:space="preserve">Position der Schrauben? Anschraubpunkt</w:t></w:r></w:p>',
    '<w:p w:rsidR="E3858870" w:rsidP="E3858870" w:rsidRDefault="E3858870"><w:pPr><w:rPr/></w:pPr><w:r><w:t xml:space="preserve">Ma&#223;nahmen Design&#228;nderung, die Steifigkeit und Materialverbrauch verbessern</w:t></w:r></w:p>'
]

last_node = target_para
for para in new_paras:
    nodes = doc["word/document.xml"].insert_after(last_node, para)
    last_node = nodes[-1]

doc.save()
