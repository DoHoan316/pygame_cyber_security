
"""Compatibility launcher. The actual Pygame V3 implementation is in main.py."""

import asyncio

try:
    from .main import CyberSafeV3
except ImportError:
    from main import CyberSafeV3


if __name__ == "__main__":
    asyncio.run(CyberSafeV3().run())
