# Name: Confictura Shared Pathing Module
# Description: Provides reusable segmented same-map coordinate navigation with deterministic stop reasons.
# Author: ChatGPT Codex
# Shard: Confictura

import time

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.safe_api import safe_pathfind
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


try:
    _INTEGER_TYPES = (int, long)
except Exception:
    _INTEGER_TYPES = (int,)

_PATHFINDING_UNAVAILABLE_LOGGED = False


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


def _ctx_fail(ctx, state_name, reason, details):
    if ctx is not None and hasattr(ctx, "fail"):
        ctx.fail(state_name, reason, details)
        return

    Telemetry.error(state_name, reason, details)


def _distance_between(point_a, point_b):
    ax = _to_int(point_a[0], 0)
    ay = _to_int(point_a[1], 0)
    az = _to_int(point_a[2], 0)

    bx = _to_int(point_b[0], 0)
    by = _to_int(point_b[1], 0)
    bz = _to_int(point_b[2], 0)

    return max(abs(ax - bx), abs(ay - by), abs(az - bz))


def _snapshot_self():
    return {
        "map": _safe_call(-1, Map),
        "x": _safe_call(0, X, "self"),
        "y": _safe_call(0, Y, "self"),
        "z": _safe_call(0, Z, "self")
    }


def _point_from_snapshot(snapshot):
    return (
        _to_int(snapshot.get("x", 0), 0),
        _to_int(snapshot.get("y", 0), 0),
        _to_int(snapshot.get("z", 0), 0)
    )


def _normalize_destination(destination):
    if isinstance(destination, dict):
        if "x" not in destination or "y" not in destination:
            return None
        return (
            _to_int(destination.get("x", 0), 0),
            _to_int(destination.get("y", 0), 0),
            _to_int(destination.get("z", 0), 0)
        )

    if isinstance(destination, tuple) or isinstance(destination, list):
        if len(destination) < 2:
            return None
        if len(destination) >= 3:
            return (
                _to_int(destination[0], 0),
                _to_int(destination[1], 0),
                _to_int(destination[2], 0)
            )
        return (
            _to_int(destination[0], 0),
            _to_int(destination[1], 0),
            _safe_call(0, Z, "self")
        )

    return None


