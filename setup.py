from setuptools import setup, find_packages

setup(
    name='overture-sdk',
    version='0.2.0',
    description="A Python library interface with SONG services",
    packages=find_packages(),
    install_requires=['requests>=2.20.0', 'dataclasses>=0.4'],
)