"""
Unit test suite-wide functions and classes.
"""


def skipIfTrue(flag):
    def deco(f):
        def wrapper(self, *args, **kwargs):
            if getattr(self, flag):
                self.skipTest("Necessary previous test failed!")
            else:
                f(self, *args, **kwargs)
        return wrapper
    return deco