# Name: Britain Thief Recon Controller
# Description: Runs spawn-to-thief reconnaissance FSM with fail-fast risk policy and no theft/combat actions.
# Author: ChatGPT Codex
# Shard: Confictura

import sys


def _purge_confictura_import_cache():
    purge_keys = []
    for module_name in sys.modules.keys():
        try:
            if module_name == "britain_thief_recon_config" or module_name.startswith("confictura_bot"):
                purge_keys.append(module_name)
        except Exception:
            continue

    for module_name in purge_keys:
        try:
            del sys.modules[module_name]
        except Exception:
            pass


_purge_confictura_import_cache()

from confictura_bot.context import BotContext
from confictura_bot.fsm import State
from confictura_bot.fsm import StateMachine
from confictura_bot.guards import guard_player_alive
from confictura_bot.safe_api import safe_pathfind
from confictura_bot.safe_api import safe_use_object
from confictura_bot.telemetry import Telemetry
from britain_thief_recon_config import BOT_CONFIG
from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.ca_shim import publish_known_ca_api

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


def _lower_text(value):
    if value is None:
        return ""

    try:
        return str(value).strip().lower()
    except Exception:
        return ""


def _serial_hex(serial_value):
    try:
        return hex(int(serial_value))
    except Exception:
        return "0x0"


def _coord_from_row(row):
    return (
        _to_int(row.get("x", 0), 0),
        _to_int(row.get("y", 0), 0),
        _to_int(row.get("z", 0), 0)
    )


def _chebyshev_distance(point_a, point_b):
    ax = _to_int(point_a[0], 0)
    ay = _to_int(point_a[1], 0)
    az = _to_int(point_a[2], 0)

    bx = _to_int(point_b[0], 0)
    by = _to_int(point_b[1], 0)
    bz = _to_int(point_b[2], 0)

    return max(abs(ax - bx), abs(ay - by), abs(az - bz))


def _distance_to_point(point):
    current = (
        _safe_call(0, X, "self"),
        _safe_call(0, Y, "self"),
        _safe_call(0, Z, "self")
    )
    return _chebyshev_distance(current, point)


def _clamp_axis_delta(delta_value, max_step):
    if delta_value > max_step:
        return max_step
    if delta_value < (0 - max_step):
        return (0 - max_step)
    return delta_value


def _build_segment_candidates(destination, max_step):
    current = (
        _safe_call(0, X, "self"),
        _safe_call(0, Y, "self"),
        _safe_call(0, Z, "self")
    )

    destination_point = (
        _to_int(destination[0], 0),
        _to_int(destination[1], 0),
        _to_int(destination[2], 0)
    )

    remaining_distance = _chebyshev_distance(current, destination_point)
    if remaining_distance <= max_step:
        return [destination_point]

    dx = destination_point[0] - current[0]
    dy = destination_point[1] - current[1]
    dz = destination_point[2] - current[2]

    max_axis = max(abs(dx), abs(dy), abs(dz))
    if max_axis <= 0:
        return [destination_point]

    scale = float(max_step) / float(max_axis)

    step_dx = int(dx * scale)
    step_dy = int(dy * scale)
    step_dz = int(dz * scale)

    if dx != 0 and step_dx == 0:
        step_dx = 1 if dx > 0 else -1
    if dy != 0 and step_dy == 0:
        step_dy = 1 if dy > 0 else -1
    if dz != 0 and step_dz == 0:
        step_dz = 1 if dz > 0 else -1

    primary = (
        current[0] + step_dx,
        current[1] + step_dy,
        current[2] + step_dz
    )

    axis_x = (
        current[0] + _clamp_axis_delta(dx, max_step),
        current[1],
        current[2]
    )

    axis_y = (
        current[0],
        current[1] + _clamp_axis_delta(dy, max_step),
        current[2]
    )

    candidates = []
    candidate_pool = [primary, axis_x, axis_y]

    idx = 0
    while idx < len(candidate_pool):
        candidate = candidate_pool[idx]
        idx += 1

        if candidate == current:
            continue

        if candidate in candidates:
            continue

        candidates.append(candidate)

    if len(candidates) <= 0:
        candidates.append(destination_point)

    return candidates


def _snapshot_self_state():
    return {
        "name": _safe_call("", Name, "self"),
        "map": _safe_call(-1, Map),
        "x": _safe_call(0, X, "self"),
        "y": _safe_call(0, Y, "self"),
        "z": _safe_call(0, Z, "self"),
        "hits": _safe_call(0, Hits, "self"),
        "max_hits": _safe_call(0, MaxHits, "self"),
        "hidden": _safe_call(False, Hidden, "self"),
        "war_mode": _safe_call(False, War, "self")
    }


def _notoriety_of_alias(alias_name):
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


def _normalize_waypoint(raw_waypoint, index_value):
    if not isinstance(raw_waypoint, dict):
        return None

    try:
        waypoint = {
            "name": str(raw_waypoint.get("name", "waypoint_{0}".format(index_value + 1))),
            "x": _to_int(raw_waypoint.get("x", 0), 0),
            "y": _to_int(raw_waypoint.get("y", 0), 0),
            "z": _to_int(raw_waypoint.get("z", 0), 0),
            "within_distance": _to_int(raw_waypoint.get("within_distance", 2), 2),
            "avoid_exact_tile": bool(raw_waypoint.get("avoid_exact_tile", False)),
            "scan_enabled": bool(raw_waypoint.get("scan_enabled", True)),
            "interaction": raw_waypoint.get("interaction", None)
        }
    except Exception:
        return None

    if waypoint["within_distance"] < 0:
        waypoint["within_distance"] = 0

    return waypoint


