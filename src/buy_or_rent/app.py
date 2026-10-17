"""Streamlit user interface for the buy-or-rent comparison."""

from dataclasses import dataclass
from typing import Literal

import streamlit as st

from buy_or_rent.finance import (
    MAX_DEBT_RATIO,
    estimated_property_value,
    resale_outcome,
    simulate,
    total_acquisition_cost,
)
from buy_or_rent.i18n import LANGUAGES, format_eur, format_percent, t
from buy_or_rent.models import (
    HouseholdParams,
    LoanParams,
    MarketParams,
    OwnerCostsParams,
    PurchaseParams,
    RentParams,
    SimulationInputs,
    SimulationResult,
)

FieldKind = Literal["eur", "pct", "years"]

RESALE_YEAR_KEY = "resale_year"
RESALE_PRICE_KEY = "resale_price"
RESALE_FEE_KEY = "resale_fee_rate_at_sale"
RESALE_PRICE_SOURCE_KEY = "resale_price_source"
RESALE_FEE_SOURCE_KEY = "resale_fee_source"


@dataclass(frozen=True)
class Field:
    """Definition of a numeric input of the sidebar.

    Attributes:
        key: Session state key, also used as translation key for the label.
        kind: Unit of the field.
        default: Default value, in percent for percentage fields.
        min_value: Lower bound.
        max_value: Upper bound, or None.
        help_key: Optional translation key of the tooltip.
    """

    key: str
    kind: FieldKind
    default: float
    min_value: float = 0.0
    max_value: float | None = None
    help_key: str | None = None


SECTIONS: list[tuple[str, list[Field]]] = [
    (
        "section_household",
        [
            Field("total_savings", "eur", 80_000),
            Field("savings_rate", "pct", 3.0, min_value=-50.0, max_value=100.0),
            Field("monthly_income", "eur", 5_000, help_key="monthly_income_help"),
            Field("income_growth", "pct", 1.5, min_value=-50.0, max_value=100.0),
            Field("monthly_savings", "eur", 1_700, help_key="monthly_savings_help"),
            Field("inflation", "pct", 2.0, min_value=-50.0, max_value=100.0),
        ],
    ),
    (
        "section_rent",
        [
            Field("monthly_rent", "eur", 1_300),
            Field("rent_growth", "pct", 2.0, min_value=-50.0, max_value=100.0),
        ],
    ),
    (
        "section_purchase",
        [
            Field("price", "eur", 300_000),
            Field("notary_fees", "eur", 22_500),
            Field("agency_fees", "eur", 0),
            Field("works", "eur", 10_000),
            Field("loan_fees", "eur", 3_000),
            Field("down_payment", "eur", 50_000),
        ],
    ),
    (
        "section_loan",
        [
            Field("loan_years", "years", 25, min_value=1, max_value=40),
            Field("loan_rate", "pct", 3.3, max_value=100.0),
            Field("monthly_insurance", "eur", 70),
        ],
    ),
    (
        "section_owner",
        [
            Field("condo_fees", "eur", 150),
            Field("property_tax", "eur", 1_200),
            Field("home_insurance", "eur", 20),
            Field("annual_maintenance", "eur", 1_500),
        ],
    ),
    (
        "section_market",
        [
            Field("property_growth", "pct", 1.5, min_value=-50.0, max_value=100.0),
            Field("resale_fee_rate", "pct", 5.0, max_value=100.0),
            Field("horizon_years", "years", 30, min_value=1, max_value=60),
        ],
    ),
]

FIELDS: dict[str, Field] = {
    field.key: field for _, fields in SECTIONS for field in fields
}


def init_state() -> None:
    """Initialise the sidebar inputs with their default values."""
    for field in FIELDS.values():
        default = int(field.default) if field.kind == "years" else float(field.default)
        st.session_state.setdefault(field.key, default)


def value(key: str) -> float:
    """Read a sidebar value converted to the model unit.

    Args:
        key: Field key.

    Returns:
        The value, percentages converted to decimals.
    """
    raw = float(st.session_state[key])
    return raw / 100 if FIELDS[key].kind == "pct" else raw


