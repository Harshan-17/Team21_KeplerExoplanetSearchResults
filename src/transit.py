"""Next-transit calculations for the catalog's BKJD timing fields."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone


BKJD_OFFSET = 2_454_833.0


@dataclass(frozen=True)
class TransitResult:
    """The calculated next future transit or a clear invalid result."""

    validity: bool
    next_expected_transit: datetime | None = None
    remaining: timedelta | None = None
    next_transit_bkjd: float | None = None
    reason: str | None = None


def utc_to_bkjd(value: datetime) -> float:
    """Convert a UTC datetime to BKJD using the Kepler catalog offset."""

    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc)
    julian_date = value.timestamp() / 86_400.0 + 2_440_587.5
    return julian_date - BKJD_OFFSET


def bkjd_to_utc(value: float) -> datetime:
    """Convert a BKJD value to an aware UTC datetime."""

    unix_seconds = (value + BKJD_OFFSET - 2_440_587.5) * 86_400.0
    return datetime.fromtimestamp(unix_seconds, tz=timezone.utc)


def calculate_next_transit(
    transit_epoch_bkjd: object,
    orbital_period_days: object,
    now: datetime | None = None,
) -> TransitResult:
    """Calculate the next future event from epoch + n * orbital period."""

    try:
        epoch = float(transit_epoch_bkjd)
        period = float(orbital_period_days)
    except (TypeError, ValueError):
        return TransitResult(False, reason="Catalog timing fields are not numeric.")

    if not math.isfinite(epoch) or not math.isfinite(period) or period <= 0:
        return TransitResult(False, reason="Catalog timing fields are invalid.")

    current = now or datetime.now(timezone.utc)
    if current.tzinfo is None:
        current = current.replace(tzinfo=timezone.utc)
    current = current.astimezone(timezone.utc)
    current_bkjd = utc_to_bkjd(current)

    cycle = 0 if current_bkjd < epoch else math.floor((current_bkjd - epoch) / period) + 1
    next_bkjd = epoch + cycle * period
    next_utc = bkjd_to_utc(next_bkjd)
    remaining = next_utc - current

    if remaining.total_seconds() <= 0:
        cycle += 1
        next_bkjd = epoch + cycle * period
        next_utc = bkjd_to_utc(next_bkjd)
        remaining = next_utc - current

    return TransitResult(True, next_utc, remaining, next_bkjd)


def format_countdown(remaining: timedelta | None) -> str:
    """Format a remaining duration as DD : HH : MM : SS."""

    if remaining is None:
        return "-- : -- : -- : --"
    seconds = max(0, int(remaining.total_seconds()))
    days, seconds = divmod(seconds, 86_400)
    hours, seconds = divmod(seconds, 3_600)
    minutes, seconds = divmod(seconds, 60)
    return f"{days:02d} : {hours:02d} : {minutes:02d} : {seconds:02d}"
