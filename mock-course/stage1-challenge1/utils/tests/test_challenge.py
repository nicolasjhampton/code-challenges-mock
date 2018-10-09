import unittest
import challenge


class TestDependsOn(unittest.TestCase):

    def test_dependencies_present(self):

        class SampleFirst:
            pass

        @challenge.depends_on(SampleFirst)
        class SampleSecond:
            pass

        @challenge.depends_on(SampleFirst, SampleSecond)
        class SampleThird:
            pass

        self.assertIn(SampleFirst, SampleSecond._dependencies)
        self.assertIn(SampleFirst, SampleThird._dependencies)
        self.assertIn(SampleSecond, SampleThird._dependencies)


class TestResultsFromTestCases(unittest.TestCase):

    class SampleNeverWorks(unittest.TestCase):

        def test_no(self):
            self.assertTrue(False, msg="Canary Never Works")

    class SamplePasses(unittest.TestCase):

        def test_good_to_go(self):
            pass

    @challenge.depends_on(SampleNeverWorks)
    class SampleDependsFail(unittest.TestCase):

        def test_sure_why_not(self):
            pass

    @challenge.depends_on(SamplePasses)
    class SampleDependsPassesButFails(unittest.TestCase):

        def test_no_way(self):
            self.assertTrue(False, msg="Canary Depends Passed But Failure")

    def test_failure_present(self):
        output, results = challenge.results_from_test_cases([self.SampleNeverWorks])

        self.assertIn("Canary Never Works", output)
        self.assertEqual(len(results), 1)
        self.assertFalse(results[0].wasSuccessful())

    def test_passing_works(self):
        output, results = challenge.results_from_test_cases([self.SamplePasses])

        self.assertEqual(1, len(results))
        self.assertTrue(results[0].wasSuccessful())

    def test_dependency_fails(self):
        # NOTE: Not passing dependency SampleNeverWorks, but its results are here
        output, results = challenge.results_from_test_cases([self.SampleDependsFail])

        self.assertIn("Canary Never Works", output)
        self.assertEqual(1, len(results))
        self.assertFalse(results[0].wasSuccessful())

    def test_dependency_passes(self):
        output, results = challenge.results_from_test_cases([self.SampleDependsPassesButFails])

        self.assertIn("Canary Depends Passed But Failure", output)
        self.assertEqual(2, len(results))
        # One True, One False expected...order indeterminate
        states = [result.wasSuccessful() for result in results]
        self.assertTrue(any(states))
        self.assertFalse(all(states))
