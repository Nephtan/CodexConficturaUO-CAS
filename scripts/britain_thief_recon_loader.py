# Name: Confictura Britain Thief Recon Loader
# Description: Loads and executes britain_thief_recon_controller from repo path.
# Author: ChatGPT Codex
# Shard: Confictura

import sys

SCRIPT_ROOT = r"D:\CodexConficturaUO-CAS\CodexConficturaUO-CAS\scripts"
SCRIPT_FILE = r"D:\CodexConficturaUO-CAS\CodexConficturaUO-CAS\scripts\britain_thief_recon_controller.py"

purge_keys = []
for module_name in list(sys.modules.keys()):
    try:
        if module_name == "britain_thief_recon_config":
            purge_keys.append(module_name)
            continue
        if module_name.startswith("britain_thief_recon_controller"):
            purge_keys.append(module_name)
            continue
        if module_name.startswith("confictura_bot"):
            purge_keys.append(module_name)
            continue
    except Exception:
        continue

for module_name in purge_keys:
    try:
        del sys.modules[module_name]
    except Exception:
        pass

if SCRIPT_ROOT not in sys.path:
    sys.path.append(SCRIPT_ROOT)

execfile(SCRIPT_FILE)
