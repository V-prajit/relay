"""
EfficientRenderer - Lightweight document rendering optimized for laptop constraints

Renders PDF pages and images at optimized resolutions for DeepSeek-OCR compression.
Uses streaming approach to minimize memory footprint.
"""

import fitz  # PyMuPDF
from PIL import Image
import io
from pathlib import Path
from typing import Iterator, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class EfficientRenderer:
    """
    Memory-efficient document renderer with streaming support.

    Renders documents at 150 DPI (vs 200 DPI original) for laptop optimization,
    with automatic resizing to target resolutions (512 or 640).
    """

    def __init__(self, target_dpi: int = 150, max_dimension: int = 640):
        """
        Initialize the renderer.

        Args:
            target_dpi: Rendering DPI (150 for laptops, 200 for workstations)
            max_dimension: Maximum width/height before resizing (512, 640, or 1024)
        """
        self.dpi = target_dpi
        self.max_dimension = max_dimension

    def render_pdf_streaming(
        self,
        pdf_path: str,
        max_pages: Optional[int] = None,
        target_size: Tuple[int, int] = (640, 640)
    ) -> Iterator[Tuple[Image.Image, int]]:
        """
        Stream render PDF pages one at a time to save memory.

        Args:
            pdf_path: Path to PDF file
            max_pages: Maximum number of pages to process (None = all)
            target_size: Target (width, height) for resizing

        Yields:
            Tuple of (PIL Image, page_number)

        Raises:
            FileNotFoundError: If PDF doesn't exist
            Exception: If rendering fails
        """
        pdf_path_obj = Path(pdf_path)
        if not pdf_path_obj.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")

        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages) if max_pages else total_pages

            logger.info(f"Rendering PDF: {pdf_path_obj.name} ({pages_to_process}/{total_pages} pages)")

            for page_num in range(pages_to_process):
                page = doc[page_num]

                # Render at specified DPI
                mat = fitz.Matrix(self.dpi / 72, self.dpi / 72)
                pix = page.get_pixmap(matrix=mat, alpha=False)

                # Convert to PIL Image
                img_data = pix.tobytes("png")
                img = Image.open(io.BytesIO(img_data))

                # Resize to target dimensions
                img_resized = self._resize_to_target(img, target_size)

                yield img_resized, page_num

                # Clean up page resources immediately
                pix = None
                page = None

            doc.close()
            logger.info(f"Completed rendering {pages_to_process} pages")

        except Exception as e:
            logger.error(f"Error rendering PDF: {str(e)}")
            raise

    def render_image(self, image_path: str, target_size: Tuple[int, int] = (640, 640)) -> Image.Image:
        """
        Render a single image file.

        Args:
            image_path: Path to image file
            target_size: Target (width, height) for resizing

        Returns:
            PIL Image resized to target dimensions

        Raises:
            FileNotFoundError: If image doesn't exist
        """
        img_path = Path(image_path)
        if not img_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        try:
            img = Image.open(image_path)

            # Convert to RGB if needed (handles RGBA, grayscale, etc.)
            if img.mode != 'RGB':
                img = img.convert('RGB')

            # Resize to target
            img_resized = self._resize_to_target(img, target_size)

            logger.info(f"Rendered image: {img_path.name} -> {img_resized.size}")
            return img_resized

        except Exception as e:
            logger.error(f"Error rendering image: {str(e)}")
            raise

    def _resize_to_target(self, img: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """
        Resize image to target dimensions with aspect ratio preservation.

        Uses two strategies:
        - For Tiny/Small modes (512, 640): Direct resize to avoid wasting tokens
        - For Base/Large modes (1024, 1280): Padding to preserve aspect ratio

        Args:
            img: Input PIL Image
            target_size: Target (width, height)

        Returns:
            Resized PIL Image
        """
        target_w, target_h = target_size
        original_w, original_h = img.size

        # For small resolutions, use direct resize (Tiny/Small mode)
        if target_w <= 640:
            if original_w > target_w or original_h > target_h:
                img.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
            return img

        # For larger resolutions, use padding to preserve aspect ratio (Base/Large mode)
        else:
            # Calculate aspect ratio preserving dimensions
            ratio = min(target_w / original_w, target_h / original_h)
            new_w = int(original_w * ratio)
            new_h = int(original_h * ratio)

            # Resize
            img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

            # Create padded canvas
            padded = Image.new('RGB', (target_w, target_h), (255, 255, 255))
            paste_x = (target_w - new_w) // 2
            paste_y = (target_h - new_h) // 2
            padded.paste(img_resized, (paste_x, paste_y))

            return padded

    def estimate_document_complexity(self, file_path: str) -> int:
        """
        Estimate document complexity (approximate text token count).

        Used to determine which compression mode to use.

        Args:
            file_path: Path to document

        Returns:
            Estimated text token count (rough approximation)
        """
        path = Path(file_path)

        # Simple heuristic based on file size and type
        file_size_mb = path.stat().st_size / 1e6

        if path.suffix.lower() == '.pdf':
            try:
                doc = fitz.open(file_path)
                page_count = len(doc)
                doc.close()

                # Rough estimate: 500 tokens per page
                estimated_tokens = page_count * 500
            except:
                # Fallback based on file size
                estimated_tokens = int(file_size_mb * 200)
        else:
            # For images, estimate based on resolution
            try:
                img = Image.open(file_path)
                width, height = img.size
                # Larger images likely contain more text
                estimated_tokens = int((width * height) / 5000)
            except:
                estimated_tokens = 500  # Default guess

        logger.debug(f"Estimated complexity for {path.name}: {estimated_tokens} tokens")
        return estimated_tokens

    def get_resolution_for_mode(self, mode: str) -> Tuple[int, int]:
        """
        Get target resolution for a given compression mode.

        Args:
            mode: One of 'tiny', 'small', 'base', 'large'

        Returns:
            Tuple of (width, height)
        """
        mode_resolutions = {
            'tiny': (512, 512),
            'small': (640, 640),
            'base': (1024, 1024),
            'large': (1280, 1280),
        }

        return mode_resolutions.get(mode, (640, 640))  # Default to small mode
