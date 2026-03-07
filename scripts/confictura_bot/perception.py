# Name: Confictura Perception Sensors
# Description: Collects nearby map, mobile, and object observations using ClassicAssist APIs.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


def _to_int(value, default_value=0):
    try:
        return int(value)
    except Exception:
        return default_value


def _safe_call(default_value, fn, *args):
    try:
        return fn(*args)
    except Exception:
        return default_value


def _serial_hex(serial_value):
    try:
        return hex(int(serial_value))
    except Exception:
        return "0x0"


def _notoriety_of(alias_name):
    if _safe_call(False, Invulnerable, alias_name):
        return "Invulnerable"
    if _safe_call(False, Ally, alias_name):
        return "Ally"
    if _safe_call(False, Innocent, alias_name):
        return "Innocent"
    if _safe_call(False, Gray, alias_name):
        return "Gray"
    if _safe_call(False, Criminal, alias_name):
        return "Criminal"
    if _safe_call(False, Murderer, alias_name):
        return "Murderer"
    if _safe_call(False, Enemy, alias_name):
        return "Enemy"
    return "Unknown"


def snapshot_self_state(state_name, region_attributes):
    snapshot = {
        "name": _safe_call("", Name, "self"),
        "map": _safe_call(-1, Map),
        "x": _safe_call(0, X, "self"),
        "y": _safe_call(0, Y, "self"),
        "z": _safe_call(0, Z, "self"),
        "hits": _safe_call(0, Hits, "self"),
        "max_hits": _safe_call(0, MaxHits, "self"),
        "mana": _safe_call(0, Mana, "self"),
        "max_mana": _safe_call(0, MaxMana, "self"),
        "stam": _safe_call(0, Stam, "self"),
        "max_stam": _safe_call(0, MaxStam, "self"),
        "weight": _safe_call(0, Weight),
        "max_weight": _safe_call(0, MaxWeight),
        "war_mode": _safe_call(False, War, "self"),
        "hidden": _safe_call(False, Hidden, "self"),
        "poisoned": _safe_call(False, Poisoned, "self"),
        "paralyzed": _safe_call(False, Paralyzed, "self")
    }

    for attribute_name in region_attributes:
        key = "region_{0}".format(attribute_name)
        snapshot[key] = _safe_call(False, InRegion, attribute_name, "self")

    Telemetry.info(state_name, "Self snapshot", snapshot)
    return snapshot


def scan_mobiles(state_name, mobile_scan_cfg):
    if not mobile_scan_cfg.get("enabled", True):
        Telemetry.debug(state_name, "Mobile scan disabled")
        return []

    scan_range = mobile_scan_cfg.get("range", 12)
    max_entities = mobile_scan_cfg.get("max_entities", 24)
    notorieties = mobile_scan_cfg.get("notorieties", ["Any"])

    results = []
    seen_serials = {}
    repeat_hits = 0

    ClearIgnoreList()

    index_value = 0
    while index_value < max_entities:
        found_mobile = GetEnemy(notorieties, "Any", "Closest", "Any", scan_range)
        if not found_mobile:
            break

        serial_value = _to_int(GetAlias("enemy"), 0)
        if serial_value <= 0:
            Telemetry.warn(state_name, "GetEnemy returned invalid alias serial")
            break

        if serial_value in seen_serials:
            repeat_hits += 1
            IgnoreObject("enemy")
            if repeat_hits >= 2:
                break
            Pause(20)
            continue

        repeat_hits = 0
        seen_serials[serial_value] = True

        mobile_data = {
            "serial": serial_value,
            "serial_hex": _serial_hex(serial_value),
            "name": _safe_call("", Name, "enemy"),
            "x": _safe_call(0, X, "enemy"),
            "y": _safe_call(0, Y, "enemy"),
            "z": _safe_call(0, Z, "enemy"),
            "distance": _safe_call(-1, Distance, "enemy"),
            "hits": _safe_call(0, Hits, "enemy"),
            "max_hits": _safe_call(0, MaxHits, "enemy"),
            "notoriety": _notoriety_of("enemy"),
            "war_mode": _safe_call(False, War, "enemy"),
            "hidden": _safe_call(False, Hidden, "enemy")
        }

        results.append(mobile_data)
        IgnoreObject("enemy")
        Pause(20)
        index_value += 1

    ClearIgnoreList()

    Telemetry.info(state_name, "Mobile scan complete", {
        "count": len(results),
        "range": scan_range,
        "max_entities": max_entities
    })

    return results


