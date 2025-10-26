"""
AdaptiveCompressor - Compression engine with CPU/GPU fallback support

Handles the compression of rendered images with intelligent fallback to CPU
when GPU memory is insufficient.
"""

import torch
from PIL import Image
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AdaptiveCompressor:
    """
    Adaptive compression engine with GPU/CPU fallback.

    Monitors compression ratios and provides warnings when exceeding
    the safe 10x threshold documented in DeepSeek-OCR research.
    """

    def __init__(self):
        """Initialize the compressor with mode configurations."""
        self.compression_modes = {
            'tiny': {
                'resolution': 512,
                'tokens': 64,
                'max_text_tokens': 600,
                'safe_ratio': 9.4  # 600/64 = 9.4x
            },
            'small': {
                'resolution': 640,
                'tokens': 100,
                'max_text_tokens': 900,
                'safe_ratio': 9.0  # 900/100 = 9x
            },
            'base': {
                'resolution': 1024,
                'tokens': 256,
                'max_text_tokens': 2500,
                'safe_ratio': 9.8  # 2500/256 = 9.8x
            }
        }

    def compress_with_fallback(
        self,
        image: Image.Image,
        encoder,
        mode: str = 'small'
    ) -> torch.Tensor:
        """
        Try GPU compression first, fall back to CPU if needed.

        Args:
            image: PIL Image to compress
            encoder: LaptopDeepEncoder instance
            mode: Compression mode

        Returns:
            Compressed vision tokens

        Raises:
            Exception: If both GPU and CPU compression fail
        """
        try:
            # Attempt GPU compression
            if torch.cuda.is_available():
                return self.gpu_compress(image, encoder, mode)
        except torch.cuda.OutOfMemoryError:
            logger.warning("GPU OOM - falling back to CPU compression")
            torch.cuda.empty_cache()

        # CPU fallback (slower but works)
        return self.cpu_compress(image, encoder, mode)

    def gpu_compress(
        self,
        image: Image.Image,
        encoder,
        mode: str
    ) -> torch.Tensor:
        """
        GPU-accelerated compression.

        Args:
            image: PIL Image
            encoder: LaptopDeepEncoder instance
            mode: Compression mode

        Returns:
            Compressed vision tokens on GPU
        """
        return encoder.encode(image, mode=mode)

    def cpu_compress(
        self,
        image: Image.Image,
        encoder,
        mode: str
    ) -> torch.Tensor:
        """
        CPU-only compression using reduced precision.

        Args:
            image: PIL Image
            encoder: LaptopDeepEncoder instance
            mode: Compression mode

        Returns:
            Compressed vision tokens on CPU
        """
        with torch.no_grad():
            # Temporarily move model to CPU if needed
            original_device = next(encoder.model.parameters()).device

            if original_device.type != 'cpu':
                logger.info("Moving model to CPU for compression")
                encoder.model = encoder.model.cpu()

            try:
                # Encode on CPU with FP16 to save memory
                tokens = encoder.encode(image, mode=mode)

                # Convert to FP16 for memory efficiency
                tokens = tokens.half()

                return tokens
            finally:
                # Move model back to original device
                if original_device.type != 'cpu':
                    encoder.model = encoder.model.to(original_device)

    def monitor_compression_ratio(
        self,
        original_tokens: int,
        compressed_tokens: int,
        mode: str
    ) -> dict:
        """
        Monitor compression ratio and check if it exceeds safe threshold.

        Args:
            original_tokens: Original text token count estimate
            compressed_tokens: Compressed vision token count
            mode: Compression mode used

        Returns:
            Dict with ratio, status, and warning message
        """
        if compressed_tokens == 0:
            return {
                'ratio': 0,
                'status': 'error',
                'message': 'Invalid compression: zero tokens',
                'safe': False
            }

        ratio = original_tokens / compressed_tokens
        mode_config = self.compression_modes.get(mode, {})
        safe_ratio = mode_config.get('safe_ratio', 10.0)

        result = {
            'ratio': round(ratio, 2),
            'compressed_tokens': compressed_tokens,
            'original_tokens': original_tokens,
            'mode': mode,
            'safe_ratio': safe_ratio,
            'safe': ratio <= 10.0  # DeepSeek-OCR safe threshold
        }

        if ratio > 10.0:
            result['status'] = 'warning'
            result['message'] = (
                f"⚠️  Compression ratio {ratio:.1f}x exceeds safe threshold (10x). "
                f"Accuracy may degrade. Consider using a higher resolution mode or OCR fallback."
            )
            logger.warning(result['message'])
        elif ratio > safe_ratio:
            result['status'] = 'caution'
            result['message'] = (
                f"Compression ratio {ratio:.1f}x exceeds optimal threshold for {mode} mode ({safe_ratio:.1f}x). "
                f"Consider upgrading to next mode."
            )
            logger.info(result['message'])
        else:
            result['status'] = 'ok'
            result['message'] = f"Compression ratio {ratio:.1f}x is within safe limits."
            logger.debug(result['message'])

        return result

    def estimate_text_tokens(self, image: Image.Image) -> int:
        """
        Rough estimation of text tokens in an image.

        Uses heuristic based on image size. More accurate methods would require
        actual text extraction.

        Args:
            image: PIL Image

        Returns:
            Estimated text token count
        """
        width, height = image.size
        total_pixels = width * height

        # Heuristic: ~5000 pixels per token (rough approximation)
        # Assumes standard document layout with reasonable text density
        estimated_tokens = total_pixels // 5000

        # Clamp to reasonable bounds
        estimated_tokens = max(100, min(estimated_tokens, 5000))

        return estimated_tokens

    def get_recommended_mode(self, estimated_text_tokens: int) -> str:
        """
        Recommend compression mode based on estimated text tokens.

        Args:
            estimated_text_tokens: Estimated text token count

        Returns:
            Recommended mode name
        """
        if estimated_text_tokens <= 600:
            return 'tiny'
        elif estimated_text_tokens <= 900:
            return 'small'
        elif estimated_text_tokens <= 2500:
            return 'base'
        else:
            return 'gundam'  # Would need implementation for very large documents
