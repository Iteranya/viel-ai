PLUGINS = {}

def plugin(fn):
    """Decorator to register a plugin function."""
    PLUGINS[fn.__name__] = fn
    return fn
