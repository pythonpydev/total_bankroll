# This is a special pytest file used for configuration and defining fixtures/hooks.

import pytest

def pytest_addoption(parser):
    """Adds the --num-tests command line option to pytest."""
    parser.addoption(
        "--num-tests",
        action="store",
        default=1,
        type=int,
        help="The number of random hands to select and verify."
    )

def pytest_generate_tests(metafunc):
    """Parametrizes a test to run multiple times based on the --num-tests option."""
    # This hook is called for every test function collected.
    # We check if our test function needs the 'iteration' fixture.
    if "iteration" in metafunc.fixturenames:
        # Get the value provided on the command line (or the default of 1).
        num_tests_to_run = metafunc.config.getoption("num_tests")
        # Parametrize the test to run N times, passing in the iteration number.
        metafunc.parametrize("iteration", range(num_tests_to_run))
