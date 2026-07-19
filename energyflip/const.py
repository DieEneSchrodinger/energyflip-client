"""EnergyFlip constants"""

API_HOST = "api.aurumeurope.com"

OAUTH_CLIENT_ID = "b58efc0b"
OAUTH_SCOPE = "role:enduser realm:aurum"
OAUTH_ACCESS_TOKEN = "access_token"

AUTHENTICATION_PATH = "/oauth2/v1/token"
"""Path to perform authentication. Result is a user id and an auth token"""

"""Some of these values are left here for possible later implementation when the end points are found"""
SOURCE_TYPE_ELECTRICITY = "electricity"
SOURCE_TYPE_ELECTRICITY_IN = "electricityIn"
SOURCE_TYPE_ELECTRICITY_IN_LOW = "electricityInLow"
SOURCE_TYPE_ELECTRICITY_IN_HIGH = "electricityInHigh"
SOURCE_TYPE_ELECTRICITY_OUT = "electricityOut"
SOURCE_TYPE_ELECTRICITY_OUT_LOW = "electricityOutLow"
SOURCE_TYPE_ELECTRICITY_OUT_HIGH = "electricityOutHigh"
SOURCE_TYPE_ELECTRICITY_NET_OUT = "electricityNetOut"
SOURCE_TYPE_ELECTRICITY_NET_IN = "electricityNetIn"
SOURCE_TYPE_ELECTRICITY_HOUSE_IN = "electricityHouseIn"
SOURCE_TYPE_SOLAR_IN_HOUSE = "solarInHouse"
SOURCE_TYPE_ELECTRICITY_EXPECTED = "electricityExpected"
SOURCE_TYPE_ELECTRICITY_GOAL = "electricityGoal"
SOURCE_TYPE_GAS = "gas"
SOURCE_TYPE_GAS_EXPECTED = "gasExpected"
SOURCE_TYPE_GAS_GOAL = "gasGoal"

DEFAULT_ELECTRICITY_SOURCES = [
    SOURCE_TYPE_ELECTRICITY,
    SOURCE_TYPE_ELECTRICITY_IN,
    SOURCE_TYPE_ELECTRICITY_IN_LOW,
    SOURCE_TYPE_ELECTRICITY_IN_HIGH,
    SOURCE_TYPE_ELECTRICITY_OUT,
    SOURCE_TYPE_ELECTRICITY_OUT_LOW,
    SOURCE_TYPE_ELECTRICITY_OUT_HIGH,
    SOURCE_TYPE_ELECTRICITY_NET_OUT,
    SOURCE_TYPE_ELECTRICITY_NET_IN,
    SOURCE_TYPE_ELECTRICITY_HOUSE_IN,
    SOURCE_TYPE_SOLAR_IN_HOUSE
]
"""Default energy sources to fetch and store"""

DEFAULT_SOURCE_TYPES = [SOURCE_TYPE_ELECTRICITY,
                        SOURCE_TYPE_ELECTRICITY_IN,
                        SOURCE_TYPE_ELECTRICITY_IN_LOW,
                        SOURCE_TYPE_ELECTRICITY_OUT,
                        SOURCE_TYPE_ELECTRICITY_OUT_LOW,
                        SOURCE_TYPE_ELECTRICITY_EXPECTED,
                        SOURCE_TYPE_ELECTRICITY_GOAL,
                        SOURCE_TYPE_GAS,
                        SOURCE_TYPE_GAS_EXPECTED,
                        SOURCE_TYPE_GAS_GOAL]
"""Default source types to fetch if none are specified. Kept for compatibility"""

CUSTOMER_OVERVIEW_PATH = "/user/v3/customers/overview"
"""Path to request details of the customer."""

ACTUALS_SUMMARY_PATH = "/user/v4/customers/%s/measurements/actualsSummary"
"""Path to request current values. Should be formatted with user id."""

CUMULATIVE_HISTORY_PATH = "/user/v4/customers/%s/measurements/cumulativeHistory"
"""Path to request cumulative values of type over time. Should be formatted with user id."""

AUTH_TOKEN_HEADER = "Authorization"
"""Header which should contain (in request) the authentication token"""