def _waypoint_interaction_satisfied(interaction_cfg):
    if not isinstance(interaction_cfg, dict):
        return (True, "no_interaction")

    expected_region = str(interaction_cfg.get("expected_region", "")).strip()
    if len(expected_region) > 0:
        if _safe_call(False, InRegion, expected_region, "self"):
            return (True, "expected_region")

    expected_destination = interaction_cfg.get("expected_destination", None)
    max_distance = _to_int(interaction_cfg.get("expected_distance", 8), 8)

    if isinstance(expected_destination, tuple) and len(expected_destination) == 3:
        observed_distance = _distance_to_point(expected_destination)
        if observed_distance <= max_distance:
            return (True, "expected_destination")

    return (False, "not_satisfied")


def _find_interaction_object(state_name, interaction_cfg, waypoint):
    graphic = _to_int(interaction_cfg.get("graphic", 0), 0)
    hue = _to_int(interaction_cfg.get("hue", -1), -1)
    search_range = _to_int(interaction_cfg.get("search_range", 8), 8)
    max_scans = _to_int(interaction_cfg.get("max_scans", 12), 12)
    source_max_distance = _to_int(interaction_cfg.get("source_max_distance", 6), 6)
    name_tokens = interaction_cfg.get("name_tokens", [])

    source_point = (waypoint.get("x", 0), waypoint.get("y", 0), waypoint.get("z", 0))

    observed_names = {}
    scan_count = 0
    seen_serials = {}

    if graphic <= 0:
        return {
            "matched": False,
            "reason": "invalid_graphic",
            "observed_names": [],
            "scan_count": 0
        }

    ClearIgnoreList()

    while scan_count < max_scans:
        scan_count += 1

        if not _find_type_host_safe(graphic, search_range, source_point, hue):
            break

        serial_value = _to_int(_safe_call(0, GetAlias, "found"), 0)
        if serial_value <= 0:
            IgnoreObject("found")
            Pause(15)
            continue

        if serial_value in seen_serials:
            IgnoreObject("found")
            Pause(15)
            continue

        seen_serials[serial_value] = True

        row = {
            "serial": serial_value,
            "serial_hex": _serial_hex(serial_value),
            "name": _safe_call("", Name, "found"),
            "graphic": _safe_call(graphic, Graphic, "found"),
            "hue": _safe_call(-1, Hue, "found"),
            "x": _safe_call(0, X, "found"),
            "y": _safe_call(0, Y, "found"),
            "z": _safe_call(0, Z, "found"),
            "distance": _safe_call(-1, Distance, "found")
        }

        lowered_name = _lower_text(row.get("name", ""))
        if lowered_name:
            observed_names[lowered_name] = True

        match_ok = True

        if hue != -1 and _to_int(row.get("hue", -1), -1) != hue:
            match_ok = False

        if match_ok:
            row_point = _coord_from_row(row)
            if _chebyshev_distance(row_point, source_point) > source_max_distance:
                match_ok = False

        if match_ok and len(name_tokens) > 0:
            token_match = False
            token_index = 0
            while token_index < len(name_tokens):
                token = _lower_text(name_tokens[token_index])
                if token and token in lowered_name:
                    token_match = True
                    break
                token_index += 1

            if not token_match:
                match_ok = False

        if match_ok:
            ClearIgnoreList()
            return {
                "matched": True,
                "row": row,
                "scan_count": scan_count,
                "observed_names": sorted(observed_names.keys())
            }

        IgnoreObject("found")
        Pause(15)

    ClearIgnoreList()

    return {
        "matched": False,
        "reason": "not_found",
        "scan_count": scan_count,
        "observed_names": sorted(observed_names.keys())
    }


def _execute_waypoint_interaction(ctx, state_name, waypoint):
    interaction_cfg = waypoint.get("interaction", None)
    if not isinstance(interaction_cfg, dict):
        return True

    interaction_type = _lower_text(interaction_cfg.get("type", ""))
    if interaction_type != "public_door":
        ctx.fail(state_name, "Unsupported waypoint interaction", {
            "interaction_type": interaction_cfg.get("type", "")
        })
        return False

    satisfied, reason = _waypoint_interaction_satisfied(interaction_cfg)
    if satisfied:
        Telemetry.info(state_name, "Waypoint interaction already satisfied", {
            "interaction_type": interaction_type,
            "reason": reason,
            "waypoint_name": waypoint.get("name", "unknown")
        })
        return True

    match_result = _find_interaction_object(state_name, interaction_cfg, waypoint)
    if not match_result.get("matched", False):
        ctx.fail(state_name, "Interaction object not found", {
            "waypoint_name": waypoint.get("name", "unknown"),
            "interaction_type": interaction_type,
            "graphic": _to_int(interaction_cfg.get("graphic", 0), 0),
            "hue": _to_int(interaction_cfg.get("hue", -1), -1),
            "search_range": _to_int(interaction_cfg.get("search_range", 8), 8),
            "scan_count": match_result.get("scan_count", 0),
            "observed_names": "|".join(match_result.get("observed_names", []))
        })
        return False

    matched_row = match_result.get("row", {})

    Telemetry.info(state_name, "Executing waypoint interaction", {
        "waypoint_name": waypoint.get("name", "unknown"),
        "interaction_type": interaction_type,
        "target_serial": matched_row.get("serial_hex", "0x0"),
        "target_name": matched_row.get("name", ""),
        "target_x": matched_row.get("x", 0),
        "target_y": matched_row.get("y", 0),
        "target_z": matched_row.get("z", 0)
    })

    safe_use_object(ctx, state_name, "found", _to_int(interaction_cfg.get("post_use_pause_ms", 600), 600))

    verify_attempts = _to_int(interaction_cfg.get("verify_attempts", 8), 8)
    verify_pause_ms = _to_int(interaction_cfg.get("verify_pause_ms", 250), 250)

    attempt = 0
    while attempt < verify_attempts:
        attempt += 1

        satisfied, reason = _waypoint_interaction_satisfied(interaction_cfg)
        if satisfied:
            Telemetry.info(state_name, "Waypoint interaction verified", {
                "waypoint_name": waypoint.get("name", "unknown"),
                "reason": reason,
                "attempt": attempt,
                "x": _safe_call(0, X, "self"),
                "y": _safe_call(0, Y, "self"),
                "z": _safe_call(0, Z, "self")
            })
            return True

        Pause(verify_pause_ms)

    ctx.fail(state_name, "Waypoint interaction verification failed", {
        "waypoint_name": waypoint.get("name", "unknown"),
        "expected_region": interaction_cfg.get("expected_region", ""),
        "expected_destination": interaction_cfg.get("expected_destination", None),
        "expected_distance": _to_int(interaction_cfg.get("expected_distance", 8), 8),
        "x": _safe_call(0, X, "self"),
        "y": _safe_call(0, Y, "self"),
        "z": _safe_call(0, Z, "self")
    })
    return False


