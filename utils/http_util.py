import requests

from utils.logger import get_local_logger

logger = get_local_logger(__name__)


def get_session(total_retries=3, backoff_factor=0.1):
    from requests.adapters import HTTPAdapter
    from urllib3.util.retry import Retry

    s = requests.Session()
    retries = Retry(total=total_retries,
                    backoff_factor=backoff_factor,
                    status_forcelist=[500, 502, 503, 504])
    s.mount('http://', HTTPAdapter(max_retries=retries))
    s.mount('https://', HTTPAdapter(max_retries=retries))

    return s

