"""
MWACS-triggered Events: The events that a group of MWACS entities might
fire-off
"""
from event.base     import Event
from mwacs.entities import MWACSHost, MWACSProcess, MWACSProperty
from mwacs.entities import InvalidProcessError
from mwacs.entities import InvalidHostError
from mwacs.entities import InvalidPropertyError

## Process-related events ##

class ProcessEvent(Event):
    """
    Represents an event occurring on an instance of MWACSProcess

    Properties

    process
        The process that sent the event
    """
    eventType = "Process"

    def __init__(self, process):
        """
        Initialises a ProcessEvent

        process
            The process in which the event occurred
        """
        if not isinstance(process, MWACSProcess):
            raise InvalidProcessError("Object "+ str(process) + " is not a " \
                                      + "valid MWACSProcess")
        self.process = process

class ProcessStoppedEvent(ProcessEvent):
    """Fired when a process stops unexpectedly"""
    eventType = "ProcessStopped"

class ProcessTimeoutEvent(ProcessEvent):
    """Fired when a process doesn't report in after a given length of time"""
    eventType = "ProcessTimeout"

## Host-related events ##

class HostEvent(Event):
    """
    A base-class for host-related events

    Properties:

    host
        The host that raised the event
    """
    eventType = "Host"

    def __init__(self, host):
        if not isinstance(host, MWACSHost):
            raise InvalidHostError("Object "+ str(host) + " is not a " \
                                      + "valid MWACSHost")

        self.host = host

class HostTimeoutEvent(HostEvent):
    """Fired when a host doesn't report in"""
    eventType = "HostTimeout"

class HighLoadAverageEvent(HostEvent):
    """Fired when a host's load average gets too high"""
    eventType = "HighLoadAverage"

## Property-related events

class PropertyEvent(Event):
    """
    A base class for property-fired events

    Properties:

    property
        The property that fired off the event
    """
    eventType = "Property"

    def __init__(self, property):
        """
        Initialises the event

        property
            The MWACSProperty that the event occured in
        """

        if not isinstance(property, MWACSProperty):
            raise InvalidPropertyError("Object "+ str(property) + " is not a " \
                                      + "valid MWACSProperty")
