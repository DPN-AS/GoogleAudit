"""Testing utility for Google API connectivity.

This module provides a very small script used during development to verify
that application credentials are valid and that the required Google Workspace
APIs can be reached.  The implementation is intentionally lightweight so the
script can run independently of the rest of the application stack.

The APIs tested are derived from the project reference guide:

- Admin SDK Directory API
- Admin SDK Reports API
- Gmail API
- Drive API
- Alert Center API

The script attempts a simple read-only call against each service and prints
the results to stdout.
"""

from __future__ import annotations

from typing import Callable


def _require_google_client() -> "module":
    """Import :mod:`googleapiclient.discovery` or raise a helpful error."""

    try:  # Deferred import so the script can fail gracefully if missing
        from googleapiclient import discovery
    except ModuleNotFoundError as exc:  # pragma: no cover - runtime dependency
        raise RuntimeError(
            "google-api-python-client is required to run the API tests"
        ) from exc

    return discovery


def run_api_tests() -> None:
    """Run connectivity tests against Google APIs."""

    discovery = _require_google_client()

    try:
        from credential_loader import load_credentials
    except Exception as exc:  # pragma: no cover - environment configuration
        raise RuntimeError("Unable to import credential loader") from exc

    creds = load_credentials()
    if creds is None:
        print("Unable to load credentials")
        return

    ServiceSpec = tuple[str, str, Callable[["object"], None]]
    services: dict[str, ServiceSpec] = {
        "Admin SDK Directory API": (
            "admin",
            "directory_v1",
            lambda svc: svc.users()
            .list(customer="my_customer", maxResults=1)
            .execute(),
        ),
        "Admin SDK Reports API": (
            "admin",
            "reports_v1",
            lambda svc: svc.activities()
            .list(userKey="all", applicationName="login", maxResults=1)
            .execute(),
        ),
        "Gmail API": (
            "gmail",
            "v1",
            lambda svc: svc.users().getProfile(userId="me").execute(),
        ),
        "Drive API": (
            "drive",
            "v3",
            lambda svc: svc.about().get(fields="user").execute(),
        ),
        "Alert Center API": (
            "alertcenter",
            "v1beta1",
            lambda svc: svc.alerts().list(pageSize=1).execute(),
        ),
    }

    results: dict[str, bool] = {}
    for name, (service_name, version, test_fn) in services.items():
        print(f"Testing {name}...", end="", flush=True)
        try:
            service = discovery.build(
                service_name, version, credentials=creds, cache_discovery=False
            )
            test_fn(service)
            print("OK")
            results[name] = True
        except Exception as exc:  # pragma: no cover - network failures
            print(f"FAILED ({exc})")
            results[name] = False

    print("\nSummary:")
    for name, ok in results.items():
        status = "SUCCESS" if ok else "FAIL"
        print(f" - {name}: {status}")
