from app.core.osint_domain_snapshot import build_passive_domain_snapshot
from app.core.osint_passive_sources import (
    PassiveSourceResult,
    fetch_certificate_transparency,
    fetch_rdap_domain,
)


class FakeResponse:
    def __init__(self, status_code=200, payload=None, text=""):
        self.status_code = status_code
        self._payload = payload
        self.text = text

    def json(self):
        if isinstance(self._payload, Exception):
            raise self._payload
        return self._payload


def test_rdap_source_parses_operational_summary(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse(
            payload={
                "ldhName": "example.com",
                "handle": "2336799_DOMAIN_COM-VRSN",
                "status": ["active"],
                "events": [{"eventAction": "registration", "eventDate": "1995-08-14T04:00:00Z"}],
                "entities": [["ignored"], {"roles": ["registrar"], "vcardArray": ["vcard", [["fn", {}, "text", "Example Registrar"]]]}],
            }
        )

    monkeypatch.setattr("app.core.osint_passive_sources.requests.get", fake_get)

    result = fetch_rdap_domain("example.com")

    assert result.status == "READY"
    assert result.summary["ldh_name"] == "example.com"
    assert result.summary["events"]["registration"] == "1995-08-14T04:00:00Z"
    assert result.to_dict()["target_web_request_performed"] is False
    assert result.to_dict()["port_scan_performed"] is False


def test_certificate_transparency_source_deduplicates_domain_names(monkeypatch):
    def fake_get(url, **kwargs):
        return FakeResponse(
            payload=[
                {"name_value": "www.example.com\n*.api.example.com", "issuer_name": "Issuer A"},
                {"name_value": "www.example.com\nnotexample.net", "issuer_name": "Issuer B"},
            ]
        )

    monkeypatch.setattr("app.core.osint_passive_sources.requests.get", fake_get)

    result = fetch_certificate_transparency("example.com")

    assert result.status == "READY"
    assert result.summary["name_count"] == 2
    assert result.summary["names"] == ["api.example.com", "www.example.com"]
    assert result.summary["issuers"] == ["Issuer A", "Issuer B"]


def test_snapshot_can_include_external_passive_sources(monkeypatch):
    monkeypatch.setattr(
        "app.core.osint_domain_snapshot.fetch_external_passive_sources",
        lambda domain: (
            PassiveSourceResult("rdap", "READY", f"https://rdap.org/domain/{domain}", {"ldh_name": domain}),
            PassiveSourceResult(
                "certificate_transparency",
                "READY",
                "https://crt.sh/?q=%25.example.com&output=json",
                {"name_count": 3, "names": ["www.example.com"]},
            ),
        ),
    )

    snapshot = build_passive_domain_snapshot("localhost", record_types=("A",), include_external=True)
    payload = snapshot.to_dict()

    assert payload["external_sources"][0]["source"] == "rdap"
    assert payload["assessment"]["external_source_count"] == 2
    assert payload["assessment"]["rdap_available"] is True
    assert payload["assessment"]["certificate_name_count"] == 3