def _invoke_mobile_selector(source_name, notorieties, selection, search_mode, body_filter, search_range):
    selector = GetEnemy
    alias_name = "enemy"

    if source_name == "friend":
        selector = GetFriend
        alias_name = "friend"

    attempts = [
        (notorieties, selection, search_mode, body_filter, search_range),
        (notorieties, selection, search_mode, search_range),
        (notorieties, search_mode, search_range)
    ]

    last_error = None
    index_value = 0
    while index_value < len(attempts):
        attempt_args = attempts[index_value]

        try:
            found_mobile = selector(*attempt_args)
            return (found_mobile, alias_name, "attempt_{0}".format(index_value + 1), None)
        except Exception as ex:
            last_error = ex

        index_value += 1

    return (False, alias_name, "failed", str(last_error))


def _scan_mobiles_multi_pass(ctx, state_name):
    recon_cfg = ctx.config.get("recon", {})
    pass_cfgs = recon_cfg.get("mobile_scan_passes", [])

    all_rows = []
    scan_counts = {}
    scan_order = []
    observed_name_set = {}
    seen_serials = {}

    pass_index = 0
    while pass_index < len(pass_cfgs):
        scan_cfg = pass_cfgs[pass_index]
        pass_name = str(scan_cfg.get("name", "pass_{0}".format(pass_index + 1)))
        source_name = _lower_text(scan_cfg.get("source", "enemy"))

        if source_name not in ("enemy", "friend"):
            source_name = "enemy"

        notorieties = scan_cfg.get("notorieties", ["Any"])
        selection = str(scan_cfg.get("selection", "Any"))
        search_mode = str(scan_cfg.get("search_mode", "Next"))
        body_filter = str(scan_cfg.get("body_filter", "Any"))
        search_range = _to_int(scan_cfg.get("search_range", 12), 12)
        max_scans = _to_int(scan_cfg.get("max_scans", 24), 24)

        pass_counts = {
            "attempted": 0,
            "captured": 0,
            "duplicate": 0,
            "invalid": 0,
            "selector_false": 0,
            "selector_errors": 0,
            "selector_signature": ""
        }

        ClearIgnoreList()

        scan_index = 0
        while scan_index < max_scans:
            found_mobile, alias_name, signature_name, selector_error = _invoke_mobile_selector(
                source_name,
                notorieties,
                selection,
                search_mode,
                body_filter,
                search_range
            )

            pass_counts["attempted"] += 1
            pass_counts["selector_signature"] = signature_name

            if selector_error is not None:
                pass_counts["selector_errors"] += 1
                Telemetry.warn(state_name, "Selector overload failed", {
                    "pass_name": pass_name,
                    "source": source_name,
                    "error": selector_error,
                    "signature": signature_name
                })
                break

            if not found_mobile:
                pass_counts["selector_false"] += 1
                break

            serial_value = _to_int(_safe_call(0, GetAlias, alias_name), 0)
            if serial_value <= 0:
                pass_counts["invalid"] += 1
                IgnoreObject(alias_name)
                Pause(15)
                scan_index += 1
                continue

            if serial_value in seen_serials:
                pass_counts["duplicate"] += 1
                IgnoreObject(alias_name)
                Pause(15)
                scan_index += 1
                continue

            seen_serials[serial_value] = True

            row = {
                "serial": serial_value,
                "serial_hex": _serial_hex(serial_value),
                "name": _safe_call("", Name, alias_name),
                "x": _safe_call(0, X, alias_name),
                "y": _safe_call(0, Y, alias_name),
                "z": _safe_call(0, Z, alias_name),
                "distance": _safe_call(-1, Distance, alias_name),
                "notoriety": _notoriety_of_alias(alias_name),
                "source": source_name,
                "scan_pass": pass_name
            }

            all_rows.append(row)
            pass_counts["captured"] += 1
            scan_order.append("{0}:{1}".format(pass_name, row.get("serial_hex", "0x0")))

            lowered_name = _lower_text(row.get("name", ""))
            if lowered_name:
                observed_name_set[lowered_name] = True

            IgnoreObject(alias_name)
            Pause(15)
            scan_index += 1

        ClearIgnoreList()

        scan_counts[pass_name] = pass_counts
        pass_index += 1

    observed_names = sorted(observed_name_set.keys())

    return {
        "rows": all_rows,
        "observed_names": observed_names,
        "scan_order": scan_order,
        "scan_counts": scan_counts
    }


