# Task Summary
Delivered a new autonomous onboarding vertical for the Confictura start area, driven by a deterministic interaction table and integrated with the existing Python 2.7 FSM runtime.

New/updated files:
- `scripts/gypsy_onboarding_controller.py`
- `scripts/gypsy_onboarding_config.py`
- `scripts/confictura_bot/gump_ids.py`
- `scripts/confictura_bot/gump_router.py`
- `scripts/confictura_bot/safe_api.py`

What was implemented:
- **Step-table onboarding controller** for the exact gypsy-tent sequence:
  - Move to gypsy seat.
  - Open gypsy context menu.
  - Advance gypsy tarot gump.
  - Open race potion shelf and apply configured race selection button.
  - Open visitor journal and submit configured rename candidates.
  - Move to Thuvia, speak `choose`, and reply PvP/PvE/Neutral gump.
  - Return to gypsy, reopen tarot, draw configured card button.
  - Verify teleport completion via journal text.
- **Gump type -> id resolver** using legacy .NET string hash behavior (for ServUO/RunUO-style `GetType().FullName.GetHashCode()` gump IDs).
- **Router upgrades**:
  - Rules now support `gump_key` / `gump_type` and optional id overrides.
  - Added `text_all` and `text_not` matching support.
  - Improved unknown-gump diagnostics with resolved candidate IDs.
- **Safe wrapper upgrades**:
  - Added `safe_wait_for_context`.
  - Hardened `safe_reply_gump` with gump-open checks and text-entry normalization.
- **Rename no-op handling**:
  - Detects when `NameAlterGump` submission returns no name change.
  - Logs explicit no-op diagnostics (likely dupe-check/no-op path).
  - Retries through `rename_desired_names` candidates.
  - Enforces fail-safe stop or optional skip (`rename_allow_skip`).

# Testing Instructions
1. Keep folder structure intact and load scripts into ClassicAssist.
2. Open `scripts/gypsy_onboarding_config.py` and set:
   - `onboarding.rename_desired_names` to names you want tested.
   - `onboarding.thuvia_mode` to `PVE`, `PVP`, or `NEUTRAL`.
   - `onboarding.race_button_id` (default `1000` for human reset).
3. Run `gypsy_onboarding_controller.py` immediately after entering the start area.
4. Observe full step execution in order:
   - `MOVE_TO_GYPSY_SEAT` -> `OPEN_GYPSY_CONTEXT` -> `GYPSY_OPEN_DECK`
   - `RACE_SHELF_OPEN` -> `RACE_SHELF_SELECT`
   - `RENAME_CHARACTER`
   - `MOVE_TO_THUVIA` -> `SPEAK_THUVIA_CHOOSE` -> `THUVIA_SELECT_MODE`
   - `RETURN_TO_GYPSY_SEAT` -> `OPEN_GYPSY_CONTEXT_FINAL` -> `GYPSY_OPEN_DECK_FINAL` -> `GYPSY_DRAW_CARD`
   - `VERIFY_TELEPORT_MESSAGE`
5. Validate successful stop in `COMPLETE_STOP` and no unhandled gump errors.
6. **Rename no-op validation** (Testing Instruction 2 focus):
   - Set `rename_desired_names` to known-invalid or duplicate names.
   - Re-run and confirm telemetry reports `Rename no-op detected after gump submit` and retries next candidate.
   - If all candidates fail and `rename_allow_skip=False`, confirm fail-safe stop (`FATAL_STOP`) with explicit reason.
7. If a gump fails to match due shard/runtime id differences, add override(s) under `onboarding.gump_id_overrides` and re-run.

# Expected Telemetry
Healthy progression examples:
- `[FSM][MOVE_TO_GYPSY_SEAT][INFO] Pathfinding to reference | ...`
- `[FSM][OPEN_GYPSY_CONTEXT][INFO] Matched mobile | name=..., serial=...`
- `[FSM][GYPSY_OPEN_DECK][INFO] Gump rule matched | rule=Gypsy Start Tarot, button_id=99, ...`
- `[FSM][THUVIA_SELECT_MODE][INFO] Gump rule matched | rule=Thuvia PvP Mode, button_id=2, ...`
- `[FSM][VERIFY_TELEPORT_MESSAGE][INFO] Journal completion matched | text=The card vanishes...`
- `[FSM][COMPLETE_STOP][INFO] Gypsy onboarding complete | completed_steps=..., current_name=...`

Rename no-op diagnostics:
- `[FSM][RENAME_CHARACTER][ERROR] Rename no-op detected after gump submit | candidate=..., hint=NameAlterGump dupe-check/no-op path likely triggered`

Unknown gump path:
- `[FSM][...][ERROR] Unknown gump content for open candidate ids | candidate_ids=...`
- `[FSM][FATAL_STOP][FATAL] Entering FATAL_STOP | last_error=Unknown gump during onboarding, ...`

# Known Fragilities
- Gump IDs may vary by server runtime/string-hash behavior; `gump_id_overrides` is provided for deterministic correction without code edits.
- Gypsy interaction depends on being at the required seat tile before context-menu action.
- Mobile/name matching uses nearby mobile text matching (`gypsy`, `thuvia`); unusual naming/localization can require config token updates.
- Race shelf and journal lookup depend on expected graphics (`0x506C`, `0x14EF`) being present and reachable.
- Strict unknown-gump policy is intentionally fail-fast to force explicit rule updates rather than silent misclick behavior.

