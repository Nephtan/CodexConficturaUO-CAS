# Name: Britain Pathing RnD Config
# Description: Defines staged Britain-only route tests and runtime tuning for standalone pathing validation.
# Author: ChatGPT Codex
# Shard: Confictura

BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 150,
        "max_runtime_ticks": 20000,
        "max_retries_per_state": 0,
        "pause_between_routes_ms": 300
    },
    "pathing_defaults": {
        "within_distance": 2,
        "settle_ms": 350,
        "max_attempts": 120,
        "max_ms": 120000,
        "min_progress": 1,
        "max_hop_distance": 12,
        "min_hop_distance": 2,
        "hop_backoff_step": 2,
        "hop_recover_step": 1,
        "stall_tolerance": 4,
        "stall_pause_ms": 250,
        "lateral_step": 1,
        "short_step_divisor": 2,
        "enforce_same_map": True,
        "max_evidence_attempts": 80
    },
    "test_harness": {
        "success_rate_target_percent": 90,
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
                "name": "stage_2_corridor_chokepoint",
                "enabled": True,
                "mode": "fixed",
                "route_names": [
                    "corridor_public_door_lane",
                    "corridor_market_cross",
                    "corridor_guard_traffic"
                ]
            },
            {
                "name": "stage_3_medium_long_routes",
                "enabled": True,
                "mode": "fixed",
                "route_names": [
                    "medium_town_square",
                    "long_west_gate_approach",
                    "long_east_court_approach"
                ]
            },
            {
                "name": "stage_4_random_batch",
                "enabled": True,
                "mode": "random_batch"
            },
            {
                "name": "stage_5_negative_unreachable",
                "enabled": True,
                "mode": "fixed",
                "route_names": [
                    "negative_invalid_high_z",
                    "negative_probable_blocked_tile"
                ]
            }
        ],
        "fixed_routes": [
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
                "name": "corridor_public_door_lane",
                "destination": (3006, 1108, 0),
                "expected_reachable": True,
                "category": "chokepoint"
            },
            {
                "name": "corridor_market_cross",
                "destination": (3015, 1112, 0),
                "expected_reachable": True,
                "category": "chokepoint"
            },
            {
                "name": "corridor_guard_traffic",
                "destination": (2988, 1110, 0),
                "expected_reachable": True,
                "category": "chokepoint"
            },
            {
                "name": "medium_town_square",
                "destination": (3025, 1140, 0),
                "expected_reachable": True,
                "category": "medium"
            },
            {
                "name": "long_west_gate_approach",
                "destination": (2950, 1080, 0),
                "expected_reachable": True,
                "category": "long"
            },
            {
                "name": "long_east_court_approach",
                "destination": (3120, 1048, 0),
                "expected_reachable": True,
                "category": "long"
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
        ],
        "random_batch": {
            "enabled": True,
            "seed": 1337,
            "sample_count": 8,
            "x_min": 2940,
            "x_max": 3135,
            "y_min": 1000,
            "y_max": 1165,
            "default_z": 0,
            "expected_reachable": True,
            "within_distance": 2,
            "options": {
                "max_attempts": 90,
                "max_ms": 90000
            }
        }
    }
}
