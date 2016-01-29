"""
MWACS Entities: Classes that represent the different parts of an MWACS XML
file
"""
from event.base import Notifier

import config

class InvalidPropertyError(Exception):
    """
    Raised when a non-property is passed to an MWACSHost's addProperty()
    method
    """

class InvalidProcessError(InvalidPropertyError):
    """
    Raised when a non-process is passed to an MWACSHost's addProcess()
    method
    """

class InvalidHostError(Exception):
    """
    Raised when a non-process is passed to an MWACSHost's addProcess()
    method
    """

class DuplicatePropertyError(Exception):
    """
    Raised when an attempt is made to overwrite a property of an MWACSHost
    without the overwrite flag of addProperty being set
    """

class DuplicateProcessError(DuplicatePropertyError):
    """
    Raised when an attempt is made to overwrite a process of an MWACSHost
    without the overwrite flag of addProcess being set
    """

class MWACSHost(Notifier):
    """
    Represents a host in MWACS output. A host consists of a hostname, a pair
    of dictionaries (processess and properties) and little else
    """

    def __init__(self, name, age=0, value=0):
        """
        Initialises the host and its dictionaries

        name
           The hostname, as described in the MWACS XML

        age
            The age (time since last reporting in) of the host

        value
            The arbitrary value (usually load avg.) of the host.
        """
        Notifier.__init__(self)
        self.name  = name
        self.age   = age
        self.value = value

        # Initialise the dicts of processess and properties
        self.props = {}
        self.procs = {}

    def __setattr__(self, name, value):
        """
        Magic internal method for handling the setting of attributes.
        We override it here to add the event-firing hooks for timeouts
        and high load averages

        name
            The name of the attribute to set

        value
            Its new value
        """

        # If we don't have the attribute in our __dict__, add it and set it
        # to None (this should allow us to handle high load averages and the
        # like still
        if not self.__dict__.has_key(name):
            self.__dict__[name] = None

        # We're only interested in value and age for Hosts
        if name is 'age':
            # We need do imports here to avoid circular references
            from events import HostTimeoutEvent

            # We only fire an event if the age has changed as well as being over
            # the legal limit
            if value != self.age and value > config.TIMEOUT:
                self.notifyListeners(HostTimeoutEvent(self))

        elif name is 'value':
            from events import HighLoadAverageEvent

            # We fire an event if the load average has changed and is > than
            # the upper limit in the config
            if value != self.value and value > config.LOAD_AVG_HIGH:
                self.notifyListeners(HighLoadAverageEvent(self))

        # Finally, we update the property regardless
        self.__dict__[name] = value

    def _addProp(self, prop, overwrite=False, name=None):
        """
        Adds a new MWACSProperty to the specified dictionary of properties.

        prop
            The MWACSProperty to add. By default, it's name property will
            be used as the key for the props{} dictionary

        overwrite
            If True, an existing property with the same name as this
            will be overwritten. If False, an existing property with the
            same name will cause a DuplicatePropertyError to be raised

        name
            Used to specify a name for the property. Specifying a name here
            will override the name property of the property being added
        """

        # Check that prop is actually a property first
        if not isinstance(prop, MWACSProperty):
            raise InvalidPropertyError("Passed property isn't a property")

        if name is not None:
            propName = name
        else:
            propName = prop.name

        # work out where we're going to stick this property
        if isinstance(prop, MWACSProcess):
            target = self.procs
        else:
            target = self.props

        # If we're not overwriting, check that this name doesn't already exist
        if not overwrite and target.has_key(propName):
            raise DuplicatePropertyError("Property %s already exists for host %s" \
                %(propName, self.name))

        # Let the property know who's boss
        prop.owner = self

        # Bung the property in its slot
        if isinstance(prop, MWACSProcess):
            target[propName.lower()] = prop
        else:
            target[propName.lower()] = prop

    def addProperty(self, prop, overwrite=False, name=None):
        """
        Adds a new MWACSProperty to the specified dictionary of properties.

        prop
            The MWACSProperty to add. By default, it's name property will
            be used as the key for the props{} dictionary

        overwrite
            If True, an existing property with the same name as this
            will be overwritten. If False, an existing property with the
            same name will cause a DuplicatePropertyError to be raised

        name
            Used to specify a name for the property. Specifying a name here
            will override the name property of the property being added
        """

        # Check that prop is actually a property first
        if not isinstance(prop, MWACSProperty):
            raise InvalidPropertyError("Passed property isn't a property")

        # Pass it on to _addProp to deal with
        self._addProp(prop, overwrite, name)

    def addProcess(self, proc, overwrite=False, name=None):
        """
        Adds a new MWACSProcess to the dictionary of processes

        prop
            The MWACSProcess to add. By default, its name property will
            be used as the key for the procs{} dictionary

        overwrite
            If True, an existing process with the same name as this
            will be overwritten. If False, an existing process with the
            same name will cause a DuplicateProcessError to be raised

        name
            Used to specify a name for the process. Specifying a name here
            will override the name property of the process being added
        """

        # Check that prop is actually a process first
        if not isinstance(proc, MWACSProcess):
            raise InvalidProcessError("Passed process isn't a process")

        # Pass it on to _addProp to deal with
        self._addProp(proc, overwrite, name)

    def addListener(self, listener, addRecursively=True):
        """
        Adds a listener to the host

        listener
            The listener to add

        addRecursively
            Flags whether or not all processes and properties owned by this
            host should get the listener too.
        """

        # We let Notifier do the hard work, so we don't have to
        Notifier.addListener(self, listener)

        # And then, if necessary, we pass it on to our children
        if addRecursively:
            for proc in self.procs.values(): proc.addListener(listener \
                                                              ,addRecursively)
            for prop in self.props.values(): prop.addListener(listener)

    def __str__(self):
        return "Host " + self.name

