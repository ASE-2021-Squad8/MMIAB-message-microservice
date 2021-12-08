#!/usr/bin/env bash

export FLASK_ENV=testing
rm test.db
pytest -v --cov-report=term-missing
