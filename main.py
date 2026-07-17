"""
Turnstile solver microservice using FastAPI and SeleniumBase CDP mode.
Solves Cloudflare Turnstile captchas using a stealth browser.
"""

import os
import time
import logging
import traceback
from typing import Optional
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Turnstile Solver API")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Target details
SITEKEY = "0x4AAAAAADuXG2nt8DMgL_NF"
PAGEURL = "https://tma.foxigrow.com"


def parse_proxy(raw_proxy: str) -> Optional[str]:
    """Parse proxy from HOST:PORT:USER:PASS to USER:PASS@HOST:PORT format."""
    if not raw_proxy:
        return None
    try:
        parts = raw_proxy.strip().split(':')
        if len(parts) == 4:
            host, port, user, password = parts
            return f"{user}:{password}@{host}:{port}"
        else:
            logger.warning(f"Unsupported proxy format. Expected HOST:PORT:USER:PASS, got {len(parts)} parts.")
            return None
    except Exception as e:
        logger.error(f"Failed to parse proxy: {e}")
        return None


def solve_turnstile(proxy_str: Optional[str] = None) -> Optional[str]:
    """Launch a stealth browser via SeleniumBase CDP and solve Turnstile."""
    from seleniumbase import sb_cdp

    logger.info("Launching SeleniumBase UC browser...")
    sb = None
    try:
        chrome_args = {
            "guest": True,
            "binary_location": "/usr/bin/chromium",
        }
        if proxy_str:
            logger.info("Applying proxy to browser...")
            chrome_args["proxy"] = proxy_str

        sb = sb_cdp.Chrome(**chrome_args)

        logger.info(f"Navigating to {PAGEURL}...")
        sb.open(PAGEURL)
        time.sleep(2)

        logger.info("Injecting Turnstile widget...")
        inject_js = (
            "const container = document.createElement('div');"
            "container.id = 'cf-turnstile-container';"
            "container.style.cssText = 'position:fixed;top:10px;left:10px;z-index:999999;background:#fff;padding:10px;';"
            "document.body.appendChild(container);"
            "const script = document.createElement('script');"
            "script.src = 'https://challenges.cloudflare.com/turnstile/v0/api.js?render=explicit&onload=__onTurnstileReady';"
            "window.__onTurnstileReady = () => {"
            "  window.turnstile.render('#cf-turnstile-container', {"
            "    sitekey: '" + SITEKEY + "',"
            "    callback: (token) => { window.__turnstileToken = token; },"
            "    'error-callback': (code) => { window.__turnstileError = String(code); }"
            "  });"
            "};"
            "document.head.appendChild(script);"
        )
        sb.evaluate(inject_js)

        logger.info("Waiting for Turnstile auto-solve...")
        for i in range(60):  # 30s timeout (60 * 0.5s)
            time.sleep(0.5)
            token = sb.evaluate("window.__turnstileToken || null")
            if token and token != "null":
                logger.info(f"SUCCESS! Solved in {(i + 1) * 0.5}s")
                return token

            error = sb.evaluate("window.__turnstileError || null")
            if error and error != "null":
                logger.error(f"Turnstile error: {error}")
                return None

        logger.error("Timeout waiting for token after 30s")
        return None

    except Exception as e:
        logger.error(f"Error during solve: {e}")
        logger.error(traceback.format_exc())
        return None
    finally:
        if sb:
            try:
                sb.quit()
            except Exception:
                pass


@app.get("/")
def root():
    """Health check endpoint."""
    return {"status": "ok", "service": "Turnstile Solver API"}


@app.get("/getToken")
def get_token():
    """Solve a Turnstile captcha and return the token."""
    try:
        raw_proxy = os.environ.get("PROXY_URL", "")
        proxy_config = parse_proxy(raw_proxy)

        start_time = time.time()
        token = solve_turnstile(proxy_config)
        elapsed = time.time() - start_time

        if token:
            return JSONResponse(content={
                "success": True,
                "token": token,
                "elapsed_s": round(elapsed, 2)
            })
        else:
            return JSONResponse(
                content={"success": False, "error": "Failed to solve Turnstile"},
                status_code=503
            )
    except Exception as e:
        tb = traceback.format_exc()
        logger.error(f"Unhandled exception in getToken: {tb}")
        return JSONResponse(
            content={"success": False, "error": str(e), "traceback": tb},
            status_code=500
        )


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
