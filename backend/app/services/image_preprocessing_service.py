"""
image_preprocessing_service.py
================================
Stage 2 — OpenCV Image Preprocessing Pipeline

Pipeline steps (in order):
  1. Load & validate (reject non-images)
  2. EXIF auto-orientation
  3. Resize guard (max 4096px)
  4. Glare detection & suppression (Navier-Stokes inpainting)
  5. CLAHE contrast enhancement (LAB L-channel)
  6. Skew detection & correction (Hough lines)
  7. Perspective correction (largest quad contour warp) — best-effort
  8. Denoising (fastNlMeansDenoisingColored)
  9. Unsharp mask sharpening
 10. Save processed JPEG + grayscale PNG; return PreprocessingResult
"""

import os
import time
import logging
import math
from dataclasses import dataclass, field
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image, ExifTags

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Configuration Constants
# ---------------------------------------------------------------------------
MAX_DIMENSION_PX: int = 4096          # Resize guard ceiling
JPEG_QUALITY: int = 95                 # Output JPEG quality
SKEW_THRESHOLD_DEG: float = 0.5       # Minimum skew to correct
GLARE_THRESHOLD: int = 240            # Brightness threshold for specular highlight
GLARE_INPAINT_RADIUS: int = 5         # Inpainting radius (pixels)
CLAHE_CLIP_LIMIT: float = 2.0         # CLAHE contrast limit
CLAHE_TILE_SIZE: Tuple[int, int] = (8, 8)  # CLAHE tile grid size
DENOISE_H: int = 10                   # Denoising filter strength
DENOISE_TEMPLATE_WINDOW: int = 7      # Template window size
DENOISE_SEARCH_WINDOW: int = 21       # Search window size
UNSHARP_SIGMA: float = 1.0            # Unsharp mask Gaussian sigma
UNSHARP_STRENGTH: float = 1.5         # Unsharp mask blend weight


# ---------------------------------------------------------------------------
# Result Dataclass
# ---------------------------------------------------------------------------
@dataclass
class PreprocessingResult:
    """Structured result returned by ImagePreprocessingService.preprocess()."""
    success: bool
    processed_image_path: str = ""          # Color JPEG path
    grayscale_image_path: str = ""          # Grayscale PNG path
    skew_angle_degrees: float = 0.0
    perspective_corrected: bool = False
    glare_regions_detected: int = 0
    contrast_enhanced: bool = False
    original_width: int = 0
    original_height: int = 0
    processed_width: int = 0
    processed_height: int = 0
    processing_time_ms: float = 0.0
    quality_score: float = 0.0              # 0–100 IQA metric
    detected_barcode: Optional[str] = None  # EAN-13, UPC, DataMatrix digits
    barcode_type: Optional[str] = None      # EAN_13, QRCODE, etc.
    error_message: Optional[str] = None
    pipeline_steps: list = field(default_factory=list)  # Audit trail of steps


