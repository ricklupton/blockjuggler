"""Test functions related to simple time conversions.
"""
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from blockjuggler import tj_datetime

# Timezone in Prague
PRAGUE = ZoneInfo("Europe/Prague")
# UTC
UTC = ZoneInfo("UTC")


@pytest.mark.parametrize(
    "dt, expected", [
        (datetime(2017, 12, 15, 17, 35, 0, 0, UTC),
         "2017-12-15-17:35-+0000"),
        (datetime(2017, 12, 15, 18, 35, 0, 0, UTC),
         "2017-12-15-18:35-+0000"),
        (datetime(2017, 12, 15, 18, 35, 0, 0, PRAGUE),
         "2017-12-15-18:35-+0100"),
    ],
    ids=lambda itm: str(itm))
def test_tj_datetime(dt, expected):
    res = tj_datetime(dt)
    assert res == expected
