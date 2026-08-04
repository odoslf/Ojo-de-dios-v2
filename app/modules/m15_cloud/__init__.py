"""Physical package for read-only Cloud / Containers / Kubernetes audits.

The R17 implementation intentionally exposes only passive technique classes that
consume operator-supplied inventories and reports.  No module-level re-exports
are used here, so recursive registry discovery finds the concrete classes from
``techniques.py`` exactly once.
"""
