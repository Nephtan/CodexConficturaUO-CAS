# Name: Britain Pathing RnD Controller
# Description: Runs an isolated Britain-only FSM harness that validates shared coordinate pathing behavior.
# Author: ChatGPT Codex
# Shard: Confictura

import random
import sys


def _purge_confictura_import_cache():
    purge_keys = []
    for module_name in sys.modules.keys():
        try:
            if module_name == "britain_pathing_rd_config":
                purge_keys.append(module_name)
                continue
            if module_name.startswith("confictura_bot"):
                purge_keys.append(module_name)
                continue
        except Exception:
            continue

    for module_name in purge_keys:
        try:
            del sys.modules[module_name]
        except Exception:
            pass


_purge_confictura_import_cache()

from britain_pathing_rd_config import BOT_CONFIG
from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.ca_shim import publish_known_ca_api
from confictura_bot.context import BotContext
from confictura_bot.fsm import State
from confictura_bot.fsm import StateMachine
from confictura_bot.guards import guard_player_alive
from confictura_bot.pathing import navigate_to_coordinate
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


try:
    _INTEGER_TYPES = (int, long)
except Exception:
    _INTEGER_TYPES = (int,)

_SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED = False


def _to_int(value, default_value):
    try:
        return int(value)
    except Exception:
        return default_value


def _to_bool(value, default_value):
    if isinstance(value, bool):
        return value

    if isinstance(value, _INTEGER_TYPES):
        return value != 0

    if value is None:
        return default_value

    try:
        text = str(value).strip().lower()
    except Exception:
        return default_value

    if text in ("1", "true", "yes", "on", "enabled"):
        return True
    if text in ("0", "false", "no", "off", "disabled"):
        return False

    return default_value


def _safe_call(default_value, fn, *args):
    try:
        return fn(*args)
    except Exception:
        return default_value


def _lower_text(value):
    try:
        return str(value).strip().lower()
    except Exception:
        return ""


def _serial_hex(serial_value):
    try:
        return hex(int(serial_value))
    except Exception:
        return "0x0"


def _copy_dict(source_dict):
    copied = {}
    if not isinstance(source_dict, dict):
        return copied

    for key in source_dict.keys():
        copied[key] = source_dict[key]

    return copied


def _destination_text(destination):
    return "{0},{1},{2}".format(destination[0], destination[1], destination[2])


def _normalize_destination(destination):
    if isinstance(destination, tuple) or isinstance(destination, list):
        if len(destination) >= 3:
            return (
                _to_int(destination[0], 0),
                _to_int(destination[1], 0),
                _to_int(destination[2], 0)
            )
        if len(destination) == 2:
            return (
                _to_int(destination[0], 0),
                _to_int(destination[1], 0),
                _safe_call(0, Z, "self")
            )

    if isinstance(destination, dict):
        if "x" not in destination or "y" not in destination:
            return None

        return (
            _to_int(destination.get("x", 0), 0),
            _to_int(destination.get("y", 0), 0),
            _to_int(destination.get("z", 0), 0)
        )

    return None


def _merge_options(pathing_defaults, route_overrides, within_distance_override):
    merged = _copy_dict(pathing_defaults)

    if isinstance(route_overrides, dict):
        for key in route_overrides.keys():
            merged[key] = route_overrides[key]

    if within_distance_override is not None:
        merged["within_distance"] = _to_int(within_distance_override, _to_int(merged.get("within_distance", 1), 1))

    return merged


