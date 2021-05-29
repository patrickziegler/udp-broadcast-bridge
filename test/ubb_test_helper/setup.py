from setuptools import setup, find_packages


if __name__ == "__main__":
    from ubb_test_helper.main import __version__

    setup(
        version=__version__,
        packages=find_packages(),
        entry_points = {
            "console_scripts": ["ubb_test_helper=ubb_test_helper.main:main"],
        }
    )
