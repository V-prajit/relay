"""
LaptopDeepSeekOCR - Main pipeline controller for DeepSeek-OCR

Integrates all components (renderer, encoder, compressor, decoder, fallback)
into a cohesive pipeline optimized for laptop constraints.
"""

import os
from pathlib import Path
from typing import Optional, Iterator
import logging
import time

from .model_loader import OptimizedModelLoader
from .image_renderer import EfficientRenderer
from .encoder import LaptopDeepEncoder
from .compressor import AdaptiveCompressor
from .decoder import StreamingDecoder
from .ocr_fallback import HybridOCR
from ..utils.memory_guard import MemoryGuard

logger = logging.getLogger(__name__)


class LaptopDeepSeekOCR:
    """
    Main DeepSeek-OCR pipeline optimized for laptop deployment.

    Features:
    - INT8 quantized model loading
    - Automatic mode selection (tiny/small/base)
    - Memory-efficient streaming processing
    - OCR fallback for complex documents
    - Comprehensive error handling
    """

    def __init__(
        self,
        memory_limit_gb: float = 8,
        enable_quantization: bool = True,
        target_dpi: int = 150
    ):
        """
        Initialize the DeepSeek-OCR pipeline.

        Args:
            memory_limit_gb: Maximum GPU memory to use
            enable_quantization: Use INT8 quantization (recommended for laptops)
            target_dpi: Document rendering DPI
        """
        self.memory_limit = memory_limit_gb
        self.enable_quantization = enable_quantization

        # Components (lazy initialized)
        self.model_loader: Optional[OptimizedModelLoader] = None
        self.model = None
        self.renderer = EfficientRenderer(target_dpi=target_dpi)
        self.encoder: Optional[LaptopDeepEncoder] = None
        self.compressor = AdaptiveCompressor()
        self.decoder: Optional[StreamingDecoder] = None
        self.fallback = HybridOCR()

        self.initialized = False

    def initialize(self) -> bool:
        """
        Initialize the DeepSeek model and components.

        Returns:
            True if successful, False if fallback-only mode

        Raises:
            Exception: If critical initialization fails
        """
        try:
            logger.info("Initializing LaptopDeepSeekOCR...")

            # Load model
            self.model_loader = OptimizedModelLoader(use_quantization=self.enable_quantization)

            # Set max memory constraints
            max_memory = {0: f"{self.memory_limit}GB", "cpu": "16GB"}

            with MemoryGuard():
                self.model = self.model_loader.load_model(max_memory=max_memory)

            # Initialize encoder and decoder
            self.encoder = LaptopDeepEncoder(self.model, max_memory_gb=self.memory_limit)
            self.decoder = StreamingDecoder(self.model)

            self.initialized = True
            logger.info("✓ DeepSeek-OCR initialized successfully")

            # Print model info
            model_info = self.model_loader.get_model_info()
            logger.info(f"Model: {model_info}")

            return True

        except Exception as e:
            logger.error(f"Failed to initialize DeepSeek model: {e}")
            logger.info("Running in fallback-only mode (PaddleOCR/Tesseract)")
            self.initialized = False
            return False

    def process_file(
        self,
        file_path: str,
        output_format: str = 'text',
        mode: Optional[str] = None,
        stream: bool = False
    ) -> str:
        """
        Process a document file (PDF or image) with DeepSeek-OCR.

        Args:
            file_path: Path to document
            output_format: Output format ('text', 'markdown', 'html')
            mode: Force specific compression mode ('tiny', 'small', 'base') or None for auto
            stream: Enable streaming output

        Returns:
            Extracted text

        Raises:
            FileNotFoundError: If file doesn't exist
            Exception: If processing fails
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        logger.info(f"Processing file: {Path(file_path).name}")
        start_time = time.time()

        # Check file size
        file_size_mb = Path(file_path).stat().st_size / 1e6

        if file_size_mb > 10:
            logger.info(f"Large file ({file_size_mb:.1f}MB) - using streaming")
            return self._process_streaming(file_path, output_format, mode)

        # Try DeepSeek first if initialized
        if self.initialized and self.model:
            try:
                result = self._process_with_deepseek(file_path, output_format, mode, stream)
                elapsed = time.time() - start_time
                logger.info(f"✓ Processed in {elapsed:.2f}s with DeepSeek")
                return result

            except Exception as e:
                logger.warning(f"DeepSeek processing failed: {e}")
                logger.info("Falling back to traditional OCR")

        # Fallback to traditional OCR
        result = self.fallback.process_document(file_path, deepseek_service=None)
        elapsed = time.time() - start_time

        if result['status'] == 'success':
            logger.info(f"✓ Processed in {elapsed:.2f}s with {result['engine']}")
            return result['text']
        else:
            raise Exception(f"All OCR methods failed: {result.get('error', 'Unknown error')}")

    def _process_with_deepseek(
        self,
        file_path: str,
        output_format: str,
        mode: Optional[str],
        stream: bool
    ) -> str:
        """
        Process document with DeepSeek-OCR.

        Args:
            file_path: Document path
            output_format: Output format
            mode: Compression mode
            stream: Streaming enabled

        Returns:
            Extracted text
        """
        path = Path(file_path)
        all_text = []

        with MemoryGuard():
            # Determine document type
            if path.suffix.lower() == '.pdf':
                # PDF processing
                pages = self.renderer.render_pdf_streaming(file_path)
            else:
                # Image processing
                img = self.renderer.render_image(file_path)
                pages = [(img, 0)]

            # Process each page
            for page_img, page_num in pages:
                logger.debug(f"Processing page {page_num + 1}")

                # Auto-select mode if not specified
                if mode is None:
                    doc_complexity = self.renderer.estimate_document_complexity(file_path)
                    mode = self.encoder.auto_select_mode(doc_complexity)

                # Compress image to vision tokens
                tokens = self.compressor.compress_with_fallback(page_img, self.encoder, mode)

                # Monitor compression ratio
                est_text_tokens = self.compressor.estimate_text_tokens(page_img)
                ratio_info = self.compressor.monitor_compression_ratio(
                    est_text_tokens,
                    len(tokens.flatten()) if hasattr(tokens, 'flatten') else 100,
                    mode
                )

                # Check if compression ratio is safe
                if not ratio_info['safe']:
                    logger.warning(f"Unsafe compression ratio detected: {ratio_info['ratio']}x")
                    logger.info("Switching to OCR fallback for this document")
                    return self.fallback.process_document(file_path, deepseek_service=None)['text']

                # Decode to text
                if stream:
                    page_text = ''.join(self.decoder.decode_streaming(tokens, output_format))
                else:
                    page_text = self.decoder.decode(tokens, output_format, stream=False)

                all_text.append(page_text)

        # Combine all pages
        return '\n\n'.join(all_text)

    def _process_streaming(
        self,
        file_path: str,
        output_format: str,
        mode: Optional[str]
    ) -> str:
        """
        Stream process large documents.

        Args:
            file_path: Document path
            output_format: Output format
            mode: Compression mode

        Returns:
            Extracted text
        """
        logger.info("Using streaming mode for large document")
        return self._process_with_deepseek(file_path, output_format, mode, stream=True)

    def benchmark_performance(self) -> dict:
        """
        Benchmark what compression modes work on current hardware.

        Returns:
            Dict with benchmark results
        """
        import torch

        if not self.initialized:
            return {'error': 'Model not initialized'}

        logger.info("Running performance benchmark...")
        test_sizes = [512, 640, 1024]
        results = {}

        for size in test_sizes:
            mode = {512: 'tiny', 640: 'small', 1024: 'base'}[size]

            try:
                with MemoryGuard():
                    # Create dummy image
                    dummy_img = torch.randn(1, 3, size, size)
                    if torch.cuda.is_available():
                        dummy_img = dummy_img.cuda()

                    # Test encoding
                    start = time.time()
                    _ = self.encoder.encode(dummy_img, mode=mode)
                    elapsed = time.time() - start

                    memory_stats = MemoryGuard.get_memory_stats()

                    results[mode] = {
                        'works': True,
                        'time_seconds': elapsed,
                        'resolution': size,
                        'memory_gb': memory_stats.get('allocated_gb', 0)
                    }

                logger.info(f"✓ {mode} mode: {elapsed:.2f}s")

            except Exception as e:
                results[mode] = {
                    'works': False,
                    'error': str(e),
                    'resolution': size
                }
                logger.warning(f"✗ {mode} mode failed: {e}")

        return results

    def get_system_info(self) -> dict:
        """
        Get system and model information.

        Returns:
            Dict with system info
        """
        info = {
            'initialized': self.initialized,
            'quantization': self.enable_quantization,
            'memory_limit_gb': self.memory_limit,
            'available_engines': self.fallback.get_available_engines()
        }

        if self.model_loader:
            info['model'] = self.model_loader.get_model_info()

        info['memory'] = MemoryGuard.get_memory_stats()

        return info

    def cleanup(self):
        """Clean up resources and free memory."""
        logger.info("Cleaning up resources...")

        if self.model_loader:
            self.model_loader.unload_model()

        self.model = None
        self.encoder = None
        self.decoder = None

        MemoryGuard.force_clear_cache()

        logger.info("✓ Cleanup complete")


# Singleton instance for API usage
_deepseek_instance: Optional[LaptopDeepSeekOCR] = None


def get_deepseek_service(
    memory_limit_gb: float = 8,
    enable_quantization: bool = True
) -> LaptopDeepSeekOCR:
    """
    Get or create singleton DeepSeek service instance.

    Args:
        memory_limit_gb: Memory limit in GB
        enable_quantization: Enable INT8 quantization

    Returns:
        LaptopDeepSeekOCR instance
    """
    global _deepseek_instance

    if _deepseek_instance is None:
        _deepseek_instance = LaptopDeepSeekOCR(
            memory_limit_gb=memory_limit_gb,
            enable_quantization=enable_quantization
        )

    return _deepseek_instance
