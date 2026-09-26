import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent / "data"


def _load_data():
    data = {}
    for path in DATA_DIR.glob("*.json"):
        name = path.stem.split(" ", 1)[-1].casefold()
        with path.open("r", encoding="utf-8") as data_file:
            data[name] = json.load(data_file)
    return data


DATA = _load_data()
CLASSES = DATA.get("classes", {})
SPECIES = DATA.get("races", {}).get("Races", {})
BACKGROUNDS = {}
FEATS = DATA.get("feats", {}).get("Feats", {})
SPELLS = DATA.get("spellcasting", {}).get("Spellcasting", {})
EQUIPMENT = DATA.get("equipment", {}).get("Equipment", {})
MECHANICS = DATA.get("mechanics", {})


def _normalize_name(name: str):
    return " ".join(name.strip().casefold().split())


def _find_named_entry(value, target: str):
    if isinstance(value, dict):
        for key, entry in value.items():
            if _normalize_name(key) == target:
                return entry
        for entry in value.values():
            result = _find_named_entry(entry, target)
            if result is not None:
                return result
    elif isinstance(value, list):
        for entry in value:
            result = _find_named_entry(entry, target)
            if result is not None:
                return result
    return None


def _find_table_entry(value, target: str):
    if isinstance(value, dict):
        table = value.get("table")
        if isinstance(table, dict):
            name_column = next(
                (
                    values
                    for column, values in table.items()
                    if _normalize_name(column) in {"name", "item"}
                    and isinstance(values, list)
                ),
                None,
            )
            if name_column is not None:
                for index, item_name in enumerate(name_column):
                    if isinstance(item_name, str) and _normalize_name(item_name) == target:
                        return {
                            column: values[index]
                            for column, values in table.items()
                            if isinstance(values, list) and index < len(values)
                        }
        for entry in value.values():
            result = _find_table_entry(entry, target)
            if result is not None:
                return result
    elif isinstance(value, list):
        for entry in value:
            result = _find_table_entry(entry, target)
            if result is not None:
                return result
    return None


def _get_info(catalog: dict, name: str):
    """Look up an entry by name, ignoring surrounding whitespace and case."""
    if not isinstance(name, str):
        return None
    target = _normalize_name(name)
    result = _find_named_entry(catalog, target)
    if result is not None:
        return result
    return _find_table_entry(catalog, target)


def get_class_info(class_name: str):
    """Get information about a D&D character class."""
    return _get_info(CLASSES, class_name)


def get_species_info(species_name: str):
    """Get information about a character species."""
    return _get_info(SPECIES, species_name)


def get_background_info(background_name: str):
    """Get information about a character background, if one is available."""
    return _get_info(BACKGROUNDS, background_name)


def get_feat_info(feat_name: str):
    """Get information about a feat."""
    return _get_info(FEATS, feat_name)


def get_spell_info(spell_name: str):
    """Get information about a spell."""
    return _get_info(SPELLS, spell_name)


def get_equipment_info(equipment_name: str):
    """Get information about equipment, including matching table entries."""
    return _get_info(EQUIPMENT, equipment_name)


def get_mechanics_info(topic_name: str):
    """Get information about a game mechanics topic."""
    return _get_info(MECHANICS, topic_name)


def get_spellcasting_info(topic_name: str):
    """Get information about a spellcasting rules topic."""
    return _get_info(SPELLS, topic_name)