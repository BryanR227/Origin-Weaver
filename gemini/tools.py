CLASSES = {
    "paladin": {
        "hit_die": "d10",
        "primary_abilities": ["STR", "CHA"],
        "saving_throws": ["WIS", "CHA"],
        "armor_proficiencies": ["light armor", "medium armor", "heavy armor", "shields"],
        "weapon_proficiencies": ["simple weapons", "martial weapons"],
        "spellcasting": True,
        "description": "A martial class empowered by divine magic.",
    },
    "artificer": {
        "hit_die": "d8",
        "primary_abilities": ["CON", "INT"],
        "saving_throws": ["CON", "INT"],
        "armor_proficiencies": ["light armor", "medium armor", "shields"],
        "weapon_proficiencies": ["simple weapons"],
        "spellcasting": True,
        "description": "A magical inventor who infuses objects and crafts useful tools.",
    },
    "barbarian": {
        "hit_die": "d12",
        "primary_abilities": ["STR", "CON"],
        "saving_throws": ["STR", "CON"],
        "armor_proficiencies": ["light armor", "medium armor", "shields"],
        "weapon_proficiencies": ["simple weapons", "martial weapons"],
        "spellcasting": False,
        "description": "A durable warrior who channels rage to become more dangerous in combat.",
    },
    "bard": {
        "hit_die": "d8",
        "primary_abilities": ["DEX", "CHA"],
        "saving_throws": ["DEX", "CHA"],
        "armor_proficiencies": ["light armor"],
        "weapon_proficiencies": ["simple weapons", "hand crossbows", "longswords", "rapiers", "shortswords"],
        "spellcasting": True,
        "description": "A versatile performer whose magic and talents inspire allies and hinder foes.",
    },
    "bloodhunter": {
        "hit_die": "d10",
        "primary_abilities": ["DEX", "INT"],
        "saving_throws": ["DEX", "INT"],
        "armor_proficiencies": ["light armor", "medium armor", "shields"],
        "weapon_proficiencies": ["simple weapons", "martial weapons"],
        "spellcasting": False,
        "description": "A homebrew warrior who uses occult rites and their own vitality to hunt threats.",
    },
    "cleric": {
        "hit_die": "d8",
        "primary_abilities": ["WIS", "CHA"],
        "saving_throws": ["WIS", "CHA"],
        "armor_proficiencies": ["light armor", "medium armor", "shields"],
        "weapon_proficiencies": ["simple weapons"],
        "spellcasting": True,
        "description": "A divine spellcaster who draws power from a deity to protect and support others.",
    },
    "druid": {
        "hit_die": "d8",
        "primary_abilities": ["INT", "WIS"],
        "saving_throws": ["INT", "WIS"],
        "armor_proficiencies": ["light armor", "medium armor", "shields (nonmetal)"],
        "weapon_proficiencies": ["clubs", "daggers", "darts", "javelins", "maces", "quarterstaffs", "scimitars", "sickles", "slings", "spears"],
        "spellcasting": True,
        "description": "A nature-focused spellcaster who draws on the forces of the natural world.",
    },
    "fighter": {
        "hit_die": "d10",
        "primary_abilities": ["STR", "CON"],
        "saving_throws": ["STR", "CON"],
        "armor_proficiencies": ["light armor", "medium armor", "heavy armor", "shields"],
        "weapon_proficiencies": ["simple weapons", "martial weapons"],
        "spellcasting": False,
        "description": "A highly trained combatant who can master a wide range of weapons and tactics.",
    },
    "monk": {
        "hit_die": "d8",
        "primary_abilities": ["STR", "DEX"],
        "saving_throws": ["STR", "DEX"],
        "armor_proficiencies": [],
        "weapon_proficiencies": ["simple weapons", "shortswords"],
        "spellcasting": False,
        "description": "A disciplined martial artist who fights with speed, focus, and unarmed techniques.",
    },
    "ranger": {
        "hit_die": "d10",
        "primary_abilities": ["STR", "DEX"],
        "saving_throws": ["STR", "DEX"],
        "armor_proficiencies": ["light armor", "medium armor", "shields"],
        "weapon_proficiencies": ["simple weapons", "martial weapons"],
        "spellcasting": True,
        "description": "A skilled hunter who combines wilderness expertise, weapons, and nature magic.",
    },
    "rogue": {
        "hit_die": "d8",
        "primary_abilities": ["DEX", "INT"],
        "saving_throws": ["DEX", "INT"],
        "armor_proficiencies": ["light armor"],
        "weapon_proficiencies": ["simple weapons", "hand crossbows", "longswords", "rapiers", "shortswords"],
        "spellcasting": False,
        "description": "A resourceful specialist who relies on stealth, precision, and skill.",
    },
    "sorcerer": {
        "hit_die": "d6",
        "primary_abilities": ["CON", "CHA"],
        "saving_throws": ["CON", "CHA"],
        "armor_proficiencies": [],
        "weapon_proficiencies": ["daggers", "darts", "slings", "quarterstaffs", "light crossbows"],
        "spellcasting": True,
        "description": "A spellcaster whose innate magical power comes from an unusual source or lineage.",
    },
    "warlock": {
        "hit_die": "d8",
        "primary_abilities": ["WIS", "CHA"],
        "saving_throws": ["WIS", "CHA"],
        "armor_proficiencies": ["light armor"],
        "weapon_proficiencies": ["simple weapons"],
        "spellcasting": True,
        "description": "A spellcaster who gains magical abilities through a pact with a powerful patron.",
    },
    "wizard": {
        "hit_die": "d6",
        "primary_abilities": ["INT", "WIS"],
        "saving_throws": ["INT", "WIS"],
        "armor_proficiencies": [],
        "weapon_proficiencies": ["daggers", "darts", "slings", "quarterstaffs", "light crossbows"],
        "spellcasting": True,
        "description": "A scholar of magic who learns and prepares spells through study and experimentation.",
    },
}

