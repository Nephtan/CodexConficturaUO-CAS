# Name: Confictura Gypsy Onboarding Controller
# Description: Executes autonomous gypsy tent onboarding (race shelf, rename journal, Thuvia, tarot) via deterministic step table.
# Author: ChatGPT Codex
# Shard: Confictura

import sys


def _purge_confictura_import_cache():
    purge_keys = []
    for module_name in sys.modules.keys():
        try:
            if module_name == "gypsy_onboarding_config" or module_name.startswith("confictura_bot"):
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
from confictura_bot.safe_api import safe_pathfind
from confictura_bot.safe_api import safe_speech
from confictura_bot.safe_api import safe_use_object
from confictura_bot.safe_api import safe_context_menu
from confictura_bot.safe_api import safe_click_object
from confictura_bot.safe_api import safe_wait_for_context
from confictura_bot.safe_api import safe_wait_for_gump_any
from confictura_bot.safe_api import safe_wait_for_journal_any
from confictura_bot.safe_api import safe_reply_gump
from confictura_bot.telemetry import Telemetry
from confictura_bot.gump_ids import gump_hex
from confictura_bot.gump_ids import resolve_gump_id
from gypsy_onboarding_config import BOT_CONFIG
from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.ca_shim import publish_known_ca_api

bind_ca_api(globals())


MODE_TO_BUTTON = {
    "NEUTRAL": 0,
    "PVP": 1,
    "PVE": 2
}


def _copy_dict(value):
    copied = {}
    if not isinstance(value, dict):
        return copied
    for key in value.keys():
        copied[key] = value[key]
    return copied


def _normalize_tokens(values):
    if values is None:
        return []
    if not isinstance(values, list) and not isinstance(values, tuple):
        return []

    lowered = []
    for token in values:
        if token is None:
            continue
        text = str(token).strip().lower()
        if text == "":
            continue
        lowered.append(text)
    return lowered


def _name_matches(candidate_name, tokens):
    if len(tokens) == 0:
        return True

    lowered = str(candidate_name).lower()
    for token in tokens:
        if token in lowered:
            return True
    return False


def _resolve_world_ref(ctx, key_name, default_value=None):
    return ctx.config.get("world_refs", {}).get(key_name, default_value)


def _self_tile():
    return (int(X("self")), int(Y("self")), int(Z("self")))


def _is_on_tile(tile):
    if not isinstance(tile, tuple) or len(tile) != 3:
        return False
    x_self, y_self, z_self = _self_tile()
    return x_self == int(tile[0]) and y_self == int(tile[1])


def _ensure_on_ref_tile(ctx, state_name, ref_name, runtime_cfg):
    destination = _resolve_world_ref(ctx, ref_name)
    if not isinstance(destination, tuple) or len(destination) != 3:
        ctx.fail(state_name, "Invalid waypoint reference", {"ref": ref_name})
        return False

    max_attempts = int(runtime_cfg.get("path_reissue_max_attempts", 5))
    path_wait_loops = int(runtime_cfg.get("path_wait_loops", 80))
    settle_ms = int(runtime_cfg.get("pathfind_settle_ms", 350))

    attempt = 0
    while attempt < max_attempts:
        if _is_on_tile(destination):
            return True

        attempt += 1
        Telemetry.debug(state_name, "Pathing attempt to tile", {
            "ref": ref_name,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "target_x": destination[0],
            "target_y": destination[1],
            "target_z": destination[2]
        })

        if not safe_pathfind(ctx, state_name, destination, settle_ms):
            return False

        loop = 0
        while loop < path_wait_loops:
            loop += 1
            if not Pathfinding():
                break
            Pause(50)

        Pause(50)

    x_self, y_self, z_self = _self_tile()
    ctx.fail(state_name, "Unable to reach required tile", {
        "ref": ref_name,
        "target_x": destination[0],
        "target_y": destination[1],
        "target_z": destination[2],
        "self_x": x_self,
        "self_y": y_self,
        "self_z": z_self
    })
    return False


def _distance_to_tile_xy(tile):
    if not isinstance(tile, tuple) or len(tile) < 2:
        return -1

    try:
        return int(Distance(int(tile[0]), int(tile[1])))
    except Exception:
        return -1


def _build_adjacent_tiles(tile, max_radius):
    if not isinstance(tile, tuple) or len(tile) != 3:
        return []

    target_x = int(tile[0])
    target_y = int(tile[1])
    target_z = int(tile[2])

    radius_limit = int(max_radius)
    if radius_limit < 1:
        radius_limit = 1

    candidates = []
    seen = {}

    radius = 1
    while radius <= radius_limit:
        dx = -radius
        while dx <= radius:
            dy = -radius
            while dy <= radius:
                if dx == 0 and dy == 0:
                    dy += 1
                    continue

                if max(abs(dx), abs(dy)) != radius:
                    dy += 1
                    continue

                key = (target_x + dx, target_y + dy, target_z)
                if key not in seen:
                    seen[key] = True
                    candidates.append(key)
                dy += 1
            dx += 1
        radius += 1

    return candidates


