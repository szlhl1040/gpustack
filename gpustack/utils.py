import random
import shutil
import socket
import threading
import time
import netifaces
from typing import Callable

stop_event = threading.Event()


def is_command_available(command_name):
    """
    Use `shutil.which` to determine whether a command is available.

    Args:
    command_name (str): The name of the command to check.

    Returns:
    bool: True if the command is available, False otherwise.
    """

    return shutil.which(command_name) is not None


def normalize_route_path(path: str) -> str:
    """
    Normalize the route path by adding / at the beginning if not present.
    """

    if not path.startswith("/"):
        path = "/" + path
    return path


def get_first_non_loopback_ip():
    """
    Get the first non-loopback IP address of the machine.
    """

    for interface in netifaces.interfaces():
        addresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in addresses:
            for link in addresses[netifaces.AF_INET]:
                ip_address = link["addr"]
                if not ip_address.startswith("127.") and not ip_address.startswith(
                    "169.254."
                ):
                    return ip_address

    raise Exception("No non-loopback IP address found.")


def run_periodically(func: Callable[[], None], interval: float) -> None:
    """
    Repeatedly run a function with a given interval.

    Args:
        func: The function to be executed.
        interval: The interval time in seconds.
    """

    while not stop_event.is_set():
        func()
        time.sleep(interval)


def run_periodically_async(func: Callable[[], None], interval: float) -> None:
    """
    Repeatedly run a function asynchronously with a given interval.
    """

    threading.Thread(
        target=run_periodically,
        args=(func, interval),
        daemon=True,
    ).start()


def get_free_port(start=40000, end=41024) -> int:
    while True:
        port = random.randint(start, end)
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(("", port))
                return port
            except OSError:
                continue
