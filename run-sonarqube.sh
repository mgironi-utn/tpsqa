#!/bin/bash

set -e
cd "$(dirname "$0")"

echo "=== Proximity Detector - SonarQube Analysis ==="

if ! command -v sonar-scanner &> /dev/null; then
  echo "Warning: sonar-scanner is not installed."
  echo "Install from: https://docs.sonarqube.org/latest/analysis/scan/sonarscanner/"
  echo "Continuing with code quality checks only..."
  SONAR_AVAILABLE=false
else
  SONAR_AVAILABLE=true
fi

echo "Running pylint..."
if command -v pylint &> /dev/null; then
  pylint src/proximity_detector.py test/test_integration.py --output-format=parseable > pylint-report.txt 2>&1 || true
  echo "Generated pylint-report.txt"
else
  echo "pylint not installed; skipping pylint report"
fi

echo "Generating coverage report..."
if command -v pytest &> /dev/null; then
  pytest --cov=. --cov-report=xml 2> coverage.log || true
  echo "Generated coverage.xml"
else
  echo "pytest not installed; skipping coverage report"
fi

if [ "$SONAR_AVAILABLE" = true ]; then
  echo "Running SonarQube scanner against sonar-project.properties with sonar.host.url defintion"
  sonar-scanner \
    -Dsonar.projectBaseDir=. \
    -Dsonar.sources=. \
    -Dsonar.exclusions=test/**,test_*.py
else
  echo "Skipping SonarQube scanner (not installed)"
fi

echo "=== SonarQube analysis complete ==="
