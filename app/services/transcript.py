"""Transcript extraction service.

Extracts subtitles/captions from videos and converts to plain text.
- Downloaded files: Fetch captions from source URL via yt-dlp
- Local files: Extract embedded subtitles via ffmpeg
"""

import re
import subprocess
import tempfile
from pathlib import Path
from dataclasses import dataclass

from loguru import logger

from app.config import OUTPUT_DIR
from app.services.file_metadata import load_file_metadata


@dataclass
class TranscriptResult:
    """Result of transcript extraction."""
    success: bool
    text: str = ""
    output_path: Path | None = None
    source_type: str = ""  # "url" or "embedded"
    subtitle_type: str = ""  # "manual" or "auto"
    error: str = ""


class SubtitleParser:
    """Parse VTT/SRT subtitle files to plain text."""

    # VTT timestamp: 00:00:00.000 --> 00:00:00.000
    TS_LINE = re.compile(r"^\d{1,2}:\d{2}:\d{2}\.\d{3}\s-->\s\d{1,2}:\d{2}:\d{2}\.\d{3}.*$")
    # SRT timestamp: 00:00:00,000 --> 00:00:00,000
    SRT_TS = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3}\s-->\s\d{2}:\d{2}:\d{2},\d{3}.*$")

    @staticmethod
    def to_plain_text(sub: str) -> str:
        """Convert subtitle content to plain text.

        Removes:
        - WEBVTT header
        - Timestamps
        - Cue indices
        - HTML/VTT tags
        - Speaker labels
        - Duplicate consecutive lines
        """
        lines = []
        for ln in sub.splitlines():
            s = ln.strip()
            if not s:
                continue
            # Skip WEBVTT header
            if s.upper() == "WEBVTT":
                continue
            # Skip cue index (SRT)
            if s.isdigit():
                continue
            # Skip timestamps
            if SubtitleParser.TS_LINE.match(s) or SubtitleParser.SRT_TS.match(s):
                continue
            # Skip NOTE sections
            if s.upper().startswith("NOTE"):
                continue
            # Skip STYLE sections
            if s.upper().startswith("STYLE"):
                continue
            # Strip HTML/VTT tags like <c>, <v>, <b>, etc.
            s = re.sub(r"<[^>]+>", "", s)
            # Strip VTT speaker labels like ">>" or "NAME:"
            s = re.sub(r"^\>\>\s*", "", s)
            # Strip inline timing tags
            s = re.sub(r"<\d{2}:\d{2}:\d{2}\.\d{3}>", "", s)
            lines.append(s)

        # De-dupe repeated consecutive lines (common in captions)
        deduped = []
        for ln in lines:
            if not deduped or deduped[-1] != ln:
                deduped.append(ln)

        return "\n".join(deduped).strip()


def extract_transcript(input_file: str, lang: str = "en") -> TranscriptResult:
    """Extract transcript from input file.

    Strategy:
    1. Check if file has source URL in metadata -> fetch from URL
    2. Otherwise, try to extract embedded subtitles from file

    Args:
        input_file: Name of the input file
        lang: Preferred subtitle language code

    Returns:
        TranscriptResult with extracted text or error
    """
    from app.config import INPUT_DIR

    # Load file metadata to check for source URL
    metadata = load_file_metadata(input_file)
    source_url = metadata.get("source", {}).get("url", "")

    if source_url:
        logger.info(f"Extracting transcript from URL: {source_url}")
        return extract_from_url(source_url, lang)

    # Try embedded subtitles
    input_path = INPUT_DIR / input_file
    if input_path.exists():
        logger.info(f"Extracting embedded subtitles from: {input_path}")
        return extract_embedded_subtitles(input_path, lang)

    return TranscriptResult(
        success=False,
        error="File not found"
    )


def extract_from_url(url: str, lang: str = "en", prefer: str = "manual") -> TranscriptResult:
    """Fetch subtitles from URL via yt-dlp.

    Args:
        url: Source URL (YouTube, etc.)
        lang: Subtitle language code
        prefer: "manual" for human subs first, "auto" for auto-captions first

    Returns:
        TranscriptResult with extracted text
    """
    with tempfile.TemporaryDirectory() as td:
        outtmpl = str(Path(td) / "sub.%(ext)s")

        # Try manual subs first, then auto (or vice versa based on prefer)
        attempts = ("manual", "auto") if prefer == "manual" else ("auto", "manual")
        last_err = None
        subtitle_type = ""

        for kind in attempts:
            try:
                _yt_dlp_download(url, kind, lang, outtmpl)
                raw_sub, sub_file = _read_downloaded_sub(td)

                if raw_sub.strip():
                    text = SubtitleParser.to_plain_text(raw_sub)
                    if text.strip():
                        subtitle_type = kind
                        # Save transcript
                        output_path = save_transcript(text, url)
                        return TranscriptResult(
                            success=True,
                            text=text,
                            output_path=output_path,
                            source_type="url",
                            subtitle_type=subtitle_type,
                        )
            except Exception as e:
                logger.debug(f"yt-dlp {kind} subs failed: {e}")
                last_err = e

        error_msg = "No captions available for this video"
        if last_err:
            error_msg = f"Could not fetch captions from source URL: {last_err}"

        return TranscriptResult(
            success=False,
            error=error_msg
        )


