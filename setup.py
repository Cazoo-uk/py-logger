from setuptools import setup
import versioneer
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="cazoo_logger",
    version=versioneer.get_version(),
    url="https://gitlab.com/bobthemighty/py-logger",
    license="MIT",
    author="Bob Gregory",
    author_email="bob.gregory@cazoo.co.uk",
    description="Super-opinionated structured logger for AWS lambda",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=["cazoo_logger"],
    cmdclass=versioneer.get_cmdclass(),
)