def _find_object_by_graphic(graphic_value, scan_range, hue_value):
    if hue_value is None or hue_value == -1:
        return FindType(graphic_value, scan_range)
    return FindType(graphic_value, scan_range, -1, hue_value)


def scan_objects(state_name, object_scan_cfg):
    if not object_scan_cfg.get("enabled", True):
        Telemetry.debug(state_name, "Object scan disabled")
        return []

    scan_range = object_scan_cfg.get("range", 12)
    properties_timeout = object_scan_cfg.get("properties_timeout_ms", 250)
    watch_graphics = object_scan_cfg.get("watch_graphics", [])

    results = []

    watch_index = 0
    while watch_index < len(watch_graphics):
        watch_item = watch_graphics[watch_index]
        watch_name = watch_item.get("name", "unnamed")
        graphic_value = watch_item.get("graphic", 0)
        hue_value = watch_item.get("hue", -1)
        max_instances = watch_item.get("max_instances", 8)
        property_keywords = watch_item.get("property_keywords", [])

        seen_serials = {}

        ClearIgnoreList()

        found_count = 0
        while found_count < max_instances:
            found_object = _find_object_by_graphic(graphic_value, scan_range, hue_value)
            if not found_object:
                break

            serial_value = _to_int(GetAlias("found"), 0)
            if serial_value <= 0:
                break

            if serial_value in seen_serials:
                IgnoreObject("found")
                break

            seen_serials[serial_value] = True
            WaitForProperties("found", properties_timeout)

            object_data = {
                "watch_name": watch_name,
                "serial": serial_value,
                "serial_hex": _serial_hex(serial_value),
                "graphic": _safe_call(graphic_value, Graphic, "found"),
                "hue": _safe_call(-1, Hue, "found"),
                "x": _safe_call(0, X, "found"),
                "y": _safe_call(0, Y, "found"),
                "z": _safe_call(0, Z, "found"),
                "distance": _safe_call(-1, Distance, "found"),
                "name": _safe_call("", Name, "found"),
                "property_hits": []
            }

            keyword_index = 0
            while keyword_index < len(property_keywords):
                keyword = property_keywords[keyword_index]
                if _safe_call(False, Property, "found", keyword):
                    object_data["property_hits"].append(keyword)
                keyword_index += 1

            results.append(object_data)
            IgnoreObject("found")
            Pause(15)
            found_count += 1

        ClearIgnoreList()
        watch_index += 1

    Telemetry.info(state_name, "Object scan complete", {
        "count": len(results),
        "watch_graphics": len(watch_graphics),
        "range": scan_range
    })

    return results


def merge_world_observations(ctx, self_snapshot, mobile_rows, object_rows):
    if not hasattr(ctx, "world_model") or ctx.world_model is None:
        ctx.world_model = {
            "visited_tiles": {},
            "mobiles": {},
            "objects": {},
            "cycle": 0,
            "unknown_gumps": 0
        }

    world_model = ctx.world_model
    world_model["cycle"] = world_model.get("cycle", 0) + 1

    tile_key = "{0}:{1}:{2}:{3}".format(
        self_snapshot.get("map", -1),
        self_snapshot.get("x", 0),
        self_snapshot.get("y", 0),
        self_snapshot.get("z", 0)
    )
    world_model["visited_tiles"][tile_key] = True

    for mobile_data in mobile_rows:
        serial_value = mobile_data.get("serial", 0)
        if serial_value <= 0:
            continue
        mobile_data["last_seen_cycle"] = world_model["cycle"]
        world_model["mobiles"][serial_value] = mobile_data

    for object_data in object_rows:
        serial_value = object_data.get("serial", 0)
        if serial_value <= 0:
            continue
        object_data["last_seen_cycle"] = world_model["cycle"]
        world_model["objects"][serial_value] = object_data

    summary = {
        "cycle": world_model["cycle"],
        "visited_tiles": len(world_model["visited_tiles"]),
        "unique_mobiles": len(world_model["mobiles"]),
        "unique_objects": len(world_model["objects"]),
        "unknown_gumps": world_model.get("unknown_gumps", 0)
    }

    return summary

