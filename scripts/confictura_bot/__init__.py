# Name: Confictura Bot Framework Package Init
# Description: Initializes shared FSM framework modules for Confictura automation scripts.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api

FRAMEWORK_VERSION = "1.0.1"


def _bootstrap_ca_api():
    try:
        import __builtin__
    except Exception:
        __builtin__ = None

    if __builtin__ is None:
        return

    try:
        namespace = __builtin__.__dict__
    except Exception:
        return

    bind_ca_api(namespace)


_bootstrap_ca_api()
