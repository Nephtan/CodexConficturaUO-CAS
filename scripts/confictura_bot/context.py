# Name: Confictura FSM Runtime Context
# Description: Stores shared configuration, counters, alias cache, and runtime error details.
# Author: ChatGPT Codex
# Shard: Confictura

import time

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


class BotContext(object):

    def __init__(self, config):
        self.config = config
        self.running = True
        self.current_state = None
        self.previous_state = None
        self.state_enter_time = None

        self.retry_counts = {}
        self.watchdogs = {}
        self.alias_cache = {}

        self.tick_count = 0
        self.transition_count = 0

        self.last_error = None
        self.last_error_state = None
        self.last_failed_state = None

    def set_state(self, state_name):
        self.previous_state = self.current_state
        self.current_state = state_name
        self.state_enter_time = time.time()
        self.transition_count += 1

    def state_age_ms(self):
        if self.state_enter_time is None:
            return 0
        return int((time.time() - self.state_enter_time) * 1000)

    def mark_watchdog(self, key):
        self.watchdogs[key] = time.time()

    def watchdog_elapsed_ms(self, key):
        started = self.watchdogs.get(key)
        if started is None:
            return -1
        return int((time.time() - started) * 1000)

    def increment_retry(self, state_name):
        self.retry_counts[state_name] = self.retry_counts.get(state_name, 0) + 1
        return self.retry_counts[state_name]

    def reset_retry(self, state_name):
        self.retry_counts[state_name] = 0

    def reset_all_retries(self):
        for key in self.retry_counts.keys():
            self.retry_counts[key] = 0

    def set_alias(self, alias_name, value):
        self.alias_cache[alias_name] = value
        SetAlias(alias_name, value)

    def get_alias(self, alias_name):
        if alias_name in self.alias_cache:
            return self.alias_cache[alias_name]
        value = GetAlias(alias_name)
        self.alias_cache[alias_name] = value
        return value

    def fail(self, state_name, reason, details=None):
        self.last_error_state = state_name
        self.last_failed_state = state_name
        self.last_error = reason
        Telemetry.error(state_name, reason, details)

    def stop(self, reason):
        Telemetry.fatal(self.current_state, "Bot stopping", {"reason": reason})
        self.running = False

