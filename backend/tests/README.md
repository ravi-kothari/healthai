# Backend Testing Guide

## Overview

This directory contains comprehensive tests for the AI Healthcare Application backend, covering:
- **Unit tests**: Fast, isolated tests for individual functions and classes
- **Integration tests**: Tests for complete workflows and API endpoints
- **Test fixtures**: Reusable test data and database setup

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and shared fixtures
├── unit/                    # Unit tests (fast, no external dependencies)
│   ├── test_auth.py        # Authentication and JWT tests
│   └── test_previsit_services.py  # PreVisit.ai service tests
└── integration/             # Integration tests (database, API)
    └── test_previsit_flow.py      # Complete PreVisit.ai workflow tests
```

## Running Tests

### Option 1: Using Docker (Recommended)

The recommended way to run tests is inside the Docker container where all dependencies are installed:

```bash
# Start the Docker containers
cd backend/docker
docker-compose up -d

# Run all tests
docker-compose exec api pytest

# Run with coverage report
docker-compose exec api pytest --cov=src --cov-report=html

# Run specific test categories
docker-compose exec api pytest -m unit        # Only unit tests
docker-compose exec api pytest -m integration # Only integration tests
docker-compose exec api pytest -m previsit    # Only PreVisit.ai tests
docker-compose exec api pytest -m auth        # Only auth tests

# Run specific test file
docker-compose exec api pytest tests/unit/test_auth.py -v

# Run specific test class or function
docker-compose exec api pytest tests/unit/test_auth.py::TestUserLogin -v
docker-compose exec api pytest tests/unit/test_auth.py::TestUserLogin::test_login_success_with_username -v
```

### Option 2: Local Virtual Environment

If you prefer to run tests locally without Docker:

```bash
# Create virtual environment
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html --cov-report=term-missing

# Open coverage report
open htmlcov/index.html  # On macOS
# or
xdg-open htmlcov/index.html  # On Linux
```

## Test Configuration

### pytest.ini

The `pytest.ini` file in the backend root directory configures:
- Test discovery patterns
- Coverage settings (minimum 80% required)
- Test markers for organizing tests
- Logging configuration
- Async test support

### Test Markers

Tests are organized using markers defined in `pytest.ini`:

- `@pytest.mark.unit` - Fast unit tests
- `@pytest.mark.integration` - Integration tests with database
- `@pytest.mark.slow` - Slow-running tests
- `@pytest.mark.auth` - Authentication tests
- `@pytest.mark.previsit` - PreVisit.ai feature tests
- `@pytest.mark.appoint_ready` - Appoint-Ready feature tests
- `@pytest.mark.fhir` - FHIR integration tests

Example usage:
```python
@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    # Test code here
```

## Test Fixtures

### Database Fixtures

Located in `conftest.py`:

- `db_session` - Fresh database session for each test (auto-rollback)
- `test_engine` - Test database engine (SQLite in-memory)
- `TestSessionLocal` - Session factory for tests

### User Fixtures

- `test_user` - Provider user with credentials
- `test_patient_user` - Patient user with credentials
- `auth_token` - JWT token for provider
- `patient_auth_token` - JWT token for patient
- `auth_headers` - Authorization headers for API requests

### Data Fixtures

- `test_patient` - Sample patient record
- `multiple_test_patients` - List of patients for pagination tests
- `test_appointment` - Sample appointment
- `test_symptoms_data` - Sample symptoms for PreVisit.ai
- `test_triage_data` - Sample triage assessment data

### Mock Fixtures

- `mock_openai_response` - Mock AI analysis response
- `mock_fhir_patient_data` - Mock FHIR patient resource

## Writing New Tests

### Unit Test Example

```python
import pytest
from src.api.auth.password import hash_password, verify_password

@pytest.mark.unit
@pytest.mark.auth
def test_password_hashing():
    """Test password hashing works correctly."""
    password = "SecurePassword123!"
    hashed = hash_password(password)

    assert hashed != password
    assert verify_password(password, hashed) is True
```

### Integration Test Example

```python
import pytest
from fastapi import status

@pytest.mark.integration
@pytest.mark.previsit
@pytest.mark.asyncio
async def test_symptom_analysis_flow(client, patient_auth_headers):
    """Test complete symptom analysis workflow."""
    symptom_data = {
        "symptoms": [
            {
                "name": "Headache",
                "severity": "moderate",
                "duration": "2 days"
            }
        ]
    }

    response = client.post(
        "/api/previsit/analyze-symptoms",
        json=symptom_data,
        headers=patient_auth_headers
    )

    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "urgency" in data
    assert "recommendations" in data
```

## Test Coverage Goals

- **Overall**: 80%+ code coverage
- **Backend services**: 85%+
- **API endpoints**: 90%+
- **Critical paths (auth, PreVisit, Appoint-Ready)**: 95%+

## Continuous Integration

Tests are automatically run in CI/CD pipeline on:
- Every pull request
- Every push to `main` or `develop` branches
- Nightly builds

## Troubleshooting

### Tests fail with "ModuleNotFoundError"

Make sure you're running tests from the correct directory and all dependencies are installed:

```bash
cd backend
pip install -r requirements.txt
pytest
```

### Database connection errors

When running locally, ensure the test database is accessible or use SQLite (default in tests).

### Import errors

Make sure the `src` directory is in your Python path:

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest
```

### Async test errors

Ensure `pytest-asyncio` is installed and tests are marked with `@pytest.mark.asyncio`:

```bash
pip install pytest-asyncio
```

## Best Practices

1. **Keep tests fast**: Unit tests should complete in milliseconds
2. **Use fixtures**: Reuse common setup code via fixtures
3. **Test one thing**: Each test should verify one specific behavior
4. **Use descriptive names**: Test names should explain what they test
5. **Mock external services**: Don't make real API calls in tests
6. **Clean up**: Tests should not leave side effects
7. **Test edge cases**: Include tests for error conditions
8. **Maintain coverage**: Don't let coverage drop below 80%

## Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/14/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites)
- [Project Test Strategy](../../docs/TESTING_STRATEGY.md)

## Next Steps

To complete the testing setup:

1. ✅ Testing framework configured
2. ✅ Unit tests for authentication written
3. ✅ Unit tests for PreVisit.ai services written
4. ✅ Integration tests for PreVisit.ai workflow written
5. ⏳ Add tests for Appoint-Ready services
6. ⏳ Add tests for patient CRUD operations
7. ⏳ Add E2E tests with Playwright
8. ⏳ Set up CI/CD pipeline with automated testing
9. ⏳ Configure code coverage reporting
10. ⏳ Add performance/load tests

---

**Last Updated**: November 4, 2025
**Test Coverage**: Unit tests implemented, integration tests implemented
**Status**: Ready for execution in Docker environment