class MWACSProperty(Notifier):
    """
    Represents a single property of an MWACS host, as described in the MWACS
    XML output
    """

    def __init__(self, name, value=None, owner=None):
        """
        Creates a new MWACSProperty

        name
            The name of the property as defined in the name element of the
            MWACS XML

        value
            (Optional) The initial value for the property

        owner
            (Optional) The MWACSHost or MWACSProcess that owns this property
        """
        Notifier.__init__(self)

        self.name  = name
        self.value = value
        self.owner = owner

    def getOwner(self):
        """
        Returns the owner of the property, including its ancestors, in the form
        host.process.property and so on.
        """
        # First, see if our owner has an owner
        try:
            ownerString = self.owner.getOwner()
        except AttributeError:
            if self.owner is not None: ownerString = self.owner.name
            else:                      ownerString = ""

        return ownerString


    def __str__(self):
        return "Property " + self.getOwner() + "." + self.name

class MWACSProcess(MWACSProperty):
    """
    Represents a single process within MWACS

    Processes are a special case of properties, having as they do an age
    on top of everything else
    """

    def __init__(self, name, value=None, age=0, owner=None):
        """
        Creates a new MWACSProcess

        name
            The name of the process as defined in the name element of the
            MWACS XML

        value
            The initial value for the process

        age
            The initial age of the process. This tells us how long it was
            since the process updated its status file

        owner
            (Optional) The MWACSHost that owns this process
        """
        MWACSProperty.__init__(self, name, value, owner)

        self.age = age

        # Processes can have properties, too
        self.props = {}

    def __setattr__(self, name, value):
        """
        Magic internal method for handling the setting of attributes.
        We override it here to add the event-firing hooks for timeouts
        and high load averages

        name
            The name of the attribute to set

        value
            Its new value
        """

        # Create any attributes we don't have already
        if not self.__dict__.has_key(name):
            self.__dict__[name] = None

        # We're only interested in value and age for Hosts
        if name is 'age':
            from events import ProcessTimeoutEvent

            # We only fire an event if the age has changed as well as being over
            # the legal limit
            if value != self.age and value > config.TIMEOUT:
                self.notifyListeners(ProcessTimeoutEvent(self))

        elif name is 'value':
            from events import ProcessStoppedEvent

            # We fire an event if the load average has changed and is > than
            # the upper limit in the config
            if value != self.value and value.lower() is not "stopped":
                self.notifyListeners(ProcessStoppedEvent(self))

        # Finally, we update the property regardless
        self.__dict__[name] = value

    def addProperty(self, prop, overwrite=False, name=None):
        """
        Adds a new MWACSProperty to the process's dictionary of properties.

        prop
            The MWACSProperty to add. By default, it's name property will
            be used as the key for the props{} dictionary

        overwrite
            If True, an existing property with the same name as this
            will be overwritten. If False, an existing property with the
            same name will cause a DuplicatePropertyError to be raised

        name
            Used to specify a name for the property. Specifying a name here
            will override the name property of the property being added
        """

        # Check that prop is actually a property first
        if not isinstance(prop, MWACSProperty):
            raise InvalidPropertyError("Passed property isn't a property")

        if name is not None:
            propName = name
        else:
            propName = prop.name

        # If we're not overwriting, check that this name doesn't already exist
        if not overwrite and self.props.has_key(propName):
            raise DuplicatePropertyError("Property %s already exists for process %s" \
                %(propName, self.name))

        # Make us the property's new owner
        prop.owner = self

        # Bung the property in its slot
        self.props[propName.lower()] = prop

    def addListener(self, listener, addRecursively=True):
        """
        Adds a listener to the process

        listener
            The listener to add

        addRecursively
            Flags whether or not all properties owned by this process should
            get the listener too.
        """

        # We let Notifier do the hard work, so we don't have to
        Notifier.addListener(self, listener)

        # And then, if necessary, we pass it on to our children
        if addRecursively:
            for prop in self.props.values(): prop.addListener(listener)

    def __str__(self):
        return "Process " + self.getOwner() + "." + self.name


