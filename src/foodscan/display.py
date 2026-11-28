"""Presentation helpers shared by the CLI and local web page."""
import re


# Keep in sync with ingredientItem in web_preview/template.html.
_TRAILING_PERCENT = re.compile(r"^(.*?)(?:\s+([0-9]+(?:\.[0-9]+)?)\s*%|\s*\(\s*([0-9]+(?:\.[0-9]+)?)\s*%\s*\))$")


def ingredient_display(item: str) -> tuple[str, str | None]:
    """Return the displayed name and an optional trailing percentage tag."""
    match = _TRAILING_PERCENT.fullmatch(item)
    if match:
        name = match[1].rstrip()
        if name and (name[-1].isalnum() or name[-1] in ")]}"):
            return name, f"({match[2] or match[3]}%)"
    return item, None
