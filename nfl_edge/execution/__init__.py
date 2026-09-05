"""Execution semantics: ticks, fees, and the strict separation of touch from fill."""
from nfl_edge.execution.fees import FeeSchedule, load_fee_schedule  # noqa: F401
from nfl_edge.execution.ticks import is_valid_price, round_to_tick, tick_down, tick_up  # noqa: F401
