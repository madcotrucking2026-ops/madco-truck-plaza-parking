"""ERROR-level logs become a phone notification, not a line in a file.

A truck stop has no ops team tailing logs. When something that matters breaks —
a webhook that can't finalize a paid charge, an unhandled crash on the renew
path — the owner finds out today from a Slack/Discord/ntfy webhook, not next
week from an angry driver.

Design constraints, in order:
  * NEVER take the app down or slow a request: fire-and-forget daemon thread,
    short timeout, every exception swallowed.
  * NEVER melt the webhook when something fails in a loop: one alert per
    cooldown window, the rest counted and summarised in the next one.
  * requests is a direct dependency (see requirements.txt), kept small and sync.
"""

import logging
import threading
import time

import requests

logger = logging.getLogger(__name__)

COOLDOWN_SECONDS = 60


class WebhookAlertHandler(logging.Handler):
    def __init__(self, url: str):
        super().__init__(level=logging.ERROR)
        self.url = url
        self._lock2 = threading.Lock()
        self._last_sent = 0.0
        self._suppressed = 0

    def emit(self, record: logging.LogRecord) -> None:
        try:
            with self._lock2:
                now = time.monotonic()
                if now - self._last_sent < COOLDOWN_SECONDS:
                    self._suppressed += 1
                    return
                suppressed, self._suppressed = self._suppressed, 0
                self._last_sent = now

            text = f"MTPMS {record.levelname}: {self.format(record)}"
            if suppressed:
                text += f"\n(+{suppressed} more error(s) in the last minute, see logs)"
            threading.Thread(target=self._post, args=(text,), daemon=True).start()
        except Exception:  # noqa: BLE001 — alerting must never break the app
            # handleError never re-raises (respects logging.raiseExceptions) and
            # writes the traceback to stderr, so a broken alert path is visible
            # without taking down the request that logged the original error.
            self.handleError(record)

    def _post(self, text: str) -> None:
        try:
            # {"text": ...} is Slack's shape; Discord wants {"content": ...} and
            # ntfy takes a raw body. Send a superset — all three accept it.
            requests.post(self.url, json={"text": text, "content": text}, timeout=5)
        except Exception:  # noqa: BLE001
            # Runs in a daemon thread; a failed webhook post must not raise.
            # DEBUG so it never re-enters this ERROR-level handler (no recursion).
            logger.debug("MTPMS alert webhook post failed", exc_info=True)
