import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="energyflip-api-client",
    version="0.3.0",
    author="Cat-Basement",
    author_email="pypi@cat-basement.schoevaars.eu",
    description="Client for EnergyFlip API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DieEneSchrodinger/energyflip-client",
    packages=setuptools.find_packages(),
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Home Automation"
    ],
    python_requires='>=3.12'
)
