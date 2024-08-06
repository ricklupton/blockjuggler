"""Test functions related to simple time conversions.
"""
from datetime import datetime

import pytest
from pytz import timezone

from blockjuggler import tj_datetime #, org_date

# Timezone in Prague
PRAGUE = timezone("Europe/Prague")
# UTC
UTC = timezone("UTC")


@pytest.mark.parametrize(
    "dt, tz, expected", [
        (datetime(2017, 12, 15, 17, 35, 0, 0, UTC), PRAGUE,
         "2017-12-15-18:35"),
        (datetime(2017, 12, 15, 18, 35, 0, 0, UTC), PRAGUE,
         "2017-12-15-19:35"),
    ],
    ids=lambda itm: str(itm))
def test_tj_datetime(dt, tz, expected):
    res = tj_datetime(dt, tz)
    assert res == expected


# @pytest.mark.parametrize(
#     "dt, tz, expected", [
#         (datetime(2017, 12, 15, 17, 35, 0, 0, UTC), PRAGUE,
#          "<2017-12-15 Fri>"),
#         (datetime(2017, 12, 15, 18, 35, 0, 0, UTC), PRAGUE,
#          "<2017-12-15 Fri>"),
#     ],
#     ids=lambda itm: str(itm))
# def test_org_date(dt, tz, expected):
#     res = org_date(dt, tz)
#     assert res == expected
