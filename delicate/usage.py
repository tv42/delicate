from twisted.python.usage import Options, UsageError
from twisted.plugin import IPlugin, getPlugins

class ICommand(IPlugin):
    def parseOptions(args):
        pass

class PluginMixin(object):
    """Make plugins appear as subcommands."""
    def __init__(self):
        super(PluginMixin, self).__init__()
        self.initializeSubCommands()

    def initializeSubCommands(self):
        interface = getattr(self, 'subCommandInterface', None)
        if interface is None:
            return

        package = getattr(self, 'subCommandPackage', None)
        if interface is None:
            return

        l = []
        for plugin in getPlugins(interface=interface,
                                 package=package):
            l.append((plugin.__class__.__name__.lower(),
                      getattr(plugin, 'shortcut', None),
                      plugin.__class__,
                      plugin.__doc__,
                      ))
        self.subCommands = l

class RequireSubcommandMixin(object):
    """Require a subcommand to be given."""
    def getSynopsis(self):
        s = super(RequireSubcommandMixin, self).getSynopsis()
        if self.subCommand is None:
            s = s + ' COMMAND [options]'
        return s

    def postOptions(self):
        super(RequireSubcommandMixin, self).postOptions()
        if self.subCommand is None:
            self.opt_help()
