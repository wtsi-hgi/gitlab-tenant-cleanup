from setuptools import setup, find_packages

try:
    from pypandoc import convert
    def read_markdown(file: str) -> str:
        return convert(file, "rst")
except ImportError:
    def read_markdown(file: str) -> str:
        return open(file, "r").read()

setup(
    name="sequencescape-db",
    version="0.2.0",
    author="Colin Nolan",
    author_email="colin.nolan@sanger.ac.uk",
    packages=find_packages(exclude=["tests"]),
    install_requires=[x for x in open("requirements.txt").read().splitlines() if "://" not in x],
    dependency_links=[x for x in open("requirements.txt").read().splitlines() if "://" in x],
    url="https://github.com/wtsi-hgi/python-sequencescape-client",
    license="MIT",
    description="Python client for using a Sequencescape database.",
    long_description=read_markdown("README.md"),
    test_suite="hgijson.tests"
)