def _scan_nearby_mobiles(state_name, search_range, max_scans):
    global _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED

    rows = []
    observed_name_set = {}

    if search_range < 1:
        search_range = 1
    if max_scans < 1:
        max_scans = 1

    try:
        from Assistant import Engine
    except Exception as ex:
        if not _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED:
            _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED = True
            Telemetry.warn(state_name, "Shop goal mobile scan unavailable", {
                "reason": "engine_import_failed",
                "error": str(ex)
            })
        return {
            "rows": rows,
            "observed_names": []
        }

    player = None
    try:
        player = Engine.Player
    except Exception:
        player = None

    if player is None:
        if not _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED:
            _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED = True
            Telemetry.warn(state_name, "Shop goal mobile scan unavailable", {
                "reason": "player_unavailable"
            })
        return {
            "rows": rows,
            "observed_names": []
        }

    mobiles = None
    try:
        mobiles = Engine.Mobiles
    except Exception as ex:
        mobiles = None
        if not _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED:
            _SHOP_ENGINE_SCAN_UNAVAILABLE_LOGGED = True
            Telemetry.warn(state_name, "Shop goal mobile scan unavailable", {
                "reason": "mobiles_unavailable",
                "error": str(ex)
            })

    if mobiles is None:
        return {
            "rows": rows,
            "observed_names": []
        }

    player_serial = _to_int(getattr(player, "Serial", 0), 0)
    px = _to_int(getattr(player, "X", 0), 0)
    py = _to_int(getattr(player, "Y", 0), 0)
    pz = _to_int(getattr(player, "Z", 0), 0)

    seen_serials = {}
    for mobile in mobiles:
        if len(rows) >= max_scans:
            break

        if mobile is None:
            continue

        serial_value = _to_int(getattr(mobile, "Serial", 0), 0)
        if serial_value <= 0:
            continue
        if serial_value == player_serial:
            continue
        if serial_value in seen_serials:
            continue

        x_value = _to_int(getattr(mobile, "X", 0), 0)
        y_value = _to_int(getattr(mobile, "Y", 0), 0)
        z_value = _to_int(getattr(mobile, "Z", 0), 0)
        distance_value = max(abs(x_value - px), abs(y_value - py), abs(z_value - pz))
        if distance_value > search_range:
            continue

        seen_serials[serial_value] = True

        name_text = ""
        try:
            name_text = str(getattr(mobile, "Name", ""))
        except Exception:
            name_text = ""

        lowered_name = _lower_text(name_text)
        if len(lowered_name) > 0:
            observed_name_set[lowered_name] = True

        rows.append({
            "serial": serial_value,
            "serial_hex": _serial_hex(serial_value),
            "name": name_text,
            "x": x_value,
            "y": y_value,
            "z": z_value,
            "distance": distance_value,
            "source": "engine_mobiles"
        })

    rows.sort(key=lambda row: _to_int(row.get("distance", 9999), 9999))

    observed_names = []
    for name_key in observed_name_set.keys():
        observed_names.append(name_key)

    observed_names.sort()

    return {
        "rows": rows,
        "observed_names": observed_names
    }


def _normalize_point_tuple(point_value):
    if isinstance(point_value, tuple) or isinstance(point_value, list):
        if len(point_value) >= 3:
            return (
                _to_int(point_value[0], 0),
                _to_int(point_value[1], 0),
                _to_int(point_value[2], 0)
            )
        if len(point_value) == 2:
            return (
                _to_int(point_value[0], 0),
                _to_int(point_value[1], 0),
                _safe_call(0, Z, "self")
            )

    return None


def _dedupe_points(points):
    deduped = []
    seen = {}

    idx = 0
    while idx < len(points):
        point = _normalize_point_tuple(points[idx])
        idx += 1

        if point is None:
            continue

        key = "{0}:{1}:{2}".format(point[0], point[1], point[2])
        if key in seen:
            continue

        seen[key] = True
        deduped.append(point)

    return deduped


def _scan_vendor_matches(state_name, vendor_tokens, search_range, max_scans):
    scan_result = _scan_nearby_mobiles(state_name, search_range, max_scans)
    rows = scan_result.get("rows", [])

    normalized_tokens = []
    token_seen = {}
    token_index = 0
    while token_index < len(vendor_tokens):
        token = _lower_text(vendor_tokens[token_index])
        token_index += 1

        if len(token) <= 0:
            continue
        if token in token_seen:
            continue

        token_seen[token] = True
        normalized_tokens.append(token)

    matches = []
    token_hits = {}
    row_index = 0
    while row_index < len(rows):
        row = rows[row_index]
        row_index += 1

        name_text = _lower_text(row.get("name", ""))
        if len(name_text) <= 0:
            continue

        if len(normalized_tokens) <= 0:
            matches.append(row)
            continue

        token_idx = 0
        while token_idx < len(normalized_tokens):
            token = normalized_tokens[token_idx]
            token_idx += 1

            if token in name_text:
                token_hits[token] = True
                matches.append(row)
                break

    matches.sort(key=lambda row: _to_int(row.get("distance", 9999), 9999))

    token_hit_list = []
    for token_key in token_hits.keys():
        token_hit_list.append(token_key)

    token_hit_list.sort()

    return {
        "matches": matches,
        "observed_names": scan_result.get("observed_names", []),
        "normalized_tokens": normalized_tokens,
        "token_hits": token_hit_list,
        "scanned_count": len(rows)
    }


def _build_shop_goal_options(route_options):
    options = _copy_dict(route_options)

    options["within_distance"] = _to_int(route_options.get("shop_goal_vendor_within_distance", 2), 2)
    options["max_attempts"] = _to_int(route_options.get("shop_goal_max_attempts", 30), 30)
    options["max_ms"] = _to_int(route_options.get("shop_goal_max_ms", 30000), 30000)

    if _to_int(options.get("max_regression_from_best", 4), 4) < 2:
        options["max_regression_from_best"] = 2
    if _to_int(options.get("no_best_progress_tolerance", 20), 20) < 10:
        options["no_best_progress_tolerance"] = 10

    return options


