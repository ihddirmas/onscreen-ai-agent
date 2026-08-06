"""Render build hook: install LiteLLM deps and generate the Prisma client at build time."""
from __future__ import annotations

import os
import subprocess
import sys

from setuptools import setup
from setuptools.command.install import install


class InstallWithPrisma(install):
    def run(self) -> None:
        install.run(self)
        import litellm

        schema = os.path.join(os.path.dirname(litellm.__file__), "proxy", "schema.prisma")
        subprocess.check_call(
            [sys.executable, "-m", "prisma", "generate", "--schema", schema],
            env={**os.environ, "PATH": os.path.dirname(sys.executable) + os.pathsep + os.environ.get("PATH", "")},
        )


setup(
    name="oncue-litellm-render",
    version="0.1.0",
    install_requires=[
        "litellm[proxy]>=1.57.0",
        "psycopg2-binary>=2.9.9",
        "prisma>=0.15.0",
    ],
    cmdclass={"install": InstallWithPrisma},
)