def _normalize_options(options):
    if options is None:
        options = {}

    normalized = {
        "within_distance": _to_int(options.get("within_distance", 1), 1),
        "min_action_delay_ms": _to_int(options.get("min_action_delay_ms", 600), 600),
        "settle_ms": _to_int(options.get("settle_ms", 600), 600),
        "max_attempts": _to_int(options.get("max_attempts", 80), 80),
        "max_ms": _to_int(options.get("max_ms", 90000), 90000),
        "min_progress": _to_int(options.get("min_progress", 1), 1),
        "max_hop_distance": _to_int(options.get("max_hop_distance", 12), 12),
        "min_hop_distance": _to_int(options.get("min_hop_distance", 2), 2),
        "hop_backoff_step": _to_int(options.get("hop_backoff_step", 2), 2),
        "hop_recover_step": _to_int(options.get("hop_recover_step", 1), 1),
        "stall_tolerance": _to_int(options.get("stall_tolerance", 4), 4),
        "stall_pause_ms": _to_int(options.get("stall_pause_ms", 600), 600),
        "lateral_step": _to_int(options.get("lateral_step", 1), 1),
        "short_step_divisor": _to_int(options.get("short_step_divisor", 2), 2),
        "enforce_same_map": _to_bool(options.get("enforce_same_map", True), True),
        "max_evidence_attempts": _to_int(options.get("max_evidence_attempts", 50), 50),
        "client_pathfind_max_distance": _to_int(options.get("client_pathfind_max_distance", 18), 18),
        "pathfinding_wait_ms": _to_int(options.get("pathfinding_wait_ms", 900), 900),
        "pathfinding_poll_ms": _to_int(options.get("pathfinding_poll_ms", 100), 100),
        "cancel_active_pathfind": _to_bool(options.get("cancel_active_pathfind", True), True),
        "candidate_repeat_window": _to_int(options.get("candidate_repeat_window", 12), 12),
        "candidate_repeat_limit": _to_int(options.get("candidate_repeat_limit", 2), 2),
        "near_target_distance": _to_int(options.get("near_target_distance", 6), 6),
        "near_target_stall_tolerance": _to_int(options.get("near_target_stall_tolerance", 2), 2),
        "max_regression_from_best": _to_int(options.get("max_regression_from_best", 3), 3),
        "no_best_progress_tolerance": _to_int(options.get("no_best_progress_tolerance", 12), 12),
        "hop_wait_per_tile_ms": _to_int(options.get("hop_wait_per_tile_ms", 220), 220),
        "hop_wait_min_ms": _to_int(options.get("hop_wait_min_ms", 700), 700),
        "hop_wait_max_ms": _to_int(options.get("hop_wait_max_ms", 2600), 2600),
        "hop_wait_poll_ms": _to_int(options.get("hop_wait_poll_ms", 100), 100),
        "hop_wait_stable_polls": _to_int(options.get("hop_wait_stable_polls", 3), 3),
        "hop_wait_candidate_within": _to_int(options.get("hop_wait_candidate_within", 1), 1),
        "hop_awareness_enabled": _to_bool(options.get("hop_awareness_enabled", True), True),
        "hop_awareness_range": _to_int(options.get("hop_awareness_range", 8), 8),
        "hop_awareness_max_entities": _to_int(options.get("hop_awareness_max_entities", 10), 10)
    }

    if normalized["within_distance"] < 0:
        normalized["within_distance"] = 0
    if normalized["min_action_delay_ms"] < 600:
        normalized["min_action_delay_ms"] = 600
    if normalized["settle_ms"] < 0:
        normalized["settle_ms"] = 0
    if normalized["max_attempts"] < 1:
        normalized["max_attempts"] = 1
    if normalized["max_ms"] < 1:
        normalized["max_ms"] = 1
    if normalized["min_progress"] < 1:
        normalized["min_progress"] = 1
    if normalized["max_hop_distance"] < 1:
        normalized["max_hop_distance"] = 1
    if normalized["min_hop_distance"] < 1:
        normalized["min_hop_distance"] = 1
    if normalized["min_hop_distance"] > normalized["max_hop_distance"]:
        normalized["min_hop_distance"] = normalized["max_hop_distance"]
    if normalized["hop_backoff_step"] < 1:
        normalized["hop_backoff_step"] = 1
    if normalized["hop_recover_step"] < 1:
        normalized["hop_recover_step"] = 1
    if normalized["stall_tolerance"] < 0:
        normalized["stall_tolerance"] = 0
    if normalized["stall_pause_ms"] < 0:
        normalized["stall_pause_ms"] = 0
    if normalized["lateral_step"] < 1:
        normalized["lateral_step"] = 1
    if normalized["short_step_divisor"] < 2:
        normalized["short_step_divisor"] = 2
    if normalized["max_evidence_attempts"] < 1:
        normalized["max_evidence_attempts"] = 1
    if normalized["client_pathfind_max_distance"] < 1:
        normalized["client_pathfind_max_distance"] = 1
    if normalized["pathfinding_wait_ms"] < 0:
        normalized["pathfinding_wait_ms"] = 0
    if normalized["pathfinding_poll_ms"] < 50:
        normalized["pathfinding_poll_ms"] = 50
    if normalized["candidate_repeat_window"] < 1:
        normalized["candidate_repeat_window"] = 1
    if normalized["candidate_repeat_limit"] < 1:
        normalized["candidate_repeat_limit"] = 1
    if normalized["near_target_distance"] < 0:
        normalized["near_target_distance"] = 0
    if normalized["near_target_stall_tolerance"] < 1:
        normalized["near_target_stall_tolerance"] = 1
    if normalized["max_regression_from_best"] < 0:
        normalized["max_regression_from_best"] = 0
    if normalized["no_best_progress_tolerance"] < 1:
        normalized["no_best_progress_tolerance"] = 1
    if normalized["hop_wait_per_tile_ms"] < 0:
        normalized["hop_wait_per_tile_ms"] = 0
    if normalized["hop_wait_min_ms"] < 0:
        normalized["hop_wait_min_ms"] = 0
    if normalized["hop_wait_max_ms"] < normalized["hop_wait_min_ms"]:
        normalized["hop_wait_max_ms"] = normalized["hop_wait_min_ms"]
    if normalized["hop_wait_poll_ms"] < 50:
        normalized["hop_wait_poll_ms"] = 50
    if normalized["hop_wait_stable_polls"] < 1:
        normalized["hop_wait_stable_polls"] = 1
    if normalized["hop_wait_candidate_within"] < 0:
        normalized["hop_wait_candidate_within"] = 0
    if normalized["hop_awareness_range"] < 1:
        normalized["hop_awareness_range"] = 1
    if normalized["hop_awareness_max_entities"] < 1:
        normalized["hop_awareness_max_entities"] = 1

    if normalized["max_hop_distance"] > normalized["client_pathfind_max_distance"]:
        normalized["max_hop_distance"] = normalized["client_pathfind_max_distance"]
    if normalized["min_hop_distance"] > normalized["max_hop_distance"]:
        normalized["min_hop_distance"] = normalized["max_hop_distance"]

    if normalized["settle_ms"] < normalized["min_action_delay_ms"]:
        normalized["settle_ms"] = normalized["min_action_delay_ms"]
    if normalized["stall_pause_ms"] < normalized["min_action_delay_ms"]:
        normalized["stall_pause_ms"] = normalized["min_action_delay_ms"]

    return normalized

def _clamp_axis_delta(delta_value, max_step):
    if delta_value > max_step:
        return max_step
    if delta_value < (0 - max_step):
        return (0 - max_step)
    return delta_value


def _scaled_step(delta_value, step_limit, max_axis):
    scaled = int(delta_value * (float(step_limit) / float(max_axis)))
    if delta_value != 0 and scaled == 0:
        if delta_value > 0:
            return 1
        return -1
    return scaled


def _append_candidate(rows, seen, current, label, point):
    if point == current:
        return
    if point in seen:
        return
    rows.append({"label": label, "point": point})
    seen[point] = True


