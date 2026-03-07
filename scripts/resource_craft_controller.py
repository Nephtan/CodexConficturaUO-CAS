# Name: Confictura Resource Craft Controller
# Description: Runs an autonomous onboarding and resource FSM with fail-safe telemetry and gump triage.
# Author: ChatGPT Codex
# Shard: Confictura

import sys


def _purge_confictura_import_cache():
    purge_keys = []
    for module_name in sys.modules.keys():
        try:
            if module_name == "resource_craft_config" or module_name.startswith("confictura_bot"):
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
from confictura_bot.guards import guard_alias_available
from confictura_bot.guards import guard_item_exists
from confictura_bot.guards import guard_journal_clean
from confictura_bot.guards import guard_player_alive
from confictura_bot.guards import guard_weight_ok
from confictura_bot.safe_api import safe_context_menu
from confictura_bot.safe_api import safe_move_type
from confictura_bot.safe_api import safe_pathfind
from confictura_bot.safe_api import safe_speech
from confictura_bot.safe_api import safe_target
from confictura_bot.safe_api import safe_target_by_resource
from confictura_bot.safe_api import safe_target_tile_offset
from confictura_bot.safe_api import safe_use_object
from confictura_bot.safe_api import safe_use_skill
from confictura_bot.safe_api import safe_use_type
from confictura_bot.safe_api import safe_wait_for_gump_any
from confictura_bot.safe_api import safe_wait_for_journal_any
from confictura_bot.safe_api import safe_wait_for_target
from confictura_bot.telemetry import Telemetry
from resource_craft_config import BOT_CONFIG
from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.ca_shim import publish_known_ca_api

bind_ca_api(globals())


def _resolve_waypoint(ctx, waypoint_name):
    waypoint = ctx.config.get("waypoints", {}).get(waypoint_name, {})
    mode = waypoint.get("mode", "alias")

    if mode == "alias":
        return waypoint.get("alias", "")

    return (
        waypoint.get("x", 0),
        waypoint.get("y", 0),
        waypoint.get("z", 0)
    )


def _journal_has_any(ctx, state_name, entries, timeout_ms):
    if len(entries) == 0:
        return (False, None)

    matched, matched_text = safe_wait_for_journal_any(ctx, state_name, entries, timeout_ms, "")
    return (matched, matched_text)


def _find_usable_tool(ctx):
    inventory_cfg = ctx.config.get("inventory", {})
    gather_cfg = ctx.config.get("gather", {})

    tool_graphics = inventory_cfg.get("tool_graphics", [])
    if gather_cfg.get("tool_graphic", 0) not in tool_graphics:
        tool_graphics.insert(0, gather_cfg.get("tool_graphic", 0))

    known_hues = inventory_cfg.get("known_tool_hues", [-1])
    for graphic in tool_graphics:
        for hue in known_hues:
            if FindType(graphic, -1, "backpack", hue):
                return (graphic, hue)

    return (None, None)


class BootstrapState(State):
    key = "BOOTSTRAP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering BOOTSTRAP")

    def tick(self, ctx):
        required_sections = [
            "runtime",
            "safety",
            "onboarding",
            "aliases",
            "inventory",
            "gather",
            "craft",
            "waypoints"
        ]
        for section in required_sections:
            if section not in ctx.config:
                ctx.fail(self.key, "Missing config section", {"section": section})
                return "FATAL_STOP"

        aliases = ctx.config.get("aliases", {})
        for alias_name in aliases.keys():
            alias_spec = aliases[alias_name]
            alias_value = alias_spec.get("value", 0)

            if alias_value not in (None, 0, ""):
                Telemetry.info(self.key, "Setting alias", {
                    "alias": alias_name,
                    "value": alias_value
                })
                ctx.set_alias(alias_name, alias_value)

        onboarding_cfg = ctx.config.get("onboarding", {})
        if onboarding_cfg.get("enabled", True):
            return "ONBOARDING_INTERACT"

        return "PRECHECK"


