const EVENT_NAME = "open-command-palette";

export function openCommandPalette() {
  window.dispatchEvent(new CustomEvent(EVENT_NAME));
}

export function onOpenCommandPalette(handler: () => void) {
  window.addEventListener(EVENT_NAME, handler);
  return () => window.removeEventListener(EVENT_NAME, handler);
}
