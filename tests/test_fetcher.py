import json

from prime_rate_tracker.fetcher import OBSERVATION_URL, fetch_latest_prime
from prime_rate_tracker.errors import ParseError


class FakeResponse:
    def __init__(self, payload: dict, status: int = 200):
        self.payload = payload
        self.status = status

    def read(self) -> bytes:
        return json.dumps(self.payload).encode()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


def test_fetcher_parses_latest_observation(monkeypatch) -> None:
    payload = {
        "observations": [
            {
                "d": "2024-05-01",
                "V80691311": {"v": "7.2"},
            }
        ]
    }

    def fake_urlopen(request, timeout):
        assert request.full_url == OBSERVATION_URL
        return FakeResponse(payload)

    monkeypatch.setattr("urllib.request.urlopen", fake_urlopen)

    prime = fetch_latest_prime(timeout=1.0)

    assert prime.date == "2024-05-01"
    assert prime.rate == 7.2


def test_fetcher_raises_on_missing_data(monkeypatch) -> None:
    monkeypatch.setattr(
        "urllib.request.urlopen",
        lambda *args, **kwargs: FakeResponse({"observations": []}),
    )

    try:
        fetch_latest_prime(timeout=1.0)
    except ParseError as exc:
        assert "No observations" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("ParseError not raised")