def _yt_dlp_download(url: str, kind: str, lang: str, outtmpl: str) -> None:
    """Download subtitles via yt-dlp."""
    cmd = [
        "yt-dlp",
        "--skip-download",
        "--no-warnings",
        "--no-progress",
        "--sub-langs", lang,
        "--sub-format", "vtt/srt/best",
        "-o", outtmpl,
        url,
    ]

    if kind == "auto":
        cmd.insert(1, "--write-auto-subs")
    else:
        cmd.insert(1, "--write-subs")

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

    if result.returncode != 0:
        raise RuntimeError(f"yt-dlp failed ({kind}): {result.stderr.strip() or result.stdout.strip()}")


def _read_downloaded_sub(tmpdir: str) -> tuple[str, Path | None]:
    """Read downloaded subtitle file from temp directory."""
    td = Path(tmpdir)
    candidates = sorted(td.glob("sub.*"))

    if not candidates:
        return "", None

    # Prefer VTT/SRT
    candidates.sort(key=lambda p: (0 if p.suffix.lower() in (".vtt", ".srt") else 1, p.name))
    sub_file = candidates[0]
    raw = sub_file.read_text(encoding="utf-8", errors="replace")

    return raw, sub_file


def extract_embedded_subtitles(input_path: Path, lang: str = "en") -> TranscriptResult:
    """Extract embedded subtitles from video file using ffmpeg.

    Args:
        input_path: Path to the video file
        lang: Preferred subtitle language

    Returns:
        TranscriptResult with extracted text
    """
    # First, probe for subtitle streams
    probe_cmd = [
        "ffprobe",
        "-v", "quiet",
        "-print_format", "json",
        "-show_streams",
        "-select_streams", "s",
        str(input_path),
    ]

    try:
        result = subprocess.run(probe_cmd, capture_output=True, text=True, timeout=30)

        if result.returncode != 0:
            return TranscriptResult(
                success=False,
                error="No captions available for this file"
            )

        import json
        probe_data = json.loads(result.stdout)
        streams = probe_data.get("streams", [])

        if not streams:
            return TranscriptResult(
                success=False,
                error="No captions available for this file"
            )

        # Find best subtitle stream (prefer specified language)
        stream_index = 0
        for i, stream in enumerate(streams):
            tags = stream.get("tags", {})
            stream_lang = tags.get("language", "")
            if stream_lang.lower().startswith(lang.lower()):
                stream_index = i
                break

        # Extract subtitle to temp file
        with tempfile.NamedTemporaryFile(suffix=".srt", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            extract_cmd = [
                "ffmpeg",
                "-y",
                "-i", str(input_path),
                "-map", f"0:s:{stream_index}",
                "-c:s", "srt",
                tmp_path,
            ]

            result = subprocess.run(extract_cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                return TranscriptResult(
                    success=False,
                    error="Failed to extract embedded subtitles"
                )

            raw_sub = Path(tmp_path).read_text(encoding="utf-8", errors="replace")
            text = SubtitleParser.to_plain_text(raw_sub)

            if not text.strip():
                return TranscriptResult(
                    success=False,
                    error="Transcript is empty"
                )

            # Save transcript
            output_path = save_transcript(text, input_path.name)

            return TranscriptResult(
                success=True,
                text=text,
                output_path=output_path,
                source_type="embedded",
                subtitle_type="embedded",
            )
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    except subprocess.TimeoutExpired:
        return TranscriptResult(
            success=False,
            error="Extraction timed out"
        )
    except json.JSONDecodeError:
        return TranscriptResult(
            success=False,
            error="No captions available for this file"
        )
    except Exception as e:
        logger.exception("Embedded subtitle extraction failed")
        return TranscriptResult(
            success=False,
            error=str(e)
        )


def save_transcript(text: str, source_name: str) -> Path:
    """Save transcript text to output directory.

    Args:
        text: The transcript text
        source_name: Original filename or URL for naming

    Returns:
        Path to saved transcript file
    """
    # Generate output filename from source
    if source_name.startswith(("http://", "https://")):
        # Extract video ID or use timestamp
        import re
        match = re.search(r"[?&]v=([^&]+)", source_name)
        if match:
            base_name = f"transcript_{match.group(1)}"
        else:
            from datetime import datetime
            base_name = f"transcript_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    else:
        # Use input filename stem
        base_name = f"transcript_{Path(source_name).stem}"

    output_path = OUTPUT_DIR / f"{base_name}.txt"

    # Avoid overwriting - add number suffix if needed
    counter = 1
    while output_path.exists():
        output_path = OUTPUT_DIR / f"{base_name}_{counter}.txt"
        counter += 1

    output_path.write_text(text, encoding="utf-8")
    logger.info(f"Saved transcript to {output_path}")

    return output_path
