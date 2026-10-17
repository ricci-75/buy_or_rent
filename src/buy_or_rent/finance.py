"""Pure financial computations for the buy-or-rent comparison."""

from dataclasses import replace

from buy_or_rent.models import (
    HouseholdParams,
    PurchaseParams,
    ResaleOutcome,
    SimulationInputs,
    SimulationResult,
    YearlyRow,
)

MAX_DEBT_RATIO = 0.35


def monthly_rate(annual_rate: float) -> float:
    """Convert an annual compound rate into the equivalent monthly rate.

    Args:
        annual_rate: Annual rate as a decimal.

    Returns:
        The monthly rate yielding the same annual growth.
    """
    return (1 + annual_rate) ** (1 / 12) - 1


def annuity_payment(principal: float, annual_rate: float, years: int) -> float:
    """Compute the constant monthly payment of an amortizing loan.

    French mortgages quote a nominal rate, so the monthly rate is the annual
    rate divided by 12 rather than the compound equivalent.

    Args:
        principal: Amount borrowed.
        annual_rate: Annual nominal interest rate as a decimal.
        years: Loan duration in years.

    Returns:
        The monthly payment excluding insurance.
    """
    if principal <= 0 or years <= 0:
        return 0.0
    n = years * 12
    r = annual_rate / 12
    if r == 0:
        return principal / n
    return principal * r / (1 - (1 + r) ** -n)


def remaining_principal(
    principal: float, annual_rate: float, years: int, months_paid: int
) -> float:
    """Compute the outstanding principal after a number of payments.

    Args:
        principal: Amount borrowed.
        annual_rate: Annual nominal interest rate as a decimal.
        years: Loan duration in years.
        months_paid: Number of monthly payments already made.

    Returns:
        The outstanding principal, never negative.
    """
    n = years * 12
    if principal <= 0 or months_paid >= n:
        return 0.0
    r = annual_rate / 12
    if r == 0:
        return principal * (1 - months_paid / n)
    growth_n = (1 + r) ** n
    return principal * (growth_n - (1 + r) ** months_paid) / (growth_n - 1)


def total_acquisition_cost(purchase: PurchaseParams) -> float:
    """Compute the total cost of the acquisition.

    Args:
        purchase: Acquisition parameters.

    Returns:
        Price plus notary, agency, works and loan fees.
    """
    return (
        purchase.price
        + purchase.notary_fees
        + purchase.agency_fees
        + purchase.works
        + purchase.loan_fees
    )


def loan_amount(purchase: PurchaseParams) -> float:
    """Compute the amount to borrow.

    Args:
        purchase: Acquisition parameters.

    Returns:
        Total acquisition cost minus the down payment.

    Raises:
        ValueError: If the down payment exceeds the acquisition cost.
    """
    total = total_acquisition_cost(purchase)
    if purchase.down_payment > total:
        raise ValueError("Down payment exceeds the total acquisition cost.")
    return total - purchase.down_payment


def credit_cost(
    principal: float, payment: float, insurance: float, years: int
) -> float:
    """Compute the total cost of the credit over its whole duration.

    Args:
        principal: Amount borrowed.
        payment: Monthly loan payment excluding insurance.
        insurance: Monthly borrower insurance.
        years: Loan duration in years.

    Returns:
        Total interest plus total borrower insurance.
    """
    if principal <= 0:
        return 0.0
    return (payment + insurance) * years * 12 - principal


def living_expenses(household: HouseholdParams, monthly_rent: float) -> float:
    """Derive the monthly living expenses, excluding housing, from the savings.

    Args:
        household: Household parameters, savings being those made while renting.
        monthly_rent: Current monthly rent.

    Returns:
        Income minus rent minus monthly savings.

    Raises:
        ValueError: If the savings exceed what the income leaves after rent.
    """
    expenses = household.monthly_income - monthly_rent - household.monthly_savings
    if expenses < 0:
        raise ValueError("Monthly savings exceed income minus rent.")
    return expenses