def _step_off_exact_tile(ctx, state_name, destination, runtime_cfg, desired_distance):
    settle_ms = int(runtime_cfg.get("pathfind_settle_ms", 350))
    path_wait_loops = int(runtime_cfg.get("path_wait_loops", 80))

    adjacent_tiles = _build_adjacent_tiles(destination, desired_distance)
    if len(adjacent_tiles) == 0:
        return False

    Telemetry.debug(state_name, "Attempting sidestep from exact tile", {
        "candidate_count": len(adjacent_tiles),
        "target_x": destination[0],
        "target_y": destination[1],
        "target_z": destination[2],
        "desired_distance": desired_distance
    })

    for tile in adjacent_tiles:
        Telemetry.debug(state_name, "Sidestep candidate", {
            "candidate_x": tile[0],
            "candidate_y": tile[1],
            "candidate_z": tile[2]
        })

        safe_pathfind(
            ctx,
            state_name,
            tile,
            settle_ms,
            None,
            None,
            False
        )

        loop = 0
        while loop < path_wait_loops:
            loop += 1
            if not Pathfinding():
                break
            Pause(50)

        Pause(50)

        current_distance = _distance_to_tile_xy(destination)
        if current_distance > 0 and current_distance <= int(desired_distance):
            Telemetry.info(state_name, "Sidestep complete", {
                "distance": current_distance,
                "desired_distance": desired_distance
            })
            return True

    return False


def _ensure_near_ref_tile(ctx, state_name, ref_name, runtime_cfg, desired_distance, avoid_exact_tile=False):
    destination = _resolve_world_ref(ctx, ref_name)
    if not isinstance(destination, tuple) or len(destination) != 3:
        ctx.fail(state_name, "Invalid waypoint reference", {"ref": ref_name})
        return False

    desired = int(desired_distance)
    if desired < 1:
        desired = 1

    max_attempts = int(runtime_cfg.get("path_reissue_max_attempts", 5))
    path_wait_loops = int(runtime_cfg.get("path_wait_loops", 80))
    settle_ms = int(runtime_cfg.get("pathfind_settle_ms", 350))

    attempt = 0
    while attempt < max_attempts:
        current_distance = _distance_to_tile_xy(destination)
        if current_distance >= 0 and current_distance <= desired:
            if not avoid_exact_tile or current_distance > 0:
                return True

            if current_distance == 0 and avoid_exact_tile:
                Telemetry.warn(state_name, "Standing on exact tile; attempting sidestep", {
                    "ref": ref_name,
                    "desired_distance": desired
                })
                if _step_off_exact_tile(ctx, state_name, destination, runtime_cfg, desired):
                    return True
                break

        attempt += 1
        Telemetry.debug(state_name, "Pathing attempt near tile", {
            "ref": ref_name,
            "attempt": attempt,
            "max_attempts": max_attempts,
            "target_x": destination[0],
            "target_y": destination[1],
            "target_z": destination[2],
            "desired_distance": desired,
            "avoid_exact_tile": avoid_exact_tile,
            "current_distance": current_distance
        })

        safe_pathfind(
            ctx,
            state_name,
            destination,
            settle_ms,
            True,
            desired,
            False
        )

        loop = 0
        while loop < path_wait_loops:
            loop += 1
            if not Pathfinding():
                break
            Pause(50)

        Pause(50)

    final_distance = _distance_to_tile_xy(destination)
    x_self, y_self, z_self = _self_tile()
    ctx.fail(state_name, "Unable to reach required proximity to tile", {
        "ref": ref_name,
        "target_x": destination[0],
        "target_y": destination[1],
        "target_z": destination[2],
        "desired_distance": desired,
        "avoid_exact_tile": avoid_exact_tile,
        "distance": final_distance,
        "self_x": x_self,
        "self_y": y_self,
        "self_z": z_self
    })
    return False

def _expected_gump_ids_for_step(ctx, step):
    onboarding_cfg = ctx.config.get("onboarding", {})
    overrides = onboarding_cfg.get("gump_id_overrides", {})

    resolved = []

    for key_name in step.get("expect_gump_keys", []):
        gump_id = resolve_gump_id({"gump_key": key_name}, overrides)
        if gump_id > 0 and gump_id not in resolved:
            resolved.append(gump_id)

    for explicit_id in step.get("expect_gump_ids", []):
        try:
            parsed = int(explicit_id)
        except Exception:
            parsed = 0
        if parsed > 0 and parsed not in resolved:
            resolved.append(parsed)

    return resolved


