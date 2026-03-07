# Name: Confictura ClassicAssist API Scope Shim
# Description: Binds ClassicAssist macro commands from the main macro scope into imported modules.
# Author: ChatGPT Codex
# Shard: Confictura

_KNOWN_CA_COMMANDS = [
    "Pause",
    "Stop",
    "Name",
    "WarMode",
    "Msg",
    "SetAlias",
    "GetAlias",
    "FindAlias",
    "FindType",
    "CountType",
    "MoveType",
    "WaitForTarget",
    "Target",
    "TargetByResource",
    "TargetTileOffset",
    "UseSkill",
    "UseObject",
    "UseType",
    "ClickObject",
    "ContextMenu",
    "WaitForContext",
    "WaitForGump",
    "GumpExists",
    "ReplyGump",
    "InGump",
    "WaitForJournal",
    "ClearJournal",
    "Dead",
    "MaxWeight",
    "Weight",
    "Pathfind",
    "Distance",
    "GetFriend",
    "GetEnemy",
    "IgnoreObject",
    "ClearIgnoreList",
    "ClearObjectQueue",
    "CancelTarget",
    "WaitForProperties",
    "Graphic",
    "Hue",
    "X",
    "Y",
    "Z",
    "Hits",
    "MaxHits",
    "Mana",
    "MaxMana",
    "Stam",
    "MaxStam",
    "Map",
    "War",
    "Hidden",
    "Poisoned",
    "Paralyzed",
    "Invulnerable",
    "Ally",
    "Innocent",
    "Gray",
    "Criminal",
    "Murderer",
    "Enemy",
    "Property",
    "InRegion"
]


def _resolve_name_from_namespace(namespace, name):
    if isinstance(namespace, dict) and name in namespace:
        return (True, namespace[name])

    if isinstance(namespace, dict):
        try:
            return (True, eval(name, namespace))
        except Exception:
            pass

    return (False, None)


def publish_known_ca_api(namespace):
    bound_count = 0

    try:
        import __builtin__
    except Exception:
        __builtin__ = None

    if __builtin__ is None:
        return bound_count

    try:
        target_namespace = __builtin__.__dict__
    except Exception:
        return bound_count

    for name in _KNOWN_CA_COMMANDS:
        found, value = _resolve_name_from_namespace(namespace, name)
        if not found:
            continue

        try:
            target_namespace[name] = value
            bound_count += 1
        except Exception:
            continue

    return bound_count


def _bind_from_module(namespace, module_obj):
    if module_obj is None:
        return

    try:
        module_names = dir(module_obj)
    except Exception:
        return

    for name in module_names:
        if name.startswith("__"):
            continue
        if name in namespace:
            continue

        try:
            value = getattr(module_obj, name)
        except Exception:
            continue

        try:
            if len(name) > 0 and name[0].isupper():
                namespace[name] = value
        except Exception:
            continue


def bind_ca_api(namespace):
    if namespace is None:
        return

    publish_known_ca_api(namespace)

    try:
        import __main__
    except Exception:
        __main__ = None

    _bind_from_module(namespace, __main__)

    try:
        import __builtin__
    except Exception:
        __builtin__ = None

    _bind_from_module(namespace, __builtin__)