def debt_ratio(monthly_loan_cost: float, monthly_income: float) -> float:
    """Compute the debt-to-income ratio.

    Args:
        monthly_loan_cost: Monthly loan payment including insurance.
        monthly_income: Monthly net income.

    Returns:
        The ratio, or infinity when income is zero and a loan is due.
    """
    if monthly_income <= 0:
        return float("inf") if monthly_loan_cost > 0 else 0.0
    return monthly_loan_cost / monthly_income


def break_even_month(
    rent_net_worth: list[float], buy_net_worth: list[float]
) -> int | None:
    """Find the first month from which buying stays at least as good as renting.

    Args:
        rent_net_worth: Renter net worth per month, index 0 being today.
        buy_net_worth: Owner net worth per month, index 0 being today.

    Returns:
        The month index, or None if renting is still ahead at the end.
    """
    last_rent_ahead = -1
    for month, (rent, buy) in enumerate(
        zip(rent_net_worth, buy_net_worth, strict=True)
    ):
        if buy < rent:
            last_rent_ahead = month
    if last_rent_ahead == len(buy_net_worth) - 1:
        return None
    return last_rent_ahead + 1


def simulate(inputs: SimulationInputs) -> SimulationResult:
    """Simulate both scenarios month by month over the horizon.

    Living expenses are derived from the current savings while renting. Each
    month, every scenario saves its income minus living expenses and housing
    cost (a negative amount is drawn from the savings), and the savings grow
    at the savings rate. Yearly indexations apply at each anniversary.

    Args:
        inputs: All simulation parameters.

    Returns:
        The simulation result.

    Raises:
        ValueError: If the down payment exceeds the savings or the acquisition
            cost, or if the monthly savings exceed income minus rent.
    """
    hh = inputs.household
    purchase = inputs.purchase
    loan = inputs.loan
    owner = inputs.owner_costs
    market = inputs.market

    if purchase.down_payment > hh.total_savings:
        raise ValueError("Down payment exceeds total savings.")

    principal = loan_amount(purchase)
    payment = annuity_payment(principal, loan.rate, loan.years)
    insurance = loan.monthly_insurance if principal > 0 else 0.0
    base_expenses = living_expenses(hh, inputs.rent.monthly_rent)
    loan_months = loan.years * 12
    savings_monthly_rate = monthly_rate(hh.savings_rate)
    property_monthly_rate = monthly_rate(market.property_growth)

    rent_savings = hh.total_savings
    buy_savings = hh.total_savings - purchase.down_payment
    property_value = purchase.price

    def buy_net_worth(value: float, debt: float, savings: float) -> float:
        """Compute the owner liquidation net worth.

        Args:
            value: Property market value.
            debt: Outstanding principal.
            savings: Owner invested savings.

        Returns:
            Net worth if the property were sold now.
        """
        return value * (1 - market.resale_fee_rate) - debt + savings

    rent_worth = [rent_savings]
    buy_worth = [buy_net_worth(property_value, principal, buy_savings)]
    rent_costs: list[float] = []
    buy_costs: list[float] = []
    yearly = [
        YearlyRow(
            year=0,
            rent_monthly_cost=0.0,
            buy_monthly_cost=0.0,
            rent_savings=rent_savings,
            buy_savings=buy_savings,
            property_value=property_value,
            remaining_principal=principal,
            rent_net_worth=rent_worth[0],
            buy_net_worth=buy_worth[0],
        )
    ]

    for month in range(1, market.horizon_years * 12 + 1):
        year_index = (month - 1) // 12
        inflation_factor = (1 + hh.inflation) ** year_index
        income = hh.monthly_income * (1 + hh.income_growth) ** year_index
        expenses = base_expenses * inflation_factor
        rent_cost = (
            inputs.rent.monthly_rent * (1 + inputs.rent.rent_growth) ** year_index
        )
        loan_cost = payment + insurance if month <= loan_months else 0.0
        buy_cost = (
            loan_cost
            + (
                owner.monthly_condo_fees
                + owner.annual_property_tax / 12
                + owner.monthly_home_insurance
                + owner.annual_maintenance / 12
            )
            * inflation_factor
        )

        rent_savings = (
            rent_savings * (1 + savings_monthly_rate) + income - expenses - rent_cost
        )
        buy_savings = (
            buy_savings * (1 + savings_monthly_rate) + income - expenses - buy_cost
        )
        property_value *= 1 + property_monthly_rate
        debt = remaining_principal(principal, loan.rate, loan.years, month)

        rent_costs.append(rent_cost)
        buy_costs.append(buy_cost)
        rent_worth.append(rent_savings)
        buy_worth.append(buy_net_worth(property_value, debt, buy_savings))

        if month % 12 == 0:
            yearly.append(
                YearlyRow(
                    year=month // 12,
                    rent_monthly_cost=rent_cost,
                    buy_monthly_cost=buy_cost,
                    rent_savings=rent_savings,
                    buy_savings=buy_savings,
                    property_value=property_value,
                    remaining_principal=debt,
                    rent_net_worth=rent_worth[-1],
                    buy_net_worth=buy_worth[-1],
                )
            )

    return SimulationResult(
        acquisition_cost=total_acquisition_cost(purchase),
        loan_amount=principal,
        loan_payment=payment,
        loan_insurance=insurance,
        credit_cost=credit_cost(principal, payment, insurance, loan.years),
        total_outlay=purchase.down_payment + (payment + insurance) * loan_months,
        initial_rent_cost=rent_costs[0] if rent_costs else inputs.rent.monthly_rent,
        initial_buy_cost=buy_costs[0] if buy_costs else 0.0,
        debt_ratio=debt_ratio(payment + insurance, hh.monthly_income),
        rent_net_worth=rent_worth,
        buy_net_worth=buy_worth,
        rent_costs=rent_costs,
        buy_costs=buy_costs,
        yearly=yearly,
        break_even_month=break_even_month(rent_worth, buy_worth),
    )


