import sys
import os
from pathlib import Path
import pytest
import asyncio


root_dir = str(Path(__file__).parent.parent)
sys.path.insert(0, root_dir)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close() 