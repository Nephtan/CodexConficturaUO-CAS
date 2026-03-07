# Name: Confictura World Awareness Controller
# Description: Builds and updates a local world model of map tiles, mobiles, objects, and gump events.
# Author: ChatGPT Codex
# Shard: Confictura

import sys


def _purge_confictura_import_cache():
    purge_keys = []
    for module_name in sys.modules.keys():
        try:
            if module_name == "world_awareness_config" or module_name.startswith("confictura_bot"):
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
from confictura_bot.gump_router import handle_configured_gumps
from confictura_bot.guards import guard_player_alive
from confictura_bot.perception import merge_world_observations
from confictura_bot.perception import scan_mobiles
from confictura_bot.perception import scan_objects
from confictura_bot.perception import snapshot_self_state
from confictura_bot.safe_api import safe_pathfind
from confictura_bot.safe_api import safe_wait_for_gump_any
from confictura_bot.telemetry import Telemetry
from world_awareness_config import BOT_CONFIG
from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.ca_shim import publish_known_ca_api

bind_ca_api(globals())


class BootstrapState(State):
    key = "BOOTSTRAP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering BOOTSTRAP")

    def tick(self, ctx):
        required_sections = ["runtime", "safety", "awareness", "gumps", "exploration"]
        for section in required_sections:
            if section not in ctx.config:
                ctx.fail(self.key, "Missing config section", {"section": section})
                return "FATAL_STOP"

        ctx.world_model = {
            "visited_tiles": {},
            "mobiles": {},
            "objects": {},
            "cycle": 0,
            "unknown_gumps": 0
        }

        ctx.current_self = {}
        ctx.current_mobiles = []
        ctx.current_objects = []
        ctx.patrol_index = 0

        return "SELF_SCAN"


class SelfScanState(State):
    key = "SELF_SCAN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering SELF_SCAN")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        awareness_cfg = ctx.config.get("awareness", {})
        region_attributes = awareness_cfg.get("region_attributes_probe", [])

        ctx.current_self = snapshot_self_state(self.key, region_attributes)
        return "MOBILE_SCAN"


class MobileScanState(State):
    key = "MOBILE_SCAN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering MOBILE_SCAN")

    def tick(self, ctx):
        awareness_cfg = ctx.config.get("awareness", {})
        mobile_scan_cfg = awareness_cfg.get("mobile_scan", {})

        ctx.current_mobiles = scan_mobiles(self.key, mobile_scan_cfg)
        return "OBJECT_SCAN"


class ObjectScanState(State):
    key = "OBJECT_SCAN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering OBJECT_SCAN")

    def tick(self, ctx):
        awareness_cfg = ctx.config.get("awareness", {})
        object_scan_cfg = awareness_cfg.get("object_scan", {})

        ctx.current_objects = scan_objects(self.key, object_scan_cfg)
        return "GUMP_SCAN"


class GumpScanState(State):
    key = "GUMP_SCAN"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering GUMP_SCAN")

    def tick(self, ctx):
        gump_cfg = ctx.config.get("gumps", {})
        runtime_cfg = ctx.config.get("runtime", {})

        if not gump_cfg.get("enabled", True):
            Telemetry.debug(self.key, "Gump scan disabled")
            return "REPORT"

        if not safe_wait_for_gump_any(ctx, self.key, runtime_cfg.get("gump_timeout_ms", 1200)):
            return "REPORT"

        gump_result = handle_configured_gumps(
            ctx,
            self.key,
            gump_cfg.get("rules", []),
            gump_cfg.get("candidate_gump_ids", [])
        )

        if gump_result.get("status") == "unknown":
            ctx.world_model["unknown_gumps"] = ctx.world_model.get("unknown_gumps", 0) + 1
            ctx.fail(self.key, "Unhandled gump detected", {
                "unknown_gumps": ctx.world_model.get("unknown_gumps", 0),
                "action": "Add new gump rule"
            })

            if gump_cfg.get("strict_unknown_gump", True):
                return "FATAL_STOP"

        return "REPORT"


class ReportState(State):
    key = "REPORT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering REPORT")

    def tick(self, ctx):
        awareness_cfg = ctx.config.get("awareness", {})
        max_report = awareness_cfg.get("max_report_entities", 10)

        summary = merge_world_observations(
            ctx,
            ctx.current_self,
            ctx.current_mobiles,
            ctx.current_objects
        )

        Telemetry.info(self.key, "World model summary", summary)

        mobile_index = 0
        while mobile_index < len(ctx.current_mobiles) and mobile_index < max_report:
            mobile_data = ctx.current_mobiles[mobile_index]
            Telemetry.debug(self.key, "Mobile observed", {
                "serial": mobile_data.get("serial_hex", "0x0"),
                "name": mobile_data.get("name", ""),
                "distance": mobile_data.get("distance", -1),
                "notoriety": mobile_data.get("notoriety", "Unknown"),
                "x": mobile_data.get("x", 0),
                "y": mobile_data.get("y", 0),
                "z": mobile_data.get("z", 0)
            })
            mobile_index += 1

        object_index = 0
        while object_index < len(ctx.current_objects) and object_index < max_report:
            object_data = ctx.current_objects[object_index]
            Telemetry.debug(self.key, "Object observed", {
                "serial": object_data.get("serial_hex", "0x0"),
                "watch_name": object_data.get("watch_name", ""),
                "graphic": hex(object_data.get("graphic", 0)),
                "distance": object_data.get("distance", -1),
                "x": object_data.get("x", 0),
                "y": object_data.get("y", 0),
                "z": object_data.get("z", 0),
                "property_hits": "|".join(object_data.get("property_hits", []))
            })
            object_index += 1

        max_cycles = awareness_cfg.get("max_cycles", 0)
        if max_cycles > 0 and summary.get("cycle", 0) >= max_cycles:
            return "COMPLETE_STOP"

        return "PATROL_MOVE"


