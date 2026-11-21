"""
FastAPI REST API Service for Easy Cartoonify.
"""

from io import BytesIO
from typing import Any, Dict, List
import cv2
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from easy_cartoonify import __version__
from easy_cartoonify.core import Cartoonifier
from easy_cartoonify.exceptions import EasyCartoonifyError
from easy_cartoonify.models import CartoonConfig, CartoonStyle

app = FastAPI(
    title="Easy Cartoonify API",
    description="Production REST microservice for converting images into cartoon, comic art, and sketches.",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Monitoring"])
async def health_check() -> Dict[str, Any]:
    """Health check probe for container orchestrators (Kubernetes, ECS)."""
    return {
        "status": "healthy",
        "service": "easy-cartoonify",
        "version": __version__,
    }


@app.get("/api/v1/styles", tags=["Cartoonify"])
async def list_styles() -> List[Dict[str, str]]:
    """List all supported cartoon styles and descriptions."""
    return [
        {
            "id": CartoonStyle.STYLE_1.value,
            "name": "Smooth Painterly Cartoon",
            "description": "Smooth painterly cartoon effect with soft color transitions (Legacy Style 1).",
        },
        {
            "id": CartoonStyle.STYLE_2.value,
            "name": "Crisp Vibrant Cartoon",
            "description": "Crisp cartoon effect with saturated colors and sharp edges (Legacy Style 2).",
        },
        {
            "id": CartoonStyle.CLASSIC.value,
            "name": "Classic Comic Book",
            "description": "Classic graphic novel / comic book aesthetic using bilateral filtering and adaptive ink lines.",
        },
        {
            "id": CartoonStyle.PENCIL_GRAY.value,
            "name": "Pencil Sketch (B&W)",
            "description": "Monochrome graphite pencil sketch effect.",
        },
        {
            "id": CartoonStyle.PENCIL_COLOR.value,
            "name": "Pencil Sketch (Color)",
            "description": "Colored pencil sketch effect.",
        },
        {
            "id": CartoonStyle.EDGE_PRESERVE.value,
            "name": "Edge-Preserving Stylization",
            "description": "High-fidelity photographic smoothing while retaining all sharp features.",
        },
    ]


@app.post("/api/v1/cartoonify", tags=["Cartoonify"])
async def cartoonify_image(
    file: UploadFile = File(..., description="Image file to process (JPEG, PNG, WebP)"),
    style: str = Form(
        default=CartoonStyle.STYLE_1.value,
        description="Style name or number (style_1, style_2, classic, pencil_gray, pencil_color, edge_preserve)",
    ),
    sigma_s: float = Form(
        default=None,
        description="Spatial smoothness parameter (optional override)",
    ),
    sigma_r: float = Form(
        default=None,
        description="Range color smoothness parameter (optional override)",
    ),
    format: str = Form(
        default="jpeg",
        description="Output format: jpeg, png, or webp",
    ),
) -> Response:
    """
    Upload an image and receive the transformed cartoonified image.
    """
    try:
        style_enum = CartoonStyle.from_input(style)
        config = CartoonConfig.default_for_style(style_enum)

        if sigma_s is not None:
            config.sigma_s = sigma_s
        if sigma_r is not None:
            config.sigma_r = sigma_r

    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty.")

    try:
        engine = Cartoonifier(config)
        processed = engine.process(content, config=config)

        ext = format.lower().strip(".")
        if ext in ("jpg", "jpeg"):
            mime_type = "image/jpeg"
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
            encode_ext = ".jpg"
        elif ext == "png":
            mime_type = "image/png"
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 3]
            encode_ext = ".png"
        elif ext == "webp":
            mime_type = "image/webp"
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 95]
            encode_ext = ".webp"
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported output format '{format}'. Use 'jpeg', 'png', or 'webp'.",
            )

        success, encoded = cv2.imencode(encode_ext, processed, encode_param)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to encode cartoonified image.",
            )

        return Response(
            content=encoded.tobytes(),
            media_type=mime_type,
            headers={
                "Content-Disposition": f'inline; filename="{file.filename or "cartoon"}_{style_enum.value}{encode_ext}"'
            },
        )

    except EasyCartoonifyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Processing failed: {exc}")
