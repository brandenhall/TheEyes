import tornado.options
import importlib


class Settings():
    def __init__(self, settings_module):
        # store the settings module in case someone later cares
        self.SETTINGS_MODULE = settings_module

        try:
            mod = importlib.import_module(self.SETTINGS_MODULE)
        except ImportError as e:
            raise ImportError(
                "Could not import settings '%s': %s"
                % (self.SETTINGS_MODULE, e)
            )

        for setting in dir(mod):
            if setting == setting.upper():
                setattr(self, setting, getattr(mod, setting))

    def __getattr__(self, name):
        return None

tornado.options.define(
    "settings",
    default='',
    help="settings",
    type=str
)

tornado.options.parse_command_line()
settings = Settings(tornado.options.options.settings)
