import unittest
from tracker import build_url, parse_availability

SAMPLE = {
    "body": {"content": {"pickupMessage": {"stores": [
        {"storeNumber": "R001", "storeName": "Test Store",
         "partsAvailability": {
             "PART1": {"pickupDisplay": "available", "pickupSearchQuote": "Pickup today"},
             "PART2": {"pickupDisplay": "unavailable", "pickupSearchQuote": "Currently unavailable"},
         }},
        {"storeNumber": "R999", "storeName": "Other", "partsAvailability": {}},
    ]}}}
}
MODELS = [{"label": "A", "part_number": "PART1"}, {"label": "B", "part_number": "PART2"}]


class TrackerTests(unittest.TestCase):
    def test_build_url_includes_store_and_parts(self):
        url = build_url("R001", ["P1", "P2"], "80206")
        self.assertIn("store=R001", url)
        self.assertIn("parts.0=P1", url)
        self.assertIn("parts.1=P2", url)
        self.assertIn("location=80206", url)

    def test_parse_filters_to_requested_store(self):
        results = parse_availability(SAMPLE, "R001", MODELS)
        self.assertEqual(len(results), 2)
        self.assertTrue(results[0].available)
        self.assertFalse(results[1].available)
        self.assertEqual(results[0].store_name, "Test Store")

    def test_parse_missing_store_returns_empty(self):
        self.assertEqual(parse_availability(SAMPLE, "R404", MODELS), [])

    def test_parse_handles_empty_payload(self):
        self.assertEqual(parse_availability({}, "R001", MODELS), [])


if __name__ == "__main__":
    unittest.main()
