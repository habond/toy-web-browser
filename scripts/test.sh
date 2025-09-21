#!/bin/bash
# Testing script for the toy web browser project

set -e

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Default values
COVERAGE=false
VERBOSE=false
FAST=false
PATTERN=""
HTML_REPORT=false

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -c, --coverage     Run tests with coverage report"
    echo "  -v, --verbose      Run tests with verbose output"
    echo "  -f, --fast         Run only fast tests (skip integration tests)"
    echo "  -p, --pattern      Run tests matching pattern (e.g., 'test_config')"
    echo "  -h, --html         Generate HTML coverage report"
    echo "  --help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  ./scripts/test.sh                    # Run all tests"
    echo "  ./scripts/test.sh -c                # Run tests with coverage"
    echo "  ./scripts/test.sh -c -h             # Run tests with HTML coverage report"
    echo "  ./scripts/test.sh -v                # Run tests with verbose output"
    echo "  ./scripts/test.sh -f                # Run only fast unit tests"
    echo "  ./scripts/test.sh -p test_config    # Run only config tests"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -f|--fast)
            FAST=true
            shift
            ;;
        -p|--pattern)
            PATTERN="$2"
            shift 2
            ;;
        -h|--html)
            HTML_REPORT=true
            COVERAGE=true  # HTML report implies coverage
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

echo "🧪 Running toy web browser tests..."

# Build pytest command
PYTEST_CMD="python -m pytest"

# Add test paths - prioritize working tests
if [ "$FAST" = true ]; then
    echo "⚡ Running fast tests only..."
    TEST_PATHS="tests/test_*.py tests/unit/test_config.py tests/unit/elements/test_element_factory.py tests/unit/test_font_manager.py tests/unit/test_layout_utils_simple.py tests/unit/test_renderer_simple.py"
else
    echo "🔄 Running all working tests..."
    # Dynamic approach: include entire directories
    # This automatically picks up new tests without manual maintenance
    TEST_PATHS="tests/integration/ tests/test_*.py tests/unit/"
fi

# Add pattern matching
if [ -n "$PATTERN" ]; then
    echo "🔍 Running tests matching pattern: $PATTERN"
    PYTEST_CMD="$PYTEST_CMD -k $PATTERN"
fi

# Add verbose output
if [ "$VERBOSE" = true ]; then
    echo "📝 Using verbose output..."
    PYTEST_CMD="$PYTEST_CMD -v"
fi

# Add coverage options
if [ "$COVERAGE" = true ]; then
    echo "📊 Generating coverage report..."
    PYTEST_CMD="$PYTEST_CMD --cov=src --cov-report=term-missing"

    if [ "$HTML_REPORT" = true ]; then
        echo "🌐 Generating HTML coverage report..."
        PYTEST_CMD="$PYTEST_CMD --cov-report=html"
    fi
fi

# Run the tests
echo "🚀 Executing: $PYTEST_CMD $TEST_PATHS"
$PYTEST_CMD $TEST_PATHS

# Show coverage report location if HTML was generated
if [ "$HTML_REPORT" = true ]; then
    echo ""
    echo "📊 HTML coverage report generated at: htmlcov/index.html"
    echo "   Open with: open htmlcov/index.html"
fi

echo "✅ Tests completed successfully!"
