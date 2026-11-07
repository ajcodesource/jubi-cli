from requests import RequestException

from jubi.integrations.exceptions import NotificationError
from jubi.integrations.notifications import Notifications


def send_add_notification(position_name: str, company_name: str):
    try:
        notification_handler = Notifications()
        notification_handler.add_notif(position_name, company_name)

    except RequestException as r:
        raise NotificationError(f"Notification Failed {r}")
