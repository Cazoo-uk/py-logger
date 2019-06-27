from setuptools import setup
import versioneer

setup(
    name="cazoo_logger",
    version=versioneer.get_version(),
    url="https://gitlab.com/bobthemighty/py-logger",
    license="MIT",
    author="Bob Gregory",
    author_email="bob.gregory@cazoo.co.uk",
    description="Super-opinionated structured logger for AWS lambda",
    packages=["cazoo_logger"],
    cmdclass=versioneer.get_cmdclass(),
)
