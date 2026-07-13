"""Helpers for encoding Pillow images without blocking the Discord event loop."""

import asyncio
from io import BytesIO

from PIL import Image


def _encode_png(image: Image.Image) -> BytesIO:
    buffer = BytesIO()
    # The previews are transient Discord attachments; fast compression keeps
    # interactions responsive while preserving lossless PNG output.
    image.save(buffer, format="PNG", optimize=False, compress_level=3)
    buffer.seek(0)
    return buffer


async def encode_png(image: Image.Image) -> BytesIO:
    return await asyncio.to_thread(_encode_png, image)