---

# Iteration Update (2026-03-06): ClassicAssist API Scope Binding Fix

## Task Summary
Fixed startup crashes caused by ClassicAssist macro commands (`Name`, `WarMode`, `Pause`, etc.) not being visible inside imported modules.

Implemented:
- Added reusable API scope shim: `scripts/confictura_bot/ca_shim.py`.
- Added package-level bootstrap in `scripts/confictura_bot/__init__.py` to bind macro commands into `__builtin__`.
- Added explicit `bind_ca_api(globals())` in all active runtime/controller modules that call ClassicAssist APIs:
  - `scripts/gypsy_onboarding_controller.py`
  - `scripts/world_awareness_controller.py`
  - `scripts/resource_craft_controller.py`
  - `scripts/confictura_bot/context.py`
  - `scripts/confictura_bot/fsm.py`
  - `scripts/confictura_bot/guards.py`
  - `scripts/confictura_bot/safe_api.py`
  - `scripts/confictura_bot/gump_router.py`
  - `scripts/confictura_bot/perception.py`

## Testing Instructions
1. In ClassicAssist, create a new macro named `run_gypsy_onboarding`.
2. Paste this loader code in the macro editor:
   ```python
   # Name: Confictura Gypsy Onboarding Loader
   # Description: Loads and executes gypsy_onboarding_controller from repo path.
   # Author: ChatGPT Codex
   # Shard: Confictura

   import sys

   SCRIPT_ROOT = r"D:\CodexConficturaUO-CAS\CodexConficturaUO-CAS\scripts"
   SCRIPT_FILE = r"D:\CodexConficturaUO-CAS\CodexConficturaUO-CAS\scripts\gypsy_onboarding_controller.py"

   if SCRIPT_ROOT not in sys.path:
       sys.path.append(SCRIPT_ROOT)

   execfile(SCRIPT_FILE)
   ```
3. Assign a hotkey and run in the start area.
4. Confirm BOOTSTRAP no longer throws `global name 'Name' is not defined`.
5. If failure is forced, confirm `FATAL_STOP` no longer throws `global name 'WarMode' is not defined`.

## Expected Telemetry
- `[FSM][MAIN][INFO] Starting GypsyOnboardingController`
- `[FSM][BOOTSTRAP][INFO] Entering BOOTSTRAP`
- `[FSM][BOOTSTRAP][INFO] Bootstrap ready | initial_name=..., step_count=...`
- On forced failure path, clean fatal stop without macro-level NameError:
  - `[FSM][FATAL_STOP][FATAL] Entering FATAL_STOP | ...`
  - `[FSM][FATAL_STOP][FATAL] Bot stopping | reason=Fail-safe stop policy triggered`

## Known Fragilities
- If ClassicAssist host changes where macro commands are exposed (neither `__main__` nor `__builtin__`), bindings can still fail; telemetry will show immediate unresolved command exceptions.
- Loader macro path must match local repo location exactly.
- If scripts are copy/pasted directly into macro editor instead of loaded from file, ensure package imports still resolve via `sys.path`.

---

# Iteration Update (2026-03-06): Pause Binding Repair

## Task Summary
Resolved the follow-up failure:
- `global name 'Pause' is not defined` from `scripts/confictura_bot/fsm.py`.

Changes made:
- Updated `scripts/confictura_bot/ca_shim.py` binding behavior:
  - Removed strict `callable()` filter.
  - Now binds PascalCase symbols from `__main__`/`__builtin__` (covers ClassicAssist macro commands even when IronPython reports non-standard callability).
- Hardened `scripts/confictura_bot/fsm.py`:
  - Added `_pause_or_fail(...)` wrapper.
  - If `Pause` resolution fails, emits explicit telemetry and cleanly stops FSM instead of hard macro crash.

## Testing Instructions
1. Re-run the same ClassicAssist loader macro (no loader changes needed).
2. Confirm script proceeds beyond BOOTSTRAP and STEP_EXECUTOR entry without `Pause` NameError.
3. If Pause still cannot resolve, expect explicit telemetry line:
   - `[FSM][...][ERROR] Pause command unavailable | ...`
   and deterministic stop instead of raw macro exception.

## Expected Telemetry
- `[FSM][MAIN][INFO] Starting GypsyOnboardingController`
- `[FSM][BOOTSTRAP][INFO] Bootstrap ready | ...`
- `[FSM][STEP_EXECUTOR][INFO] Entering STEP_EXECUTOR`
- Next onboarding step logs (e.g., `MOVE_TO_GYPSY_SEAT`) without immediate macro-level NameError.

## Known Fragilities
- If the ClassicAssist host surface changes macro command exposure semantics again, binding may still need host-specific adaptation.

---

# Iteration Update (2026-03-06): Import Cache Purge For Hotkey Re-Runs

## Task Summary
Observed telemetry still referenced old `fsm.py` line layout after file edits, indicating ClassicAssist retained cached Python modules across hotkey invocations.

Implemented cache-purge bootstrap at top of controller scripts:
- `scripts/gypsy_onboarding_controller.py`
- `scripts/world_awareness_controller.py`
- `scripts/resource_craft_controller.py`

