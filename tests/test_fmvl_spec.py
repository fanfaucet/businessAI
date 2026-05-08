from __future__ import annotations

import json
import unittest
from pathlib import Path


class FMVLOpenAPISpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.spec_path = Path("docs/fmvl/openapi.json")
        cls.spec = json.loads(cls.spec_path.read_text())

    def test_openapi_primary_artifact_declares_required_endpoints(self) -> None:
        self.assertEqual(self.spec["openapi"], "3.0.3")
        expected_paths = {
            "/ingest/observation",
            "/analyze/disagreement-field",
            "/metrics/trust-map",
            "/audit/lineage-trace",
            "/advisory/interpretation",
        }
        self.assertEqual(set(self.spec["paths"]), expected_paths)

    def test_all_operations_are_advisory_only_and_control_free(self) -> None:
        for path, methods in self.spec["paths"].items():
            for method, operation in methods.items():
                with self.subTest(path=path, method=method):
                    self.assertTrue(operation.get("x-advisory-only"))
                    self.assertNotIn("delete", method.lower())
                    self.assertNotIn("patch", method.lower())
                    if path == "/audit/lineage-trace":
                        self.assertTrue(operation.get("x-read-only"))
                    else:
                        self.assertTrue(operation.get("x-no-control-pathway"))

    def test_required_schemas_exist_with_advisory_outputs(self) -> None:
        schemas = self.spec["components"]["schemas"]
        for schema_name in [
            "Observation",
            "Sensor",
            "ConsensusGapField",
            "TrustVector",
            "LineageTrace",
            "AdvisoryInterpretation",
        ]:
            self.assertIn(schema_name, schemas)

        for schema_name in ["ConsensusGapField", "TrustMapResponse", "AdvisoryInterpretation", "ErrorResponse"]:
            advisory = schemas[schema_name]["properties"]["advisory_only"]
            self.assertEqual(advisory["enum"], [True])

    def test_security_and_rate_limits_are_declared(self) -> None:
        security_schemes = self.spec["components"]["securitySchemes"]
        self.assertIn("ApiKeyAuth", security_schemes)
        self.assertIn("SignedTokenAuth", security_schemes)
        for methods in self.spec["paths"].values():
            for operation in methods.values():
                self.assertIn("x-rate-limit", operation)
                self.assertIn("limit", operation["x-rate-limit"])
                self.assertIn("window", operation["x-rate-limit"])

    def test_technical_spec_sections_are_present(self) -> None:
        text = Path("docs/fmvl/technical_specification.md").read_text()
        required_headings = [
            "## 2. OpenAPI 3.0 Primary Artifact",
            "## 3. Data Model Specification",
            "## 4. Event Stream Architecture (ESDS-Style)",
            "## 5. Security and Governance Model",
            "## 6. TRL Justification",
            "## 7. NASA ESTO / ESDS Alignment",
            "## 8. Comparative Prior Art",
        ]
        for heading in required_headings:
            self.assertIn(heading, text)


if __name__ == "__main__":
    unittest.main()
