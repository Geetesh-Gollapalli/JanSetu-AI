"""
JanSetu AI - Render Deployment Entry Point

This file is ONLY a deployment adapter.
The existing JanSetu application is not modified.

Render provides the PORT environment variable.
The existing server/app.py already exposes run(port),
so this wrapper simply passes Render's PORT to it.
"""

import os

from server.app import run


def main():
    port = int(os.environ.get("PORT", "8080"))

    print("=" * 70)
    print("  JANSETU AI - RENDER DEPLOYMENT")
    print(f"  Listening on port: {port}")
    print("=" * 70)

    run(port)


if __name__ == "__main__":
    main()