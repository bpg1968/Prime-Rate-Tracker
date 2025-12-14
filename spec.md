# Prime Rate Tracker (Canada) — spec.md

## Goal

Create a small Python program that fetches the **latest Canadian prime rate** from the **Bank of Canada Valet API** and updates a **SQLite** database with:

1. **Current data**: latest rate + effective date
2. **Historic data**: append a row **only when the rate changes** (new rate + its effective date)

This program is intended to run **daily** via **cron** or **anacron**, so it must be non-interactive, safe, quiet, and idempotent.

---

### Local Git (required immediately)

Codex must:

* Initialise a **local Git repository** (`git init`) as part of project setup.
* Ensure the default branch is named **`main`**.

  * If Git initialises with a different default (e.g., `master`), Codex must rename it to `main`.
* Create a reasonable `.gitignore`.
* Make an **initial commit** once the project skeleton and baseline files are created.

### GitHub (later, only when Brian says it’s ready)

* Brian will create/setup the GitHub repository manually.
* **Until Brian explicitly says GitHub is ready**, Codex must **not**:

  * create a remote
  * push
  * open PRs
  * interact with GitHub in any way

Once Brian says GitHub is ready:

* Codex may help configure the remote and push, using Brian’s instructions.
* The primary branch must remain **`main`**.
* Codex should behave conservatively (no force pushes unless explicitly requested).

### Reminder to update this spec after GitHub is ready

When Brian indicates that the GitHub repository is set up and ready:

* Codex must **remind Brian to update `spec.md`** to reflect that GitHub interactions are now allowed (and note any remote name/branch conventions decided at that time).

### Commit message style (mandatory)

Commit messages must be:

* **Capitalized**
* **Concise**
* **Descriptive**
* Written in **English (Canadian spelling)**

---

## Runtime Assumptions (cron/anacron)

* **Non-interactive**: no prompts, no TUI.
* **Zero output on success** (default).
* Clear **exit codes** on failure (for cron mail/monitoring).
* Safe if run multiple times in a day.
* Prevent concurrent overlapping runs (simple lock; exit immediately if locked).

---

## Data Source

Use Bank of Canada Valet API series **Prime rate**: `V80691311`.

* Latest observation:

  * `GET https://www.bankofcanada.ca/valet/observations/V80691311/json?recent=1`

Parse:

* `date`: `.observations[-1].d` (ISO date string `YYYY-MM-DD`)
* `rate`: `.observations[-1].V80691311.v` (string → float)

---

## Behaviour

### Main behaviour (default)

On each run:

1. Acquire an exclusive process lock (see **Locking**).
2. Fetch latest (`date`, `rate`).
3. Open/create SQLite DB at `--db`.
4. Ensure schema exists.
5. Read existing `current_prime` row (if any).
6. Apply update logic:

   * **No current row yet**:

     * Insert into `current_prime`
     * Insert into `prime_history` (baseline entry)
   * **Rate differs** from stored current rate:

     * Update `current_prime` (`as_of_date`, `rate`, `updated_at`)
     * Insert into `prime_history` (`effective_date`, `rate`, `recorded_at`)
   * **Rate same**:

     * Do **not** insert into history
     * If fetched `date` differs from stored `as_of_date`, update `current_prime.as_of_date` and `updated_at` (date-only change rule)

### Date-only change rule

If the fetched rate is the same but the fetched date differs:

* Update `current_prime.as_of_date`
* Do **not** insert into `prime_history`

### Idempotency

Running repeatedly with the same API data must not create duplicates.

* `prime_history` must enforce `UNIQUE(effective_date)`.

---

## Locking (cron-safe)

* Use an OS-level file lock via `fcntl.flock` (Unix-like systems).
* Lock file path:

  * `<db_path>.lock`
* If lock is already held:

  * Exit **immediately**
  * Exit code: **2**
  * No output unless `--verbose`

---

## Database Schema (SQLite)

### `current_prime` (single-row table)

Fields:

* `id INTEGER PRIMARY KEY CHECK (id = 1)`
* `as_of_date TEXT NOT NULL` (`YYYY-MM-DD`)
* `rate REAL NOT NULL`
* `updated_at TEXT NOT NULL` (UTC ISO-8601, e.g. `2025-12-14T13:12:05Z`)

Rules:

* Always exactly one row once initialised.

### `prime_history`

Fields:

* `id INTEGER PRIMARY KEY AUTOINCREMENT`
* `effective_date TEXT NOT NULL UNIQUE`
* `rate REAL NOT NULL`
* `recorded_at TEXT NOT NULL` (UTC ISO-8601)

---

## CLI / Configuration

Entrypoint:

* `python -m prime_rate_tracker`

Arguments:

* `--db PATH` (default: `data/prime_rates.sqlite3`)
* `--timeout SECONDS` (default: 20)
* `--verbose` (enable debug/info logging)
* `--dry-run` (no DB writes)

### Output rules

* Success: **no output**
* Failure: single concise error message to **stderr**
* Stack traces only when `--verbose` is enabled

---

## Exit Codes

* `0` success
* `2` already running (lock held)
* `10` network error
* `11` parse/validation error
* `20` database error
* `21` filesystem/path error

---

## Error Handling Requirements

* HTTP:

  * Timeout required
  * Non-200 response → error
* JSON:

  * `observations` exists and non-empty
  * `V80691311` exists
  * Rate converts cleanly to float
  * Date matches `YYYY-MM-DD` (basic validation)
* Filesystem/DB:

  * Create DB parent directory if missing
  * Use transactions for writes
  * Schema creation must be idempotent

---

## Python Version & Style

* Target **Python 3.12.3**
* Use type hints where helpful
* Small, readable functions
* No frameworks
* Clear separation of responsibilities

---

## Project Layout (PyCharm-friendly)

```
prime-rate-tracker/
  spec.md
  pyproject.toml
  README.md
  .gitignore
  src/
    prime_rate_tracker/
      __init__.py
      __main__.py
      main.py
      fetcher.py
      db.py
      lock.py
      models.py   # optional
  tests/
    test_db.py
    test_logic.py
    test_fetcher.py
    test_lock.py
  data/
```

---

## Testing

Use `pytest`.

Minimum tests:

* Schema creation on fresh DB
* First run inserts current + history
* Repeat run does not duplicate history
* Rate change updates current + history
* Date-only change updates current only
* Fetcher parsing with mocked JSON
* Lock prevents concurrent execution (exit code 2)

---

## Acceptance Criteria

* Runs cleanly under cron/anacron
* Silent on success
* Correctly tracks prime rate changes
* Safe under concurrent execution
* Clean Git history with sensible commits that follow the commit message style
* No GitHub interaction until Brian explicitly says GitHub is ready
* When GitHub becomes ready, Codex reminds Brian to update this spec accordingly

