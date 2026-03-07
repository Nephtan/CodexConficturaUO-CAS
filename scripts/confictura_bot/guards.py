# Name: Confictura FSM Guard Utilities
# Description: Provides reusable precondition checks for safe non-blocking FSM execution.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


def guard_player_alive(ctx, state_name):
    if Dead("self"):
        ctx.fail(state_name, "Player is dead")
        return False
    return True


def guard_weight_ok(ctx, state_name):
    inventory_cfg = ctx.config.get("inventory", {})
    max_ratio = inventory_cfg.get("max_weight_ratio", 0.9)

    max_weight = MaxWeight()
    current_weight = Weight()

    if max_weight <= 0:
        ctx.fail(state_name, "MaxWeight returned invalid value", {"max_weight": max_weight})
        return False

    ratio = float(current_weight) / float(max_weight)
    Telemetry.debug(state_name, "Weight check", {
        "current_weight": current_weight,
        "max_weight": max_weight,
        "ratio": "{0:.2f}".format(ratio),
        "threshold": max_ratio
    })

    if ratio >= max_ratio:
        ctx.fail(state_name, "Weight threshold reached", {
            "ratio": "{0:.2f}".format(ratio),
            "threshold": max_ratio
        })
        return False
    return True


def guard_alias_available(ctx, state_name, alias_name, allow_builtins=True):
    if allow_builtins and alias_name in ("self", "last", "backpack", "bank"):
        return True

    aliases_cfg = ctx.config.get("aliases", {})
    if alias_name in aliases_cfg:
        mapped = aliases_cfg[alias_name].get("value")
        if allow_builtins and mapped in ("self", "last", "backpack", "bank"):
            return True

    if FindAlias(alias_name):
        return True

    try:
        alias_serial = GetAlias(alias_name)
        if alias_serial not in (None, 0):
            return True
    except Exception:
        pass

    ctx.fail(state_name, "Alias is missing", {"alias": alias_name})
    return False


def guard_item_exists(ctx, state_name, graphic, container_alias, hue):
    found = FindType(graphic, -1, container_alias, hue)
    Telemetry.debug(state_name, "Item search", {
        "graphic": hex(graphic),
        "container": container_alias,
        "hue": hue,
        "found": found
    })
    if not found:
        ctx.fail(state_name, "Required item not found", {
            "graphic": hex(graphic),
            "container": container_alias,
            "hue": hue
        })
        return False
    return True


def guard_journal_clean(state_name):
    Telemetry.debug(state_name, "Clearing journal buffer")
    ClearJournal()


def guard_no_open_gump(state_name, gump_id):
    exists = GumpExists(gump_id)
    Telemetry.debug(state_name, "Gump presence check", {
        "gump_id": hex(gump_id),
        "exists": exists
    })
    return not exists

