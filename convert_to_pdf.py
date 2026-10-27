"""
convert_to_pdf.py
Converts Energy_Consumption_Prediction_Final_Report.docx to PDF
using Microsoft Word COM automation (win32com.client).
"""

import os
import sys
import time

try:
    import win32com.client
except ImportError:
    print("Error: win32com.client is not installed.")
    sys.exit(1)

base_dir = os.path.dirname(os.path.abspath(__file__))
docx_path = os.path.join(base_dir, "Energy_Consumption_Prediction_Final_Report.docx")
pdf_path = os.path.join(base_dir, "Energy_Consumption_Prediction_Final_Report.pdf")

if not os.path.exists(docx_path):
    print(f"Error: {docx_path} does not exist.")
    sys.exit(1)

print(f"Converting DOCX to PDF via Microsoft Word...")
print(f"Source: {docx_path}")
print(f"Target: {pdf_path}")

word = None
doc = None
try:
    word = win32com.client.DispatchEx("Word.Application")
    word.Visible = False
    word.DisplayAlerts = False
    
    doc = word.Documents.Open(docx_path)
    # wdFormatPDF = 17
    doc.SaveAs(pdf_path, FileFormat=17)
    print("Successfully exported PDF using Microsoft Word!")
except Exception as e:
    print(f"Failed to export PDF via Word COM: {e}")
    sys.exit(1)
finally:
    if doc:
        try:
            doc.Close(False)
        except Exception:
            pass
    if word:
        try:
            word.Quit()
        except Exception:
            pass

if os.path.exists(pdf_path):
    print(f"[OK] PDF successfully verified on disk! Size: {os.path.getsize(pdf_path):,} bytes")
else:
    print("Error: PDF file was not created.")
    sys.exit(1)
