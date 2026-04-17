

LEVELS = [
    {"name": "YSA Apprenticeship", "min_points": 0, "multiplier": 1.0},
    {"name": "Explorer", "min_points": 100, "multiplier": 1.0},
    {"name": "Ambassador-in-Training", "min_points": 400, "multiplier": 1.5},
    {"name": "Ambassador", "min_points": 600, "multiplier": 2.0},
]

def get_user_level(total_points):
    current_level = LEVELS[0]
    for level in LEVELS:
        if total_points >= level["min_points"]:
            current_level = level
        else:
            break
    return current_level

def points_to_next_level(current_points):
    if current_points < 100:
        return 100 - current_points, "Explorer"
    elif current_points < 400:
        return 400 - current_points, "Ambassador-in-Training"
    elif current_points < 600:
        return 600 - current_points, "Ambassador"
    else:
        return 0, "Ambassador"
