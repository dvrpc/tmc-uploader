from random import randrange


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
