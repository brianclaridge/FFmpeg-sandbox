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