SPECIES = {
    "dwarf": {
        "size": "Medium",
        "speed": 25,
        "traits": ["Darkvision", "Dwarven Resilience", "Stonecunning"],
        "description": "A sturdy people known for resilience, craftsmanship, and strong community ties.",
    },
    "elf": {
        "size": "Medium",
        "speed": 30,
        "traits": ["Darkvision", "Keen Senses", "Fey Ancestry", "Trance"],
        "description": "A long-lived people with keen senses and a deep connection to magic and nature.",
    },
    "halfling": {
        "size": "Small",
        "speed": 25,
        "traits": ["Lucky", "Brave", "Halfling Nimbleness"],
        "description": "A small, nimble people known for courage, luck, and close-knit communities.",
    },
    "human": {
        "size": "Medium",
        "speed": 30,
        "traits": ["Versatile"],
        "description": "An adaptable people found in a wide variety of cultures and ways of life.",
    },
}

BACKGROUNDS = {
    "acolyte": {
        "skill_proficiencies": ["Insight", "Religion"],
        "tool_proficiencies": [],
        "description": "A person who served in a temple and studied its rites and teachings.",
    },
    "criminal": {
        "skill_proficiencies": ["Deception", "Stealth"],
        "tool_proficiencies": ["one type of gaming set", "thieves' tools"],
        "description": "A practiced operator with a history in crime or the underworld.",
    },
    "sage": {
        "skill_proficiencies": ["Arcana", "History"],
        "tool_proficiencies": [],
        "description": "A researcher whose life has been devoted to learning and uncovering lore.",
    },
    "soldier": {
        "skill_proficiencies": ["Athletics", "Intimidation"],
        "tool_proficiencies": ["one type of gaming set", "vehicles (land)"],
        "description": "A trained veteran shaped by military service and life among other soldiers.",
    },
}

FEATS = {
    "alert": {
        "prerequisite": None,
        "benefits": ["Gain a +5 bonus to initiative", "Cannot be surprised while conscious"],
        "description": "A feat for characters who are exceptionally quick to notice danger.",
    },
    "lucky": {
        "prerequisite": None,
        "benefits": ["Gain luck points to reroll an attack roll, ability check, or saving throw"],
        "description": "A feat representing extraordinary luck at critical moments.",
    },
    "war caster": {
        "prerequisite": "Ability to cast at least one spell",
        "benefits": ["Advantage on concentration saves", "Cast a spell for certain opportunity attacks"],
        "description": "A feat for maintaining and using spells amid the chaos of combat.",
    },
}

SPELLS = {
    "cure wounds": {
        "level": 1,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "Touch",
        "description": "A creature you touch regains hit points based on the spell slot used.",
    },
    "fireball": {
        "level": 3,
        "school": "Evocation",
        "casting_time": "1 action",
        "range": "150 feet",
        "description": "A burst of flame damages creatures in a designated area.",
    },
    "guidance": {
        "level": 0,
        "school": "Divination",
        "casting_time": "1 action",
        "range": "Touch",
        "description": "The target gains a small bonus to one ability check before the spell ends.",
    },
    "mage armor": {
        "level": 1,
        "school": "Abjuration",
        "casting_time": "1 action",
        "range": "Touch",
        "description": "A willing unarmored creature gains a magical defensive ward.",
    },
}

EQUIPMENT = {
    "dagger": {
        "category": "weapon",
        "cost": "2 gp",
        "weight": "1 lb.",
        "properties": ["finesse", "light", "thrown (range 20/60)"],
        "description": "A light blade suitable for close combat or throwing.",
    },
    "longsword": {
        "category": "weapon",
        "cost": "15 gp",
        "weight": "3 lb.",
        "properties": ["versatile (1d10)"],
        "description": "A martial blade that can be wielded with one hand or two.",
    },
    "chain mail": {
        "category": "armor",
        "cost": "75 gp",
        "weight": "55 lb.",
        "armor_class": 16,
        "stealth_disadvantage": True,
        "description": "Heavy armor made from interlocking metal rings.",
    },
    "shield": {
        "category": "armor",
        "cost": "10 gp",
        "weight": "6 lb.",
        "armor_class_bonus": 2,
        "description": "A hand-held shield that improves its wielder's defense.",
    },
}


def _get_info(catalog: dict, name: str):
    """Look up a catalog entry by name, ignoring surrounding whitespace and case."""
    return catalog.get(name.strip().lower())


def get_class_info(class_name: str):
    """
    Get information about a D&D character class.

    Args:
        class_name: The name of the D&D class to look up.

    Returns:
        Information about the class, or None if the class does not exist.
    """
    return _get_info(CLASSES, class_name)


def get_species_info(species_name: str):
    """Get information about a character species, or None if it is unknown."""
    return _get_info(SPECIES, species_name)


def get_background_info(background_name: str):
    """Get information about a character background, or None if it is unknown."""
    return _get_info(BACKGROUNDS, background_name)


def get_feat_info(feat_name: str):
    """Get information about a feat, or None if it is unknown."""
    return _get_info(FEATS, feat_name)


def get_spell_info(spell_name: str):
    """Get information about a spell, or None if it is unknown."""
    return _get_info(SPELLS, spell_name)


def get_equipment_info(equipment_name: str):
    """Get information about equipment, or None if it is unknown."""
    return _get_info(EQUIPMENT, equipment_name)

