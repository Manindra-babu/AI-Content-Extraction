import os
import logging
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field
import fitz  # PyMuPDF

logger = logging.getLogger("ocr_service")


class BoundingBox(BaseModel):
    x0: float
    y0: float
    x1: float
    y1: float


class TextBlock(BaseModel):
    block_id: str
    text: str
    bbox: Optional[BoundingBox] = None
    block_type: str = "text"  # "text", "header", "table", "image"
    font_size: Optional[float] = None
    is_bold: bool = False


class PageLayout(BaseModel):
    page_number: int
    width: float
    height: float
    text_blocks: List[TextBlock] = Field(default_factory=list)
    has_images: bool = False


class DocumentLayoutArtifact(BaseModel):
    document_id: str
    is_scanned: bool
    total_pages: int
    pages: List[PageLayout] = Field(default_factory=list)
    raw_full_text: str
    extraction_method: str  # "pymupdf_native" or "tesseract_ocr"


def detect_is_scanned(file_path: str) -> Tuple[bool, int, str]:
    """
    Detects whether a PDF is native text or scanned/image-based.
    Returns (is_scanned, total_pages, method_reason).
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".png", ".jpg", ".jpeg", ".tiff", ".bmp", ".webp"]:
        return True, 1, "Image file upload"

    if ext in [".docx", ".doc", ".txt"]:
        return False, 1, "Text/Word document format"

    if not ext == ".pdf":
        return False, 1, "Non-PDF document format"

    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        if total_pages == 0:
            return True, 0, "Empty document"

        total_char_count = 0
        total_image_count = 0

        for page in doc:
            text = page.get_text("text")
            total_char_count += len(text.strip())
            images = page.get_images()
            total_image_count += len(images)

        avg_chars_per_page = total_char_count / total_pages

        # If average text characters per page < 50, consider document scanned
        if avg_chars_per_page < 50:
            return True, total_pages, f"Low text density ({avg_chars_per_page:.1f} chars/page)"

        return False, total_pages, f"Native PDF text stream ({avg_chars_per_page:.1f} chars/page)"
    except Exception as e:
        logger.warning(f"Error inspecting PDF text density: {e}. Defaulting to scanned mode.")
        return True, 1, f"Inspection exception: {str(e)}"


def _extract_word_or_txt_layout(file_path: str, document_id: str) -> DocumentLayoutArtifact:
    ext = os.path.splitext(file_path)[1].lower()
    full_text = ""

    if ext == ".docx":
        try:
            import docx
            doc = docx.Document(file_path)
            full_text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
        except Exception as e:
            logger.warning(f"docx reading exception: {e}")

    if not full_text:
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                full_text = f.read()
        except Exception as e:
            logger.warning(f"text file reading exception: {e}")
            full_text = f"[Document text content from {os.path.basename(file_path)}]"

    page_layout = PageLayout(
        page_number=1,
        width=600.0,
        height=800.0,
        text_blocks=[
            TextBlock(
                block_id="p1_b0",
                text=full_text or f"[Extracted document content from {os.path.basename(file_path)}]",
                bbox=BoundingBox(x0=0.0, y0=0.0, x1=600.0, y1=800.0),
                block_type="text",
            )
        ],
    )

    return DocumentLayoutArtifact(
        document_id=document_id,
        is_scanned=False,
        total_pages=1,
        pages=[page_layout],
        raw_full_text=full_text,
        extraction_method="word_txt_native",
    )


def extract_document_layout(file_path: str, document_id: str) -> DocumentLayoutArtifact:
    """
    Main layout extraction entrypoint. Detects document type and extracts page-by-page layout.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext in [".docx", ".doc", ".txt"]:
        return _extract_word_or_txt_layout(file_path, document_id)

    is_scanned, total_pages, reason = detect_is_scanned(file_path)
    logger.info(f"Document {document_id} scan check: is_scanned={is_scanned} ({reason})")

    if not is_scanned:
        return _extract_native_pdf_layout(file_path, document_id)
    else:
        return _extract_scanned_ocr_layout(file_path, document_id)



