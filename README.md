# Prime Rate Tracker (Canada)

This project is largely unmaintained. Please read the [Code of Conduct](CODE_OF_CONDUCT.md) before filing issues or contacting the author.

A small Python utility that fetches the latest Canadian prime rate from the Bank of Canada Valet API and records changes in a SQLite database. It is designed to run quietly under cron/anacron and maintain a history of rate changes.

## Local installation

1. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `source .venv/bin/activate`
2. Install the package:
   - `python -m pip install .`
3. Run the tracker (creates `data/prime_rates.sqlite3` by default):
   - `python -m prime_rate_tracker`

## Development

- Python 3.12 recommended.
- Create a virtual environment and install tooling:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `python -m pip install -e ".[test]"`
- Run tests with `python -m pytest`.
- Entry point: `python -m prime_rate_tracker`.

See `spec.md` for the detailed behaviour requirements and acceptance criteria.
