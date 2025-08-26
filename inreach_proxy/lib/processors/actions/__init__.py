from inreach_proxy.lib.processors.actions.forecast import SpotForecastAction
from inreach_proxy.lib.processors.actions.grib import GribFetchAction
from inreach_proxy.lib.processors.actions.ping import PingPongAction

VALID_ACTIONS = {
    0: PingPongAction,
    1: GribFetchAction,
    2: SpotForecastAction,
}
ACTION_TO_DB_ID = {v: k for k, v in VALID_ACTIONS.items()}
