# Name: Confictura Gump Rule Router
# Description: Applies configured gump text/button rules and logs unknown gumps for operator triage.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry
from confictura_bot.safe_api import safe_reply_gump
from confictura_bot.gump_ids import KNOWN_GUMP_TYPES
from confictura_bot.gump_ids import gump_hex
from confictura_bot.gump_ids import resolve_gump_id

bind_ca_api(globals())


def _list_or_empty(value):
    if value is None:
        return []
    if isinstance(value, list) or isinstance(value, tuple):
        return list(value)
    return []


def _matches_text(gump_id, text_any, text_all, text_not):
    for phrase in text_not:
        if InGump(gump_id, phrase):
            return False

    if len(text_all) > 0:
        for phrase in text_all:
            if not InGump(gump_id, phrase):
                return False

    if len(text_any) > 0:
        any_hit = False
        for phrase in text_any:
            if InGump(gump_id, phrase):
                any_hit = True
                break
        if not any_hit:
            return False

    return True


def _resolve_candidate_ids(candidate_gump_ids, gump_id_overrides, known_gump_types):
    resolved = []

    for spec in candidate_gump_ids:
        candidate_id = resolve_gump_id(spec, gump_id_overrides, known_gump_types)
        if candidate_id > 0:
            resolved.append(candidate_id)

    return resolved


def _try_add_uint32(target, raw_value):
    try:
        parsed = int(raw_value) & 0xFFFFFFFF
    except Exception:
        return False

    if parsed <= 0:
        return False

    if parsed in target:
        return False

    target.append(parsed)
    return True


def _extract_common_id_fields(value, discovered):
    field_names = ["Key", "ID", "Id", "GumpID", "GumpId", "Serial", "Value"]
    for field_name in field_names:
        try:
            raw_value = getattr(value, field_name)
        except Exception:
            continue

        _try_add_uint32(discovered, raw_value)


def _collect_ids_from_enumerable(value, discovered, depth, max_items):
    if value is None:
        return

    if depth > 2:
        return

    if isinstance(value, str) or isinstance(value, unicode):
        return

    _try_add_uint32(discovered, value)
    _extract_common_id_fields(value, discovered)

    try:
        keys = getattr(value, "Keys")
        seen = 0
        for key in keys:
            _try_add_uint32(discovered, key)
            seen += 1
            if seen >= max_items:
                break
    except Exception:
        pass

    try:
        values = getattr(value, "Values")
        seen = 0
        for entry in values:
            _collect_ids_from_enumerable(entry, discovered, depth + 1, max_items)
            seen += 1
            if seen >= max_items:
                break
    except Exception:
        pass

    try:
        seen = 0
        for entry in value:
            _try_add_uint32(discovered, entry)
            _extract_common_id_fields(entry, discovered)
            if depth < 2:
                _collect_ids_from_enumerable(entry, discovered, depth + 1, max_items)

            seen += 1
            if seen >= max_items:
                break
    except Exception:
        pass


def _discover_open_gump_ids():
    discovered = []

    try:
        from Assistant import Engine
    except Exception:
        return discovered

    try:
        gumps = Engine.Gumps
    except Exception:
        return discovered

    _collect_ids_from_enumerable(gumps, discovered, 0, 64)

    try:
        gumps_type = gumps.GetType()
        properties = gumps_type.GetProperties()

        seen_properties = 0
        for prop in properties:
            seen_properties += 1
            if seen_properties > 40:
                break

            try:
                prop_value = prop.GetValue(gumps, None)
            except Exception:
                continue

            _collect_ids_from_enumerable(prop_value, discovered, 1, 64)
    except Exception:
        pass

    return discovered


