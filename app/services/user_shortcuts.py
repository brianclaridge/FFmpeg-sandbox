"""User presets service - manages user-created filter presets."""

import re
from pathlib import Path
from typing import Any

import yaml
from loguru import logger
from pydantic import ValidationError

from app.config import DATA_DIR
from app.services.presets import CONFIG_CLASSES


USER_PRESETS_FILE = DATA_DIR / "user-presets.yml"


def load_user_shortcuts() -> dict[str, dict[str, dict[str, Any]]]:
    """Load user presets from YAML file.

    Returns:
        Dictionary with validated user presets organized by filter_type/category
        Returns empty structure if file doesn't exist
    """
    if not USER_PRESETS_FILE.exists():
        logger.debug("User presets file does not exist yet")
        return {"audio": {}, "video": {}}

    logger.debug(f"Loading user presets from {USER_PRESETS_FILE}")

    with open(USER_PRESETS_FILE, "r") as f:
        raw_data = yaml.safe_load(f) or {}

    validated_presets = {"audio": {}, "video": {}}

    # Validate audio presets
    for category, config_class in CONFIG_CLASSES.get("audio", {}).items():
        if category not in raw_data.get("audio", {}):
            validated_presets["audio"][category] = {}
            continue

        category_presets = {}
        for preset_key, preset_data in raw_data["audio"][category].items():
            try:
                # Ensure user preset flags are set
                preset_data["is_user_shortcut"] = True
                preset_data.setdefault("preset_category", "Custom")
                validated = config_class(**preset_data)
                category_presets[preset_key] = validated
            except ValidationError as e:
                logger.warning(f"Invalid user preset audio/{category}/{preset_key}: {e}")
                continue  # Skip invalid presets, don't fail

        validated_presets["audio"][category] = category_presets

    # Validate video presets
    for category, config_class in CONFIG_CLASSES.get("video", {}).items():
        if category not in raw_data.get("video", {}):
            validated_presets["video"][category] = {}
            continue

        category_presets = {}
        for preset_key, preset_data in raw_data["video"][category].items():
            try:
                preset_data["is_user_shortcut"] = True
                preset_data.setdefault("preset_category", "Custom")
                validated = config_class(**preset_data)
                category_presets[preset_key] = validated
            except ValidationError as e:
                logger.warning(f"Invalid user preset video/{category}/{preset_key}: {e}")
                continue

        validated_presets["video"][category] = category_presets

    total = sum(
        len(presets)
        for group in validated_presets.values()
        for presets in group.values()
    )
    if total > 0:
        logger.info(f"Loaded {total} user presets from {USER_PRESETS_FILE}")

    return validated_presets


def _save_user_shortcuts_file(data: dict) -> None:
    """Write user presets to YAML file."""
    USER_PRESETS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(USER_PRESETS_FILE, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)
    logger.debug(f"Saved user presets to {USER_PRESETS_FILE}")


def _load_raw_user_presets() -> dict:
    """Load raw YAML data without validation."""
    if not USER_PRESETS_FILE.exists():
        return {"audio": {}, "video": {}}
    with open(USER_PRESETS_FILE, "r") as f:
        return yaml.safe_load(f) or {"audio": {}, "video": {}}


def generate_shortcut_key(name: str) -> str:
    """Generate URL-safe preset key from display name.

    Args:
        name: Human-readable preset name (e.g., "My Podcast Volume")

    Returns:
        URL-safe key (e.g., "my_podcast_volume")
    """
    # Convert to lowercase
    key = name.lower()
    # Replace spaces and special chars with underscore
    key = re.sub(r"[^a-z0-9]+", "_", key)
    # Remove leading/trailing underscores
    key = key.strip("_")
    # Ensure not empty
    return key or "preset"


def save_user_shortcut(
    filter_type: str,
    filter_category: str,
    preset_key: str,
    preset_data: dict,
) -> bool:
    """Save a new user preset.

    Args:
        filter_type: "audio" or "video"
        filter_category: Category name (e.g., "volume", "brightness")
        preset_key: Unique key for the preset
        preset_data: Preset configuration data

    Returns:
        True if saved successfully, False otherwise
    """
    if filter_type not in ("audio", "video"):
        logger.error(f"Invalid filter_type: {filter_type}")
        return False

    if filter_category not in CONFIG_CLASSES.get(filter_type, {}):
        logger.error(f"Invalid filter_category: {filter_category}")
        return False

    # Validate against Pydantic model
    config_class = CONFIG_CLASSES[filter_type][filter_category]
    try:
        preset_data["is_user_shortcut"] = True
        preset_data.setdefault("preset_category", "Custom")
        validated = config_class(**preset_data)
    except ValidationError as e:
        logger.error(f"Invalid preset data: {e}")
        return False

    # Load existing, add new, save
    raw_data = _load_raw_user_presets()

    if filter_type not in raw_data:
        raw_data[filter_type] = {}
    if filter_category not in raw_data[filter_type]:
        raw_data[filter_type][filter_category] = {}

    # Convert validated model to dict for YAML
    raw_data[filter_type][filter_category][preset_key] = validated.model_dump()

    _save_user_shortcuts_file(raw_data)
    logger.info(f"Saved user preset: {filter_type}/{filter_category}/{preset_key}")
    return True


