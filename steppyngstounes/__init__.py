from inspect import isclass
from pkgutil import iter_modules
from os.path import (abspath, dirname)
from importlib import import_module

# Import all classes defined in modules into package namespace
#
# From https://julienharbulot.com/python-dynamical-import.html
#
# It's a more opaque way to say
#
#   from . import module
#   from .module import *
#   __all__.extend(module.__all__)
#
# OTOH, linters don't complain
# and modules don't have to be listed manually

# iterate through the modules in the current package
package_dir = dirname(abspath(__file__))
for (_, module_name, _) in iter_modules([package_dir]):

    # import the module and iterate through its attributes
    module = import_module("{}.{}".format(__name__, module_name))
    for attribute_name in dir(module):
        attribute = getattr(module, attribute_name)

        if isclass(attribute):
            # Add the class to this package's variables
            globals()[attribute_name] = attribute
