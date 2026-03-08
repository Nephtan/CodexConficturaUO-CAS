# Name: Britain Pathing RnD Config
# Description: Defines staged Britain-only route tests and runtime tuning for standalone pathing validation.
# Author: ChatGPT Codex
# Shard: Confictura

from britain_pathing_targets_generated import BRITAIN_CASTLE_FOCUS_TARGETS
from britain_pathing_targets_generated import BRITAIN_LOCATION_INDEX_TARGETS
from britain_pathing_targets_generated import BRITAIN_LOCATION_TARGETS
from britain_pathing_targets_generated import BRITAIN_NPC_SPAWNER_TARGETS
from britain_pathing_targets_generated import BRITAIN_SHOP_SIGN_TARGETS
from britain_pathing_targets_generated import BRITAIN_TARGET_SUMMARY


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


def _slug_text(value, fallback_text):
    raw_text = ""
    try:
        raw_text = str(value)
    except Exception:
        raw_text = fallback_text

    if len(raw_text) <= 0:
        raw_text = fallback_text

    lowered = raw_text.strip().lower()
    if len(lowered) <= 0:
        lowered = fallback_text

    chars = []
    prev_is_sep = False

    index = 0
    while index < len(lowered):
        ch = lowered[index]
        index += 1

        if ("a" <= ch <= "z") or ("0" <= ch <= "9"):
            chars.append(ch)
            prev_is_sep = False
            continue

        if prev_is_sep:
            continue

        chars.append("_")
        prev_is_sep = True

    slug = "".join(chars).strip("_")
    if len(slug) <= 0:
        slug = fallback_text

    if len(slug) > 48:
        slug = slug[:48].strip("_")
        if len(slug) <= 0:
            slug = fallback_text

    return slug


def _copy_dict(source_dict):
    copied = {}
    if not isinstance(source_dict, dict):
        return copied

    for key in source_dict.keys():
        copied[key] = source_dict[key]

    return copied


def _build_route_row(prefix, index_value, target_row, category_name, source_name, route_options):
    destination = target_row.get("destination", (0, 0, 0))
    if not isinstance(destination, tuple):
        destination = tuple(destination)

    target_name = target_row.get("name", "{0}_{1}".format(prefix, index_value))
    slug = _slug_text(target_name, "{0}_{1}".format(prefix, index_value))

    route_name = "{0}_{1:03d}_{2}".format(prefix, index_value, slug)

    row = {
        "name": route_name,
        "destination": destination,
        "expected_reachable": True,
        "category": category_name,
        "source": source_name
    }

    if isinstance(route_options, dict) and len(route_options) > 0:
        row["options"] = _copy_dict(route_options)

    return row


def _append_generated_routes(fixed_routes, route_names, targets, prefix, category_name, source_name, route_options, route_limit, include_predicate=None):
    if not isinstance(targets, list):
        return

    appended = 0
    index = 0
    while index < len(targets):
        target_row = targets[index]
        index += 1

        if not isinstance(target_row, dict):
            continue

        if include_predicate is not None:
            try:
                if not include_predicate(target_row):
                    continue
            except Exception:
                continue

        appended += 1

        if route_limit > 0 and appended > route_limit:
            break

        row = _build_route_row(prefix, appended, target_row, category_name, source_name, route_options)
        fixed_routes.append(row)
        route_names.append(row["name"])


def _build_generated_routes(generated_cfg):
    enabled = _to_bool(generated_cfg.get("enabled", True), True)
    if not enabled:
        return ([], {"shop_signs": [], "npc_spawners": [], "locations": [], "castle_focus": []})

    include_dungeon_spawners = _to_bool(generated_cfg.get("include_dungeon_spawners", True), True)

    shop_limit = _to_int(generated_cfg.get("shop_sign_limit", 0), 0)
    spawner_limit = _to_int(generated_cfg.get("npc_spawner_limit", 0), 0)
    location_limit = _to_int(generated_cfg.get("location_limit", 0), 0)
    location_index_limit = _to_int(generated_cfg.get("location_index_limit", 0), 0)
    castle_limit = _to_int(generated_cfg.get("castle_focus_limit", 0), 0)

    shop_options = {"max_attempts": 90, "max_ms": 90000}
    spawner_options = {"max_attempts": 80, "max_ms": 90000}
    location_options = {"max_attempts": 90, "max_ms": 90000}
    castle_options = {"max_attempts": 80, "max_ms": 80000}

    fixed_routes = []
    stage_routes = {
        "shop_signs": [],
        "npc_spawners": [],
        "locations": [],
        "castle_focus": []
    }

    _append_generated_routes(
        fixed_routes,
        stage_routes["shop_signs"],
        BRITAIN_SHOP_SIGN_TARGETS,
        "shop_sign",
        "shop_sign",
        "generated_shop_sign",
        shop_options,
        shop_limit
    )

    def _spawner_include(row):
        if include_dungeon_spawners:
            return True
        return str(row.get("area", "city")) != "dungeons"

    _append_generated_routes(
        fixed_routes,
        stage_routes["npc_spawners"],
        BRITAIN_NPC_SPAWNER_TARGETS,
        "npc_spawner",
        "npc_spawner",
        "generated_npc_spawner",
        spawner_options,
        spawner_limit,
        _spawner_include
    )

    _append_generated_routes(
        fixed_routes,
        stage_routes["locations"],
        BRITAIN_LOCATION_TARGETS,
        "location",
        "location",
        "generated_location",
        location_options,
        location_limit
    )

    _append_generated_routes(
        fixed_routes,
        stage_routes["locations"],
        BRITAIN_LOCATION_INDEX_TARGETS,
        "location_index",
        "location",
        "generated_location_index",
        location_options,
        location_index_limit
    )

    _append_generated_routes(
        fixed_routes,
        stage_routes["castle_focus"],
        BRITAIN_CASTLE_FOCUS_TARGETS,
        "castle_focus",
        "castle_focus",
        "generated_castle_focus",
        castle_options,
        castle_limit
    )

    return (fixed_routes, stage_routes)