def _build_shop_goal_exit_options(route_options):
    options = _copy_dict(route_options)

    options["within_distance"] = _to_int(route_options.get("shop_goal_exit_within_distance", 2), 2)
    options["max_attempts"] = _to_int(route_options.get("shop_goal_exit_max_attempts", route_options.get("shop_goal_max_attempts", 30)), 30)
    options["max_ms"] = _to_int(route_options.get("shop_goal_exit_max_ms", route_options.get("shop_goal_max_ms", 30000)), 30000)

    if _to_int(options.get("max_regression_from_best", 4), 4) < 2:
        options["max_regression_from_best"] = 2
    if _to_int(options.get("no_best_progress_tolerance", 20), 20) < 10:
        options["no_best_progress_tolerance"] = 10

    return options


def _run_shop_visit_goal(ctx, state_name, route_row, route_options):
    goal_enabled = _to_bool(route_options.get("shop_goal_enabled", False), False)
    if not goal_enabled:
        return {
            "enabled": False,
            "passed": True,
            "reason": "disabled",
            "observed_names": "",
            "matched_vendor": "",
            "matched_vendor_serial": "",
            "anchors_attempted": 0
        }

    goal_name = str(route_options.get("shop_goal_name", route_row.get("name", "shop_goal")))
    vendor_tokens = route_options.get("shop_goal_vendor_tokens", [])
    anchor_points = _dedupe_points(route_options.get("shop_goal_vendor_anchor_points", []))
    scan_range = _to_int(route_options.get("shop_goal_vendor_scan_range", 12), 12)
    max_scans = _to_int(route_options.get("shop_goal_vendor_max_scans", 16), 16)
    vendor_required = _to_bool(route_options.get("shop_goal_vendor_required", True), True)
    require_all_tokens = _to_bool(route_options.get("shop_goal_require_all_vendor_tokens", True), True)
    require_all_anchors = _to_bool(route_options.get("shop_goal_require_all_anchors", True), True)
    exit_required = _to_bool(route_options.get("shop_goal_exit_required", True), True)

    if scan_range < 1:
        scan_range = 1
    if max_scans < 1:
        max_scans = 1

    Telemetry.info(state_name, "Shop goal preconditions", {
        "shop_goal_name": goal_name,
        "vendor_token_count": len(vendor_tokens),
        "anchor_count": len(anchor_points),
        "scan_range": scan_range,
        "max_scans": max_scans,
        "vendor_required": vendor_required,
        "require_all_tokens": require_all_tokens,
        "require_all_anchors": require_all_anchors,
        "exit_required": exit_required
    })

    goal_options = _build_shop_goal_options(route_options)
    exit_options = _build_shop_goal_exit_options(route_options)
    goal_within_distance = _to_int(goal_options.get("within_distance", 2), 2)
    exit_within_distance = _to_int(exit_options.get("within_distance", 2), 2)

    initial_scan = _scan_vendor_matches(state_name, vendor_tokens, scan_range, max_scans)
    observed_name_set = {}
    token_hit_set = {}
    matched_vendor_lookup = {}

    def _merge_shop_scan(scan_row):
        match_rows = scan_row.get("matches", [])
        observed_rows = scan_row.get("observed_names", [])
        token_rows = scan_row.get("token_hits", [])

        idx = 0
        while idx < len(observed_rows):
            observed_name_set[_lower_text(observed_rows[idx])] = True
            idx += 1

        idx = 0
        while idx < len(token_rows):
            token_hit_set[_lower_text(token_rows[idx])] = True
            idx += 1

        idx = 0
        while idx < len(match_rows):
            row = match_rows[idx]
            idx += 1

            serial_value = _to_int(row.get("serial", 0), 0)
            if serial_value <= 0:
                continue

            serial_key = str(serial_value)
            if serial_key not in matched_vendor_lookup:
                matched_vendor_lookup[serial_key] = row

    _merge_shop_scan(initial_scan)

    if len(anchor_points) <= 0:
        initial_matches = initial_scan.get("matches", [])
        idx = 0
        while idx < len(initial_matches):
            row = initial_matches[idx]
            idx += 1

            point = _normalize_point_tuple((row.get("x", 0), row.get("y", 0), row.get("z", 0)))
            if point is None:
                continue
            anchor_points.append(point)

        anchor_points = _dedupe_points(anchor_points)

    anchors_attempted = 0
    anchors_reached = 0

    anchor_index = 0
    while anchor_index < len(anchor_points):
        anchor = anchor_points[anchor_index]
        anchor_index += 1
        anchors_attempted += 1

        Telemetry.info(state_name, "Shop goal anchor move", {
            "shop_goal_name": goal_name,
            "anchor_index": anchor_index,
            "anchor_total": len(anchor_points),
            "anchor_point": anchor
        })

        anchor_nav = navigate_to_coordinate(ctx, state_name, anchor, goal_options)
        anchor_reached = _to_bool(anchor_nav.get("success", False), False) and _to_int(anchor_nav.get("final_distance", 9999), 9999) <= goal_within_distance
        if anchor_reached:
            anchors_reached += 1

        post_scan = _scan_vendor_matches(state_name, vendor_tokens, scan_range, max_scans)
        _merge_shop_scan(post_scan)

    normalized_tokens = initial_scan.get("normalized_tokens", [])
    token_total = len(normalized_tokens)
    token_hits = 0
    token_index = 0
    while token_index < len(normalized_tokens):
        token = _lower_text(normalized_tokens[token_index])
        token_index += 1

        if token in token_hit_set:
            token_hits += 1

    token_requirement_pass = True
    if vendor_required and token_total > 0:
        if require_all_tokens:
            token_requirement_pass = token_hits >= token_total
        else:
            token_requirement_pass = token_hits >= 1

    anchor_requirement_pass = True
    if vendor_required and len(anchor_points) > 0:
        if require_all_anchors:
            anchor_requirement_pass = anchors_reached >= len(anchor_points)
        else:
            anchor_requirement_pass = anchors_reached >= 1

    observed_names = []
    for observed_name in observed_name_set.keys():
        if len(observed_name) > 0:
            observed_names.append(observed_name)
    observed_names.sort()
    observed_names_text = "|".join(observed_names)

    matched_vendor = ""
    matched_vendor_serial = ""
    if len(matched_vendor_lookup) > 0:
        nearest_match = None
        for match_key in matched_vendor_lookup.keys():
            row = matched_vendor_lookup[match_key]
            if nearest_match is None:
                nearest_match = row
                continue

            if _to_int(row.get("distance", 9999), 9999) < _to_int(nearest_match.get("distance", 9999), 9999):
                nearest_match = row

        if nearest_match is not None:
            matched_vendor = str(nearest_match.get("name", ""))
            matched_vendor_serial = str(nearest_match.get("serial_hex", _serial_hex(nearest_match.get("serial", 0))))

    vendor_presence_pass = True
    if vendor_required:
        vendor_presence_pass = (len(matched_vendor_lookup) > 0) or (token_hits > 0)

    egress_destination = _normalize_destination(route_options.get("shop_goal_exit_point", route_row.get("destination")))
    if egress_destination is None:
        egress_destination = _normalize_destination(route_row.get("destination"))

    egress_reached = not exit_required
    egress_stop_reason = "not_required"

    if egress_destination is not None:
        Telemetry.info(state_name, "Shop goal egress move", {
            "shop_goal_name": goal_name,
            "egress_destination": egress_destination
        })

        egress_nav = navigate_to_coordinate(ctx, state_name, egress_destination, exit_options)
        egress_stop_reason = str(egress_nav.get("stop_reason", "unknown"))
        egress_reached = _to_bool(egress_nav.get("success", False), False) and _to_int(egress_nav.get("final_distance", 9999), 9999) <= exit_within_distance
    elif exit_required:
        egress_stop_reason = "exit_point_unavailable"
        egress_reached = False

    if not vendor_presence_pass:
        return {
            "enabled": True,
            "passed": False,
            "reason": "vendor_not_observed",
            "observed_names": observed_names_text,
            "matched_vendor": matched_vendor,
            "matched_vendor_serial": matched_vendor_serial,
            "anchors_attempted": anchors_attempted
        }

    if not token_requirement_pass:
        return {
            "enabled": True,
            "passed": False,
            "reason": "vendor_tokens_missing_{0}_{1}".format(token_hits, token_total),
            "observed_names": observed_names_text,
            "matched_vendor": matched_vendor,
            "matched_vendor_serial": matched_vendor_serial,
            "anchors_attempted": anchors_attempted
        }

    if not anchor_requirement_pass:
        return {
            "enabled": True,
            "passed": False,
            "reason": "anchor_reach_failed_{0}_{1}".format(anchors_reached, len(anchor_points)),
            "observed_names": observed_names_text,
            "matched_vendor": matched_vendor,
            "matched_vendor_serial": matched_vendor_serial,
            "anchors_attempted": anchors_attempted
        }

    if exit_required and not egress_reached:
        return {
            "enabled": True,
            "passed": False,
            "reason": "egress_failed_{0}".format(egress_stop_reason),
            "observed_names": observed_names_text,
            "matched_vendor": matched_vendor,
            "matched_vendor_serial": matched_vendor_serial,
            "anchors_attempted": anchors_attempted
        }

    return {
        "enabled": True,
        "passed": True,
        "reason": "vendor_and_egress_complete",
        "observed_names": observed_names_text,
        "matched_vendor": matched_vendor,
        "matched_vendor_serial": matched_vendor_serial,
        "anchors_attempted": anchors_attempted
    }


