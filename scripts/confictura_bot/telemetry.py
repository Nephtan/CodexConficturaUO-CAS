# Name: Confictura FSM Telemetry Utilities
# Description: Provides standardized console logging helpers for state machines.
# Author: ChatGPT Codex
# Shard: Confictura

class Telemetry(object):

    LEVEL_DEBUG = "DEBUG"
    LEVEL_INFO = "INFO"
    LEVEL_WARN = "WARN"
    LEVEL_ERROR = "ERROR"
    LEVEL_FATAL = "FATAL"

    @staticmethod
    def _format_kv(data):
        if data is None:
            return ""
        if not isinstance(data, dict):
            return ""
        pairs = []
        for key in sorted(data.keys()):
            pairs.append("{0}={1}".format(key, data[key]))
        return " | " + ", ".join(pairs) if pairs else ""

    @staticmethod
    def log(state, level, message, data=None):
        state_name = state if state else "UNSET"
        line = "[FSM][{0}][{1}] {2}{3}".format(
            state_name,
            level,
            message,
            Telemetry._format_kv(data)
        )
        print(line)

    @staticmethod
    def debug(state, message, data=None):
        Telemetry.log(state, Telemetry.LEVEL_DEBUG, message, data)

    @staticmethod
    def info(state, message, data=None):
        Telemetry.log(state, Telemetry.LEVEL_INFO, message, data)

    @staticmethod
    def warn(state, message, data=None):
        Telemetry.log(state, Telemetry.LEVEL_WARN, message, data)

    @staticmethod
    def error(state, message, data=None):
        Telemetry.log(state, Telemetry.LEVEL_ERROR, message, data)

    @staticmethod
    def fatal(state, message, data=None):
        Telemetry.log(state, Telemetry.LEVEL_FATAL, message, data)