def _build_candidates(current, destination, hop_size, lateral_step, short_step_divisor):
    dx = destination[0] - current[0]
    dy = destination[1] - current[1]
    dz = destination[2] - current[2]

    remaining = max(abs(dx), abs(dy), abs(dz))
    if remaining <= 0:
        return [{"label": "destination", "point": destination}]

    step_limit = hop_size
    if remaining < step_limit:
        step_limit = remaining
    if step_limit < 1:
        step_limit = 1

    max_axis = max(abs(dx), abs(dy), abs(dz))
    if max_axis <= 0:
        return [{"label": "destination", "point": destination}]

    step_dx = _scaled_step(dx, step_limit, max_axis)
    step_dy = _scaled_step(dy, step_limit, max_axis)
    step_dz = _scaled_step(dz, step_limit, max_axis)

    primary = (
        current[0] + step_dx,
        current[1] + step_dy,
        current[2] + step_dz
    )

    axis_x_step = _clamp_axis_delta(dx, step_limit)
    axis_y_step = _clamp_axis_delta(dy, step_limit)
    axis_z_step = _clamp_axis_delta(dz, step_limit)

    axis_x = (
        current[0] + axis_x_step,
        current[1],
        current[2]
    )
    axis_y = (
        current[0],
        current[1] + axis_y_step,
        current[2]
    )

    short_step = step_limit / short_step_divisor
    if short_step < 1:
        short_step = 1

    short_forward = (
        current[0] + _clamp_axis_delta(dx, short_step),
        current[1] + _clamp_axis_delta(dy, short_step),
        current[2] + _clamp_axis_delta(dz, short_step)
    )

    lateral_left_forward = current
    lateral_right_forward = current
    lateral_left = current
    lateral_right = current

    if abs(dy) >= abs(dx):
        lateral_left_forward = (
            current[0] - lateral_step,
            current[1] + axis_y_step,
            current[2] + axis_z_step
        )
        lateral_right_forward = (
            current[0] + lateral_step,
            current[1] + axis_y_step,
            current[2] + axis_z_step
        )
        lateral_left = (
            current[0] - lateral_step,
            current[1],
            current[2]
        )
        lateral_right = (
            current[0] + lateral_step,
            current[1],
            current[2]
        )
    else:
        lateral_left_forward = (
            current[0] + axis_x_step,
            current[1] - lateral_step,
            current[2] + axis_z_step
        )
        lateral_right_forward = (
            current[0] + axis_x_step,
            current[1] + lateral_step,
            current[2] + axis_z_step
        )
        lateral_left = (
            current[0],
            current[1] - lateral_step,
            current[2]
        )
        lateral_right = (
            current[0],
            current[1] + lateral_step,
            current[2]
        )

    rows = []
    seen = {}

    _append_candidate(rows, seen, current, "primary", primary)
    _append_candidate(rows, seen, current, "axis_x", axis_x)
    _append_candidate(rows, seen, current, "axis_y", axis_y)
    _append_candidate(rows, seen, current, "short_forward", short_forward)
    _append_candidate(rows, seen, current, "lateral_left_forward", lateral_left_forward)
    _append_candidate(rows, seen, current, "lateral_right_forward", lateral_right_forward)
    _append_candidate(rows, seen, current, "lateral_left", lateral_left)
    _append_candidate(rows, seen, current, "lateral_right", lateral_right)
    _append_candidate(rows, seen, current, "destination", destination)

    if len(rows) <= 0:
        rows.append({"label": "destination", "point": destination})

    return rows


def _prepare_candidates_for_attempt(candidates, destination, remaining_distance, client_max_distance, stall_count):
    filtered = []

    idx = 0
    while idx < len(candidates):
        row = candidates[idx]
        idx += 1

        if row["label"] == "destination" and remaining_distance > client_max_distance:
            continue

        filtered.append(row)

    if len(filtered) <= 0:
        filtered.append({"label": "destination", "point": destination})

    if remaining_distance <= client_max_distance:
        destination_row = None
        others = []

        idx = 0
        while idx < len(filtered):
            row = filtered[idx]
            idx += 1

            if row["label"] == "destination":
                destination_row = row
                continue

            others.append(row)

        if destination_row is not None:
            filtered = [destination_row] + others
        else:
            filtered = others
    elif stall_count > 0 and len(filtered) > 1:
        rotate_by = stall_count % len(filtered)
        if rotate_by > 0:
            filtered = filtered[rotate_by:] + filtered[:rotate_by]

    return filtered


def _recent_point_count(history_points, point):
    count = 0

    idx = 0
    while idx < len(history_points):
        if history_points[idx] == point:
            count += 1
        idx += 1

    return count


def _append_recent_point(history_points, point, max_window):
    history_points.append(point)

    while len(history_points) > max_window:
        history_points.pop(0)


def _invoke_get_enemy_any(scan_range):
    attempts = [
        (["Any"], "Any", "Next", "Any", scan_range),
        (["Any"], "Any", "Next", scan_range),
        (["Any"], "Next", scan_range)
    ]

    idx = 0
    while idx < len(attempts):
        args = attempts[idx]
        idx += 1

        try:
            return GetEnemy(*args)
        except Exception:
            continue

    return False


