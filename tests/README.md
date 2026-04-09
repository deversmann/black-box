# Black Box Swarm Tests

## Running Tests

### All tests
```bash
pytest
```

### With coverage
```bash
pytest --cov=blackbox --cov-report=html
```

### Specific test file
```bash
pytest tests/unit/test_agents/test_sieve.py
```

### Integration tests only
```bash
pytest tests/integration/
```

### Unit tests only
```bash
pytest tests/unit/
```

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/
│   ├── test_agents/         # Individual agent tests
│   │   ├── test_sieve.py
│   │   ├── test_flash.py
│   │   ├── test_command.py
│   │   └── test_verdict.py
│   └── test_config.py       # Configuration tests
└── integration/
    └── test_swarm_flow.py   # End-to-end swarm tests
```

## Writing Tests

All async functions should use `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_my_async_function():
    result = await my_function()
    assert result is not None
```

Use fixtures from `conftest.py` for common setups:

```python
def test_agent(sieve_config, mock_openrouter_client):
    agent = Sieve(sieve_config, mock_openrouter_client)
    assert agent.name == "Sieve"
```
