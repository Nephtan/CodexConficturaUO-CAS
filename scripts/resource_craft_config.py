# Name: Confictura Resource Craft Config
# Description: Centralized configuration dictionary for the ResourceCraftController FSM.
# Author: ChatGPT Codex
# Shard: Confictura

# Tool IDs from ConficturaRepository docs:
# - Pickaxe base graphic: 0x0E86 (flip 0x0E85)
# - Shovel graphic: 0x0F39
# - Hatchet graphic: 0x0F43
# - Sturdy tool hue variant: 0x0973
BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 250,
        "max_runtime_ticks": 5000,
        "max_retries_per_state": 3,
        "target_timeout_ms": 5000,
        "journal_timeout_ms": 6000,
        "pathfind_settle_ms": 300,
        "action_settle_ms": 250,
        "gump_timeout_ms": 2500
    },
    "safety": {
        "fail_safe_stop": True
    },
    "onboarding": {
        "enabled": True,
        "require_complete": True,
        "unknown_gump_is_fatal": True,
        "max_npc_attempts": 3,
        "npc_search_range": 8,
        "npc_notorieties": ["Innocent", "Ally"],
        "speech_script": [
            "hello",
            "hail",
            "adventure",
            "yes",
            "continue",
            "accept",
            "train"
        ],
        "context_menu_entries": [1, 2, 3],
        "completion_journal_any": [
            "You may now leave",
            "You may now proceed",
            "Good luck"
        ],
        "candidate_gump_ids": [
            0x54F555DF,
            0x554B87F3
        ],
        "gump_rules": [
            {
                "name": "Start Area Continue",
                "gump_id": 0x54F555DF,
                "text_any": ["continue", "next", "proceed"],
                "button_id": 1,
                "wait_timeout_ms": 0,
                "marks_complete": False
            },
            {
                "name": "Start Area Accept",
                "gump_id": 0x554B87F3,
                "text_any": ["accept", "begin", "confirm"],
                "button_id": 1,
                "wait_timeout_ms": 0,
                "marks_complete": True
            }
        ]
    },
    "aliases": {
        "backpack": {
            "value": "backpack",
            "prompt_on_boot": False
        },
        "storage_container": {
            "value": "bank",
            "prompt_on_boot": False
        }
    },
    "waypoints": {
        "resource_node": {
            "mode": "alias",
            "alias": "self"
        },
        "home": {
            "mode": "alias",
            "alias": "self"
        }
    },
    "inventory": {
        "max_weight_ratio": 0.90,
        "tool_graphics": [0x0E86, 0x0E85, 0x0F39, 0x0F43],
        "tool_hue": -1,
        "known_tool_hues": [-1, 0x0973],
        "deposit_enabled": False,
        "resupply_enabled": False,
        "deposit_item_graphics": [0x1BF2],
        "deposit_item_hue": -1,
        "resupply": [
            {
                "graphic": 0x0E86,
                "hue": -1,
                "minimum": 1,
                "restock_to": 2,
                "source_alias": "storage_container"
            }
        ]
    },
    "gather": {
        "mode": "tool_target",
        "tool_graphic": 0x0E86,
        "tool_hue": -1,
        "target_mode": "by_resource",
        "resource_type": "Ore",
        "target_alias": "self",
        "tile_target": {
            "xoffset": 0,
            "yoffset": 0,
            "zoffset": 0,
            "itemid": 0
        },
        "success_journal_any": [
            "You put",
            "You dig",
            "You loosen"
        ],
        "failure_journal_any": [
            "There is no",
            "You cannot mine",
            "That is too far"
        ],
        "attempts_per_cycle": 5
    },
    "craft": {
        "enabled": False,
        "queue": [],
        "success_journal_any": [
            "You create",
            "You put"
        ],
        "failure_journal_any": [
            "You have failed",
            "You lack",
            "You cannot"
        ]
    }
}