def _quick_mobile_awareness_scan(scan_range, max_entities):
    rows = []
    seen_serials = {}
    sample_names = {}

    try:
        ClearIgnoreList()
    except Exception:
        pass

    idx = 0
    while idx < max_entities:
        found_mobile = _invoke_get_enemy_any(scan_range)
        if not found_mobile:
            break

        serial_value = _to_int(_safe_call(0, GetAlias, "enemy"), 0)
        if serial_value <= 0:
            break

        if serial_value in seen_serials:
            try:
                IgnoreObject("enemy")
            except Exception:
                pass
            idx += 1
            continue

        seen_serials[serial_value] = True

        name_text = _safe_call("", Name, "enemy")
        distance_value = _to_int(_safe_call(-1, Distance, "enemy"), -1)

        rows.append({
            "serial": serial_value,
            "name": name_text,
            "distance": distance_value
        })

        lowered_name = ""
        try:
            lowered_name = str(name_text).strip().lower()
        except Exception:
            lowered_name = ""

        if len(lowered_name) > 0 and lowered_name not in sample_names:
            sample_names[lowered_name] = True

        try:
            IgnoreObject("enemy")
        except Exception:
            pass

        try:
            Pause(10)
        except Exception:
            pass

        idx += 1

    try:
        ClearIgnoreList()
    except Exception:
        pass

    sample = []
    for name_key in sample_names.keys():
        sample.append(name_key)

    sample.sort()
    if len(sample) > 6:
        sample = sample[:6]

    return {
        "rows": rows,
        "sample_names": sample
    }


def _estimate_hop_wait_budget_ms(current_point, candidate_point, opts):
    candidate_distance = _distance_between(current_point, candidate_point)
    per_tile_ms = _to_int(opts.get("hop_wait_per_tile_ms", 220), 220)
    min_wait_ms = _to_int(opts.get("hop_wait_min_ms", 700), 700)
    max_wait_ms = _to_int(opts.get("hop_wait_max_ms", 2600), 2600)

    wait_budget = min_wait_ms + (candidate_distance * per_tile_ms)

    if wait_budget < min_wait_ms:
        wait_budget = min_wait_ms
    if wait_budget > max_wait_ms:
        wait_budget = max_wait_ms

    return wait_budget


def _wait_for_hop_settle(state_name, candidate_point, destination_point, wait_budget_ms, poll_ms, stable_polls, candidate_within):
    wait_budget = _to_int(wait_budget_ms, 0)
    poll = _to_int(poll_ms, 100)
    stable_target = _to_int(stable_polls, 3)
    candidate_stop = _to_int(candidate_within, 1)

    if poll < 50:
        poll = 50
    if stable_target < 1:
        stable_target = 1
    if candidate_stop < 0:
        candidate_stop = 0
    if wait_budget <= 0:
        wait_budget = poll

    elapsed = 0
    polls = 0
    stable_count = 0
    moved_polls = 0
    startup_wait_ms = poll * 2

    start_point = _point_from_snapshot(_snapshot_self())
    last_point = start_point
    best_candidate_distance = _distance_between(start_point, candidate_point)
    final_destination_distance = _distance_between(start_point, destination_point)
    final_candidate_distance = best_candidate_distance
    reason = "budget_exhausted"

    while elapsed < wait_budget:
        try:
            Pause(poll)
        except Exception as ex:
            return {
                "ok": False,
                "elapsed_ms": elapsed,
                "polls": polls,
                "stable_count": stable_count,
                "moved_polls": moved_polls,
                "reason": "pause_unavailable",
                "exception": str(ex),
                "best_candidate_distance": best_candidate_distance,
                "final_candidate_distance": final_candidate_distance,
                "final_destination_distance": final_destination_distance
            }

        elapsed += poll
        polls += 1

        current_point = _point_from_snapshot(_snapshot_self())

        if current_point != last_point:
            moved_polls += 1
            stable_count = 0
        else:
            stable_count += 1

        final_candidate_distance = _distance_between(current_point, candidate_point)
        final_destination_distance = _distance_between(current_point, destination_point)

        if final_candidate_distance < best_candidate_distance:
            best_candidate_distance = final_candidate_distance

        if final_candidate_distance <= candidate_stop:
            reason = "candidate_reached"
            last_point = current_point
            break

        if stable_count >= stable_target and elapsed >= startup_wait_ms:
            reason = "movement_settled"
            last_point = current_point
            break

        last_point = current_point

    return {
        "ok": True,
        "elapsed_ms": elapsed,
        "polls": polls,
        "stable_count": stable_count,
        "moved_polls": moved_polls,
        "reason": reason,
        "best_candidate_distance": best_candidate_distance,
        "final_candidate_distance": final_candidate_distance,
        "final_destination_distance": final_destination_distance
    }


def _pathfinding_active_or_none(state_name):
    global _PATHFINDING_UNAVAILABLE_LOGGED

    pathfinding_fn = globals().get("Pathfinding")
    if pathfinding_fn is None:
        if not _PATHFINDING_UNAVAILABLE_LOGGED:
            _PATHFINDING_UNAVAILABLE_LOGGED = True
            Telemetry.warn(state_name, "Pathfinding() command unavailable; using settle-only fallback")
        return None

    try:
        return bool(pathfinding_fn())
    except Exception:
        return False

def _cancel_active_pathfind(ctx, state_name, pause_ms):
    is_active = _pathfinding_active_or_none(state_name)
    if is_active is None:
        return False
    if not is_active:
        return False

    try:
        Pathfind(-1)
    except Exception as ex:
        Telemetry.warn(state_name, "Pathfind cancel failed (non-fatal)", {
            "exception": str(ex)
        })
        return False

    if pause_ms > 0:
        if not _safe_pause(ctx, state_name, pause_ms):
            return False

    Telemetry.debug(state_name, "Cancelled active pathfind before new request")
    return True