def _route_copy_with_stage(route_row, stage_name):
    copied = _copy_dict(route_row)
    copied["stage_name"] = stage_name
    return copied


def _normalize_fixed_routes(config):
    harness_cfg = config.get("test_harness", {})
    pathing_defaults = _copy_dict(config.get("pathing_defaults", {}))
    fixed_routes = harness_cfg.get("fixed_routes", [])

    lookup = {}
    errors = []

    index = 0
    while index < len(fixed_routes):
        raw_route = fixed_routes[index]
        index += 1

        if not isinstance(raw_route, dict):
            errors.append("fixed_route_not_dict_{0}".format(index))
            continue

        route_name = str(raw_route.get("name", "fixed_route_{0}".format(index)))
        destination = _normalize_destination(raw_route.get("destination"))

        if destination is None:
            errors.append("fixed_route_invalid_destination_{0}".format(route_name))
            continue

        within_distance = raw_route.get("within_distance", pathing_defaults.get("within_distance", 1))
        options = _merge_options(pathing_defaults, raw_route.get("options", {}), within_distance)

        route_row = {
            "name": route_name,
            "destination": destination,
            "expected_reachable": _to_bool(raw_route.get("expected_reachable", True), True),
            "category": str(raw_route.get("category", "unspecified")),
            "options": options,
            "source": "fixed"
        }

        if "target_name" in raw_route:
            route_row["target_name"] = raw_route.get("target_name")
        if "target_area" in raw_route:
            route_row["target_area"] = raw_route.get("target_area")
        if "target_class" in raw_route:
            route_row["target_class"] = raw_route.get("target_class")
        if "goal_type" in raw_route:
            route_row["goal_type"] = str(raw_route.get("goal_type", "none"))

        lookup[route_name] = route_row

    return (lookup, errors)


