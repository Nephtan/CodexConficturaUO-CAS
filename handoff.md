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

---

# Iteration Update (2026-03-07): Completion Check Debounce (Journal Timing + Distance Fallback)

## Task Summary
Onboarding reached Britain successfully but failed at final verification due journal timing race.

Observed behavior:
- Teleport success messages appeared in journal before or around verification step start.
- `VERIFY_TELEPORT_MESSAGE` then waited for *new* journal hits and timed out, causing false fail-stop.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - Enhanced `_execute_wait_journal_any(...)` with deterministic pre-check:
    - if step specifies `success_if_far_from_ref`, it computes distance from that reference tile.
    - if distance >= threshold, step passes immediately without waiting on journal timing.
  - Telemetry added:
    - `Completion condition met by distance from start area`
- `scripts/gypsy_onboarding_config.py`
  - Expanded completion journal list:
    - keeps card-vanish line
    - adds `You have entered the City of Britain.`
  - Updated `VERIFY_TELEPORT_MESSAGE` step:
    - `success_if_far_from_ref: "gypsy_seat"`
    - `success_min_distance: 20`

## Testing Instructions
1. Re-run `gypsy_onboarding_controller.py` from start area.
2. Confirm final stage after tarot draw does not fail-stop when teleport already occurred.
3. Success expected via one of two paths:
   - Journal line match, or
   - distance fallback pass.
4. Confirm `COMPLETE_STOP` instead of `FATAL_STOP`.

## Expected Telemetry
- On fallback path:
  - `[FSM][VERIFY_TELEPORT_MESSAGE][INFO] Completion condition met by distance from start area | ref=gypsy_seat, distance=..., min_distance=20`
- Final:
  - `[FSM][COMPLETE_STOP][INFO] Gypsy onboarding complete | ...`

## Known Fragilities
- City-entry journal strings may vary by destination; distance fallback now handles this deterministically.

---

# Iteration Update (2026-03-07): Thuvia Proximity Movement Policy

## Task Summary
Implemented requested movement behavior for Thuvia approach:
- Get within 1 tile of Thuvia.
- Do not stand on Thuvia's exact coordinate tile.

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - Updated `MOVE_TO_THUVIA` step:
    - `within_distance: 1`
    - `avoid_exact_tile: True`
- `scripts/gypsy_onboarding_controller.py`
  - Added proximity movement helper `_ensure_near_ref_tile(...)`.
  - Added XY-distance helper `_distance_to_tile_xy(...)`.
  - Updated `_execute_move_to_ref(...)`:
    - If step provides `within_distance`, use proximity pathing instead of exact-tile enforcement.
    - Respect `avoid_exact_tile` when evaluating success.

## Testing Instructions
1. Re-run onboarding script from start area.
2. Watch `MOVE_TO_THUVIA` telemetry for:
   - `Pathfinding near reference`
   - `desired_distance=1`
   - `avoid_exact_tile=True`
3. Confirm character stops adjacent to Thuvia (not on her coordinate tile).
4. Confirm remainder of flow still completes to `COMPLETE_STOP`.

## Expected Telemetry
- `[FSM][MOVE_TO_THUVIA][INFO] Pathfinding near reference | ... desired_distance=1, avoid_exact_tile=True`
- no exact-tile failure for Thuvia step.

## Known Fragilities
- If nearby obstacles force movement constraints, client pathfinding may still momentarily route through tight tiles; success gate now explicitly checks distance and exact-tile avoidance before passing.

---

# Iteration Update (2026-03-07): Pathfind Overload Compatibility Fix

## Task Summary
Resolved runtime crash in `MOVE_TO_THUVIA` proximity mode:
- `Pathfind() takes at most 3 arguments (5 given)`

Root cause:
- This ClassicAssist host does not expose advanced Pathfind overloads with `checkdistance` / `desireddistance` arguments.

Changes made:
- `scripts/confictura_bot/safe_api.py`
  - Updated `safe_pathfind(...)` to call only destination-only signatures:
    - `Pathfind(x, y, z)` or `Pathfind(obj)`
  - Kept `checkdistance` / `desireddistance` as telemetry metadata only.
  - Added exception capture in fail payloads.

Why this still preserves behavior:
- Proximity constraints are now enforced by controller-side distance checks in `_ensure_near_ref_tile(...)` rather than by Pathfind overload arguments.

## Testing Instructions
1. Re-run onboarding script.
2. Confirm `MOVE_TO_THUVIA` no longer throws Pathfind argument exception.
3. Confirm character ends adjacent to Thuvia and flow continues.

## Expected Telemetry
- `[FSM][MOVE_TO_THUVIA][INFO] Pathfinding near reference | ...`
- no `Pathfind() takes at most 3 arguments` exception.

---

# Iteration Update (2026-03-07): MOVE_TO_THUVIA Exact-Tile Sidestep Fix

