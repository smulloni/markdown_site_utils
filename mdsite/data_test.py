import datetime
import os
import tempfile
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
            datetime.datetime(1979, 5, 27, 7, 32, tzinfo=datetime.UTC).isoformat(),
        )
        self.assertIs(result["owner"]["dob"].tzinfo, datetime.UTC)

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

    def testLastModIsAwareUTC(self):
        for path in ("toml", "nougat"):
            last_mod = self.db.get_data(path)["last_mod"]
            self.assertEqual(last_mod.tzinfo, datetime.UTC)
            fs_path = os.path.join(self.data_dir, path)
            if not os.path.isdir(fs_path):
                fs_path += ".md"
            self.assertAlmostEqual(
                last_mod.timestamp(), os.path.getmtime(fs_path), delta=1e-6
            )

    def testDirectoryLastModComesFromIndexFile(self):
        with tempfile.TemporaryDirectory() as data_dir:
            leaf_dir = os.path.join(data_dir, "a", "b")
            os.makedirs(leaf_dir)
            index_path = os.path.join(leaf_dir, "index.md")
            with open(index_path, "w") as fp:
                fp.write("# Leaf\n")
            # Make the index file and its directory disagree, as they do
            # when index.md is edited in place.
            os.utime(index_path, (1_000_000_000, 1_000_000_000))
            os.utime(leaf_dir, (2_000_000_000, 2_000_000_000))
            db = DB(data_dir)
            expected = datetime.datetime.fromtimestamp(1_000_000_000, tz=datetime.UTC)
            self.assertEqual(db.get_data("/a/b/index")["last_mod"], expected)
            self.assertEqual(db.get_data("/a/b")["last_mod"], expected)


if __name__ == "__main__":
    unittest.main()
