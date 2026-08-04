# Invoice Rounding Fixture

The billing rule requires monetary totals to round to two decimal places using
decimal half-up rounding. The current implementation reports `2.67` for an
amount of `2.675`; the expected invoice total is `2.68`.