class PatrolMoveState(State):
    key = "PATROL_MOVE"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering PATROL_MOVE")

    def tick(self, ctx):
        exploration_cfg = ctx.config.get("exploration", {})
        runtime_cfg = ctx.config.get("runtime", {})

        if not exploration_cfg.get("patrol_enabled", False):
            Telemetry.debug(self.key, "Patrol disabled")
            return "LOOP_DELAY"

        waypoints = exploration_cfg.get("patrol_waypoints", [])
        if len(waypoints) == 0:
            Telemetry.warn(self.key, "Patrol enabled but no waypoints configured")
            return "LOOP_DELAY"

        waypoint = waypoints[ctx.patrol_index % len(waypoints)]
        ctx.patrol_index += 1

        if not isinstance(waypoint, tuple) or len(waypoint) != 3:
            ctx.fail(self.key, "Invalid waypoint format", {"waypoint": waypoint})
            return "RECOVER"

        Telemetry.info(self.key, "Patrol waypoint", {
            "index": ctx.patrol_index,
            "x": waypoint[0],
            "y": waypoint[1],
            "z": waypoint[2]
        })

        if not safe_pathfind(ctx, self.key, waypoint, runtime_cfg.get("pathfind_settle_ms", 300)):
            return "RECOVER"

        return "LOOP_DELAY"


class LoopDelayState(State):
    key = "LOOP_DELAY"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering LOOP_DELAY")

    def tick(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        Pause(runtime_cfg.get("scan_interval_ms", 800))
        return "SELF_SCAN"


class RecoverState(State):
    key = "RECOVER"

    def enter(self, ctx):
        Telemetry.warn(self.key, "Entering RECOVER", {
            "last_failed_state": ctx.last_failed_state,
            "last_error": ctx.last_error
        })

    def tick(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        max_retries = runtime_cfg.get("max_retries_per_state", 3)

        failed_state = ctx.last_failed_state
        if failed_state is None:
            failed_state = "UNKNOWN"

        retry_count = ctx.increment_retry(failed_state)
        Telemetry.warn(self.key, "Retrying state", {
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
            return "FATAL_STOP"

        return "SELF_SCAN"


class CompleteStopState(State):
    key = "COMPLETE_STOP"

    def enter(self, ctx):
        summary = {
            "cycles": ctx.world_model.get("cycle", 0),
            "visited_tiles": len(ctx.world_model.get("visited_tiles", {})),
            "unique_mobiles": len(ctx.world_model.get("mobiles", {})),
            "unique_objects": len(ctx.world_model.get("objects", {})),
            "unknown_gumps": ctx.world_model.get("unknown_gumps", 0)
        }

        Telemetry.info(self.key, "Awareness cycle complete", summary)
        ctx.stop("Configured awareness cycle limit reached")
        Stop()

    def tick(self, ctx):
        return None


class FatalStopState(State):
    key = "FATAL_STOP"

    def enter(self, ctx):
        Telemetry.fatal(self.key, "Entering FATAL_STOP", {
            "last_error_state": ctx.last_error_state,
            "last_error": ctx.last_error,
            "cycle": ctx.world_model.get("cycle", 0)
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
        "SELF_SCAN": SelfScanState(),
        "MOBILE_SCAN": MobileScanState(),
        "OBJECT_SCAN": ObjectScanState(),
        "GUMP_SCAN": GumpScanState(),
        "REPORT": ReportState(),
        "PATROL_MOVE": PatrolMoveState(),
        "LOOP_DELAY": LoopDelayState(),
        "RECOVER": RecoverState(),
        "COMPLETE_STOP": CompleteStopState(),
        "FATAL_STOP": FatalStopState()
    }


def run_world_awareness_controller(config):
    published_api = publish_known_ca_api(globals())
    Telemetry.debug("MAIN", "Published ClassicAssist API symbols", {"count": published_api})
    Telemetry.info("MAIN", "Starting WorldAwarenessController")

    ctx = BotContext(config)
    states = _build_states()

    machine = StateMachine(ctx, states, "BOOTSTRAP")
    machine.run()

    Telemetry.info("MAIN", "WorldAwarenessController finished", {
        "tick_count": ctx.tick_count,
        "transition_count": ctx.transition_count,
        "last_error_state": ctx.last_error_state,
        "last_error": ctx.last_error,
        "cycle": ctx.world_model.get("cycle", 0)
    })


run_world_awareness_controller(BOT_CONFIG)



