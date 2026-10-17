"""Input parameters and simulation results for the buy-or-rent comparison.

All rates are expressed as decimals (0.03 means 3 %) and all amounts in euros.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class HouseholdParams:
    """Financial situation of the household.

    Attributes:
        total_savings: Total savings available today.
        savings_rate: Annual net return of the savings.
        monthly_income: Monthly net income before income tax.
        income_growth: Annual growth rate of the income.
        monthly_savings: Amount currently saved each month while renting.
        inflation: Annual inflation applied to living expenses and owner costs.
    """

    total_savings: float
    savings_rate: float
    monthly_income: float
    income_growth: float
    monthly_savings: float
    inflation: float


@dataclass(frozen=True)
class RentParams:
    """Current rental situation.

    Attributes:
        monthly_rent: Monthly rent including charges and home insurance.
        rent_growth: Annual rent increase rate.
    """

    monthly_rent: float
    rent_growth: float


@dataclass(frozen=True)
class PurchaseParams:
    """Acquisition costs of the property.

    Attributes:
        price: Net seller price of the property.
        notary_fees: Notary fees.
        agency_fees: Agency fees paid by the buyer.
        works: Renovation works budget.
        loan_fees: Bank file and guarantee fees.
        down_payment: Down payment taken from the savings.
    """

    price: float
    notary_fees: float
    agency_fees: float
    works: float
    loan_fees: float
    down_payment: float


@dataclass(frozen=True)
class LoanParams:
    """Mortgage parameters.

    Attributes:
        years: Loan duration in years.
        rate: Annual nominal interest rate.
        monthly_insurance: Monthly borrower insurance, paid during the loan.
    """

    years: int
    rate: float
    monthly_insurance: float


@dataclass(frozen=True)
class OwnerCostsParams:
    """Recurring costs borne by the owner, excluding the loan.

    Attributes:
        monthly_condo_fees: Monthly co-ownership charges.
        annual_property_tax: Annual property tax.
        monthly_home_insurance: Monthly home insurance.
        annual_maintenance: Annual maintenance budget.
    """

    monthly_condo_fees: float
    annual_property_tax: float
    monthly_home_insurance: float
    annual_maintenance: float


@dataclass(frozen=True)
class MarketParams:
    """Real estate market and simulation settings.

    Attributes:
        property_growth: Annual change of the property value.
        resale_fee_rate: Fees paid on resale as a share of the property value.
        horizon_years: Simulation horizon in years.
    """

    property_growth: float
    resale_fee_rate: float
    horizon_years: int


@dataclass(frozen=True)
class SimulationInputs:
    """All parameters needed to run a simulation.

    Attributes:
        household: Household financial situation.
        rent: Rental scenario parameters.
        purchase: Acquisition costs.
        loan: Mortgage parameters.
        owner_costs: Recurring owner costs.
        market: Market and horizon settings.
    """

    household: HouseholdParams
    rent: RentParams
    purchase: PurchaseParams
    loan: LoanParams
    owner_costs: OwnerCostsParams
    market: MarketParams


@dataclass(frozen=True)
class YearlyRow:
    """Snapshot of both scenarios at the end of a year.

    Attributes:
        year: Number of elapsed years.
        rent_monthly_cost: Monthly housing cost of the renter during that year.
        buy_monthly_cost: Monthly housing cost of the owner during that year.
        rent_savings: Invested savings of the renter.
        buy_savings: Invested savings of the owner.
        property_value: Market value of the property.
        remaining_principal: Outstanding loan principal.
        rent_net_worth: Net worth of the renter.
        buy_net_worth: Liquidation net worth of the owner.
    """

    year: int
    rent_monthly_cost: float
    buy_monthly_cost: float
    rent_savings: float
    buy_savings: float
    property_value: float
    remaining_principal: float
    rent_net_worth: float
    buy_net_worth: float


@dataclass(frozen=True)
class SimulationResult:
    """Outcome of a buy-or-rent simulation.

    Attributes:
        acquisition_cost: Price plus all fees and works.
        loan_amount: Amount borrowed.
        loan_payment: Monthly loan payment excluding insurance.
        loan_insurance: Monthly borrower insurance.
        credit_cost: Total interest and borrower insurance over the loan.
        total_outlay: Down payment plus all loan payments and insurance.
        initial_rent_cost: Monthly housing cost of the renter at month 1.
        initial_buy_cost: Monthly housing cost of the owner at month 1.
        debt_ratio: Share of income spent on the loan at month 1.
        rent_net_worth: Renter net worth for each month, index 0 being today.
        buy_net_worth: Owner net worth for each month, index 0 being today.
        rent_costs: Renter monthly housing cost for each month starting at month 1.
        buy_costs: Owner monthly housing cost for each month starting at month 1.
        yearly: Yearly snapshots, year 0 being today.
        break_even_month: First month from which buying stays ahead, or None.
    """

    acquisition_cost: float
    loan_amount: float
    loan_payment: float
    loan_insurance: float
    credit_cost: float
    total_outlay: float
    initial_rent_cost: float
    initial_buy_cost: float
    debt_ratio: float
    rent_net_worth: list[float]
    buy_net_worth: list[float]
    rent_costs: list[float]
    buy_costs: list[float]
    yearly: list[YearlyRow]
    break_even_month: int | None


@dataclass(frozen=True)
class ResaleOutcome:
    """Outcome of selling the property at a given year.

    Attributes:
        year: Number of years after purchase when the property is sold.
        sale_price: Net seller resale price.
        sale_fees: Fees paid on resale.
        remaining_principal: Outstanding loan principal repaid at sale.
        net_proceeds: Cash left after fees and loan repayment.
        capital_gain: Resale price minus total acquisition cost.
        owner_outlay: Down payment plus all owner housing costs until the sale.
        rent_outlay: All rents paid over the same period.
        buy_net_worth: Owner net worth right after the sale.
        rent_net_worth: Renter net worth at the same date.
    """

    year: int
    sale_price: float
    sale_fees: float
    remaining_principal: float
    net_proceeds: float
    capital_gain: float
    owner_outlay: float
    rent_outlay: float
    buy_net_worth: float
    rent_net_worth: float
