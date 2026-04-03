from pathlib import Path
from PIL import Image
import pytesseract
from app.ingestion.pdf_ingestor import chunk_text


def ingest_image(file_path: Path) -> list[dict]:
    """OCR the image, chunk the text, store image_path for viewer."""
    image = Image.open(file_path)

    # IMPORTANT: Always convert to RGB — avoids crashes on PNG with alpha channel
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    raw_text = pytesseract.image_to_string(image, lang="eng").strip()

    # If OCR finds nothing, use filename as fallback so file is still indexed
    if not raw_text:
        raw_text = f"Image file: {file_path.name}. No text detected."

    chunks = chunk_text(raw_text)
    return [
        {
            "chunk_index": i,
            "text": chunk,
            "image_path": str(file_path),
            "modality": "image",
            "page": None,
            "start_time": None,
            "end_time": None,
        }
        for i, chunk in enumerate(chunks)
    ]