def _build_random_batch_routes(config, stage_name):
    harness_cfg = config.get("test_harness", {})
    random_cfg = harness_cfg.get("random_batch", {})
    pathing_defaults = _copy_dict(config.get("pathing_defaults", {}))

    if not _to_bool(random_cfg.get("enabled", False), False):
        return []

    sample_count = _to_int(random_cfg.get("sample_count", 0), 0)
    if sample_count <= 0:
        return []

    x_min = _to_int(random_cfg.get("x_min", 2940), 2940)
    x_max = _to_int(random_cfg.get("x_max", 3135), 3135)
    y_min = _to_int(random_cfg.get("y_min", 1000), 1000)
    y_max = _to_int(random_cfg.get("y_max", 1165), 1165)
    default_z = _to_int(random_cfg.get("default_z", 0), 0)

    if x_max < x_min:
        x_max = x_min
    if y_max < y_min:
        y_max = y_min

    seed = _to_int(random_cfg.get("seed", 1337), 1337)
    expected_reachable = _to_bool(random_cfg.get("expected_reachable", True), True)
    within_distance = random_cfg.get("within_distance", pathing_defaults.get("within_distance", 1))
    random_options = random_cfg.get("options", {})

    rng = random.Random(seed)
    rows = []

    index = 0
    while index < sample_count:
        index += 1

        x_value = rng.randint(x_min, x_max)
        y_value = rng.randint(y_min, y_max)

        destination = (x_value, y_value, default_z)
        options = _merge_options(pathing_defaults, random_options, within_distance)

        rows.append({
            "name": "random_batch_{0:02d}".format(index),
            "destination": destination,
            "expected_reachable": expected_reachable,
            "category": "random",
            "options": options,
            "source": "random_batch",
            "stage_name": stage_name,
            "random_seed": seed
        })

    return rows


def _build_execution_plan(config):
    harness_cfg = config.get("test_harness", {})
    stages = harness_cfg.get("stages", [])

    fixed_lookup, fixed_errors = _normalize_fixed_routes(config)

    plan = []
    errors = []

    for fixed_error in fixed_errors:
        errors.append(fixed_error)

    stage_index = 0
    while stage_index < len(stages):
        stage = stages[stage_index]
        stage_index += 1

        if not isinstance(stage, dict):
            errors.append("stage_not_dict_{0}".format(stage_index))
            continue

        stage_name = str(stage.get("name", "stage_{0}".format(stage_index)))
        enabled = _to_bool(stage.get("enabled", True), True)

        if not enabled:
            Telemetry.info("BOOTSTRAP", "Stage skipped by policy", {
                "stage_name": stage_name,
                "enabled": enabled
            })
            continue

        mode = str(stage.get("mode", "fixed")).strip().lower()
        if mode == "random_batch":
            random_rows = _build_random_batch_routes(config, stage_name)
            if len(random_rows) <= 0:
                errors.append("random_batch_empty_{0}".format(stage_name))
                continue

            row_index = 0
            while row_index < len(random_rows):
                plan.append(random_rows[row_index])
                row_index += 1

            continue

        route_names = stage.get("route_names", [])
        if len(route_names) <= 0:
            errors.append("stage_route_names_empty_{0}".format(stage_name))
            continue

        route_index = 0
        while route_index < len(route_names):
            route_name = str(route_names[route_index])
            route_index += 1

            if route_name not in fixed_lookup:
                errors.append("route_missing_{0}_{1}".format(stage_name, route_name))
                continue

            plan.append(_route_copy_with_stage(fixed_lookup[route_name], stage_name))

    return (plan, errors)


