import datetime
import os
import unittest

from mdsite.data import DB, PathConflict


class DBTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "testdata"
        )
        self.db = DB(self.data_dir)

    def testParseTOML(self):
        result = self.db.get_data("toml")
        self.assertEqual(result["owner"]["name"], "Tom Preston-Werner")
        self.assertEqual(
            result["owner"]["dob"].isoformat(),
            datetime.datetime(
                1979, 5, 27, 7, 32, tzinfo=datetime.timezone.utc
            ).isoformat(),
        )

    def testParseYAML(self):
        result = self.db.get_data("yaml")
        self.assertEqual(result["owner"]["name"], "YAML Guy")
        self.assertEqual(result["database"]["enabled"], True)
        self.assertEqual(result["database"]["connection_max"], 5000)

    def testParseJSON(self):
        result = self.db.get_data("json")
        self.assertEqual(result["title"], "Well, Well!")

    def testConflict(self):
        with self.assertRaises(PathConflict):
            self.db.get_data("conflict")

    def testConfig(self):
        config = self.db.get_config("/")
        self.assertEqual(config["template"], "base.tmpl")
        config = self.db.get_config("/nougat")
        self.assertEqual(config["template"], "dessert.tmpl")

    def testListing(self):
        data = self.db.get_data("/")
        self.assertEqual(
            data["listing"],
            (["conflict", "nougat"], ["conflict", "json", "nohead", "toml", "yaml"]),
        )

    def testRecursiveListing(self):
        listing = self.db.get_recursive_listing("/")
        self.assertEqual(
            listing,
            {
                "": (
                    ["conflict", "nougat"],
                    ["conflict", "json", "nohead", "toml", "yaml"],
                ),
                "conflict": ([], ["index"]),
                "nougat": ([], []),
            },
        )

    def testRecursiveData(self):
        all_data = self.db.get_recursive_data("/nougat")
        self.assertEqual(set(all_data), {"nougat"})

    def testNoDataHeader(self):
        data = self.db.get_data("nohead")
        self.assertTrue(data.get("content", ""))
        self.assertIn("This markdown file", data.get("content", ""))



if __name__ == "__main__":
    unittest.main()
