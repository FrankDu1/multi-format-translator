"""
Small compatibility shim for PyTorch/transformers import mismatch.

Some PyTorch builds expose `_register_pytree_node` but not the name
`register_pytree_node` expected by certain `transformers` versions.

This module attempts to add a backward-compatible alias at import time.
Import this module before importing `transformers` in any file.

If torch is not installed (e.g., using cloud translation), this shim does nothing.
"""

try:
    import torch
    # Some torch builds expose `_register_pytree_node` but not
    # `register_pytree_node`. If that's the case, create the alias.
    pytree = getattr(torch.utils, "_pytree", None)
    if pytree is not None:
        if not hasattr(pytree, "register_pytree_node") and hasattr(pytree, "_register_pytree_node"):
            try:
                pytree.register_pytree_node = pytree._register_pytree_node
            except Exception:
                # If assignment fails for any reason, don't crash the import.
                pass
except ImportError:
    # torch not installed (e.g., cloud translation mode) - that's fine
    pass
except Exception:
    # If something else goes wrong, silence the shim.
    pass