Behavior:
- On each script start, purge `confictura_bot*` plus the controller-specific config module from `sys.modules`.
- Then re-import framework/config modules, ensuring latest on-disk code is used every run.

## Testing Instructions
1. Re-run the same loader macro without restarting ClassicAssist.
2. Confirm runtime now executes latest framework code (no stale line references).
3. Validate no immediate `Pause` NameError after entering `STEP_EXECUTOR`.

## Expected Telemetry
- Normal BOOTSTRAP and STEP_EXECUTOR logs.
- If a pause issue remains, telemetry should now come from `_pause_or_fail` path (explicit `[ERROR] Pause command unavailable`) instead of raw macro NameError.

## Known Fragilities
- Aggressive module purging is intended for rapid iteration and can reset in-memory module state between runs.

---

# Iteration Update (2026-03-06): Explicit ClassicAssist API Publication

## Task Summary
Addressed persistent `Pause` resolution failure in imported modules by publishing known ClassicAssist commands into `__builtin__` from controller runtime scope before FSM execution.

Changes made:
- `scripts/confictura_bot/ca_shim.py`
  - Added `_KNOWN_CA_COMMANDS` catalog.
  - Added `publish_known_ca_api(namespace)`.
  - `bind_ca_api(namespace)` now invokes `publish_known_ca_api(namespace)` first.
- Controllers now publish at runtime entry before FSM starts:
  - `scripts/gypsy_onboarding_controller.py`
  - `scripts/world_awareness_controller.py`
  - `scripts/resource_craft_controller.py`
  - Added startup telemetry: `Published ClassicAssist API symbols | count=...`

## Testing Instructions
1. Run the same loader macro again.
2. Validate the new startup debug line appears before `Starting ...Controller`:
   - `[FSM][MAIN][DEBUG] Published ClassicAssist API symbols | count=...`
3. Confirm script proceeds past first loop delay without `Pause command unavailable`.

## Expected Telemetry
- `[FSM][MAIN][DEBUG] Published ClassicAssist API symbols | count=...`
- `[FSM][MAIN][INFO] Starting GypsyOnboardingController`
- `[FSM][STEP_EXECUTOR][INFO] Entering STEP_EXECUTOR`
- Next step execution logs (`MOVE_TO_GYPSY_SEAT` etc.) instead of immediate stop.

## Known Fragilities
- If `count=0`, ClassicAssist is exposing command symbols via a non-standard scope resolver not reachable through dictionary/eval lookup; in that case we need an engine-specific fallback strategy.

---

# Iteration Update (2026-03-06): Gypsy Mobile Acquisition Fix

## Task Summary
Resolved onboarding stall at `OPEN_GYPSY_CONTEXT` where gypsy could not be found even while nearby.

Changes made:
- Reworked mobile lookup in `scripts/gypsy_onboarding_controller.py`:
  - Replaced single `GetFriend(..., "Closest", ...)` loop with dual-selector scan:
    1. `GetEnemy(["Any"], "Any", <order>, "Any", range)`
    2. `GetFriend(["Any"], "Any", <order>, "Any", range)`
  - Default scan order now `Next` (iterates candidates instead of hammering same closest target).
  - Added per-pass telemetry: `Scanning mobiles` with selector/order/range.
  - Added failure diagnostics: `observed_names` list in error payload.
- Updated defaults in `scripts/gypsy_onboarding_config.py`:
  - `gypsy_name_any`: `['gypsy', 'arabelle']`
  - `mobile_search_order`: `"Next"`
  - `mobile_search_max_scan`: `40`

## Testing Instructions
1. Re-run `run_gypsy_onboarding` from the same start area position.
2. Confirm `OPEN_GYPSY_CONTEXT` logs either:
   - `Matched mobile | name=Arabelle the gypsy ...` then continues, or
   - `Unable to locate required mobile ... observed_names=...`.
3. If it still fails, send the full `OPEN_GYPSY_CONTEXT` block including `observed_names`.

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Scanning mobiles | selector=enemy_any, scan_order=Next, ...`
- `[FSM][OPEN_GYPSY_CONTEXT][INFO] Matched mobile | name=Arabelle the gypsy, ...`
- Transition to `GYPSY_OPEN_DECK` if context succeeds.

## Known Fragilities
- If the gypsy name is localized or customized, `gypsy_name_any` may need additional tokens.
- If context menu entry index differs, `entry_index` in step config may require adjustment.

---

# Iteration Update (2026-03-06): Gypsy Seat/Context Gate Fix

## Task Summary
Used `ConficturaRepositoryDocs` shard code to correct onboarding behavior for gypsy interaction.

Validated shard logic:
- `ShardGreeterEntry.OnClick()` only opens `GypsyTarotGump` when player is on seat tile `(3567,3404)` (or `RaceID > 0`).
- Gypsy context entry is the `Talk` context action.

Implemented fixes:
- `scripts/gypsy_onboarding_controller.py`
  - Added `_ensure_on_ref_tile(...)` to repeatedly path and verify exact tile reach before continuing.
  - `MOVE_TO_GYPSY_SEAT` now requires actual tile arrival, not a single path request.
  - `OPEN_GYPSY_CONTEXT` no longer pathfinds away to the NPC alias (this previously broke seat requirement).
  - `OPEN_GYPSY_CONTEXT` now tries context by entry name (`"Talk"`) first, then falls back to index.
- `scripts/confictura_bot/safe_api.py`
  - `safe_wait_for_context(..., fail_on_timeout=True)` now supports non-fatal probe mode for entry-name fallback.
- `scripts/gypsy_onboarding_config.py`
  - Added step fields on both gypsy context steps:
    - `entry_name: "Talk"`
    - `require_ref: "gypsy_seat"`

## Testing Instructions
1. Run `run_gypsy_onboarding` again from the same loader macro.
2. Confirm logs show repeated tile enforcement for gypsy seat when needed.
3. In `OPEN_GYPSY_CONTEXT`, verify context is attempted with `entry_name=Talk` and no immediate move away from seat.
4. Confirm `GYPSY_OPEN_DECK` receives `GypsyTarotGump` and applies button `99`.

## Expected Telemetry
- `[FSM][MOVE_TO_GYPSY_SEAT][DEBUG] Pathing attempt to tile | ref=gypsy_seat, ...`
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Waiting for context action | entry=Talk, ...`
- `[FSM][GYPSY_OPEN_DECK][INFO] Incoming gump packet detected`
- `[FSM][GYPSY_OPEN_DECK][INFO] Gump rule matched | rule=Gypsy Start Tarot, button_id=99, ...`