def _stage_key(route_row):
    return str(route_row.get("stage_name", "unknown_stage"))


def _append_stage_counter(store, stage_name, key_name):
    if stage_name not in store:
        store[stage_name] = {
            "total": 0,
            "pass": 0,
            "fail": 0,
            "expected_reachable_total": 0,
            "expected_reachable_pass": 0,
            "negative_total": 0,
            "negative_pass": 0
        }

    stage_bucket = store[stage_name]
    stage_bucket[key_name] = stage_bucket.get(key_name, 0) + 1


def _evaluate_route_result(route_row, result_row, allowed_negative_stop_reasons):
    expected_reachable = _to_bool(route_row.get("expected_reachable", True), True)
    success = _to_bool(result_row.get("success", False), False)
    stop_reason = str(result_row.get("stop_reason", ""))

    if expected_reachable:
        if success:
            return (True, "reachable_success")
        return (False, "reachable_failed_{0}".format(stop_reason))

    if not success:
        if stop_reason in allowed_negative_stop_reasons:
            return (True, "negative_expected_failure")
        return (False, "negative_unexpected_stop_reason_{0}".format(stop_reason))

    return (False, "negative_unexpected_success")


class BootstrapState(State):
    key = "BOOTSTRAP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering BOOTSTRAP")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            ctx.stop_cause = "player_dead"
            return "FATAL_STOP"

        plan, errors = _build_execution_plan(ctx.config)

        if len(errors) > 0:
            ctx.fail(self.key, "Harness bootstrap validation failed", {
                "errors": "|".join(errors)
            })
            ctx.stop_cause = "bootstrap_validation_failed"
            return "FATAL_STOP"

        if len(plan) <= 0:
            ctx.fail(self.key, "No routes available after stage policy resolution")
            ctx.stop_cause = "empty_execution_plan"
            return "FATAL_STOP"

        ctx.route_plan = plan
        ctx.route_index = 0
        ctx.route_reports = []

        generated_summary = ctx.config.get("test_harness", {}).get("generated_target_summary", {})
        if isinstance(generated_summary, dict) and len(generated_summary) > 0:
            Telemetry.info(self.key, "Generated target summary", generated_summary)

        Telemetry.info(self.key, "Bootstrap ready", {
            "route_count": len(plan),
            "stage_count": len(ctx.config.get("test_harness", {}).get("stages", [])),
            "random_batch_enabled": _to_bool(ctx.config.get("test_harness", {}).get("random_batch", {}).get("enabled", False), False)
        })

        return "RUN_ROUTE"