def _find_type_host_safe(graphic, search_range, find_location, hue):
    if isinstance(find_location, tuple) and len(find_location) == 3:
        try:
            if FindType(graphic, search_range, find_location):
                return True
        except Exception:
            pass

    try:
        if FindType(graphic, search_range):
            return True
    except Exception:
        pass

    if _to_int(hue, -1) != -1:
        try:
            if FindType(graphic, search_range, -1, hue):
                return True
        except Exception:
            pass

    return False


def _scan_object_watch(ctx, state_name, watch_cfg):
    runtime_cfg = ctx.config.get("runtime", {})

    watch_name = str(watch_cfg.get("name", "unnamed_watch"))
    graphic = _to_int(watch_cfg.get("graphic", 0), 0)
    hue = _to_int(watch_cfg.get("hue", -1), -1)
    scan_range = _to_int(watch_cfg.get("scan_range", 12), 12)
    max_instances = _to_int(watch_cfg.get("max_instances", 4), 4)
    name_tokens = watch_cfg.get("name_tokens", [])
    property_keywords = watch_cfg.get("property_keywords", [])
    expected_near = watch_cfg.get("expected_near", None)
    max_distance = _to_int(watch_cfg.get("max_distance", 12), 12)

    if not isinstance(expected_near, tuple) or len(expected_near) != 3:
        expected_near = None

    found_rows = []
    matched_rows = []
    seen_serials = {}

    counts = {
        "attempted": 0,
        "captured": 0,
        "duplicate": 0,
        "hue_mismatch": 0,
        "name_mismatch": 0,
        "distance_mismatch": 0,
        "find_false": 0
    }

    ClearIgnoreList()

    idx = 0
    while idx < max_instances:
        counts["attempted"] += 1

        located = _find_type_host_safe(graphic, scan_range, expected_near, hue)
        if not located:
            counts["find_false"] += 1
            break

        serial_value = _to_int(_safe_call(0, GetAlias, "found"), 0)
        if serial_value <= 0:
            IgnoreObject("found")
            Pause(15)
            idx += 1
            continue

        if serial_value in seen_serials:
            counts["duplicate"] += 1
            IgnoreObject("found")
            Pause(15)
            idx += 1
            continue

        seen_serials[serial_value] = True

        WaitForProperties("found", runtime_cfg.get("properties_timeout_ms", 250))

        row = {
            "serial": serial_value,
            "serial_hex": _serial_hex(serial_value),
            "name": _safe_call("", Name, "found"),
            "graphic": _safe_call(graphic, Graphic, "found"),
            "hue": _safe_call(-1, Hue, "found"),
            "x": _safe_call(0, X, "found"),
            "y": _safe_call(0, Y, "found"),
            "z": _safe_call(0, Z, "found"),
            "distance": _safe_call(-1, Distance, "found"),
            "watch_name": watch_name,
            "property_hits": []
        }

        keyword_index = 0
        while keyword_index < len(property_keywords):
            keyword = property_keywords[keyword_index]
            if _safe_call(False, Property, "found", keyword):
                row["property_hits"].append(keyword)
            keyword_index += 1

        found_rows.append(row)
        counts["captured"] += 1

        is_match = True

        if hue != -1 and _to_int(row.get("hue", -1), -1) != hue:
            counts["hue_mismatch"] += 1
            is_match = False

        if is_match and len(name_tokens) > 0:
            lowered_name = _lower_text(row.get("name", ""))
            token_match = False

            token_index = 0
            while token_index < len(name_tokens):
                token = _lower_text(name_tokens[token_index])
                if token and token in lowered_name:
                    token_match = True
                    break
                token_index += 1

            if not token_match:
                counts["name_mismatch"] += 1
                is_match = False

        if is_match and expected_near is not None:
            row_point = _coord_from_row(row)
            check_distance = _chebyshev_distance(row_point, expected_near)
            if check_distance > max_distance:
                counts["distance_mismatch"] += 1
                is_match = False

        if is_match:
            matched_rows.append(row)

        IgnoreObject("found")
        Pause(15)
        idx += 1

    ClearIgnoreList()

    observed_name_set = {}
    row_index = 0
    while row_index < len(found_rows):
        lowered_name = _lower_text(found_rows[row_index].get("name", ""))
        if lowered_name:
            observed_name_set[lowered_name] = True
        row_index += 1

    return {
        "watch_name": watch_name,
        "found_rows": found_rows,
        "matched_rows": matched_rows,
        "observed_names": sorted(observed_name_set.keys()),
        "counts": counts,
        "search_range": scan_range
    }


def _mobile_matches_watch(mobile_row, watch_cfg):
    tokens = watch_cfg.get("name_tokens", [])
    expected_near = watch_cfg.get("expected_near", None)
    max_distance = _to_int(watch_cfg.get("max_distance", 12), 12)

    if len(tokens) > 0:
        lowered_name = _lower_text(mobile_row.get("name", ""))
        token_match = False

        token_index = 0
        while token_index < len(tokens):
            token = _lower_text(tokens[token_index])
            if token and token in lowered_name:
                token_match = True
                break
            token_index += 1

        if not token_match:
            return False

    if isinstance(expected_near, tuple) and len(expected_near) == 3:
        point = _coord_from_row(mobile_row)
        check_distance = _chebyshev_distance(point, expected_near)
        if check_distance > max_distance:
            return False

    return True


def _register_watch_hits(store, watch_name, matched_rows):
    if watch_name not in store:
        store[watch_name] = {}

    watch_store = store[watch_name]

    row_index = 0
    while row_index < len(matched_rows):
        row = matched_rows[row_index]
        serial_value = _to_int(row.get("serial", 0), 0)
        if serial_value > 0:
            watch_store[serial_value] = row
        row_index += 1