## Known Fragilities
- If context entry label differs by localization/client build, fallback index may still be required.
- If pathing cannot land exactly on `(3567,3404)`, gypsy gump will not open by shard design.

---

# Iteration Update (2026-03-06): Context->Gump Coupling And Retry Fix

## Task Summary
Addressed failure pattern where `OPEN_GYPSY_CONTEXT` reported success but `GYPSY_OPEN_DECK` timed out repeatedly without reissuing context interaction.

Implemented:
- `scripts/gypsy_onboarding_controller.py`
  - Reworked `mobile_context` execution to support multiple context candidates (`context_entries`) in one attempt.
  - Added per-candidate fallback loop (example: `"Talk"`, `1`, `0`, `2`).
  - Added optional `expect_gump_after_context` check so context step only succeeds if a gump packet actually arrives.
  - Added explicit failure diagnostics:
    - `Context candidate did not produce gump`
    - `No gump arrived after context attempts`
- `scripts/gypsy_onboarding_config.py`
  - Clean rewrite to valid Python structure.
  - Increased `runtime.gump_timeout_ms` to `4500`.
  - Added `runtime.post_context_gump_timeout_ms`.
  - Updated both gypsy context steps with:
    - `context_entries: ["Talk", 1, 0, 2]`
    - `expect_gump_after_context: True`
    - `post_context_gump_timeout_ms: 4500`

## Testing Instructions
1. Run `run_gypsy_onboarding` again.
2. Watch `OPEN_GYPSY_CONTEXT` telemetry:
   - It should try context candidates and immediately wait for gump after each candidate.
3. If all candidates fail, it should fail in `OPEN_GYPSY_CONTEXT` (not loop only in `GYPSY_OPEN_DECK`).
4. Send the full `OPEN_GYPSY_CONTEXT` block if it still fails.

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Waiting for context action | entry=Talk ...`
- If candidate fails to open gump:
  - `[FSM][OPEN_GYPSY_CONTEXT][WARN] Context candidate did not produce gump | candidate=...`
- If success:
  - `[FSM][OPEN_GYPSY_CONTEXT][INFO] Incoming gump packet detected`
  - then normal `GYPSY_OPEN_DECK` parse/reply logs.

## Known Fragilities
- If shard/client localizes context label, `"Talk"` match may fail and rely on index fallback.
- If gump id hashing differs from expected runtime, additional gump-id override tuning may still be required.

---

# Iteration Update (2026-03-06): Open-Gump Loop Guard For Gypsy Context

## Task Summary
Addressed the loop where `OPEN_GYPSY_CONTEXT` repeatedly retried even though the gypsy gump was already visible.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - Reworked `STEP_EXECUTOR._execute_mobile_context(...)` to reduce false negatives from packet-only gump waits.
  - Added pre-check for already-open expected gumps before trying context entries.
  - Added policy fallback: if context attempts succeed but no new gump packet is observed, optionally advance to the next gump-rule step instead of re-looping context forever.
  - Added richer telemetry payloads in this path (`expected_ids`, policy marker, tried entries).
- `scripts/gypsy_onboarding_config.py`
  - Added runtime policy default:
    - `allow_context_success_without_packet: True`

Why this fix:
- `WaitForGump(...)` listens for incoming packets, not "already open" gumps.
- In live runs, gypsy gumps can be open/visible without a fresh packet being caught during the context wait window.

## Testing Instructions
1. Re-run the same macro loader and execute `gypsy_onboarding_controller.py` in the start area.
2. Watch `OPEN_GYPSY_CONTEXT` behavior specifically:
   - If gump is already open, expect immediate pass with telemetry:
     - `Expected gump already open before context action`
   - If no packet is seen after context attempts, expect policy fallback telemetry:
     - `No gump packet observed after context attempts; advancing by policy`
3. Confirm the script advances into `GYPSY_OPEN_DECK` rather than looping `OPEN_GYPSY_CONTEXT`.
4. Send the full telemetry block from:
   - `OPEN_GYPSY_CONTEXT`
   - `GYPSY_OPEN_DECK`
   - first `RECOVER`/`FATAL_STOP` (if any)

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][INFO] Expected gump already open before context action | open_expected_ids=...`
- or
- `[FSM][OPEN_GYPSY_CONTEXT][WARN] No gump packet observed after context attempts; advancing by policy | tried=..., expected_ids=..., policy=allow_context_success_without_packet`
- followed by:
  - `[FSM][GYPSY_OPEN_DECK][INFO] ...` rule parsing path (or a precise failure reason if gump id/content mismatches).

