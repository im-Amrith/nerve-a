"""
Perception Engine: Computer Vision + Groq VLM for UI understanding.
Implements the "Screen-to-JSON" coordinate mapping without fragile DOM selectors.

NOTE: This module requires desktop GUI capabilities (PIL ImageGrab).
It will not work on headless Linux servers.
"""

from __future__ import annotations

import base64
import hashlib
import time
from io import BytesIO
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from datetime import datetime

# Type checking imports (not evaluated at runtime)
if TYPE_CHECKING:
    from PIL import Image as PILImage
    import numpy as np

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None
    CV2_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False

# PIL imports with graceful fallback for headless servers
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    Image = None
    PIL_AVAILABLE = False

try:
    from PIL import ImageGrab
    IMAGEGRAB_AVAILABLE = True
except (ImportError, OSError):
    # ImageGrab not available on headless Linux
    ImageGrab = None
    IMAGEGRAB_AVAILABLE = False

try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False

from loguru import logger

from ..core.state import UIElement, PerceptionResult


class PerceptionEngine:
    """
    Handles visual perception of trading UI using:
    1. Screenshot capture
    2. Computer vision preprocessing
    3. Groq VLM for semantic understanding
    4. Coordinate mapping for action execution
    
    NOTE: Requires desktop environment. Not available on headless servers.
    """
    
    def __init__(self, groq_api_key: str, model: str = "llama-3.2-90b-vision-preview"):
        if not GROQ_AVAILABLE:
            raise RuntimeError("Groq client not available. Install groq package.")
        if not IMAGEGRAB_AVAILABLE:
            raise RuntimeError(
                "PerceptionEngine requires desktop GUI capabilities (PIL ImageGrab). "
                "This is not available on headless Linux servers."
            )
        self.client = Groq(api_key=groq_api_key)
        self.model = model
        self.last_ui_hash = None
        
    def capture_screen(self, bbox: Optional[Tuple[int, int, int, int]] = None) -> Any:
        """
        Capture screenshot of the trading interface.
        
        Args:
            bbox: Optional bounding box (left, top, right, bottom) to capture specific region
            
        Returns:
            PIL Image of captured screen
        """
        try:
            screenshot = ImageGrab.grab(bbox=bbox)
            logger.info(f"Screenshot captured: {screenshot.size}")
            return screenshot
        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            raise
    
    def preprocess_image(self, image: Any) -> Tuple[Any, Any]:
        """
        Preprocess image for better VLM and CV analysis.
        
        Returns:
            Tuple of (processed PIL Image, OpenCV numpy array)
        """
        # Convert to numpy array for OpenCV
        img_array = np.array(image)
        img_cv = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Apply preprocessing for better edge detection
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Adaptive thresholding for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Convert back to PIL for VLM
        enhanced_rgb = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        enhanced_pil = Image.fromarray(enhanced_rgb)
        
        return enhanced_pil, img_cv
    
    def detect_ui_elements_cv(self, image_cv: Any) -> List[Dict]:
        """
        Use computer vision to detect UI elements (buttons, inputs, etc.).
        This provides fast, deterministic bounding boxes.
        
        Args:
            image_cv: OpenCV numpy array
            
        Returns:
            List of detected elements with coordinates
        """
        elements = []
        gray = cv2.cvtColor(image_cv, cv2.COLOR_BGR2GRAY)
        
        # Edge detection
        edges = cv2.Canny(gray, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            # Filter small contours
            area = cv2.contourArea(contour)
            if area < 100:  # Minimum area threshold
                continue
                
            x, y, w, h = cv2.boundingRect(contour)
            
            # Basic shape classification
            aspect_ratio = w / float(h) if h > 0 else 0
            element_type = "unknown"
            
            if 0.8 < aspect_ratio < 1.2 and area < 10000:
                element_type = "button"
            elif aspect_ratio > 3:
                element_type = "input_field"
            elif area > 50000:
                element_type = "chart_area"
            
            elements.append({
                "id": f"cv_element_{i}",
                "type": element_type,
                "coordinates": {"x": int(x), "y": int(y), "width": int(w), "height": int(h)},
                "area": int(area),
                "aspect_ratio": float(aspect_ratio)
            })
        
        logger.info(f"Detected {len(elements)} UI elements via CV")
        return elements
    
    def encode_image_base64(self, image: Any) -> str:
        """Convert PIL Image to base64 for Groq API."""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    def analyze_with_vlm(self, image: Any, cv_elements: List[Dict]) -> Dict:
        """
        Use Groq VLM to semantically understand the UI and map elements.
        
        Args:
            image: PIL Image of the UI
            cv_elements: Pre-detected elements from CV for grounding
            
        Returns:
            Structured analysis with semantic labels and coordinates
        """
        base64_image = self.encode_image_base64(image)
        
        # Construct prompt for semantic understanding
        prompt = f"""You are analyzing a trading interface screenshot. Your task is to identify and locate key trading UI elements.

Detected elements from computer vision (use these as anchors):
{cv_elements[:10]}  // Showing first 10 for context

Please identify and locate the following elements if present:
1. Buy/Sell buttons
2. Price input fields
3. Quantity input fields
4. Order type selectors (Market/Limit/Stop)
5. Symbol/ticker display
6. Current price display
7. Portfolio/positions panel
8. Order book
9. Chart area
10. Submit/Cancel buttons

For each element found, provide:
- semantic_label: A clear identifier (e.g., "buy_button", "price_input")
- coordinates: Best estimate of {{"x": X, "y": Y, "width": W, "height": H}}
- confidence: 0.0 to 1.0
- description: Brief description of what you see

Return your response as a structured JSON with this format:
{{
  "ui_type": "trading_platform_name",
  "elements": [
    {{
      "semantic_label": "buy_button",
      "element_type": "button",
      "coordinates": {{"x": 100, "y": 200, "width": 80, "height": 40}},
      "confidence": 0.95,
      "text_content": "BUY",
      "description": "Green button labeled BUY"
    }}
  ],
  "layout_description": "Overall UI layout description",
  "detected_state": "What trading state is visible (e.g., order entry, portfolio view)"
}}

Respond ONLY with valid JSON, no additional text."""

        try:
            start_time = time.time()
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            inference_time = (time.time() - start_time) * 1000
            logger.info(f"VLM inference completed in {inference_time:.2f}ms")
            
            raw_response = response.choices[0].message.content
            
            # Parse JSON response
            import json
            try:
                # Try to extract JSON if wrapped in markdown
                if "```json" in raw_response:
                    json_str = raw_response.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_response:
                    json_str = raw_response.split("```")[1].split("```")[0].strip()
                else:
                    json_str = raw_response.strip()
                    
                parsed = json.loads(json_str)
                parsed["inference_time_ms"] = inference_time
                parsed["raw_response"] = raw_response
                return parsed
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse VLM JSON response: {e}")
                logger.debug(f"Raw response: {raw_response}")
                return {
                    "ui_type": "unknown",
                    "elements": [],
                    "layout_description": "Failed to parse",
                    "detected_state": "error",
                    "raw_response": raw_response,
                    "error": str(e)
                }
                
        except Exception as e:
            logger.error(f"VLM analysis failed: {e}")
            raise
    
    def compute_ui_hash(self, image: Any) -> str:
        """
        Compute hash of UI layout for change detection.
        Uses perceptual hashing to detect meaningful UI changes.
        """
        # Resize to standard size for consistent hashing
        img_resized = image.resize((64, 64), Image.Resampling.LANCZOS)
        img_gray = img_resized.convert('L')
        
        # Convert to numpy and compute hash
        img_array = np.array(img_gray)
        hash_value = hashlib.md5(img_array.tobytes()).hexdigest()
        
        return hash_value
    
    def detect_ui_change(self, current_hash: str) -> bool:
        """
        Detect if UI has changed significantly since last perception.
        This enables self-healing when UI elements move.
        """
        if self.last_ui_hash is None:
            self.last_ui_hash = current_hash
            return False
        
        changed = current_hash != self.last_ui_hash
        if changed:
            logger.warning(f"UI change detected! Old: {self.last_ui_hash[:8]}... New: {current_hash[:8]}...")
            self.last_ui_hash = current_hash
        
        return changed
    
    def perceive(self, bbox: Optional[Tuple[int, int, int, int]] = None) -> PerceptionResult:
        """
        Main perception loop: Capture -> Analyze -> Map
        
        Args:
            bbox: Optional screen region to capture
            
        Returns:
            PerceptionResult with all detected elements and mappings
        """
        logger.info("Starting perception cycle...")
        
        # Step 1: Capture screen
        screenshot = self.capture_screen(bbox)
        
        # Step 2: Preprocess
        processed_img, cv_image = self.preprocess_image(screenshot)
        
        # Step 3: CV-based element detection (fast, deterministic)
        cv_elements = self.detect_ui_elements_cv(cv_image)
        
        # Step 4: VLM semantic understanding (slow, intelligent)
        vlm_analysis = self.analyze_with_vlm(screenshot, cv_elements)
        
        # Step 5: Merge CV and VLM results
        ui_elements = []
        for elem in vlm_analysis.get("elements", []):
            ui_element = UIElement(
                element_type=elem.get("element_type", "unknown"),
                coordinates=elem.get("coordinates", {"x": 0, "y": 0, "width": 0, "height": 0}),
                confidence=elem.get("confidence", 0.0),
                text_content=elem.get("text_content"),
                semantic_label=elem.get("semantic_label", "unknown")
            )
            ui_elements.append(ui_element)
        
        # Step 6: Build coordinate map for actions
        coordinate_map = {
            elem.semantic_label: elem.coordinates
            for elem in ui_elements
            if elem.confidence > 0.5
        }
        
        # Step 7: Compute UI hash for change detection
        ui_hash = self.compute_ui_hash(screenshot)
        ui_changed = self.detect_ui_change(ui_hash)
        
        result = PerceptionResult(
            screenshot_timestamp=datetime.now(),
            detected_elements=ui_elements,
            ui_state_hash=ui_hash,
            raw_vision_response=vlm_analysis.get("raw_response", ""),
            coordinate_map=coordinate_map
        )
        
        logger.success(f"Perception complete: {len(ui_elements)} elements mapped, UI changed: {ui_changed}")
        return result
    
    def get_element_center(self, semantic_label: str, perception: PerceptionResult) -> Optional[Tuple[int, int]]:
        """
        Get the center coordinates of an element by semantic label.
        Used for click actions.
        
        Args:
            semantic_label: Element to locate (e.g., "buy_button")
            perception: Latest perception result
            
        Returns:
            (x, y) tuple of center coordinates, or None if not found
        """
        if semantic_label not in perception.coordinate_map:
            logger.warning(f"Element '{semantic_label}' not found in coordinate map")
            return None
        
        coords = perception.coordinate_map[semantic_label]
        center_x = coords["x"] + coords["width"] // 2
        center_y = coords["y"] + coords["height"] // 2
        
        return (center_x, center_y)