def _watch_store_summary(store, limit_per_watch):
    if not isinstance(store, dict) or len(store.keys()) == 0:
        return "<none>"

    sections = []

    for watch_name in sorted(store.keys()):
        watch_rows = store.get(watch_name, {})
        serials = sorted(watch_rows.keys())

        pieces = []
        serial_index = 0
        while serial_index < len(serials) and serial_index < limit_per_watch:
            serial_value = serials[serial_index]
            row = watch_rows[serial_value]
            pieces.append(
                "{0}@({1},{2},{3})#{4}".format(
                    row.get("name", "unknown"),
                    row.get("x", 0),
                    row.get("y", 0),
                    row.get("z", 0),
                    row.get("serial_hex", "0x0")
                )
            )
            serial_index += 1

        sections.append("{0}=[{1}]".format(watch_name, "; ".join(pieces)))

    return " | ".join(sections)


def _unresolved_watch_names(store, watch_cfgs):
    unresolved = []

    index_value = 0
    while index_value < len(watch_cfgs):
        cfg = watch_cfgs[index_value]
        watch_name = str(cfg.get("name", "watch_{0}".format(index_value + 1)))

        watch_rows = store.get(watch_name, {})
        if len(watch_rows.keys()) <= 0:
            unresolved.append(watch_name)

        index_value += 1

    return unresolved


def _risk_policy_triggered(ctx, state_name, mobile_rows):
    risk_cfg = ctx.config.get("risk", {})
    if not bool(risk_cfg.get("fail_fast_on_guard_or_criminal", True)):
        return False

    signals = []

    if bool(risk_cfg.get("stop_on_criminal_state", True)) and _safe_call(False, Criminal, "self"):
        signals.append("self_criminal")

    if bool(risk_cfg.get("stop_on_murderer_state", True)) and _safe_call(False, Murderer, "self"):
        signals.append("self_murderer")

    guard_tokens = risk_cfg.get("guard_name_tokens", ["guard", "town guard"])

    row_index = 0
    while row_index < len(mobile_rows):
        row = mobile_rows[row_index]
        lowered_name = _lower_text(row.get("name", ""))

        token_index = 0
        while token_index < len(guard_tokens):
            token = _lower_text(guard_tokens[token_index])
            if token and token in lowered_name:
                signals.append(
                    "guard_mobile:{0}:{1}".format(
                        row.get("serial_hex", "0x0"),
                        row.get("name", "unknown")
                    )
                )
                break
            token_index += 1

        row_index += 1

    if len(signals) > 0:
        ctx.fail(state_name, "Risk policy triggered", {
            "policy": "fail_fast_on_guard_or_criminal",
            "signals": "|".join(signals)
        })
        ctx.stop_cause = "risk_policy"
        return True

    return False


class BootstrapState(State):
    key = "BOOTSTRAP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering BOOTSTRAP")

    def tick(self, ctx):
        required_sections = ["runtime", "safety", "route", "recon", "risk"]

        section_index = 0
        while section_index < len(required_sections):
            section_name = required_sections[section_index]
            if section_name not in ctx.config:
                ctx.fail(self.key, "Missing config section", {"section": section_name})
                return "FATAL_STOP"
            section_index += 1

        waypoints = ctx.config.get("route", {}).get("corridor_waypoints", [])
        if len(waypoints) == 0:
            ctx.fail(self.key, "No route waypoints configured")
            return "FATAL_STOP"

        ctx.route_index = 0
        ctx.current_waypoint = None
        ctx.spawn_snapshot = None
        ctx.scan_cycle_count = 0
        ctx.discovered_mobiles = {}
        ctx.discovered_objects = {}
        ctx.last_scan_evidence = {}
        ctx.final_summary = {}
        ctx.stop_cause = ""
        ctx.segment_no_progress_count = 0

        Telemetry.info(self.key, "Bootstrap ready", {
            "waypoint_count": len(waypoints),
            "mobile_watch_count": len(ctx.config.get("recon", {}).get("mobile_watch", [])),
            "object_watch_count": len(ctx.config.get("recon", {}).get("object_watch", [])),
            "max_retries_per_state": ctx.config.get("runtime", {}).get("max_retries_per_state", 1)
        })

        if ctx.config.get("route", {}).get("spawn_capture_enabled", True):
            return "CAPTURE_SPAWN"

        return "TRAVEL_TO_WAYPOINT"


class CaptureSpawnState(State):
    key = "CAPTURE_SPAWN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering CAPTURE_SPAWN")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        snapshot = _snapshot_self_state()
        ctx.spawn_snapshot = snapshot

        Telemetry.info(self.key, "Captured spawn snapshot", snapshot)
        return "TRAVEL_TO_WAYPOINT"


