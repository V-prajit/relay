"""
MemoryGuard - Automatic memory management utility

Context manager that automatically clears GPU cache before and after operations
to prevent OOM errors on laptops with limited VRAM.
"""

import torch
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MemoryGuard:
    """
    Context manager for automatic GPU memory management.

    Usage:
        with MemoryGuard(threshold_percent=90):
            # Your GPU operations here
            result = model.encode(image)
    """

    def __init__(self, threshold_percent: int = 90):
        """
        Initialize memory guard.

        Args:
            threshold_percent: Memory usage threshold for auto-clearing (0-100)
        """
        self.threshold = threshold_percent
        self.initial_memory = None

    def __enter__(self):
        """Enter context - clear cache and record initial memory."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            self.initial_memory = torch.cuda.memory_allocated()
            logger.debug(f"MemoryGuard: Cleared cache, initial memory: {self.initial_memory / 1e9:.2f}GB")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context - clear cache and log memory delta."""
        if torch.cuda.is_available():
            final_memory = torch.cuda.memory_allocated()
            delta = (final_memory - self.initial_memory) / 1e9 if self.initial_memory else 0

            torch.cuda.empty_cache()

            logger.debug(f"MemoryGuard: Cleared cache, memory delta: {delta:+.2f}GB")

        # Don't suppress exceptions
        return False

    def check_and_clear(self) -> bool:
        """
        Check memory usage and clear cache if threshold exceeded.

        Returns:
            True if cache was cleared, False otherwise
        """
        if not torch.cuda.is_available():
            return False

        allocated = torch.cuda.memory_allocated()
        reserved = torch.cuda.memory_reserved()

        if reserved > 0:
            usage_percent = (allocated / reserved) * 100

            if usage_percent > self.threshold:
                torch.cuda.empty_cache()
                logger.info(f"Memory threshold exceeded ({usage_percent:.1f}%), cleared cache")
                return True

        return False

    @staticmethod
    def get_memory_stats() -> dict:
        """
        Get current GPU memory statistics.

        Returns:
            Dict with memory info (empty if no GPU)
        """
        if not torch.cuda.is_available():
            return {
                'gpu_available': False,
                'message': 'No GPU available'
            }

        allocated = torch.cuda.memory_allocated()
        reserved = torch.cuda.memory_reserved()
        free, total = torch.cuda.mem_get_info()

        return {
            'gpu_available': True,
            'allocated_gb': allocated / 1e9,
            'reserved_gb': reserved / 1e9,
            'free_gb': free / 1e9,
            'total_gb': total / 1e9,
            'usage_percent': (allocated / reserved * 100) if reserved > 0 else 0,
            'device_name': torch.cuda.get_device_name(0)
        }

    @staticmethod
    def force_clear_cache():
        """Force clear GPU cache immediately."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            logger.info("Forced GPU cache clear")

    @staticmethod
    def is_memory_critical(threshold_gb: float = 1.0) -> bool:
        """
        Check if available GPU memory is critically low.

        Args:
            threshold_gb: Critical threshold in GB

        Returns:
            True if memory is critical
        """
        if not torch.cuda.is_available():
            return False

        free, _ = torch.cuda.mem_get_info()
        free_gb = free / 1e9

        return free_gb < threshold_gb


# Convenience function for quick memory checks
def check_gpu_memory() -> None:
    """Print current GPU memory status."""
    stats = MemoryGuard.get_memory_stats()

    if stats.get('gpu_available'):
        print("=" * 50)
        print("GPU Memory Status")
        print("=" * 50)
        print(f"Device: {stats['device_name']}")
        print(f"Allocated: {stats['allocated_gb']:.2f}GB")
        print(f"Reserved: {stats['reserved_gb']:.2f}GB")
        print(f"Free: {stats['free_gb']:.2f}GB")
        print(f"Total: {stats['total_gb']:.2f}GB")
        print(f"Usage: {stats['usage_percent']:.1f}%")
        print("=" * 50)
    else:
        print(stats['message'])
