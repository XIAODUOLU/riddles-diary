"""
Image editing client utility.

This module provides functions to upload local images and save edited images
using an AI image editing API.
"""
import base64
import logging
import os
import re
from pathlib import Path
from typing import Optional, Union, List

import cv2
import numpy as np
import requests

logger = logging.getLogger(__name__)

# Global configuration - can be overridden via environment variables
API_URL = os.getenv("IMAGE_EDIT_API_URL", "https://api.example.com/v1/chat/completions")
API_KEY = os.getenv("IMAGE_EDIT_API_KEY", "your-api-key")
MODEL = os.getenv("IMAGE_EDIT_MODEL", "gpt-4-vision")


def image_to_base64(image_path: Union[str, Path]) -> str:
    """
    Convert a local image to base64 encoding.

    Args:
        image_path: Path to the image file.

    Returns:
        Base64 encoded image string with data URI prefix.

    Raises:
        FileNotFoundError: If the image file does not exist.
        ValueError: If the image cannot be read or encoded.
    """
    image_path = Path(image_path)
    
    if not image_path.exists():
        raise FileNotFoundError(f"Image file not found: {image_path}")

    # Read image file
    img = cv2.imread(str(image_path))
    
    if img is None:
        raise ValueError(f"Unable to read image file: {image_path}")

    # Determine image format from file extension
    ext = image_path.suffix.lower()
    if ext in [".jpg", ".jpeg"]:
        img_format = "jpeg"
    elif ext == ".png":
        img_format = "png"
    elif ext == ".webp":
        img_format = "webp"
    else:
        img_format = "png"  # Default format

    # Encode image
    success, encoded_img = cv2.imencode(f".{img_format}", img)
    
    if not success:
        raise ValueError(f"Failed to encode image: {image_path}")

    # Convert to base64
    img_base64 = base64.b64encode(encoded_img.tobytes()).decode("utf-8")
    
    # Add data URI prefix
    data_uri = f"data:image/{img_format};base64,{img_base64}"
    
    logger.info(f"Successfully converted image to base64: {image_path}")
    return data_uri


def base64_to_image(base64_str: str, output_path: Union[str, Path]) -> bool:
    """
    Convert a base64 string to an image and save it.

    Args:
        base64_str: Base64 encoded image string.
        output_path: Path where the image will be saved.

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Extract base64 data and image format
        pattern = r"data:image/(\w+);base64,(.+)"
        match = re.findall(pattern, base64_str)

        if match:
            img_format, img_data = match[0]
            img_format = img_format.lower()
        else:
            # If no prefix, use the entire string
            img_data = base64_str
            img_format = "jpg"

        # Decode base64
        img_bytes = base64.b64decode(img_data)

        # Convert to numpy array
        nparr = np.frombuffer(img_bytes, np.uint8)

        # Decode with OpenCV
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is None:
            logger.error("Unable to decode image, please check base64 data")
            return False

        # Ensure output directory exists
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine file extension
        if output_path.suffix.lower() not in [".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"]:
            if img_format == "png":
                output_path = output_path.with_suffix(".png")
            elif img_format == "webp":
                output_path = output_path.with_suffix(".webp")
            elif img_format in ["jpg", "jpeg"]:
                output_path = output_path.with_suffix(".jpg")
            else:
                output_path = output_path.with_suffix(".png")

        # Save image
        success = cv2.imwrite(str(output_path), img)
        if success:
            logger.info(f"Image saved to: {output_path}")
        else:
            logger.error(f"Failed to save image: {output_path}")
            
        return success
        
    except Exception as e:
        logger.error(f"Failed to convert base64 to image: {str(e)}")
        logger.exception("Detailed error:", exc_info=True)
        return False


def edit_image(
    image_paths: List[Union[str, Path]],
    user_prompt: str,
    output_path: Union[str, Path],
    api_url: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 600,
) -> bool:
    """
    Edit an image using AI and save the result.

    Args:
        image_paths: Paths to the input image.
        user_prompt: User prompt describing the desired edit.
        output_path: Path where the edited image will be saved.
        api_url: Optional API URL override. If None, uses global API_URL.
        api_key: Optional API key override. If None, uses global API_KEY.
        model: Optional model override. If None, uses global MODEL.
        timeout: Request timeout in seconds (default: 600).

    Returns:
        True if successful, False otherwise.
    """
    try:
        # Use provided values or fall back to globals
        api_url = api_url or API_URL
        api_key = api_key or API_KEY
        model = model or MODEL

        content = [
            {"type": "text", "text": user_prompt}
        ]

        # Read local image and convert to base64
        for image_path in image_paths:
            logger.info(f"Reading local image: {image_path}")
            image_base64 = image_to_base64(image_path)
            content.append(
                {
                    "type": "image_url",
                    "image_url": {"url": image_base64}
                }
            )

        # Build user message
        user_message = {
            "role": "user",
            "content": content
        }

        # Build request payload
        payload = {
            "model": model,
            "messages": [user_message],
        }

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Send request
        logger.info(f"Sending image edit request to API: {api_url}")
        resp = requests.post(url=api_url, json=payload, headers=headers, timeout=timeout)

        if resp.status_code != 200:
            logger.error(f"API request failed with status {resp.status_code}: {resp.text}")
            raise Exception(f"Image edit failed: {resp.text}")

        # Parse response
        result = resp.json()["choices"][0]["message"]["content"]

        # Save edited image
        logger.info(f"Saving edited image to: {output_path}")
        success = base64_to_image(result, output_path)

        if success:
            logger.info(f"Image editing completed successfully: {output_path}")
        else:
            logger.error("Failed to save edited image")

        return success

    except Exception as e:
        logger.error(f"Image editing process failed: {str(e)}")
        logger.exception("Detailed error:", exc_info=True)
        return False


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    # Example: Edit an image
    success = edit_image(
        image_paths=["input.jpg"],
        user_prompt="Change this model to red color",
        output_path="output.png",
    )

    if success:
        print("Image editing successful!")
    else:
        print("Image editing failed!")
