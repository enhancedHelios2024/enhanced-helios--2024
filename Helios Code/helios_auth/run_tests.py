import unittest
from unit_testing_facial_recognition import FacialRecognitionTests

suite = unittest.TestLoader().loadTestsFromTestCase(FacialRecognitionTests)

result = unittest.TextTestRunner().run(suite)

if result.wasSuccessful():
    print("✅ All tests passed successfully:")
    for test_case in suite:
        print(f"  ✅ {test_case.id()} - {test_case.shortDescription()}")
else:
    print("❌ Some tests failed.")