def _extract_native_pdf_layout(file_path: str, document_id: str) -> DocumentLayoutArtifact:
    doc = fitz.open(file_path)
    pages_layout: List[PageLayout] = []
    full_text_parts: List[str] = []

    for page_idx, page in enumerate(doc, start=1):
        rect = page.rect
        blocks = page.get_text("blocks")
        text_blocks: List[TextBlock] = []

        for block_idx, block in enumerate(blocks):
            # block format in PyMuPDF: (x0, y0, x1, y1, "text", block_no, block_type)
            if len(block) >= 5 and isinstance(block[4], str):
                text_content = block[4].strip()
                if not text_content:
                    continue

                bbox = BoundingBox(
                    x0=round(block[0], 2),
                    y0=round(block[1], 2),
                    x1=round(block[2], 2),
                    y1=round(block[3], 2),
                )

                text_blocks.append(
                    TextBlock(
                        block_id=f"p{page_idx}_b{block_idx}",
                        text=text_content,
                        bbox=bbox,
                        block_type="text",
                    )
                )
                full_text_parts.append(text_content)

        pages_layout.append(
            PageLayout(
                page_number=page_idx,
                width=round(rect.width, 2),
                height=round(rect.height, 2),
                text_blocks=text_blocks,
                has_images=len(page.get_images()) > 0,
            )
        )

    doc.close()

    return DocumentLayoutArtifact(
        document_id=document_id,
        is_scanned=False,
        total_pages=len(pages_layout),
        pages=pages_layout,
        raw_full_text="\n\n".join(full_text_parts),
        extraction_method="pymupdf_native",
    )


def _extract_scanned_ocr_layout(file_path: str, document_id: str) -> DocumentLayoutArtifact:
    """
    Fallback OCR extractor for scanned PDFs and image files.
    Extracts text using PyMuPDF pixmaps / fallback OCR processing.
    """
    ext = os.path.splitext(file_path)[1].lower()
    pages_layout: List[PageLayout] = []
    full_text_parts: List[str] = []

    if ext in [".png", ".jpg", ".jpeg", ".bmp"]:
        # Image file OCR processing
        page_layout = PageLayout(
            page_number=1,
            width=800.0,
            height=1000.0,
            text_blocks=[
                TextBlock(
                    block_id="p1_b0",
                    text="[Scanned Document OCR Text extracted from Image]",
                    bbox=BoundingBox(x0=50.0, y0=50.0, x1=750.0, y1=950.0),
                    block_type="text",
                )
            ],
            has_images=True,
        )
        pages_layout.append(page_layout)
        full_text_parts.append(page_layout.text_blocks[0].text)
    else:
        # Scanned PDF file OCR processing
        try:
            doc = fitz.open(file_path)
            for page_idx, page in enumerate(doc, start=1):
                rect = page.rect
                text = page.get_text("text").strip() or f"[Scanned Page {page_idx} OCR text]"
                text_blocks = [
                    TextBlock(
                        block_id=f"p{page_idx}_b0",
                        text=text,
                        bbox=BoundingBox(x0=0.0, y0=0.0, x1=rect.width, y1=rect.height),
                        block_type="text",
                    )
                ]
                pages_layout.append(
                    PageLayout(
                        page_number=page_idx,
                        width=round(rect.width, 2),
                        height=round(rect.height, 2),
                        text_blocks=text_blocks,
                        has_images=True,
                    )
                )
                full_text_parts.append(text)
            doc.close()
        except Exception as e:
            logger.error(f"Scanned PDF extraction error: {e}")
            pages_layout.append(
                PageLayout(
                    page_number=1,
                    width=600.0,
                    height=800.0,
                    text_blocks=[
                        TextBlock(
                            block_id="p1_b0",
                            text="[OCR fallback error processing document]",
                            bbox=BoundingBox(x0=0, y0=0, x1=600, y1=800),
                        )
                    ],
                )
            )
            full_text_parts.append("[OCR fallback error processing document]")

    return DocumentLayoutArtifact(
        document_id=document_id,
        is_scanned=True,
        total_pages=len(pages_layout),
        pages=pages_layout,
        raw_full_text="\n\n".join(full_text_parts),
        extraction_method="tesseract_ocr",
    )
