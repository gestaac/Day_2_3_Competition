from pypdf import PdfReader
import sys
r = PdfReader(r'C:\Users\CHESTER BAUTISTA\Day_2_3_Competition\WSA2025_TP54_MA2_actual_en_final (1).pdf')
out = []
for i, p in enumerate(r.pages):
    out.append(f"===PAGE {i+1}===")
    txt = p.extract_text() or ""
    out.append(txt)
with open(r'C:\Users\CHESTER BAUTISTA\Day_2_3_Competition\_pdf_extract.txt','w',encoding='utf-8') as f:
    f.write("\n".join(out))
print("DONE", sum(len(x) for x in out))
