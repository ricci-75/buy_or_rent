# Buy or rent

Streamlit app (French / English) comparing the net worth of renting versus buying a home, month by month, and showing after how long buying pays off.

## Layout

Single page: all inputs in the sidebar, then key figures (loan, credit cost, debt ratio, break-even), charts, yearly table and a resale simulation (net seller price prefilled with the estimate, year, fees) comparing net worth with renting at that date.

## Run

```bash
uv sync
uv run buy-or-rent
# or
uv run streamlit run src/buy_or_rent/app.py
```

## Docker

```bash
docker compose up --build
# or
docker build -t buy-or-rent .
docker run --rm -p 8501:8501 buy-or-rent
```

Then open http://localhost:8501.

## Model

- Loan = price + notary fees + agency fees + works + loan fees - down payment.
- Living expenses = income - current rent - current monthly savings (entered by the user).
- Each month, each scenario saves income - living expenses - housing cost; savings grow at the savings rate.
- Buying net worth = property value x (1 - resale fees) - outstanding principal + savings.
- Break-even = first month from which buying stays ahead of renting.
- No income tax, capital gains tax or early repayment modelling: enter net savings returns and enter monthly savings after income tax.

## Development

```bash
uv run ruff check --fix && uv run ruff format
uv run ty check
uv run pytest
```
