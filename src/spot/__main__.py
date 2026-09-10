"""SPOT command-line entry point.

Allows SPOT to be started with:

```
python -m spot
```

"""

from **future** import annotations

import sys

from .version import **version**

def main() -> int:
"""Run the SPOT command-line interface."""

```
print(f"SPOT - Synthetic Persona Obfuscation Tool v{__version__}")
print("SPOT command-line interface is not yet implemented.")

return 0
```

if **name** == "**main**":
sys.exit(main())
