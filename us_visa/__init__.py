import numpy as np

# Compatibility patch for NumPy 2.0+ with legacy packages (e.g. evidently 0.2.8)
if not hasattr(np, "float_"):
    np.float_ = np.float64
if not hasattr(np, "int_"):
    np.int_ = np.int64
if not hasattr(np, "bool_"):
    np.bool_ = bool
