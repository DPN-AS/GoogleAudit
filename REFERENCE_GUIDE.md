# GAudit V2 - Comprehensive Reference Guide

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Core Modules](#core-modules)
   - [Main Application](#1-main-application)
   - [Audit Engine](#2-audit-engine)
   - [Database Management](#3-database-management)
   - [Report Generation](#4-report-generation)
4. [Supporting Modules](#supporting-modules)
   - [Authentication](#authentication)
   - [Analytics Tabs](#analytics-tabs)
   - [Utilities](#utilities)
5. [Audit Coverage](#audit-coverage)
6. [Integration Points](#integration-points)
7. [Security Considerations](#security-considerations)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)
10. [Development Guide](#development-guide)

## Overview

GAudit V2 is an advanced security auditing tool designed specifically for Google Workspace environments. It provides comprehensive security assessments across multiple Google Workspace services, helping administrators identify and mitigate security risks. The application features a modern PyQt6-based graphical user interface, modular audit components, and extensive reporting capabilities.

## Architecture

The application follows a modular architecture with clear separation of concerns:

```
GAudit V2/
├── main_window.py                # Main application window and UI controller
├── audit_engine.py               # Core auditing logic
├── audit_visuals.py              # Data visualization components
├── db.py                         # Database schema and helpers
├── report_exporter.py            # Report generation
├── credential_loader.py          # Authentication handling
├── secure_store.py               # Secure credential storage
├── data_validator.py             # Input validation utilities
├── qt_helpers.py                 # PyQt6 UI helper functions
├── report_db.py                  # Database access for reports
├── compare_audits_dialog.py      # Audit comparison UI
├── help_dialog.py                # Application help system
├── create_synthetic_audit.py     # Test data generation
├── api_test_script.py            # API testing utility
│
├── analytics_tabs/              # UI components for different audit areas
│   ├── authentication_analytics_tab.py  # Authentication analysis
│   ├── drive_analytics_tab.py           # Drive security analysis
│   ├── email_security_analytics_tab.py  # Email security analysis
│   ├── group_analytics_tab.py           # Group management analysis
│   └── users_ous_analytics_tab.py       # User and OU analysis
│
└── Reference/                  # Reference and legacy implementations
    ├── GAuditV3.py               # Previous version of main application
    ├── GWAuditV2.py              # Alternative audit implementation
    ├── report_genV3.py           # Legacy report generation
    └── report_generator.py       # Previous report generator
```

## Core Modules

### 1. Main Application (`main_window.py`)

The main application module provides the user interface and coordinates between different components.

#### Key Components:

**MainWindow Class**
- Central controller for the application UI
- Manages tabs, menus, and status bar
- Handles user interactions and orchestrates audit processes
- Provides export and reporting functionality

**ApiValidationThread**
- Runs API validation in a background thread
- Prevents UI freezing during API checks
- Emits signals for validation progress and completion

**ApiValidationStatusDialog**
- Displays API validation status
- Shows detailed error messages for failed API connections
- Provides options to proceed or cancel based on validation results

**RunAuditSettingsDialog**
- Configures audit run parameters
- Options for database handling (create new/use existing)
- Toggle for intensive audit mode

**AuditWorker**
- Executes audit processes in a background thread
- Emits progress updates for UI feedback
- Handles error conditions and timeouts

### 2. Audit Engine (`audit_engine.py`)

The core auditing module containing all security checks and validations.

#### Key Functions:

**API Validation**
- `validate_api_services()`: Verifies API access and required scopes
- Tests connectivity to all required Google APIs
- Returns detailed status for each service

**Audit Functions**
1. **User and OU Audits**
   - `audit_users_and_ous()`: Validates user configurations and OU structures
   - Checks for inactive accounts, password policies, and OU delegation

2. **Authentication Audits**
   - `audit_authentication()`: Reviews authentication methods
   - Validates 2FA enforcement, password policies, and SSO configurations

3. **Privilege Audits**
   - `audit_admin_privileges()`: Examines admin role assignments
   - Identifies excessive privileges and separation of duties issues

4. **Group Audits**
   - `audit_groups()`: Analyzes group settings and memberships
   - Checks external sharing settings and group delegation

5. **Data Security Audits**
   - `audit_drive_data_security()`: Reviews Drive sharing settings
   - Identifies over-shared files and folders
   - Validates sharing restrictions and link sharing settings

6. **Email Security Audits**
   - `audit_email_security()`: Checks Gmail security settings
   - Validates email forwarding, delegation, and IMAP/POP settings

7. **Application Security**
   - `audit_application_security()`: Reviews third-party app access
   - Identifies high-risk applications and OAuth scopes

8. **Logging and Monitoring**
   - `audit_logging_and_alerts()`: Validates security logging configurations
   - Checks for alerting rules and retention policies

9. **Device Management**
   - `audit_mdm_basics()`: Reviews mobile device management settings
   - `audit_chromeos_devices()`: Validates ChromeOS device policies

### 3. Database Management (`db.py`)

Manages the SQLite database for storing audit results.

#### Database Schema:

```sql
-- Audit run metadata
CREATE TABLE run (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    domain TEXT,
    cli_args_json TEXT,
    skipped_services_json TEXT,
    overall_status TEXT
);

-- Individual audit sections
CREATE TABLE section (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    status TEXT,
    duration_s REAL
);

-- Security findings
CREATE TABLE finding (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
    severity TEXT,
    message TEXT
);

-- Statistical data
CREATE TABLE stat (
    section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
    key TEXT,
    value TEXT
);

-- Raw audit data
CREATE TABLE raw_object (
    -- Implementation details
);
```

#### Key Functions:
- `init_db()`: Initializes the database schema
- `create_run()`: Creates a new audit run record
- `finalize_run()`: Marks a run as complete
- `start_section()`/`complete_section()`: Tracks audit section execution
- `insert_finding()`: Records security findings
- `insert_stat()`: Stores statistical data
- `insert_raw()`: Saves raw audit data

### 4. Report Generation (`report_exporter.py`)

Generates comprehensive audit reports in HTML and PDF formats.

#### Features:
- Executive summary with risk overview
- Visual charts for findings distribution
- Detailed findings with severity levels
- Remediation recommendations
- Comparison between audit runs

#### Key Functions:
- `generate_html_report()`: Creates HTML report
- `export_html_report()`: Saves HTML to file
- `export_pdf_report()`: Generates PDF version
- Comparison report functions for trend analysis

## Supporting Modules

### Authentication
- `credential_loader.py`: Manages OAuth2 authentication flow and service account delegation
- `secure_store.py`: Securely stores and retrieves credentials using platform-specific keychains

### Analytics Tabs
Specialized UI components for different audit areas:
- `authentication_analytics_tab.py`: Authentication-related visualizations and security assessments
- `drive_analytics_tab.py`: Drive security metrics and sharing analysis
- `email_security_analytics_tab.py`: Email security status and configuration analysis
- `group_analytics_tab.py`: Group management insights and permission analysis
- `users_ous_analytics_tab.py`: User and organizational unit analysis

### Utilities
- `data_validator.py`: Input validation and data sanitization helpers
- `qt_helpers.py`: PyQt6 UI utilities and common widget implementations
- `report_db.py`: Database access layer for report generation and data retrieval
- `report_exporter.py`: Handles export of audit reports to various formats (HTML/PDF)
- `audit_visuals.py`: Visualization components for audit data presentation
- `compare_audits_dialog.py`: UI and logic for comparing multiple audit results
- `help_dialog.py`: Application help system and documentation browser
- `create_synthetic_audit.py`: Utility for generating test audit data
- `api_test_script.py`: Testing utility for API connectivity and functionality

### Reference Implementations
Located in the `Reference/` directory, these files serve as examples or previous versions:
- `Reference/GAuditV3.py`: Previous version of the main application
- `Reference/GWAuditV2.py`: Alternative implementation of audit functionality
- `Reference/report_genV3.py`: Legacy report generation module
- `Reference/report_generator.py`: Previous version of the report generator

## Audit Coverage

GAudit V2 provides comprehensive coverage of Google Workspace security controls:

### 1. Identity and Access Management
- User account lifecycle management
- Group memberships and nesting
- Organizational unit structure
- Admin role assignments
- Service account management

### 2. Authentication Security
- Multi-factor authentication (MFA) enforcement
- Password policies
- OAuth app permissions
- API access controls
- Session management

### 3. Data Protection
- Drive sharing and permissions
- File exposure analysis
- Data loss prevention (DLP) policies
- Vault retention rules

### 4. Email Security
- Gmail security settings
- Email forwarding rules
- Attachment controls
- Spam and phishing protections
- Email delegation

### 5. Device Security
- Mobile device management (MDM)
- ChromeOS device policies
- Endpoint verification
- Context-aware access controls

### 6. Monitoring and Logging
- Admin activity logs
- Login audit logs
- Alerting configurations
- Security investigation tools

## Integration Points

### Google Workspace APIs
- Admin SDK Directory API
- Admin SDK Reports API
- Gmail API
- Drive API
- Groups Settings API
- Alert Center API

### External Dependencies
- Python 3.8+
- PyQt6 for the GUI
- Google API Client Libraries
- SQLite for data storage
- Matplotlib for reporting charts

## Security Considerations

### Authentication
- Implements OAuth 2.0 with service account delegation
- Supports domain-wide delegation for service accounts
- Securely stores credentials using platform-specific keychains

### Data Protection
- All sensitive data is encrypted at rest
- Database connections use parameterized queries
- Audit logs track all privileged operations

### Access Controls
- Principle of least privilege for API scopes
- Granular permission controls
- Audit trails for all administrative actions

## Deployment

### Prerequisites
- Python 3.8 or higher
- Google Workspace admin access
- Service account with appropriate permissions

### Installation
1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Configure service account credentials
4. Run the application:
   ```
   python main_window.py
   ```

## Troubleshooting

### Common Issues
1. **API Access Denied**
   - Verify service account has required scopes
   - Check domain-wide delegation settings
   - Validate service account key is valid

2. **Permission Errors**
   - Confirm admin privileges
   - Check API access in Google Cloud Console
   - Verify domain-wide delegation is properly configured

3. **Report Generation Failures**
   - Ensure all required Python packages are installed
   - Check write permissions for output directory
   - Verify database connectivity

## Development Guide

### Code Organization
- Follows PEP 8 style guide
- Uses type hints for better code clarity
- Modular design for easy extension

### Adding New Audits
1. Create a new function in `audit_engine.py`
2. Add the audit to the `run_audit()` function
3. Create corresponding UI components if needed
4. Update documentation

### Testing
- Unit tests for core functionality
- Integration tests for API interactions
- UI tests for critical user flows

### Contributing
1. Fork the repository
2. Create a feature branch
3. Submit a pull request
4. Include tests and documentation updates

## License
[Specify License]

## Acknowledgements
- Google Workspace Admin SDK team
- PyQt6 developers
- Open source contributors
