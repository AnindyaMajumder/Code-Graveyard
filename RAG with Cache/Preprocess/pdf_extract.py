import os
import shutil
import fitz  # PyMuPDF
import torch
from pathlib import Path
from dotenv import load_dotenv

# ── Monkey-patch transformers bug in video_processing_auto ────────────────────
import importlib
import transformers.models.auto.video_processing_auto as _vpa
from transformers.models.auto.auto_factory import model_type_to_module_name


def _patched_vp_class_from_name(class_name):
    for module_name, extractors in _vpa.VIDEO_PROCESSOR_MAPPING_NAMES.items():
        if extractors is None:
            continue
        if class_name in extractors:
            mod_name = model_type_to_module_name(module_name)
            module = importlib.import_module(f".{mod_name}", "transformers.models")
            try:
                return getattr(module, class_name)
            except AttributeError:
                continue

    for extractor in _vpa.VIDEO_PROCESSOR_MAPPING._extra_content.values():
        if getattr(extractor, "__name__", None) == class_name:
            return extractor

    main_module = importlib.import_module("transformers")
    if hasattr(main_module, class_name):
        return getattr(main_module, class_name)
    return None


_vpa.video_processor_class_from_name = _patched_vp_class_from_name
# ──────────────────────────────────────────────────────────────────────────────

from transformers import AutoProcessor, AutoModelForImageTextToText

# ── paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PDF_DIR = DATA_DIR / "chemestry"
OUTPUT_DIR = DATA_DIR / "extracted"
CACHE_DIR = BASE_DIR / "Preprocess" / ".page_cache"

MODEL_PATH = "zai-org/GLM-OCR"

# ── env / auth ────────────────────────────────────────────────────────────────
load_dotenv(BASE_DIR / ".env")
HF_TOKEN = os.getenv("HUGGINGFACE_ACCESS_TOKEN")


def pdf_to_images(pdf_path: Path, cache_dir: Path) -> list[Path]:
    """Convert every page of a PDF to a PNG image and store in cache_dir."""
    doc = fitz.open(pdf_path)
    image_paths: list[Path] = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        # render at 300 DPI for good OCR quality
        pix = page.get_pixmap(dpi=300)
        img_path = cache_dir / f"{pdf_path.stem}_page_{page_num + 1}.png"
        pix.save(str(img_path))
        image_paths.append(img_path)
        print(f"  Cached page {page_num + 1}/{len(doc)} → {img_path.name}")
    doc.close()
    return image_paths


def load_model():
    """Load GLM-OCR model and processor once."""
    print(f"Loading model {MODEL_PATH} …")
    processor = AutoProcessor.from_pretrained(
        MODEL_PATH, trust_remote_code=True, token=HF_TOKEN
    )
    model = AutoModelForImageTextToText.from_pretrained(
        MODEL_PATH,
        torch_dtype="auto",
        device_map="auto",
        trust_remote_code=True,
        token=HF_TOKEN,
    )
    print("Model loaded.\n")
    return processor, model


def ocr_image(image_path: Path, processor, model) -> str:
    """Run GLM-OCR on a single image and return the recognised text."""
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "image", "url": str(image_path)},
                {"type": "text", "text": "Text Recognition:"},
            ],
        }
    ]

    inputs = processor.apply_chat_template(
        messages,
        tokenize=True,
        add_generation_prompt=True,
        return_dict=True,
        return_tensors="pt",
    ).to(model.device)
    inputs.pop("token_type_ids", None)

    with torch.no_grad():
        generated_ids = model.generate(**inputs, max_new_tokens=8192)

    output_text = processor.decode(
        generated_ids[0][inputs["input_ids"].shape[1] :],
        skip_special_tokens=True,
    )
    return output_text


def process_pdf(pdf_path: Path, processor, model) -> None:
    """Full pipeline for one PDF: pages → cache → OCR → save → cleanup."""
    pdf_name = pdf_path.stem
    print(f"\n{'='*60}")
    print(f"Processing: {pdf_path.name}")
    print(f"{'='*60}")

    # --- 1. Convert pages to images (cache) ---
    pdf_cache = CACHE_DIR / pdf_name
    pdf_cache.mkdir(parents=True, exist_ok=True)
    image_paths = pdf_to_images(pdf_path, pdf_cache)

    # --- 2. OCR each page ---
    all_text: list[str] = []
    for idx, img_path in enumerate(image_paths, 1):
        print(f"  OCR page {idx}/{len(image_paths)} …", end=" ", flush=True)
        text = ocr_image(img_path, processor, model)
        all_text.append(f"--- Page {idx} ---\n{text}")
        print("done")

    # --- 3. Save output ---
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_file = OUTPUT_DIR / f"{pdf_name}.md"
    out_file.write_text("\n\n".join(all_text), encoding="utf-8")
    print(f"  Saved → {out_file}")

    # --- 4. Remove cached images ---
    shutil.rmtree(pdf_cache)
    print(f"  Cache cleared for {pdf_name}")


def main():
    # Only process c1.pdf
    pdf = input("Enter PDF filename (e.g. c1.pdf): ")
    target = PDF_DIR / pdf
    if not target.exists():
        print(f"PDF not found: {target}")
        return
    pdfs = [target]

    print(f"Found {len(pdfs)} PDF(s) to process\n")

    # ensure cache root exists
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # load model once
    processor, model = load_model()

    for pdf_path in pdfs:
        process_pdf(pdf_path, processor, model)

    # remove cache root if empty
    if CACHE_DIR.exists() and not any(CACHE_DIR.iterdir()):
        CACHE_DIR.rmdir()
        print("\nAll cache cleaned up.")

    print("\nAll done.")


if __name__ == "__main__":
    main()
