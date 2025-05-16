import unittest
from unittest.mock import patch
from app import app

class TestApp(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_version(self):
        response = self.client.get("/version")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json, {"version": "0.0.1"})

    @patch("app.get_average_temperature")
    def test_temperature_success(self, mock_temp):
        mock_temp.return_value = 22.7
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 200)
        self.assertIn("temperature", response.json)
        self.assertEqual(response.json["temperature"], 22.7)

    @patch("app.get_average_temperature")
    def test_temperature_failure(self, mock_temp):
        mock_temp.return_value = None
        response = self.client.get("/temperature")
        self.assertEqual(response.status_code, 503)
        self.assertIn("error", response.json)

if __name__ == "__main__":
    unittest.main()
