# layered-settings task runner.
# Requires: uv (https://docs.astral.sh/uv/). Run `just` to list recipes.

# Show available recipes.
default:
    @just --list

# Remove build artifacts.
clean:
    rm -rf dist build *.egg-info

# Run the test suite.
test:
    uv run python -m unittest discover -s tests -p '*.py' -t .

# Build sdist + wheel into dist/.
build: clean
    uv build

# Validate built artifacts' metadata.
check: build
    uvx twine check dist/*

# Build, validate, and publish to PyPI.
# Auth: credentials read from ~/.pypirc (use __token__ + a PyPI API token).
publish: check
    uvx twine upload dist/*

# Publish to TestPyPI instead. Auth: [testpypi] section in ~/.pypirc.
publish-test: check
    uvx twine upload --repository testpypi dist/*