class TravelToWaypointState(State):
    key = "TRAVEL_TO_WAYPOINT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering TRAVEL_TO_WAYPOINT")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        if _risk_policy_triggered(ctx, self.key, []):
            return "FATAL_STOP"

        route_cfg = ctx.config.get("route", {})
        runtime_cfg = ctx.config.get("runtime", {})

        waypoints = route_cfg.get("corridor_waypoints", [])
        if ctx.route_index >= len(waypoints):
            return "FINAL_SUMMARY"

        raw_waypoint = waypoints[ctx.route_index]
        waypoint = _normalize_waypoint(raw_waypoint, ctx.route_index)

        if waypoint is None:
            ctx.fail(self.key, "Invalid waypoint format", {
                "index": ctx.route_index + 1,
                "raw_waypoint": raw_waypoint
            })
            return "RECOVER"

        destination = (waypoint["x"], waypoint["y"], waypoint["z"])
        initial_distance_to_waypoint = _distance_to_point(destination)

        max_hop_distance = _to_int(runtime_cfg.get("pathfind_max_hop_distance", 12), 12)
        min_progress = _to_int(runtime_cfg.get("pathfind_min_progress", 1), 1)

        if max_hop_distance < 1:
            max_hop_distance = 1

        if min_progress < 1:
            min_progress = 1

        strategy_name = "safe_pathfind_direct"
        if initial_distance_to_waypoint > max_hop_distance:
            strategy_name = "safe_pathfind_segmented"

        Telemetry.info(self.key, "Action preconditions", {
            "waypoint_index": ctx.route_index + 1,
            "waypoint_name": waypoint["name"],
            "strategy": strategy_name,
            "destination": destination,
            "within_distance": waypoint["within_distance"],
            "avoid_exact_tile": waypoint["avoid_exact_tile"],
            "remaining_distance": initial_distance_to_waypoint,
            "max_hop_distance": max_hop_distance
        })

        if initial_distance_to_waypoint > max_hop_distance:
            segment_candidates = _build_segment_candidates(destination, max_hop_distance)
            candidate_order = []

            idx = 0
            while idx < len(segment_candidates):
                candidate = segment_candidates[idx]
                candidate_order.append("{0},{1},{2}".format(candidate[0], candidate[1], candidate[2]))
                idx += 1

            Telemetry.info(self.key, "Segment path preconditions", {
                "waypoint_name": waypoint["name"],
                "remaining_distance": initial_distance_to_waypoint,
                "max_hop_distance": max_hop_distance,
                "candidate_count": len(segment_candidates),
                "candidate_order": "|".join(candidate_order)
            })

            segment_progress = False
            segment_target = None
            segment_before = initial_distance_to_waypoint
            segment_after = initial_distance_to_waypoint
            candidate_results = []

            idx = 0
            while idx < len(segment_candidates):
                candidate = segment_candidates[idx]
                idx += 1

                before_candidate = _distance_to_point(destination)

                attempt_ok = safe_pathfind(
                    ctx,
                    self.key,
                    candidate,
                    runtime_cfg.get("pathfind_settle_ms", 350),
                    fail_on_error=False
                )

                after_candidate = _distance_to_point(destination)
                progress_candidate = before_candidate - after_candidate

                candidate_results.append(
                    "{0},{1},{2}:ok={3}:before={4}:after={5}:progress={6}".format(
                        candidate[0],
                        candidate[1],
                        candidate[2],
                        attempt_ok,
                        before_candidate,
                        after_candidate,
                        progress_candidate
                    )
                )

                if attempt_ok and progress_candidate >= min_progress:
                    segment_progress = True
                    segment_target = candidate
                    segment_before = before_candidate
                    segment_after = after_candidate
                    break

            if segment_progress:
                ctx.segment_no_progress_count = 0
                Telemetry.info(self.key, "Segment path progress", {
                    "waypoint_name": waypoint["name"],
                    "segment_target": segment_target,
                    "before": segment_before,
                    "after": segment_after,
                    "progress": segment_before - segment_after
                })
                return "TRAVEL_TO_WAYPOINT"

            tolerance = _to_int(runtime_cfg.get("segment_no_progress_tolerance", 4), 4)
            if tolerance < 0:
                tolerance = 0

            ctx.segment_no_progress_count = _to_int(getattr(ctx, "segment_no_progress_count", 0), 0) + 1

            Telemetry.warn(self.key, "Segment path no progress", {
                "waypoint_name": waypoint["name"],
                "destination": destination,
                "remaining_distance": initial_distance_to_waypoint,
                "candidate_order": "|".join(candidate_order),
                "candidate_results": "|".join(candidate_results),
                "stall_count": ctx.segment_no_progress_count,
                "stall_tolerance": tolerance,
                "min_progress": min_progress
            })

            if ctx.segment_no_progress_count > tolerance:
                ctx.fail(self.key, "Segment path no-progress tolerance exceeded", {
                    "waypoint_name": waypoint["name"],
                    "destination": destination,
                    "remaining_distance": initial_distance_to_waypoint,
                    "candidate_order": "|".join(candidate_order),
                    "candidate_results": "|".join(candidate_results),
                    "stall_count": ctx.segment_no_progress_count,
                    "stall_tolerance": tolerance,
                    "min_progress": min_progress
                })
                return "RECOVER"

            Pause(_to_int(runtime_cfg.get("segment_stall_pause_ms", 250), 250))
            return "TRAVEL_TO_WAYPOINT"

        if not safe_pathfind(ctx, self.key, destination, runtime_cfg.get("pathfind_settle_ms", 350)):
            return "RECOVER"

        ctx.segment_no_progress_count = 0
        distance_to_waypoint = _distance_to_point(destination)
        ctx.current_waypoint = waypoint
        if distance_to_waypoint > waypoint["within_distance"]:
            ctx.fail(self.key, "Unable to reach waypoint proximity", {
                "waypoint_name": waypoint["name"],
                "expected": waypoint["within_distance"],
                "observed": distance_to_waypoint,
                "destination": destination
            })
            return "RECOVER"

        if waypoint["avoid_exact_tile"] and distance_to_waypoint == 0:
            Telemetry.warn(self.key, "Standing on exact tile while avoid_exact_tile requested", {
                "waypoint_name": waypoint["name"],
                "distance": distance_to_waypoint
            })

        Telemetry.info(self.key, "Waypoint reached", {
            "waypoint_name": waypoint["name"],
            "distance": distance_to_waypoint,
            "destination": destination
        })

        if not _execute_waypoint_interaction(ctx, self.key, waypoint):
            return "RECOVER"

        if not bool(waypoint.get("scan_enabled", True)):
            Telemetry.info(self.key, "Waypoint scan skipped by policy", {
                "waypoint_name": waypoint["name"],
                "scan_enabled": waypoint.get("scan_enabled", True)
            })
            return "ADVANCE_WAYPOINT"

        return "RECON_SCAN"


