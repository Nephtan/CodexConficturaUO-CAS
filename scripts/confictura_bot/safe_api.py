# Name: Confictura ClassicAssist Safe API Wrappers
# Description: Wraps blocking actions with validation, timeout control, and telemetry.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry
from confictura_bot.gump_ids import gump_hex

bind_ca_api(globals())


def _normalize_text_entries(textentries):
    if textentries is None:
        return {}
    if not isinstance(textentries, dict):
        return {}

    normalized = {}
    for key in textentries.keys():
        try:
            entry_id = int(key)
        except Exception:
            continue

        value = textentries.get(key)
        if value is None:
            value = ""

        try:
            normalized[entry_id] = unicode(value)
        except Exception:
            try:
                normalized[entry_id] = str(value)
            except Exception:
                normalized[entry_id] = ""

    return normalized


def safe_wait_for_target(ctx, state_name, timeout_ms):
    timeout = int(timeout_ms)
    if timeout <= 0:
        timeout = ctx.config.get("runtime", {}).get("target_timeout_ms", 5000)

    Telemetry.debug(state_name, "Waiting for target", {"timeout_ms": timeout})
    ok = WaitForTarget(timeout)

    if not ok:
        ctx.fail(state_name, "WaitForTarget timeout", {"timeout_ms": timeout})
        return False

    return True


def safe_wait_for_gump(ctx, state_name, gump_id, timeout_ms):
    timeout = int(timeout_ms)
    Telemetry.debug(state_name, "Waiting for specific gump", {
        "gump_id": gump_hex(gump_id),
        "timeout_ms": timeout
    })
    ok = WaitForGump(gump_id, timeout)
    if not ok:
        ctx.fail(state_name, "WaitForGump timeout", {
            "gump_id": gump_hex(gump_id),
            "timeout_ms": timeout
        })
        return False
    return True


def safe_wait_for_gump_any(ctx, state_name, timeout_ms):
    timeout = int(timeout_ms)
    Telemetry.debug(state_name, "Waiting for any gump", {"timeout_ms": timeout})
    ok = WaitForGump(0, timeout)
    if ok:
        Telemetry.info(state_name, "Incoming gump packet detected")
    return ok


def safe_target(ctx, state_name, target_obj, target_kind):
    if target_kind == "alias":
        if target_obj not in ("self", "last", "backpack", "bank") and not FindAlias(target_obj):
            ctx.fail(state_name, "Target alias missing", {"target": target_obj})
            return False

    Telemetry.info(state_name, "Sending target", {
        "target": target_obj,
        "target_kind": target_kind
    })
    Target(target_obj)
    return True


def safe_target_tile_offset(ctx, state_name, xoffset, yoffset, zoffset, itemid):
    Telemetry.info(state_name, "Targeting tile offset", {
        "xoffset": xoffset,
        "yoffset": yoffset,
        "zoffset": zoffset,
        "itemid": itemid
    })
    TargetTileOffset(xoffset, yoffset, zoffset, itemid)
    return True


def safe_target_by_resource(ctx, state_name, tool_alias, resource_type, settle_pause_ms):
    Telemetry.info(state_name, "Target by resource", {
        "tool_alias": tool_alias,
        "resource_type": resource_type
    })
    TargetByResource(tool_alias, resource_type)
    Pause(settle_pause_ms)
    return True


def safe_use_skill(ctx, state_name, skill_name, settle_pause_ms):
    Telemetry.info(state_name, "Using skill", {"skill": skill_name})
    UseSkill(skill_name)
    Pause(settle_pause_ms)
    return True


def safe_use_object(ctx, state_name, obj, settle_pause_ms):
    Telemetry.info(state_name, "Using object", {"object": obj})
    UseObject(obj)
    Pause(settle_pause_ms)
    return True


def safe_use_type(ctx, state_name, graphic, hue, container_alias, settle_pause_ms):
    Telemetry.info(state_name, "Using type", {
        "graphic": hex(graphic),
        "hue": hue,
        "container": container_alias
    })
    UseType(graphic, hue, container_alias)
    Pause(settle_pause_ms)
    return True


def safe_context_menu(ctx, state_name, obj, entry_index, settle_pause_ms):
    Telemetry.info(state_name, "Opening context menu entry", {
        "object": obj,
        "entry_index": entry_index
    })
    ContextMenu(obj, entry_index)
    Pause(settle_pause_ms)
    return True

def safe_click_object(ctx, state_name, obj, settle_pause_ms):
    Telemetry.info(state_name, "Single-clicking object", {"object": obj})
    ClickObject(obj)
    Pause(settle_pause_ms)
    return True


def safe_wait_for_context(ctx, state_name, obj, entry, timeout_ms, fail_on_timeout=True):
    timeout = int(timeout_ms)
    Telemetry.debug(state_name, "Waiting for context action", {
        "object": obj,
        "entry": entry,
        "timeout_ms": timeout
    })

    ok = WaitForContext(obj, entry, timeout)
    if not ok:
        if fail_on_timeout:
            ctx.fail(state_name, "WaitForContext failed", {
                "object": obj,
                "entry": entry,
                "timeout_ms": timeout
            })
        else:
            Telemetry.warn(state_name, "WaitForContext returned false", {
                "object": obj,
                "entry": entry,
                "timeout_ms": timeout
            })
        return False

    return True

def safe_speech(ctx, state_name, text, settle_pause_ms):
    Telemetry.info(state_name, "Speaking", {"text": text})
    Msg(text)
    Pause(settle_pause_ms)
    return True


