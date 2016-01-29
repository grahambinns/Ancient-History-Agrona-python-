"""
Event handling classes and functions for Agrona
"""
from   base      import Listener
from   datetime  import datetime
import logging
import config
import smtplib
import xmlrpclib

class EventHandler(Listener):
    """
    The Event handler is responsible for actually handling any events that
    happen to be fired.

    TODO: Eventually we'll want to subclass this perhaps, or turn it into some
    kind of factory so that we can do more useful stuff when errors occur (like
    attempting to restart processes remotely perhaps? Hmm... could be
    permission issues there...)
    """

    def notify(self, notifier, event=None):
        """
        Called by notifiers when an event is fired.
        This is where our business logic for event handling actually lives.

        notifier
            The object that sent the notification

        event
            The event we're being notified about. If this is None then all
            notify will do is log the fact that it was called
        """
        Listener.notify(self, notifier, event)

        logging.info("EventHandler notified of event " + event.eventType + " by "
                     +"notifier " + str(notifier))

        # If we don't have an event to handle, we can't really do anything
        if event is None: return

        # Otherwise, we look to see if there are any alerts for it
        now = datetime.now().strftime(config.DATE_FORMAT)
        if config.ALERTS.has_key(event.eventType):
            logging.info("Sending alerts for event type " + event.eventType)
            alertBody = config.ALERTS[event.eventType] % (str(notifier), now)

            # Send out the alerts
            # By email
            smtp = smtplib.SMTP(config.SMTP_HOST)
            for recipient in config.RECIPIENTS['email']:
                logging.debug("Sending alert email to " + recipient)
                smtp.sendmail(config.FROM_ADDR, recipient, alertBody)
            smtp.quit()

            # And by SMS, using the MobServ XML-RPC web service
            try:
                server = xmlrpclib.ServerProxy(config.XMLRPC_SERVER)
                for recipient in config.RECIPIENTS['sms']:
                    logging.debug("Sending alert sms to " + recipient)
                    continue
                    server.neit.sendSMS(config.FROM_MSISDN, recipient, alertBody)
            except xmlrpclib.ProtocolError, err:
                logging.error("Unable to send SMS through MobServ: " + err)

