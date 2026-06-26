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
  pylint proximity_detector.py test_integration.py --output-format=parseable > pylint-report.txt 2>&1 || true
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

SONAR_HOST_URL=${SONAR_HOST_URL:-http://localhost:9000}
SONAR_TOKEN=${SONAR_TOKEN:-sqa_393252ea720ef02413c509e2512e91a10335a527}

if [ "$SONAR_AVAILABLE" = true ]; then
  echo "Running SonarQube scanner against $SONAR_HOST_URL..."
  sonar-scanner \
    -Dsonar.host.url="$SONAR_HOST_URL" \
    -Dsonar.login="$SONAR_TOKEN" \
    -Dsonar.projectBaseDir=. \
    -Dsonar.sources=. \
    -Dsonar.exclusions=test_*.py
else
  echo "Skipping SonarQube scanner (not installed)"
fi

echo "=== SonarQube analysis complete ==="
