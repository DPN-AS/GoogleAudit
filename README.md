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

Running the app will create `gaudit.db` in the working directory to store audit results. Basic runtime information is logged to `gaudit.log`.
