"""Physical package for defensive honeypots and deception analysis.

R19 exposes only defensive technique classes in ``techniques.py``.  The package
keeps module-level exports empty so recursive registry discovery registers each
concrete class once.
"""
