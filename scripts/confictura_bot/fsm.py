# Name: Confictura FSM Core Runtime
# Description: Defines state contract and deterministic state-machine execution loop.
# Author: ChatGPT Codex
# Shard: Confictura

from confictura_bot.ca_shim import bind_ca_api
from confictura_bot.telemetry import Telemetry

bind_ca_api(globals())


def _pause_or_fail(ctx, state_name, milliseconds):
    try:
        Pause(int(milliseconds))
        return True
    except Exception as ex:
        if ctx is not None:
            ctx.fail(state_name, "Pause command unavailable", {
                "milliseconds": milliseconds,
                "exception": str(ex)
            })
            ctx.running = False
        else:
            Telemetry.fatal(state_name, "Pause command unavailable", {
                "milliseconds": milliseconds,
                "exception": str(ex)
            })
        return False


class State(object):

    key = "UNSET"

    def enter(self, ctx):
        return None

    def tick(self, ctx):
        raise NotImplementedError("State.tick must be implemented")

    def exit(self, ctx):
        return None


class StateMachine(object):

    def __init__(self, ctx, states, initial_state):
        self.ctx = ctx
        self.states = states
        self.initial_state = initial_state

    def _change_state(self, next_state, reason):
        current_key = self.ctx.current_state

        if current_key is not None:
            current_state = self.states[current_key]
            current_state.exit(self.ctx)

        self.ctx.set_state(next_state)
        Telemetry.info(next_state, "State transition", {
            "from_state": current_key,
            "reason": reason,
            "transition_count": self.ctx.transition_count
        })
        self.states[next_state].enter(self.ctx)

    def run(self):
        runtime_cfg = self.ctx.config.get("runtime", {})
        tick_pause_ms = runtime_cfg.get("tick_pause_ms", 250)
        max_ticks = runtime_cfg.get("max_runtime_ticks", 5000)

        if self.initial_state not in self.states:
            Telemetry.fatal("FSM", "Initial state missing", {"state": self.initial_state})
            return

        self._change_state(self.initial_state, "initialization")

        while self.ctx.running and self.ctx.tick_count < max_ticks:
            self.ctx.tick_count += 1
            state_key = self.ctx.current_state

            if state_key not in self.states:
                Telemetry.fatal("FSM", "Unknown current state", {"state": state_key})
                self.ctx.running = False
                break

            state = self.states[state_key]

            try:
                next_state = state.tick(self.ctx)
            except Exception as ex:
                self.ctx.fail(state_key, "Unhandled exception in tick", {
                    "exception": str(ex),
                    "tick": self.ctx.tick_count
                })
                self.ctx.last_failed_state = state_key
                next_state = "FATAL_STOP"

            if next_state is None:
                if not _pause_or_fail(self.ctx, state_key, tick_pause_ms):
                    break
                continue

            if next_state not in self.states:
                self.ctx.fail(state_key, "Returned unknown next state", {
                    "next_state": next_state
                })
                next_state = "FATAL_STOP"

            if next_state != state_key:
                self._change_state(next_state, "tick return")

            if not _pause_or_fail(self.ctx, self.ctx.current_state, tick_pause_ms):
                break

        if self.ctx.tick_count >= max_ticks:
            Telemetry.fatal(self.ctx.current_state, "Max tick count reached", {
                "max_ticks": max_ticks
            })
