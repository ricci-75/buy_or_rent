"""Tests for the financial computations."""

import dataclasses

import pytest

from buy_or_rent.finance import (
    annuity_payment,
    break_even_month,
    credit_cost,
    debt_ratio,
    estimated_property_value,
    living_expenses,
    loan_amount,
    monthly_rate,
    remaining_principal,
    resale_outcome,
    simulate,
)
from buy_or_rent.models import (
    HouseholdParams,
    LoanParams,
    MarketParams,
    OwnerCostsParams,
    PurchaseParams,
    RentParams,
    SimulationInputs,
)


def make_inputs() -> SimulationInputs:
    """Build a simple, deterministic set of inputs.

    Returns:
        Simulation inputs with no growth, no inflation and no fees.
    """
    return SimulationInputs(
        household=HouseholdParams(
            total_savings=50_000,
            savings_rate=0.0,
            monthly_income=4_000,
            income_growth=0.0,
            monthly_savings=1_500,
            inflation=0.0,
        ),
        rent=RentParams(monthly_rent=1_000, rent_growth=0.0),
        purchase=PurchaseParams(
            price=200_000,
            notary_fees=0.0,
            agency_fees=0.0,
            works=0.0,
            loan_fees=0.0,
            down_payment=50_000,
        ),
        loan=LoanParams(years=20, rate=0.0, monthly_insurance=0.0),
        owner_costs=OwnerCostsParams(
            monthly_condo_fees=0.0,
            annual_property_tax=0.0,
            monthly_home_insurance=0.0,
            annual_maintenance=0.0,
        ),
        market=MarketParams(property_growth=0.0, resale_fee_rate=0.0, horizon_years=25),
    )


def test_monthly_rate_compounds_to_annual() -> None:
    """Twelve monthly periods give back the annual rate."""
    assert (1 + monthly_rate(0.05)) ** 12 == pytest.approx(1.05)


def test_annuity_payment_known_value() -> None:
    """A 200k loan at 3 % over 20 years costs about 1109.20 per month."""
    assert annuity_payment(200_000, 0.03, 20) == pytest.approx(1109.20, abs=0.01)


def test_annuity_payment_zero_rate() -> None:
    """At 0 % the payment is the principal split evenly."""
    assert annuity_payment(120_000, 0.0, 10) == pytest.approx(1_000)


def test_annuity_payment_no_principal() -> None:
    """Nothing borrowed means nothing to pay."""
    assert annuity_payment(0, 0.03, 20) == 0.0


@pytest.mark.parametrize("rate", [0.0, 0.035])
def test_remaining_principal_bounds(rate: float) -> None:
    """Principal is full at start and zero at the end."""
    assert remaining_principal(100_000, rate, 15, 0) == pytest.approx(100_000)
    assert remaining_principal(100_000, rate, 15, 180) == 0.0
    assert 0 < remaining_principal(100_000, rate, 15, 90) < 100_000


def test_remaining_principal_matches_amortization() -> None:
    """Closed form matches a step-by-step amortization."""
    principal, rate, years = 150_000, 0.04, 20
    payment = annuity_payment(principal, rate, years)
    balance = float(principal)
    for _ in range(60):
        balance = balance * (1 + rate / 12) - payment
    assert remaining_principal(principal, rate, years, 60) == pytest.approx(balance)


def test_loan_amount_includes_all_costs() -> None:
    """Loan covers price, fees and works minus the down payment."""
    purchase = PurchaseParams(
        price=300_000,
        notary_fees=22_500,
        agency_fees=10_000,
        works=20_000,
        loan_fees=3_000,
        down_payment=50_000,
    )
    assert loan_amount(purchase) == pytest.approx(
        300_000 + 22_500 + 10_000 + 20_000 + 3_000 - 50_000
    )


def test_loan_amount_rejects_excessive_down_payment() -> None:
    """A down payment above the total cost is invalid."""
    purchase = PurchaseParams(
        price=100,
        notary_fees=0.0,
        agency_fees=0.0,
        works=0.0,
        loan_fees=0.0,
        down_payment=200,
    )
    with pytest.raises(ValueError):
        loan_amount(purchase)


def test_debt_ratio() -> None:
    """Ratio is loan cost over income, infinite without income."""
    assert debt_ratio(1_000, 4_000) == pytest.approx(0.25)
    assert debt_ratio(1_000, 0) == float("inf")
    assert debt_ratio(0, 0) == 0.0


def test_break_even_month() -> None:
    """Break-even is the first month after which buying stays ahead."""
    assert break_even_month([10, 10, 10, 10], [5, 11, 9, 12]) == 3
    assert break_even_month([10, 10], [10, 11]) == 0
    assert break_even_month([10, 10], [11, 9]) is None


def test_simulate_rejects_down_payment_above_savings() -> None:
    """The down payment cannot exceed available savings."""
    inputs = make_inputs()
    inputs = dataclasses.replace(
        inputs, purchase=dataclasses.replace(inputs.purchase, down_payment=60_000)
    )
    with pytest.raises(ValueError):
        simulate(inputs)


def test_simulate_without_growth() -> None:
    """With no growth or fees, both scenarios are easy to compute by hand."""
    result = simulate(make_inputs())
    assert result.loan_amount == pytest.approx(150_000)
    assert result.loan_payment == pytest.approx(625)
    assert result.initial_rent_cost == pytest.approx(1_000)
    assert result.initial_buy_cost == pytest.approx(625)
    assert len(result.yearly) == 26
    # Owner pays 375 less per month than the renter, so both net worths match at start.
    assert result.buy_net_worth[0] == pytest.approx(result.rent_net_worth[0])
    assert result.break_even_month == 0
    final = result.yearly[-1]
    assert final.remaining_principal == 0.0
    assert final.rent_net_worth == pytest.approx(
        50_000 + 2_500 * 12 * 25 - 1_000 * 12 * 25
    )
    assert final.buy_net_worth == pytest.approx(
        200_000 + 2_500 * 12 * 25 - 625 * 12 * 20
    )


