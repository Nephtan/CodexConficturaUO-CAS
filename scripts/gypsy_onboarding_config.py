# Name: Confictura Gypsy Onboarding Config
# Description: Deterministic interaction table for the gypsy tent, race shelf, rename journal, and Thuvia flow.
# Author: ChatGPT Codex
# Shard: Confictura

BOT_CONFIG = {
    "runtime": {
        "tick_pause_ms": 150,
        "max_runtime_ticks": 4000,
        "max_retries_per_state": 1,
        "action_settle_ms": 250,
        "pathfind_settle_ms": 350,
        "object_use_range": 3,
        "gump_timeout_ms": 4500,
        "journal_timeout_ms": 4500,
        "context_timeout_ms": 3000,
        "post_context_gump_timeout_ms": 4500,
        "allow_context_success_without_packet": True,
        "rename_apply_pause_ms": 500
    },
    "safety": {
        "fail_safe_stop": True
    },
    "onboarding": {
        "unknown_gump_is_fatal": True,
        "allow_any_open_gump_fallback": False,
        "enable_race_shelf": True,
        "race_category_button_id": 123456789,
        "race_button_id": 1000,
        "enable_rename": True,
        "rename_allow_skip": True,
        "rename_desired_names": [
            "Wayfarer",
            "Ashwander",
            "Sablethorn"
        ],
        "thuvia_mode": "NEUTRAL",
        "tarot_card_button_id": 101,
        "completion_journal_any": [
            "The card vanishes from your hand as you magically appear elsewhere.",
            "You have entered the City of Britain."
        ],
        # Optional manual overrides if runtime gump ids differ on your server build.
        # Keys can be gump_key values (example: "GYPSY_TAROT") or full type names.
        "gump_id_overrides": {
            "GYPSY_TAROT": 0x758C021A,
            "RACE_POTIONS": 0x54C2BB00,
            "PKNONPK": 0x9DD37300
        }
    },
    "world_refs": {
        "gypsy_seat": (3567, 3404, 0),
        "thuvia_spot": (3563, 3413, 0),
        "gypsy_name_any": ["gypsy", "arabelle"],
        "thuvia_name_any": ["thuvia"],
        "mobile_search_range": 14,
        "mobile_search_order": "Next",
        "mobile_search_max_scan": 40,
        "object_search_max_scan": 40,
        "race_shelf_graphic": 0x506C,
        "race_shelf_hue": 0x0ABE,
        "race_shelf_range": 8,
        "rename_journal_graphic": 0x14EF,
        "rename_journal_hue": -1,
        "rename_journal_range": 8
    },
    "steps": [
        {
            "name": "MOVE_TO_GYPSY_SEAT",
            "action": "move_to_ref",
            "ref": "gypsy_seat"
        },
        {
            "name": "OPEN_GYPSY_CONTEXT",
            "action": "mobile_context",
            "name_any_ref": "gypsy_name_any",
            "entry_name": "Talk",
            "entry_index": 1,
            "context_entries": [1],
            "require_ref": "gypsy_seat",
            "expect_gump_after_context": True, "expect_gump_keys": ["GYPSY_TAROT"], "post_context_gump_timeout_ms": 4500
        },
        {
            "name": "GYPSY_OPEN_DECK",
            "action": "gump_rule",
            "rule": {
                "name": "Gypsy Start Tarot",
                "gump_key": "GYPSY_TAROT",
                "text_any": ["Greetings", "tarot"],
                "button_id": 99,
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "RACE_SHELF_OPEN",
            "enabled_flag": "enable_race_shelf",
            "action": "use_object_ref",
            "graphic_ref": "race_shelf_graphic",
            "hue_ref": "race_shelf_hue",
            "range_ref": "race_shelf_range"
        },
        {
            "name": "RACE_SHELF_SELECT_CATEGORY",
            "enabled_flag": "enable_race_shelf",
            "action": "gump_rule",
            "rule": {
                "name": "Race Shelf Category Selection",
                "gump_key": "RACE_POTIONS",
                "text_any": ["GYPSY POTION SHELF", "CATEGORIES"],
                "button_from_config": "race_category_button_id",
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "RACE_SHELF_SELECT",
            "enabled_flag": "enable_race_shelf",
            "action": "gump_rule",
            "rule": {
                "name": "Race Shelf Selection",
                "gump_key": "RACE_POTIONS",
                "text_any": ["GYPSY POTION SHELF", "CATEGORIES"],
                "button_from_config": "race_button_id",
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "RENAME_CHARACTER",
            "enabled_flag": "enable_rename",
            "action": "rename_via_journal"
        },
        {
            "name": "MOVE_TO_THUVIA",
            "action": "move_to_ref",
            "ref": "thuvia_spot",
            "within_distance": 1,
            "avoid_exact_tile": True
        },
        {
            "name": "SPEAK_THUVIA_CHOOSE",
            "action": "speak",
            "text": "choose"
        },
        {
            "name": "THUVIA_SELECT_MODE",
            "action": "gump_rule",
            "rule": {
                "name": "Thuvia PvP Mode",
                "gump_key": "PKNONPK",
                "text_any": [],
                "button_from_mode": True,
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "RETURN_TO_GYPSY_SEAT",
            "action": "move_to_ref",
            "ref": "gypsy_seat"
        },
        {
            "name": "OPEN_GYPSY_CONTEXT_FINAL",
            "action": "mobile_context",
            "name_any_ref": "gypsy_name_any",
            "entry_name": "Talk",
            "entry_index": 1,
            "context_entries": [1],
            "require_ref": "gypsy_seat",
            "expect_gump_after_context": True, "expect_gump_keys": ["GYPSY_TAROT"], "post_context_gump_timeout_ms": 4500
        },
        {
            "name": "GYPSY_OPEN_DECK_FINAL",
            "action": "gump_rule",
            "rule": {
                "name": "Gypsy Start Tarot Final",
                "gump_key": "GYPSY_TAROT",
                "text_any": ["Greetings", "tarot"],
                "button_id": 99,
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "GYPSY_DRAW_CARD",
            "action": "gump_rule",
            "rule": {
                "name": "Gypsy Draw Tarot Card",
                "gump_key": "GYPSY_TAROT",
                "text_any": [
                    "If you choose this fate",
                    "If you choose this card",
                    "If you take this card",
                    "If this is the card you want",
                    "If this card is yours",
                    "If this fate is meant for you",
                    "If you draw this card",
                    "If you choose this path",
                    "If you take this road"
                ],
                "button_from_config": "tarot_card_button_id",
                "wait_timeout_ms": 0,
                "marks_complete": False
            }
        },
        {
            "name": "VERIFY_TELEPORT_MESSAGE",
            "action": "wait_journal_any",
            "entries_from_config": "completion_journal_any",
            "success_if_far_from_ref": "gypsy_seat",
            "success_min_distance": 20
        }
    ]
}






