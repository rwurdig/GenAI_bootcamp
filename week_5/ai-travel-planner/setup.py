from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="AI-TRAVEL-PLANNER",
    version="0.1",
    author="rwurdig2",
    packages=find_packages(),
    install_requires=requirements,
)