class RunRouteState(State):
    key = "RUN_ROUTE"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering RUN_ROUTE")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            ctx.stop_cause = "player_dead"
            return "FATAL_STOP"

        plan = getattr(ctx, "route_plan", [])
        route_index = _to_int(getattr(ctx, "route_index", 0), 0)

        if route_index >= len(plan):
            return "FINAL_SUMMARY"

        route_row = plan[route_index]
        route_name = str(route_row.get("name", "route_{0}".format(route_index + 1)))
        stage_name = _stage_key(route_row)
        destination = route_row.get("destination", (0, 0, 0))
        options = _copy_dict(route_row.get("options", {}))

        Telemetry.info(self.key, "Action preconditions", {
            "route_index": route_index + 1,
            "route_total": len(plan),
            "route_name": route_name,
            "stage_name": stage_name,
            "category": route_row.get("category", "unspecified"),
            "source": route_row.get("source", "fixed"),
            "expected_reachable": route_row.get("expected_reachable", True),
            "destination": destination,
            "within_distance": options.get("within_distance", 1),
            "max_attempts": options.get("max_attempts", 0),
            "max_ms": options.get("max_ms", 0)
        })

        result_row = navigate_to_coordinate(ctx, self.key, destination, options)

        harness_cfg = ctx.config.get("test_harness", {})
        allowed_negative_stop_reasons = harness_cfg.get("allowed_negative_stop_reasons", [])

        passed, pass_reason = _evaluate_route_result(route_row, result_row, allowed_negative_stop_reasons)
        goal_type = str(route_row.get("goal_type", "none"))
        goal_enabled = False
        goal_passed = True
        goal_reason = "not_applicable"
        goal_vendor = ""
        goal_vendor_serial = ""
        goal_observed_names = ""
        goal_anchors_attempted = 0

        if _to_bool(options.get("shop_goal_enabled", False), False):
            goal_enabled = True
            if passed:
                goal_result = _run_shop_visit_goal(ctx, self.key, route_row, options)
                goal_enabled = _to_bool(goal_result.get("enabled", False), False)
                goal_passed = _to_bool(goal_result.get("passed", False), False)
                goal_reason = str(goal_result.get("reason", "unknown"))
                goal_vendor = str(goal_result.get("matched_vendor", ""))
                goal_vendor_serial = str(goal_result.get("matched_vendor_serial", ""))
                goal_observed_names = str(goal_result.get("observed_names", ""))
                goal_anchors_attempted = _to_int(goal_result.get("anchors_attempted", 0), 0)

                if goal_enabled and not goal_passed:
                    passed = False
                    pass_reason = "shop_goal_failed_{0}".format(goal_reason)
            else:
                goal_passed = False
                goal_reason = "skipped_route_failed"

        evidence = result_row.get("evidence", {})
        report_row = {
            "route_index": route_index + 1,
            "stage_name": stage_name,
            "route_name": route_name,
            "category": route_row.get("category", "unspecified"),
            "source": route_row.get("source", "fixed"),
            "destination": _destination_text(destination),
            "expected_reachable": route_row.get("expected_reachable", True),
            "success": result_row.get("success", False),
            "passed": passed,
            "pass_reason": pass_reason,
            "stop_reason": result_row.get("stop_reason", ""),
            "attempts": result_row.get("attempts", 0),
            "elapsed_ms": result_row.get("elapsed_ms", 0),
            "final_distance": result_row.get("final_distance", -1),
            "best_distance": evidence.get("best_distance", -1),
            "candidate_order_last": evidence.get("candidate_order_last", ""),
            "candidate_results_last": evidence.get("candidate_results_last", ""),
            "goal_type": goal_type,
            "goal_enabled": goal_enabled,
            "goal_passed": goal_passed,
            "goal_reason": goal_reason,
            "goal_vendor": goal_vendor,
            "goal_vendor_serial": goal_vendor_serial,
            "goal_observed_names": goal_observed_names,
            "goal_anchors_attempted": goal_anchors_attempted
        }

        ctx.route_reports.append(report_row)

        log_fn = Telemetry.info
        log_message = "Route test passed"
        if not passed:
            log_fn = Telemetry.warn
            log_message = "Route test failed"

        log_fn(self.key, log_message, {
            "route_name": route_name,
            "stage_name": stage_name,
            "expected_reachable": report_row["expected_reachable"],
            "success": report_row["success"],
            "passed": report_row["passed"],
            "pass_reason": report_row["pass_reason"],
            "stop_reason": report_row["stop_reason"],
            "attempts": report_row["attempts"],
            "elapsed_ms": report_row["elapsed_ms"],
            "final_distance": report_row["final_distance"],
            "goal_type": report_row["goal_type"],
            "goal_enabled": report_row["goal_enabled"],
            "goal_passed": report_row["goal_passed"],
            "goal_reason": report_row["goal_reason"],
            "goal_vendor": report_row["goal_vendor"],
            "goal_vendor_serial": report_row["goal_vendor_serial"],
            "goal_anchors_attempted": report_row["goal_anchors_attempted"]
        })

        ctx.route_index = route_index + 1

        pause_between_routes = _to_int(ctx.config.get("runtime", {}).get("pause_between_routes_ms", 600), 600)
        if pause_between_routes > 0:
            try:
                Pause(pause_between_routes)
            except Exception as ex:
                ctx.fail(self.key, "Pause command unavailable", {
                    "milliseconds": pause_between_routes,
                    "exception": str(ex)
                })
                ctx.stop_cause = "pause_unavailable"
                return "FATAL_STOP"

        return "RUN_ROUTE"


