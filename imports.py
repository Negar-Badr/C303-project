import inspect
import os, sys, types
import importlib.util

def find_303mud(start_dir):
    current = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(current, "303MUD")
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent

current_directory = os.path.dirname(__file__)
mud_folder = find_303mud(current_directory)
assert mud_folder, "The 303MUD folder could not be found. Did you set up the folder structure as seen in class?"

def load_module(module, root_folder):
    subdirs = module.split('/')
    module_name = subdirs[-1]
    module_path = os.path.join(root_folder, *subdirs) + ".py"
    
    alias = '303MUD.' + '.'.join(module.split('/'))
    
    if '303MUD' not in sys.modules:
        mud_pkg = types.ModuleType('303MUD')
        mud_pkg.__path__ = [root_folder]
        sys.modules['303MUD'] = mud_pkg
    
    spec = importlib.util.spec_from_file_location(alias, module_path, submodule_search_locations=[os.path.dirname(module_path)])
    if spec is None:
        raise ImportError(f"Could not load spec for {module_name} from {module_path}")
    
    if alias in sys.modules:
        module_obj = sys.modules[alias]
    else:
        module_obj = importlib.util.module_from_spec(spec)
        module_obj.__package__ = alias.rpartition('.')[0]
        spec.loader.exec_module(module_obj)
        sys.modules[alias] = module_obj
    
    return module_obj

modules = []
modules_to_load = ["command", "coord", "message", "NPC", "Player", "maps/base", "tiles/base", "tiles/map_objects"]
for module in modules_to_load:
    modules.append(load_module(module, mud_folder))

__all__ = []
for mod in modules:
    for name, obj in inspect.getmembers(mod):
        if inspect.isclass(obj) and obj.__module__ == mod.__name__:
            globals()[name] = obj
            __all__.append(name)

#print("Exported names:", __all__)