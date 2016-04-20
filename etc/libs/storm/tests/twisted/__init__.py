__all__ = [
    'has_twisted',
    ]

try:
    import twisted
except ImportError:
    has_twisted = False
else:
    has_twisted = True
