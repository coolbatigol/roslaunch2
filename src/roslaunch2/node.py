import warnings
import lxml.etree
import enum

import remapable
import interfaces
import package
import machine
import parameter
import environment


class Output(enum.IntEnum):
    Screen = 1
    Log = 2

    def __str__(self):
        if self.value == Output.Screen:
            return 'screen'
        elif self.value == Output.Log:
            return 'log'


class Runnable(remapable.Remapable, interfaces.Composable, interfaces.Composer):
    def __init__(self, tag_name, pkg, node_type=None, name=None, args=None):
        remapable.Remapable.__init__(self)
        interfaces.Composable.__init__(self)
        interfaces.Composer.__init__(self, [parameter.Parameter, environment.EnvironmentVariable])
        if pkg and not node_type:
            node_type = pkg
        if not name:
            name = node_type
        if not pkg:
            raise ValueError("pkg='{}' cannot be empty or None.".format(pkg))
        self._pkg = package.Package(pkg) if type(pkg) is str else pkg
        self._node = node_type  # equals the 'type' attribute in XML
        self.name = name
        self.args = args
        self.clear_params = None
        self.ns = None
        self.prefix = None  # equals the 'launch-prefix' attribute in XML
        self.__tag_name = tag_name

    @property
    def pkg(self):
        return self._pkg

    @property
    def node(self):
        return self._node

    @pkg.setter
    def pkg(self, value):
        if not value:
            raise ValueError("pkg='{}' cannot be empty or None.".format(value))
        self._pkg = package.Package(value) if type(value) is str else value

    @node.setter
    def node(self, value):
        if not value:
            raise ValueError("node='{}' cannot be empty or None.".format(value))
        self._node = value

    def __del__(self):
        if not self.rooted:
            warnings.warn('{} has been created but never add()ed.'.format(str(self)), Warning, 2)

    def __str__(self):
        return '{:s}@{:s}: {:s}'.format(self.node, self.pkg, self.name)

    def add(self, param):
        for p in self.children:
            if param == p:
                raise ValueError("Parameter '{}' already added.".format(str(param)))

        interfaces.Composer.add(self, param)

    def clear_params(self, clear=None):
        self.clear_params = clear

    def set_namespace(self, ns=None):
        self.ns = ns

    def generate(self, root, machines, pkg):
        elem = lxml.etree.SubElement(root, self.__tag_name)
        remapable.Remapable.generate(self, elem, machines, self._pkg)

        interfaces.GeneratorBase.to_attr(elem, 'pkg', self._pkg, package.Package)
        interfaces.GeneratorBase.to_attr(elem, 'type', self._node, str)
        interfaces.GeneratorBase.to_attr(elem, 'name', self.name, str)
        interfaces.GeneratorBase.to_attr(elem, 'clear_params', self.clear_params, bool)
        interfaces.GeneratorBase.to_attr(elem, 'args', self.args, str)
        interfaces.GeneratorBase.to_attr(elem, 'ns', self.ns, str)
        interfaces.GeneratorBase.to_attr(elem, 'launch-prefix', self.prefix, str)
        return elem


class Node(Runnable):
    """
    For starting ROS nodes, equals <node>.
    """
    def __init__(self, pkg, node_type=None, name=None, output=Output.Screen, args=None):
        Runnable.__init__(self, 'node', pkg, node_type, name, args)
        assert not output or type(output) == Output
        self.output = output
        self._respawn = None  # None -> use roslaunch default
        self.respawn_delay = None
        self.machine = None
        self._required = None

    @property
    def required(self):
        return self._required

    @required.setter
    def required(self, value):
        if value and self._respawn:
            raise ValueError('Cannot set both required and respawn to True (incompatible).')
        self._required = value

    @property
    def respawn(self):
        return self._respawn

    @respawn.setter
    def respawn(self, value):
        if value and self._required:
            raise ValueError('Cannot set both required and respawn to True (incompatible).')
        self._respawn = value

    def start_on(self, machine_object):
        self.machine = machine_object

    def generate(self, root, machines, pkg):
        # The following allows machine.Resolvable objects in self.args:
        self.args = str(machine.Machine.resolve_if(self.args, self.machine, self._pkg))
        elem = Runnable.generate(self, root, machines, pkg)
        interfaces.GeneratorBase.to_attr(elem, 'output', self.output, Output)
        interfaces.GeneratorBase.to_attr(elem, 'respawn', self._respawn, bool)
        interfaces.GeneratorBase.to_attr(elem, 'machine', self.machine, machine.Machine)
        if self._respawn:
            interfaces.GeneratorBase.to_attr(elem, 'respawn_delay', self.respawn_delay, str)
        interfaces.GeneratorBase.to_attr(elem, 'required', self._required, bool)
        if self.machine:
            assert type(machines) is list
            machines.append(self.machine)
        # Generate parameter/environment tags and resolve paths / environment variables:
        for p in self.children:
            p.generate(elem, self.machine, self._pkg)