def build_inputs() -> SimulationInputs:
    """Build the simulation inputs from the stored values.

    Returns:
        The simulation inputs.
    """
    return SimulationInputs(
        household=HouseholdParams(
            total_savings=value("total_savings"),
            savings_rate=value("savings_rate"),
            monthly_income=value("monthly_income"),
            income_growth=value("income_growth"),
            monthly_savings=value("monthly_savings"),
            inflation=value("inflation"),
        ),
        rent=RentParams(
            monthly_rent=value("monthly_rent"), rent_growth=value("rent_growth")
        ),
        purchase=PurchaseParams(
            price=value("price"),
            notary_fees=value("notary_fees"),
            agency_fees=value("agency_fees"),
            works=value("works"),
            loan_fees=value("loan_fees"),
            down_payment=value("down_payment"),
        ),
        loan=LoanParams(
            years=int(value("loan_years")),
            rate=value("loan_rate"),
            monthly_insurance=value("monthly_insurance"),
        ),
        owner_costs=OwnerCostsParams(
            monthly_condo_fees=value("condo_fees"),
            annual_property_tax=value("property_tax"),
            monthly_home_insurance=value("home_insurance"),
            annual_maintenance=value("annual_maintenance"),
        ),
        market=MarketParams(
            property_growth=value("property_growth"),
            resale_fee_rate=value("resale_fee_rate"),
            horizon_years=int(value("horizon_years")),
        ),
    )


def max_down_payment() -> float:
    """Compute the highest allowed down payment.

    Returns:
        The lowest of total savings and total acquisition cost.
    """
    costs = PurchaseParams(
        price=value("price"),
        notary_fees=value("notary_fees"),
        agency_fees=value("agency_fees"),
        works=value("works"),
        loan_fees=value("loan_fees"),
        down_payment=0.0,
    )
    return min(value("total_savings"), total_acquisition_cost(costs))


def savings_too_high() -> bool:
    """Check whether monthly savings exceed what income leaves after rent.

    Returns:
        True if the entered savings are impossible.
    """
    return value("monthly_savings") > value("monthly_income") - value("monthly_rent")


def render_field(field: Field, lang: str) -> None:
    """Render one numeric input bound to the session state.

    Args:
        field: Field definition.
        lang: Language code.
    """
    help_text = t(field.help_key, lang) if field.help_key else None
    label = t(field.key, lang)
    if field.kind == "years":
        st.number_input(
            label,
            min_value=int(field.min_value),
            max_value=int(field.max_value) if field.max_value is not None else None,
            step=1,
            key=field.key,
            help=help_text,
        )
        return
    max_value = field.max_value
    if field.key == "down_payment":
        max_value = max_down_payment()
        st.session_state[field.key] = min(st.session_state[field.key], max_value)
    st.number_input(
        label,
        min_value=float(field.min_value),
        max_value=float(max_value) if max_value is not None else None,
        step=100.0 if field.kind == "eur" else 0.1,
        format="%.0f" if field.kind == "eur" else "%.2f",
        key=field.key,
        help=help_text,
    )


def sync_resale_defaults() -> None:
    """Keep resale price and fees in line with the sidebar until edited by hand.

    The price follows the estimate and the fees follow the sidebar rate as long
    as the user has not typed another value.
    """
    st.session_state.setdefault(RESALE_YEAR_KEY, min(10, int(value("horizon_years"))))
    sources = (
        (
            RESALE_PRICE_KEY,
            RESALE_PRICE_SOURCE_KEY,
            round(
                estimated_property_value(
                    value("price"),
                    value("property_growth"),
                    int(st.session_state[RESALE_YEAR_KEY]),
                )
            ),
        ),
        (
            RESALE_FEE_KEY,
            RESALE_FEE_SOURCE_KEY,
            float(st.session_state["resale_fee_rate"]),
        ),
    )
    for key, source_key, source in sources:
        current = st.session_state.get(key)
        if current is None or current == st.session_state.get(source_key):
            st.session_state[key] = source
        st.session_state[source_key] = source


