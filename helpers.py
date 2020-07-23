from random import randrange
import pandas as pd


def make_random_gradient(style: str = "random") -> str:

    def _make_random_rgba():
        v1 = randrange(255)
        v2 = randrange(255)
        v3 = randrange(255)

        return f"rgba({v1},{v2},{v3},X)"

    def _gradient(color: str) -> str:
        color1 = color.replace("X", "0.8")
        color2 = color.replace("X", "0")
        return f"{color1}, {color2}"

    # For now, just use random colors
    if style == "default":
        color1 = "rgba(255,0,0,X)"
        color2 = "rgba(0,255,0,X)"
        color3 = "rgba(0,0,255,X)"

    elif style == "random":
        color1 = _make_random_rgba()
        color2 = _make_random_rgba()
        color3 = _make_random_rgba()

    rot1 = randrange(360)
    rot2 = randrange(360)
    rot3 = randrange(360)

    text = f"""
background: linear-gradient({rot1}deg, {_gradient(color1)} 70.71%),
                           linear-gradient({rot2}deg, {_gradient(color2)} 70.71%),
                           linear-gradient({rot3}deg, {_gradient(color3)} 70.71%);
    """

    return text


def flatten_headers(input_file,
                    tabname: str) -> list:
    """
    Transform a multi-level header into a single header row.

    For example:
        - 'Southbound / U Turns' becomes 'SB U'
        - 'Eastbound / Straight Through' becomes 'EB Thru'
    """

    replacements_level_1 = {
        "southbound": "SB",
        "westbound": "WB",
        "northbound": "NB",
        "eastbound": "EB",
        "northeastbound": "NEB",
        "southeastbound": "SEB",
        "southwestbound": "SWB",
        "northwestbound": "NWB",
    }

    replacements_level_2 = {
        "u turns": "U",
        "left turns": "Left",
        "straight through": "Thru",
        "right turns": "Right",
        "peds in crosswalk": "Peds Xwalk",
        "bikes in crosswalk": "Bikes Xwalk",
        "time": "time",

        # handle the expected typos!
        "bikes in croswalk": "Bikes Xwalk",
        "peds in croswalk": "Peds Xwalk",
    }

    df = pd.read_excel(input_file,
                       nrows=3,
                       header=None,
                       sheet_name=tabname)

    headers = []

    # Start off with a blank l1
    l1 = ""

    for col in df.columns:
        level_1 = df.at[1, col]
        level_2 = df.at[2, col]

        # Update the l1 anytime a value is found
        if not pd.isna(level_1):
            if level_1.lower() not in replacements_level_1:
                l1 = level_1.lower().replace(" ", "")
                # msg = f"!!! '{level_1}' isn't included in the level 1 lookup. It won't be renamed."
                # print(msg)
            else:
                l1 = replacements_level_1[level_1.lower()]

        # Warn the user if the file has unexpected headers!
        # If it does, use the raw value instead of our nicely formatted one
        if level_2.lower() in replacements_level_2:
            l2 = replacements_level_2[level_2.lower()]
        else:
            # msg = f"!!! '{level_2}' isn't included in the level 2 lookup. It won't be renamed."
            # print(msg)
            l2 = level_2.lower().replace(" ", "")

        if l2 == "time":
            headers.append(l2)
        else:   
            headers.append(l1 + " " + l2)

    return headers