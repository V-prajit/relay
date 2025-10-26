"""
HybridOCR - Intelligent OCR fallback system

Routes to appropriate OCR engine based on document complexity and available resources.
Falls back to traditional OCR (PaddleOCR, Tesseract) when DeepSeek is unavailable or unsuitable.
"""

import torch
from PIL import Image
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class HybridOCR:
    """
    Hybrid OCR system with intelligent routing between DeepSeek, PaddleOCR, and Tesseract.

    Automatically selects the best OCR engine based on:
    - Available GPU memory
    - Document complexity
    - Document type
    """

    def __init__(self, enable_paddle: bool = True, enable_tesseract: bool = True):
        """
        Initialize hybrid OCR system.

        Args:
            enable_paddle: Enable PaddleOCR fallback
            enable_tesseract: Enable Tesseract fallback
        """
        self.deepseek_available = self.check_deepseek_memory()
        self.paddle = None
        self.enable_paddle = enable_paddle
        self.enable_tesseract = enable_tesseract

        # Lazy load PaddleOCR only if needed
        if enable_paddle:
            try:
                from paddleocr import PaddleOCR
                self.paddle = PaddleOCR(
                    use_angle_cls=True,
                    lang='en',
                    use_gpu=torch.cuda.is_available(),
                    show_log=False
                )
                logger.info("PaddleOCR initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize PaddleOCR: {e}")
                self.paddle = None

    def process_document(
        self,
        image_path: str,
        deepseek_service: Optional[object] = None,
        force_engine: Optional[str] = None
    ) -> dict:
        """
        Process document with intelligent engine selection.

        Args:
            image_path: Path to image/PDF
            deepseek_service: Optional DeepSeek service instance
            force_engine: Force specific engine ('deepseek', 'paddle', 'tesseract')

        Returns:
            Dict with extracted text and metadata
        """
        doc_complexity = self._estimate_document_complexity(image_path)

        # Determine which engine to use
        if force_engine:
            engine = force_engine
        else:
            engine = self._select_engine(doc_complexity, deepseek_service)

        logger.info(f"Using OCR engine: {engine} for {Path(image_path).name}")

        # Route to appropriate engine
        if engine == 'deepseek' and deepseek_service:
            return self._process_with_deepseek(image_path, deepseek_service)
        elif engine == 'paddle' and self.paddle:
            return self._process_with_paddle(image_path)
        elif engine == 'tesseract':
            return self._process_with_tesseract(image_path)
        else:
            # Fallback chain
            logger.warning(f"Requested engine '{engine}' not available, trying fallbacks")
            return self._fallback_chain(image_path, deepseek_service)

    def _select_engine(self, doc_complexity: int, deepseek_service: Optional[object]) -> str:
        """
        Select optimal OCR engine based on complexity and resources.

        Args:
            doc_complexity: Estimated text token count
            deepseek_service: DeepSeek service if available

        Returns:
            Engine name
        """
        # Simple documents with DeepSeek available - use DeepSeek
        if self.deepseek_available and deepseek_service and doc_complexity < 1000:
            return 'deepseek'

        # Medium complexity - use PaddleOCR if available
        elif self.paddle and doc_complexity < 2000:
            return 'paddle'

        # Complex/long documents - use Tesseract (most robust for large docs)
        else:
            return 'tesseract'

    def _process_with_deepseek(self, image_path: str, deepseek_service) -> dict:
        """
        Process with DeepSeek-OCR.

        Args:
            image_path: Image path
            deepseek_service: DeepSeek service instance

        Returns:
            OCR result dict
        """
        try:
            result = deepseek_service.process_file(image_path, output_format='text')

            return {
                'text': result,
                'engine': 'deepseek',
                'status': 'success'
            }
        except Exception as e:
            logger.error(f"DeepSeek processing failed: {e}")
            return {
                'text': '',
                'engine': 'deepseek',
                'status': 'error',
                'error': str(e)
            }

    def _process_with_paddle(self, image_path: str) -> dict:
        """
        Process with PaddleOCR.

        Args:
            image_path: Image path

        Returns:
            OCR result dict
        """
        try:
            result = self.paddle.ocr(image_path, cls=True)

            # Extract text from PaddleOCR result format
            text_lines = []
            for line in result:
                if line:
                    for word_info in line:
                        text = word_info[1][0]  # (bbox, (text, confidence))
                        text_lines.append(text)

            full_text = '\n'.join(text_lines)

            return {
                'text': full_text,
                'engine': 'paddle',
                'status': 'success',
                'line_count': len(text_lines)
            }

        except Exception as e:
            logger.error(f"PaddleOCR processing failed: {e}")
            return {
                'text': '',
                'engine': 'paddle',
                'status': 'error',
                'error': str(e)
            }

    def _process_with_tesseract(self, image_path: str) -> dict:
        """
        Process with Tesseract OCR.

        Args:
            image_path: Image path

        Returns:
            OCR result dict
        """
        try:
            import pytesseract

            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)

            return {
                'text': text,
                'engine': 'tesseract',
                'status': 'success'
            }

        except Exception as e:
            logger.error(f"Tesseract processing failed: {e}")
            return {
                'text': '',
                'engine': 'tesseract',
                'status': 'error',
                'error': str(e)
            }

    def _fallback_chain(self, image_path: str, deepseek_service: Optional[object]) -> dict:
        """
        Try OCR engines in fallback order until one succeeds.

        Args:
            image_path: Image path
            deepseek_service: DeepSeek service

        Returns:
            First successful OCR result
        """
        # Try DeepSeek first if available
        if self.deepseek_available and deepseek_service:
            result = self._process_with_deepseek(image_path, deepseek_service)
            if result['status'] == 'success':
                return result

        # Try PaddleOCR
        if self.paddle:
            result = self._process_with_paddle(image_path)
            if result['status'] == 'success':
                return result

        # Finally try Tesseract
        if self.enable_tesseract:
            result = self._process_with_tesseract(image_path)
            if result['status'] == 'success':
                return result

        # All failed
        return {
            'text': '',
            'engine': 'none',
            'status': 'error',
            'error': 'All OCR engines failed'
        }

    def _estimate_document_complexity(self, file_path: str) -> int:
        """
        Estimate document complexity (token count).

        Args:
            file_path: Path to document

        Returns:
            Estimated token count
        """
        path = Path(file_path)
        file_size_mb = path.stat().st_size / 1e6

        # Heuristic based on file type and size
        if path.suffix.lower() == '.pdf':
            import fitz
            try:
                doc = fitz.open(file_path)
                page_count = len(doc)
                doc.close()
                return page_count * 500  # ~500 tokens per page
            except:
                return int(file_size_mb * 200)
        else:
            # For images, estimate from dimensions
            try:
                img = Image.open(file_path)
                width, height = img.size
                return int((width * height) / 5000)
            except:
                return 500

    def check_deepseek_memory(self) -> bool:
        """
        Check if we have enough memory for DeepSeek.

        Returns:
            True if sufficient memory available
        """
        if torch.cuda.is_available():
            free_mem = torch.cuda.mem_get_info()[0] / 1e9
            required_mem = 4  # Minimum 4GB for quantized model
            available = free_mem > required_mem
            logger.info(f"GPU memory check: {free_mem:.1f}GB free, DeepSeek {'available' if available else 'unavailable'}")
            return available
        logger.info("No GPU available - DeepSeek unavailable")
        return False

    def get_available_engines(self) -> list:
        """
        Get list of available OCR engines.

        Returns:
            List of engine names
        """
        engines = []

        if self.deepseek_available:
            engines.append('deepseek')
        if self.paddle:
            engines.append('paddle')
        if self.enable_tesseract:
            engines.append('tesseract')

        return engines