## Known Fragilities
- If Confictura runtime gump id hashing differs from expected values and the open gump cannot be resolved by configured ids, `GYPSY_OPEN_DECK` may still fail; in that case capture the new telemetry and we will add a runtime gump-id discovery path/override.

---

# Iteration Update (2026-03-07): Runtime Gump-ID Discovery Fallback

## Task Summary
Addressed the new blocker where `OPEN_GYPSY_CONTEXT` advances but `GYPSY_OPEN_DECK` still times out on expected id `0x3536596C`.

Implemented runtime discovery so rules can bind to the actual open gump id even when configured hash ids do not match.

Changes made:
- `scripts/confictura_bot/gump_router.py`
  - Added open-gump id discovery pipeline (`_discover_open_gump_ids`) using live `Assistant.Engine.Gumps` object introspection/enumeration.
  - Added text-anchored fallback matcher (`_match_rules_against_open_ids`) that attempts configured rule matching/reply against discovered live ids.
  - Added telemetry:
    - `Discovered open gump ids`
    - `Gump rule matched via discovered open id`
- `scripts/gypsy_onboarding_controller.py`
  - Updated `_wait_and_apply_rule(...)` to attempt router parsing even when no fresh gump packet is seen.
  - Added telemetry warning when packet wait misses:
    - `No incoming gump packet during wait window`
  - Failure payload now includes discovered ids when available.

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` from the same loader macro.
2. Focus on `GYPSY_OPEN_DECK` telemetry:
   - If discovery works, expect:
     - `Discovered open gump ids | ids=...`
     - `Gump rule matched via discovered open id | gump_id=...`
3. If it still fails, send the full block for:
   - `GYPSY_OPEN_DECK`
   - the immediately following `RECOVER` entry

## Expected Telemetry
- `[FSM][GYPSY_OPEN_DECK][WARN] No incoming gump packet during wait window | expected_gump_id=...`
- `[FSM][GYPSY_OPEN_DECK][DEBUG] Discovered open gump ids | ids=...`
- `[FSM][GYPSY_OPEN_DECK][WARN] Gump rule matched via discovered open id | gump_id=..., rule=Gypsy Start Tarot, ...`

## Known Fragilities
- Discovery relies on `Assistant.Engine.Gumps` runtime surface; if client build hides active gump state behind non-enumerable internals, fallback may still need one more engine-specific probe path.

---

# Iteration Update (2026-03-07): Direct ContextMenu Fallback + Wider Talk Index Sweep

## Task Summary
Recent telemetry showed `WaitForContext` probes returning without producing a gypsy gump packet. Added a second interaction path that directly calls `ContextMenu(obj, index)` and expanded index coverage.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - `OPEN_GYPSY_CONTEXT` now resolves mobile alias to serial and uses serial target for context calls.
  - After each `WaitForContext(...)` candidate, it now attempts direct `ContextMenu(...)` for numeric candidates.
  - Added telemetry marker for direct path:
    - `Direct ContextMenu attempt`
    - packet/open-gump warnings include `source=ContextMenu` vs `source=WaitForContext`.
- `scripts/gypsy_onboarding_config.py`
  - Expanded gypsy context candidate list on both context steps:
    - `context_entries: ["Talk", 1, 0, 2, 3, 4, 5, 6, 7, 8]`

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py`.
2. Watch `OPEN_GYPSY_CONTEXT` for direct-attempt telemetry.
3. If gypsy gump opens, `OPEN_GYPSY_CONTEXT` should pass and `GYPSY_OPEN_DECK` should continue immediately.
4. If it still fails, send full logs for:
   - `OPEN_GYPSY_CONTEXT`
   - first `GYPSY_OPEN_DECK`

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Direct ContextMenu attempt | candidate=..., object=...`
- success path should then show either:
  - `Incoming gump packet detected`, or
  - `Expected gump already open despite no packet wait hit | source=ContextMenu`

## Known Fragilities
- This increases context attempts for robustness, so failure cycles are longer if gypsy context is blocked by shard-side gating.

---

# Iteration Update (2026-03-07): ClickObject Pre-Context + Cliloc Talk Candidate

## Task Summary
Latest telemetry showed all context attempts (including direct index calls) still failing to open any gump. Added explicit single-click priming and cliloc-id targeting for the gypsy talk entry.

Changes made:
- `scripts/confictura_bot/ca_shim.py`
  - Added `ClickObject` to known ClassicAssist command publication list.
- `scripts/confictura_bot/safe_api.py`
  - Added `safe_click_object(ctx, state_name, obj, settle_pause_ms)`.
- `scripts/gypsy_onboarding_controller.py`
  - `OPEN_GYPSY_CONTEXT` now calls `safe_click_object(...)` before `WaitForContext(...)` and before direct `ContextMenu(...)` attempts.
  - Added automatic candidate expansion when `"Talk"` is present:
    - appends cliloc candidate `6146`.
  - Added pre-context reset:
    - `WarMode("off")`
    - `CancelTarget()`
- `scripts/gypsy_onboarding_config.py`
  - Added `6146` explicitly to both gypsy context candidate lists.

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py`.
2. In `OPEN_GYPSY_CONTEXT`, verify you now see:
   - `Single-clicking object`
   - `Expanded context candidates with cliloc id | added=6146`
