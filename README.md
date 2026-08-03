# EnergyFlip client

Client to communicate with the API behind [EnergyFlip](https://www.energyflip.com/).

EnergyFlip is an app and measuring device to monitor the usage of electricity and gas in real time.

[![Build status](httphttps://github.com/DieEneSchrodinger/energyflip-client/actions/workflows/build.yml/badge.svg)](https://github.com/DieEneSchrodinger/energyflip-client/actions)
[![Coverage Status](https://coveralls.io/repos/github/DieEneSchrodinger/energyflip-client/badge.svg?branch=master)](https://coveralls.io/github/DieEneSchrodinger/energyflip-client?branch=master)
[![PyPI version](https://badge.fury.io/py/energyflip-api-client.svg)](https://pypi.org/project/energyflip-api-client/)

## Installation
```bash
pip install energyflip-api-client
```
## Usage

See the [example](examples/example.py) on how to use this library.

## Development

This project uses [pipenv](https://pypi.org/project/pipenv/) for dependency and environment management.

Install dependencies using
```bash
pipenv install --dev
```   
### TODO

Replace use of cumulativeHistory with cumulativeHistoryAggregations, since only the Aggregations part is used.  

## Testing

Run all tests using
```bash
pipenv run pytest
```
## Packaging

Create a package using
```bash
python3 setup.py sdist bdist_wheel
```
This creates a package in `dist`

Upload the package using
```bash
python3 -m twine upload dist/*
```