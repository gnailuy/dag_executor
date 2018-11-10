class Config(dict):
    def __init__(self, init=None, name=None):
        if init is None:
            init = {}
        name = name or self.__class__.__name__.lower()
        dict.__init__(init)
        dict.__setattr__(self, '_name', name)

    def __getstate__(self):
        return self.__dict__.items()

    def __setstate__(self, items):
        for key, val in items:
            self.__dict__[key] = val

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, dict.__repr__(self))

    def __str__(self):
        n = self._name
        s = ['{}(name={!r}):'.format(self.__class__.__name__, n)]
        s = s + ['\t{}.{} = {!r}'.format(n, it[0], it[1]) for it in self.items()]
        return '\n'.join(s)

    def __setitem__(self, key, value):
        return super(Config, self).__setitem__(key, value)

    def __getitem__(self, name):
        return super(Config, self).__getitem__(name)

    def __delitem__(self, name):
        return super(Config, self).__delitem__(name)

    def set(self, name, value):
        return super(Config, self).__setitem__(name, value)

    __getattr__ = __getitem__
    __setattr__ = __setitem__
    __delattr__ = __delitem__

    def copy(self):
        return Config(self)

    def merge_another(self, conf, override=False):
        assert isinstance(conf, Config)
        for key in conf:
            if conf.get(key) is not None and override or key not in self:
                self.set(key, conf.get(key))

    def read_from_file(self, filename):
        if filename is None:
            return

        # Load the configuration file
        with open(filename) as f:
            import configparser
            ini = configparser.RawConfigParser(allow_no_value=True)
            ini.read_file(f)

            for section in ini.sections():
                for option in ini.options(section=section):
                    key = section + '_' + option \
                        if section.lower() != 'default' else option
                    value = ini.get(section=section, option=option)
                    self.set(key, value)

