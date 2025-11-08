import re


def parse_header(value: str):
    """Minimal replacement for the deprecated stdlib cgi.parse_header."""
    if value is None:
        return "", {}
    parts = [part.strip() for part in value.split(";")]
    if not parts:
        return "", {}
    key = parts[0]
    params = {}
    for segment in parts[1:]:
        if not segment:
            continue
        if "=" not in segment:
            params[segment.lower()] = ""
            continue
        name, val = segment.split("=", 1)
        name = name.strip().lower()
        val = val.strip().strip('"')
        params[name] = val
    return key, params
