def autodoc_skip_member(app, what, name, obj, skip, options):
    if name == '__init__':
        return False
    return skip

def setup(app):
    app.connect('autodoc-skip-member', autodoc_skip_member)
