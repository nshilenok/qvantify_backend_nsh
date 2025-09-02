import os
import resource
import tempfile
import logging
import time

logger = logging.getLogger(__name__)

def check_fd_usage():
    tmp_fd, tmp_path = tempfile.mkstemp()
    logger.debug(f"Temporary file opened with FD: {tmp_fd}")

    open_fds = [fd for fd in range(resource.getrlimit(resource.RLIMIT_NOFILE)[0]) if os.path.exists(f"/proc/self/fd/{fd}")]

    soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
    logger.info(f"[HEARTBEAT] Soft limit for FDs: {soft_limit}, Hard limit for FDs: {hard_limit},  Total open file descriptors: {len(open_fds)}")

    os.close(tmp_fd)
    logger.debug(f"Temporary file descriptor {tmp_fd} closed")

    os.remove(tmp_path)
    logger.debug(f"Temporary file {tmp_path} deleted")

    if len(open_fds) < soft_limit:
        logger.debug("Current open FDs are within the system limit.")
    else:
        logger.warn("[HEARTBEAT] Warning: Current open FDs are at or near the system limit!")

def heartbeat():
        check_fd_usage()