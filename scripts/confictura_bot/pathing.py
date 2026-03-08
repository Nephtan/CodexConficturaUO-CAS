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
        "max_evidence_attempts": _to_int(options.get("max_evidence_attempts", 50), 50)
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
        "stall_pause_ms": opts["stall_pause_ms"]
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
    stop_reason = ""

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

        candidate_order = []
        candidate_rows = []

        idx = 0
        while idx < len(candidates):
            row = candidates[idx]
            point = row["point"]
            label = row["label"]
            candidate_order.append("{0}:{1},{2},{3}".format(label, point[0], point[1], point[2]))
            idx += 1

        attempts += 1

        Telemetry.debug(state_name, "Pathing attempt", {
            "attempt": attempts,
            "remaining_distance": remaining_distance,
            "hop_size": hop_size,
            "candidate_count": len(candidates),
            "candidate_order": "|".join(candidate_order),
            "stall_count": stall_count
        })

        progressed = False
        attempt_start_distance = remaining_distance
        selected_label = ""
        selected_before = remaining_distance
        selected_after = remaining_distance
        selected_progress = 0
        selected_candidate_progress = 0
        selected_point = None

        idx = 0
        while idx < len(candidates):
            row = candidates[idx]
            idx += 1

            label = row["label"]
            candidate_point = row["point"]

            before_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)
            pathfind_ok = False
            exception_text = ""

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

            after_distance = _distance_between(_point_from_snapshot(_snapshot_self()), destination_point)
            candidate_progress_delta = before_distance - after_distance
            attempt_progress_delta = attempt_start_distance - after_distance

            row_text = "{0}:{1},{2},{3}:ok={4}:before={5}:after={6}:candidate_progress={7}:attempt_progress={8}".format(
                label,
                candidate_point[0],
                candidate_point[1],
                candidate_point[2],
                pathfind_ok,
                before_distance,
                after_distance,
                candidate_progress_delta,
                attempt_progress_delta
            )

            if len(exception_text) > 0:
                row_text = "{0}:exception={1}".format(row_text, exception_text)

            candidate_rows.append(row_text)

            if attempt_progress_delta >= opts["min_progress"]:
                progressed = True
                selected_label = label
                selected_before = attempt_start_distance
                selected_after = after_distance
                selected_progress = attempt_progress_delta
                selected_candidate_progress = candidate_progress_delta
                selected_point = candidate_point
                break

        evidence["candidate_order_last"] = "|".join(candidate_order)
        evidence["candidate_results_last"] = "|".join(candidate_rows)

        attempt_record = {
            "attempt": attempts,
            "before_distance": remaining_distance,
            "hop_size": hop_size,
            "stall_count_before": stall_count,
            "candidate_order": evidence["candidate_order_last"],
            "candidate_results": evidence["candidate_results_last"]
        }

        if len(evidence["attempt_records"]) < opts["max_evidence_attempts"]:
            evidence["attempt_records"].append(attempt_record)
        else:
            evidence["dropped_attempt_records"] += 1

        if progressed:
            stall_count = 0
            if hop_size < opts["max_hop_distance"]:
                hop_size += opts["hop_recover_step"]
                if hop_size > opts["max_hop_distance"]:
                    hop_size = opts["max_hop_distance"]

            if selected_after < evidence["best_distance"]:
                evidence["best_distance"] = selected_after

            Telemetry.info(state_name, "Pathing progress", {
                "attempt": attempts,
                "selected_candidate": selected_label,
                "candidate_point": selected_point,
                "before": selected_before,
                "after": selected_after,
                "progress": selected_progress,
                "candidate_progress": selected_candidate_progress,
                "next_hop_size": hop_size
            })
            continue

        stall_count += 1
        if hop_size > opts["min_hop_distance"]:
            hop_size -= opts["hop_backoff_step"]
            if hop_size < opts["min_hop_distance"]:
                hop_size = opts["min_hop_distance"]

        Telemetry.warn(state_name, "Pathing stall detected", {
            "attempt": attempts,
            "stall_count": stall_count,
            "stall_tolerance": opts["stall_tolerance"],
            "next_hop_size": hop_size,
            "remaining_distance": remaining_distance,
            "candidate_order": evidence["candidate_order_last"],
            "candidate_results": evidence["candidate_results_last"]
        })

        if stall_count > opts["stall_tolerance"]:
            stop_reason = "stall_tolerance_exceeded"
            _ctx_fail(ctx, state_name, "Pathing stall tolerance exceeded", {
                "attempt": attempts,
                "stall_count": stall_count,
                "stall_tolerance": opts["stall_tolerance"],
                "remaining_distance": remaining_distance,
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
        "stall_count_final": stall_count
    })

    return result


