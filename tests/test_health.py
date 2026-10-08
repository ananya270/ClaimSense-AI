"""Unit tests for ClaimSense AI health endpoint."""
import unittest
from backend.app import create_app


class HealthEndpointTestCase(unittest.TestCase):
    """Test health check route and app initialization."""

    def setUp(self):
        self.app = create_app()
        self.client = self.app.test_client()

    def test_health_check_status_code(self):
        """Ensure /api/health returns 200 OK."""
        response = self.client.get("/api/health")
        self.assertEqual(response.status_code, 200)

    def test_health_check_payload(self):
        """Ensure /api/health contains expected fields."""
        response = self.client.get("/api/health")
        data = response.get_json()
        self.assertEqual(data.get("status"), "healthy")
        self.assertEqual(data.get("project"), "ClaimSense AI")
        self.assertIn("version", data)
        self.assertIn("phase", data)
        self.assertIn("timestamp", data)

    def test_frontend_index_route(self):
        """Ensure GET / returns index.html (200 OK)."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ClaimSense AI", response.data)

    def test_404_handling(self):
        """Ensure nonexistent endpoint returns 404 JSON."""
        response = self.client.get("/api/nonexistent")
        self.assertEqual(response.status_code, 404)
        data = response.get_json()
        self.assertIn("error", data)


if __name__ == "__main__":
    unittest.main()
