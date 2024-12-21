import unittest
import sys
import os

# Add the project root directory to the system path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add test files
    suite.addTests(loader.discover(start_dir='tests', pattern='test_*.py'))

    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)