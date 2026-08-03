from collections.abc import Awaitable, Callable
from typing import Any, Literal, TypeAlias, TypedDict, overload

import aiohttp
from yarl import URL

from .const import (
    API_HOST,
    DEFAULT_SOURCE_TYPES,
)

SourceType:TypeAlias = Literal["electricity", "gas", "solar"]
Timespan: TypeAlias = Literal["day", "week", "month", "year"]

class CurrentUsageInfo(TypedDict):
    """The current usage information for a source type, which is returned by the current_measurements() method."""
    rate: float
    time: str
    "Formatted as a string in ISO 8601 format, e.g. 2023-12-31T23:59:59.999+02:00"
    costPerHour: float

class EnergyFlip:
    """Client to connect with EnergyFlip"""

    _customer_id: str | None
    _auth_token: str | None
    _sources: dict[str, str]
    api_scheme: str
    api_host: str
    api_port: int
    request_timeout: int
    source_types: list[SourceType]

    def __init__(
        self,
        username: str,
        password: str,
        api_scheme: str = "https",
        api_host: str = API_HOST,
        api_port: int = 443,
        request_timeout: int = 10,
        source_types=DEFAULT_SOURCE_TYPES,
    ): ...

    async def authenticate(self) -> None:
        """Log in using username and password.

        If succesful, the authentication is saved and is_authenticated() returns true
        """

    async def customer_overview(self) -> None:
        """Request the customer overview.
        
        The resulting customer id and source ids are stored in the instance and can be retrieved using get_user_id() and get_source_ids() respectively.
        Must be authenticated before calling this method."""

        
    async def get_actuals_summary(self) -> dict[str, Any]:
        """Get the summary of the actuals for the current day, week, month and year.
        
        This gives for the current day, week, month and year the total usage and cost for each source type, 
        as well as the current usage rate and cost per hour for each source type.

        If there is no usage for a source type, the usage and cost will be 0, and the current usage rate and cost per hour will be None.
        """

    async def get_cumulative(self, type: SourceType, time: Timespan) -> dict[str, dict[str, int|float]]:
        """Gets the cumulative history of `type` over time period time.
        
        :param type: Type to request (electricity, gas, solar).
        :param time: Time period to request data for (day, week, month, year)."""


    async def current_measurements(self):
        """Wrapper method which returns the relevant actual values of sources.

        When required, this method attempts to authenticate."""

    @overload
    async def request[F](
        self,
        method: str,
        url: URL,
        data: dict|None = None,
        callback: Callable[[aiohttp.ClientResponse], Awaitable[None]]|None = None,
    ) -> None: ...
    @overload
    async def request[F](
        self,
        method: str,
        url: URL,
        data: dict |None = None,
        callback: Callable[[aiohttp.ClientResponse], Awaitable[F]] |None = None,
    ) -> F: ...

    def is_authenticated(self) -> bool:
        """Returns whether this instance is authenticated

        Note: despite this method returning true, requests could still fail to an authentication error."""

    def get_user_id(self) -> str | None:
        """Returns the unique id of the currently authenticated user.
        Guaranteed to be str if is_authenticated() returns true, otherwise None."""

    def invalidate_authentication(self) -> None:
        """Invalidate the current authentication tokens and account details."""

    def get_source_ids(self) -> list[str]:
        """Gets the ids of the sources which belong to self.source_types, if present."""

    def get_source_id(self, source_type) -> str|None:
        """Gets the id of the source which belongs to the given source type, if present."""