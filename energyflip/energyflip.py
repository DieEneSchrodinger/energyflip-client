import asyncio
import aiohttp
from yarl import URL
from collections.abc import Awaitable, Callable
from typing import Any, TypeVar, overload
import datetime as dt
import calendar
import time

from .const import (
    API_HOST,
    AUTHENTICATION_PATH,
    DEFAULT_SOURCE_TYPES,
    ACTUALS_SUMMARY_PATH,
    OAUTH_ACCESS_TOKEN,
    OAUTH_SCOPE,
    OAUTH_CLIENT_ID,
    CUSTOMER_OVERVIEW_PATH,
    CUMULATIVE_HISTORY_PATH,
    AUTH_TOKEN_HEADER,
    DEFAULT_ELECTRICITY_SOURCES
)
from .exceptions import (
    EnergyFlipConnectionException,
    EnergyFlipException,
    EnergyFlipUnauthenticatedException,
)

F = TypeVar('F')

class EnergyFlip:
    """Client to connect with EnergyFlip"""

    _customer_id: str | None
    _auth_token: str | None
    _sources: dict[str, str] = {}

    def __init__(
        self,
        username: str,
        password: str,
        api_scheme: str = "https",
        api_host: str = API_HOST,
        api_port: int = 443,
        request_timeout: int = 10,
        source_types=DEFAULT_SOURCE_TYPES,
    ):
        self.api_scheme = api_scheme
        self.api_host = api_host
        self.api_port = api_port
        self.request_timeout = request_timeout
        self.source_types = source_types

        self._username = username
        self._password = password
        self._customer_id = None
        self._auth_token = None
        self._sources = {}

    async def authenticate(self) -> None:
        """Log in using username and password.

        If succesfull, the authentication is saved and is_authenticated() returns true
        """
        # Make sure all data is cleared
        self.invalidate_authentication()

        url = URL.build(
            scheme=self.api_scheme,
            host=self.api_host,
            port=self.api_port,
            path=AUTHENTICATION_PATH
        )

        # Oauth2 request, password grant type
        data = {
            "grant_type": "password",
            "client_id": OAUTH_CLIENT_ID,
            "username": self._username,
            "password": self._password,
            "scope": OAUTH_SCOPE
        }

        return await self.request(
            "POST",
            url,
            data=data,
            callback=self._handle_authenticate_response,
        )

    async def _handle_authenticate_response(self, response: aiohttp.ClientResponse) -> None:
        json: dict = await response.json()
        self._auth_token = json[OAUTH_ACCESS_TOKEN]

    async def customer_overview(self) -> None:
        """Request the customer overview."""
        if not self.is_authenticated():
            raise EnergyFlipUnauthenticatedException("Authentication required")

        url = URL.build(
            scheme=self.api_scheme,
            host=self.api_host,
            port=self.api_port,
            path=CUSTOMER_OVERVIEW_PATH,
        )

        return await self.request(
            "GET", url, callback=self._handle_customer_overview_response
        )

    async def _handle_customer_overview_response(self, response: aiohttp.ClientResponse) -> None:
        json: dict = await response.json()
        self._customer_id = json["data"]["customerSummary"]["sessionIdentifiers"]["customerId"]
        
        # Keep sources for now, is currently unused
        self._sources = dict()
        for source in json["data"]["customerSummary"]["sources"]:
            self._sources[source["type"]] = source["source"]
        
    async def get_actuals_summary(self) -> dict:
        url = URL.build(
            scheme=self.api_scheme,
            host=self.api_host,
            port=self.api_port,
            path=(ACTUALS_SUMMARY_PATH % self._customer_id),
        )
        
        return await self.request("GET", url, callback=self._handle_get_actuals_summary)

    async def _handle_get_actuals_summary(self, response: aiohttp.ClientResponse) -> dict:
        json: dict = await response.json()
        return json["data"]["actualsSummary"]
    
    async def get_cumulative(self, type: str, time: str) -> dict:
        """Gets the cumulative history of type over time period time.
        
        :param type: Type to request (electricity, gas, solar).
        :param time: Time period to request data for (day, week, month, year)."""
        start : dt.datetime = dt.datetime.combine(dt.date.today(), dt.time.min).astimezone()
        end : dt.datetime = dt.datetime.combine(dt.date.today(), dt.time.max).astimezone()
        
        if time == "week":
            start = start - dt.timedelta(days=start.weekday())
            end = end + dt.timedelta(days=6 - end.weekday())
        elif time == "month":
            start.replace(day=1)
            end.replace(day=calendar.monthrange(end.year, end.month)[1])
        elif time == "year":
            start.replace(month=1, day=1)
            end.replace(month=12, day=31)
        
        query = {
            "timeResolution" : time + "1",
            "views" : type,
            "startTime" : start.isoformat(timespec="seconds"),
            "endTime" : end.isoformat(timespec="seconds")
        }
        url = URL.build(
            scheme=self.api_scheme,
            host=self.api_host,
            port=self.api_port,
            path=(CUMULATIVE_HISTORY_PATH % self._customer_id),
            query=query
        )

        return await self.request("GET", url, callback=self._handle_get_cumulative)

    async def _handle_get_cumulative(self, response: aiohttp.ClientResponse) -> dict:
        json: dict = await response.json()
        return json["data"]["cumulativeHistory"]["aggregations"]

    async def current_measurements(self) -> dict[dict, Any]:
        """Wrapper method which returns the relevant actual values of sources.

        When required, this method attempts to authenticate."""
        try:
            if not self.is_authenticated():
                await self.authenticate()
                await self.customer_overview()

            measurements = dict()
            
            # Since all values over time are now stored in the same endpoint, we iterate over all the queries that are required to extract them
            for type in ["gas", "electricity"]:
                measurements[type] = dict()
                for period in ["day", "week", "month", "year"]:
                    cumulative: dict = await self.get_cumulative(type, period)
                    
                    if type == "electricity":
                        for measurement in DEFAULT_ELECTRICITY_SOURCES:
                            storedMeasurement = measurement + "Sum"
                            # NOTE: keep compatability with previous versions - only change what we extracted from API
                            if storedMeasurement in cumulative:
                                if measurement not in measurements:
                                    measurements[measurement] = dict()
                                measurements[measurement]["this" + period.capitalize()] = cumulative[storedMeasurement]
                    elif type == "gas":
                        # If the gas is not supported or there is no usage, set value to 0
                        if "gasSum" in cumulative:
                            measurements[type]["this" + period.capitalize()] = cumulative["gasSum"]
                        else:
                            measurements[type]["this" + period.capitalize()] = 0
            
            current: dict = await self.get_actuals_summary()
            
            
            for type in ["gas"] + DEFAULT_ELECTRICITY_SOURCES:
                if type in current and "gridUsage" in current[type]:
                    partMeasurement = measurements[type]["measurement"] if "measurement" in measurements[type] else {}
                    gridUsage = current[type]["gridUsage"]
                    
                    # Different fields to keep compatibility with previous versions and current HA implementation
                    partMeasurement["rate"] = gridUsage["value"]
                    partMeasurement["time"] = gridUsage["timestamp"]
                    partMeasurement["costPerHour"] = gridUsage["costPerHour"]
                    
                    measurements[type]["measurement"] = partMeasurement
                elif type in measurements:
                    measurements[type]["measurement"] = "None"
            return measurements
        
        except EnergyFlipUnauthenticatedException as exception:
            self.invalidate_authentication()
            raise exception

    @overload
    async def request(
        self,
        method: str,
        url: URL,
        data: dict|None = None,
        callback: Callable[[aiohttp.ClientResponse], Awaitable[None]]|None = None,
    ) -> None: ...
    @overload
    async def request(
        self,
        method: str,
        url: URL,
        data: dict |None = None,
        callback: Callable[[aiohttp.ClientResponse], Awaitable[F]] |None = None,
    ) -> F: ...

    
    async def request(
        self,
        method: str,
        url: URL,
        data: dict |None= None,
        callback: Callable[[aiohttp.ClientResponse], Awaitable[F]] |None = None,
    ) -> F | None:
        headers = {"Accept": "application/json"}

        # Insert authentication
        if self._auth_token is not None:
            headers[AUTH_TOKEN_HEADER] = "Bearer %s" % self._auth_token

        try:
            async with asyncio.timeout(self.request_timeout):
                async with aiohttp.ClientSession() as session:
                    req = session.request(
                        method, url, data=data, headers=headers, ssl=True
                    )
                    async with req as response:
                        status = response.status
                        is_json = "application/json" in response.headers.get(
                            "Content-Type", ""
                        )

                        if status == 401:
                            raise EnergyFlipUnauthenticatedException(
                                await response.text()
                            )

                        if not is_json:
                            raise EnergyFlipException(
                                "Response is not json", await response.text()
                            )

                        if not is_json or (status // 100) in [4, 5]:
                            raise EnergyFlipException(
                                "Response is not success",
                                response.status,
                                await response.text(),
                            )

                        if callback is not None:
                            return await callback(response)

        except asyncio.TimeoutError as exception:
            raise EnergyFlipConnectionException(
                "Timeout occurred while communicating with EnergyFlip"
            ) from exception
        except aiohttp.ClientError as exception:
            raise EnergyFlipConnectionException(
                "Error occurred while communicating with EnergyFlip"
            ) from exception

    def is_authenticated(self):
        """Returns whether this instance is authenticated

        Note: despite this method returning true, requests could still fail to an authentication error."""
        return self._auth_token is not None

    def get_user_id(self) -> str | None:
        """Returns the unique id of the currently authenticated user"""
        return self._customer_id

    def invalidate_authentication(self) -> None:
        """Invalidate the current authentication tokens and account details."""
        self._customer_id = None
        self._sources = {}
        self._auth_token = None

    def get_source_ids(self):
        """Gets the ids of the sources which belong to self.source_types, if present."""
        return [
            source_id
            for source_id in map(self.get_source_id, self.source_types)
            if source_id is not None
        ]

    def get_source_id(self, source_type):
        """Gets the id of the source which belongs to the given source type, if present."""
        return (
            self._sources[source_type]
            if self._sources is not None and source_type in self._sources
            else None
        )