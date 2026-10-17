"""User interface translations and euro formatting."""

LANGUAGES: dict[str, str] = {"fr": "Français", "en": "English"}

TRANSLATIONS: dict[str, dict[str, str]] = {
    "fr": {
        "title": "Louer ou acheter ?",
        "subtitle": "Compare l'évolution de ton patrimoine net en location et en achat.",
        "language": "Langue",
        "section_household": "Foyer",
        "total_savings": "Épargne totale (€)",
        "savings_rate": "Rendement net annuel de l'épargne (%)",
        "monthly_income": "Revenu mensuel net avant impôt (€)",
        "monthly_income_help": "Sert au taux d'endettement et à l'évolution de l'épargne via la croissance du revenu.",
        "income_growth": "Croissance annuelle du revenu (%)",
        "monthly_savings": "Épargne mensuelle actuelle (€)",
        "monthly_savings_help": "Ce que tu mets de côté chaque mois aujourd'hui en location. Les dépenses de vie en sont déduites : revenu - loyer - épargne.",
        "savings_too_high": "L'épargne mensuelle dépasse le revenu moins le loyer.",
        "inflation": "Inflation annuelle (%)",
        "section_rent": "Location",
        "monthly_rent": "Loyer + charges + assurance mensuels (€)",
        "rent_growth": "Revalorisation annuelle du loyer (%)",
        "section_purchase": "Achat",
        "price": "Prix net vendeur (€)",
        "notary_fees": "Frais de notaire (€)",
        "agency_fees": "Frais d'agence à charge acquéreur (€)",
        "works": "Travaux (€)",
        "loan_fees": "Frais de dossier et garantie (€)",
        "down_payment": "Apport (€)",
        "section_loan": "Prêt",
        "loan_years": "Durée (années)",
        "loan_rate": "Taux nominal annuel (%)",
        "monthly_insurance": "Assurance emprunteur mensuelle (€)",
        "section_owner": "Coûts propriétaire",
        "condo_fees": "Charges de copropriété mensuelles (€)",
        "property_tax": "Taxe foncière annuelle (€)",
        "home_insurance": "Assurance habitation mensuelle (€)",
        "annual_maintenance": "Entretien annuel (€)",
        "section_market": "Marché et horizon",
        "property_growth": "Évolution annuelle du prix de l'immobilier (%)",
        "resale_fee_rate": "Frais de revente (% de la valeur)",
        "horizon_years": "Horizon de simulation (années)",
        "acquisition_cost": "Coût total de l'acquisition",
        "loan_amount": "Montant emprunté",
        "credit_cost": "Coût du crédit (intérêts + assurance)",
        "total_outlay": "Total déboursé sur la durée du prêt",
        "total_outlay_help": "Apport + toutes les mensualités + assurance emprunteur.",
        "monthly_rent_cost": "Coût mensuel location",
        "monthly_buy_cost": "Coût mensuel achat",
        "loan_payment_detail": "dont prêt {payment} + assurance {insurance}",
        "debt_ratio": "Taux d'endettement",
        "debt_ratio_warning": "Taux d'endettement supérieur à {limit} : un financement bancaire est peu probable.",
        "break_even": "Achat plus rentable après",
        "break_even_value": "{years} ans et {months} mois",
        "break_even_never": "Jamais sur l'horizon",
        "break_even_now": "Dès aujourd'hui",
        "negative_savings_warning": "L'épargne devient négative dans le scénario {scenario} : le budget ne tient pas.",
        "scenario_rent": "location",
        "scenario_buy": "achat",
        "chart_net_worth": "Patrimoine net",
        "chart_costs": "Coût mensuel du logement",
        "table_title": "Détail annuel",
        "col_year": "Année",
        "col_rent_net_worth": "Patrimoine location",
        "col_buy_net_worth": "Patrimoine achat",
        "col_difference": "Écart achat - location",
        "col_rent_cost": "Coût mensuel location",
        "col_buy_cost": "Coût mensuel achat",
        "col_property_value": "Valeur du bien",
        "col_remaining_principal": "Capital restant dû",
        "col_buy_savings": "Épargne acheteur",
        "rent_label": "Location",
        "buy_label": "Achat",
        "resale_title": "Simulation de revente",
        "resale_year": "Année de revente (après l'achat)",
        "resale_price": "Prix de revente net vendeur (€)",
        "resale_price_help": "Pré-rempli avec le prix d'achat revalorisé de {rate} par an, tant que tu ne le modifies pas.",
        "sale_fees": "Frais de revente",
        "net_proceeds": "Net encaissé après remboursement du prêt",
        "capital_gain": "Plus-value (revente - coût d'acquisition)",
        "owner_outlay": "Total déboursé en achat jusqu'à la revente",
        "owner_outlay_help": "Apport + mensualités + assurance + charges + taxe foncière + entretien.",
        "rent_outlay": "Total des loyers sur la même période",
        "buy_wealth_at_sale": "Patrimoine achat après la revente",
        "rent_wealth_at_sale": "Patrimoine location à la même date",
        "resale_verdict_buy": "Acheter puis revendre au bout de {years} ans te laisse {amount} de plus que louer.",
        "resale_verdict_rent": "Louer t'aurait laissé {amount} de plus qu'acheter puis revendre au bout de {years} ans.",
        "resale_negative_proceeds": "Le prix de revente ne couvre pas les frais et le capital restant dû : il faut remettre {amount} de ta poche.",
        "assumptions": (
            "Hypothèses : patrimoine achat = valeur du bien moins frais de revente moins capital "
            "restant dû plus épargne. Chaque mois, chaque scénario épargne revenu moins dépenses "
            "moins coût du logement, les dépenses de vie étant déduites de l'épargne "
            "actuelle en location. Pas de fiscalité sur l'épargne ni sur la plus-value."
        ),
    },
    "en": {
        "title": "Rent or buy?",
        "subtitle": "Compare how your net worth evolves when renting versus buying.",
        "language": "Language",
        "section_household": "Household",
        "total_savings": "Total savings (€)",
        "savings_rate": "Annual net return on savings (%)",
        "monthly_income": "Monthly net income before income tax (€)",
        "monthly_income_help": "Used for the debt ratio and to grow savings with income growth.",
        "income_growth": "Annual income growth (%)",
        "monthly_savings": "Current monthly savings (€)",
        "monthly_savings_help": "What you put aside each month today while renting. Living expenses are derived from it: income - rent - savings.",
        "savings_too_high": "Monthly savings exceed income minus rent.",
        "inflation": "Annual inflation (%)",
        "section_rent": "Renting",
        "monthly_rent": "Monthly rent + charges + insurance (€)",
        "rent_growth": "Annual rent increase (%)",
        "section_purchase": "Buying",
        "price": "Net seller price (€)",
        "notary_fees": "Notary fees (€)",
        "agency_fees": "Agency fees paid by buyer (€)",
        "works": "Renovation works (€)",
        "loan_fees": "Loan file and guarantee fees (€)",
        "down_payment": "Down payment (€)",
        "section_loan": "Mortgage",
        "loan_years": "Duration (years)",
        "loan_rate": "Annual nominal rate (%)",
        "monthly_insurance": "Monthly borrower insurance (€)",
        "section_owner": "Owner costs",
        "condo_fees": "Monthly co-ownership charges (€)",
        "property_tax": "Annual property tax (€)",
        "home_insurance": "Monthly home insurance (€)",
        "annual_maintenance": "Annual maintenance (€)",
        "section_market": "Market and horizon",
        "property_growth": "Annual property price change (%)",
        "resale_fee_rate": "Resale fees (% of value)",
        "horizon_years": "Simulation horizon (years)",
        "acquisition_cost": "Total acquisition cost",
        "loan_amount": "Loan amount",
        "credit_cost": "Credit cost (interest + insurance)",
        "total_outlay": "Total paid over the loan",
        "total_outlay_help": "Down payment + all loan payments + borrower insurance.",
        "monthly_rent_cost": "Monthly cost renting",
        "monthly_buy_cost": "Monthly cost buying",
        "loan_payment_detail": "incl. loan {payment} + insurance {insurance}",
        "debt_ratio": "Debt-to-income ratio",
        "debt_ratio_warning": "Debt-to-income ratio above {limit}: bank financing is unlikely.",
        "break_even": "Buying pays off after",
        "break_even_value": "{years} years and {months} months",
        "break_even_never": "Never within horizon",
        "break_even_now": "Right away",
        "negative_savings_warning": "Savings go negative in the {scenario} scenario: the budget does not hold.",
        "scenario_rent": "renting",
        "scenario_buy": "buying",
        "chart_net_worth": "Net worth",
        "chart_costs": "Monthly housing cost",
        "table_title": "Yearly breakdown",
        "col_year": "Year",
        "col_rent_net_worth": "Net worth renting",
        "col_buy_net_worth": "Net worth buying",
        "col_difference": "Buying minus renting",
        "col_rent_cost": "Monthly cost renting",
        "col_buy_cost": "Monthly cost buying",
        "col_property_value": "Property value",
        "col_remaining_principal": "Outstanding principal",
        "col_buy_savings": "Buyer savings",
        "rent_label": "Renting",
        "buy_label": "Buying",
        "resale_title": "Resale simulation",
        "resale_year": "Resale year (after purchase)",
        "resale_price": "Net seller resale price (€)",
        "resale_price_help": "Prefilled with the purchase price grown by {rate} per year, until you edit it.",
        "sale_fees": "Resale fees",
        "net_proceeds": "Cash left after loan repayment",
        "capital_gain": "Capital gain (resale - acquisition cost)",
        "owner_outlay": "Total paid as owner until resale",
        "owner_outlay_help": "Down payment + loan payments + insurance + charges + property tax + maintenance.",
        "rent_outlay": "Total rent over the same period",
        "buy_wealth_at_sale": "Net worth buying after resale",
        "rent_wealth_at_sale": "Net worth renting at the same date",
        "resale_verdict_buy": "Buying then selling after {years} years leaves you {amount} more than renting.",
        "resale_verdict_rent": "Renting would have left you {amount} more than buying then selling after {years} years.",
        "resale_negative_proceeds": "The resale price does not cover fees and outstanding principal: you must add {amount} from your pocket.",
        "assumptions": (
            "Assumptions: buying net worth = property value minus resale fees minus outstanding "
            "principal plus savings. Each month, each scenario saves income minus expenses minus "
            "housing cost, living expenses being derived from current savings while "
            "renting. No tax on savings or capital gains."
        ),
    },
}


def t(key: str, lang: str) -> str:
    """Translate a UI key.

    Args:
        key: Translation key.
        lang: Language code, falling back to French when unknown.

    Returns:
        The translated text.
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS["fr"])[key]


def format_eur(value: float, lang: str) -> str:
    """Format an amount in euros, rounded to the unit.

    Args:
        value: Amount in euros.
        lang: Language code driving the number format.

    Returns:
        "1 234 €" in French, "€1,234" in English.
    """
    amount = f"{abs(round(value)):,}"
    sign = "-" if round(value) < 0 else ""
    if lang == "en":
        return f"{sign}€{amount}"
    return f"{sign}{amount.replace(',', ' ')} €"


def format_percent(value: float, lang: str) -> str:
    """Format a decimal ratio as a percentage with one decimal.

    Args:
        value: Ratio as a decimal.
        lang: Language code driving the decimal separator.

    Returns:
        "33,3 %" in French, "33.3%" in English.
    """
    text = f"{value * 100:.1f}"
    if lang == "en":
        return f"{text}%"
    return f"{text.replace('.', ',')} %"
