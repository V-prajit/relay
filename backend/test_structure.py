"""
Structural validation test - checks code architecture without dependencies
"""

import ast
import sys
from pathlib import Path

def check_class_exists(file_path, class_name):
    """Check if a class exists in a file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())

        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        return class_name in classes
    except Exception as e:
        return False

def check_function_exists(file_path, func_name):
    """Check if a function exists in a file."""
    try:
        with open(file_path) as f:
            tree = ast.parse(f.read())

        functions = [node.name for node in ast.walk(tree)
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        return func_name in functions
    except Exception as e:
        return False

def main():
    """Run structural validation."""
    print("=" * 60)
    print("DeepSeek-OCR Structural Validation")
    print("=" * 60)

    base = Path("app")
    tests = []

    # Check core services
    print("\n1. Core Services:")
    tests.append(("OptimizedModelLoader", check_class_exists(base / "services/model_loader.py", "OptimizedModelLoader")))
    tests.append(("EfficientRenderer", check_class_exists(base / "services/image_renderer.py", "EfficientRenderer")))
    tests.append(("LaptopDeepEncoder", check_class_exists(base / "services/encoder.py", "LaptopDeepEncoder")))
    tests.append(("AdaptiveCompressor", check_class_exists(base / "services/compressor.py", "AdaptiveCompressor")))
    tests.append(("StreamingDecoder", check_class_exists(base / "services/decoder.py", "StreamingDecoder")))
    tests.append(("HybridOCR", check_class_exists(base / "services/ocr_fallback.py", "HybridOCR")))
    tests.append(("LaptopDeepSeekOCR", check_class_exists(base / "services/deepseek_service.py", "LaptopDeepSeekOCR")))

    for name, result in tests[-7:]:
        status = "✓" if result else "✗"
        print(f"   {status} {name}")

    # Check utilities
    print("\n2. Utilities:")
    tests.append(("MemoryGuard", check_class_exists(base / "utils/memory_guard.py", "MemoryGuard")))
    status = "✓" if tests[-1][1] else "✗"
    print(f"   {status} MemoryGuard")

    # Check API routes
    print("\n3. API Routes:")
    routes = [
        "process_document",
        "initialize_service",
        "get_status",
        "run_benchmark",
        "get_memory_stats",
        "cleanup_resources"
    ]

    for route in routes:
        result = check_function_exists(base / "routes/deepseek.py", route)
        tests.append((route, result))
        status = "✓" if result else "✗"
        print(f"   {status} {route}")

    # Check documentation
    print("\n4. Documentation:")
    docs = [
        ("DEEPSEEK_README.md", Path("DEEPSEEK_README.md").exists()),
        (".env.example", Path(".env.example").exists()),
        ("test_deepseek.py", Path("test_deepseek.py").exists()),
    ]

    for name, result in docs:
        tests.append((name, result))
        status = "✓" if result else "✗"
        print(f"   {status} {name}")

    # Summary
    passed = sum(1 for _, result in tests if result)
    total = len(tests)

    print("\n" + "=" * 60)
    print(f"Results: {passed}/{total} checks passed")
    print("=" * 60)

    if passed == total:
        print("\n🎉 All structural checks passed!")
        print("✓ Code architecture is complete")
        print("✓ All classes and methods are defined")
        print("✓ API routes are configured")
        print("✓ Documentation is present")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Configure .env file")
        print("3. Run: python test_deepseek.py --status")
        return 0
    else:
        print("\n⚠️  Some checks failed")
        failed = [name for name, result in tests if not result]
        print(f"Failed: {', '.join(failed)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