def safe_pathfind(ctx, state_name, destination, settle_pause_ms, checkdistance=None, desireddistance=None, fail_on_error=True):
    telemetry_payload = {"destination": destination}
    if checkdistance is not None:
        telemetry_payload["checkdistance"] = bool(checkdistance)
    if desireddistance is not None:
        telemetry_payload["desireddistance"] = int(desireddistance)

    Telemetry.info(state_name, "Pathfind request", telemetry_payload)

    result = False
    if isinstance(destination, tuple) and len(destination) == 3:
        if checkdistance is None and desireddistance is None:
            result = Pathfind(destination[0], destination[1], destination[2])
        else:
            check_flag = bool(checkdistance)
            desired = int(desireddistance if desireddistance is not None else 1)
            result = Pathfind(destination[0], destination[1], destination[2], check_flag, desired)
    else:
        if checkdistance is None and desireddistance is None:
            result = Pathfind(destination)
        else:
            check_flag = bool(checkdistance)
            desired = int(desireddistance if desireddistance is not None else 1)
            result = Pathfind(destination, check_flag, desired)

    Pause(settle_pause_ms)
    if not result:
        if fail_on_error:
            ctx.fail(state_name, "Pathfind failed", telemetry_payload)
        else:
            Telemetry.warn(state_name, "Pathfind failed (non-fatal)", telemetry_payload)
        return False

    return True


def safe_reply_gump(ctx, state_name, gump_id, button_id, timeout_ms, switches=None, textentries=None):
    if switches is None:
        switches = []

    normalized_entries = _normalize_text_entries(textentries)

    Telemetry.debug(state_name, "Preparing gump reply", {
        "gump_id": gump_hex(gump_id),
        "button_id": button_id,
        "timeout_ms": timeout_ms,
        "switch_count": len(switches),
        "text_entry_count": len(normalized_entries)
    })

    if timeout_ms > 0:
        wait_target = gump_id
        if int(gump_id) <= 0:
            wait_target = 0

        if not WaitForGump(wait_target, timeout_ms):
            ctx.fail(state_name, "WaitForGump timeout", {
                "gump_id": gump_hex(gump_id),
                "wait_target": gump_hex(wait_target),
                "timeout_ms": timeout_ms
            })
            return False
    else:
        if int(gump_id) > 0:
            if not GumpExists(gump_id):
                ctx.fail(state_name, "Gump not open for reply", {
                    "gump_id": gump_hex(gump_id)
                })
                return False
        else:
            Telemetry.warn(state_name, "Replying without specific gump id", {
                "button_id": button_id,
                "mode": "any_open_gump"
            })

    Telemetry.info(state_name, "Replying to gump", {
        "gump_id": gump_hex(gump_id),
        "button_id": button_id
    })

    has_switches = len(switches) > 0
    has_text_entries = len(normalized_entries) > 0

    # Prefer the simple overload when no optional payload is needed.
    if not has_switches and not has_text_entries:
        try:
            ReplyGump(gump_id, button_id)
        except Exception as ex:
            ctx.fail(state_name, "ReplyGump failed", {
                "gump_id": gump_hex(gump_id),
                "button_id": button_id,
                "exception": str(ex)
            })
            return False
        return True

    dotnet_switches = switches
    dotnet_entries = normalized_entries

    # ClassicAssist expects Int32[] and Dictionary[Int32, String] for the 4-arg overload.
    try:
        from System import Array
        from System import Int32
        from System import String
        from System.Collections.Generic import Dictionary

        coerced_switches = []
        for switch_value in switches:
            try:
                coerced_switches.append(int(switch_value))
            except Exception:
                continue

        dotnet_switches = Array[Int32](coerced_switches)
        dotnet_entries = Dictionary[Int32, String]()

        for key in normalized_entries.keys():
            try:
                entry_key = Int32(int(key))
            except Exception:
                continue

            try:
                entry_value = String(unicode(normalized_entries.get(key, u"")))
            except Exception:
                try:
                    entry_value = String(str(normalized_entries.get(key, "")))
                except Exception:
                    entry_value = String("")

            dotnet_entries[entry_key] = entry_value
    except Exception as ex:
        Telemetry.warn(state_name, "Unable to coerce gump payload to .NET types", {
            "exception": str(ex)
        })

    try:
        ReplyGump(gump_id, button_id, dotnet_switches, dotnet_entries)
    except Exception as ex:
        ctx.fail(state_name, "ReplyGump failed", {
            "gump_id": gump_hex(gump_id),
            "button_id": button_id,
            "exception": str(ex),
            "switch_count": len(switches),
            "text_entry_count": len(normalized_entries)
        })
        return False
    return True


def safe_wait_for_journal_any(ctx, state_name, entries, timeout_ms, author=""):
    Telemetry.debug(state_name, "Waiting for journal entries", {
        "entries": "|".join(entries),
        "timeout_ms": timeout_ms,
        "author": author
    })

    result = WaitForJournal(entries, timeout_ms, author)
    if result is None:
        ctx.fail(state_name, "WaitForJournal returned None")
        return (False, None)

    # Handles tuple or .NET ValueTuple return shapes.
    try:
        index_value = result[0]
        text_value = result[1]
        if index_value is None:
            return (False, None)
        return (True, text_value)
    except Exception:
        pass

    # Defensive fallback if API behavior differs by shard/client version.
    if result is True:
        return (True, "")

    return (False, None)


def safe_move_type(ctx, state_name, graphic, source_alias, destination_alias, hue, amount):
    Telemetry.info(state_name, "Moving item type", {
        "graphic": hex(graphic),
        "source": source_alias,
        "destination": destination_alias,
        "hue": hue,
        "amount": amount
    })
    MoveType(graphic, source_alias, destination_alias, -1, -1, 0, hue, amount)
    return True









