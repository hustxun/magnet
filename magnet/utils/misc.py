try: get_ipython()
except NameError: in_notebook = False
else: in_notebook = True

def caller_locals(ancestor=False):
    """Print the local variables in the caller's frame."""
    import inspect
    frame = inspect.currentframe().f_back.f_back

    try:
        l = frame.f_locals

        if ancestor:
            f_class = l.pop('__class__', None)
            caller = l.pop('self')
            while f_class is not None and isinstance(caller, f_class):
                l.pop('args', None)
                args = frame.f_locals.pop('args', None)
                l.update(frame.f_locals)
                if args is not None: l['args'] = args

                l.pop('self', None)
                frame = frame.f_back
                f_class = frame.f_locals.pop('__class__', None)

        l.pop('self', None)
        l.pop('__class__', None)
        return l
    finally: del frame

def num_params(module):
    from numpy import prod

    trainable, non_trainable = 0, 0
    for p in module.parameters():
        n = prod(p.size())
        if p.requires_grad:
            trainable += n
        else:
            non_trainable += n

    return trainable, non_trainable

def get_tqdm():
    r"""Returns a flexible tqdm object according to the
    environment of execution.
    """
    import tqdm

    mode = 'tqdm_notebook' if in_notebook else 'tqdm'
    return getattr(tqdm, mode)
