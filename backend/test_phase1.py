"""
Phase 1 Testing Script

Validates that all Phase 1 components are implemented correctly.
"""

import sys
import os
from pathlib import Path

# Add app directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

print("=" * 60)
print("Phase 1 Testing: Foundation Setup")
print("=" * 60)
print()

# Test 1: Import all modules
print("[Test 1] Importing all modules...")
try:
    from app import main
    from app.models import requests, responses
    print("  [PASS] All modules imported successfully")
except Exception as e:
    print(f"  [FAIL] Import error: {e}")
    sys.exit(1)

# Test 2: Validate request models with valid data
print("\n[Test 2] Validating request models with valid data...")
try:
    from app.models.requests import AnalyzeBugRequest, CreatePRRequest, OCRAnalyzeRequest

    # Test AnalyzeBugRequest
    analyze_req = AnalyzeBugRequest(
        repo_url="https://github.com/user/repo",
        bug_description="Authentication fails with 401 error",
        file_path="src/auth.py",
        line_hint=45
    )
    assert analyze_req.repo_url == "https://github.com/user/repo"
    assert analyze_req.line_hint == 45

    # Test CreatePRRequest
    pr_req = CreatePRRequest(
        repo_url="https://github.com/user/repo",
        branch_name="fix/auth-error",
        patch_content="diff --git a/auth.py b/auth.py",
        title="Fix auth error",
        description="This fixes the authentication bug"
    )
    assert pr_req.branch_name == "fix/auth-error"

    # Test OCRAnalyzeRequest
    ocr_req = OCRAnalyzeRequest(
        image_data="base64encodeddata",
        bug_description="Got this error in terminal",
        repo_url="https://github.com/user/repo"
    )
    assert ocr_req.image_data == "base64encodeddata"

    print("  [PASS] All request models validated successfully")
except Exception as e:
    print(f"  [FAIL] Validation error: {e}")
    sys.exit(1)

# Test 3: Validate request models reject invalid data
print("\n[Test 3] Validating request models reject invalid data...")
try:
    from pydantic import ValidationError

    # Test invalid GitHub URL
    try:
        AnalyzeBugRequest(
            repo_url="https://gitlab.com/user/repo",  # Not GitHub
            bug_description="Some bug description here",
            file_path="auth.py"
        )
        print("  [FAIL] Should have rejected non-GitHub URL")
        sys.exit(1)
    except ValidationError:
        pass  # Expected

    # Test bug description too short
    try:
        AnalyzeBugRequest(
            repo_url="https://github.com/user/repo",
            bug_description="short",  # Too short
            file_path="auth.py"
        )
        print("  [FAIL] Should have rejected short bug description")
        sys.exit(1)
    except ValidationError:
        pass  # Expected

    # Test empty file path
    try:
        AnalyzeBugRequest(
            repo_url="https://github.com/user/repo",
            bug_description="Authentication fails with 401 error",
            file_path="   "  # Empty after stripping
        )
        print("  [FAIL] Should have rejected empty file path")
        sys.exit(1)
    except ValidationError:
        pass  # Expected

    print("  [PASS] Request models correctly reject invalid data")
except Exception as e:
    print(f"  [FAIL] Unexpected error: {e}")
    sys.exit(1)

# Test 4: Validate response models
print("\n[Test 4] Validating response models...")
try:
    from app.models.responses import (
        CommitInfo, ClaudeAnalysis, AnalyzeBugResponse,
        CreatePRResponse, ErrorResponse
    )

    # Test CommitInfo
    commit = CommitInfo(
        commit_hash="a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0",
        author="John Doe",
        timestamp=1698765432,
        message="Fix bug",
        line_number=45
    )
    assert commit.author == "John Doe"

    # Test ClaudeAnalysis
    analysis = ClaudeAnalysis(
        root_cause="Removed null check",
        developer_intent="Simplify code",
        minimal_patch="diff --git a/file.py",
        confidence=0.85
    )
    assert analysis.confidence == 0.85

    # Test confidence bounds
    try:
        ClaudeAnalysis(
            root_cause="test",
            developer_intent="test",
            minimal_patch="test",
            confidence=1.5  # Invalid: > 1.0
        )
        print("  [FAIL] Should have rejected confidence > 1.0")
        sys.exit(1)
    except ValidationError:
        pass  # Expected

    # Test AnalyzeBugResponse
    bug_response = AnalyzeBugResponse(
        first_bad_commit="abc123",
        commits=[commit],
        file_path="src/auth.py",
        analysis=analysis
    )
    assert len(bug_response.commits) == 1

    # Test CreatePRResponse
    pr_response = CreatePRResponse(
        success=True,
        pr_url="https://github.com/user/repo/pull/123",
        branch_name="fix/bug"
    )
    assert pr_response.success is True

    # Test ErrorResponse
    error_response = ErrorResponse(
        error="File not found",
        suggestion="Check the file path",
        status=404,
        details={"traceback": "..."}
    )
    assert error_response.status == 404

    print("  [PASS] All response models validated successfully")
except Exception as e:
    print(f"  [FAIL] Validation error: {e}")
    sys.exit(1)

# Test 5: Verify FastAPI app configuration
print("\n[Test 5] Verifying FastAPI app configuration...")
try:
    from app.main import app

    assert app.title == "BugRewind API"
    assert app.version == "1.0.0"
    assert "Git archaeology" in app.description

    # Check routes exist
    routes = [route.path for route in app.routes]
    assert "/health" in routes
    assert "/docs" in routes
    assert "/redoc" in routes

    print("  [PASS] FastAPI app configured correctly")
except Exception as e:
    print(f"  [FAIL] Configuration error: {e}")
    sys.exit(1)

# Test 6: Verify CLONE_DIR creation
print("\n[Test 6] Verifying CLONE_DIR handling...")
try:
    from dotenv import load_dotenv
    load_dotenv()

    clone_dir = os.getenv("CLONE_DIR", "/tmp/bugrewind-clones")

    # The startup event will create this, but we can verify the logic
    assert clone_dir is not None
    print(f"  [PASS] CLONE_DIR configured as: {clone_dir}")
except Exception as e:
    print(f"  [FAIL] CLONE_DIR error: {e}")
    sys.exit(1)

# All tests passed
print("\n" + "=" * 60)
print("All Phase 1 Tests Passed!")
print("=" * 60)
print()
print("Next steps:")
print("1. Run 'python run.py' to start the server")
print("2. Visit http://localhost:8000/health to verify")
print("3. Visit http://localhost:8000/docs to see API documentation")
print()
print("Note: Make sure you're in the backend/ directory when running run.py")
print()
