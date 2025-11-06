# scraper_playwright.py
import asyncio, hashlib, json, time
from playwright.async_api import async_playwright
from urllib.parse import urlparse
from config import PAGES

async def scrape_one(page, url, timeout=30000):
    await page.goto(url, wait_until="load", timeout=timeout)
    # Title, meta
    title = await page.title()
    md = await page.query_selector("meta[name='description']")
    meta_desc = None
    if md:
        meta_desc = await md.get_attribute("content")
    # H1s, imgs
    h1s = await page.query_selector_all("h1")
    imgs = await page.query_selector_all("img")
    images_missing_alt = 0
    for img in imgs:
        alt = await img.get_attribute("alt")
        if not alt or not alt.strip():
            images_missing_alt += 1
    # Links
    anchors = await page.query_selector_all("a[href]")
    links = [await a.get_attribute("href") for a in anchors]
    parsed = urlparse(url)
    domain = f"{parsed.scheme}://{parsed.netloc}"
    internal = 0
    for l in links:
        if not l: continue
        if l.startswith("/") or l.startswith(domain) or parsed.netloc in l:
            internal += 1
    external = len(links) - internal
    # Text / word count
    body_text = await page.inner_text("body")
    word_count = len(body_text.split())
    # resources & timing
    total_bytes = 0
    req_count = 0
    resources = []
    # get performance timing if available
    try:
        timing = await page.evaluate("() => window.performance.timing.toJSON ? window.performance.timing.toJSON() : window.performance.timing")
    except Exception:
        timing = None
    # use route for responses: gather responses after navigation using requestfinished events
    async def on_request_finished(request):
        nonlocal total_bytes, req_count, resources
        try:
            resp = await request.response()
            if not resp:
                return
            headers = resp.headers
            size = 0
            cl = headers.get("content-length")
            if cl and cl.isdigit():
                size = int(cl)
            else:
                try:
                    body = await resp.body()
                    size = len(body)
                except Exception:
                    size = 0
            total_bytes += size
            req_count += 1
            resources.append({"url": request.url, "type": request.resource_type, "status": resp.status, "size": size})
        except Exception:
            pass

    page.on("requestfinished", on_request_finished)

    # Wait a short moment to let requests finish
    await asyncio.sleep(1)

    # compute total_load_ms and ttfb if timing present
    total_load_ms = None
    ttfb_ms = None
    if timing:
        try:
            navigation_start = timing.get("navigationStart") or timing.get("fetchStart")
            load_event_end = timing.get("loadEventEnd")
            response_start = timing.get("responseStart")
            if navigation_start and load_event_end:
                total_load_ms = int(load_event_end - navigation_start)
            if navigation_start and response_start:
                ttfb_ms = int(response_start - navigation_start)
        except Exception:
            pass

    # status code & final url
    try:
        main_req = None
        for r in resources:
            if r["url"].rstrip("/") == url.rstrip("/"):
                main_req = r
                break
        # fallback: page.url
        final_url = page.url
        status_code = None
        # get response of main navigation
        try:
            nav_resp = await page.wait_for_response(lambda resp: resp.url.rstrip("/") == final_url.rstrip("/"), timeout=2000)
            status_code = nav_resp.status
        except Exception:
            status_code = None
    except Exception:
        final_url = page.url
        status_code = None

    return {
        "url": url,
        "final_url": final_url,
        "status_code": status_code,
        "title": title,
        "meta_description": meta_desc,
        "has_title": bool(title and title.strip()),
        "has_meta_description": bool(meta_desc and meta_desc.strip()),
        "h1_count": len(h1s),
        "images_count": len(imgs),
        "images_missing_alt": images_missing_alt,
        "links_total": len(links),
        "internal_links": internal,
        "external_links": external,
        "word_count": word_count,
        "num_requests": req_count,
        "total_bytes": total_bytes,
        "total_load_ms": total_load_ms,
        "ttfb_ms": ttfb_ms,
        "resources": resources
    }

async def run_all():
    results = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        for url in PAGES:
            try:
                r = await scrape_one(page, url)
                results.append(r)
            except Exception as e:
                results.append({"url": url, "error": str(e)})
        await browser.close()
    print(json.dumps(results, indent=2))

if __name__ == "__main__":
    asyncio.run(run_all())
