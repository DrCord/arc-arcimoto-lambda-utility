import unittest
import xmlrunner

if __name__ == "__main__":
    xmlrunner.XMLTestRunner(output='test-reports').run(
        unittest.TestLoader().discover("."))