def delete_user_shortcut(
    filter_type: str,
    filter_category: str,
    preset_key: str,
) -> bool:
    """Delete a user preset.

    Args:
        filter_type: "audio" or "video"
        filter_category: Category name
        preset_key: Key of preset to delete

    Returns:
        True if deleted, False if not found or error
    """
    raw_data = _load_raw_user_presets()

    try:
        del raw_data[filter_type][filter_category][preset_key]
        _save_user_shortcuts_file(raw_data)
        logger.info(f"Deleted user preset: {filter_type}/{filter_category}/{preset_key}")
        return True
    except KeyError:
        logger.warning(f"Preset not found: {filter_type}/{filter_category}/{preset_key}")
        return False


def update_user_shortcut(
    filter_type: str,
    filter_category: str,
    preset_key: str,
    preset_data: dict,
) -> bool:
    """Update an existing user preset.

    Args:
        filter_type: "audio" or "video"
        filter_category: Category name
        preset_key: Key of preset to update
        preset_data: New configuration data

    Returns:
        True if updated, False if error
    """
    raw_data = _load_raw_user_presets()

    # Check preset exists
    if preset_key not in raw_data.get(filter_type, {}).get(filter_category, {}):
        logger.warning(f"Preset not found for update: {filter_type}/{filter_category}/{preset_key}")
        return False

    # Validate and save (same as save)
    return save_user_shortcut(filter_type, filter_category, preset_key, preset_data)


def export_shortcuts(
    filter_type: str | None = None,
    filter_category: str | None = None,
    include_system: bool = False,
) -> str:
    """Export presets as YAML string.

    Args:
        filter_type: Optional filter by "audio" or "video"
        filter_category: Optional filter by category (requires filter_type)
        include_system: If True, include system presets from presets.yml

    Returns:
        YAML string of presets
    """
    from app.services.presets import get_presets

    if include_system:
        all_presets = get_presets()
    else:
        all_presets = load_user_shortcuts()

    export_data = {}

    if filter_type:
        if filter_category:
            # Export single category
            category_data = all_presets.get(filter_type, {}).get(filter_category, {})
            export_data = {
                filter_type: {
                    filter_category: {
                        k: v.model_dump() if hasattr(v, "model_dump") else v
                        for k, v in category_data.items()
                    }
                }
            }
        else:
            # Export all categories for filter_type
            type_data = all_presets.get(filter_type, {})
            export_data = {
                filter_type: {
                    cat: {
                        k: v.model_dump() if hasattr(v, "model_dump") else v
                        for k, v in presets.items()
                    }
                    for cat, presets in type_data.items()
                }
            }
    else:
        # Export everything
        export_data = {
            ft: {
                cat: {
                    k: v.model_dump() if hasattr(v, "model_dump") else v
                    for k, v in presets.items()
                }
                for cat, presets in categories.items()
            }
            for ft, categories in all_presets.items()
        }

    return yaml.dump(export_data, default_flow_style=False, sort_keys=False)


def import_shortcuts(yaml_content: str, merge: bool = True) -> dict:
    """Import presets from YAML string.

    Args:
        yaml_content: YAML string containing presets
        merge: If True, merge with existing; if False, replace all

    Returns:
        Dict with 'added', 'updated', 'skipped', 'errors' counts
    """
    result = {"added": 0, "updated": 0, "skipped": 0, "errors": []}

    try:
        import_data = yaml.safe_load(yaml_content)
    except yaml.YAMLError as e:
        result["errors"].append(f"Invalid YAML: {e}")
        return result

    if not import_data:
        result["errors"].append("Empty or invalid preset data")
        return result

    if merge:
        existing = _load_raw_user_presets()
    else:
        existing = {"audio": {}, "video": {}}

    for filter_type in ("audio", "video"):
        if filter_type not in import_data:
            continue

        if filter_type not in existing:
            existing[filter_type] = {}

        for category, presets in import_data[filter_type].items():
            if category not in CONFIG_CLASSES.get(filter_type, {}):
                result["errors"].append(f"Unknown category: {filter_type}/{category}")
                continue

            if category not in existing[filter_type]:
                existing[filter_type][category] = {}

            config_class = CONFIG_CLASSES[filter_type][category]

            for preset_key, preset_data in presets.items():
                try:
                    # Force user preset flags
                    preset_data["is_user_shortcut"] = True
                    preset_data.setdefault("preset_category", "Custom")
                    validated = config_class(**preset_data)

                    is_update = preset_key in existing[filter_type][category]
                    existing[filter_type][category][preset_key] = validated.model_dump()

                    if is_update:
                        result["updated"] += 1
                    else:
                        result["added"] += 1

                except ValidationError as e:
                    result["errors"].append(f"{filter_type}/{category}/{preset_key}: {e}")
                    result["skipped"] += 1

    _save_user_shortcuts_file(existing)
    logger.info(f"Imported presets: {result['added']} added, {result['updated']} updated, {result['skipped']} skipped")

    return result