## Task Summary
Fixed the remaining Thuvia proximity edge case where the character reached `distance=0` (standing on Thuvia's exact tile) and then looped until `FATAL_STOP`.

Root cause:
- `_ensure_near_ref_tile(...)` correctly rejected `distance=0` when `avoid_exact_tile=True`, but still kept pathing to the same destination tile, which cannot satisfy `distance>0`.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - Added `_build_adjacent_tiles(...)` to generate neighbor tiles around the reference tile.
  - Added `_step_off_exact_tile(...)` to actively sidestep from the exact tile to a valid adjacent tile.
  - Updated `_ensure_near_ref_tile(...)`:
    - When `current_distance == 0` and `avoid_exact_tile=True`, it now runs sidestep logic instead of re-pathing to destination.
    - If sidestep succeeds, step passes immediately.
    - If sidestep fails, step fails fast (no repeated re-path spam to same exact tile).

## Testing Instructions
1. Run `gypsy_onboarding_controller.py` from a fresh start-area character.
2. Watch `MOVE_TO_THUVIA`.
3. Verify behavior when character lands exactly on Thuvia tile:
   - It should log sidestep attempt.
   - It should move to adjacent tile and proceed to `SPEAK_THUVIA_CHOOSE`.
4. Confirm full run still reaches `COMPLETE_STOP`.

## Expected Telemetry
- `[FSM][MOVE_TO_THUVIA][WARN] Standing on exact tile; attempting sidestep | ...`
- `[FSM][MOVE_TO_THUVIA][DEBUG] Sidestep candidate | ...`
- `[FSM][MOVE_TO_THUVIA][INFO] Sidestep complete | distance=1, desired_distance=1`
- Then transition to next step without `Unable to reach required proximity to tile`.

## Known Fragilities
- If every adjacent tile is blocked by shard dynamics/mobiles at that instant, sidestep can still fail and the fail-safe policy will trigger.
- This fix is movement-policy specific; it does not alter gump logic or retry policy.

---

# Iteration Update (2026-03-07): Visitor Journal Rename Hardening (Policy + Shard Evidence)

## Task Summary
Updated rename flow to use Confictura shard evidence for the start-area rename object and removed default skip behavior.

Confirmed from `ConficturaRepositoryDocs/ConficturaRepository.xml`:
- Start-area placement: `ChangeName 20445 (Name=Visitor Journal)` at `3570 3400 7`
- Item implementation: `ChangeName : Item` with `base(0x14EF)` and `OnDoubleClick -> NameAlterGump`

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - `onboarding.rename_allow_skip = False` (fail-stop by default)
  - Added/updated world refs:
    - `rename_journal_graphic = 0x14EF`
    - `rename_journal_name_any = ["visitor journal", "name change contract"]`
    - `rename_journal_spot = (3570, 3400, 0)` (movement-safe floor reference near journal)
    - `rename_journal_range = 12`
- `scripts/gypsy_onboarding_controller.py`
  - `_find_object_alias(...)` now supports multi-factor matching:
    - graphic, hue, optional name tokens, optional find_location
    - logs `observed_names` and token filters on failure
  - `_resolve_object_refs(...)` and `_execute_use_object_ref(...)` now pass name tokens and optional find-location through to object search
  - `_rename_via_journal(...)` now:
    - paths near `rename_journal_spot` before lookup
    - matches Visitor Journal by configured name tokens
    - uses relaxed gump text gate (`text_any=[]`) for NameAlter rule to avoid brittle text coupling

## Testing Instructions
1. Run `gypsy_onboarding_controller.py` with a fresh starting-area character.
2. Watch `RENAME_CHARACTER` specifically:
   - confirm `Pathfinding near Visitor Journal`
   - confirm `Matched object` includes name token context
   - confirm gump submit attempts for each candidate name
3. If all candidates are unavailable, expect fail-stop (not skip).
4. Share logs from `RENAME_CHARACTER` start through either success or fail-stop.

## Expected Telemetry
- `[FSM][RENAME_CHARACTER][INFO] Pathfinding near Visitor Journal | ...`
- `[FSM][RENAME_CHARACTER][INFO] Matched object | graphic=0x14ef, ... name_tokens=visitor journal|name change contract`
- success path:
  - `[FSM][RENAME_CHARACTER][INFO] Rename succeeded | ...`
- fail-stop path:
  - `[FSM][RENAME_CHARACTER][ERROR] Rename failed for all candidate names | ...`

## Known Fragilities
- Candidate names can be rejected by shard naming rules/uniqueness; this is now intentionally fail-stop unless skip policy is explicitly re-enabled.
- If start-area decoration/layout changes, only `rename_journal_spot` / token list should need config retuning.

---

# Alpha Retrospective (2026-03-07)

## Lessons Learned
1. ClassicAssist recorder output is authoritative for command sequencing and practical button IDs.
2. Gump packet waits alone are insufficient; open-gump state checks are required in parallel.
3. Confictura server code/world definitions must drive object IDs, names, and placement assumptions.
4. Context menu handling requires shard-specific candidate strategies and explicit telemetry.
5. Pathfind overload support varies by host; proximity intent should be enforced in controller logic.
6. ?Near but not exact tile? requires explicit sidestep behavior when `distance=0` occurs.
7. One-retry policy gives faster signal and reduces noisy loops on deterministic failures.
8. Completion verification should combine journal checks with world-state fallbacks.
9. Optional-step skipping should be explicit policy, off by default for critical onboarding steps.
10. High-verbosity structured telemetry is the core debugging tool for blind development.


---

# Iteration Update (2026-03-07): Object Finder Overload Regression Fix (Race Shelf)

## Task Summary
Fixed regression where `RACE_SHELF_OPEN` stopped finding the race shelf after object-matching hardening.

Root cause:
- `_find_object_alias(...)` started using extended `FindType(...)` overloads for hue/location filtering.
- On this ClassicAssist host, that overload path can fail, causing immediate `found=False` and no object discovery.

Changes made:
- `scripts/gypsy_onboarding_controller.py`
  - `_find_object_alias(...)` now uses host-safe search order:
    1. Try `FindType(graphic, range, find_location)` only if location is explicitly provided.
    2. Fallback to `FindType(graphic, range)`.
  - Hue validation remains manual via `Hue("found")` after object discovery.
  - Name-token matching remains manual via `Name("found")` after object discovery.

This restores race shelf compatibility while keeping the new multi-factor matching behavior.

## Testing Instructions
1. Run onboarding again from start area.
2. Confirm `RACE_SHELF_OPEN` finds shelf instead of failing at index 4.
3. Confirm flow continues into:
   - `RACE_SHELF_SELECT_CATEGORY`
   - `RACE_SHELF_SELECT`
   - `RENAME_CHARACTER`
4. Share log from `RACE_SHELF_OPEN` through `RENAME_CHARACTER` outcome.

## Expected Telemetry
- `[FSM][RACE_SHELF_OPEN][INFO] Matched object | graphic=0x506c, hue=2750, ...`
- no immediate `Unable to locate required object` at race shelf step.

## Known Fragilities
- If the shard/client changes `FindType` signature behavior again, this function is now biased toward minimal overloads to stay compatible.
- Location-constrained search still depends on host support for the 3-argument form.

## Iteration Addendum (2026-03-07): Visitor Journal Pre-Path Relaxation

Adjustment made after live failure telemetry:
- `RENAME_CHARACTER` was failing before object interaction because strict pre-path to `rename_journal_spot` could not satisfy proximity in that tent layout.

Change:
- In `_rename_via_journal(...)`, inability to path near Visitor Journal is now warning-only.
- Flow now continues to direct object lookup (`FindType` + hue/name token checks) instead of hard-failing on movement alone.

Expected effect:
- Rename step now validates based on actual ability to find/use the Visitor Journal, not on pre-positioning success.

## Iteration Update (2026-03-07): Rename Feature Removal (Project Runtime)

## Task Summary
Removed character-rename functionality from the runtime onboarding project code path.

Changes made:
- `scripts/gypsy_onboarding_config.py`
  - Removed all rename config keys and world refs.
  - Removed `RENAME_CHARACTER` step from `steps`.
  - Onboarding sequence is now 14 total steps.
- `scripts/gypsy_onboarding_controller.py`
  - Removed `rename_via_journal` action dispatch.
  - Removed `_rename_via_journal(...)` function.
  - Removed rename bootstrap counters/fields.
  - Removed rename field from completion telemetry.
  - Updated controller metadata description to reflect no rename path.
- `scripts/confictura_bot/gump_ids.py`
  - Removed `NAME_ALTER` and `NAME_CHANGE` constants.

## Testing Instructions
1. Start in the gypsy tent and run the onboarding macro.
2. Confirm total step count logs as `step_count=14` during `BOOTSTRAP`.
3. Confirm flow proceeds:
   - `GYPSY_OPEN_DECK`
   - `RACE_SHELF_OPEN`
   - `RACE_SHELF_SELECT_CATEGORY`
   - `RACE_SHELF_SELECT`
   - `MOVE_TO_THUVIA`
4. Confirm there are no `RENAME_CHARACTER` logs and no rename retries.
5. Confirm flow reaches `COMPLETE_STOP` after teleport success verification.

## Expected Telemetry
- `[FSM][BOOTSTRAP][INFO] Bootstrap ready | ..., step_count=14`
- No telemetry entries containing `RENAME_CHARACTER`.
- Standard completion:
  - `[FSM][COMPLETE_STOP][INFO] Gypsy onboarding complete | completed_steps=14, total_steps=14, ...`

## Known Fragilities
- Historical handoff sections above this update still include older rename-era logs for traceability; runtime code no longer executes rename behavior.


## Iteration Update (2026-03-07): Thuvia-First Route + Neutral Skip

## Task Summary
Adjusted onboarding route to reduce travel backtracking:
- Thuvia flow now executes before moving to gypsy seat.
- If `onboarding.thuvia_mode == "NEUTRAL"`, Thuvia steps are skipped entirely by policy.
- Removed redundant `RETURN_TO_GYPSY_SEAT` step from the flow.

Implementation notes:
- `scripts/gypsy_onboarding_config.py`
  - Reordered `steps` to start with:
    - `MOVE_TO_THUVIA`
    - `SPEAK_THUVIA_CHOOSE`
    - `THUVIA_SELECT_MODE`
  - Added `skip_if_mode: "NEUTRAL"` on all three Thuvia steps.
  - Removed `RETURN_TO_GYPSY_SEAT`.
- `scripts/gypsy_onboarding_controller.py`
  - Extended `_step_enabled(...)` to honor per-step `skip_if_mode` (string or list/tuple).
  - Skip telemetry now includes `enabled_flag`, `skip_if_mode`, and current `thuvia_mode`.

## Testing Instructions
1. Set `onboarding.thuvia_mode = "PVE"`.
2. Run macro in starting area and confirm first executed action is `MOVE_TO_THUVIA`.
3. Confirm flow then goes to `MOVE_TO_GYPSY_SEAT` and does not include `RETURN_TO_GYPSY_SEAT`.
4. Set `onboarding.thuvia_mode = "NEUTRAL"`.
5. Run again and confirm:
   - `MOVE_TO_THUVIA`, `SPEAK_THUVIA_CHOOSE`, `THUVIA_SELECT_MODE` are skipped.
   - First movement action is `MOVE_TO_GYPSY_SEAT`.

## Expected Telemetry
- Non-neutral modes:
  - `[FSM][MOVE_TO_THUVIA][INFO] Executing onboarding step | ...`
- Neutral mode:
  - `[FSM][MOVE_TO_THUVIA][INFO] Step skipped by policy | skip_if_mode=NEUTRAL, thuvia_mode=NEUTRAL, ...`
  - same for `SPEAK_THUVIA_CHOOSE` and `THUVIA_SELECT_MODE`.

## Known Fragilities
- If `thuvia_mode` contains unexpected text, mode-based button selection defaults to `NEUTRAL` behavior; keep values within `NEUTRAL|PVP|PVE`.

## Iteration Addendum (2026-03-07): Enabled-Flag Hardening + Final Gypsy Rule Relaxation

Adjustment made after neutral-mode run telemetry:
- Race shelf steps were unexpectedly policy-skipped despite configured enable flag.
- Final gypsy open-deck step failed on strict text matching when expected gump was already open in a different content state.

Changes:
- `scripts/gypsy_onboarding_controller.py`
  - `_step_enabled(...)` now normalizes flag values robustly (`bool`, numeric, and string forms such as `true/false`, `on/off`, `1/0`).
  - Skip telemetry now includes `enabled_flag_value` to expose the actual evaluated value.
- `scripts/gypsy_onboarding_config.py`
  - `GYPSY_OPEN_DECK_FINAL.rule.text_any` set to empty list so gump-id match can proceed without brittle content string requirements.

Expected effect:
- Race shelf enable flag behavior is deterministic and diagnosable from logs.
- Final gypsy transition is tolerant when the tarot gump is already open but not on the exact prior text page.

---

# Beta Retrospective (2026-03-07): Starting Area Clear Achieved

## Lessons Learned
1. ClassicAssist Recorder output is the strongest operational truth for interaction sequencing and button IDs.
2. Confictura-specific behavior must be assumed by default; vanilla assumptions cause avoidable failures.
3. Gump handling must combine packet waits with open-gump state checks (`GumpExists`) to handle client/state desyncs.
4. Stateful gumps (like Gypsy tarot) should not rely on strict text signatures once flow is already established.
5. Context interactions require shard-safe fallbacks (named entry + numeric entry + telemetry evidence).
6. Step policy must be explicit and data-driven (`enabled_flag`, `skip_if_mode`) with clear skip telemetry.
7. Config booleans must be normalized robustly (bool/int/string) before policy decisions.
8. Pathing intent matters: ?within distance? and ?avoid exact tile? need explicit controller logic, not just raw `Pathfind` calls.
9. Host/API signature variance is real (e.g., `Pathfind`/`FindType` overload behavior); wrappers and fallback paths are required.
10. One-retry fail-fast policy is effective on this shard due low lag and deterministic failure modes.
11. Completion checks should include world-state fallbacks (distance from start zone) in addition to journal-only checks.
12. High-verbosity structured telemetry is the primary debugger for blind development and should be treated as part of runtime design.

## Beta Status
- Gypsy/Thuvia/race/tarot onboarding now clears the starting area and reaches terminal completion under tested paths.
- This is the current baseline for post-start-world autonomous module work.

---

# Iteration Update (2026-03-07): Britain Spawn-to-Thief Recon FSM (No Theft)

## Task Summary
Implemented a new recon-only post-onboarding FSM for Britain-to-Thieves-Guild mapping that never issues theft/combat actions.

New files:
- `scripts/britain_thief_recon_controller.py`
- `scripts/britain_thief_recon_config.py`

What was added:
- Deterministic FSM states for recon flow:
  - `BOOTSTRAP -> CAPTURE_SPAWN -> TRAVEL_TO_WAYPOINT -> RECON_SCAN -> ADVANCE_WAYPOINT -> FINAL_SUMMARY -> COMPLETE_STOP`
  - plus `RECOVER` and `FATAL_STOP`
- ClassicAssist runtime hygiene:
  - import-cache purge for `britain_thief_recon_config` and `confictura_bot*`
  - API publication telemetry via `publish_known_ca_api(...)`
- Multi-pass mobile acquisition policy (bounded scans):
  - `GetEnemy(..., "Next", ...)` pass
  - `GetFriend(..., "Next", ...)` pass
  - bounded attempts and structured failure evidence (`observed_names`, `search_range`, `scan_order`, `scan_counts`)
- Object watch recon for thief hub artifacts and fixtures:
  - stealing board, pickpocket dip, training dummy, practice lockboxes, guild bank vault, and secret doors
- Fail-fast risk policy:
  - `risk.fail_fast_on_guard_or_criminal = True`
  - immediate fatal stop on self criminal/murderer state or nearby guard-name token hit
- Final structured summary payload:
  - discovered mobile/object serial+name+position tuples per watch target
  - unresolved expected watch targets

No `UseSkill("Stealing")`, `Attack(...)`, or theft logic is used in this controller.

## Testing Instructions
1. Finish onboarding so the character is in Britain, then run:
   - `scripts/britain_thief_recon_controller.py`
2. Confirm bootstrap checks and spawn capture:
   - `BOOTSTRAP` validates required config sections
   - `CAPTURE_SPAWN` prints current map/position snapshot
3. Confirm route traversal through configured thief-hub waypoints around:
   - `3409-3421, 3187-3203` (Sosaria context)
4. Confirm `RECON_SCAN` behavior at each waypoint:
   - multi-pass mobile scan executes
   - object watches attempt discovery
   - unmatched targets emit structured warning evidence (not silent)
5. Confirm final stop behavior:
   - `FINAL_SUMMARY` prints discovered tuples + unresolved target lists
   - `COMPLETE_STOP` reports deterministic stop cause (`recon_complete`)
6. Policy checks:
   - Ensure no stealing/combat command is triggered by this script
   - If character becomes criminal or guard token is detected nearby, verify immediate fail-stop path

## Expected Telemetry
- `[FSM][BOOTSTRAP][INFO] Bootstrap ready | waypoint_count=..., mobile_watch_count=..., object_watch_count=...`
- `[FSM][CAPTURE_SPAWN][INFO] Captured spawn snapshot | map=..., x=..., y=..., z=...`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Action preconditions | strategy=safe_pathfind, destination=(...), within_distance=...`
- `[FSM][RECON_SCAN][INFO] Action preconditions | selector_strategy=multi_pass_enemy_friend_next, ...`
- `[FSM][RECON_SCAN][INFO] Mobile watch matched | watch_name=..., matched_count=...`
- `[FSM][RECON_SCAN][WARN] Mobile watch unmatched | observed_names=..., scan_order=..., scan_counts=...`
- `[FSM][RECON_SCAN][INFO] Object watch matched | watch_name=..., matched_count=...`
- `[FSM][RECON_SCAN][WARN] Object watch unmatched | expected=graphic=...,hue=..., observed=..., counts=...`
- `[FSM][FINAL_SUMMARY][INFO] Recon summary ready | discovered_mobiles=..., discovered_objects=..., unresolved_mobile_watch=..., unresolved_object_watch=...`
- `[FSM][COMPLETE_STOP][INFO] Britain thief recon complete | stop_cause=recon_complete, ...`

## Known Fragilities
- `GetEnemy/GetFriend` overload behavior can vary by host build; controller includes fallback signatures, but edge hosts may still require tuning.
- Static object graphics in the thief hub can change with shard updates; retune only `recon.object_watch` entries in config.
- Route waypoints are shard-evidence defaults near thief hub and may need coordinate adjustment if spawn/corridor pathing differs live.
- Guard-token detection is name-based and conservative by policy; crowded sessions may trigger intentional fail-fast stops.
- Unmatched watches are warning-only by default (`recon.fail_if_unresolved=False`) to keep recon runs finishable while collecting evidence.

## Iteration Addendum (2026-03-07): Britain Long-Hop Pathfind Failure Fix

## Task Summary
Applied a route/interact fix after live run failure:
- Failure observed: `Maximum distance exceeded` when trying to path directly from Britain spawn (`~2999,1030`) to thief-hub waypoint (`3409,3198`).
- Root cause: first waypoint assumed same-map walk path; shard flow requires nearby `PublicDoor` use to enter Thieves Guild area.
- Fix implemented:
  - Added first waypoint at `3006,1108,0` with `interaction.type = "public_door"`.
  - Interaction resolves object by `graphic+hue+name_tokens` (`oak shelf` / `trapdoor`), uses object, then verifies destination by region/proximity.
  - Added policy `scan_enabled=False` on pre-guild hop waypoints so Britain-area scans do not trigger guard-token fail-fast.
  - Travel state now conditionally skips scanning when `scan_enabled` is false and advances waypoint deterministically.

## Testing Instructions
1. Start from the same post-onboarding Britain spawn used in the failed run.
2. Run `scripts/britain_thief_recon_controller.py`.
3. Confirm sequence:
   - `TRAVEL_TO_WAYPOINT` reaches `britain_public_door_to_thieves`
   - `Executing waypoint interaction`
   - `Waypoint interaction verified` with either `reason=expected_region` or `reason=expected_destination`
   - `Waypoint scan skipped by policy` for the first 1-2 waypoints
4. Confirm later waypoints enter `RECON_SCAN` and produce watch telemetry.

## Expected Telemetry
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Waypoint reached | waypoint_name=britain_public_door_to_thieves, ...`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Executing waypoint interaction | interaction_type=public_door, target_name=...`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Waypoint interaction verified | reason=expected_region|expected_destination, ...`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Waypoint scan skipped by policy | waypoint_name=britain_public_door_to_thieves, scan_enabled=False`

## Known Fragilities
- If the shard remaps public-door source tile or object identity (graphic/hue/name), retune only the first waypoint `interaction` block in config.
- If entry region name differs from `the Thieves Guild`, update `interaction.expected_region` or rely on destination-distance verification.

## Iteration Addendum (2026-03-07): ClassicAssist Macro Loader Added

## Task Summary
Added a thin Macro-tab loader file:
- `scripts/britain_thief_recon_loader.py`
- Appends repo `scripts` path, purges cached `confictura_bot*` and recon modules, then `execfile(...)` runs `britain_thief_recon_controller.py`.

## Testing Instructions
1. In ClassicAssist Macros, create a script from `scripts/britain_thief_recon_loader.py` content.
2. Run from post-onboarding Britain spawn.
3. Confirm first logs include API publication and `Starting BritainThiefReconController`.

## Iteration Addendum (2026-03-07): Segmented Pathfinding For Spawn-to-Door Travel

## Task Summary
Applied controller-side movement hardening after live log still showed:
- `Maximum distance exceeded` on first waypoint pathfind from spawn (`2999,1030`) to public-door source (`3006,1108`).

Changes:
- `scripts/britain_thief_recon_controller.py`
  - Added bounded hop candidate planner:
    - diagonal segment toward destination
    - axis-X fallback
    - axis-Y fallback
  - `TRAVEL_TO_WAYPOINT` now uses segmented mode when `remaining_distance > runtime.pathfind_max_hop_distance`.
  - Each segment call uses `safe_pathfind(..., fail_on_error=False)` and emits explicit candidate order telemetry.
  - Added fail-stop checks for non-progressing segments (`pathfind_min_progress`).
- `scripts/britain_thief_recon_config.py`
  - Added runtime tuning keys:
    - `pathfind_max_hop_distance: 12`
    - `pathfind_min_progress: 1`

## Testing Instructions
1. Stand at spawn (`2999,1030`) and run recon loader.
2. Confirm `TRAVEL_TO_WAYPOINT` logs:
   - `strategy=safe_pathfind_segmented`
   - `Segment path preconditions`
   - repeated `Segment path progress` until within hop range
3. Confirm state eventually reaches:
   - `Waypoint reached | waypoint_name=britain_public_door_to_thieves`
   - then door interaction logs.

## Expected Telemetry
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Action preconditions | ..., strategy=safe_pathfind_segmented, remaining_distance=..., max_hop_distance=12`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Segment path preconditions | candidate_order=...`
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Segment path progress | before=..., after=..., progress=...`

## Known Fragilities
- If local terrain blocks all three hop candidates, run fails fast with `Segment pathfind failed` and candidate evidence payload.
- If shard/client changes per-call movement limits, retune only `runtime.pathfind_max_hop_distance` in config.

## Iteration Addendum (2026-03-08): Stall-Tolerant Segmented Movement

## Task Summary
Live log showed segmented routing was partially working but failed too aggressively on transient stalls:
- Movement advanced from spawn to around `3000,1048`.
- Controller failed on single `progress=0` segment checks, consuming retries and stopping.

Fixes applied:
- `scripts/britain_thief_recon_controller.py`
  - Segment mode now evaluates candidate outcomes per attempt (`before/after/progress`) and records structured evidence.
  - Single no-progress segment is now warning-path, not immediate fatal-recover.
  - Added bounded stall counter on context (`segment_no_progress_count`) with tolerance gate.
  - Fail-stop now occurs only when no-progress count exceeds configured tolerance.
  - Stall counter resets on successful segment progress and on direct waypoint-path success.
- `scripts/britain_thief_recon_config.py`
  - Added runtime tuning:
    - `segment_no_progress_tolerance: 4`
    - `segment_stall_pause_ms: 250`

## Testing Instructions
1. Keep character at current position (`3000,1048`) and run recon loader.
2. Confirm logs may include intermittent:
   - `Segment path no progress` warnings with `stall_count` increasing.
3. Confirm run continues through warnings and resumes progress before tolerance exceeded.
4. Confirm eventual arrival at first waypoint and door interaction attempt.

## Expected Telemetry
- `[FSM][TRAVEL_TO_WAYPOINT][WARN] Segment path no progress | stall_count=..., stall_tolerance=4, candidate_results=...`
- subsequent successful recovery:
  - `[FSM][TRAVEL_TO_WAYPOINT][INFO] Segment path progress | before=..., after=..., progress=...`

## Known Fragilities
- If terrain repeatedly blocks all candidate hops, controller will still fail-stop when `stall_count > segment_no_progress_tolerance` by design.
- If movement remains too slow, increase `segment_stall_pause_ms` before relaxing tolerance.

## Iteration Addendum (2026-03-08): Segment Progress Classification + Lateral Escape Candidates

## Task Summary
Live telemetry exposed two movement bugs near `remaining_distance ~16`:
1. Segment attempts with `ok=False` but real movement (`before->after`) were treated as no-progress.
2. One-axis approach produced single repeated candidate (`3006,1104,0`) with no lateral escape options.

Fixes applied:
- `scripts/britain_thief_recon_controller.py`
  - Segment success now keys on measured movement (`progress_candidate >= min_progress`) regardless of `Pathfind` boolean return.
  - `_build_segment_candidates(...)` now emits expanded pool:
    - primary, axis-x, axis-y, short-forward
    - plus lateral sidestep candidates to break one-axis stalls.
  - `RECOVER.enter` resets `segment_no_progress_count` for `TRAVEL_TO_WAYPOINT` retries.

## Testing Instructions
1. Re-run from the current stuck corridor area.
2. Confirm segment logs now show:
   - additional sidestep candidates in `candidate_order` when path narrows.
   - progress accepted even when candidate row has `ok=False` but `progress>0`.
3. Confirm no immediate repeat-lock on `3006,1104,0` unless all lateral escapes are blocked.

## Expected Telemetry
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Segment path preconditions | candidate_count=...` with >1 candidate near stalls.
- `[FSM][TRAVEL_TO_WAYPOINT][INFO] Segment path progress | ...` on any measured distance drop, including prior `ok=False` movement cases.

## Iteration Addendum (2026-03-08): Close-Range Segment Routing (No Direct Flip)

## Task Summary
Live run reached near-target corridor but failed when logic switched from segmented to direct pathing at `remaining_distance <= max_hop_distance`.
- Direct call to exact tile (`3006,1108`) failed repeatedly despite nearby progress.

Fixes applied:
- `scripts/britain_thief_recon_controller.py`
  - Segmented routing now remains active for all distances until `within_distance` is met.
  - Removed brittle direct-only path attempt branch for close-range movement.
  - Added `movement_not_required` strategy when already within waypoint proximity.
- `_build_segment_candidates(...)`
  - Removed early-return-to-destination behavior for `remaining_distance <= max_hop_distance`.
  - Candidate generation now uses `step_limit=min(max_hop_distance, remaining_distance)` so close-range still gets fallback options (short-forward + lateral).

## Testing Instructions
1. Re-run from current close-range position near `(3006,1097)` corridor.
2. Confirm `strategy=safe_pathfind_segmented` continues while distance remains above `within_distance`.
3. Confirm candidate list remains multi-option near close range instead of collapsing to direct-only.
4. Confirm transition to `Waypoint reached` once distance <= configured proximity.

## Iteration Update (2026-03-08): Britain-First Standalone Pathing R&D Harness

### Task Summary
Implemented an isolated Britain-only pathfinding R&D stack without replacing existing production movement logic.

New files:
- `scripts/confictura_bot/pathing.py`
- `scripts/britain_pathing_rd_config.py`
- `scripts/britain_pathing_rd_controller.py`
- `scripts/britain_pathing_rd_loader.py`

What was built:
- New shared API:
  - `navigate_to_coordinate(ctx, state_name, destination, options)`
  - Returns structured result: `success`, `stop_reason`, `final_distance`, `attempts`, `elapsed_ms`, `evidence`
- Policy-level behavior in shared module (built on top of `safe_pathfind` primitive):
  - Segmented adaptive hops
  - Proximity completion via `within_distance`
  - Candidate diversity: `primary`, `axis_x`, `axis_y`, `short_forward`, lateral sidesteps
  - Progress measured by distance delta (not bool-only pathfind result)
  - Bounded stall tolerance and hop-size backoff/recovery
  - Deterministic stop budgets (`max_attempts`, `max_ms`) with explicit `stop_reason`
- Dedicated Britain harness controller with staged route execution and summary aggregation.
- Dedicated Britain test config with:
  - Runtime tuning knobs
  - Fixed route set (short/medium/long/chokepoint/negative)
  - Optional random batch within Britain bounds
- Dedicated macro loader to isolate test execution from existing FSMs.

### Testing Instructions
1. In ClassicAssist Macro tab, run `scripts/britain_pathing_rd_loader.py` (or copy its content into a macro).
2. Stand in Britain start area (same-map walking context).
3. Run harness and let it progress through all configured stages:
   - Stage 1: local short sanity routes
   - Stage 2: corridor/chokepoint routes
   - Stage 3: medium/long routes
   - Stage 4: random-batch routes within configured bounds
   - Stage 5: negative/unreachable routes
4. If route tuning is needed, edit only `scripts/britain_pathing_rd_config.py`:
   - `pathing_defaults`
   - `test_harness.fixed_routes`
   - `test_harness.random_batch`
5. Re-run via loader after each tuning iteration; import cache purge is built in.

### Expected Telemetry Contract
Per harness route:
- `[FSM][RUN_ROUTE][INFO] Action preconditions | route_name=..., stage_name=..., destination=..., expected_reachable=...`

Per shared pathing attempt:
- `[FSM][RUN_ROUTE][DEBUG] Pathing attempt | attempt=..., hop_size=..., candidate_order=..., stall_count=...`
- `[FSM][RUN_ROUTE][INFO] Pathing progress | selected_candidate=..., before=..., after=..., progress=...`
- `[FSM][RUN_ROUTE][WARN] Pathing stall detected | stall_count=..., candidate_results=...`

Per route result:
- `[FSM][RUN_ROUTE][INFO|WARN] Route test passed|failed | pass_reason=..., stop_reason=..., attempts=..., elapsed_ms=...`

Final summary:
- `[FSM][FINAL_SUMMARY][INFO] Britain pathing RnD summary | route_total=..., route_pass=..., reachable_success_rate=..., baseline_ready=...`
- `[FSM][FINAL_SUMMARY][INFO] Route summary row | idx=..., stage=..., route=..., passed=..., stop_reason=...`

### Summary Report (Current)
Execution status in this Codex environment: `NOT_RUN` (live shard/operator run required).

| Stage | Route | Expected Outcome | Current Result |
|---|---|---|---|
| stage_1_local_sanity | sanity_short_north | PASS (reachable) | NOT_RUN |
| stage_1_local_sanity | sanity_short_east | PASS (reachable) | NOT_RUN |
| stage_1_local_sanity | sanity_return_origin | PASS (reachable) | NOT_RUN |
| stage_2_corridor_chokepoint | corridor_public_door_lane | PASS (reachable) | NOT_RUN |
| stage_2_corridor_chokepoint | corridor_market_cross | PASS (reachable) | NOT_RUN |
| stage_2_corridor_chokepoint | corridor_guard_traffic | PASS (reachable) | NOT_RUN |
| stage_3_medium_long_routes | medium_town_square | PASS (reachable) | NOT_RUN |
| stage_3_medium_long_routes | long_west_gate_approach | PASS (reachable) | NOT_RUN |
| stage_3_medium_long_routes | long_east_court_approach | PASS (reachable) | NOT_RUN |
| stage_4_random_batch | random_batch_01..random_batch_08 | PASS target >= 90% reachable success | NOT_RUN |
| stage_5_negative_unreachable | negative_invalid_high_z | PASS (expected bounded failure) | NOT_RUN |
| stage_5_negative_unreachable | negative_probable_blocked_tile | PASS (expected bounded failure) | NOT_RUN |

Exit criteria to confirm on live run:
- Reachable-route success rate >= 90%
- No infinite loops
- All failures terminate with deterministic structured evidence (`stop_reason`, `candidate_order`, `candidate_results`, counters)

### Recommended Default Tuning Values
Initial recommended defaults (already set in `pathing_defaults`):
- `within_distance=2`
- `settle_ms=350`
- `max_hop_distance=12`
- `min_hop_distance=2`
- `min_progress=1`
- `stall_tolerance=4`
- `stall_pause_ms=250`
- `max_attempts=120`
- `max_ms=120000`
- `hop_backoff_step=2`
- `hop_recover_step=1`
- `lateral_step=1`

### Known Fragilities
- Some fixed coordinates are Britain baseline candidates and may require shard-live adjustment for blocked tiles or dynamic traffic patterns.
- Negative route `negative_probable_blocked_tile` is intentionally heuristic; if it becomes reachable live, keep it but update expected behavior and/or coordinate.
- Same-map-only policy is enforced by default (`enforce_same_map=True`); cross-map transitions are out of scope for this v1 module.

## Iteration Addendum (2026-03-08): Live Run Feedback Integration - False Progress Loop Fix

### Live Observations Received
Operator run confirmed:
- Stage 1 routes passed (`sanity_short_north`, `sanity_short_east`, `sanity_return_origin`).
- Stage 2 routes passed (`corridor_public_door_lane`, `corridor_market_cross`, `corridor_guard_traffic`).
- Harness later entered a long repeat pattern in Stage 3 (`medium_town_square`) without reaching fail-stop before manual operator stop.
- Manual stop location: `(3002, 1126, 0)` under south Britain wall gate.

### Root Cause
`navigate_to_coordinate(...)` classified progress using per-candidate `before -> after` delta inside the same attempt. In obstacle oscillation cases this can report `progress=1` while attempt-level distance does not actually improve, preventing stall/fail-stop escalation.

### Fix Applied
Updated shared module:
- `scripts/confictura_bot/pathing.py`

Behavior change:
- Progress gate now uses **attempt-start distance** (`attempt_start_distance - after_distance`) instead of per-candidate `before - after` only.
- Candidate telemetry now includes both values:
  - `candidate_progress`
  - `attempt_progress`

Expected effect:
- Repeated oscillation at a fixed attempt distance no longer resets progress incorrectly.
- Stall tolerance should now trigger deterministic fail-stop when true attempt-level progress is absent.

### Re-Test Instructions
1. Start from current operator location `(3002, 1126, 0)`.
2. Run `scripts/britain_pathing_rd_loader.py`.
3. Capture telemetry from:
   - first `RUN_ROUTE` line for `medium_town_square`
   - first `Pathing stall detected`
   - terminal route result (`Pathing finished` + `Route test passed|failed`) for that route
4. If the route now fails, expected stop reason should be deterministic (`stall_tolerance_exceeded` or budget stop).

### Expected Telemetry Delta
- `Pathing progress` lines now report:
  - `progress=<attempt_progress>`
  - `candidate_progress=<candidate_before_after_delta>`
- In false-progress loops, `progress` should remain `0` and stall counter should rise toward deterministic stop.

## Iteration Addendum (2026-03-08): Server Action Delay Floor Enforcement (600ms)

### Task Summary
Applied a hard minimum action-delay policy to avoid issuing movement/actions faster than shard tolerance.

Updated files:
- `scripts/confictura_bot/pathing.py`
- `scripts/britain_pathing_rd_config.py`
- `scripts/britain_pathing_rd_controller.py`

What changed:
- Shared pathing options now include `min_action_delay_ms` (default `600`).
- `navigate_to_coordinate(...)` clamps both:
  - `settle_ms >= min_action_delay_ms`
  - `stall_pause_ms >= min_action_delay_ms`
- Harness config defaults raised to 600ms pacing:
  - `runtime.tick_pause_ms: 600`
  - `runtime.pause_between_routes_ms: 600`
  - `pathing_defaults.settle_ms: 600`
  - `pathing_defaults.stall_pause_ms: 600`
  - `pathing_defaults.min_action_delay_ms: 600`
- Harness controller fallback for route-to-route pause updated to 600ms when config is absent.

### Testing Instructions
1. Start from current location `(3002, 1126, 0)`.
2. Run `scripts/britain_pathing_rd_loader.py`.
3. Confirm precondition telemetry prints:
   - `min_action_delay_ms=600`
   - `settle_ms=600`
   - `stall_pause_ms=600`
4. Spot-check pathing request cadence in logs to ensure no rapid sub-600 burst behavior.

### Expected Telemetry
- `[FSM][RUN_ROUTE][INFO] Pathing action preconditions | ..., min_action_delay_ms=600, settle_ms=600, stall_pause_ms=600`

### Known Fragilities
- If server enforces higher than 600ms during load/save windows, further tuning may still be required (recommended next step would be `650-750ms`).

## Iteration Addendum (2026-03-08): Data-Driven Britain Coverage (Shop Signs + Spawners + Locations + Castle)

### Task Summary
Switched Britain pathing R&D from hand-picked coordinates to repository-derived target sets so runs validate real POIs.

Updated files:
- `scripts/britain_pathing_targets_generated.py` (new)
- `scripts/britain_pathing_rd_config.py`
- `scripts/britain_pathing_rd_controller.py`

Data source used:
- `ConficturaRepositoryDocs/ConficturaRepository.xml`
  - `Data/Decoration/Sosaria/decorate.cfg`
  - `Data/Spawns/towns.map`
  - location index entries (`Britain`, `Britain Castle`)
  - Britain region rectangles from region definitions

Generated target summary (current):
- `shop_sign_count=25`
- `npc_spawner_count=121` (source dataset includes Britain city plus one Britain dungeons entry)
- `location_count=56`
- `location_index_count=2` (`Britain`, `Britain Castle`)
- `castle_focus_count=63`
- `total_unique_coordinates=204`

Stage model now:
1. `stage_1_local_sanity` (3 baseline checks)
2. `stage_2_shop_signs` (generated)
3. `stage_3_npc_spawners` (generated)
4. `stage_4_locations_and_castle` (generated + location index)
5. `stage_5_castle_focus` (optional; default disabled to avoid duplicate runtime)
6. `stage_6_negative_unreachable` (bounded fail-stop checks)

Default policy note:
- `test_harness.generated_targets.include_dungeon_spawners` defaults to `False` so stage 3 stays city/castle-focused.
- Set it to `True` if you want the Britain-dungeons guard spawn included.

### Testing Instructions
1. Run `scripts/britain_pathing_rd_loader.py`.
2. Verify bootstrap shows generated coverage telemetry before routes start.
3. Let stages 2-4 complete for full Britain POI pass.
4. If runtime is too long, tune only limits in `scripts/britain_pathing_rd_config.py` under:
   - `test_harness.generated_targets.shop_sign_limit`
   - `test_harness.generated_targets.npc_spawner_limit`
   - `test_harness.generated_targets.location_limit`
   - `test_harness.generated_targets.location_index_limit`
5. Optional castle stress pass:
   - set `test_harness.generated_targets.include_castle_focus_stage = True`
   - optionally set `castle_focus_limit`.

### Expected Telemetry
- Bootstrap:
  - `[FSM][BOOTSTRAP][INFO] Generated target summary | shop_sign_count=..., npc_spawner_count=..., location_count=..., ...`
  - `[FSM][BOOTSTRAP][INFO] Bootstrap ready | route_count=..., stage_count=...`
- Per route (unchanged contract):
  - `[FSM][RUN_ROUTE][INFO] Action preconditions | route_name=..., category=shop_sign|npc_spawner|location, source=generated_...`
- Final summary:
  - route/stage pass-fail rollup with deterministic stop reasons on failures.

### Known Fragilities
- `ConficturaRepository.xml` is a packed snapshot; if shard content changes and docs lag, generated target coverage can become stale.
- Some generated POIs may be technically reachable only via specific approach vectors; expect occasional bounded failures in dense NPC traffic.
- Full generated coverage is intentionally large; use limits for faster tuning loops before full-batch validation.

## Iteration Addendum (2026-03-08): Client Pathfind Synergy + Oscillation Guardrails

### Task Summary
Integrated a client-pathfinding-first execution model to stop request thrash and building-loop oscillations seen in the latest live logs.

Updated files:
- `scripts/confictura_bot/pathing.py`
- `scripts/britain_pathing_rd_config.py`

What changed:
- Pathing now issues **one movement request per attempt** instead of rapid multi-candidate request bursts.
- Added ClassicUO pathfinding synchronization:
  - optional `Pathfind(-1)` cancel of active auto-walk before a new request
  - bounded wait for `Pathfinding()` to settle (`pathfinding_wait_ms`, `pathfinding_poll_ms`)
- Added shard-safe client range policy:
  - `client_pathfind_max_distance` (default `18`)
  - destination candidate is suppressed when out of client range (prevents repeated `Maximum distance exceeded` probes)
  - destination candidate is prioritized when within range
- Added anti-oscillation memory:
  - `candidate_repeat_window`
  - `candidate_repeat_limit`
  - skips recently repeated candidate points unless forced fallback is required
- Added deterministic near-target fail-stop:
  - `near_target_distance`
  - `near_target_stall_tolerance`
  - terminal reason: `near_target_oscillation`
- Added config defaults for the above in `pathing_defaults` and accepted `near_target_oscillation` for negative-route expected failure reasons.

### Testing Instructions
1. Run `scripts/britain_pathing_rd_loader.py` from Britain city area (same-map).
2. Verify preconditions now print:
   - `client_pathfind_max_distance=18`
   - `pathfinding_wait_ms=900`
   - `pathfinding_poll_ms=100`
   - `candidate_repeat_window=12`
   - `candidate_repeat_limit=2`
   - `near_target_distance=6`
   - `near_target_stall_tolerance=2`
3. Re-run the known problem routes from the latest log snippet (especially `npc_spawner_019_gypsylady` and `npc_spawner_024_adventurereast`).
4. Confirm per-attempt behavior:
   - exactly one `Pathfind request` should be associated with each `Pathing attempt` cycle
   - no repeated out-of-range destination probes while remaining distance is > 18
5. If looping persists near destination (distance ~3-6), confirm deterministic stop reason is `near_target_oscillation` instead of long timeout churn.

### Expected Telemetry Delta
- `Pathing attempt` now includes client-synergy knobs (`client_pathfind_max_distance`, repeat settings).
- `candidate_results` may include:
  - `skipped=recent_repeat`
  - `selection=forced_repeat_override`
  - `cancelled_active_pathfind=True`
- `Pathing progress` now includes:
  - `repeat_count`
  - `forced_selection`
- Failure mode near close-range ping-pong should emit:
  - `Pathing near-target oscillation detected`
  - `stop_reason=near_target_oscillation`

### Known Fragilities
- If `Pathfinding()` reports inconsistently in a specific ClassicUO build, the wait loop falls back to bounded polling and may still require higher `pathfinding_wait_ms`.
- On very high latency, cancel-before-request can occasionally interrupt useful momentum; set `cancel_active_pathfind=False` if that pattern appears.
- Repeat filtering is intentionally conservative; in extremely tight geometry, increasing `candidate_repeat_limit` to `3` may improve recovery.

## Iteration Addendum (2026-03-08): Pathfinding() Optional-API Guard Fix

### Task Summary
Live test exposed a fatal host-interop gap: this client profile does not publish `Pathfinding()` into macro scope, and the new sync logic referenced it directly.

Updated file:
- `scripts/confictura_bot/pathing.py`

Fix applied:
- Added host-safe resolver `_pathfinding_active_or_none(state_name)`.
- If `Pathfinding()` is unavailable:
  - logs one warning (`Pathfinding() command unavailable; using settle-only fallback`)
  - disables cancel/wait sync behavior gracefully
  - continues with settle-based pacing instead of hard-failing.
- `_cancel_active_pathfind(...)` and `_wait_for_pathfinding_idle(...)` now use optional feature-detection instead of direct symbol reference.

### Testing Instructions
1. Re-run `scripts/britain_pathing_rd_loader.py` from current location.
2. Confirm no fatal exception at first route tick.
3. Expect a single warning (once) about missing `Pathfinding()` and continued route execution.
4. Capture first 3 `Pathing attempt` blocks to confirm the harness continues after warning.

### Expected Telemetry
- One-time warning:
  - `[FSM][RUN_ROUTE][WARN] Pathfinding() command unavailable; using settle-only fallback`
- No `Unhandled exception in tick` for `global name 'Pathfinding' is not defined`.

### Known Fragilities
- Without `Pathfinding()` availability, synchronization falls back to settle timing; if oscillation remains under load, increase `settle_ms/pathfinding_wait_ms` pacing together.

## Iteration Addendum (2026-03-08): Interior Oscillation Clamp (Best-Distance Regression Guard)

### Task Summary
Added a hard anti-oscillation control that tracks route quality against the **best distance reached so far**. This prevents endless inside-structure ping-pong from being treated as healthy progress.

Updated files:
- `scripts/confictura_bot/pathing.py`
- `scripts/britain_pathing_rd_config.py`

What changed:
- Added pathing options:
  - `max_regression_from_best` (default clamp in module, configured to `2` in RnD config)
  - `no_best_progress_tolerance` (default `12`)
- Progress qualification now requires both:
  - `attempt_progress >= min_progress`
  - `after_distance <= (best_distance + max_regression_from_best)`
- Added deterministic fail-stop:
  - `stop_reason=no_best_progress_exceeded`
  - triggers when attempts since last **new best** exceed tolerance.
- Telemetry now includes best-distance context:
  - per-attempt debug includes `best_distance`, `attempts_since_best`
  - candidate result rows include `best_distance_before`, `regression_from_best`, `new_best`
  - progress/stall/final logs include `attempts_since_best` fields.

### Testing Instructions
1. Run `scripts/britain_pathing_rd_loader.py` from Britain center (same setup as latest failed run).
2. Watch the problematic stage/routes where building loops were observed (shop sign routes near blacksmith area).
3. Verify preconditions include:
   - `max_regression_from_best=2`
   - `no_best_progress_tolerance=12`
4. Confirm long ping-pong loops now terminate with deterministic reason:
   - `stop_reason=no_best_progress_exceeded`
5. Share one failing route block containing:
   - first 3 `Pathing attempt` lines,
   - first `Pathing stall detected`,
   - terminal `Pathing finished without success` + `Route test failed`.

### Expected Telemetry
- Candidate rows now show:
  - `best_distance_before=...`
  - `regression_from_best=...`
  - optional `progress_disqualified=regression_guard`
- Terminal warning path for this condition:
  - `Pathing no-best-progress tolerance exceeded`
  - `stop_reason=no_best_progress_exceeded`

### Known Fragilities
- If a valid route truly requires long detours away from current best point, this guard may stop earlier than before. Tune by raising:
  - `max_regression_from_best` (e.g. `3-4`)
  - `no_best_progress_tolerance` (e.g. `16-20`)

## Iteration Addendum (2026-03-08): Shop-Visit Goals + Adaptive Hop Settle + Stall Awareness

### Task Summary
Implemented a concrete "visit each shop" goal path and added hop-level movement/awareness controls to reduce interior ping-pong and false stalls.

Updated files:
- `scripts/confictura_bot/pathing.py`
- `scripts/britain_pathing_rd_config.py`
- `scripts/britain_pathing_rd_controller.py`

What changed:
- Shop routes now carry goal metadata derived from generated Britain targets:
  - `goal_type=shop_visit`
  - `shop_goal_vendor_tokens` and `shop_goal_vendor_anchor_points`
- RUN_ROUTE now executes a shop-goal phase for routes with `shop_goal_enabled=True`:
  - scans nearby mobiles for vendor-token matches
  - if needed, tries anchor points near the shop sign
  - attempts vendor approach (within goal distance)
  - route pass/fail now incorporates goal outcome (`shop_goal_failed_*`)
- Added adaptive hop settle wait in shared pathing:
  - wait budget scales with hop size (`hop_wait_per_tile_ms`, min/max clamp)
  - polls until candidate reached or movement settles
  - avoids evaluating progress too early while client is still auto-walking
- Added lightweight stall-time awareness scan in shared pathing:
  - captures nearby mobile count + sample names in attempt telemetry when stalled
- Relaxed regression/best-progress defaults for city geometry:
  - `max_regression_from_best=4`
  - `no_best_progress_tolerance=20`

### Testing Instructions
1. Run `scripts/britain_pathing_rd_loader.py` from Britain city center.
2. Let stage 2 (`shop_signs`) run at least 8-10 routes.
3. Verify per-route preconditions include new hop/awareness knobs:
   - `hop_wait_per_tile_ms`, `hop_wait_min_ms`, `hop_wait_max_ms`
   - `hop_wait_poll_ms`, `hop_wait_stable_polls`, `hop_wait_candidate_within`
   - `hop_awareness_enabled`, `hop_awareness_range`, `hop_awareness_max_entities`
4. Verify shop-goal telemetry appears for shop routes:
   - `Shop goal preconditions`
   - optional `Shop goal anchor move`
   - `Shop goal vendor approach`
5. Confirm route outcome payload now includes goal fields:
   - `goal_enabled`, `goal_passed`, `goal_reason`, `goal_vendor`, `goal_vendor_serial`, `goal_anchors_attempted`
6. If a route reaches sign but not vendor, expect deterministic goal failure reason:
   - `pass_reason=shop_goal_failed_*`

### Expected Telemetry
- Pathing progress rows now include hop settle evidence:
  - `hop_wait_reason`, `hop_wait_elapsed_ms`
- Candidate result rows now include:
  - `hop_wait_budget_ms`, `hop_wait_elapsed_ms`, `hop_wait_reason`, `hop_wait_candidate_distance`, `hop_wait_moved_polls`
- Route test logs now include goal context fields (type/enabled/passed/reason/vendor).

### Known Fragilities
- Vendor detection uses mobile-name token matching from nearby spawner-derived names; if a shop has nonstandard vendor naming, add/adjust token derivation rules.
- Anchor moves are bounded; if shop interior requires multi-door traversal or atypical elevation transitions, goal may fail even when area route is otherwise reachable.
- Adaptive settle waiting improves evaluation quality but increases per-attempt latency; tune `hop_wait_*` if total run time becomes excessive.

## Iteration Addendum (2026-03-08): Shop Interior Loop Fix (Visit-All Anchors + Mandatory Egress)

### Task Summary
Refined the shop-goal execution so the character does not linger inside interiors after entering.

Updated files:
- `scripts/britain_pathing_rd_controller.py`
- `scripts/britain_pathing_rd_config.py`
- `scripts/confictura_bot/pathing.py`

What changed:
- Replaced shop goal mobile acquisition from `GetEnemy/GetFriend` selectors with passive `Assistant.Engine.Mobiles` snapshot scanning.
  - This removes repeated enemy-target selector churn during shop-goal scans.
- Shop-goal behavior now executes as a deterministic sequence:
  1. collect vendor evidence,
  2. walk to each vendor anchor point (`shop_goal_vendor_anchor_points`),
  3. verify token/anchor requirements,
  4. walk back to configured shop exit point (`shop_goal_exit_point`, default route destination).
- Added strict goal policy flags per shop route:
  - `shop_goal_require_all_vendor_tokens`
  - `shop_goal_require_all_anchors`
  - `shop_goal_exit_required`
  - `shop_goal_exit_within_distance`, `shop_goal_exit_max_attempts`, `shop_goal_exit_max_ms`
- Tightened generated anchor discovery:
  - reduced default spawner radius from 14 -> 10
  - added `max_spawner_z_delta` filter to avoid mixed-floor anchors
  - increased token/anchor caps to support full in-shop traversal (up to 10)
- Preserved route metadata in fixed-route normalization:
  - `goal_type`, `target_name`, `target_area`, `target_class` now survive controller normalization.
- Repaired `pathing.py` awareness call corruption and ensured awareness fallback guard is defined.

### Testing Instructions
1. Start in Britain and run `scripts/britain_pathing_rd_loader.py`.
2. Focus on stage 2 shop routes, especially:
   - `shop_sign_012_the_hammer_and_anvil`
3. Verify route log shows preserved goal metadata:
   - `goal_type=shop_visit`
   - `goal_enabled=True`
4. For successful shop goals, verify sequence telemetry:
   - `Shop goal preconditions`
   - one or more `Shop goal anchor move`
   - `Shop goal egress move`
   - route result with `goal_reason=vendor_and_egress_complete`
5. Confirm the character exits the shop area after vendor-anchor passes and proceeds to next shop route.
6. Confirm enemy selector spam from shop-goal scanning is absent/reduced (no repeated goal-side `Target: ... [Enemy]` churn).

### Expected Telemetry
- Goal-enabled shop routes should report:
  - `goal_type=shop_visit`
  - `goal_anchors_attempted>0` for anchor-enabled shops
- On failure, deterministic reasons should now identify exact goal phase:
  - `vendor_not_observed`
  - `vendor_tokens_missing_*`
  - `anchor_reach_failed_*`
  - `egress_failed_*`

### Known Fragilities
- Anchor quality depends on nearby spawner-derived coordinates; unusual interiors may still need manual radius/z tuning.
- Strict all-anchor/all-token policy can fail shops with temporarily blocked interiors or dynamic NPC displacement.
- If a shop sign destination is not a valid exterior egress tile, set a custom `shop_goal_exit_point` for that route.