3. If this still fails, send full `OPEN_GYPSY_CONTEXT` block again (from first candidate through policy-advance/fail).

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][INFO] Single-clicking object | object=...`
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Expanded context candidates with cliloc id | added=6146`
- then either incoming gump detection or existing-gump detection.

## Known Fragilities
- If shard/client blocks scripted context selection entirely in this region, final fallback may require a one-time packet-level gump id capture probe.

---

# Iteration Update (2026-03-07): Any-Open-Gump Reply Fallback

## Task Summary
Your screenshot/log confirmed the gypsy tarot gump is visibly open, but ID-bound matching still fails (`expected_gump_id=0x3536596C`, `discovered_open_ids=`). Added a direct fallback path that can match by text and reply without a specific gump id.

Changes made:
- `scripts/confictura_bot/safe_api.py`
  - `safe_reply_gump(...)` now supports `gump_id <= 0` as "any open gump" mode.
  - In this mode it logs warning telemetry and sends `ReplyGump(0, button_id, ...)`.
- `scripts/confictura_bot/gump_router.py`
  - Added `InGump(0, <text>)` text-matching fallback (`_match_rules_any_open_gump`).
  - If a rule text matches any open gump, router now replies via any-open mode and logs:
    - `Gump rule matched via any-open-gump fallback`
  - Added explicit telemetry when engine probe returns no discovered ids:
    - `No discovered open gump ids from Engine.Gumps probe`

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` with the same character setup.
2. Focus on `GYPSY_OPEN_DECK` logs.
3. Success signature should include:
   - `No discovered open gump ids from Engine.Gumps probe` (possible)
   - `Replying without specific gump id | mode=any_open_gump`
   - `Gump rule matched via any-open-gump fallback | rule=Gypsy Start Tarot`
4. Then verify bot advances to `RACE_SHELF_OPEN`.

## Expected Telemetry
- `[FSM][GYPSY_OPEN_DECK][WARN] Replying without specific gump id | button_id=99, mode=any_open_gump`
- `[FSM][GYPSY_OPEN_DECK][WARN] Gump rule matched via any-open-gump fallback | rule=Gypsy Start Tarot, button_id=99, ...`

## Known Fragilities
- Any-open fallback is text-anchored, but if multiple open gumps contain overlapping phrases, wrong-target replies are still possible. Current phrase set (`Greetings`, `tarot`) keeps risk low for gypsy flow.

---

# Iteration Update (2026-03-07): Recorded Gypsy ID Alignment + Deterministic Context Entry

## Task Summary
Aligned gypsy onboarding behavior to your live ClassicAssist recording so the controller targets the same interaction path the client actually uses.

Your recording source-of-truth:
- `WaitForContext(0x4d506, 1, 5000)`
- `WaitForGump(0x758c021a, 5000)`
- `ReplyGump(0x758c021a, 99)`

Implemented changes:
- `scripts/gypsy_onboarding_config.py`
  - Set onboarding gypsy override:
    - `onboarding.gump_id_overrides["GYPSY_TAROT"] = 0x758C021A`
  - Narrowed both gypsy context steps to deterministic entry index only:
    - `context_entries: [1]`
  - Added safer default to avoid ambiguous any-open replies unless explicitly enabled:
    - `onboarding.allow_any_open_gump_fallback = False`

Rationale:
- Previous failures were driven by id mismatch (`0x3536596C` expected vs live `0x758C021A`) and over-broad context probing loops.
- This iteration uses the exact path verified by your macro recorder.

## Testing Instructions
1. Run `gypsy_onboarding_controller.py` from the start area as before.
2. Confirm `OPEN_GYPSY_CONTEXT` now only tries entry `1`.
3. Confirm `GYPSY_OPEN_DECK` shows expected id `0x758C021A` in telemetry.
4. Verify flow reaches race shelf steps before final gypsy completion path:
   - `RACE_SHELF_OPEN` -> `RACE_SHELF_SELECT` must happen before `GYPSY_DRAW_CARD`.
5. If gypsy still fails, capture only:
   - first `OPEN_GYPSY_CONTEXT` block
   - first `GYPSY_OPEN_DECK` block

## Expected Telemetry
- `[FSM][OPEN_GYPSY_CONTEXT][DEBUG] Waiting for context action | entry=1, ...`
- `[FSM][GYPSY_OPEN_DECK][INFO/WARN] ... expected_gump_id=0x758C021A ...`
- On success:
  - `[FSM][GYPSY_OPEN_DECK][INFO] Gump rule matched | rule=Gypsy Start Tarot, button_id=99, ...`
  - transition to `RACE_SHELF_OPEN`

## Known Fragilities
- If shard code changes gypsy gump id again, update `onboarding.gump_id_overrides` instead of editing controller logic.
- `allow_any_open_gump_fallback` is intentionally disabled to avoid wrong-gump replies while multiple gumps are open.
- Context menu index assumptions are now strict (`1`) by design for deterministic behavior; if server-side context entries change, this will fail fast with clear telemetry.

---

# Iteration Update (2026-03-07): ReplyGump .NET Argument Coercion Fix

## Task Summary
Fixed the runtime crash after successful gypsy gump match/reply:
- `Unhandled exception in tick | exception=expected Array[int], got list`

Root cause:
- `safe_reply_gump(...)` always called the 4-argument `ReplyGump(...)` overload and passed Python `list`/`dict` objects.
- IronPython/ClassicAssist expected .NET types (`Int32[]` and `Dictionary[Int32, String]`) for that overload.

Changes made:
- `scripts/confictura_bot/safe_api.py`
  - `safe_reply_gump(...)` now uses `ReplyGump(gump_id, button_id)` when there are no switches or text entries.
  - For payload replies, it now attempts to coerce payloads to:
    - `System.Array[Int32]` for switches
    - `System.Collections.Generic.Dictionary[Int32, String]` for text entries
  - Added warning telemetry if coercion fails before 4-arg reply call.

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` from the starting area.
2. Confirm `GYPSY_OPEN_DECK` no longer crashes after:
   - `Preparing gump reply ... gump_id=0x758C021A ...`
   - `Replying to gump ...`
