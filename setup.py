from setuptools import setup


REQUIREMENTS_TEST_FILENAME = "requirements_test.txt"
REQUIREMENTS_DEV_FILENAME = "requirements_dev.txt"


def load_requirements(filename: str) -> list[str]:
    """Load requirements from file"""
    try:
        with open(filename, encoding="utf-8") as fh:
            return fh.read().splitlines()
    except FileNotFoundError:
        return []


TEST_REQUIRED = load_requirements(REQUIREMENTS_TEST_FILENAME)
DEV_REQUIRED = load_requirements(REQUIREMENTS_DEV_FILENAME)


# What packages are optional?
EXTRAS = {
    "test": TEST_REQUIRED,
    "dev": DEV_REQUIRED + TEST_REQUIRED,
}


setup(
    extras_require=EXTRAS,
)
