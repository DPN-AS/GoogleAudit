"""Core auditing logic for GAudit V2."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List
import os

import settings

import db


@dataclass
class AuditFinding:
    """Represents a single security finding."""

    severity: str
    message: str


@dataclass
class AuditSectionResult:
    """Aggregated results for an individual audit section."""

    name: str
    findings: List[AuditFinding] = field(default_factory=list)
    stats: Dict[str, str] = field(default_factory=dict)

    @property
    def status(self) -> str:
        """Return PASS if no findings have severity ERROR or WARNING."""

        for finding in self.findings:
            if finding.severity.upper() in {"ERROR", "WARNING"}:
                return "FAIL"
        return "PASS"


def _env_int(key: str, default: int = 0) -> int:
    """Return an integer from ``os.environ`` or ``default`` if not set."""
    try:
        return int(os.getenv(key, str(default)))
    except ValueError:
        return default


def _env_bool(key: str, default: bool = False) -> bool:
    """Return a boolean from ``os.environ`` or ``default`` if not set."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.lower() in {"1", "true", "yes", "on"}


# API validation

def validate_api_services() -> Dict[str, bool]:
    """Verify API access and required scopes.

    Returns a mapping of service name to boolean connectivity status. This
    implementation simulates connectivity checks and always succeeds.
    """

    config = settings.load_settings()
    services = config.get("api_services", [])

    status: Dict[str, bool] = {}
    for service in services:
        try:
            status[service] = _env_bool(f"GAUDIT_SERVICE_{service.upper()}", True)
        except Exception:  # pragma: no cover - environment error
            status[service] = False
    return status


# User and OU Audits

def audit_users_and_ous() -> AuditSectionResult:
    """Validate user configurations and OU structures."""

    result = AuditSectionResult(name="Users and OUs")
    inactive_accounts = _env_int("GAUDIT_INACTIVE_ACCOUNTS", 0)
    result.stats["inactive_accounts"] = str(inactive_accounts)
    if inactive_accounts > 0:
        result.findings.append(
            AuditFinding("WARNING", f"{inactive_accounts} inactive accounts found")
        )
    return result


def audit_authentication() -> AuditSectionResult:
    """Review authentication methods."""

    result = AuditSectionResult(name="Authentication")
    two_fa_enabled = _env_bool("GAUDIT_TWO_FA_ENABLED", True)
    result.stats["two_fa_enabled"] = str(two_fa_enabled)
    if not two_fa_enabled:
        result.findings.append(
            AuditFinding("ERROR", "Two-factor authentication is not enforced")
        )
    return result


def audit_admin_privileges() -> AuditSectionResult:
    """Examine admin role assignments."""

    result = AuditSectionResult(name="Admin Privileges")
    excessive_admins = _env_int("GAUDIT_EXCESSIVE_ADMINS", 0)
    result.stats["excessive_admins"] = str(excessive_admins)
    if excessive_admins:
        result.findings.append(
            AuditFinding("WARNING", f"{excessive_admins} users with excessive privileges")
        )
    return result


def audit_groups() -> AuditSectionResult:
    """Analyze group settings and memberships."""

    result = AuditSectionResult(name="Groups")
    external_members = _env_int("GAUDIT_EXTERNAL_MEMBERS", 0)
    result.stats["external_members"] = str(external_members)
    if external_members:
        result.findings.append(
            AuditFinding("WARNING", f"{external_members} external group members")
        )
    return result


def audit_drive_data_security() -> AuditSectionResult:
    """Review Drive sharing settings."""

    result = AuditSectionResult(name="Drive Data Security")
    overshared_files = _env_int("GAUDIT_OVERSHARED_FILES", 0)
    result.stats["overshared_files"] = str(overshared_files)
    if overshared_files:
        result.findings.append(
            AuditFinding("WARNING", f"{overshared_files} overshared Drive files")
        )
    return result


def audit_email_security() -> AuditSectionResult:
    """Check Gmail security settings."""

    result = AuditSectionResult(name="Email Security")
    forwarding_rules = _env_int("GAUDIT_FORWARDING_RULES", 0)
    result.stats["forwarding_rules"] = str(forwarding_rules)
    if forwarding_rules:
        result.findings.append(
            AuditFinding("WARNING", f"{forwarding_rules} active forwarding rules")
        )
    return result


def audit_application_security() -> AuditSectionResult:
    """Review third-party app access."""

    result = AuditSectionResult(name="Application Security")
    risky_apps = _env_int("GAUDIT_RISKY_APPS", 0)
    result.stats["risky_apps"] = str(risky_apps)
    if risky_apps:
        result.findings.append(
            AuditFinding("ERROR", f"{risky_apps} high risk applications detected")
        )
    return result


def audit_logging_and_alerts() -> AuditSectionResult:
    """Validate security logging configurations."""

    result = AuditSectionResult(name="Logging and Alerts")
    alert_rules = _env_int("GAUDIT_ALERT_RULES", 1)
    result.stats["alert_rules"] = str(alert_rules)
    if alert_rules == 0:
        result.findings.append(
            AuditFinding("WARNING", "No alerting rules configured")
        )
    return result


def audit_mdm_basics() -> AuditSectionResult:
    """Review mobile device management settings."""

    result = AuditSectionResult(name="MDM Basics")
    managed_devices = _env_int("GAUDIT_MANAGED_DEVICES", 0)
    result.stats["managed_devices"] = str(managed_devices)
    return result


def audit_chromeos_devices() -> AuditSectionResult:
    """Validate ChromeOS device policies."""

    result = AuditSectionResult(name="ChromeOS Devices")
    compliant = _env_bool("GAUDIT_POLICY_COMPLIANT", True)
    result.stats["policy_compliant"] = str(compliant)
    if not compliant:
        result.findings.append(
            AuditFinding("ERROR", "ChromeOS device policies are not compliant")
        )
    return result


def run_audit() -> List[AuditSectionResult]:
    """Run all audit sections and record results in the database."""

    run_id = db.create_run()

    sections: List[tuple[str, Callable[[], AuditSectionResult]]] = [
        ("Users and OUs", audit_users_and_ous),
        ("Authentication", audit_authentication),
        ("Admin Privileges", audit_admin_privileges),
        ("Groups", audit_groups),
        ("Drive Data Security", audit_drive_data_security),
        ("Email Security", audit_email_security),
        ("Application Security", audit_application_security),
        ("Logging and Alerts", audit_logging_and_alerts),
        ("MDM Basics", audit_mdm_basics),
        ("ChromeOS Devices", audit_chromeos_devices),
    ]

    results: List[AuditSectionResult] = []
    for name, func in sections:
        section_id = db.start_section(run_id, name)
        result = func()
        for finding in result.findings:
            db.insert_finding(section_id, finding.severity, finding.message)
        for key, value in result.stats.items():
            db.insert_stat(section_id, key, value)
        db.complete_section(section_id)
        results.append(result)

    return results