def _find_mobile_alias_by_name_tokens(ctx, state_name, tokens, search_range):
    world_cfg = ctx.config.get("world_refs", {})
    scan_order = str(world_cfg.get("mobile_search_order", "Next"))
    max_scan = int(world_cfg.get("mobile_search_max_scan", 40))

    selectors = [
        {
            "label": "enemy_any",
            "fn": GetEnemy,
            "alias": "enemy",
            "notorieties": ["Any"]
        },
        {
            "label": "friend_any",
            "fn": GetFriend,
            "alias": "friend",
            "notorieties": ["Any"]
        }
    ]

    observed_names = []

    for selector in selectors:
        scanned = 0
        seen_serials = {}
        ClearIgnoreList()

        Telemetry.debug(state_name, "Scanning mobiles", {
            "selector": selector.get("label", "unknown"),
            "scan_order": scan_order,
            "search_range": search_range,
            "max_scan": max_scan
        })

        while scanned < max_scan:
            found = selector["fn"](selector["notorieties"], "Any", scan_order, "Any", search_range)
            if not found:
                break

            alias_name = selector["alias"]

            serial_value = 0
            try:
                serial_value = int(GetAlias(alias_name))
            except Exception:
                serial_value = 0

            if serial_value <= 0:
                break

            if serial_value in seen_serials:
                IgnoreObject(alias_name)
                scanned += 1
                Pause(10)
                continue

            seen_serials[serial_value] = True

            candidate_name = Name(alias_name)
            if candidate_name is None:
                candidate_name = ""

            if len(observed_names) < 12:
                observed_names.append(str(candidate_name))

            if _name_matches(candidate_name, tokens):
                ctx.set_alias("onboarding_mobile", serial_value)
                Telemetry.info(state_name, "Matched mobile", {
                    "serial": hex(serial_value),
                    "name": candidate_name,
                    "distance": Distance("onboarding_mobile"),
                    "selector": selector.get("label", "unknown")
                })
                ClearIgnoreList()
                return "onboarding_mobile"

            IgnoreObject(alias_name)
            scanned += 1
            Pause(10)

        ClearIgnoreList()

    ctx.fail(state_name, "Unable to locate required mobile", {
        "name_tokens": "|".join(tokens),
        "search_range": search_range,
        "scan_order": scan_order,
        "observed_names": "|".join(observed_names)
    })
    return None

def _find_object_alias(ctx, state_name, graphic, hue, search_range, name_tokens=None, find_location=None):
    world_cfg = ctx.config.get("world_refs", {})
    max_scan = int(world_cfg.get("object_search_max_scan", 40))

    normalized_tokens = _normalize_tokens(name_tokens)

    found = False
    matched_hue = -1
    scanned = 0
    observed_names = []

    ClearIgnoreList()

    while scanned < max_scan:
        found = False
        try:
            if find_location in (None, ""):
                if int(hue) == -1:
                    found = FindType(graphic, search_range)
                else:
                    found = FindType(graphic, search_range, -1, int(hue))
            else:
                if int(hue) == -1:
                    found = FindType(graphic, search_range, find_location)
                else:
                    found = FindType(graphic, search_range, find_location, int(hue))
        except Exception:
            found = False

        if not found:
            break

        try:
            matched_hue = int(Hue("found"))
        except Exception:
            matched_hue = -2

        if int(hue) != -1 and int(matched_hue) != int(hue):
            IgnoreObject("found")
            scanned += 1
            Pause(10)
            continue

        candidate_name = ""
        try:
            candidate_name = Name("found")
        except Exception:
            candidate_name = ""

        if candidate_name is None:
            candidate_name = ""

        if len(observed_names) < 12:
            observed_names.append(str(candidate_name))

        if len(normalized_tokens) > 0 and not _name_matches(candidate_name, normalized_tokens):
            IgnoreObject("found")
            scanned += 1
            Pause(10)
            continue

        break

    ClearIgnoreList()

    if not found:
        ctx.fail(state_name, "Unable to locate required object", {
            "graphic": hex(graphic),
            "hue": hue,
            "range": search_range,
            "name_tokens": "|".join(normalized_tokens),
            "find_location": str(find_location),
            "observed_names": "|".join(observed_names)
        })
        return None

    if int(hue) != -1 and int(matched_hue) != int(hue):
        ctx.fail(state_name, "Object hue mismatch for required object", {
            "graphic": hex(graphic),
            "required_hue": int(hue),
            "matched_hue": int(matched_hue),
            "range": search_range,
            "name_tokens": "|".join(normalized_tokens)
        })
        return None

    try:
        serial_value = int(GetAlias("found"))
    except Exception:
        serial_value = 0

    if serial_value <= 0:
        ctx.fail(state_name, "FindType returned invalid object alias", {
            "graphic": hex(graphic),
            "hue": hue,
            "name_tokens": "|".join(normalized_tokens)
        })
        return None

    ctx.set_alias("onboarding_object", serial_value)
    Telemetry.info(state_name, "Matched object", {
        "serial": hex(serial_value),
        "graphic": hex(graphic),
        "hue": hue,
        "distance": Distance("onboarding_object"),
        "name_tokens": "|".join(normalized_tokens)
    })

    return "onboarding_object"

class BootstrapState(State):
    key = "BOOTSTRAP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering BOOTSTRAP")

    def tick(self, ctx):
        required_sections = ["runtime", "safety", "onboarding", "world_refs", "steps"]
        for section_name in required_sections:
            if section_name not in ctx.config:
                ctx.fail(self.key, "Missing config section", {"section": section_name})
                return "FATAL_STOP"

        steps = ctx.config.get("steps", [])
        if len(steps) == 0:
            ctx.fail(self.key, "No onboarding steps configured")
            return "FATAL_STOP"

        ctx.onboarding_index = 0
        ctx.onboarding_started_name = Name("self")
        ctx.onboarding_last_rename_name = ""
        ctx.onboarding_rename_attempts = 0

        Telemetry.info(self.key, "Bootstrap ready", {
            "initial_name": ctx.onboarding_started_name,
            "step_count": len(steps)
        })

        return "STEP_EXECUTOR"


