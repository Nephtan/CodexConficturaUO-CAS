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
            "candidate_results_last": evidence.get("candidate_results_last", "")
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
            "final_distance": report_row["final_distance"]
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

