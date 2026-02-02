import sys
from image2menu import validate_images, jpgs_to_pdf
from pdf2menu import extract_from_pdf
import json

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1].lower() == "pdf":
        # Only extract from existing PDF
        pdf_path = "files/demo4.pdf"
        # print(f"Extracting from PDF: {pdf_path}")
        response = extract_from_pdf(pdf_path)
            
    elif len(sys.argv) > 1 and sys.argv[1].lower() == "jpg":
        # Only process images
        if validate_images():
            pdf_path = jpgs_to_pdf("files", "menu.pdf")
            # print(f"PDF created: {pdf_path}")
            response = extract_from_pdf(pdf_path)
        else:
            raise ValueError("No valid images found in the 'files' directory.")
    
    else:
        print("Usage: python menu.py [pdf|jpg]")
        exit(1)
    
    print(response)
    # Validate & Convert to json
    try:
        response = json.loads(response)
    except Exception as e:
        raise ValueError(f"Extracted JSON is not in correct format: {e}")
    
    print(json.dumps(response, indent=2, ensure_ascii=False))