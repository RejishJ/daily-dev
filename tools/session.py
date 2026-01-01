"""session - small helper for input validation."""

def run(items):
    """Return processed input validation."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
