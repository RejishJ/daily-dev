"""snippet - small helper for config migration."""

def run(items):
    """Return processed config migration."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