def _match_rules_against_open_ids(
    ctx,
    state_name,
    gump_rules,
    open_ids
):
    if len(open_ids) == 0:
        return None

    for rule in gump_rules:
        text_any = _list_or_empty(rule.get("text_any", []))
        text_all = _list_or_empty(rule.get("text_all", []))
        text_not = _list_or_empty(rule.get("text_not", []))

        # Discovery mode is text-anchored to avoid blind replies.
        if len(text_any) == 0 and len(text_all) == 0:
            continue

        button_id = int(rule.get("button_id", 0))
        button_timeout = int(rule.get("wait_timeout_ms", 0))
        switches = _list_or_empty(rule.get("switches", []))
        text_entries = rule.get("text_entries", {})

        for gump_id in open_ids:
            exists = False
            try:
                exists = GumpExists(gump_id)
            except Exception:
                exists = False

            if not exists:
                continue

            if not _matches_text(gump_id, text_any, text_all, text_not):
                continue

            if not safe_reply_gump(
                ctx,
                state_name,
                gump_id,
                button_id,
                button_timeout,
                switches,
                text_entries
            ):
                return {
                    "status": "unknown",
                    "rule_name": rule.get("name", ""),
                    "complete": False,
                    "resolved_gump_id": gump_id,
                    "discovered_ids": open_ids
                }

            rule_name = rule.get("name", "unnamed")
            Telemetry.warn(state_name, "Gump rule matched via discovered open id", {
                "rule": rule_name,
                "gump_id": gump_hex(gump_id),
                "button_id": button_id,
                "marks_complete": rule.get("marks_complete", False)
            })

            return {
                "status": "matched",
                "rule_name": rule_name,
                "complete": rule.get("marks_complete", False),
                "resolved_gump_id": gump_id,
                "discovered_ids": open_ids
            }

    return None



def _matches_text_any_open_gump(text_any, text_all, text_not):
    for phrase in text_not:
        try:
            if InGump(0, phrase):
                return False
        except Exception:
            continue

    if len(text_all) > 0:
        for phrase in text_all:
            matched = False
            try:
                matched = InGump(0, phrase)
            except Exception:
                matched = False
            if not matched:
                return False

    if len(text_any) > 0:
        any_hit = False
        for phrase in text_any:
            matched = False
            try:
                matched = InGump(0, phrase)
            except Exception:
                matched = False
            if matched:
                any_hit = True
                break
        if not any_hit:
            return False

    return True


def _match_rules_any_open_gump(ctx, state_name, gump_rules):
    for rule in gump_rules:
        text_any = _list_or_empty(rule.get("text_any", []))
        text_all = _list_or_empty(rule.get("text_all", []))
        text_not = _list_or_empty(rule.get("text_not", []))

        # Any-gump fallback must be text anchored.
        if len(text_any) == 0 and len(text_all) == 0:
            continue

        if not _matches_text_any_open_gump(text_any, text_all, text_not):
            continue

        button_id = int(rule.get("button_id", 0))
        button_timeout = int(rule.get("wait_timeout_ms", 0))
        switches = _list_or_empty(rule.get("switches", []))
        text_entries = rule.get("text_entries", {})

        if not safe_reply_gump(
            ctx,
            state_name,
            0,
            button_id,
            button_timeout,
            switches,
            text_entries
        ):
            return {
                "status": "unknown",
                "rule_name": rule.get("name", ""),
                "complete": False,
                "resolved_gump_id": 0,
                "discovered_ids": []
            }

        rule_name = rule.get("name", "unnamed")
        Telemetry.warn(state_name, "Gump rule matched via any-open-gump fallback", {
            "rule": rule_name,
            "button_id": button_id,
            "marks_complete": rule.get("marks_complete", False)
        })

        return {
            "status": "matched",
            "rule_name": rule_name,
            "complete": rule.get("marks_complete", False),
            "resolved_gump_id": 0,
            "discovered_ids": []
        }

    return None
