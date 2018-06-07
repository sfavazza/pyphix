"""Create and run all test suites."""

import os
import sys
import unittest as utst
import importlib as imp

# add module under test (mut) to sys.path for test purposes only
ORIG_SYS_PATH = sys.path.copy()
sys.path.insert(0, os.path.abspath('../pyphix'))

import test_fixfmt as t_fmt     # noqa
import test_fixnum as t_num     # noqa

# refresh test definitions
imp.reload(t_fmt)
imp.reload(t_num)


# **
# *** CREATE TEST SUITES
# **
def test_suite_fixfmt():
    """Create FixFmt test suite."""

    # create test suite object
    test_suite = utst.TestSuite()

    # add tests
    test_suite.addTest(t_fmt.TestFixFmtMethods('test_properties'))

    return test_suite


def test_suite_fixnum():
    """Create FixNum test suite."""

    # create test suite
    test_suite = utst.TestSuite()

    # add tests
    for test_name in ['test_known_signed_round',
                      'test_known_unsigned_round',
                      'test_known_signed_overflow',
                      'test_known_unsigned_overflow',
                      'test_change_fix']:
        test_suite.addTest(t_num.TestFixRoundOverMethods(test_name))

    for test_name in ['test_public_methods',
                      'test_container_methods',
                      'test_generator',
                      'test_operators',
                      'test_logic_operations']:
        test_suite.addTest(t_num.TestFixNumMethods(test_name))

    return test_suite


if __name__ == '__main__':
    # Main test runner script
    # Giving -v or --verbose as script argument print more information about the tests being run

    # define test enable switches
    ENABLE_TEST_ALL = True
    ENABLE_TEST_FIXFMT = False
    ENABLE_TEST_FIXNUM = False

    # define test runner and verbosity
    VERBOSITY_LEVEL = 1
    try:
        if sys.argv[1] in ['-v', '--verbose']:
            VERBOSITY_LEVEL = 2
    except IndexError:
        pass                    # no given arguments

    TEST_RUNNER = utst.TextTestRunner(verbosity=VERBOSITY_LEVEL, failfast=True)

    try:
        TEST_RESULT = True
        if ENABLE_TEST_ALL or ENABLE_TEST_FIXFMT:
            TEST_RESULT &= TEST_RUNNER.run(test_suite_fixfmt()).wasSuccessful()

        if ENABLE_TEST_ALL or ENABLE_TEST_FIXNUM:
            TEST_RESULT &= TEST_RUNNER.run(test_suite_fixnum()).wasSuccessful()

        res_fail = 'FAIL'
        res_success = 'SUCCESS'
        print(f"Final test result: {res_success if TEST_RESULT else res_success}")

    finally:
        # clean the namespace
        del t_fmt
        del t_num

        # set path back to original one
        sys.path = ORIG_SYS_PATH.copy()
