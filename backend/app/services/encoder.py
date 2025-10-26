"""
LaptopDeepEncoder - Memory-efficient encoder with automatic mode selection

Handles encoding of document images into compressed vision tokens with
intelligent mode selection based on available memory and document complexity.
"""

import torch
from PIL import Image
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)


class LaptopDeepEncoder:
    """
    Laptop-optimized DeepSeek encoder with automatic mode selection and chunking.

    Automatically selects between Tiny (64 tokens) and Small (100 tokens) modes
    based on available GPU memory and document complexity.
    """

    def __init__(self, model, max_memory_gb: float = 8):
        """
        Initialize the encoder.

        Args:
            model: Loaded DeepSeek-OCR model
            max_memory_gb: Maximum GPU memory limit in GB
        """
        self.model = model
        self.max_memory = max_memory_gb
        self.current_mode = 'tiny'  # Default to smallest mode

        # Mode configurations
        self.mode_configs = {
            'tiny': {
                'resolution': 512,
                'tokens': 64,
                'max_text_tokens': 600,
                'memory_required_gb': 2
            },
            'small': {
                'resolution': 640,
                'tokens': 100,
                'max_text_tokens': 900,
                'memory_required_gb': 4
            },
            'base': {
                'resolution': 1024,
                'tokens': 256,
                'max_text_tokens': 2500,
                'memory_required_gb': 8
            }
        }

    def auto_select_mode(self, document_complexity: int) -> str:
        """
        Automatically select the best compression mode based on available memory and document complexity.

        Args:
            document_complexity: Estimated text token count

        Returns:
            Mode name ('tiny', 'small', or 'base')
        """
        free_memory = self._get_free_memory_gb()

        # Select mode based on memory and complexity
        if free_memory >= 8 and document_complexity < 2500:
            selected_mode = 'base'
        elif free_memory >= 4 and document_complexity < 900:
            selected_mode = 'small'
        else:
            selected_mode = 'tiny'  # Safest option for laptops

        logger.info(
            f"Auto-selected mode: {selected_mode} "
            f"(free_memory: {free_memory:.1f}GB, complexity: {document_complexity} tokens)"
        )

        self.current_mode = selected_mode
        return selected_mode

    def encode(self, image: Image.Image, mode: Optional[str] = None) -> torch.Tensor:
        """
        Encode a single image to vision tokens.

        Args:
            image: PIL Image to encode
            mode: Compression mode ('tiny', 'small', 'base') or None for auto

        Returns:
            Encoded vision tokens as tensor

        Raises:
            torch.cuda.OutOfMemoryError: If GPU runs out of memory
        """
        if mode is None:
            mode = self.current_mode

        config = self.mode_configs[mode]

        try:
            # Prepare image tensor
            image_tensor = self._prepare_image_tensor(image, config['resolution'])

            # Clear cache before encoding
            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            # Encode with model
            with torch.no_grad():
                if hasattr(self.model, 'encode_images'):
                    # Use model's encode method if available
                    tokens = self.model.encode_images(image_tensor)
                else:
                    # Fallback: use full model forward pass
                    tokens = self.model(image_tensor, output_hidden_states=True).hidden_states[-1]

            logger.debug(f"Encoded image to {tokens.shape[-2]} vision tokens (mode: {mode})")
            return tokens

        except torch.cuda.OutOfMemoryError as e:
            logger.warning(f"GPU OOM during encoding in {mode} mode")
            raise

    def encode_with_chunking(
        self,
        images: List[Image.Image],
        mode: Optional[str] = None
    ) -> List[torch.Tensor]:
        """
        Process multiple images in chunks to avoid OOM.

        Args:
            images: List of PIL Images
            mode: Compression mode or None for auto

        Returns:
            List of encoded vision token tensors
        """
        if mode is None:
            mode = self.current_mode

        encoded_chunks = []

        for idx, image in enumerate(images):
            try:
                # Clear cache between images
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()

                # Encode single image
                tokens = self.encode(image, mode=mode)
                encoded_chunks.append(tokens)

                # Offload to CPU if memory is critical
                if self._is_memory_critical():
                    logger.warning(f"Memory critical after encoding image {idx+1}/{len(images)}, offloading to CPU")
                    tokens = tokens.cpu()

            except torch.cuda.OutOfMemoryError:
                logger.error(f"Failed to encode image {idx+1}/{len(images)} due to OOM")
                # Try to recover by falling back to smaller mode
                if mode != 'tiny':
                    logger.info("Falling back to tiny mode")
                    tokens = self.encode(image, mode='tiny')
                    encoded_chunks.append(tokens.cpu())
                else:
                    raise

        return encoded_chunks

    def _prepare_image_tensor(self, image: Image.Image, target_size: int) -> torch.Tensor:
        """
        Convert PIL Image to tensor ready for model input.

        Args:
            image: PIL Image
            target_size: Target dimension (512, 640, or 1024)

        Returns:
            Image tensor normalized for model input
        """
        # Resize if needed
        if image.size != (target_size, target_size):
            image = image.resize((target_size, target_size), Image.Resampling.LANCZOS)

        # Convert to tensor and normalize
        import torchvision.transforms as transforms

        transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])

        tensor = transform(image).unsqueeze(0)  # Add batch dimension

        # Move to GPU if available
        if torch.cuda.is_available() and not self._is_memory_critical():
            tensor = tensor.cuda()

        return tensor

    def _get_free_memory_gb(self) -> float:
        """Get free GPU memory in GB."""
        if torch.cuda.is_available():
            free_mem, _ = torch.cuda.mem_get_info()
            return free_mem / 1e9
        return 0.0  # No GPU

    def _is_memory_critical(self) -> bool:
        """Check if GPU memory usage is critical (>90%)."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated()
            reserved = torch.cuda.memory_reserved()
            if reserved > 0:
                usage_ratio = allocated / reserved
                return usage_ratio > 0.9
        return False

    def get_mode_info(self, mode: str) -> dict:
        """
        Get information about a specific mode.

        Args:
            mode: Mode name

        Returns:
            Dict with mode configuration
        """
        return self.mode_configs.get(mode, {})

    def calculate_compression_ratio(self, text_tokens: int, vision_tokens: int) -> float:
        """
        Calculate compression ratio.

        Args:
            text_tokens: Original text token count
            vision_tokens: Compressed vision token count

        Returns:
            Compression ratio (e.g., 10.0 means 10x compression)
        """
        if vision_tokens == 0:
            return 0.0

        ratio = text_tokens / vision_tokens
        return ratio