# ---------------------------------------------------------------------------
# Main Service
# ---------------------------------------------------------------------------
class ImagePreprocessingService:
    """
    Stateless service — call preprocess() for each image.
    All heavy lifting uses OpenCV + NumPy; PIL is used only for EXIF.
    """

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def preprocess(
        self,
        input_path: str,
        output_dir: str,
        filename_stem: str,
    ) -> PreprocessingResult:
        """
        Run the full preprocessing pipeline on a single image.

        Args:
            input_path:    Absolute path to the raw uploaded image.
            output_dir:    Directory where processed outputs will be saved.
            filename_stem: Base name (without extension) for output files.

        Returns:
            PreprocessingResult dataclass.
        """
        t_start = time.monotonic()
        steps: list[str] = []
        result = PreprocessingResult(success=False)

        try:
            os.makedirs(output_dir, exist_ok=True)

            # ── Step 1: Load & Validate ──────────────────────────────────
            img, orig_h, orig_w = self._load_image(input_path)
            result.original_width = orig_w
            result.original_height = orig_h
            steps.append("load_validate")

            # ── Step 2: EXIF Auto-Orientation ────────────────────────────
            img = self._apply_exif_orientation(img, input_path)
            steps.append("exif_orientation")

            # ── Step 3: Resize Guard ─────────────────────────────────────
            img = self._resize_guard(img)
            steps.append("resize_guard")

            # ── Step 4: Glare Detection & Suppression ────────────────────
            img, glare_count = self._suppress_glare(img)
            result.glare_regions_detected = glare_count
            steps.append(f"glare_suppression(regions={glare_count})")

            # ── Step 5: CLAHE Contrast Enhancement ───────────────────────
            img = self._apply_clahe(img)
            result.contrast_enhanced = True
            steps.append("clahe_contrast")

            # ── Step 6: Skew Detection & Correction ──────────────────────
            img, skew_angle = self._correct_skew(img)
            result.skew_angle_degrees = round(skew_angle, 3)
            steps.append(f"skew_correction(angle={skew_angle:.2f}°)")

            # ── Step 7: Perspective Correction (best-effort) ─────────────
            img, perspective_applied = self._correct_perspective(img)
            result.perspective_corrected = perspective_applied
            steps.append(f"perspective_correction(applied={perspective_applied})")

            # ── Step 8: Denoising ────────────────────────────────────────
            img = self._denoise(img)
            steps.append("denoising")

            # ── Step 9: Unsharp Mask Sharpening ─────────────────────────
            img = self._unsharp_mask(img)
            steps.append("unsharp_mask")

            # ── Step 10: Save Outputs ────────────────────────────────────
            processed_path = os.path.join(output_dir, f"{filename_stem}_processed.jpg")
            gray_path = os.path.join(output_dir, f"{filename_stem}_gray.png")

            cv2.imwrite(processed_path, img, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            cv2.imwrite(gray_path, gray)

            processed_h, processed_w = img.shape[:2]
            result.processed_width = processed_w
            result.processed_height = processed_h
            steps.append("save_outputs")

            # ── Step 11: Image Quality Score ─────────────────────────────
            result.quality_score = self._compute_quality_score(img, gray)
            steps.append(f"quality_score({result.quality_score:.1f})")

            # ── Step 12: Barcode & GS1 EAN-13 Decoding ───────────────────
            bcode, btype = self._detect_barcode(img)
            if bcode:
                result.detected_barcode = bcode
                result.barcode_type = btype
                steps.append(f"barcode_detected({bcode})")

            result.success = True
            result.processed_image_path = processed_path
            result.grayscale_image_path = gray_path

        except FileNotFoundError as exc:
            result.error_message = f"File not found: {exc}"
            logger.error("Preprocessing failed — file not found: %s", exc)
        except ValueError as exc:
            result.error_message = str(exc)
            logger.error("Preprocessing failed — validation error: %s", exc)
        except Exception as exc:  # pylint: disable=broad-except
            result.error_message = f"Unexpected error: {exc}"
            logger.exception("Preprocessing pipeline raised an unhandled exception")
        finally:
            elapsed_ms = (time.monotonic() - t_start) * 1000
            result.processing_time_ms = round(elapsed_ms, 2)
            result.pipeline_steps = steps

        return result

    # ------------------------------------------------------------------
    # Step 1 — Load & Validate
    # ------------------------------------------------------------------
    def _load_image(self, path: str) -> Tuple[np.ndarray, int, int]:
        """Load image via OpenCV; raise ValueError if not a valid image."""
        if not os.path.isfile(path):
            raise FileNotFoundError(path)

        img = cv2.imread(path, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError(
                f"OpenCV could not decode '{path}'. "
                "File may not be a supported image format (JPEG/PNG/WEBP/BMP)."
            )
        h, w = img.shape[:2]
        if h < 32 or w < 32:
            raise ValueError(f"Image too small: {w}×{h} px (minimum 32×32).")
        return img, h, w

    # ------------------------------------------------------------------
    # Step 2 — EXIF Auto-Orientation
    # ------------------------------------------------------------------
    def _apply_exif_orientation(self, img: np.ndarray, path: str) -> np.ndarray:
        """Rotate image to EXIF upright orientation using Pillow EXIF data."""
        try:
            pil_img = Image.open(path)
            exif_data = pil_img._getexif()  # noqa: SLF001  (private but stable)
            if exif_data is None:
                return img

            orientation_tag = next(
                (k for k, v in ExifTags.TAGS.items() if v == "Orientation"), None
            )
            if orientation_tag is None:
                return img

            orientation = exif_data.get(orientation_tag)
            rotations = {
                3: cv2.ROTATE_180,
                6: cv2.ROTATE_90_CLOCKWISE,
                8: cv2.ROTATE_90_COUNTERCLOCKWISE,
            }
            if orientation in rotations:
                img = cv2.rotate(img, rotations[orientation])
        except Exception:  # pylint: disable=broad-except
            # Non-critical — continue without EXIF correction
            pass
        return img

    # ------------------------------------------------------------------
    # Step 3 — Resize Guard
    # ------------------------------------------------------------------
    def _resize_guard(self, img: np.ndarray) -> np.ndarray:
        """Downscale to MAX_DIMENSION_PX on the longest side, preserving aspect ratio."""
        h, w = img.shape[:2]
        max_side = max(h, w)
        if max_side <= MAX_DIMENSION_PX:
            return img
        scale = MAX_DIMENSION_PX / max_side
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)

    # ------------------------------------------------------------------
    # Step 4 — Glare Detection & Suppression
    # ------------------------------------------------------------------
    def _suppress_glare(self, img: np.ndarray) -> Tuple[np.ndarray, int]:
        """
        Detect specular highlights and inpaint them.

        Strategy:
          - Convert to HSV; threshold high V (brightness) channel
          - Morphologically close the mask to cover contiguous glare blobs
          - Inpaint with Navier-Stokes algorithm
        """
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        v_channel = hsv[:, :, 2]

        # Create glare mask: bright pixels above threshold
        _, glare_mask = cv2.threshold(v_channel, GLARE_THRESHOLD, 255, cv2.THRESH_BINARY)

        # Morphological close to fill small gaps in glare blobs
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (15, 15))
        glare_mask = cv2.morphologyEx(glare_mask, cv2.MORPH_CLOSE, kernel)

        # Count distinct glare regions
        num_labels, _ = cv2.connectedComponents(glare_mask)
        glare_count = max(0, num_labels - 1)  # subtract background label

        if glare_count == 0:
            return img, 0

        # Inpaint only if glare covers < 40% of image (avoid destroying over-exposed shots)
        total_pixels = glare_mask.shape[0] * glare_mask.shape[1]
        glare_pixels = np.count_nonzero(glare_mask)
        if glare_pixels / total_pixels > 0.40:
            logger.warning("Glare covers >40%% of image — skipping inpainting to preserve detail.")
            return img, glare_count

        inpainted = cv2.inpaint(img, glare_mask, GLARE_INPAINT_RADIUS, cv2.INPAINT_NS)
        return inpainted, glare_count

    # ------------------------------------------------------------------
    # Step 5 — CLAHE Contrast Enhancement
    # ------------------------------------------------------------------
    def _apply_clahe(self, img: np.ndarray) -> np.ndarray:
        """
        Apply CLAHE to the L channel of LAB colorspace.
        This enhances local contrast without blowing out colors.
        """
        lab = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
        l_channel, a_channel, b_channel = cv2.split(lab)

        clahe = cv2.createCLAHE(clipLimit=CLAHE_CLIP_LIMIT, tileGridSize=CLAHE_TILE_SIZE)
        l_enhanced = clahe.apply(l_channel)

        enhanced_lab = cv2.merge([l_enhanced, a_channel, b_channel])
        return cv2.cvtColor(enhanced_lab, cv2.COLOR_Lab2BGR)

    # ------------------------------------------------------------------
    # Step 6 — Skew Detection & Correction
    # ------------------------------------------------------------------
    def _correct_skew(self, img: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Detect dominant rotation angle using probabilistic Hough lines on Canny edges.
        Rotate to deskew if angle exceeds SKEW_THRESHOLD_DEG.

        Returns: (corrected_image, detected_angle_degrees)
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150, apertureSize=3)

        # Probabilistic Hough on edge map
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi / 180,
            threshold=100,
            minLineLength=img.shape[1] // 4,  # at least 25% of width
            maxLineGap=20,
        )

        if lines is None or len(lines) == 0:
            return img, 0.0

        # Compute angle for each line segment
        angles = []
        for line in lines:
            # OpenCV 4 returns shape (N, 1, 4); OpenCV 5 returns shape (N, 4).
            # Flatten to a 1-D array so unpacking works for both versions.
            coords = line.flatten()
            if len(coords) < 4:
                continue
            x1, y1, x2, y2 = int(coords[0]), int(coords[1]), int(coords[2]), int(coords[3])
            if x2 - x1 == 0:  # vertical line — skip
                continue
            angle_rad = math.atan2(y2 - y1, x2 - x1)
            angle_deg = math.degrees(angle_rad)
            # Normalise to [-45, 45] range to avoid large rotation
            if angle_deg < -45:
                angle_deg += 90
            elif angle_deg > 45:
                angle_deg -= 90
            angles.append(angle_deg)

        if not angles:
            return img, 0.0

        # Robust median angle
        median_angle = float(np.median(angles))

        if abs(median_angle) < SKEW_THRESHOLD_DEG:
            return img, median_angle  # No correction needed

        # Rotate around the image center
        h, w = img.shape[:2]
        center = (w / 2.0, h / 2.0)
        rot_matrix = cv2.getRotationMatrix2D(center, median_angle, 1.0)

        # Expand canvas to avoid black corners after rotation
        abs_cos = abs(rot_matrix[0, 0])
        abs_sin = abs(rot_matrix[0, 1])
        new_w = int(h * abs_sin + w * abs_cos)
        new_h = int(h * abs_cos + w * abs_sin)
        rot_matrix[0, 2] += new_w / 2 - center[0]
        rot_matrix[1, 2] += new_h / 2 - center[1]

        rotated = cv2.warpAffine(
            img, rot_matrix, (new_w, new_h),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_REPLICATE,
        )
        return rotated, median_angle

    # ------------------------------------------------------------------
    # Step 7 — Perspective Correction (best-effort)
    # ------------------------------------------------------------------
    def _correct_perspective(self, img: np.ndarray) -> Tuple[np.ndarray, bool]:
        """
        Detect the largest quadrilateral contour (document/label boundary)
        and warp it into a top-down rectangle.

        Returns: (warped_image, was_applied)
        If no suitable quad is found, returns the original image unchanged.
        """
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 75, 200)

        # Dilate edges to close small gaps in contour
        kernel = np.ones((3, 3), np.uint8)
        edges = cv2.dilate(edges, kernel, iterations=1)

        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if not contours:
            return img, False

        # Sort by area, largest first
        contours = sorted(contours, key=cv2.contourArea, reverse=True)

        img_area = img.shape[0] * img.shape[1]
        quad = None

        for contour in contours[:5]:  # Check only top-5 by area
            area = cv2.contourArea(contour)
            if area < 0.10 * img_area:  # Quad must cover at least 10% of image
                break

            peri = cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

            if len(approx) == 4:
                quad = approx
                break

        if quad is None:
            return img, False

        # Order quad corners: top-left, top-right, bottom-right, bottom-left
        pts = quad.reshape(4, 2).astype(np.float32)
        ordered = self._order_quad_points(pts)

        # Compute destination rectangle dimensions
        tl, tr, br, bl = ordered
        width_top = np.linalg.norm(tr - tl)
        width_bottom = np.linalg.norm(br - bl)
        height_left = np.linalg.norm(bl - tl)
        height_right = np.linalg.norm(br - tr)

        dst_w = int(max(width_top, width_bottom))
        dst_h = int(max(height_left, height_right))

        if dst_w < 32 or dst_h < 32:
            return img, False

        dst_pts = np.array(
            [[0, 0], [dst_w - 1, 0], [dst_w - 1, dst_h - 1], [0, dst_h - 1]],
            dtype=np.float32,
        )

        M = cv2.getPerspectiveTransform(ordered, dst_pts)
        warped = cv2.warpPerspective(img, M, (dst_w, dst_h), flags=cv2.INTER_CUBIC)
        return warped, True

    def _order_quad_points(self, pts: np.ndarray) -> np.ndarray:
        """Order 4 points as [top-left, top-right, bottom-right, bottom-left]."""
        # Sum of coordinates: top-left has smallest sum, bottom-right has largest
        s = pts.sum(axis=1)
        tl = pts[np.argmin(s)]
        br = pts[np.argmax(s)]

        # Difference: top-right has smallest diff, bottom-left has largest
        d = np.diff(pts, axis=1)
        tr = pts[np.argmin(d)]
        bl = pts[np.argmax(d)]

        return np.array([tl, tr, br, bl], dtype=np.float32)

    # ------------------------------------------------------------------
    # Step 8 — Denoising
    # ------------------------------------------------------------------
    def _denoise(self, img: np.ndarray) -> np.ndarray:
        """
        Apply Non-Local Means denoising for color images.
        Falls back to bilateral filter if image is unusually large.
        """
        h, w = img.shape[:2]
        pixel_count = h * w

        # fastNlMeans is O(N²) — use bilateral for very large images
        if pixel_count > 3_000_000:
            return cv2.bilateralFilter(img, d=9, sigmaColor=75, sigmaSpace=75)

        return cv2.fastNlMeansDenoisingColored(
            img,
            h=DENOISE_H,
            hColor=DENOISE_H,
            templateWindowSize=DENOISE_TEMPLATE_WINDOW,
            searchWindowSize=DENOISE_SEARCH_WINDOW,
        )

    # ------------------------------------------------------------------
    # Step 9 — Unsharp Mask Sharpening
    # ------------------------------------------------------------------
    def _unsharp_mask(self, img: np.ndarray) -> np.ndarray:
        """
        Enhance edge crispness via unsharp masking:
          sharpened = original * (1 + strength) - gaussian_blur * strength
        """
        blurred = cv2.GaussianBlur(img, (0, 0), UNSHARP_SIGMA)
        sharpened = cv2.addWeighted(img, UNSHARP_STRENGTH, blurred, -(UNSHARP_STRENGTH - 1), 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    # ------------------------------------------------------------------
    # Step 11 — Image Quality Assessment
    # ------------------------------------------------------------------
    def _compute_quality_score(self, color_img: np.ndarray, gray_img: np.ndarray) -> float:
        """
        Composite quality score (0–100) based on three pillars:
          - Sharpness:  Variance of Laplacian (high = sharp)
          - Brightness: How close mean luminance is to midpoint (128)
          - Contrast:   Standard deviation of the gray channel

        Scores are normalized against empirical thresholds tuned
        for product label photography conditions.
        """
        # --- Sharpness (Laplacian variance) ---
        lap_var = cv2.Laplacian(gray_img, cv2.CV_64F).var()
        sharpness_score = min(100.0, (lap_var / 500.0) * 100.0)  # 500 = "very sharp" baseline

        # --- Brightness (distance from ideal midpoint 128) ---
        mean_brightness = float(np.mean(gray_img))
        brightness_delta = abs(mean_brightness - 128.0)
        brightness_score = max(0.0, 100.0 - (brightness_delta / 1.28))  # 128 delta → 0 score

        # --- Contrast (std dev of gray) ---
        std_dev = float(np.std(gray_img.astype(np.float64)))
        contrast_score = min(100.0, (std_dev / 60.0) * 100.0)  # 60 std = "good contrast" baseline

        # Weighted composite: sharpness matters most for OCR readability
        composite = (0.50 * sharpness_score) + (0.25 * brightness_score) + (0.25 * contrast_score)
        return round(min(100.0, max(0.0, composite)), 2)

    # ------------------------------------------------------------------
    # Step 12 — Barcode Detection & GS1 Decoding
    # ------------------------------------------------------------------
    def _detect_barcode(self, img_bgr: np.ndarray) -> Tuple[Optional[str], Optional[str]]:
        """
        Detects and decodes 1D/2D barcodes (EAN-13, UPC-A, DataMatrix) using OpenCV BarcodeDetector.
        """
        try:
            if hasattr(cv2, 'barcode') and hasattr(cv2.barcode, 'BarcodeDetector'):
                detector = cv2.barcode.BarcodeDetector()
                retval, decoded_info, decoded_type, _ = detector.detectAndDecode(img_bgr)
                if retval and decoded_info:
                    for info, btype in zip(decoded_info, decoded_type):
                        if info and info.strip():
                            return info.strip(), str(btype)
        except Exception as exc:
            logger.debug("Barcode detection skipped or unsupported: %s", str(exc))
        return None, None


# Module-level singleton
image_preprocessing_service = ImagePreprocessingService()
