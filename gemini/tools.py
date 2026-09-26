CLASSES = {
    "paladin": {
        "hit_die": "d10",
        "primary_abilities": ["STR", "CHA"],
        "description": "A martial class with divine magic..."
    },
    "artificer":{
        "hit_die": "d8",
        "primary_abilities": ["CON", "INT"],
        "description": "A half-casting class that invents with magic..."
    },
    "barbarian":{
        "hit_die": "d12",
        "primary_abilities": ["STR", "CON"],
        "description": "A martial class that utilizes rage to increase their combat ability..."
    },
    "bard":{
        "hit_die": "d8",
        "primary_abilities": ["DEX", "CHA"],
        "description": "A spell casting class that is more uspport heavy, uses songs to cast spells..."
    },
    "bloodhunter":{
        "hit_die": "d10",
        "primary_abilities": ["DEX", "INT"],
        "description": "A half casting class that has magic powered by blood magic..."
    },
    "cleric":{
        "hit_die": "d8",
        "primary_abilities": ["WIS", "CHA"],
        "description": "A spell casting class that is more support oriented, relies on holy magic is capable of more..."
        
    },
    "druid":{
        "hit_die": "d8",
        "primary_abilities": ["INT", "WIS"],
        "description": "A spell caster that is multi variable, that is more focused on nature magic..."
    },
    "fighter":{
        "hit_die": "d10",
        "primary_abilities": ["STR", "CON"],
        "description": "A martial class more focused on being a front liner tank class..."
    },
    "monk": {
        "hit_die": "d8",
        "primary_abilities": ["STR", "DEX"],
        "description": "A martial class more focused on speed and martial arts attacking, using WIS..."
        
    },
    "ranger":{
        "hit_die": "d10",
        "primary_abilities": ["STR", "DEX"],
        "description": "A half-caster that uses both wild magic as well as ranged weaponry to fight..."
    },
    "rogue":{
        "hit_die": "d8",
        "primary_abilities": ["DEX", "INT"],
        "description": "They are a martial class that is more technical, focusing on sneaking and stealth..."
    },
    "sorcerer":{
        "hit_die": "d6",
        "primary_abilities": ["CON", "CHA"],
        "description": "This class is more focused on spell casting, with magic more focused on magic based on blood..."
        
    },
    "warlock":{
        "hit_die": "d8",
        "primary_abilities": ["WIS", "CHA"],
        "description": "This class is more focused on spell casting by making pacts with elder gods and more evil deities..."
        
    },
    "wizard":{
        "hit_die": "d6",
        "primary_abilities": ["INT", "WIS"],
        "description": "This class is a spellcaster more focused on spell casting through knowledge you have gathered..."
    }
}

def get_class_info(class_name: str):
    """
    Get information about a D&D character class.

    Args:
        class_name: The name of the D&D class to look up.

    Returns:
        Information about the class, or None if the class does not exist.
    """
    return CLASSES.get(class_name.lower())