def handle_configured_gumps(
    ctx,
    state_name,
    gump_rules,
    candidate_gump_ids,
    gump_id_overrides=None,
    known_gump_types=None
):
    if gump_id_overrides is None:
        gump_id_overrides = {}
    if known_gump_types is None:
        known_gump_types = KNOWN_GUMP_TYPES

    rule_count = len(gump_rules)
    Telemetry.debug(state_name, "Attempting configured gump parse", {
        "rule_count": rule_count,
        "candidate_count": len(candidate_gump_ids)
    })

    for rule in gump_rules:
        gump_id = resolve_gump_id(rule, gump_id_overrides, known_gump_types)
        if gump_id <= 0:
            continue

        if not GumpExists(gump_id):
            continue

        text_any = _list_or_empty(rule.get("text_any", []))
        text_all = _list_or_empty(rule.get("text_all", []))
        text_not = _list_or_empty(rule.get("text_not", []))

        if not _matches_text(gump_id, text_any, text_all, text_not):
            continue

        button_id = int(rule.get("button_id", 0))
        button_timeout = int(rule.get("wait_timeout_ms", 0))
        switches = _list_or_empty(rule.get("switches", []))
        text_entries = rule.get("text_entries", {})

        if not safe_reply_gump(
            ctx,
            state_name,
            gump_id,
            button_id,
            button_timeout,
            switches,
            text_entries
        ):
            return {
                "status": "unknown",
                "rule_name": rule.get("name", ""),
                "complete": False,
                "resolved_gump_id": gump_id,
                "discovered_ids": []
            }

        rule_name = rule.get("name", "unnamed")
        Telemetry.info(state_name, "Gump rule matched", {
            "rule": rule_name,
            "gump_id": gump_hex(gump_id),
            "button_id": button_id,
            "marks_complete": rule.get("marks_complete", False)
        })

        return {
            "status": "matched",
            "rule_name": rule_name,
            "complete": rule.get("marks_complete", False),
            "resolved_gump_id": gump_id,
            "discovered_ids": []
        }

    open_candidate_ids = []
    resolved_candidates = _resolve_candidate_ids(
        candidate_gump_ids,
        gump_id_overrides,
        known_gump_types
    )

    for candidate_id in resolved_candidates:
        if GumpExists(candidate_id):
            open_candidate_ids.append(gump_hex(candidate_id))

    discovered_open_ids = _discover_open_gump_ids()
    if len(discovered_open_ids) > 0:
        Telemetry.debug(state_name, "Discovered open gump ids", {
            "ids": "|".join([gump_hex(x) for x in discovered_open_ids])
        })
    else:
        Telemetry.debug(state_name, "No discovered open gump ids from Engine.Gumps probe")

    discovery_result = _match_rules_against_open_ids(
        ctx,
        state_name,
        gump_rules,
        discovered_open_ids
    )

    if discovery_result is not None:
        return discovery_result

    allow_any_open_fallback = bool(ctx.config.get("onboarding", {}).get("allow_any_open_gump_fallback", False))
    if allow_any_open_fallback:
        any_gump_result = _match_rules_any_open_gump(ctx, state_name, gump_rules)
        if any_gump_result is not None:
            return any_gump_result

    if len(open_candidate_ids) > 0:
        Telemetry.error(state_name, "Unknown gump content for open candidate ids", {
            "candidate_ids": "|".join(open_candidate_ids),
            "discovered_ids": "|".join([gump_hex(x) for x in discovered_open_ids])
        })
    elif len(discovered_open_ids) > 0:
        Telemetry.error(state_name, "Unknown gump encountered from discovered ids", {
            "discovered_ids": "|".join([gump_hex(x) for x in discovered_open_ids])
        })
    else:
        Telemetry.error(state_name, "Unknown gump encountered", {
            "detail": "WaitForGump triggered but no configured rule/candidate matched"
        })

    return {
        "status": "unknown",
        "rule_name": "",
        "complete": False,
        "resolved_gump_id": 0,
        "discovered_ids": discovered_open_ids
    }