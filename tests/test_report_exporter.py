import types
import unittest
from unittest import mock

import report_exporter


class ReportExporterTests(unittest.TestCase):
    def test_export_pdf_missing_wkhtmltopdf(self) -> None:
        fake_pdfkit = types.SimpleNamespace(
            from_string=mock.Mock(side_effect=OSError("No wkhtmltopdf executable found"))
        )
        with mock.patch.dict("sys.modules", {"pdfkit": fake_pdfkit}):
            with mock.patch("report_exporter.report_db.fetch_last_run", return_value={}):
                with self.assertRaises(RuntimeError) as ctx:
                    report_exporter.export_pdf_report("out.pdf")
        self.assertIn("wkhtmltopdf", str(ctx.exception))


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()
