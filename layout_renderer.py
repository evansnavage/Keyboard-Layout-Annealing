import json

highlights = [
    "e",
    "t",
    "a",
    "o",
    "i",
    "n",
    "s",
    "h",
]  # the 8 most common letters in english

with open("best_annealed_layout.json", "r") as f:
    keyboard_layout_json = f.read()

keyboard_layout = json.loads(keyboard_layout_json)


def render_keyboard(layout):
    """Renders a json defined keyboard to text, highlights the 8 most common english letters"""
    for row in layout["layout"]:
        line = ""
        for key in row:
            width = key.get("width", 1)
            label = key.get("base", key.get("name", " "))
            if key.get("shift", ""):
                label += " " + key["shift"]
            if "base" in key and key["base"] in highlights:
                line += f"\033[91m[{label:^{width * 3}}]\033[0m"
            else:
                line += f"[{label:^{width * 3}}]"
        print(line)


# render_keyboard(keyboard_layout)
