import urllib2
import time
import unittest

class cron_simulator(unittest.TestCase):

    def test_run(self):
        while True:
            print urllib2.urlopen("http://localhost:8080/overwatch")
            time.sleep(60)