"""bench - small helper for cache layer."""

def run(items):
    """Return processed cache layer."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
