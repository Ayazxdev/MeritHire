import pdfplumber
import sys
import os

pdf_path = sys.argv[1] if len(sys.argv) > 1 else r"test_attacks\David Chen - Senior ML Engineer.pdf"

print("="*60)
print("PDF EXTRACTION DIAGNOSTIC")
print("="*60)

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"✅ PDF opened successfully")
        print(f"   Pages: {len(pdf.pages)}")
        
        full_text = ""
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            print(f"\n--- PAGE {i+1} ---")
            print(f"Characters: {len(text) if text else 0}")
            if text:
                print(f"First 300 chars:\n{text[:300]}")
                full_text += text + "\n"
            else:
                print("⚠️ No text extracted from this page!")
        
        print(f"\n{'='*60}")
        print(f"TOTAL TEXT LENGTH: {len(full_text)} characters")
        
        if len(full_text) < 100:
            print("❌ CRITICAL: Extracted text too short!")
        else:
            print("✅ Extraction successful!")
            
        # Save full text for analysis
        with open("test_attacks/david_chen_raw_text.txt", "w", encoding="utf-8") as f:
            f.write(full_text)
        print(f"\n📂 Saved raw text to: test_attacks/david_chen_raw_text.txt")

except Exception as e:
    print(f"❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