_GENERATED_TARGET_CONFIG = {
    "enabled": True,
    "include_dungeon_spawners": False,
    "include_castle_focus_stage": False,
    "shop_sign_limit": 0,
    "npc_spawner_limit": 0,
    "location_limit": 0,
    "location_index_limit": 0,
    "castle_focus_limit": 0
}

_GENERATED_FIXED_ROUTES, _GENERATED_STAGE_ROUTES = _build_generated_routes(_GENERATED_TARGET_CONFIG)

_BASELINE_FIXED_ROUTES = [
    {
        "name": "sanity_short_north",
        "destination": (3000, 1038, 0),
        "expected_reachable": True,
        "category": "short"
    },
    {
        "name": "sanity_short_east",
        "destination": (3008, 1032, 0),
        "expected_reachable": True,
        "category": "short"
    },
    {
        "name": "sanity_return_origin",
        "destination": (2999, 1030, 0),
        "expected_reachable": True,
        "category": "short"
    },
    {
        "name": "negative_invalid_high_z",
        "destination": (3006, 1108, 120),
        "expected_reachable": False,
        "category": "negative",
        "options": {
            "max_attempts": 40,
            "max_ms": 45000,
            "stall_tolerance": 2
        }
    },
    {
        "name": "negative_probable_blocked_tile",
        "destination": (2998, 1114, 18),
        "expected_reachable": False,
        "category": "negative",
        "options": {
            "max_attempts": 45,
            "max_ms": 45000,
            "stall_tolerance": 2
        }
    }
]

BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 600,
        "max_runtime_ticks": 50000,
        "max_retries_per_state": 0,
        "pause_between_routes_ms": 600
    },
    "pathing_defaults": {
        "within_distance": 2,
        "min_action_delay_ms": 600,
        "settle_ms": 600,
        "max_attempts": 120,
        "max_ms": 120000,
        "min_progress": 1,
        "max_hop_distance": 12,
        "min_hop_distance": 2,
        "hop_backoff_step": 2,
        "hop_recover_step": 1,
        "stall_tolerance": 4,
        "stall_pause_ms": 600,
        "lateral_step": 1,
        "short_step_divisor": 2,
        "enforce_same_map": True,
        "max_evidence_attempts": 80
    },
    "test_harness": {
        "success_rate_target_percent": 90,
        "generated_targets": _copy_dict(_GENERATED_TARGET_CONFIG),
        "generated_target_summary": _copy_dict(BRITAIN_TARGET_SUMMARY),
        "allowed_negative_stop_reasons": [
            "stall_tolerance_exceeded",
            "max_attempts_exceeded",
            "max_ms_exceeded",
            "map_changed"
        ],
        "stages": [
            {
                "name": "stage_1_local_sanity",
                "enabled": True,
                "mode": "fixed",
                "route_names": [
                    "sanity_short_north",
                    "sanity_short_east",
                    "sanity_return_origin"
                ]
            },
            {
                "name": "stage_2_shop_signs",
                "enabled": len(_GENERATED_STAGE_ROUTES.get("shop_signs", [])) > 0,
                "mode": "fixed",
                "route_names": _GENERATED_STAGE_ROUTES.get("shop_signs", [])
            },
            {
                "name": "stage_3_npc_spawners",
                "enabled": len(_GENERATED_STAGE_ROUTES.get("npc_spawners", [])) > 0,
                "mode": "fixed",
                "route_names": _GENERATED_STAGE_ROUTES.get("npc_spawners", [])
            },
            {
                "name": "stage_4_locations_and_castle",
                "enabled": len(_GENERATED_STAGE_ROUTES.get("locations", [])) > 0,
                "mode": "fixed",
                "route_names": _GENERATED_STAGE_ROUTES.get("locations", [])
            },
            {
                "name": "stage_5_castle_focus",
                "enabled": _to_bool(_GENERATED_TARGET_CONFIG.get("include_castle_focus_stage", False), False) and len(_GENERATED_STAGE_ROUTES.get("castle_focus", [])) > 0,
                "mode": "fixed",
                "route_names": _GENERATED_STAGE_ROUTES.get("castle_focus", [])
            },
            {
                "name": "stage_6_negative_unreachable",
                "enabled": True,
                "mode": "fixed",
                "route_names": [
                    "negative_invalid_high_z",
                    "negative_probable_blocked_tile"
                ]
            }
        ],
        "fixed_routes": _BASELINE_FIXED_ROUTES + _GENERATED_FIXED_ROUTES
    }
}

