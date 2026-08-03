import calendar
import datetime as dt
import json
import os
import typing
from collections.abc import Iterator
from pathlib import Path
from typing import Any, NotRequired, TypedDict, overload

import anyio
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase
from aiohttp.web_request import Request

from energyflip import EnergyFlip
from energyflip.const import SOURCE_TYPE_ELECTRICITY, SOURCE_TYPE_GAS


class EnergyFlipTestCase(AioHTTPTestCase):

    async def get_application(self):



        routes = web.RouteTableDef()

        @routes.post("/oauth2/v1/token")
        async def authenticate(request: Request):
            data = await request.post()
            assert data["username"] == "username"
            assert data["password"] == "password"
            assert data["grant_type"] == "password"
            assert data["client_id"] == "b58efc0b"
            assert data["scope"] == "role:enduser realm:aurum"
            with open("tests/responses/authentication.json") as file:
                return web.Response(
                    content_type="application/json",
                    text=file.read()
                )
        @routes.get("/user/v3/customers/overview")
        async def customer_overview(request: Request):
            assert request.headers["Authorization"] == "Bearer acc35500-abcd-abcd-abcd-1234567890ab"

    
            async with await anyio.open_file("tests/responses/customer_overview.json") as file:
                return web.Response(
                    content_type="application/json",
                    text=await file.read()
                )
            
        @routes.get("/user/v4/customers/{user}/measurements/actualsSummary")
        async def actuals(request: Request):
            assert request.match_info.get("user") == "12345678-abcd-abcd-abcd-1234567890ab"
            assert request.headers["Authorization"] == "Bearer acc35500-abcd-abcd-abcd-1234567890ab"
            async with await anyio.open_file("tests/responses/actualsSummary.json") as file:
                return web.Response(
                    content_type="application/json",
                    text=await file.read()
                )

        @routes.get("/user/v4/customers/{user}/measurements/cumulativeHistory")
        async def cumulativeHistory(request: Request):
            assert request.match_info.get("user") == "12345678-abcd-abcd-abcd-1234567890ab"
            assert "timeResolution" in request.query
            assert "views" in request.query
            assert "startTime" in request.query
            assert "endTime" in request.query
            assert request.headers["Authorization"] == "Bearer acc35500-abcd-abcd-abcd-1234567890ab"

            res = request.query["timeResolution"][:-1] # remove the last character, which is always "1"
            views = request.query["views"]
            #TODO: Combine the different views into one response, instead of returning the response for the first view
            for view in views.split(","):
                path = f"tests/responses/cumulativeHistory/{view}/{res}.json"
                if os.path.exists(path):
                  break
            else:
                return web.Response(status=404)
            async with await anyio.open_file(path) as file:
                return web.Response(
                    content_type="application/json",
                    text=await file.read()
                )
        app = web.Application()

        app.add_routes(routes)
        return app

    async def test_initial_state(self):
        energyflip = EnergyFlip(
            "username",
            "password",
            api_scheme="http",
            api_host="localhost",
            api_port=self.server.port # type: ignore
        )

        assert energyflip.is_authenticated() is False
        assert energyflip.get_user_id() is None
        assert energyflip.get_source_ids() == []
        assert energyflip.get_source_id(SOURCE_TYPE_ELECTRICITY) is None

    async def test_authenticate_success(self):
        energyflip = EnergyFlip(
            "username",
            "password",
            api_scheme="http",
            api_host="localhost",
            api_port=self.server.port # type: ignore
        )
        await energyflip.authenticate()

        assert energyflip.is_authenticated()
        assert energyflip._auth_token == "acc35500-abcd-abcd-abcd-1234567890ab"

    async def test_authenticate_resets_user_details(self):
        energyflip = EnergyFlip(
            "username",
            "password",
            api_scheme="http",
            api_host="localhost",
            api_port=self.server.port # type: ignore
        )
        await energyflip.authenticate()
        await energyflip.customer_overview()
        await energyflip.authenticate()

        # User details should be reset
        assert energyflip.get_user_id() is None
        assert energyflip.get_source_ids() == []

    async def test_customer_overview(self):
        energyflip = EnergyFlip(
            "username",
            "password",
            api_scheme="http",
            api_host="localhost",
            api_port=self.server.port # type: ignore
        )
        await energyflip.authenticate()
        await energyflip.customer_overview()

        assert energyflip.get_user_id() == "12345678-abcd-abcd-abcd-1234567890ab"
        assert energyflip.get_source_ids() == [
            "00000000-0000-0000-0000-000000000005",
            "00000000-0000-0000-0000-000000000001",
            "00000000-0000-0000-0000-000000000002",
            "00000000-0000-0000-0000-000000000003",
            "00000000-0000-0000-0000-000000000004",
            "00000000-0000-0000-0000-000000000006",
            "00000000-0000-0000-0000-000000000007",
            "00000000-0000-0000-0000-000000000008",
            "00000000-0000-0000-0000-000000000009",
            "00000000-0000-0000-0000-000000000010"
            # Source ids only contain ids of supported types,
            # so sources "00000000-0000-0000-0000-000000000011" and "00000000-0000-0000-0000-000000000012"
            # are not in this list
        ]
        assert energyflip.get_source_id(SOURCE_TYPE_ELECTRICITY) == "00000000-0000-0000-0000-000000000005"
        assert energyflip.get_source_id(SOURCE_TYPE_GAS) == "00000000-0000-0000-0000-000000000008"

    async def test_current_measurements(self):
        energyflip = EnergyFlip(
            "username",
            "password",
            api_scheme="http",
            api_host="localhost",
            api_port=self.server.port #type:ignore
        )
        current_measurements = await energyflip.current_measurements()

        assert len(current_measurements) == 11
        assert "electricity" in current_measurements
        assert "electricityIn" in current_measurements
        assert "electricityInLow" in current_measurements
        assert "electricityOut" in current_measurements
        assert "electricityOutLow" in current_measurements
        assert "electricityInHigh" in current_measurements
        assert "electricityOutHigh" in current_measurements
        # No longer in new API (can only be seen for year)
        # assert "electricityExpected" in current_measurements
        # assert "electricityGoal" in current_measurements
        # assert "gasExpected" in current_measurements
        # assert "gasGoal" in current_measurements
        assert "gas" in current_measurements


        assert "electricityNetIn" in current_measurements
        assert "electricityNetOut" in current_measurements
        assert "solarInHouse" in current_measurements

        electricity = current_measurements["electricity"]
        assert "measurement" in electricity
        assert "thisDay" in electricity
        assert "thisWeek" in electricity
        assert "thisMonth" in electricity
        assert "thisYear" in electricity
        assert electricity["measurement"] is not None
        assert electricity["measurement"]["rate"] == 204
        assert electricity["measurement"]["time"] == "2025-05-01T20:37:32.000+02:00"
        assert electricity["thisDay"]["value"] == -2.6408888889999997
        assert electricity["thisDay"]["cost"] == -0.737014080031
        assert electricity["thisWeek"]["value"] == -4.719
        assert electricity["thisWeek"]["cost"] == -1.31715544


def actuals_to_aggregation(text:dict):
    """A cumulativeHistoryAggregations exists, which only gives the aggregated values. Update the given parameter to be like that"""

    text["data"]["cumulativeHistoryAggregations"] = text["data"]["cumulativeHistory"]["aggregations"]
    del text["data"]["cumulativeHistory"]