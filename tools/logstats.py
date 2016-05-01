"""logstats - small helper for error messages."""

def run(items):
    """Return processed error messages."""
    return [i for i in items if i]

def main(argv=None):
    print(run([]))