class StepExecutorState(State):
    key = "STEP_EXECUTOR"

    def enter(self, ctx):
        Telemetry.info(self.key, "Entering STEP_EXECUTOR")

    def _step_enabled(self, ctx, step):
        flag_name = step.get("enabled_flag")
        if flag_name is None or flag_name == "":
            return True
        return bool(ctx.config.get("onboarding", {}).get(flag_name, False))

    def _resolve_rule(self, ctx, raw_rule):
        onboarding_cfg = ctx.config.get("onboarding", {})
        rule = _copy_dict(raw_rule)

        config_button_key = rule.get("button_from_config")
        if config_button_key:
            rule["button_id"] = int(onboarding_cfg.get(config_button_key, rule.get("button_id", 0)))

        if rule.get("button_from_mode", False):
            mode_name = str(onboarding_cfg.get("thuvia_mode", "NEUTRAL")).upper()
            rule["button_id"] = MODE_TO_BUTTON.get(mode_name, 0)

        return rule

    def _wait_and_apply_rule(self, ctx, step_name, rule):
        runtime_cfg = ctx.config.get("runtime", {})
        onboarding_cfg = ctx.config.get("onboarding", {})
        overrides = onboarding_cfg.get("gump_id_overrides", {})

        timeout_ms = int(runtime_cfg.get("gump_timeout_ms", 3200))

        expected_id = resolve_gump_id(rule, overrides)
        gump_open = False
        if expected_id > 0:
            gump_open = GumpExists(expected_id)

        saw_packet = False
        if not gump_open:
            saw_packet = safe_wait_for_gump_any(ctx, step_name, timeout_ms)
            if not saw_packet:
                Telemetry.warn(step_name, "No incoming gump packet during wait window", {
                    "rule": rule.get("name", ""),
                    "expected_gump_id": gump_hex(expected_id),
                    "timeout_ms": timeout_ms
                })

        gump_result = handle_configured_gumps(
            ctx,
            step_name,
            [rule],
            [rule],
            overrides
        )

        if gump_result.get("status") == "matched":
            Pause(runtime_cfg.get("action_settle_ms", 250))
            return True

        if bool(rule.get("allow_any_open_reply", False)):
            fallback_button_id = int(rule.get("button_id", 0))
            fallback_switches = rule.get("switches", [])
            fallback_text_entries = rule.get("text_entries", {})

            Telemetry.warn(step_name, "Attempting any-open gump reply fallback by policy", {
                "rule": rule.get("name", ""),
                "button_id": fallback_button_id,
                "expected_gump_id": gump_hex(expected_id),
                "saw_packet": saw_packet,
                "gump_open": gump_open
            })

            fallback_ok = False
            try:
                fallback_ok = safe_reply_gump(
                    ctx,
                    step_name,
                    0,
                    fallback_button_id,
                    0,
                    fallback_switches,
                    fallback_text_entries
                )
            except Exception as ex:
                fallback_ok = False
                Telemetry.warn(step_name, "Any-open gump reply fallback threw exception", {
                    "exception": str(ex),
                    "rule": rule.get("name", "")
                })

            if fallback_ok:
                Pause(runtime_cfg.get("action_settle_ms", 250))
                Telemetry.warn(step_name, "Any-open gump reply fallback succeeded", {
                    "rule": rule.get("name", ""),
                    "button_id": fallback_button_id
                })
                return True

        if (not gump_open) and (not saw_packet):
            discovered_ids = gump_result.get("discovered_ids", [])
            discovered_hex = []
            for discovered_id in discovered_ids:
                discovered_hex.append(gump_hex(discovered_id))

            ctx.fail(step_name, "Expected gump did not arrive", {
                "rule": rule.get("name", ""),
                "expected_gump_id": gump_hex(expected_id),
                "discovered_open_ids": "|".join(discovered_hex)
            })
            return False

        if onboarding_cfg.get("unknown_gump_is_fatal", True):
            ctx.fail(step_name, "Unknown gump during onboarding", {
                "rule": rule.get("name", ""),
                "resolved_gump_id": gump_hex(gump_result.get("resolved_gump_id", 0))
            })
            return "FATAL_STOP"

        return False

    def _execute_move_to_ref(self, ctx, step_name, step):
        runtime_cfg = ctx.config.get("runtime", {})

        ref_name = step.get("ref")
        destination = _resolve_world_ref(ctx, ref_name)
        if not isinstance(destination, tuple) or len(destination) != 3:
            ctx.fail(step_name, "Invalid waypoint reference", {"ref": ref_name})
            return False

        within_distance = step.get("within_distance", None)
        avoid_exact_tile = bool(step.get("avoid_exact_tile", False))

        if within_distance is not None:
            desired_distance = int(within_distance)
            if desired_distance < 1:
                desired_distance = 1

            Telemetry.info(step_name, "Pathfinding near reference", {
                "ref": ref_name,
                "x": destination[0],
                "y": destination[1],
                "z": destination[2],
                "desired_distance": desired_distance,
                "avoid_exact_tile": avoid_exact_tile
            })

            return _ensure_near_ref_tile(
                ctx,
                step_name,
                ref_name,
                runtime_cfg,
                desired_distance,
                avoid_exact_tile
            )

        Telemetry.info(step_name, "Pathfinding to reference", {
            "ref": ref_name,
            "x": destination[0],
            "y": destination[1],
            "z": destination[2]
        })

        return _ensure_on_ref_tile(ctx, step_name, ref_name, runtime_cfg)
    def _execute_mobile_context(self, ctx, step_name, step):
        runtime_cfg = ctx.config.get("runtime", {})

        required_ref = step.get("require_ref", "")
        if required_ref != "":
            if not _ensure_on_ref_tile(ctx, step_name, required_ref, runtime_cfg):
                return False

        token_ref = step.get("name_any_ref")
        tokens = _normalize_tokens(_resolve_world_ref(ctx, token_ref, []))
        search_range = int(_resolve_world_ref(ctx, "mobile_search_range", 14))

        mobile_alias = _find_mobile_alias_by_name_tokens(ctx, step_name, tokens, search_range)
        if mobile_alias is None:
            return False

        # Context actions are most reliable when not in combat targeting mode.
        WarMode("off")
        CancelTarget()

        target_obj = mobile_alias
        try:
            mobile_serial = int(GetAlias(mobile_alias))
        except Exception:
            mobile_serial = 0
        if mobile_serial > 0:
            target_obj = mobile_serial

        context_timeout = int(runtime_cfg.get("context_timeout_ms", 3000))
        action_settle_ms = int(runtime_cfg.get("action_settle_ms", 250))
        expect_gump = bool(step.get("expect_gump_after_context", False))
        post_context_gump_timeout_ms = int(step.get("post_context_gump_timeout_ms", runtime_cfg.get("gump_timeout_ms", 3200)))
        allow_context_success_without_packet = bool(
            step.get(
                "allow_context_success_without_packet",
                runtime_cfg.get("allow_context_success_without_packet", True)
            )
        )
        expected_ids = _expected_gump_ids_for_step(ctx, step)

        candidates = []
        configured_candidates = step.get("context_entries", [])
        if isinstance(configured_candidates, list) or isinstance(configured_candidates, tuple):
            for candidate in configured_candidates:
                candidates.append(candidate)
        else:
            entry_name = str(step.get("entry_name", "")).strip()
            entry_index = int(step.get("entry_index", 1))
            if entry_name != "":
                candidates.append(entry_name)
            candidates.append(entry_index)

        has_talk_candidate = False
        for candidate in candidates:
            if str(candidate).strip().lower() == "talk":
                has_talk_candidate = True
                break

        if has_talk_candidate and 6146 not in candidates:
            candidates.append(6146)
            Telemetry.debug(step_name, "Expanded context candidates with cliloc id", {"added": 6146})

        tried = []

        if expect_gump and len(expected_ids) > 0:
            open_expected = []
            for expected_id in expected_ids:
                if GumpExists(expected_id):
                    open_expected.append(gump_hex(expected_id))

            if len(open_expected) > 0:
                Telemetry.info(step_name, "Expected gump already open before context action", {
                    "open_expected_ids": "|".join(open_expected)
                })
                return True

        for candidate in candidates:
            if candidate in tried:
                continue
            tried.append(candidate)

            safe_click_object(ctx, step_name, target_obj, action_settle_ms)

            ok = safe_wait_for_context(
                ctx,
                step_name,
                target_obj,
                candidate,
                context_timeout,
                False
            )

            if ok:
                Pause(action_settle_ms)

                if not expect_gump:
                    return True

                if safe_wait_for_gump_any(ctx, step_name, post_context_gump_timeout_ms):
                    return True

                open_expected = []
                for expected_id in expected_ids:
                    if GumpExists(expected_id):
                        open_expected.append(gump_hex(expected_id))

                if len(open_expected) > 0:
                    Telemetry.warn(step_name, "Expected gump already open despite no packet wait hit", {
                        "candidate": candidate,
                        "open_expected_ids": "|".join(open_expected),
                        "source": "WaitForContext"
                    })
                    return True

            numeric_candidate = None
            try:
                numeric_candidate = int(candidate)
            except Exception:
                numeric_candidate = None

            if numeric_candidate is not None:
                Telemetry.debug(step_name, "Direct ContextMenu attempt", {
                    "candidate": numeric_candidate,
                    "object": target_obj
                })

                safe_click_object(ctx, step_name, target_obj, action_settle_ms)

                safe_context_menu(
                    ctx,
                    step_name,
                    target_obj,
                    numeric_candidate,
                    action_settle_ms
                )

                if not expect_gump:
                    return True

                if safe_wait_for_gump_any(ctx, step_name, post_context_gump_timeout_ms):
                    return True

                open_expected = []
                for expected_id in expected_ids:
                    if GumpExists(expected_id):
                        open_expected.append(gump_hex(expected_id))

                if len(open_expected) > 0:
                    Telemetry.warn(step_name, "Expected gump already open despite no packet wait hit", {
                        "candidate": numeric_candidate,
                        "open_expected_ids": "|".join(open_expected),
                        "source": "ContextMenu"
                    })
                    return True

            Telemetry.warn(step_name, "Context candidate did not produce gump", {
                "candidate": candidate,
                "timeout_ms": post_context_gump_timeout_ms,
                "expected_ids": "|".join([gump_hex(x) for x in expected_ids])
            })

        if expect_gump:
            open_expected = []
            for expected_id in expected_ids:
                if GumpExists(expected_id):
                    open_expected.append(gump_hex(expected_id))

            if len(open_expected) > 0:
                Telemetry.warn(step_name, "Expected gump already open after context retries", {
                    "open_expected_ids": "|".join(open_expected)
                })
                return True

            if allow_context_success_without_packet and len(tried) > 0:
                Telemetry.warn(step_name, "No gump packet observed after context attempts; advancing by policy", {
                    "tried": "|".join([str(x) for x in tried]),
                    "timeout_ms": post_context_gump_timeout_ms,
                    "expected_ids": "|".join([gump_hex(x) for x in expected_ids]),
                    "policy": "allow_context_success_without_packet"
                })
                return True

            ctx.fail(step_name, "No gump arrived after context attempts", {
                "tried": "|".join([str(x) for x in tried]),
                "timeout_ms": post_context_gump_timeout_ms,
                "expected_ids": "|".join([gump_hex(x) for x in expected_ids]),
                "policy_allow_context_success_without_packet": allow_context_success_without_packet
            })
            return False

        ctx.fail(step_name, "No context entry succeeded", {
            "tried": "|".join([str(x) for x in tried]),
            "timeout_ms": context_timeout
        })
        return False
    def _resolve_object_refs(self, ctx, step):
        world_cfg = ctx.config.get("world_refs", {})

        graphic = step.get("graphic")
        if graphic is None and step.get("graphic_ref"):
            graphic = world_cfg.get(step.get("graphic_ref"))

        hue = step.get("hue", -1)
        if step.get("hue_ref"):
            hue = world_cfg.get(step.get("hue_ref"), hue)

        search_range = step.get("range", 8)
        if step.get("range_ref"):
            search_range = world_cfg.get(step.get("range_ref"), search_range)

        name_tokens = step.get("name_any", [])
        if step.get("name_any_ref"):
            name_tokens = world_cfg.get(step.get("name_any_ref"), name_tokens)
        normalized_name_tokens = _normalize_tokens(name_tokens)

        find_location = step.get("find_location", None)
        if step.get("find_location_ref"):
            find_location = world_cfg.get(step.get("find_location_ref"), find_location)

        return (int(graphic), int(hue), int(search_range), normalized_name_tokens, find_location)

    def _execute_use_object_ref(self, ctx, step_name, step):
        runtime_cfg = ctx.config.get("runtime", {})

        graphic, hue, search_range, name_tokens, find_location = self._resolve_object_refs(ctx, step)
        if graphic <= 0:
            ctx.fail(step_name, "Invalid object graphic", {"graphic": graphic})
            return False

        object_alias = _find_object_alias(ctx, step_name, graphic, hue, search_range, name_tokens, find_location)
        if object_alias is None:
            return False
        action_settle_ms = int(runtime_cfg.get("action_settle_ms", 250))
        pathfind_settle_ms = int(runtime_cfg.get("pathfind_settle_ms", 350))
        desired_distance = int(step.get("pathfind_desired_distance", runtime_cfg.get("object_use_range", 3)))
        if desired_distance < 1:
            desired_distance = 1

        distance_now = -1
        try:
            distance_now = int(Distance(object_alias))
        except Exception:
            distance_now = -1

        if distance_now > desired_distance:
            path_ok = safe_pathfind(
                ctx,
                step_name,
                object_alias,
                pathfind_settle_ms,
                True,
                desired_distance,
                False
            )

            distance_after = -1
            try:
                distance_after = int(Distance(object_alias))
            except Exception:
                distance_after = -1

            if not path_ok and (distance_after < 0 or distance_after > desired_distance):
                ctx.fail(step_name, "Unable to reach object interaction range", {
                    "object": object_alias,
                    "desired_distance": desired_distance,
                    "distance_after": distance_after
                })
                return False

            if not path_ok:
                Telemetry.warn(step_name, "Pathfind failed but object is already within interaction range", {
                    "object": object_alias,
                    "desired_distance": desired_distance,
                    "distance_after": distance_after
                })
        else:
            Telemetry.debug(step_name, "Skipping pathfind; object already within interaction range", {
                "object": object_alias,
                "distance": distance_now,
                "desired_distance": desired_distance
            })

        if not safe_use_object(ctx, step_name, object_alias, action_settle_ms):
            return False

        return True
    def _execute_speak(self, ctx, step_name, step):
        runtime_cfg = ctx.config.get("runtime", {})
        line = step.get("text", "")
        if line == "":
            ctx.fail(step_name, "Speak step missing text")
            return False

        return safe_speech(ctx, step_name, line, runtime_cfg.get("action_settle_ms", 250))

    def _execute_gump_rule(self, ctx, step_name, step):
        raw_rule = step.get("rule", {})
        rule = self._resolve_rule(ctx, raw_rule)

        wait_result = self._wait_and_apply_rule(ctx, step_name, rule)
        return wait_result

    def _rename_via_journal(self, ctx, step_name):
        runtime_cfg = ctx.config.get("runtime", {})
        onboarding_cfg = ctx.config.get("onboarding", {})

        old_name = Name("self")
        desired_names = onboarding_cfg.get("rename_desired_names", [])

        if len(desired_names) == 0:
            ctx.fail(step_name, "Rename enabled but no rename_desired_names configured")
            return False

        desired_match = False
        for candidate_name in desired_names:
            if str(candidate_name).lower() == str(old_name).lower():
                desired_match = True
                break

        if desired_match:
            Telemetry.info(step_name, "Current name already acceptable", {"name": old_name})
            return True

        rename_ref = _resolve_world_ref(ctx, "rename_journal_spot")
        if isinstance(rename_ref, tuple) and len(rename_ref) == 3:
            Telemetry.info(step_name, "Pathfinding near Visitor Journal", {
                "ref": "rename_journal_spot",
                "x": rename_ref[0],
                "y": rename_ref[1],
                "z": rename_ref[2],
                "desired_distance": 2
            })
            if not _ensure_near_ref_tile(ctx, step_name, "rename_journal_spot", runtime_cfg, 2, False):
                return False
        rename_rule_template = {
            "name": "Rename Character",
            "gump_key": "NAME_ALTER",
            "text_any": [],
            "button_id": 1,
            "wait_timeout_ms": 0,
            "marks_complete": False
        }

        idx = 0
        while idx < len(desired_names):
            candidate = str(desired_names[idx]).strip()
            idx += 1
            if candidate == "":
                continue

            Telemetry.info(step_name, "Rename attempt", {
                "candidate": candidate,
                "attempt_index": idx,
                "total_candidates": len(desired_names)
            })

            use_step = {
                "graphic_ref": "rename_journal_graphic",
                "hue_ref": "rename_journal_hue",
                "range_ref": "rename_journal_range",
                "name_any_ref": "rename_journal_name_any",
                "pathfind_desired_distance": 2
            }
            if not self._execute_use_object_ref(ctx, step_name, use_step):
                continue

            rename_rule = _copy_dict(rename_rule_template)
            rename_rule["text_entries"] = {1: candidate}

            result = self._wait_and_apply_rule(ctx, step_name, rename_rule)
            if result == "FATAL_STOP":
                return "FATAL_STOP"
            if not result:
                continue

            Pause(runtime_cfg.get("rename_apply_pause_ms", 500))
            current_name = Name("self")

            if str(current_name).lower() == str(candidate).lower():
                ctx.onboarding_last_rename_name = current_name
                ctx.onboarding_rename_attempts += 1
                Telemetry.info(step_name, "Rename succeeded", {
                    "new_name": current_name,
                    "old_name": old_name
                })
                return True

            if str(current_name).lower() == str(old_name).lower():
                Telemetry.error(step_name, "Rename no-op detected after gump submit", {
                    "candidate": candidate,
                    "current_name": current_name,
                    "hint": "NameAlterGump dupe-check/no-op path likely triggered"
                })
            else:
                Telemetry.warn(step_name, "Name changed to unexpected value", {
                    "expected": candidate,
                    "actual": current_name
                })
                ctx.onboarding_last_rename_name = current_name
                return True

        if onboarding_cfg.get("rename_allow_skip", False):
            Telemetry.warn(step_name, "Rename failed for all candidates; skipping by policy", {
                "candidate_count": len(desired_names)
            })
            return True

        ctx.fail(step_name, "Rename failed for all candidate names", {
            "candidate_count": len(desired_names),
            "current_name": Name("self")
        })
        return False

    def _execute_wait_journal_any(self, ctx, step_name, step):
        runtime_cfg = ctx.config.get("runtime", {})
        onboarding_cfg = ctx.config.get("onboarding", {})

        fallback_ref = step.get("success_if_far_from_ref", "")
        if fallback_ref != "":
            ref_tile = _resolve_world_ref(ctx, fallback_ref)
            min_distance = int(step.get("success_min_distance", runtime_cfg.get("teleport_min_distance", 20)))
            if min_distance < 1:
                min_distance = 1

            if isinstance(ref_tile, tuple) and len(ref_tile) >= 2:
                distance_from_ref = -1
                try:
                    distance_from_ref = int(Distance(int(ref_tile[0]), int(ref_tile[1])))
                except Exception:
                    distance_from_ref = -1

                if distance_from_ref >= min_distance:
                    Telemetry.info(step_name, "Completion condition met by distance from start area", {
                        "ref": fallback_ref,
                        "distance": distance_from_ref,
                        "min_distance": min_distance
                    })
                    return True

        entries_key = step.get("entries_from_config")
        entries = onboarding_cfg.get(entries_key, [])
        if len(entries) == 0:
            ctx.fail(step_name, "Journal wait step has no entries", {"config_key": entries_key})
            return False

        matched, matched_text = safe_wait_for_journal_any(
            ctx,
            step_name,
            entries,
            runtime_cfg.get("journal_timeout_ms", 4500),
            ""
        )
        if not matched:
            ctx.fail(step_name, "Expected journal completion message missing", {
                "entries": "|".join(entries)
            })
            return False

        Telemetry.info(step_name, "Journal completion matched", {
            "text": matched_text
        })
        return True
    def _execute_step(self, ctx, step):
        step_name = step.get("name", "UNNAMED_STEP")
        action = step.get("action", "")

        if not self._step_enabled(ctx, step):
            Telemetry.info(step_name, "Step skipped by policy", {
                "enabled_flag": step.get("enabled_flag")
            })
            return True

        Telemetry.info(step_name, "Executing onboarding step", {
            "index": ctx.onboarding_index + 1,
            "total_steps": len(ctx.config.get("steps", [])),
            "action": action
        })

        if action == "move_to_ref":
            return self._execute_move_to_ref(ctx, step_name, step)

        if action == "mobile_context":
            return self._execute_mobile_context(ctx, step_name, step)

        if action == "use_object_ref":
            return self._execute_use_object_ref(ctx, step_name, step)

        if action == "speak":
            return self._execute_speak(ctx, step_name, step)

        if action == "gump_rule":
            return self._execute_gump_rule(ctx, step_name, step)

        if action == "rename_via_journal":
            return self._rename_via_journal(ctx, step_name)

        if action == "wait_journal_any":
            return self._execute_wait_journal_any(ctx, step_name, step)

        ctx.fail(step_name, "Unknown step action", {"action": action})
        return False

    def tick(self, ctx):
        if not guard_player_alive(ctx, self.key):
            return "RECOVER"

        steps = ctx.config.get("steps", [])
        if ctx.onboarding_index >= len(steps):
            return "COMPLETE_STOP"

        step = steps[ctx.onboarding_index]
        step_name = step.get("name", "UNNAMED_STEP")

        result = self._execute_step(ctx, step)

        if result == "FATAL_STOP":
            return "FATAL_STOP"

        if result:
            ctx.reset_retry(step_name)
            ctx.onboarding_index += 1

            if ctx.onboarding_index >= len(steps):
                return "COMPLETE_STOP"

            return None

        ctx.last_failed_state = step_name
        return "RECOVER"


