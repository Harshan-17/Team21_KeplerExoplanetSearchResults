"""Mathematical next-transit calculations for Kepler catalog observations."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import math
from typing import Any


# Kepler Barycentric Julian Date is defined relative to this Julian Date offset.
BKJD_OFFSET = 2_454_833.0
JULIAN_DATE_UNIX_EPOCH = 2_440_587.5
SECONDS_PER_DAY = 86_400.0


@dataclass(frozen=True)
class TransitResult:
    """Result of calculating the next future transit."""

    valid: bool
    next_expected_transit_bkjd: float | None
    next_expected_transit_utc: datetime | None
    remaining_time: timedelta | None

    @property
    def next_expected_transit(self) -> datetime | None:
        """Return the next expected transit in UTC for a simple public API."""

        return self.next_expected_transit_utc


def _invalid_result() -> TransitResult:
    return TransitResult(
        valid=False,
        next_expected_transit_bkjd=None,
        next_expected_transit_utc=None,
        remaining_time=None,
    )


def _finite_float(value: Any) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def _normalise_utc(value: datetime | None) -> datetime:
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _utc_to_bkjd(value: datetime) -> float:
    unix_seconds = (value - datetime(1970, 1, 1, tzinfo=timezone.utc)).total_seconds()
    julian_date = JULIAN_DATE_UNIX_EPOCH + unix_seconds / SECONDS_PER_DAY
    return julian_date - BKJD_OFFSET


def _bkjd_to_utc(value: float) -> datetime:
    julian_date = value + BKJD_OFFSET
    days_since_unix_epoch = julian_date - JULIAN_DATE_UNIX_EPOCH
    return datetime(1970, 1, 1, tzinfo=timezone.utc) + timedelta(days=days_since_unix_epoch)


def calculate_next_transit(
    transit_epoch_bkjd: Any,
    orbital_period_days: Any,
    now_utc: datetime | None = None,
) -> TransitResult:
    """Calculate the next future transit from a catalog epoch and period.

    The application maps the repository's ``koi_time0bk`` field to
    ``transit_epoch_bkjd`` and ``koi_period`` to ``orbital_period_days``.
    ``now_utc`` is injectable so the mathematical result can be tested
    deterministically; omitted values use the current UTC time.
    """

    epoch = _finite_float(transit_epoch_bkjd)
    period = _finite_float(orbital_period_days)
    if epoch is None or period is None or period <= 0:
        return _invalid_result()

    current_utc = _normalise_utc(now_utc)
    current_bkjd = _utc_to_bkjd(current_utc)

    # n is constrained to the reference epoch and later transits. The loop
    # protects the strict-future requirement from floating-point rounding.
    n = max(0, math.floor((current_bkjd - epoch) / period) + 1)
    next_bkjd = epoch + n * period
    while next_bkjd <= current_bkjd:
        n += 1
        next_bkjd = epoch + n * period

    next_utc = _bkjd_to_utc(next_bkjd)
    remaining = next_utc - current_utc
    if remaining.total_seconds() <= 0:
        return _invalid_result()

    return TransitResult(
        valid=True,
        next_expected_transit_bkjd=next_bkjd,
        next_expected_transit_utc=next_utc,
        remaining_time=remaining,
    )
