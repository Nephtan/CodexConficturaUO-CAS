# ClassicAssist Script Metadata Checklist

Use this checklist before saving any new `.py` macro file.

- First four lines are exactly:
  - `# Name: [Highly Descriptive Name of State Machine]`
  - `# Description: [Brief explanation of the core execution loop]`
  - `# Author: ChatGPT Codex`
  - `# Shard: Confictura`
- Python syntax is compatible with Python 2.7 (IronPython).
- No `time.sleep()` calls; only `Pause(milliseconds)`.
- Every `WaitForTarget` call includes an explicit timeout.
- State transitions and failures log telemetry with `[FSM][STATE][LEVEL]` format.
- Blocking actions are preceded by guard checks.