def break_even_text(month: int | None, lang: str) -> str:
    """Describe the break-even point.

    Args:
        month: Break-even month index, or None.
        lang: Language code.

    Returns:
        Human readable break-even duration.
    """
    if month is None:
        return t("break_even_never", lang)
    if month == 0:
        return t("break_even_now", lang)
    return t("break_even_value", lang).format(years=month // 12, months=month % 12)


def render_metrics(result: SimulationResult, lang: str) -> None:
    """Render the key figures.

    Args:
        result: Simulation result.
        lang: Language code.
    """
    cost_cols = st.columns(4)
    cost_cols[0].metric(
        t("acquisition_cost", lang), format_eur(result.acquisition_cost, lang)
    )
    cost_cols[1].metric(t("loan_amount", lang), format_eur(result.loan_amount, lang))
    cost_cols[2].metric(t("credit_cost", lang), format_eur(result.credit_cost, lang))
    cost_cols[3].metric(
        t("total_outlay", lang),
        format_eur(result.total_outlay, lang),
        help=t("total_outlay_help", lang),
    )

    col1, col2 = st.columns(2)
    col1.metric(t("debt_ratio", lang), format_percent(result.debt_ratio, lang))
    col2.metric(t("break_even", lang), break_even_text(result.break_even_month, lang))

    col4, col5 = st.columns(2)
    col4.metric(
        t("monthly_rent_cost", lang), format_eur(result.initial_rent_cost, lang)
    )
    col5.metric(
        t("monthly_buy_cost", lang),
        format_eur(result.initial_buy_cost, lang),
        delta=format_eur(result.initial_buy_cost - result.initial_rent_cost, lang),
        delta_color="inverse",
    )
    col5.caption(
        t("loan_payment_detail", lang).format(
            payment=format_eur(result.loan_payment, lang),
            insurance=format_eur(result.loan_insurance, lang),
        )
    )

    if result.debt_ratio > MAX_DEBT_RATIO:
        st.warning(
            t("debt_ratio_warning", lang).format(
                limit=format_percent(MAX_DEBT_RATIO, lang)
            )
        )
    for scenario, savings in (
        ("scenario_rent", [row.rent_savings for row in result.yearly]),
        ("scenario_buy", [row.buy_savings for row in result.yearly]),
    ):
        if min(savings) < 0:
            st.warning(
                t("negative_savings_warning", lang).format(scenario=t(scenario, lang))
            )


def render_charts(result: SimulationResult, lang: str) -> None:
    """Render net worth and monthly cost charts.

    Args:
        result: Simulation result.
        lang: Language code.
    """
    year_col = t("col_year", lang)
    rent_label = t("rent_label", lang)
    buy_label = t("buy_label", lang)

    st.subheader(t("chart_net_worth", lang))
    st.line_chart(
        {
            year_col: [month / 12 for month in range(len(result.rent_net_worth))],
            rent_label: result.rent_net_worth,
            buy_label: result.buy_net_worth,
        },
        x=year_col,
        y=[rent_label, buy_label],
        y_label="€",
    )

    st.subheader(t("chart_costs", lang))
    st.line_chart(
        {
            year_col: [month / 12 for month in range(1, len(result.rent_costs) + 1)],
            rent_label: result.rent_costs,
            buy_label: result.buy_costs,
        },
        x=year_col,
        y=[rent_label, buy_label],
        y_label="€",
    )


def render_table(result: SimulationResult, lang: str) -> None:
    """Render the yearly breakdown table.

    Args:
        result: Simulation result.
        lang: Language code.
    """
    st.subheader(t("table_title", lang))
    rows = [
        {
            t("col_year", lang): row.year,
            t("col_rent_net_worth", lang): format_eur(row.rent_net_worth, lang),
            t("col_buy_net_worth", lang): format_eur(row.buy_net_worth, lang),
            t("col_difference", lang): format_eur(
                row.buy_net_worth - row.rent_net_worth, lang
            ),
            t("col_rent_cost", lang): format_eur(row.rent_monthly_cost, lang),
            t("col_buy_cost", lang): format_eur(row.buy_monthly_cost, lang),
            t("col_property_value", lang): format_eur(row.property_value, lang),
            t("col_remaining_principal", lang): format_eur(
                row.remaining_principal, lang
            ),
            t("col_buy_savings", lang): format_eur(row.buy_savings, lang),
        }
        for row in result.yearly[1:]
    ]
    st.dataframe(rows, hide_index=True, width="stretch")


def render_sidebar(lang: str) -> None:
    """Render all inputs in the sidebar.

    Args:
        lang: Language code.
    """
    with st.sidebar:
        for section_key, fields in SECTIONS:
            st.header(t(section_key, lang))
            for field in fields:
                render_field(field, lang)


def render_resale(lang: str) -> None:
    """Render the outcome of selling the property at a chosen year.

    Args:
        lang: Language code.
    """
    st.header(t("resale_title", lang))
    sync_resale_defaults()

    col1, col2, col3 = st.columns(3)
    col1.number_input(
        t("resale_year", lang),
        min_value=1,
        max_value=60,
        step=1,
        key=RESALE_YEAR_KEY,
    )
    col2.number_input(
        t("resale_price", lang),
        min_value=0,
        step=1_000,
        key=RESALE_PRICE_KEY,
        help=t("resale_price_help", lang).format(
            rate=format_percent(value("property_growth"), lang)
        ),
    )
    col3.number_input(
        t("resale_fee_rate", lang),
        min_value=0.0,
        max_value=100.0,
        step=0.1,
        format="%.2f",
        key=RESALE_FEE_KEY,
    )

    outcome = resale_outcome(
        build_inputs(),
        sale_price=float(st.session_state[RESALE_PRICE_KEY]),
        year=int(st.session_state[RESALE_YEAR_KEY]),
        resale_fee_rate=float(st.session_state[RESALE_FEE_KEY]) / 100,
    )

    sale_cols = st.columns(4)
    sale_cols[0].metric(t("sale_fees", lang), format_eur(outcome.sale_fees, lang))
    sale_cols[1].metric(
        t("col_remaining_principal", lang),
        format_eur(outcome.remaining_principal, lang),
    )
    sale_cols[2].metric(t("net_proceeds", lang), format_eur(outcome.net_proceeds, lang))
    sale_cols[3].metric(t("capital_gain", lang), format_eur(outcome.capital_gain, lang))

    outlay_cols = st.columns(2)
    outlay_cols[0].metric(
        t("owner_outlay", lang),
        format_eur(outcome.owner_outlay, lang),
        help=t("owner_outlay_help", lang),
    )
    outlay_cols[1].metric(t("rent_outlay", lang), format_eur(outcome.rent_outlay, lang))

    worth_cols = st.columns(2)
    worth_cols[0].metric(
        t("buy_wealth_at_sale", lang), format_eur(outcome.buy_net_worth, lang)
    )
    worth_cols[1].metric(
        t("rent_wealth_at_sale", lang), format_eur(outcome.rent_net_worth, lang)
    )

    if outcome.net_proceeds < 0:
        st.error(
            t("resale_negative_proceeds", lang).format(
                amount=format_eur(-outcome.net_proceeds, lang)
            )
        )
    difference = outcome.buy_net_worth - outcome.rent_net_worth
    verdict_key = "resale_verdict_buy" if difference >= 0 else "resale_verdict_rent"
    message = t(verdict_key, lang).format(
        years=outcome.year, amount=format_eur(abs(difference), lang)
    )
    if difference >= 0:
        st.success(message)
    else:
        st.info(message)


def main() -> None:
    """Render the whole application."""
    st.set_page_config(page_title="Buy or rent", layout="wide")
    init_state()
    lang = st.sidebar.radio(
        "Langue / Language",
        options=list(LANGUAGES),
        format_func=lambda code: LANGUAGES[code],
        horizontal=True,
        key="lang",
    )
    st.title(t("title", lang))
    st.caption(t("subtitle", lang))
    render_sidebar(lang)

    if savings_too_high():
        st.error(t("savings_too_high", lang))
        st.stop()
    result = simulate(build_inputs())
    render_metrics(result, lang)
    render_charts(result, lang)
    render_table(result, lang)
    st.divider()
    render_resale(lang)
    st.caption(t("assumptions", lang))


main()