def estimated_property_value(price: float, annual_growth: float, years: int) -> float:
    """Estimate the property value after a number of years.

    Args:
        price: Purchase price.
        annual_growth: Annual change of the property value.
        years: Number of elapsed years.

    Returns:
        The estimated value.
    """
    return price * (1 + annual_growth) ** years


def resale_outcome(
    inputs: SimulationInputs, sale_price: float, year: int, resale_fee_rate: float
) -> ResaleOutcome:
    """Evaluate selling the property at the end of a given year.

    The simulation is extended when the resale year exceeds the horizon, so the
    savings of both scenarios are known at the sale date.

    Args:
        inputs: All simulation parameters.
        sale_price: Net seller resale price.
        year: Number of years after purchase when the property is sold.
        resale_fee_rate: Resale fees as a share of the sale price.

    Returns:
        The resale outcome.

    Raises:
        ValueError: If the year is lower than 1 or inputs are inconsistent.
    """
    if year < 1:
        raise ValueError("Resale year must be at least 1.")
    horizon = max(inputs.market.horizon_years, year)
    result = simulate(
        replace(inputs, market=replace(inputs.market, horizon_years=horizon))
    )
    row = result.yearly[year]
    months = year * 12
    sale_fees = sale_price * resale_fee_rate
    net_proceeds = sale_price - sale_fees - row.remaining_principal
    return ResaleOutcome(
        year=year,
        sale_price=sale_price,
        sale_fees=sale_fees,
        remaining_principal=row.remaining_principal,
        net_proceeds=net_proceeds,
        capital_gain=sale_price - result.acquisition_cost,
        owner_outlay=inputs.purchase.down_payment + sum(result.buy_costs[:months]),
        rent_outlay=sum(result.rent_costs[:months]),
        buy_net_worth=net_proceeds + row.buy_savings,
        rent_net_worth=row.rent_net_worth,
    )
