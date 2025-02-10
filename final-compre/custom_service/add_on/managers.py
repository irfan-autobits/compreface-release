from collections import defaultdict
from importlib import import_module
from typing import List, Type, Dict, Tuple
from types import ModuleType
from cached_property import cached_property

from custom_service.add_on import constants

from custom_service.add_on import base, mixins


ML_MODEL_SEPARATOR = '@'


def import_classes(class_path: str):
    module, class_name = class_path.rsplit('.', 1)
    return getattr(import_module(module, __package__), class_name)


class PluginManager:
    plugins_modules: Dict[ModuleType, List[str]]

    def __init__(self):
        self.plugins_modules = defaultdict(list)
        for plugin_name in self.get_plugins_names():
            module = import_module(f'{__package__}.{plugin_name.rsplit(".", 1)[0]}')
            plugin_name = plugin_name.split('.')[-2] + '.' + plugin_name.split('.')[-1]
            self.plugins_modules[module].append(plugin_name)

    @property
    def requirements(self):
        requirements = set()
        print(f"requirements manager ::{self.plugins_modules}")
        for module in self.plugins_modules:
            if hasattr(module, 'requirements'):
                requirements |= set(module.requirements)
            else:
                print(f"Warning: {module} does not have 'requirements' attribute.")
        return requirements

    def get_plugins_names(self):
        return list(filter(None, [
            constants.ENV.FACE_DETECTION_PLUGIN,
            constants.ENV.CALCULATION_PLUGIN
        ]))

    @cached_property
    def plugins(self):
        plugins = []
        for module, plugins_names in self.plugins_modules.items():
            for pl_name in plugins_names:
                mlmodel_name = None
                if ML_MODEL_SEPARATOR in pl_name:
                    pl_name, mlmodel_name = pl_name.split(ML_MODEL_SEPARATOR)
                pl_path = f'{module.__package__}.{pl_name}'
                pl_class = import_classes(pl_path)
                plugin = pl_class(ml_model_name=mlmodel_name)
                plugins.append(plugin)
        return plugins

    @cached_property
    def detector(self) -> mixins.FaceDetectorMixin:
        return [pl for pl in self.plugins
                if isinstance(pl, mixins.FaceDetectorMixin)][0]

    @cached_property
    def calculator(self) -> mixins.CalculatorMixin:
        return [pl for pl in self.plugins
                if isinstance(pl, mixins.CalculatorMixin)][0]

    @cached_property
    def face_plugins(self) -> List[base.BasePlugin]:
        return [pl for pl in self.plugins
                if not isinstance(pl, mixins.FaceDetectorMixin)]

    def filter_face_plugins(self, slugs: List[str]) -> List[base.BasePlugin]:
        return [pl for pl in self.face_plugins
                if slugs is None or pl.slug in slugs]

    def get_plugin_by_class(self, plugin_class: Type):
        for plugin in self.plugins:
            if isinstance(plugin, plugin_class):
                return plugin


plugin_manager = PluginManager()