def test_simulate_renting_wins_with_high_fees_and_returns() -> None:
    """High fees, high savings returns and falling prices favour renting."""
    inputs = make_inputs()
    inputs = dataclasses.replace(
        inputs,
        household=dataclasses.replace(inputs.household, savings_rate=0.08),
        purchase=dataclasses.replace(inputs.purchase, notary_fees=16_000),
        loan=dataclasses.replace(inputs.loan, rate=0.05),
        market=MarketParams(
            property_growth=-0.02, resale_fee_rate=0.06, horizon_years=10
        ),
    )
    assert simulate(inputs).break_even_month is None


def test_simulate_property_growth_brings_break_even_forward() -> None:
    """Faster property appreciation never delays the break-even point."""
    inputs = make_inputs()
    inputs = dataclasses.replace(
        inputs,
        household=dataclasses.replace(inputs.household, savings_rate=0.04),
        purchase=dataclasses.replace(inputs.purchase, notary_fees=16_000),
        loan=dataclasses.replace(inputs.loan, rate=0.035),
        market=dataclasses.replace(inputs.market, resale_fee_rate=0.05),
    )
    slow = simulate(
        dataclasses.replace(
            inputs, market=dataclasses.replace(inputs.market, property_growth=0.0)
        )
    )
    fast = simulate(
        dataclasses.replace(
            inputs, market=dataclasses.replace(inputs.market, property_growth=0.04)
        )
    )
    assert fast.break_even_month is not None
    assert (
        slow.break_even_month is None or fast.break_even_month <= slow.break_even_month
    )


def test_living_expenses_derived_from_savings() -> None:
    """Expenses are income minus rent minus current savings."""
    household = make_inputs().household
    assert living_expenses(household, 1_000) == pytest.approx(1_500)


def test_living_expenses_rejects_excessive_savings() -> None:
    """Saving more than income minus rent is impossible."""
    household = dataclasses.replace(make_inputs().household, monthly_savings=3_500)
    with pytest.raises(ValueError):
        living_expenses(household, 1_000)


def test_simulate_owner_costs_in_euros() -> None:
    """Insurance, maintenance and fees in euros flow into costs and loan."""
    inputs = make_inputs()
    inputs = dataclasses.replace(
        inputs,
        purchase=dataclasses.replace(inputs.purchase, notary_fees=12_000),
        loan=dataclasses.replace(inputs.loan, monthly_insurance=50),
        owner_costs=dataclasses.replace(inputs.owner_costs, annual_maintenance=1_200),
    )
    result = simulate(inputs)
    assert result.loan_amount == pytest.approx(162_000)
    assert result.loan_insurance == pytest.approx(50)
    assert result.acquisition_cost == pytest.approx(212_000)
    assert result.credit_cost == pytest.approx(50 * 240)
    assert result.total_outlay == pytest.approx(50_000 + 162_000 + 50 * 240)
    assert result.initial_buy_cost == pytest.approx(162_000 / 240 + 50 + 100)
    # Insurance stops with the loan, maintenance stays.
    assert result.buy_costs[-1] == pytest.approx(100)


def test_credit_cost() -> None:
    """Credit cost is everything paid to the bank beyond the principal."""
    payment = annuity_payment(200_000, 0.03, 20)
    assert credit_cost(200_000, payment, 40, 20) == pytest.approx(
        payment * 240 + 40 * 240 - 200_000
    )
    assert credit_cost(0, 0, 40, 20) == 0.0


def test_estimated_property_value() -> None:
    """Value compounds yearly."""
    assert estimated_property_value(100_000, 0.02, 2) == pytest.approx(104_040)


def test_resale_outcome_without_growth() -> None:
    """Selling after 10 years with no growth is easy to compute by hand."""
    outcome = resale_outcome(
        make_inputs(), sale_price=220_000, year=10, resale_fee_rate=0.05
    )
    debt = 150_000 / 2
    assert outcome.sale_fees == pytest.approx(11_000)
    assert outcome.remaining_principal == pytest.approx(debt)
    assert outcome.net_proceeds == pytest.approx(220_000 - 11_000 - debt)
    assert outcome.capital_gain == pytest.approx(20_000)
    assert outcome.owner_outlay == pytest.approx(50_000 + 625 * 120)
    assert outcome.rent_outlay == pytest.approx(1_000 * 120)
    buyer_savings = 2_500 * 120 - 625 * 120
    assert outcome.buy_net_worth == pytest.approx(outcome.net_proceeds + buyer_savings)
    assert outcome.rent_net_worth == pytest.approx(50_000 + 1_500 * 120)


def test_resale_outcome_beyond_horizon() -> None:
    """A resale after the horizon extends the simulation."""
    inputs = make_inputs()
    inputs = dataclasses.replace(
        inputs, market=dataclasses.replace(inputs.market, horizon_years=5)
    )
    outcome = resale_outcome(inputs, sale_price=200_000, year=30, resale_fee_rate=0.0)
    assert outcome.remaining_principal == 0.0
    assert outcome.net_proceeds == pytest.approx(200_000)


def test_resale_outcome_rejects_year_zero() -> None:
    """The property must be held at least one year."""
    with pytest.raises(ValueError):
        resale_outcome(make_inputs(), sale_price=200_000, year=0, resale_fee_rate=0.05)
