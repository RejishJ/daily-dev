"""fmtcheck - small helper for diff viewer."""

def run(items):
    """Return processed diff viewer."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