3. Verify next transition reaches `RACE_SHELF_OPEN`.
4. If a new failure occurs, send logs from first `GYPSY_OPEN_DECK` through first `RECOVER` or `FATAL_STOP`.

## Expected Telemetry
- `[FSM][GYPSY_OPEN_DECK][DEBUG] Preparing gump reply | button_id=99, gump_id=0x758C021A, ...`
- `[FSM][GYPSY_OPEN_DECK][INFO] Replying to gump | button_id=99, gump_id=0x758C021A`
- Transition to:
  - `[FSM][RACE_SHELF_OPEN][INFO] Executing onboarding step ...`

## Known Fragilities
- If future steps require non-empty text entries/switches and .NET type coercion fails on a specific client build, telemetry now calls this out explicitly for targeted adjustment.

---

# Iteration Update (2026-03-07): Race Shelf Reachability + Ground Alias Compatibility Fix

## Task Summary
Resolved the new blocker after successful gypsy deck open:
- `RACE_SHELF_OPEN` repeatedly found the shelf, then failed on `Pathfind` and hit retry cap.
- ClassicAssist also printed `Unknown alias "ground"` during object lookup.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - Reworked `_find_object_alias(...)` to avoid `FindType(..., "ground", ...)` calls.
  - Object search now uses `FindType(graphic, range)` with optional hue filtering in-code (`Hue("found")`) and ignore-scan retries.
  - Reworked `_execute_use_object_ref(...)`:
    - Uses configurable interaction distance (`runtime.object_use_range`, default `3`).
    - Skips pathfind when already within interaction range.
    - Uses non-fatal, desired-distance pathfind for objects (`checkdistance=True`, `desireddistance=<range>`).
    - If pathfind fails but object is still within range, continues to `UseObject` instead of failing step.
- `scripts/confictura_bot/safe_api.py`
  - Extended `safe_pathfind(...)` with optional parameters:
    - `checkdistance`, `desireddistance`, `fail_on_error`
  - Added non-fatal warning mode when `fail_on_error=False`.
- `scripts/gypsy_onboarding_config.py`
  - Added runtime/config knobs:
    - `runtime.object_use_range = 3`
    - `world_refs.object_search_max_scan = 40`

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` from the same start area state.
2. Confirm gypsy step still succeeds into `RACE_SHELF_OPEN`.
3. In `RACE_SHELF_OPEN`, verify one of these telemetry paths:
   - `Skipping pathfind; object already within interaction range`, or
   - `Pathfind failed (non-fatal)` followed by `UseObject` attempt.
4. Confirm progression to `RACE_SHELF_SELECT` and first gump-rule processing.

## Expected Telemetry
- `[FSM][RACE_SHELF_OPEN][INFO] Matched object | ...`
- then either:
  - `[FSM][RACE_SHELF_OPEN][DEBUG] Skipping pathfind; object already within interaction range | ...`
  - or `[FSM][RACE_SHELF_OPEN][WARN] Pathfind failed (non-fatal) | ...`
- followed by:
  - `[FSM][RACE_SHELF_OPEN][INFO] Using object | object=onboarding_object`
  - transition to `[FSM][RACE_SHELF_SELECT][INFO] ...`

## Known Fragilities
- If multiple nearby statics share the same graphic and hue, search may still select the wrong candidate; additional positional filtering can be added next if needed.
- If shelf use requires line-of-sight constraints stricter than range-only checks, we may need a nearby-tile waypoint hint for that tent layout.

---

# Iteration Update (2026-03-07): Single-Retry Policy + Race Shelf Any-Open Reply Fallback

## Task Summary
Applied your requested retry policy and added a race-shelf-specific fallback for the case where the shelf gump is visibly open but id-bound matching fails.

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - Set `runtime.max_retries_per_state = 1` (single retry attempt policy).
  - For `RACE_SHELF_SELECT` rule, added:
    - `allow_any_open_reply = True`
- `scripts/gypsy_onboarding_controller.py`
  - Imported `safe_reply_gump` into controller.
  - In `_wait_and_apply_rule(...)`, added policy fallback:
    - if configured rule has `allow_any_open_reply=True` and normal id-based parse fails,
      attempt `safe_reply_gump(..., gump_id=0, button_id=<resolved>)`.
    - emits explicit telemetry:
      - `Attempting any-open gump reply fallback by policy`
      - `Any-open gump reply fallback succeeded`
- `scripts/confictura_bot/safe_api.py`
  - Hardened `safe_reply_gump(...)` to catch and report `ReplyGump` exceptions instead of bubbling raw exceptions.

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py`.
2. Confirm retry cap now behaves as one retry only.
3. Focus on `RACE_SHELF_SELECT`:
   - if normal parse fails, expect fallback telemetry.
