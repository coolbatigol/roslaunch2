import warnings
import lxml.etree

import interfaces
import machine
import remapable


class Launch(object, remapable.Remapable, interfaces.Composable, interfaces.GeneratorBase):
    def __init__(self, deprecation_message=None):
        remapable.Remapable.__init__(self)
        interfaces.Composable.__init__(self)
        interfaces.GeneratorBase.__init__(self)
        if deprecation_message:
            warnings.warn(deprecation_message, DeprecationWarning)

    def __repr__(self):
        return self.children.__repr__()

    def add(self, other):
        if isinstance(other, machine.Machine):
            message = "Machines shouldn't be add()ed explicitly (skipping {})" \
                .format(repr(other))
            warnings.warn(message, Warning)
        else:
            super(Launch, self).add(other)

    def generate(self, root=None, machines=None):
        # Work around this issue (order of boolean expressions matters!):
        # http://stackoverflow.com/questions/20129996/why-does-boolxml-etree-elementtree-element-evaluate-to-false
        first_call = isinstance(root, type(None)) and not root
        if first_call:
            root = lxml.etree.Element('launch')
            machines = []
        for child in self.children:
            child.generate(root, machines)
        if first_call:
            # Machines currently insert themselves at the beginning (for simplicity):
            machines = list(set(machines))  # make unique based on machine names
            for m in machines:
                m.generate(root, None)
            return lxml.etree.tostring(root, pretty_print=True, xml_declaration=True,
                                       encoding='UTF-8', standalone='yes')
