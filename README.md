# GAudit V2

GAudit provides a simple GUI for auditing Google Workspace environments. The implementation is minimal but demonstrates the project structure described in `REFERENCE_GUIDE.md`.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   PDF export requires the `wkhtmltopdf` binary. On Debian/Ubuntu you can install it with:
   ```bash
   sudo apt-get install wkhtmltopdf
   ```

2. Run the application:
   ```bash
python main.py
```


Running the app will create `gaudit.db` in the working directory. You can override this path by setting the `GAUDIT_DB_PATH` environment variable:

```bash
export GAUDIT_DB_PATH=/path/to/custom.db
python main.py
```

## Configuration

GAudit reads additional settings from a JSON configuration file. By default the
file `config.json` in the working directory is used. You can specify an
alternative path via the `GAUDIT_CONFIG` environment variable. If the file does
not exist, a default one will be created automatically.

Example configuration structure:

```json
{
  "api_services": [
    "admin_sdk",
    "drive_api",
    "gmail_api",
    "groups_settings_api"
  ]
}
```

The `validate_api_services()` helper consults environment variables named
`GAUDIT_SERVICE_<SERVICE>` to simulate connectivity to individual APIs during
testing.
