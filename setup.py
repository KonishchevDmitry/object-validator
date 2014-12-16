"""object-validator installation script."""

from __future__ import unicode_literals

from setuptools import setup
from setuptools.command.test import test as Test


class PyTest(Test):
    def finalize_options(self):
        Test.finalize_options(self)
        self.test_args = ["tests"]
        self.test_suite = True

    def run_tests(self):
        import pytest
        pytest.main(self.test_args)


if __name__ == "__main__":
    with open("README") as readme:
        setup(
            name = "object-validator",
            version = "0.1.2",

            description = readme.readline().strip(),
            long_description = readme.read().strip() or None,
            url = "https://github.com/KonishchevDmitry/object-validator",

            license = "GPL3",
            author = "Dmitry Konishchev",
            author_email = "konishchev@gmail.com",

            classifiers = [
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                "Operating System :: MacOS :: MacOS X",
                "Operating System :: POSIX",
                "Operating System :: Unix",
                "Programming Language :: Python :: 2",
                "Programming Language :: Python :: 3",
                "Topic :: Software Development :: Libraries :: Python Modules",
            ],
            platforms = [ "unix", "linux", "osx" ],

            py_modules = [ "object_validator" ],

            cmdclass = { "test": PyTest },
            tests_require = [ "pytest" ],
        )
