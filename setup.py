from setuptools import setup, find_packages

setup(
    name='integrity_checker',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        # Add your dependencies here
    ],
    scripts=['bin/integrity_checker'],
)
