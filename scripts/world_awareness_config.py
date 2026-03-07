# Name: Confictura World Awareness Config
# Description: Centralized configuration for the autonomous world-awareness finite state machine.
# Author: ChatGPT Codex
# Shard: Confictura

BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 200,
        "max_runtime_ticks": 12000,
        "max_retries_per_state": 3,
        "gump_timeout_ms": 1200,
        "pathfind_settle_ms": 300,
        "scan_interval_ms": 800
    },
    "safety": {
        "fail_safe_stop": True
    },
    "awareness": {
        "max_cycles": 200,
        "max_report_entities": 10,
        "region_attributes_probe": [
            "Guarded",
            "NoHousing"
        ],
        "mobile_scan": {
            "enabled": True,
            "range": 12,
            "max_entities": 24,
            "notorieties": [
                "Any"
            ]
        },
        "object_scan": {
            "enabled": True,
            "range": 12,
            "properties_timeout_ms": 250,
            "watch_graphics": [
                {
                    "name": "meeting_spot",
                    "graphic": 25881,
                    "hue": -1,
                    "max_instances": 20,
                    "property_keywords": [
                        "meeting spot"
                    ]
                },
                {
                    "name": "coffer_type_a",
                    "graphic": 7182,
                    "hue": -1,
                    "max_instances": 12,
                    "property_keywords": [
                        "coffer"
                    ]
                },
                {
                    "name": "coffer_type_b",
                    "graphic": 7183,
                    "hue": -1,
                    "max_instances": 12,
                    "property_keywords": [
                        "coffer"
                    ]
                },
                {
                    "name": "teleporter",
                    "graphic": 7107,
                    "hue": -1,
                    "max_instances": 16,
                    "property_keywords": [
                        "teleporter"
                    ]
                }
            ]
        }
    },
    "gumps": {
        "enabled": True,
        "strict_unknown_gump": True,
        "candidate_gump_ids": [
            0x54F555DF,
            0x554B87F3
        ],
        "rules": [
            {
                "name": "Start Continue",
                "gump_id": 0x54F555DF,
                "text_any": [
                    "continue",
                    "next",
                    "proceed"
                ],
                "button_id": 1,
                "wait_timeout_ms": 0,
                "marks_complete": False
            },
            {
                "name": "Start Accept",
                "gump_id": 0x554B87F3,
                "text_any": [
                    "accept",
                    "begin",
                    "confirm"
                ],
                "button_id": 1,
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        ]
    },
    "exploration": {
        "patrol_enabled": False,
        "patrol_waypoints": []
    }
}