class ReconScanState(State):
    key = "RECON_SCAN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering RECON_SCAN")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        waypoint = getattr(ctx, "current_waypoint", None)
        if waypoint is None:
            ctx.fail(self.key, "No active waypoint for scan")
            return "RECOVER"

        recon_cfg = ctx.config.get("recon", {})

        Telemetry.info(self.key, "Action preconditions", {
            "waypoint_name": waypoint.get("name", "unknown"),
            "selector_strategy": "multi_pass_enemy_friend_next",
            "search_range": "pass-configured",
            "scan_pass_count": len(recon_cfg.get("mobile_scan_passes", []))
        })

        scan_result = _scan_mobiles_multi_pass(ctx, self.key)
        mobile_rows = scan_result.get("rows", [])
        observed_names = scan_result.get("observed_names", [])
        scan_order = scan_result.get("scan_order", [])
        scan_counts = scan_result.get("scan_counts", {})

        if _risk_policy_triggered(ctx, self.key, mobile_rows):
            return "FATAL_STOP"

        mobile_watch_cfgs = recon_cfg.get("mobile_watch", [])

        mw_index = 0
        while mw_index < len(mobile_watch_cfgs):
            watch_cfg = mobile_watch_cfgs[mw_index]
            watch_name = str(watch_cfg.get("name", "mobile_watch_{0}".format(mw_index + 1)))

            matched_rows = []
            row_index = 0
            while row_index < len(mobile_rows):
                row = mobile_rows[row_index]
                if _mobile_matches_watch(row, watch_cfg):
                    matched_rows.append(row)
                row_index += 1

            if len(matched_rows) > 0:
                _register_watch_hits(ctx.discovered_mobiles, watch_name, matched_rows)
                Telemetry.info(self.key, "Mobile watch matched", {
                    "watch_name": watch_name,
                    "matched_count": len(matched_rows),
                    "sample": "{0}@{1},{2},{3}".format(
                        matched_rows[0].get("name", "unknown"),
                        matched_rows[0].get("x", 0),
                        matched_rows[0].get("y", 0),
                        matched_rows[0].get("z", 0)
                    )
                })
            else:
                Telemetry.warn(self.key, "Mobile watch unmatched", {
                    "watch_name": watch_name,
                    "expected": "|".join(watch_cfg.get("name_tokens", [])),
                    "observed_names": "|".join(observed_names),
                    "search_range": "pass-configured",
                    "scan_order": "|".join(scan_order),
                    "scan_counts": scan_counts
                })

            mw_index += 1

        object_watch_cfgs = recon_cfg.get("object_watch", [])

        ow_index = 0
        while ow_index < len(object_watch_cfgs):
            watch_cfg = object_watch_cfgs[ow_index]
            object_result = _scan_object_watch(ctx, self.key, watch_cfg)

            watch_name = object_result.get("watch_name", "unnamed_object_watch")
            matched_rows = object_result.get("matched_rows", [])

            if len(matched_rows) > 0:
                _register_watch_hits(ctx.discovered_objects, watch_name, matched_rows)
                Telemetry.info(self.key, "Object watch matched", {
                    "watch_name": watch_name,
                    "matched_count": len(matched_rows),
                    "sample": "{0}@{1},{2},{3}".format(
                        matched_rows[0].get("name", "unknown"),
                        matched_rows[0].get("x", 0),
                        matched_rows[0].get("y", 0),
                        matched_rows[0].get("z", 0)
                    )
                })
            else:
                Telemetry.warn(self.key, "Object watch unmatched", {
                    "watch_name": watch_name,
                    "expected": "graphic={0},hue={1}".format(
                        _to_int(watch_cfg.get("graphic", 0), 0),
                        _to_int(watch_cfg.get("hue", -1), -1)
                    ),
                    "observed": "|".join(object_result.get("observed_names", [])),
                    "search_range": object_result.get("search_range", -1),
                    "counts": object_result.get("counts", {})
                })

            ow_index += 1

        ctx.scan_cycle_count += 1
        ctx.last_scan_evidence = {
            "waypoint": waypoint.get("name", "unknown"),
            "observed_names": observed_names,
            "scan_order": scan_order,
            "scan_counts": scan_counts
        }

        return "ADVANCE_WAYPOINT"


class AdvanceWaypointState(State):
    key = "ADVANCE_WAYPOINT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering ADVANCE_WAYPOINT")

    def tick(self, ctx):
        route_cfg = ctx.config.get("route", {})
        waypoints = route_cfg.get("corridor_waypoints", [])

        previous_index = ctx.route_index
        ctx.route_index += 1

        Telemetry.info(self.key, "Advancing route waypoint", {
            "from_index": previous_index + 1,
            "to_index": ctx.route_index + 1,
            "total_waypoints": len(waypoints)
        })

        if ctx.route_index >= len(waypoints):
            return "FINAL_SUMMARY"

        return "TRAVEL_TO_WAYPOINT"


