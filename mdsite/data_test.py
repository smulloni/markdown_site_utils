import datetime
import os
import unittest

from mdsite.data import DB, PathConflict

class DBTests(unittest.TestCase):
    def setUp(self):
        self.data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                     'testdata')
        self.db = DB(self.data_dir)

    def testParseTOML(self):
        result = self.db.get_data('toml')
        self.assertEquals(result['owner']['name'],
                          'Tom Preston-Werner')
        self.assertEquals(result['owner']['dob'],
                          datetime.datetime(1979, 5, 27, 7, 32))

    def testParseYAML(self):
        result = self.db.get_data('yaml')
        self.assertEquals(result['owner']['name'],
                          'YAML Guy')
        self.assertEquals(result['database']['enabled'], True)
        self.assertEquals(result['database']['connection_max'], 5000)

    def testConflict(self):
        with self.assertRaises(PathConflict):
            self.db.get_data("conflict")

if __name__ == '__main__':
    unittest.main()
        
