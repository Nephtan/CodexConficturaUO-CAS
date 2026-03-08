# Name: Britain Thief Recon Config
# Description: Centralized configuration dictionary for spawn-to-thief reconnaissance without criminal actions.
# Author: ChatGPT Codex
# Shard: Confictura

BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 200,
        "max_runtime_ticks": 6000,
        "max_retries_per_state": 1,
        "pathfind_settle_ms": 350,
        "pathfind_max_hop_distance": 12,
        "pathfind_min_progress": 1,
        "scan_pause_ms": 120,
        "properties_timeout_ms": 250
    },
    "safety": {
        "fail_safe_stop": True
    },
    "route": {
        "spawn_capture_enabled": True,
        "corridor_waypoints": [
            {
                "name": "britain_public_door_to_thieves",
                "x": 3006,
                "y": 1108,
                "z": 0,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": False,
                "interaction": {
                    "type": "public_door",
                    "graphic": 2718,
                    "hue": 1190,
                    "name_tokens": ["oak shelf", "trapdoor"],
                    "search_range": 8,
                    "max_scans": 12,
                    "source_max_distance": 4,
                    "post_use_pause_ms": 700,
                    "verify_attempts": 10,
                    "verify_pause_ms": 300,
                    "expected_region": "the Thieves Guild",
                    "expected_destination": (3425, 3187, 17),
                    "expected_distance": 8
                }
            },
            {
                "name": "thief_hub_entry_platform",
                "x": 3425,
                "y": 3187,
                "z": 17,
                "within_distance": 3,
                "avoid_exact_tile": False,
                "scan_enabled": False
            },
            {
                "name": "thief_hub_outer_door",
                "x": 3409,
                "y": 3198,
                "z": 0,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": True
            },
            {
                "name": "thief_hub_stealing_board",
                "x": 3415,
                "y": 3203,
                "z": 7,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": True
            },
            {
                "name": "thief_hub_guildmaster_lane",
                "x": 3418,
                "y": 3189,
                "z": 0,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": True
            },
            {
                "name": "thief_hub_practice_lockboxes",
                "x": 3417,
                "y": 3187,
                "z": 8,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": True
            },
            {
                "name": "thief_hub_training_dummy",
                "x": 3421,
                "y": 3190,
                "z": 0,
                "within_distance": 2,
                "avoid_exact_tile": False,
                "scan_enabled": True
            }
        ]
    },
    "recon": {
        "mobile_scan_passes": [
            {
                "name": "enemy_next_any",
                "source": "enemy",
                "notorieties": ["Any"],
                "selection": "Any",
                "search_mode": "Next",
                "body_filter": "Any",
                "search_range": 16,
                "max_scans": 30
            },
            {
                "name": "friend_next_any",
                "source": "friend",
                "notorieties": ["Any"],
                "selection": "Any",
                "search_mode": "Next",
                "body_filter": "Any",
                "search_range": 16,
                "max_scans": 30
            }
        ],
        "mobile_watch": [
            {
                "name": "thief_guildmaster",
                "name_tokens": ["guildmaster", "thief"],
                "expected_near": (3418, 3189, 0),
                "max_distance": 8
            },
            {
                "name": "thief_vendor",
                "name_tokens": ["thief"],
                "expected_near": (3428, 3189, 0),
                "max_distance": 10
            },
            {
                "name": "assassin_guildmaster",
                "name_tokens": ["assassin", "guildmaster"],
                "expected_near": (3420, 3215, 0),
                "max_distance": 12
            },
            {
                "name": "jester_guildmaster",
                "name_tokens": ["jester", "guildmaster"],
                "expected_near": (3430, 3209, 0),
                "max_distance": 12
            }
        ],
        "object_watch": [
            {
                "name": "stealing_board",
                "graphic": 22396,
                "hue": 2794,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": ["stealing the past"],
                "property_keywords": ["stealing the past"],
                "expected_near": (3415, 3203, 7),
                "max_distance": 5
            },
            {
                "name": "pickpocket_dip",
                "graphic": 7875,
                "hue": -1,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": [],
                "property_keywords": ["pickpocket"],
                "expected_near": (3416, 3190, 0),
                "max_distance": 6
            },
            {
                "name": "training_dummy",
                "graphic": 4212,
                "hue": -1,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": [],
                "property_keywords": ["training dummy"],
                "expected_near": (3421, 3190, 0),
                "max_distance": 6
            },
            {
                "name": "practice_lockbox_cluster",
                "graphic": 7182,
                "hue": 2913,
                "scan_range": 16,
                "max_instances": 8,
                "name_tokens": ["practice lockbox"],
                "property_keywords": ["practice lockbox"],
                "expected_near": (3418, 3187, 8),
                "max_distance": 8
            },
            {
                "name": "guild_bank_vault",
                "graphic": 1079,
                "hue": -1,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": ["bank vault"],
                "property_keywords": ["bank vault"],
                "expected_near": (3425, 3188, 3),
                "max_distance": 8
            },
            {
                "name": "secret_dungeon_door_west",
                "graphic": 788,
                "hue": 2874,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": [],
                "property_keywords": [],
                "expected_near": (3412, 3199, 0),
                "max_distance": 8
            },
            {
                "name": "secret_dungeon_door_south",
                "graphic": 796,
                "hue": 2874,
                "scan_range": 16,
                "max_instances": 2,
                "name_tokens": [],
                "property_keywords": [],
                "expected_near": (3414, 3213, 0),
                "max_distance": 10
            }
        ],
        "final_summary_limit_per_target": 4,
        "fail_if_unresolved": False
    },
    "risk": {
        "fail_fast_on_guard_or_criminal": True,
        "guard_name_tokens": ["guard", "town guard"],
        "stop_on_criminal_state": True,
        "stop_on_murderer_state": True
    }
}


