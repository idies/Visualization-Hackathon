from setuptools import setup

PACKAGE_NAME = 'dashboard_app'
DESCRIPTION = 'Dashboard for hackathon visualization'
AUTHOR = 'Ronan Perry, Darius Irani',
REQUIRED_PACKAGES = [
    'dash==0.35.1',
    'dash-html-components==0.13.4',
    'dash-core-components==0.42.1',
    'dash-table==3.1.11',
]

setup(
    name=PACKAGE_NAME,
    description=DESCRIPTION,
    author=AUTHOR,
    install_requires=REQUIRED_PACKAGES)