class FinalSummaryState(State):
    key = "FINAL_SUMMARY"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering FINAL_SUMMARY")

    def tick(self, ctx):
        recon_cfg = ctx.config.get("recon", {})

        mobile_watch_cfgs = recon_cfg.get("mobile_watch", [])
        object_watch_cfgs = recon_cfg.get("object_watch", [])

        unresolved_mobile = _unresolved_watch_names(ctx.discovered_mobiles, mobile_watch_cfgs)
        unresolved_object = _unresolved_watch_names(ctx.discovered_objects, object_watch_cfgs)

        summary_limit = _to_int(recon_cfg.get("final_summary_limit_per_target", 4), 4)

        ctx.final_summary = {
            "scan_cycles": ctx.scan_cycle_count,
            "waypoints_total": len(ctx.config.get("route", {}).get("corridor_waypoints", [])),
            "waypoints_visited": ctx.route_index,
            "spawn": ctx.spawn_snapshot,
            "discovered_mobiles": _watch_store_summary(ctx.discovered_mobiles, summary_limit),
            "discovered_objects": _watch_store_summary(ctx.discovered_objects, summary_limit),
            "unresolved_mobile_watch": "|".join(unresolved_mobile),
            "unresolved_object_watch": "|".join(unresolved_object),
            "last_scan_waypoint": ctx.last_scan_evidence.get("waypoint", "unknown")
        }

        Telemetry.info(self.key, "Recon summary ready", ctx.final_summary)

        if recon_cfg.get("fail_if_unresolved", False) and (len(unresolved_mobile) > 0 or len(unresolved_object) > 0):
            ctx.fail(self.key, "Recon unresolved expected targets", {
                "unresolved_mobile_watch": "|".join(unresolved_mobile),
                "unresolved_object_watch": "|".join(unresolved_object)
            })
            ctx.stop_cause = "unresolved_targets"
            return "FATAL_STOP"

        ctx.stop_cause = "recon_complete"
        return "COMPLETE_STOP"


class RecoverState(State):
    key = "RECOVER"

    def enter(self, ctx):
        Telemetry.warn(self.key, "Entering RECOVER", {
            "last_failed_state": ctx.last_failed_state,
            "last_error": ctx.last_error
        })

    def tick(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        max_retries = runtime_cfg.get("max_retries_per_state", 1)

        failed_state = ctx.last_failed_state
        if failed_state is None:
            failed_state = "UNKNOWN"

        retry_count = ctx.increment_retry(failed_state)
        Telemetry.warn(self.key, "Retrying failed state", {
            "failed_state": failed_state,
            "retry_count": retry_count,
            "max_retries": max_retries
        })

        CancelTarget()
        WarMode("off")
        ClearObjectQueue()
        Pause(200)

        if retry_count > max_retries:
            ctx.fail(self.key, "Retry cap exceeded", {
                "failed_state": failed_state,
                "retry_count": retry_count,
                "max_retries": max_retries
            })
            ctx.stop_cause = "retry_cap_exceeded"
            return "FATAL_STOP"

        if failed_state in ("CAPTURE_SPAWN", "TRAVEL_TO_WAYPOINT", "RECON_SCAN"):
            return failed_state

        return "TRAVEL_TO_WAYPOINT"


class CompleteStopState(State):
    key = "COMPLETE_STOP"

    def enter(self, ctx):
        summary = getattr(ctx, "final_summary", {})
        summary_payload = {
            "stop_cause": getattr(ctx, "stop_cause", "recon_complete"),
            "scan_cycles": summary.get("scan_cycles", 0),
            "waypoints_total": summary.get("waypoints_total", 0),
            "waypoints_visited": summary.get("waypoints_visited", 0),
            "unresolved_mobile_watch": summary.get("unresolved_mobile_watch", ""),
            "unresolved_object_watch": summary.get("unresolved_object_watch", "")
        }

        Telemetry.info(self.key, "Britain thief recon complete", summary_payload)
        ctx.stop("Spawn-to-thief reconnaissance complete")
        Stop()

    def tick(self, ctx):
        return None


class FatalStopState(State):
    key = "FATAL_STOP"

    def enter(self, ctx):
        Telemetry.fatal(self.key, "Entering FATAL_STOP", {
            "last_failed_step": ctx.last_failed_state,
            "failure_reason": ctx.last_error,
            "stop_cause": getattr(ctx, "stop_cause", "fail_safe_stop"),
            "tick_count": ctx.tick_count
        })

        WarMode("off")
        CancelTarget()

        ctx.stop("Fail-safe stop policy triggered")
        Stop()

    def tick(self, ctx):
        return None


def _build_states():
    return {
        "BOOTSTRAP": BootstrapState(),
        "CAPTURE_SPAWN": CaptureSpawnState(),
        "TRAVEL_TO_WAYPOINT": TravelToWaypointState(),
        "RECON_SCAN": ReconScanState(),
        "ADVANCE_WAYPOINT": AdvanceWaypointState(),
        "FINAL_SUMMARY": FinalSummaryState(),
        "RECOVER": RecoverState(),
        "COMPLETE_STOP": CompleteStopState(),
        "FATAL_STOP": FatalStopState()
    }


def run_britain_thief_recon_controller(config):
    published_api = publish_known_ca_api(globals())
    Telemetry.debug("MAIN", "Published ClassicAssist API symbols", {"count": published_api})
    Telemetry.info("MAIN", "Starting BritainThiefReconController")

    ctx = BotContext(config)
    states = _build_states()

    machine = StateMachine(ctx, states, "BOOTSTRAP")
    machine.run()

    Telemetry.info("MAIN", "BritainThiefReconController finished", {
        "tick_count": ctx.tick_count,
        "transition_count": ctx.transition_count,
        "last_error_state": ctx.last_error_state,
        "last_error": ctx.last_error,
        "stop_cause": getattr(ctx, "stop_cause", "")
    })


run_britain_thief_recon_controller(BOT_CONFIG)












