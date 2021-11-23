import abc


class ApplicationServiceInterface(abc.ABC):
    pass
    # @abc.abstractmethod
    # def observe_event(self, event: str, callback, event_type: str, event_law: dict):
    #     """
    #     Register an event handler
    #     :param event: The event topic and (optional) subtopic, separated by a '/'
    #     :param callback: The function that will handle the event
    #     :param event_type:
    #     :param event_law:
    #     :return: None
    #     """
    #     pass
    #
    # @abc.abstractmethod
    # def fire_event(self, event, **callback_kwargs):
    #     """
    #     Fire an event
    #     :param event: The event topic and (optional) subtopic, separated by a '/'
    #     :param callback_kwargs: Any additional parameters to pass to the event handler
    #     :return: None
    #     """
    #     pass
