"""
Utility functions for vision, memory, and validation.
"""

import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional


def resize_image_for_vlm(image: Image.Image, max_size: int = 1024) -> Image.Image:
    """
    Resize image to fit within VLM constraints while maintaining aspect ratio.
    
    Args:
        image: Input PIL Image
        max_size: Maximum dimension size
        
    Returns:
        Resized PIL Image
    """
    width, height = image.size
    
    if width <= max_size and height <= max_size:
        return image
    
    if width > height:
        new_width = max_size
        new_height = int((max_size / width) * height)
    else:
        new_height = max_size
        new_width = int((max_size / height) * width)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)


def enhance_screenshot_for_ocr(image: np.ndarray) -> np.ndarray:
    """
    Enhance screenshot for better OCR accuracy.
    
    Args:
        image: OpenCV image (numpy array)
        
    Returns:
        Enhanced image
    """
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply bilateral filter to reduce noise while keeping edges sharp
    denoised = cv2.bilateralFilter(gray, 9, 75, 75)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    return thresh


def calculate_image_similarity(img1: np.ndarray, img2: np.ndarray) -> float:
    """
    Calculate structural similarity between two images.
    
    Args:
        img1: First image
        img2: Second image
        
    Returns:
        Similarity score 0-1 (1 = identical)
    """
    from skimage.metrics import structural_similarity as ssim
    
    # Resize images to same size if needed
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    
    # Convert to grayscale if needed
    if len(img1.shape) == 3:
        img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    if len(img2.shape) == 3:
        img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Calculate SSIM
    similarity = ssim(img1, img2)
    return similarity


def is_element_visible(
    element_coords: dict, 
    screenshot_size: Tuple[int, int]
) -> bool:
    """
    Check if an element is visible within screenshot bounds.
    
    Args:
        element_coords: Dict with x, y, width, height
        screenshot_size: (width, height) of screenshot
        
    Returns:
        True if element is fully visible
    """
    x = element_coords.get("x", 0)
    y = element_coords.get("y", 0)
    w = element_coords.get("width", 0)
    h = element_coords.get("height", 0)
    
    screen_w, screen_h = screenshot_size
    
    return (
        x >= 0 and y >= 0 and
        x + w <= screen_w and
        y + h <= screen_h and
        w > 0 and h > 0
    )


def create_clickable_region(
    coords: dict, 
    margin: int = 5
) -> Tuple[int, int, int, int]:
    """
    Create a clickable region with margin around element.
    
    Args:
        coords: Element coordinates {x, y, width, height}
        margin: Pixels to add around element
        
    Returns:
        (x1, y1, x2, y2) tuple for clickable region
    """
    x = coords.get("x", 0)
    y = coords.get("y", 0)
    w = coords.get("width", 0)
    h = coords.get("height", 0)
    
    return (
        max(0, x - margin),
        max(0, y - margin),
        x + w + margin,
        y + h + margin
    )


def validate_trade_symbol(symbol: str) -> bool:
    """
    Validate trading symbol format.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        True if valid format
    """
    import re
    
    # Basic validation: 1-5 uppercase letters
    pattern = r'^[A-Z]{1,5}$'
    return bool(re.match(pattern, symbol.upper()))


def sanitize_user_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks.
    
    Args:
        text: User input string
        
    Returns:
        Sanitized string
    """
    import html
    
    # Remove potential script tags
    text = html.escape(text)
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32 or char in '\n\r\t')
    
    return text


def format_currency(amount: float) -> str:
    """
    Format number as currency.
    
    Args:
        amount: Dollar amount
        
    Returns:
        Formatted string like "$1,234.56"
    """
    return f"${amount:,.2f}"


def format_percentage(value: float) -> str:
    """
    Format decimal as percentage.
    
    Args:
        value: Decimal value (0.1 = 10%)
        
    Returns:
        Formatted string like "10.00%"
    """
    return f"{value * 100:.2f}%"


def calculate_position_value(quantity: int, price: float) -> float:
    """
    Calculate total position value.
    
    Args:
        quantity: Number of shares
        price: Price per share
        
    Returns:
        Total value
    """
    return quantity * price


def calculate_risk_reward_ratio(
    entry_price: float,
    stop_loss: float,
    target_price: float
) -> float:
    """
    Calculate risk/reward ratio for a trade.
    
    Args:
        entry_price: Entry price
        stop_loss: Stop loss price
        target_price: Target profit price
        
    Returns:
        Risk/reward ratio
    """
    risk = abs(entry_price - stop_loss)
    reward = abs(target_price - entry_price)
    
    if risk == 0:
        return float('inf')
    
    return reward / risk
