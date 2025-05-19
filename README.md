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

Running the app will create `gaudit.db` in the working directory. You can override this path by setting the `GAUDIT_DB_PATH` environment variable:

```bash
export GAUDIT_DB_PATH=/path/to/custom.db
python main.py
```
