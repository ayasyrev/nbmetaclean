from setuptools import setup


REQUIREMENTS_FILENAME = 'requirements.txt'
REQUIREMENTS_TEST_FILENAME = 'requirements_test.txt'


# Requirements
try:
    with open(REQUIREMENTS_FILENAME, encoding="utf-8") as fh:
        REQUIRED = fh.read().split("\n")
except FileNotFoundError:
    REQUIRED = []

try:
    with open(REQUIREMENTS_TEST_FILENAME, encoding="utf-8") as fh:
        TEST_REQUIRED = fh.read().split("\n")
except FileNotFoundError:
    TEST_REQUIRED = []

# What packages are optional?
EXTRAS = {"test": TEST_REQUIRED}


setup(
    install_requires=REQUIRED,
    extras_require=EXTRAS,
)
