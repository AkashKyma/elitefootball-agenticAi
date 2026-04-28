from dataclasses import dataclass
import logging
import time

from app.config import settings
from app.services.logging_service import log_event, log_exception, get_logger

try:
    from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
    from playwright.sync_api import sync_playwright
except ImportError:  # pragma: no cover - dependency may not be installed in bootstrap environments.
    PlaywrightTimeoutError = TimeoutError
    sync_playwright = None


logger = get_logger(__name__)
READY_SELECTORS = {
    "transfermarkt": ["main", "div.data-header__headline-container", "div.marktwert", "body"],
    "fbref": ["section.content", "div[id^='all_stats']", "table[id*='stats']", "section[data-stat='player_stats']", "div#content", "body"],
}
CHALLENGE_MARKERS = (
    "just a moment",
    "cf-mitigated",
    "cf-browser-verification",
    "challenges.cloudflare",
    "turnstile",
    "captcha",
    "access denied",
    "checking your browser",
)

# Hardening against `navigator.webdriver` and empty `window.chrome` checks (not a full bypass).
_STEALTH_INIT_SCRIPT = r"""
(() => {
  try {
    Object.defineProperty(navigator, "webdriver", { get: () => undefined, configurable: true });
  } catch (e) {}
  try {
    if (!window.chrome) {
      Object.defineProperty(window, "chrome", { value: { runtime: {} }, configurable: true });
    }
  } catch (e) {}
})();
"""

_CHROMIUM_STEALTH_ARGS: tuple[str, ...] = (
    "--disable-blink-features=AutomationControlled",
    "--disable-dev-shm-usage",
    "--no-sandbox",
    "--disable-setuid-sandbox",
    f"--window-size={settings.scrape_viewport_width},{settings.scrape_viewport_height}",
)


@dataclass(frozen=True)
class BrowserConfig:
    headless: bool = settings.scrape_headless
    delay_seconds: float = settings.scrape_delay_seconds
    timeout_ms: int = settings.scrape_timeout_ms
    use_stealth: bool = settings.scrape_use_stealth
    user_agent: str = settings.scrape_user_agent
    channel: str | None = settings.scrape_chromium_channel
    challenge_max_wait_ms: int = settings.scrape_challenge_max_wait_ms
    viewport_width: int = settings.scrape_viewport_width
    viewport_height: int = settings.scrape_viewport_height
    locale: str = settings.scrape_locale
    timezone_id: str = settings.scrape_timezone_id
    user_data_dir: str | None = settings.scrape_user_data_dir
    hold_browser_open: bool = settings.scrape_hold_browser_open


class PlaywrightUnavailableError(RuntimeError):
    """Raised when Playwright is required but unavailable."""


def _wait_for_ready_content(page: object, source: str | None, timeout_ms: int) -> str | None:
    selectors = READY_SELECTORS.get(source or "", ["body"])
    for selector in selectors:
        try:
            page.wait_for_selector(selector, timeout=max(1000, min(timeout_ms, 5000)))
            return selector
        except PlaywrightTimeoutError:
            continue
        except Exception:
            continue
    return None


def _fbref_stats_dom_present(page: object) -> bool:
    try:
        return (
            page.locator("div[id^='all_stats_'], table[id^='stats_'], table[id*='stats_']").count()
            > 0
        )
    except Exception:
        return False


def _is_challenge_like_page(page: object) -> bool:
    try:
        title = (page.title() or "").lower()
    except Exception:
        title = ""
    try:
        snippet = (page.content() or "")[:12000].lower()
    except Exception:
        snippet = ""
    blob = f"{title} {snippet}"
    return any(marker in blob for marker in CHALLENGE_MARKERS)


def _wait_for_fbref_ready(page: object, max_wait_ms: int, log_context: dict) -> None:
    """Poll until stats tables exist, Cloudflare clears, or timeout / non-challenge grace window."""
    if max_wait_ms <= 0:
        return
    no_challenge_grace_ms = 12_000
    start = time.perf_counter()
    while (time.perf_counter() - start) * 1000 < max_wait_ms:
        if _fbref_stats_dom_present(page):
            break
        elapsed_ms = (time.perf_counter() - start) * 1000
        if (
            not _is_challenge_like_page(page)
            and not _fbref_stats_dom_present(page)
            and elapsed_ms >= no_challenge_grace_ms
        ):
            break
        try:
            page.wait_for_timeout(2000)
        except Exception:
            time.sleep(2)
    elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
    log_event(
        logger,
        logging.INFO,
        "fetch.fbref_wait",
        waited_ms=elapsed_ms,
        stats_ready=_fbref_stats_dom_present(page),
        challenge_like=_is_challenge_like_page(page),
        **log_context,
    )


