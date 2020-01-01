"""depscan - small helper for dry-run flag."""

def run(items):
    """Return processed dry-run flag."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
