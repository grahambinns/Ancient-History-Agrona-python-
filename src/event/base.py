"""Our basic implementation of an event model"""

# These are the exceptions we're going to be using for events
class InvalidListenerError(Exception):
    """Raised when a non-listener is passed for registration with a Notifer"""

class InvalidEventError(Exception):
    """Raised when a non-event is passed to the notifyListeners method of a
    Notifier"""

class Event:
    """
    Represents a single event. Doesn't actually do anything in and of
    itself; must be extended
    """

    # eventType is used by EventHandler to decide how this event type should
    # be handled
    eventType = "Event"

    pass

class Listener:
    """
    A Listener is responsible for listening out for events and doing
    something with them once they occur.
    """

    def notify(self, notifier, event=None):
        """
        Called when something happens by notifiers with which the listener
        is registered
        """
        pass

class Notifier:
    """
    A Notifier can send out events to registered listeners - it's the
    publish half of our limited publish/subscribe architecture

    Properties:

    listeners
        The list of listeners that have registered themselves with this
        notifier.
    """

    def __init__(self):
        """Initialises the notifer with an empty list of listeners"""
        self.listeners = []

    def addListener(self, listener):
        """
        Adds a listener to the list of registered listeners

        listener
            The listener to add. If already registered with this notifier,
            the listener will not be added again.
            If this is not an instance of Listener, an InvalidListenerError
            will be raised.
        """
        # First, check we have a valid listener
        if not isinstance(listener, Listener):
            raise InvalidListenerError(str(listener) + " is not a valid "
                                       + " Listener instance")

        # If it's not already there, add the listener to our list
        if listener not in self.listeners: self.listeners.append(listener)

    def removeListener(self, listener):
        """
        Unregisters a listener with the current Notifier

        listener
            The listener to remove from our list of listeners. If this is
            not already registered with the Notifier, the request will be .
            ignored.
            If this is not an instance of Listener, an InvalidListenerError
            will be raised.
        """

        # Check we have a valid listener
        if not isinstance(listener, Listener):
            raise InvalidListenerError(str(listener) + " is not a valid "
                                       + " Listener instance")

        # Only remove the listener if we've got it (avoids ValueErrors)
        if listener in self.listeners: self.listeners.remove(listener)

    def notifyListeners(self, event=None):
        """
        Notifiers all listeners registered with this Notifier that
        something has happened

        event
            The event that we're notifying the listeners about. If None, no
            event will be passed to Listener.notify().
            If an object is passed here that is not an instance of Event, an
            InvalidEventError will be raised
        """

        # Validate the event, just to be safe
        if event is not None and not isinstance(event, Event):
            raise InvalidEventError("Object " + str(event) + " is not a valid Event")

        # Notify our dear listeners
        for listener in self.listeners:
            listener.notify(self, event)