class FinalSummaryState(State):
    key = "FINAL_SUMMARY"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering FINAL_SUMMARY")

    def tick(self, ctx):
        reports = getattr(ctx, "route_reports", [])
        target_percent = _to_int(ctx.config.get("test_harness", {}).get("success_rate_target_percent", 90), 90)

        total_routes = len(reports)
        pass_count = 0
        fail_count = 0
        reachable_total = 0
        reachable_pass = 0
        negative_total = 0
        negative_pass = 0
        deterministic_failures = 0

        per_stage = {}

        index = 0
        while index < len(reports):
            row = reports[index]
            index += 1

            stage_name = str(row.get("stage_name", "unknown_stage"))
            _append_stage_counter(per_stage, stage_name, "total")

            if _to_bool(row.get("passed", False), False):
                pass_count += 1
                _append_stage_counter(per_stage, stage_name, "pass")
            else:
                fail_count += 1
                _append_stage_counter(per_stage, stage_name, "fail")

            expected_reachable = _to_bool(row.get("expected_reachable", True), True)
            if expected_reachable:
                reachable_total += 1
                _append_stage_counter(per_stage, stage_name, "expected_reachable_total")
                if _to_bool(row.get("passed", False), False):
                    reachable_pass += 1
                    _append_stage_counter(per_stage, stage_name, "expected_reachable_pass")
            else:
                negative_total += 1
                _append_stage_counter(per_stage, stage_name, "negative_total")
                if _to_bool(row.get("passed", False), False):
                    negative_pass += 1
                    _append_stage_counter(per_stage, stage_name, "negative_pass")

            stop_reason = str(row.get("stop_reason", ""))
            if len(stop_reason) <= 0:
                deterministic_failures += 1

        reachable_success_rate = 0.0
        if reachable_total > 0:
            reachable_success_rate = (float(reachable_pass) * 100.0) / float(reachable_total)

        deterministic_stop_ok = deterministic_failures == 0
        baseline_ready = reachable_success_rate >= float(target_percent) and deterministic_stop_ok

        summary_row = {
            "route_total": total_routes,
            "route_pass": pass_count,
            "route_fail": fail_count,
            "reachable_total": reachable_total,
            "reachable_pass": reachable_pass,
            "reachable_success_rate": "{0:.2f}".format(reachable_success_rate),
            "negative_total": negative_total,
            "negative_pass": negative_pass,
            "target_percent": target_percent,
            "deterministic_stop_ok": deterministic_stop_ok,
            "deterministic_stop_failures": deterministic_failures,
            "baseline_ready": baseline_ready,
            "per_stage": per_stage
        }

        ctx.final_summary = summary_row

        Telemetry.info(self.key, "Britain pathing RnD summary", {
            "route_total": summary_row["route_total"],
            "route_pass": summary_row["route_pass"],
            "route_fail": summary_row["route_fail"],
            "reachable_success_rate": summary_row["reachable_success_rate"],
            "target_percent": summary_row["target_percent"],
            "deterministic_stop_ok": summary_row["deterministic_stop_ok"],
            "baseline_ready": summary_row["baseline_ready"]
        })

        summary_limit = 60
        row_index = 0
        while row_index < len(reports):
            row = reports[row_index]
            row_index += 1
            if row_index > summary_limit:
                Telemetry.info(self.key, "Route summary truncated", {
                    "shown": summary_limit,
                    "total": len(reports)
                })
                break

            Telemetry.info(self.key, "Route summary row", {
                "idx": row.get("route_index", row_index),
                "stage": row.get("stage_name", "unknown_stage"),
                "route": row.get("route_name", "unknown_route"),
                "expected_reachable": row.get("expected_reachable", True),
                "passed": row.get("passed", False),
                "stop_reason": row.get("stop_reason", ""),
                "attempts": row.get("attempts", 0),
                "elapsed_ms": row.get("elapsed_ms", 0),
                "final_distance": row.get("final_distance", -1)
            })

        ctx.stop_cause = "harness_complete"
        return "COMPLETE_STOP"


class CompleteStopState(State):
    key = "COMPLETE_STOP"

    def enter(self, ctx):
        summary = getattr(ctx, "final_summary", {})
        Telemetry.info(self.key, "Britain pathing RnD complete", {
            "stop_cause": getattr(ctx, "stop_cause", "harness_complete"),
            "route_total": summary.get("route_total", 0),
            "route_pass": summary.get("route_pass", 0),
            "route_fail": summary.get("route_fail", 0),
            "reachable_success_rate": summary.get("reachable_success_rate", "0.00"),
            "baseline_ready": summary.get("baseline_ready", False)
        })

        ctx.stop("Britain pathing RnD harness complete")
        Stop()

    def tick(self, ctx):
        return None


class FatalStopState(State):
    key = "FATAL_STOP"

    def enter(self, ctx):
        Telemetry.fatal(self.key, "Entering FATAL_STOP", {
            "last_failed_step": ctx.last_failed_state,
            "failure_reason": ctx.last_error,
            "stop_cause": getattr(ctx, "stop_cause", "fatal_stop"),
            "tick_count": ctx.tick_count
        })

        try:
            CancelTarget()
        except Exception:
            pass

        try:
            WarMode("off")
        except Exception:
            pass

        ctx.stop("Britain pathing RnD harness fatal stop")
        Stop()

    def tick(self, ctx):
        return None


def _build_states():
    return {
        "BOOTSTRAP": BootstrapState(),
        "RUN_ROUTE": RunRouteState(),
        "FINAL_SUMMARY": FinalSummaryState(),
        "COMPLETE_STOP": CompleteStopState(),
        "FATAL_STOP": FatalStopState()
    }


def run_britain_pathing_rd_controller(config):
    published_api = publish_known_ca_api(globals())
    Telemetry.debug("MAIN", "Published ClassicAssist API symbols", {"count": published_api})
    Telemetry.info("MAIN", "Starting BritainPathingRnDController")

    ctx = BotContext(config)
    states = _build_states()

    machine = StateMachine(ctx, states, "BOOTSTRAP")
    machine.run()

    Telemetry.info("MAIN", "BritainPathingRnDController finished", {
        "tick_count": ctx.tick_count,
        "transition_count": ctx.transition_count,
        "last_error_state": ctx.last_error_state,
        "last_error": ctx.last_error,
        "stop_cause": getattr(ctx, "stop_cause", "")
    })


run_britain_pathing_rd_controller(BOT_CONFIG)

