# GAudit V2

GAudit provides a simple GUI for auditing Google Workspace environments. The implementation is minimal but demonstrates the project structure described in `REFERENCE_GUIDE.md`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the application:
   ```bash
   python main.py
   ```

Running the app will create `gaudit.db` in the working directory to store audit results.

## Security

GAudit stores OAuth credentials securely using the system keychain via
`secure_store.py`. Credentials are automatically loaded when validating APIs or
running audits. API interactions are throttled with a simple rate limiter to
avoid exceeding Google Workspace quotas.
