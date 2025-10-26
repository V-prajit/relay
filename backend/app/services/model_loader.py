"""
OptimizedModelLoader - Handles loading DeepSeek-OCR model with INT8 quantization for laptop constraints

This module provides memory-efficient model loading using bitsandbytes quantization,
reducing the 6.67GB model to ~2GB for laptop deployment.
"""

import os
import torch
from transformers import AutoModel, BitsAndBytesConfig
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OptimizedModelLoader:
    """
    Loads DeepSeek-OCR model with INT8 quantization for memory efficiency.

    Reduces model size from 6.67GB (BF16) to ~2GB (INT8) while maintaining
    reasonable accuracy for inference tasks.
    """

    def __init__(self, model_name: str = "deepseek-ai/DeepSeek-OCR", use_quantization: bool = True):
        """
        Initialize the model loader.

        Args:
            model_name: HuggingFace model identifier
            use_quantization: Whether to use INT8 quantization (default: True for laptops)
        """
        self.model_name = model_name
        self.use_quantization = use_quantization
        self.model = None

        # INT8 quantization config - reduces 6.67GB to ~2GB
        if use_quantization:
            self.bnb_config = BitsAndBytesConfig(
                load_in_8bit=True,
                bnb_8bit_compute_dtype=torch.float16,
                bnb_8bit_use_double_quant=True,  # Double quantization for further compression
            )
        else:
            self.bnb_config = None

    def load_model(self, offload_folder: str = "offload", max_memory: Optional[dict] = None):
        """
        Download and load the DeepSeek-OCR model with optimizations.

        Args:
            offload_folder: Directory for CPU offloading when GPU memory is insufficient
            max_memory: Dict specifying max memory per device (e.g., {0: "6GB", "cpu": "8GB"})

        Returns:
            Loaded model instance

        Raises:
            Exception: If model loading fails
        """
        try:
            logger.info(f"Loading model: {self.model_name}")
            logger.info(f"Quantization: {'Enabled (INT8)' if self.use_quantization else 'Disabled (BF16)'}")

            # Create offload directory if it doesn't exist
            os.makedirs(offload_folder, exist_ok=True)

            # Load model with automatic device mapping
            self.model = AutoModel.from_pretrained(
                self.model_name,
                quantization_config=self.bnb_config if self.use_quantization else None,
                device_map='auto',  # Automatic CPU/GPU splitting
                offload_folder=offload_folder,  # Disk offload for overflow
                trust_remote_code=True,  # Required for custom model components
                low_cpu_mem_usage=True,  # Reduce CPU memory during loading
                max_memory=max_memory,  # Memory constraints per device
            )

            # Move to appropriate dtype if not quantized
            if not self.use_quantization and torch.cuda.is_available():
                self.model = self.model.to(torch.bfloat16).cuda()

            logger.info("Model loaded successfully")
            self._print_memory_stats()

            return self.model

        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise

    def _print_memory_stats(self):
        """Print current memory usage statistics."""
        if torch.cuda.is_available():
            allocated = torch.cuda.memory_allocated() / 1e9
            reserved = torch.cuda.memory_reserved() / 1e9
            logger.info(f"GPU Memory - Allocated: {allocated:.2f}GB, Reserved: {reserved:.2f}GB")
        else:
            logger.info("Running on CPU - No GPU memory tracking")

    def unload_model(self):
        """Unload model from memory to free resources."""
        if self.model is not None:
            del self.model
            self.model = None

            if torch.cuda.is_available():
                torch.cuda.empty_cache()

            logger.info("Model unloaded from memory")

    def get_model_info(self) -> dict:
        """
        Get information about the loaded model.

        Returns:
            Dict with model metadata
        """
        if self.model is None:
            return {"status": "not_loaded"}

        info = {
            "model_name": self.model_name,
            "quantized": self.use_quantization,
            "device": str(next(self.model.parameters()).device),
            "dtype": str(next(self.model.parameters()).dtype),
        }

        if torch.cuda.is_available():
            info["gpu_memory_allocated_gb"] = torch.cuda.memory_allocated() / 1e9
            info["gpu_memory_reserved_gb"] = torch.cuda.memory_reserved() / 1e9

        return info


# Singleton instance for global model management
_model_loader_instance: Optional[OptimizedModelLoader] = None


def get_model_loader(model_name: str = "deepseek-ai/DeepSeek-OCR", use_quantization: bool = True) -> OptimizedModelLoader:
    """
    Get or create a singleton model loader instance.

    Args:
        model_name: HuggingFace model identifier
        use_quantization: Whether to use INT8 quantization

    Returns:
        OptimizedModelLoader instance
    """
    global _model_loader_instance

    if _model_loader_instance is None:
        _model_loader_instance = OptimizedModelLoader(model_name, use_quantization)

    return _model_loader_instance
