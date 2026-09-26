def get_class_info(class_name: str):
    classes = {
        "paladin": {
            "hit_die": "d10",
            "primary_abilities": ["STR", "CHA"],
            "description": "A martial class with divine magic..."
        }
    }

    return classes.get(class_name.lower())