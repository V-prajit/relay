"""
DeepSeek-OCR CLI Test Script

Tests the DeepSeek-OCR implementation with a sample document.

Usage:
    python test_deepseek.py <file_path> [--mode MODE] [--format FORMAT] [--benchmark]
"""

import sys
import argparse
import logging
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.deepseek_service import LaptopDeepSeekOCR
from app.utils.memory_guard import MemoryGuard, check_gpu_memory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Test DeepSeek-OCR implementation")
    parser.add_argument('file', nargs='?', help='PDF or image file to process')
    parser.add_argument('--mode', default='auto', choices=['tiny', 'small', 'base', 'auto'],
                        help='Compression mode (default: auto)')
    parser.add_argument('--format', default='text', choices=['text', 'markdown', 'html'],
                        help='Output format (default: text)')
    parser.add_argument('--benchmark', action='store_true',
                        help='Run performance benchmark instead of processing file')
    parser.add_argument('--max-memory', type=int, default=8,
                        help='Max GPU memory in GB (default: 8)')
    parser.add_argument('--no-quantization', action='store_true',
                        help='Disable INT8 quantization (requires more memory)')
    parser.add_argument('--status', action='store_true',
                        help='Show system status only')

    args = parser.parse_args()

    # Show GPU memory at start
    print("\n" + "=" * 60)
    print("DeepSeek-OCR Test Script")
    print("=" * 60)
    check_gpu_memory()

    # Initialize service
    print("\nInitializing DeepSeek-OCR...")
    ocr_service = LaptopDeepSeekOCR(
        memory_limit_gb=args.max_memory,
        enable_quantization=not args.no_quantization
    )

    try:
        success = ocr_service.initialize()

        if not success:
            print("\n⚠️  DeepSeek model unavailable - running in fallback mode")
            print("Available engines:", ocr_service.fallback.get_available_engines())

        # Show system info
        if args.status:
            print("\n" + "=" * 60)
            print("System Information")
            print("=" * 60)
            import json
            system_info = ocr_service.get_system_info()
            print(json.dumps(system_info, indent=2))
            return

        # Run benchmark
        if args.benchmark:
            print("\n" + "=" * 60)
            print("Running Performance Benchmark")
            print("=" * 60)

            if not ocr_service.initialized:
                print("❌ Cannot run benchmark - model not initialized")
                return

            results = ocr_service.benchmark_performance()

            print("\nBenchmark Results:")
            print("-" * 60)
            for mode, result in results.items():
                if result['works']:
                    print(f"✓ {mode.upper():6s} mode: {result['time_seconds']:.3f}s, "
                          f"{result['memory_gb']:.2f}GB")
                else:
                    print(f"✗ {mode.upper():6s} mode: FAILED - {result.get('error', 'Unknown error')}")

            check_gpu_memory()
            return

        # Process file
        if not args.file:
            parser.error("File path required (or use --benchmark/--status)")

        file_path = Path(args.file)
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            return

        print(f"\nProcessing: {file_path.name}")
        print(f"Mode: {args.mode}")
        print(f"Format: {args.format}")
        print("-" * 60)

        # Process with memory guard
        with MemoryGuard():
            result = ocr_service.process_file(
                str(file_path),
                output_format=args.format,
                mode=args.mode if args.mode != 'auto' else None,
                stream=False
            )

        # Display results
        print("\n" + "=" * 60)
        print("Extracted Text")
        print("=" * 60)
        print(result)
        print("=" * 60)
        print(f"\nTotal length: {len(result)} characters")

        # Show final memory state
        check_gpu_memory()

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        print(f"\n❌ Error: {str(e)}")
    finally:
        # Cleanup
        print("\nCleaning up...")
        ocr_service.cleanup()
        print("✓ Done")


if __name__ == "__main__":
    main()
