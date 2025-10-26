"""
DeepSeek-OCR API Routes

Provides endpoints for document OCR processing using DeepSeek-OCR with visual context compression.
"""

import os
import tempfile
from pathlib import Path
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import JSONResponse

from ..services.deepseek_service import get_deepseek_service
from ..utils.memory_guard import MemoryGuard
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

# Global service instance (initialized on startup)
deepseek_service = None


@router.post("/ocr/process")
async def process_document(
    file: UploadFile = File(..., description="PDF or image file to process"),
    output_format: str = Form("text", description="Output format: text, markdown, or html"),
    mode: Optional[str] = Form(None, description="Compression mode: tiny, small, base, or auto"),
    stream: bool = Form(False, description="Enable streaming output")
):
    """
    Process a document with DeepSeek-OCR and extract text.

    The system automatically:
    - Renders documents at optimized resolution
    - Compresses to vision tokens (10x+ token reduction)
    - Decodes back to text with 97%+ accuracy
    - Falls back to traditional OCR if needed

    **Compression Modes:**
    - `tiny` (512×512, 64 tokens): Up to 600 text tokens, 9x compression
    - `small` (640×640, 100 tokens): Up to 900 text tokens, 9x compression
    - `base` (1024×1024, 256 tokens): Up to 2500 text tokens, 10x compression
    - `auto`: Automatically selects best mode (recommended)

    **Output Formats:**
    - `text`: Plain text extraction
    - `markdown`: Structured markdown with layout preservation
    - `html`: HTML table format (useful for tabular data)
    """
    global deepseek_service

    if deepseek_service is None:
        raise HTTPException(
            status_code=503,
            detail="DeepSeek service not initialized. Please initialize via /ocr/init endpoint."
        )

    # Validate output format
    valid_formats = ['text', 'markdown', 'html']
    if output_format not in valid_formats:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid output_format. Must be one of: {', '.join(valid_formats)}"
        )

    # Validate mode
    if mode and mode not in ['tiny', 'small', 'base', 'auto']:
        raise HTTPException(
            status_code=400,
            detail="Invalid mode. Must be one of: tiny, small, base, auto"
        )

    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name

        logger.info(f"Processing uploaded file: {file.filename} ({len(content) / 1e6:.2f}MB)")

        # Process with DeepSeek
        with MemoryGuard():
            result_text = deepseek_service.process_file(
                tmp_path,
                output_format=output_format,
                mode=mode if mode != 'auto' else None,
                stream=stream
            )

        # Clean up temp file
        os.unlink(tmp_path)

        return JSONResponse(content={
            "status": "success",
            "filename": file.filename,
            "output_format": output_format,
            "text": result_text,
            "length": len(result_text)
        })

    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error processing document: {str(e)}")
        # Clean up temp file if it exists
        try:
            if 'tmp_path' in locals():
                os.unlink(tmp_path)
        except:
            pass

        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.post("/ocr/init")
async def initialize_service(
    memory_limit_gb: float = Form(8, description="GPU memory limit in GB"),
    enable_quantization: bool = Form(True, description="Enable INT8 quantization")
):
    """
    Initialize the DeepSeek-OCR service.

    This endpoint loads the model and initializes all components.
    Call this once before processing documents.

    **Parameters:**
    - `memory_limit_gb`: Maximum GPU memory to use (default: 8GB)
    - `enable_quantization`: Use INT8 quantization for memory efficiency (default: True)

    **Note:** Initialization may take 1-2 minutes on first run to download the 6.67GB model.
    """
    global deepseek_service

    try:
        logger.info("Initializing DeepSeek-OCR service...")

        deepseek_service = get_deepseek_service(
            memory_limit_gb=memory_limit_gb,
            enable_quantization=enable_quantization
        )

        success = deepseek_service.initialize()

        if success:
            system_info = deepseek_service.get_system_info()
            return JSONResponse(content={
                "status": "success",
                "message": "DeepSeek-OCR initialized successfully",
                "system_info": system_info
            })
        else:
            return JSONResponse(
                status_code=200,  # Still return 200 as fallback mode is valid
                content={
                    "status": "fallback_mode",
                    "message": "DeepSeek model unavailable, running in fallback mode (PaddleOCR/Tesseract)",
                    "available_engines": deepseek_service.fallback.get_available_engines()
                }
            )

    except Exception as e:
        logger.error(f"Initialization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Initialization failed: {str(e)}")


@router.get("/ocr/status")
async def get_status():
    """
    Get current status and system information.

    Returns initialization status, memory usage, and available features.
    """
    global deepseek_service

    if deepseek_service is None:
        return JSONResponse(content={
            "initialized": False,
            "message": "Service not initialized. Call /ocr/init to initialize."
        })

    try:
        system_info = deepseek_service.get_system_info()
        return JSONResponse(content={
            "status": "ok",
            **system_info
        })
    except Exception as e:
        logger.error(f"Error getting status: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ocr/benchmark")
async def run_benchmark():
    """
    Run performance benchmark to test available compression modes.

    Tests Tiny (512), Small (640), and Base (1024) modes to determine
    what works on the current hardware.
    """
    global deepseek_service

    if deepseek_service is None or not deepseek_service.initialized:
        raise HTTPException(
            status_code=503,
            detail="Service not initialized or model not loaded"
        )

    try:
        results = deepseek_service.benchmark_performance()
        return JSONResponse(content={
            "status": "success",
            "benchmark_results": results
        })
    except Exception as e:
        logger.error(f"Benchmark failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ocr/memory")
async def get_memory_stats():
    """
    Get current GPU memory statistics.

    Useful for monitoring memory usage during processing.
    """
    memory_stats = MemoryGuard.get_memory_stats()
    return JSONResponse(content=memory_stats)


@router.post("/ocr/cleanup")
async def cleanup_resources():
    """
    Clean up resources and free GPU memory.

    Call this to unload the model and free memory when done processing.
    """
    global deepseek_service

    if deepseek_service:
        try:
            deepseek_service.cleanup()
            deepseek_service = None
            return JSONResponse(content={
                "status": "success",
                "message": "Resources cleaned up successfully"
            })
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    else:
        return JSONResponse(content={
            "status": "ok",
            "message": "No resources to clean up"
        })
