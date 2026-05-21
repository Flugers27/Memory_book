#!/usr/bin/env python3
"""Test script to verify model imports after refactoring"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Testing model imports...")

# Test 1: Import centralized models
try:
    from database.models.auth import User, RefreshToken, UserRole
    print("✓ Successfully imported User, RefreshToken, UserRole from database.models.auth")
except ImportError as e:
    print(f"✗ Failed to import from database.models.auth: {e}")

try:
    from database.models.memory import AgentBD, PageBD
    print("✓ Successfully imported AgentBD, PageBD from database.models.memory")
except ImportError as e:
    print(f"✗ Failed to import from database.models.memory: {e}")

try:
    from database.models.access import PageAccessControl
    print("✓ Successfully imported PageAccessControl from database.models.access")
except ImportError as e:
    print(f"✗ Failed to import from database.models.access: {e}")

# Test 2: Test service imports
print("\nTesting service imports...")

# Auth service
try:
    from services.Auth.crud import get_user_by_id
    print("✓ Successfully imported from services.Auth.crud")
except ImportError as e:
    print(f"✗ Failed to import from services.Auth.crud: {e}")

try:
    from services.Auth.auth_logic import authenticate_user
    print("✓ Successfully imported from services.Auth.auth_logic")
except ImportError as e:
    print(f"✗ Failed to import from services.Auth.auth_logic: {e}")

# Memory service
try:
    from services.Memory.crud import select_memory_agent_list_by_user
    print("✓ Successfully imported from services.Memory.crud")
except ImportError as e:
    print(f"✗ Failed to import from services.Memory.crud: {e}")

# Acces_Memory service
try:
    from services.Acces_Memory.crud import get_access_by_id
    print("✓ Successfully imported from services.Acces_Memory.crud")
except ImportError as e:
    print(f"✗ Failed to import from services.Acces_Memory.crud: {e}")

print("\nAll tests completed.")