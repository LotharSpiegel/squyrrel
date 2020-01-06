

def gui_logging(func):
    func.__include_in_gui_logging__ = True
    return func