class RecoverState(State):
    key = "RECOVER"

    def enter(self, ctx):
        Telemetry.warn(self.key, "Entering RECOVER", {
            "last_failed_state": ctx.last_failed_state,
            "last_error": ctx.last_error,
            "step_index": ctx.onboarding_index
        })

    def tick(self, ctx):
        runtime_cfg = ctx.config.get("runtime", {})
        max_retries = runtime_cfg.get("max_retries_per_state", 3)

        step_name = ctx.last_failed_state
        if step_name is None:
            step_name = "UNKNOWN_STEP"

        retry_count = ctx.increment_retry(step_name)
        Telemetry.warn(self.key, "Retrying onboarding step", {
            "step": step_name,
            "retry_count": retry_count,
            "max_retries": max_retries
        })

        CancelTarget()
        WarMode("off")
        ClearObjectQueue()
        Pause(250)

        if retry_count > max_retries:
            ctx.fail(self.key, "Retry cap exceeded", {
                "step": step_name,
                "retry_count": retry_count,
                "max_retries": max_retries
            })
            return "FATAL_STOP"

        return "STEP_EXECUTOR"


class CompleteStopState(State):
    key = "COMPLETE_STOP"

    def enter(self, ctx):
        Telemetry.info(self.key, "Gypsy onboarding complete", {
            "completed_steps": ctx.onboarding_index,
            "total_steps": len(ctx.config.get("steps", [])),
            "starting_name": ctx.onboarding_started_name,
            "current_name": Name("self"),
            "last_rename": ctx.onboarding_last_rename_name
        })

        ctx.stop("Starting-area onboarding finished")
        Stop()

    def tick(self, ctx):
        return None