class OnboardingInteractState(State):
    key = "ONBOARDING_INTERACT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering ONBOARDING_INTERACT")

    def _handle_any_gump(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        onboarding_cfg = ctx.config.get("onboarding", {})

        if not safe_wait_for_gump_any(ctx, self.key, runtime_cfg.get("gump_timeout_ms", 2500)):
            return None

        gump_result = handle_configured_gumps(
            ctx,
            self.key,
            onboarding_cfg.get("gump_rules", []),
            onboarding_cfg.get("candidate_gump_ids", [])
        )

        if gump_result.get("status") == "matched":
            if gump_result.get("complete", False):
                Telemetry.info(self.key, "Onboarding marked complete by gump rule", {
                    "rule": gump_result.get("rule_name", "")
                })
                return "PRECHECK"
            return None

        if gump_result.get("status") == "unknown":
            if onboarding_cfg.get("unknown_gump_is_fatal", True):
                ctx.fail(self.key, "Unknown gump encountered during onboarding", {
                    "action": "Add gump rule and rerun"
                })
                return "FATAL_STOP"

        return None

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        onboarding_cfg = ctx.config.get("onboarding", {})
        runtime_cfg = ctx.config.get("runtime", {})

        max_attempts = onboarding_cfg.get("max_npc_attempts", 3)
        speech_script = onboarding_cfg.get("speech_script", [])
        completion_journal = onboarding_cfg.get("completion_journal_any", [])
        context_entries = onboarding_cfg.get("context_menu_entries", [])

        attempt = 0
        while attempt < max_attempts:
            attempt += 1
            Telemetry.info(self.key, "Onboarding attempt", {
                "attempt": attempt,
                "max_attempts": max_attempts
            })

            # Friendly target acquisition in a constrained start area.
            found_friend = GetFriend(onboarding_cfg.get("npc_notorieties", ["Innocent"]))
            Telemetry.debug(self.key, "GetFriend result", {"found_friend": found_friend})

            if found_friend and FindAlias("friend"):
                safe_pathfind(ctx, self.key, "friend", runtime_cfg.get("pathfind_settle_ms", 300))
                safe_use_object(ctx, self.key, "friend", runtime_cfg.get("action_settle_ms", 250))

                gump_state = self._handle_any_gump(ctx)
                if gump_state is not None:
                    return gump_state

                for entry in context_entries:
                    safe_context_menu(ctx, self.key, "friend", entry, runtime_cfg.get("action_settle_ms", 250))
                    gump_state = self._handle_any_gump(ctx)
                    if gump_state is not None:
                        return gump_state

            for line in speech_script:
                safe_speech(ctx, self.key, line, runtime_cfg.get("action_settle_ms", 250))

                complete, complete_text = _journal_has_any(ctx, self.key, completion_journal, 700)
                if complete:
                    Telemetry.info(self.key, "Onboarding completion detected via journal", {
                        "text": complete_text
                    })
                    return "PRECHECK"

                gump_state = self._handle_any_gump(ctx)
                if gump_state is not None:
                    return gump_state

        if onboarding_cfg.get("require_complete", True):
            ctx.fail(self.key, "Onboarding did not complete", {
                "attempts": max_attempts
            })
            return "FATAL_STOP"

        return "PRECHECK"


class PrecheckState(State):
    key = "PRECHECK"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering PRECHECK")

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        if not guard_weight_ok(ctx, self.key):
            return "RETURN_HOME"

        tool_graphic, tool_hue = _find_usable_tool(ctx)
        has_tool = tool_graphic is not None

        Telemetry.debug(self.key, "Tool availability", {
            "has_tool": has_tool,
            "tool_graphic": hex(tool_graphic) if has_tool else "None",
            "tool_hue": tool_hue if has_tool else "None"
        })

        if not has_tool:
            ctx.fail(self.key, "No configured tool in backpack")
            return "RECOVER"

        return "TRAVEL_TO_NODE"


class TravelToNodeState(State):
    key = "TRAVEL_TO_NODE"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering TRAVEL_TO_NODE")

    def tick(self, ctx):
        destination = _resolve_waypoint(ctx, "resource_node")

        if destination == "self":
            Telemetry.debug(self.key, "Resource waypoint is self; skipping travel")
            return "GATHER"

        if destination in ("", (0, 0, 0)):
            ctx.fail(self.key, "Resource waypoint is not configured", {"destination": destination})
            return "RECOVER"

        if isinstance(destination, tuple):
            Telemetry.info(self.key, "Traveling to coordinates", {
                "x": destination[0],
                "y": destination[1],
                "z": destination[2]
            })
        else:
            Telemetry.info(self.key, "Traveling to alias", {"alias": destination})
            if not guard_alias_available(ctx, self.key, destination):
                return "RECOVER"

        runtime_cfg = ctx.config.get("runtime", {})
        if not safe_pathfind(ctx, self.key, destination, runtime_cfg.get("pathfind_settle_ms", 300)):
            return "RECOVER"

        return "GATHER"


class GatherState(State):
    key = "GATHER"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering GATHER")

    def _do_single_attempt(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        gather_cfg = ctx.config.get("gather", {})

        selected_graphic, selected_hue = _find_usable_tool(ctx)
        if selected_graphic is None:
            ctx.fail(self.key, "No usable gathering tool found in backpack")
            return False

        if not guard_item_exists(ctx, self.key, selected_graphic, "backpack", selected_hue):
            return False

        target_mode = gather_cfg.get("target_mode", "by_resource")

        if target_mode == "by_resource":
            resource_type = gather_cfg.get("resource_type", "Ore")
            if not safe_target_by_resource(
                ctx,
                self.key,
                "found",
                resource_type,
                runtime_cfg.get("action_settle_ms", 250)
            ):
                return False
        else:
            if not safe_use_type(
                ctx,
                self.key,
                selected_graphic,
                selected_hue,
                "backpack",
                runtime_cfg.get("action_settle_ms", 250)
            ):
                return False

            if not safe_wait_for_target(ctx, self.key, runtime_cfg.get("target_timeout_ms", 5000)):
                return False

            if target_mode == "alias":
                target_alias = gather_cfg.get("target_alias", "self")
                if not guard_alias_available(ctx, self.key, target_alias):
                    return False
                if not safe_target(ctx, self.key, target_alias, "alias"):
                    return False
            else:
                tile_target = gather_cfg.get("tile_target", {})
                if not safe_target_tile_offset(
                    ctx,
                    self.key,
                    tile_target.get("xoffset", 0),
                    tile_target.get("yoffset", 0),
                    tile_target.get("zoffset", 0),
                    tile_target.get("itemid", 0)
                ):
                    return False

        journal_timeout = runtime_cfg.get("journal_timeout_ms", 6000)
        success_entries = gather_cfg.get("success_journal_any", [])
        failure_entries = gather_cfg.get("failure_journal_any", [])

        matched_success, success_text = _journal_has_any(ctx, self.key, success_entries, journal_timeout)
        if matched_success:
            Telemetry.info(self.key, "Gather success journal matched", {"text": success_text})
            return True

        matched_fail, fail_text = _journal_has_any(ctx, self.key, failure_entries, 1000)
        if matched_fail:
            ctx.fail(self.key, "Gather failure journal matched", {"text": fail_text})
            return False

        Telemetry.warn(self.key, "No gather journal match detected")
        return True

    def tick(self, ctx):
        guard_journal_clean(self.key)

        gather_cfg = ctx.config.get("gather", {})
        attempts = gather_cfg.get("attempts_per_cycle", 5)

        attempt_index = 0
        while attempt_index < attempts:
            attempt_index += 1
            Telemetry.info(self.key, "Gather attempt", {
                "attempt": attempt_index,
                "attempts_per_cycle": attempts
            })

            if not guard_player_alive(ctx, self.key):
                return "RECOVER"

            if not guard_weight_ok(ctx, self.key):
                return "RETURN_HOME"

            ok = self._do_single_attempt(ctx)
            if not ok:
                return "RECOVER"

        return "RETURN_HOME"


class ReturnHomeState(State):
    key = "RETURN_HOME"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering RETURN_HOME")

    def tick(self, ctx):
        destination = _resolve_waypoint(ctx, "home")
        runtime_cfg = ctx.config.get("runtime", {})

        if destination == "self":
            Telemetry.debug(self.key, "Home waypoint is self; skipping travel")
            return "CRAFT"

        if destination in ("", (0, 0, 0)):
            ctx.fail(self.key, "Home waypoint is not configured", {"destination": destination})
            return "RECOVER"

        if isinstance(destination, tuple):
            Telemetry.info(self.key, "Returning home coordinates", {
                "x": destination[0],
                "y": destination[1],
                "z": destination[2]
            })
        else:
            Telemetry.info(self.key, "Returning home alias", {"alias": destination})
            if not guard_alias_available(ctx, self.key, destination):
                return "RECOVER"

        if not safe_pathfind(ctx, self.key, destination, runtime_cfg.get("pathfind_settle_ms", 300)):
            return "RECOVER"

        return "CRAFT"


class CraftState(State):
    key = "CRAFT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering CRAFT")

    def tick(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        craft_cfg = ctx.config.get("craft", {})

        if not craft_cfg.get("enabled", False):
            Telemetry.info(self.key, "Crafting disabled in config")
            return "DEPOSIT"

        queue = craft_cfg.get("queue", [])
        if len(queue) == 0:
            Telemetry.warn(self.key, "Craft queue is empty, skipping craft")
            return "DEPOSIT"

        guard_journal_clean(self.key)

        for entry in queue:
            entry_name = entry.get("name", "Unnamed craft step")
            Telemetry.info(self.key, "Running craft step", {"step": entry_name})

            skill_name = entry.get("skill", "")
            if skill_name:
                safe_use_skill(ctx, self.key, skill_name, runtime_cfg.get("action_settle_ms", 250))

            tool_alias = entry.get("use_tool_alias", "")
            if tool_alias:
                if not guard_alias_available(ctx, self.key, tool_alias):
                    return "RECOVER"
                safe_use_object(ctx, self.key, tool_alias, runtime_cfg.get("action_settle_ms", 250))

            if entry.get("requires_target", False):
                timeout_ms = entry.get("target_timeout_ms", runtime_cfg.get("target_timeout_ms", 5000))
                if not safe_wait_for_target(ctx, self.key, timeout_ms):
                    return "RECOVER"
                target_alias = entry.get("target_alias", "self")
                if not safe_target(ctx, self.key, target_alias, "alias"):
                    return "RECOVER"

            success_entries = craft_cfg.get("success_journal_any", [])
            matched_success, success_text = _journal_has_any(ctx, self.key, success_entries, runtime_cfg.get("journal_timeout_ms", 6000))
            if matched_success:
                Telemetry.info(self.key, "Craft success journal matched", {"text": success_text})
                continue

            failure_entries = craft_cfg.get("failure_journal_any", [])
            failed, failed_text = _journal_has_any(ctx, self.key, failure_entries, 1000)
            if failed:
                ctx.fail(self.key, "Craft failure journal matched", {"text": failed_text})
                return "RECOVER"

        return "DEPOSIT"


class DepositState(State):
    key = "DEPOSIT"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering DEPOSIT")

    def tick(self, ctx):
        inventory_cfg = ctx.config.get("inventory", {})

        if not inventory_cfg.get("deposit_enabled", False):
            Telemetry.info(self.key, "Deposit disabled in config")
            return "RESUPPLY"

        destination_alias = "storage_container"

        if not guard_alias_available(ctx, self.key, destination_alias):
            Telemetry.warn(self.key, "Storage alias not available, skipping deposit")
            return "RESUPPLY"

        graphics = inventory_cfg.get("deposit_item_graphics", [])
        hue = inventory_cfg.get("deposit_item_hue", -1)

        for graphic in graphics:
            amount = CountType(graphic, "backpack", hue)
            if amount <= 0:
                Telemetry.debug(self.key, "No item to deposit", {"graphic": hex(graphic)})
                continue

            safe_move_type(ctx, self.key, graphic, "backpack", destination_alias, hue, amount)
            Pause(250)

        return "RESUPPLY"


class ResupplyState(State):
    key = "RESUPPLY"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering RESUPPLY")

    def tick(self, ctx):
        inventory_cfg = ctx.config.get("inventory", {})

        if not inventory_cfg.get("resupply_enabled", False):
            Telemetry.info(self.key, "Resupply disabled in config")
            return "TRAVEL_TO_NODE"

        rules = inventory_cfg.get("resupply", [])

        for rule in rules:
            graphic = rule.get("graphic", 0)
            hue = rule.get("hue", -1)
            minimum = rule.get("minimum", 1)
            restock_to = rule.get("restock_to", minimum)
            source_alias = rule.get("source_alias", "storage_container")

            if not guard_alias_available(ctx, self.key, source_alias):
                Telemetry.warn(self.key, "Resupply source alias missing", {
                    "source_alias": source_alias
                })
                continue

            backpack_amount = CountType(graphic, "backpack", hue)
            Telemetry.debug(self.key, "Resupply check", {
                "graphic": hex(graphic),
                "backpack_amount": backpack_amount,
                "minimum": minimum,
                "restock_to": restock_to
            })

            if backpack_amount >= minimum:
                continue

            needed = restock_to - backpack_amount
            storage_amount = CountType(graphic, source_alias, hue)

            if storage_amount <= 0:
                ctx.fail(self.key, "Resupply source missing item", {
                    "graphic": hex(graphic),
                    "source_alias": source_alias
                })
                return "RECOVER"

            move_amount = needed
            if needed > storage_amount:
                move_amount = storage_amount

            safe_move_type(ctx, self.key, graphic, source_alias, "backpack", hue, move_amount)
            Pause(250)

        return "TRAVEL_TO_NODE"


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
        Telemetry.warn(self.key, "Retrying failed state", {
            "failed_state": failed_state,
            "retry_count": retry_count,
            "max_retries": max_retries
        })

        # Recovery actions to clear known sticky client states.
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

        if failed_state == "ONBOARDING_INTERACT":
            return "ONBOARDING_INTERACT"

        return "PRECHECK"


class FatalStopState(State):
    key = "FATAL_STOP"

    def enter(self, ctx):
        Telemetry.fatal(self.key, "Entering FATAL_STOP", {
            "last_error_state": ctx.last_error_state,
            "last_error": ctx.last_error,
            "tick_count": ctx.tick_count
        })

        # Explicitly stop all active combat intent and macro execution.
        WarMode("off")
        CancelTarget()

        ctx.stop("Fail-safe stop policy triggered")
        Stop()

    def tick(self, ctx):
        return None


def _build_states():
    return {
        "BOOTSTRAP": BootstrapState(),
        "ONBOARDING_INTERACT": OnboardingInteractState(),
        "PRECHECK": PrecheckState(),
        "TRAVEL_TO_NODE": TravelToNodeState(),
        "GATHER": GatherState(),
        "RETURN_HOME": ReturnHomeState(),
        "CRAFT": CraftState(),
        "DEPOSIT": DepositState(),
        "RESUPPLY": ResupplyState(),
        "RECOVER": RecoverState(),
        "FATAL_STOP": FatalStopState()
    }


def run_resource_craft_controller(config):
    published_api = publish_known_ca_api(globals())
    Telemetry.debug("MAIN", "Published ClassicAssist API symbols", {"count": published_api})
    Telemetry.info("MAIN", "Starting ResourceCraftController")

    ctx = BotContext(config)
    states = _build_states()

    machine = StateMachine(ctx, states, "BOOTSTRAP")
    machine.run()

    Telemetry.info("MAIN", "ResourceCraftController finished", {
        "tick_count": ctx.tick_count,
        "transition_count": ctx.transition_count,
        "last_error_state": ctx.last_error_state,
        "last_error": ctx.last_error
    })


run_resource_craft_controller(BOT_CONFIG)