4. Verify progression to `RENAME_CHARACTER` (or next immediate step after race select).

## Expected Telemetry
- `[FSM][RECOVER][WARN] Retrying onboarding step | max_retries=1, ...`
- `[FSM][RACE_SHELF_SELECT][WARN] Attempting any-open gump reply fallback by policy | ...`
- `[FSM][RACE_SHELF_SELECT][WARN] Any-open gump reply fallback succeeded | ...`

## Known Fragilities
- Any-open reply fallback is intentionally scoped to race shelf selection only. If multiple actionable gumps are open at that exact moment, reply targeting can still be ambiguous.

---

# Iteration Update (2026-03-07): Race Shelf Recorder Alignment + Rename Optional Skip

## Task Summary
Integrated your recorded ClassicAssist macro output as source-of-truth for race shelf behavior and removed rename as a hard blocker when no rename contract is present.

Recorder facts incorporated:
- Race shelf gump id: `0x54C2BB00`
- Help gump id observed: `0x5C045DAC`
- Human category selection button observed: `123456789`
- Race confirm OK button: `1000`

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - Added `onboarding.gump_id_overrides["RACE_POTIONS"] = 0x54C2BB00`
  - Added `onboarding.race_category_button_id = 123456789`
  - Kept `onboarding.race_button_id = 1000`
  - Added explicit two-step race shelf flow:
    - `RACE_SHELF_SELECT_CATEGORY` (category button)
    - `RACE_SHELF_SELECT` (OK/confirm button)
  - Set `onboarding.rename_allow_skip = True` so missing rename object does not halt onboarding.
- Existing single-retry policy remains in effect:
  - `runtime.max_retries_per_state = 1`

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` in the starting area.
2. Confirm sequence:
   - `RACE_SHELF_OPEN`
   - `RACE_SHELF_SELECT_CATEGORY`
   - `RACE_SHELF_SELECT`
3. Confirm either:
   - rename contract is found and rename runs, or
   - rename is skipped with warning policy and flow continues.
4. Send logs from first `RACE_SHELF_SELECT_CATEGORY` through `THUVIA_SELECT_MODE` (or fail point).

## Expected Telemetry
- `[FSM][RACE_SHELF_SELECT_CATEGORY][INFO] Gump rule matched | ... gump_id=0x54C2BB00 ...`
- `[FSM][RACE_SHELF_SELECT][INFO] Gump rule matched | ... button_id=1000 ...`
- If contract missing:
  - `[FSM][RENAME_CHARACTER][WARN] Rename failed for all candidates; skipping by policy | ...`

## Known Fragilities
- Rename contract location is shard/character-state dependent. This iteration intentionally allows progression when it is unavailable to keep onboarding autonomous.
- If race shelf UI content changes, category button ids may need minor config retuning.

---

# Iteration Update (2026-03-07): Thuvia Recorder Alignment (Gump ID Override)

## Task Summary
Aligned Thuvia mode-selection handling to your recorded macro values.

Recorder source-of-truth:
- `WaitForGump(0x9dd37300, 5000)`
- `ReplyGump(0x9dd37300, 1)` for PvP
- `ReplyGump(0x9dd37300, 2)` for PvE
- `ReplyGump(0x9dd37300, 0)` for Neutral

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - Added override:
    - `onboarding.gump_id_overrides["PKNONPK"] = 0x9DD37300`
  - Relaxed Thuvia rule text gate to avoid false negatives from content mismatch:
    - `THUVIA_SELECT_MODE.rule.text_any = []`
  - Existing button mapping logic remains unchanged:
    - `thuvia_mode -> button_id` via `button_from_mode`

## Testing Instructions
1. Run `gypsy_onboarding_controller.py`.
2. Confirm after `SPEAK_THUVIA_CHOOSE` the next step does not wait on old hash id.
3. In `THUVIA_SELECT_MODE`, verify expected id is now `0x9DD37300`.
4. Confirm transition continues to `RETURN_TO_GYPSY_SEAT`.

## Expected Telemetry
- `[FSM][THUVIA_SELECT_MODE][DEBUG/INFO] ... expected_gump_id=0x9DD37300 ...`
- `[FSM][THUVIA_SELECT_MODE][INFO] Gump rule matched | button_id=<0|1|2>, gump_id=0x9DD37300, ...`

## Known Fragilities
- If shard changes Thuvia gump id in future updates, adjust override only (no controller logic changes needed).