class FatalStopState(State):
    key = "FATAL_STOP"

    def enter(self, ctx):
        Telemetry.fatal(self.key, "Entering FATAL_STOP", {
            "last_error_state": ctx.last_error_state,
            "last_error": ctx.last_error,
            "failed_step": ctx.last_failed_state,
            "step_index": ctx.onboarding_index
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
        "STEP_EXECUTOR": StepExecutorState(),
        "RECOVER": RecoverState(),
        "COMPLETE_STOP": CompleteStopState(),
        "FATAL_STOP": FatalStopState()
    }


def run_gypsy_onboarding_controller(config):
    published_api = publish_known_ca_api(globals())
    Telemetry.debug("MAIN", "Published ClassicAssist API symbols", {"count": published_api})
    Telemetry.info("MAIN", "Starting GypsyOnboardingController")

    ctx = BotContext(config)
    states = _build_states()

    machine = StateMachine(ctx, states, "BOOTSTRAP")
    machine.run()

    Telemetry.info("MAIN", "GypsyOnboardingController finished", {
        "tick_count": ctx.tick_count,
        "transition_count": ctx.transition_count,
        "last_error_state": ctx.last_error_state,
        "last_error": ctx.last_error,
        "completed_steps": getattr(ctx, "onboarding_index", 0)
    })


run_gypsy_onboarding_controller(BOT_CONFIG)