def fetch_page_html(
    url: str,
    config: BrowserConfig | None = None,
    *,
    source: str | None = None,
    slug: str | None = None,
) -> str:
    """Fetch fully rendered HTML using Playwright."""

    runtime_config = config or BrowserConfig()
    start = time.perf_counter()
    context = {
        "source": source,
        "slug": slug,
        "url": url,
        "timeout_ms": runtime_config.timeout_ms,
        "headless": runtime_config.headless,
        "delay_seconds": runtime_config.delay_seconds,
        "use_stealth": runtime_config.use_stealth,
        "chromium_channel": runtime_config.channel or "bundled",
        "persistent_profile": bool(runtime_config.user_data_dir and source == "fbref"),
    }
    log_event(logger, logging.INFO, "fetch.start", **context)

    if sync_playwright is None:
        exc = PlaywrightUnavailableError(
            "Playwright is not installed. Install dependencies and run `playwright install` before scraping."
        )
        log_exception(logger, "fetch.playwright_unavailable", exc, **context)
        raise exc

    try:
        with sync_playwright() as playwright:
            log_event(logger, logging.INFO, "fetch.browser_launch", **context)
            context_kwargs: dict = {
                "user_agent": runtime_config.user_agent,
                "viewport": {
                    "width": runtime_config.viewport_width,
                    "height": runtime_config.viewport_height,
                },
                "locale": runtime_config.locale,
                "timezone_id": runtime_config.timezone_id,
                "extra_http_headers": {
                    "Accept-Language": "en-US,en;q=0.9",
                    "Upgrade-Insecure-Requests": "1",
                },
            }
            launch_common_kwargs: dict = {
                "headless": runtime_config.headless,
                "args": list(_CHROMIUM_STEALTH_ARGS),
            }
            if runtime_config.channel:
                launch_common_kwargs["channel"] = runtime_config.channel
            if runtime_config.user_data_dir and source == "fbref":
                browser_context = playwright.chromium.launch_persistent_context(
                    runtime_config.user_data_dir,
                    **launch_common_kwargs,
                    **context_kwargs,
                )
                managed_browser = None
                if runtime_config.use_stealth:
                    browser_context.add_init_script(_STEALTH_INIT_SCRIPT)
                if runtime_config.hold_browser_open:
                    log_event(
                        logger,
                        logging.INFO,
                        "fetch.manual_intervention_window",
                        wait_seconds=20,
                        reason="allow challenge solve in persistent profile",
                        **context,
                    )
                    time.sleep(20)
                page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
            else:
                managed_browser = playwright.chromium.launch(**launch_common_kwargs)
                browser_context = managed_browser.new_context(**context_kwargs)
                if runtime_config.use_stealth:
                    browser_context.add_init_script(_STEALTH_INIT_SCRIPT)
                page = browser_context.new_page()
            try:
                page.set_default_timeout(runtime_config.timeout_ms)
                log_event(logger, logging.INFO, "fetch.goto", **context)
                page.goto(url, wait_until="domcontentloaded")
                try:
                    page.wait_for_load_state("networkidle")
                except PlaywrightTimeoutError:
                    # Some sites keep background network activity alive indefinitely.
                    # Continue with available DOM instead of failing the entire scrape.
                    log_event(logger, logging.WARNING, "fetch.networkidle_timeout", **context)
                if source == "fbref":
                    _wait_for_fbref_ready(page, runtime_config.challenge_max_wait_ms, context)
                ready_selector = _wait_for_ready_content(page, source, runtime_config.timeout_ms)
                if runtime_config.delay_seconds > 0:
                    time.sleep(runtime_config.delay_seconds)
                html = page.content()
                try:
                    title = page.title() or ""
                except Exception:
                    title = ""
                challenge_blob = (title + " " + (html[:12000] if html else "")).lower()
                challenge_detected = any(marker in challenge_blob for marker in CHALLENGE_MARKERS)
                if challenge_detected and "incompatible" in challenge_blob:
                    log_event(
                        logger,
                        logging.WARNING,
                        "fetch.cloudflare_incompatible_notice",
                        hint=(
                            "Cloudflare reported incompatible extension or blocked verification; "
                            "ensure challenges.cloudflare.com is reachable (VPN/firewall/DNS/antivirus) "
                            "and try SCRAPE_CHROMIUM_CHANNEL=chrome with SCRAPE_USER_DATA_DIR persistent profile.",
                        ),
                        **context,
                    )
                elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
                log_event(
                    logger,
                    logging.INFO,
                    "fetch.render_complete",
                    html_length=len(html),
                    elapsed_ms=elapsed_ms,
                    ready_selector=ready_selector,
                    challenge_detected=challenge_detected,
                    page_title=title,
                    **context,
                )
                if not ready_selector:
                    log_event(logger, logging.WARNING, "fetch.selector_missing", elapsed_ms=elapsed_ms, **context)
                if challenge_detected:
                    log_event(logger, logging.WARNING, "fetch.challenge_detected", elapsed_ms=elapsed_ms, page_title=title, **context)
                log_event(logger, logging.INFO, "fetch.success", html_length=len(html), elapsed_ms=elapsed_ms, **context)
                return html
            finally:
                browser_context.close()
                if managed_browser is not None:
                    managed_browser.close()
    except Exception as exc:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 2)
        log_exception(logger, "fetch.failed", exc, elapsed_ms=elapsed_ms, **context)
        raise