def _wait_for_pathfinding_idle(ctx, state_name, timeout_ms, poll_ms):
    timeout = _to_int(timeout_ms, 0)
    if timeout <= 0:
        return True

    poll = _to_int(poll_ms, 100)
    if poll < 50:
        poll = 50

    elapsed = 0
    observed_pathing = False

    initial_active = _pathfinding_active_or_none(state_name)
    if initial_active is None:
        return True

    while elapsed < timeout:
        is_pathing = _pathfinding_active_or_none(state_name)
        if is_pathing is None:
            return True

        if is_pathing:
            observed_pathing = True

        if not is_pathing and (observed_pathing or elapsed >= poll):
            return True

        if not _safe_pause(ctx, state_name, poll):
            return False

        elapsed += poll

    return True

def _safe_pause(ctx, state_name, milliseconds):
    pause_ms = _to_int(milliseconds, 0)
    if pause_ms <= 0:
        return True

    try:
        Pause(pause_ms)
        return True
    except Exception as ex:
        _ctx_fail(ctx, state_name, "Pause command unavailable", {
            "milliseconds": pause_ms,
            "exception": str(ex)
        })
        return False


def _now_ms():
    return int(time.time() * 1000)


def navigate_to_coordinate(ctx, state_name, destination, options):
    start_ms = _now_ms()
    opts = _normalize_options(options)

    result = {
        "success": False,
        "stop_reason": "",
        "final_distance": -1,
        "attempts": 0,
        "elapsed_ms": 0,
        "evidence": {}
    }

    destination_point = _normalize_destination(destination)
    if destination_point is None:
        stop_reason = "invalid_destination"
        _ctx_fail(ctx, state_name, "Pathing destination invalid", {
            "destination": destination,
            "expected": "tuple/list len>=2 or dict with x/y[/z]"
        })
        result["stop_reason"] = stop_reason
        result["elapsed_ms"] = _now_ms() - start_ms
        result["evidence"] = {
            "expected": "x,y,z coordinate",
            "observed": destination
        }
        return result

    initial_snapshot = _snapshot_self()
    initial_point = _point_from_snapshot(initial_snapshot)
    initial_distance = _distance_between(initial_point, destination_point)

    evidence = {
        "initial_position": initial_snapshot,
        "destination": destination_point,
        "options_used": opts,
        "attempt_records": [],
        "dropped_attempt_records": 0,
        "candidate_order_last": "",
        "candidate_results_last": "",
        "stall_count_final": 0,
        "best_distance": initial_distance
    }

    Telemetry.info(state_name, "Pathing action preconditions", {
        "destination": destination_point,
        "within_distance": opts["within_distance"],
        "max_attempts": opts["max_attempts"],
        "max_ms": opts["max_ms"],
        "max_hop_distance": opts["max_hop_distance"],
        "min_hop_distance": opts["min_hop_distance"],
        "min_progress": opts["min_progress"],
        "stall_tolerance": opts["stall_tolerance"],
        "initial_distance": initial_distance,
        "enforce_same_map": opts["enforce_same_map"],
        "min_action_delay_ms": opts["min_action_delay_ms"],
        "settle_ms": opts["settle_ms"],
        "stall_pause_ms": opts["stall_pause_ms"],
        "client_pathfind_max_distance": opts["client_pathfind_max_distance"],
        "pathfinding_wait_ms": opts["pathfinding_wait_ms"],
        "pathfinding_poll_ms": opts["pathfinding_poll_ms"],
        "cancel_active_pathfind": opts["cancel_active_pathfind"],
        "candidate_repeat_window": opts["candidate_repeat_window"],
        "candidate_repeat_limit": opts["candidate_repeat_limit"],
        "near_target_distance": opts["near_target_distance"],
        "near_target_stall_tolerance": opts["near_target_stall_tolerance"],
        "max_regression_from_best": opts["max_regression_from_best"],
        "no_best_progress_tolerance": opts["no_best_progress_tolerance"],
        "hop_wait_per_tile_ms": opts["hop_wait_per_tile_ms"],
        "hop_wait_min_ms": opts["hop_wait_min_ms"],
        "hop_wait_max_ms": opts["hop_wait_max_ms"],
        "hop_wait_poll_ms": opts["hop_wait_poll_ms"],
        "hop_wait_stable_polls": opts["hop_wait_stable_polls"],
        "hop_wait_candidate_within": opts["hop_wait_candidate_within"],
        "hop_awareness_enabled": opts["hop_awareness_enabled"],
        "hop_awareness_range": opts["hop_awareness_range"],
        "hop_awareness_max_entities": opts["hop_awareness_max_entities"]
    })

    if initial_distance <= opts["within_distance"]:
        result["success"] = True
        result["stop_reason"] = "already_within_distance"
        result["final_distance"] = initial_distance
        result["elapsed_ms"] = _now_ms() - start_ms
        result["evidence"] = evidence
        Telemetry.info(state_name, "Pathing not required; already in proximity", {
            "distance": initial_distance,
            "within_distance": opts["within_distance"]
        })
        return result

    hop_size = opts["max_hop_distance"]
    stall_count = 0
    attempts = 0
    attempts_since_best = 0
    stop_reason = ""

    recent_selected_points = []

    while attempts < opts["max_attempts"]:
        elapsed_ms = _now_ms() - start_ms
        if elapsed_ms >= opts["max_ms"]:
            stop_reason = "max_ms_exceeded"
            break

        current_snapshot = _snapshot_self()
        current_point = _point_from_snapshot(current_snapshot)
        remaining_distance = _distance_between(current_point, destination_point)

        if opts["enforce_same_map"]:
            if initial_snapshot["map"] >= 0 and current_snapshot["map"] >= 0:
                if initial_snapshot["map"] != current_snapshot["map"]:
                    stop_reason = "map_changed"
                    _ctx_fail(ctx, state_name, "Pathing stopped: map changed", {
                        "expected_map": initial_snapshot["map"],
                        "observed_map": current_snapshot["map"],
                        "attempt": attempts + 1
                    })
                    break

        if remaining_distance <= opts["within_distance"]:
            stop_reason = "within_distance_reached"
            result["success"] = True
            break

        candidates = _build_candidates(
            current_point,
            destination_point,
            hop_size,
            opts["lateral_step"],
            opts["short_step_divisor"]
        )

        candidates = _prepare_candidates_for_attempt(
            candidates,
            destination_point,
            remaining_distance,
            opts["client_pathfind_max_distance"],
            stall_count
        )

        candidate_order = []
        candidate_rows = []

        idx = 0
        while idx < len(candidates):
            row = candidates[idx]
            point = row["point"]
            label = row["label"]
            candidate_order.append("{0}:{1},{2},{3}".format(label, point[0], point[1], point[2]))
            idx += 1

        awareness_mobile_count = 0
        awareness_nearby_count = 0
        awareness_sample = ""

        if opts["hop_awareness_enabled"] and stall_count > 0:
            awareness_result = _quick_mobile_awareness_scan(
                opts["hop_awareness_range"],
                opts["hop_awareness_max_entities"]
            )

            awareness_rows = awareness_result.get("rows", [])
            awareness_mobile_count = len(awareness_rows)

            awareness_index = 0
            while awareness_index < len(awareness_rows):
                if _to_int(awareness_rows[awareness_index].get("distance", -1), -1) <= 1:
                    awareness_nearby_count += 1
                awareness_index += 1

            awareness_sample = "|".join(awareness_result.get("sample_names", []))

        attempts += 1

        Telemetry.debug(state_name, "Pathing attempt", {
            "attempt": attempts,
            "remaining_distance": remaining_distance,
            "hop_size": hop_size,
            "candidate_count": len(candidates),
            "candidate_order": "|".join(candidate_order),
            "stall_count": stall_count,
            "client_pathfind_max_distance": opts["client_pathfind_max_distance"],
            "candidate_repeat_limit": opts["candidate_repeat_limit"],
            "candidate_repeat_window": opts["candidate_repeat_window"],
            "best_distance": evidence["best_distance"],
            "attempts_since_best": attempts_since_best,
            "max_regression_from_best": opts["max_regression_from_best"],
            "no_best_progress_tolerance": opts["no_best_progress_tolerance"],
            "awareness_mobile_count": awareness_mobile_count,
            "awareness_nearby_count": awareness_nearby_count,
            "awareness_sample": awareness_sample
        })

        progressed = False
        pause_unavailable = False
        attempt_start_distance = remaining_distance
        selected_label = ""
        selected_before = remaining_distance
        selected_after = remaining_distance
        selected_progress = 0
        selected_candidate_progress = 0
        selected_point = None
        selected_repeat_count = 0
        selected_forced = False
        selected_regression_from_best = 0
        selected_new_best = False
        selected_hop_wait_reason = ""
        selected_hop_wait_elapsed_ms = 0

        selected_row = None
        idx = 0
        while idx < len(candidates):
            row = candidates[idx]
            idx += 1

            repeat_count = _recent_point_count(recent_selected_points, row["point"])
            if repeat_count >= opts["candidate_repeat_limit"]:
                point = row["point"]
                candidate_rows.append("{0}:{1},{2},{3}:skipped=recent_repeat:repeat_count={4}".format(
                    row["label"],
                    point[0],
                    point[1],
                    point[2],
                    repeat_count
                ))
                continue

            selected_row = row
            selected_repeat_count = repeat_count
            break

        if selected_row is None and len(candidates) > 0:
            selected_row = candidates[0]
            selected_repeat_count = _recent_point_count(recent_selected_points, selected_row["point"])
            selected_forced = True

            point = selected_row["point"]
            candidate_rows.append("{0}:{1},{2},{3}:selection=forced_repeat_override:repeat_count={4}".format(
                selected_row["label"],
                point[0],
                point[1],
                point[2],
                selected_repeat_count
            ))

        if selected_row is not None:
            selected_label = selected_row["label"]
            candidate_point = selected_row["point"]
            selected_point = candidate_point

            before_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)
            pathfind_ok = False
            exception_text = ""
            cancelled_active_pathfind = False
            hop_wait_budget_ms = _estimate_hop_wait_budget_ms(current_point, candidate_point, opts)
            hop_wait_elapsed_ms = 0
            hop_wait_reason = "not_waited"
            hop_wait_candidate_distance = -1
            hop_wait_moved_polls = 0
            hop_wait_result = {}

            if opts["cancel_active_pathfind"]:
                cancelled_active_pathfind = _cancel_active_pathfind(ctx, state_name, opts["pathfinding_poll_ms"])

            try:
                pathfind_ok = safe_pathfind(
                    ctx,
                    state_name,
                    candidate_point,
                    opts["settle_ms"],
                    fail_on_error=False
                )
            except Exception as ex:
                pathfind_ok = False
                exception_text = str(ex)

            if not _wait_for_pathfinding_idle(ctx, state_name, opts["pathfinding_wait_ms"], opts["pathfinding_poll_ms"]):
                pause_unavailable = True

            if not pause_unavailable:
                hop_wait_result = _wait_for_hop_settle(
                    state_name,
                    candidate_point,
                    destination_point,
                    hop_wait_budget_ms,
                    opts["hop_wait_poll_ms"],
                    opts["hop_wait_stable_polls"],
                    opts["hop_wait_candidate_within"]
                )

                hop_wait_elapsed_ms = _to_int(hop_wait_result.get("elapsed_ms", 0), 0)
                hop_wait_reason = str(hop_wait_result.get("reason", ""))
                hop_wait_candidate_distance = _to_int(hop_wait_result.get("final_candidate_distance", -1), -1)
                hop_wait_moved_polls = _to_int(hop_wait_result.get("moved_polls", 0), 0)

                if not hop_wait_result.get("ok", True):
                    pause_unavailable = True
                    if len(exception_text) <= 0:
                        wait_ex = hop_wait_result.get("exception", "")
                        if len(wait_ex) > 0:
                            exception_text = str(wait_ex)

            if pause_unavailable:
                after_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)
            else:
                fallback_after_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)
                after_distance = _to_int(hop_wait_result.get("final_destination_distance", fallback_after_distance), fallback_after_distance)

            candidate_progress_delta = before_distance - after_distance
            attempt_progress_delta = attempt_start_distance - after_distance
            best_distance_before = evidence["best_distance"]
            regression_from_best = after_distance - best_distance_before
            made_new_best = False

            if after_distance < best_distance_before:
                evidence["best_distance"] = after_distance
                made_new_best = True
                attempts_since_best = 0
            elif after_distance == best_distance_before:
                attempts_since_best = 0
            else:
                attempts_since_best += 1

            within_regression_guard = regression_from_best <= opts["max_regression_from_best"]
            qualifies_progress = (
                (not pause_unavailable) and
                attempt_progress_delta >= opts["min_progress"] and
                within_regression_guard
            )

            row_text = "{0}:{1},{2},{3}:ok={4}:before={5}:after={6}:candidate_progress={7}:attempt_progress={8}:repeat_count={9}:best_distance_before={10}:regression_from_best={11}:new_best={12}:hop_wait_budget_ms={13}:hop_wait_elapsed_ms={14}:hop_wait_reason={15}:hop_wait_candidate_distance={16}:hop_wait_moved_polls={17}".format(
                selected_label,
                candidate_point[0],
                candidate_point[1],
                candidate_point[2],
                pathfind_ok,
                before_distance,
                after_distance,
                candidate_progress_delta,
                attempt_progress_delta,
                selected_repeat_count,
                best_distance_before,
                regression_from_best,
                made_new_best,
                hop_wait_budget_ms,
                hop_wait_elapsed_ms,
                hop_wait_reason,
                hop_wait_candidate_distance,
                hop_wait_moved_polls
            )

            if selected_forced:
                row_text = "{0}:forced=True".format(row_text)
            if cancelled_active_pathfind:
                row_text = "{0}:cancelled_active_pathfind=True".format(row_text)
            if len(exception_text) > 0:
                row_text = "{0}:exception={1}".format(row_text, exception_text)
            if attempt_progress_delta >= opts["min_progress"] and not within_regression_guard:
                row_text = "{0}:progress_disqualified=regression_guard:max_regression_from_best={1}".format(
                    row_text,
                    opts["max_regression_from_best"]
                )

            candidate_rows.append(row_text)
            _append_recent_point(recent_selected_points, candidate_point, opts["candidate_repeat_window"])

            if qualifies_progress:
                progressed = True
                selected_before = attempt_start_distance
                selected_after = after_distance
                selected_progress = attempt_progress_delta
                selected_candidate_progress = candidate_progress_delta
                selected_regression_from_best = regression_from_best
                selected_new_best = made_new_best
                selected_hop_wait_reason = hop_wait_reason
                selected_hop_wait_elapsed_ms = hop_wait_elapsed_ms
        else:
            attempts_since_best += 1
            candidate_rows.append("none:selected=False:reason=no_candidate_available")

        if pause_unavailable:
            stop_reason = "pause_unavailable"

        evidence["candidate_order_last"] = "|".join(candidate_order)
        evidence["candidate_results_last"] = "|".join(candidate_rows)

        attempt_record = {
            "attempt": attempts,
            "before_distance": remaining_distance,
            "hop_size": hop_size,
            "stall_count_before": stall_count,
            "attempts_since_best": attempts_since_best,
            "awareness_mobile_count": awareness_mobile_count,
            "awareness_nearby_count": awareness_nearby_count,
            "candidate_order": evidence["candidate_order_last"],
            "candidate_results": evidence["candidate_results_last"]
        }

        if len(evidence["attempt_records"]) < opts["max_evidence_attempts"]:
            evidence["attempt_records"].append(attempt_record)
        else:
            evidence["dropped_attempt_records"] += 1

        if len(stop_reason) > 0:
            break

        if attempts_since_best > opts["no_best_progress_tolerance"]:
            stop_reason = "no_best_progress_exceeded"
            _ctx_fail(ctx, state_name, "Pathing no-best-progress tolerance exceeded", {
                "attempt": attempts,
                "attempts_since_best": attempts_since_best,
                "no_best_progress_tolerance": opts["no_best_progress_tolerance"],
                "best_distance": evidence["best_distance"],
                "remaining_distance": _distance_between(_point_from_snapshot(_snapshot_self()), destination_point),
                "candidate_order": evidence["candidate_order_last"],
                "candidate_results": evidence["candidate_results_last"]
            })
            break

        if progressed:
            stall_count = 0
            if hop_size < opts["max_hop_distance"]:
                hop_size += opts["hop_recover_step"]
                if hop_size > opts["max_hop_distance"]:
                    hop_size = opts["max_hop_distance"]

            Telemetry.info(state_name, "Pathing progress", {
                "attempt": attempts,
                "selected_candidate": selected_label,
                "candidate_point": selected_point,
                "before": selected_before,
                "after": selected_after,
                "progress": selected_progress,
                "candidate_progress": selected_candidate_progress,
                "next_hop_size": hop_size,
                "repeat_count": selected_repeat_count,
                "forced_selection": selected_forced,
                "best_distance": evidence["best_distance"],
                "regression_from_best": selected_regression_from_best,
                "attempts_since_best": attempts_since_best,
                "new_best": selected_new_best,
                "hop_wait_reason": selected_hop_wait_reason,
                "hop_wait_elapsed_ms": selected_hop_wait_elapsed_ms
            })
            continue

        stall_count += 1
        if hop_size > opts["min_hop_distance"]:
            hop_size -= opts["hop_backoff_step"]
            if hop_size < opts["min_hop_distance"]:
                hop_size = opts["min_hop_distance"]

        stall_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)

        Telemetry.warn(state_name, "Pathing stall detected", {
            "attempt": attempts,
            "stall_count": stall_count,
            "stall_tolerance": opts["stall_tolerance"],
            "next_hop_size": hop_size,
            "remaining_distance": stall_distance,
            "best_distance": evidence["best_distance"],
            "attempts_since_best": attempts_since_best,
            "candidate_order": evidence["candidate_order_last"],
            "candidate_results": evidence["candidate_results_last"]
        })

        if stall_distance <= opts["near_target_distance"] and stall_count >= opts["near_target_stall_tolerance"]:
            stop_reason = "near_target_oscillation"
            _ctx_fail(ctx, state_name, "Pathing near-target oscillation detected", {
                "attempt": attempts,
                "stall_count": stall_count,
                "near_target_distance": opts["near_target_distance"],
                "near_target_stall_tolerance": opts["near_target_stall_tolerance"],
                "remaining_distance": stall_distance,
                "best_distance": evidence["best_distance"],
                "attempts_since_best": attempts_since_best,
                "candidate_order": evidence["candidate_order_last"],
                "candidate_results": evidence["candidate_results_last"]
            })
            break

        if stall_count > opts["stall_tolerance"]:
            stop_reason = "stall_tolerance_exceeded"
            _ctx_fail(ctx, state_name, "Pathing stall tolerance exceeded", {
                "attempt": attempts,
                "stall_count": stall_count,
                "stall_tolerance": opts["stall_tolerance"],
                "remaining_distance": stall_distance,
                "best_distance": evidence["best_distance"],
                "attempts_since_best": attempts_since_best,
                "candidate_order": evidence["candidate_order_last"],
                "candidate_results": evidence["candidate_results_last"]
            })
            break

        if not _safe_pause(ctx, state_name, opts["stall_pause_ms"]):
            stop_reason = "pause_unavailable"
            break
    if len(stop_reason) <= 0:
        if result["success"]:
            stop_reason = "within_distance_reached"
        elif attempts >= opts["max_attempts"]:
            stop_reason = "max_attempts_exceeded"
        else:
            stop_reason = "pathing_stopped"

    final_snapshot = _snapshot_self()
    final_point = _point_from_snapshot(final_snapshot)
    final_distance = _distance_between(final_point, destination_point)

    if not result["success"] and final_distance <= opts["within_distance"]:
        result["success"] = True
        if stop_reason in ("pathing_stopped", "max_attempts_exceeded", "max_ms_exceeded"):
            stop_reason = "within_distance_reached"

    evidence["stall_count_final"] = stall_count
    evidence["attempts_since_best_final"] = attempts_since_best
    evidence["final_position"] = final_snapshot

    result["stop_reason"] = stop_reason
    result["final_distance"] = final_distance
    result["attempts"] = attempts
    result["elapsed_ms"] = _now_ms() - start_ms
    result["evidence"] = evidence

    level = Telemetry.info
    message = "Pathing finished"
    if not result["success"]:
        level = Telemetry.warn
        message = "Pathing finished without success"

    level(state_name, message, {
        "success": result["success"],
        "stop_reason": result["stop_reason"],
        "attempts": result["attempts"],
        "elapsed_ms": result["elapsed_ms"],
        "final_distance": result["final_distance"],
        "best_distance": evidence["best_distance"],
        "stall_count_final": stall_count,
        "attempts_since_best_final": attempts_since_best
    })

    return result


