# Name: Confictura Gump Id Utilities
# Description: Resolves gump ids from explicit values or server type names using legacy .NET hash behavior.
# Author: ChatGPT Codex
# Shard: Confictura

KNOWN_GUMP_TYPES = {
    "WELCOME": "Server.Gumps.WelcomeGump",
    "GYPSY_TAROT": "Server.Gumps.GypsyTarotGump",
    "RACE_POTIONS": "Server.Items.RacePotions+RacePotionsGump",
    "PKNONPK": "Server.Gumps.PKNONPK",
    "NAME_ALTER": "Server.Gumps.NameAlterGump",
    "NAME_CHANGE": "Server.Gumps.NameChangeGump"
}


def _to_uint32(value):
    try:
        return int(value) & 0xFFFFFFFF
    except Exception:
        return 0


def _to_text(value):
    if value is None:
        return ""
    try:
        return unicode(value)
    except Exception:
        try:
            return str(value)
        except Exception:
            return ""


def dotnet_legacy_string_hash(text_value):
    """
    ServUO/RunUO commonly uses GetType().FullName.GetHashCode() for gump IDs.
    This reproduces the legacy .NET string hash algorithm.
    """
    text = _to_text(text_value)
    if text == "":
        return 0

    hash1 = 5381
    hash2 = hash1

    index_value = 0
    text_length = len(text)
    while index_value < text_length:
        hash1 = (((hash1 << 5) + hash1) ^ ord(text[index_value])) & 0xFFFFFFFF
        index_value += 1
        if index_value >= text_length:
            break
        hash2 = (((hash2 << 5) + hash2) ^ ord(text[index_value])) & 0xFFFFFFFF
        index_value += 1

    return (hash1 + (hash2 * 1566083941)) & 0xFFFFFFFF


def resolve_named_type(gump_key, known_gump_types=None):
    if known_gump_types is None:
        known_gump_types = KNOWN_GUMP_TYPES

    if gump_key is None:
        return ""

    key_text = _to_text(gump_key).strip().upper()
    if key_text == "":
        return ""

    return known_gump_types.get(key_text, "")


def resolve_gump_id(
    rule_or_spec,
    gump_id_overrides=None,
    known_gump_types=None
):
    if known_gump_types is None:
        known_gump_types = KNOWN_GUMP_TYPES

    if gump_id_overrides is None:
        gump_id_overrides = {}

    if isinstance(rule_or_spec, int) or isinstance(rule_or_spec, long):
        return _to_uint32(rule_or_spec)

    if isinstance(rule_or_spec, str) or isinstance(rule_or_spec, unicode):
        text_value = _to_text(rule_or_spec).strip()
        if text_value == "":
            return 0

        # Hex literal input (example: "0x54F555DF")
        if text_value.lower().startswith("0x"):
            try:
                return int(text_value, 16) & 0xFFFFFFFF
            except Exception:
                return 0

        # Treat bare text as gump type name.
        override_value = gump_id_overrides.get(text_value)
        if override_value is not None:
            return _to_uint32(override_value)
        return dotnet_legacy_string_hash(text_value)

    if not isinstance(rule_or_spec, dict):
        return 0

    explicit = rule_or_spec.get("gump_id")
    if explicit not in (None, 0, "", "0x0"):
        return _to_uint32(explicit)

    gump_key = rule_or_spec.get("gump_key", "")
    gump_type = rule_or_spec.get("gump_type", "")

    if gump_key != "":
        key_name = _to_text(gump_key).strip().upper()
        if key_name in gump_id_overrides:
            return _to_uint32(gump_id_overrides[key_name])

        named_type = resolve_named_type(key_name, known_gump_types)
        if named_type != "":
            if named_type in gump_id_overrides:
                return _to_uint32(gump_id_overrides[named_type])
            return dotnet_legacy_string_hash(named_type)

    if gump_type != "":
        type_text = _to_text(gump_type).strip()
        if type_text in gump_id_overrides:
            return _to_uint32(gump_id_overrides[type_text])
        return dotnet_legacy_string_hash(type_text)

    return 0


def gump_hex(gump_id):
    return "0x{0:08X}".format(_to_uint32(gump_id))