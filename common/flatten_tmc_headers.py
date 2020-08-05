import pandas as pd


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
