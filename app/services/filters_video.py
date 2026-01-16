"""Video filter builders for FFmpeg."""


def build_eq_filter(brightness: float, contrast: float, saturation: float) -> str:
    """
    Build eq filter for brightness/contrast/saturation adjustment.

    All values have "no effect" defaults: brightness=0, contrast=1, saturation=1
    """
    # Check if any adjustments needed
    if brightness == 0.0 and contrast == 1.0 and saturation == 1.0:
        return ""

    return f"eq=brightness={brightness}:contrast={contrast}:saturation={saturation}"


def build_blur_filter(sigma: float) -> str:
    """Build gblur (Gaussian blur) filter."""
    if sigma <= 0:
        return ""

    return f"gblur=sigma={sigma}"


def build_sharpen_filter(amount: float) -> str:
    """
    Build unsharp filter for sharpening.

    Uses 5x5 luma matrix with specified amount.
    """
    if amount <= 0:
        return ""

    return f"unsharp=5:5:{amount}:5:5:0"


def build_transform_filter(filter_str: str) -> str:
    """Return transform filter string directly (hflip, vflip, transpose, etc.)."""
    return filter_str if filter_str else ""


def build_crop_filter(aspect_ratio: str) -> str:
    """
    Build crop filter for aspect ratio change.

    Supported ratios: "4:3", "16:9", "1:1"
    Crops from center, using min() to handle both landscape and portrait videos.
    """
    if not aspect_ratio or aspect_ratio == "original":
        return ""

    # Map aspect ratio to crop expression
    # Use min() to ensure crop doesn't exceed input dimensions
    # For landscape: uses height-based calculation
    # For portrait: uses width-based calculation
    ratios = {
        "4:3": "crop=min(iw\\,ih*4/3):min(ih\\,iw*3/4)",
        "16:9": "crop=min(iw\\,ih*16/9):min(ih\\,iw*9/16)",
        "1:1": "crop=min(iw\\,ih):min(iw\\,ih)",
    }
    return ratios.get(aspect_ratio, "")


def build_overlay_filter(overlay_type: str) -> str:
    """
    Build drawtext filter for video overlays.

    Types: "security_cam", "timestamp", etc.

    Note: Colons in drawtext text values must be escaped as \\: for FFmpeg.
    """
    if overlay_type == "security_cam":
        # Timestamp top-left, REC indicator top-right, CAM ID bottom-left
        font = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
        # FFmpeg drawtext escaping:
        # - Filter parser runs BEFORE text expansion
        # - ALL colons in text value must be escaped as \: at filter level
        # - After filter parsing, \: becomes : for text expansion
        return (
            f"drawtext=fontfile={font}:"
            "text='%{localtime\\:%Y-%m-%d %H\\:%M\\:%S}':"
            "fontcolor=white:fontsize=18:x=10:y=10,"
            f"drawtext=fontfile={font}:"
            "text='REC':fontcolor=red:fontsize=18:x=w-tw-10:y=10,"
            f"drawtext=fontfile={font}:"
            "text='CAM 01':fontcolor=white:fontsize=16:x=10:y=h-th-10"
        )
    return ""


def build_colorshift_filter(shift_amount: int) -> str:
    """
    Build rgbashift filter for glitch-like color channel displacement.

    shift_amount: pixel displacement for red/blue channels
    """
    if shift_amount <= 0:
        return ""

    # Shift red left, blue right for classic glitch look
    return f"rgbashift=rh=-{shift_amount}:bh={shift_amount}"


def build_scale_filter(width: int, height: int) -> str:
    """
    Build scale filter for resolution change.

    Args:
        width: Target width in pixels
        height: Target height in pixels

    Returns:
        FFmpeg scale filter string or empty if no scaling needed
    """
    if width <= 0 or height <= 0:
        return ""

    return f"scale={width}:{height}"
