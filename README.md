# Prime Rate Tracker (Canada)

A small Python utility that fetches the latest Canadian prime rate from the Bank of Canada Valet API and records changes in a SQLite database. It is designed to run quietly under cron/anacron and maintain a history of rate changes.

## Development

- Python 3.12 recommended.
- Create a virtual environment and install tooling:
  - `python -m venv .venv`
  - `source .venv/bin/activate`
  - `pip install -e .[test]`
- Run tests with `pytest`.
- Entry point will be `python -m prime_rate_tracker` once the implementation is complete.

See `spec.md` for the detailed behaviour requirements and acceptance criteria.

