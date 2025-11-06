# save_to_db.py
import os, json, sys
import psycopg2
from datetime import datetime
from config import DATABASE_URL

def upsert_site_page(conn, domain, full_url):
    cur = conn.cursor()
    # site
    cur.execute("SELECT id FROM sites WHERE domain = %s", (domain,))
    res = cur.fetchone()
    if res:
        site_id = res[0]
    else:
        cur.execute("INSERT INTO sites (domain) VALUES (%s) RETURNING id", (domain,))
        site_id = cur.fetchone()[0]
    # page
    cur.execute("SELECT id FROM pages WHERE full_url = %s", (full_url,))
    res = cur.fetchone()
    if res:
        page_id = res[0]
    else:
        path = "/"  # basic
        try:
            from urllib.parse import urlparse
            p = urlparse(full_url).path
            path = p if p else "/"
        except:
            pass
        cur.execute("INSERT INTO pages (site_id, path, full_url) VALUES (%s,%s,%s) RETURNING id", (site_id, path, full_url))
        page_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    return page_id

def save_result(conn, page_id, r):
    cur = conn.cursor()
    cap_time = datetime.utcnow()
    # availability
    cur.execute("INSERT INTO availability (page_id, captured_at, status_code, final_url) VALUES (%s,%s,%s,%s)",
                (page_id, cap_time, r.get("status_code"), r.get("final_url")))
    # load_time
    cur.execute("INSERT INTO load_time (page_id, captured_at, total_load_ms) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("total_load_ms")))
    # ttfb
    cur.execute("INSERT INTO ttfb (page_id, captured_at, ttfb_ms) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("ttfb_ms")))
    # num_requests
    cur.execute("INSERT INTO num_requests (page_id, captured_at, requests_count) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("num_requests")))
    # total_bytes
    cur.execute("INSERT INTO total_bytes (page_id, captured_at, bytes) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("total_bytes")))
    # images_count
    cur.execute("INSERT INTO images_count (page_id, captured_at, images_count) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("images_count")))
    # images_missing_alt
    cur.execute("INSERT INTO images_missing_alt (page_id, captured_at, missing_alt_count) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("images_missing_alt")))
    # links_count
    cur.execute("INSERT INTO links_count (page_id, captured_at, links_total, internal_links, external_links) VALUES (%s,%s,%s,%s,%s)",
                (page_id, cap_time, r.get("links_total"), r.get("internal_links"), r.get("external_links")))
    # word_count
    cur.execute("INSERT INTO word_count (page_id, captured_at, words) VALUES (%s,%s,%s)",
                (page_id, cap_time, r.get("word_count")))
    # seo_basic
    cur.execute("INSERT INTO seo_basic (page_id, captured_at, title, has_title, meta_description, has_meta_description) VALUES (%s,%s,%s,%s,%s,%s)",
                (page_id, cap_time, r.get("title"), r.get("has_title"), r.get("meta_description"), r.get("has_meta_description")))
    # resources (optional: save each)
    resources = r.get("resources", [])
    for res in resources:
        try:
            cur.execute("INSERT INTO resources (page_id, captured_at, resource_url, resource_type, status_code, size_bytes) VALUES (%s,%s,%s,%s,%s,%s)",
                        (page_id, cap_time, res.get("url"), res.get("type"), res.get("status"), res.get("size")))
        except Exception:
            pass
    conn.commit()
    cur.close()

def main():
    if not DATABASE_URL:
        print("Set DATABASE_URL in env")
        sys.exit(1)

    data = None
    # If provided a filename argument, read JSON; otherwise run scraper_playwright.py and capture output
    if len(sys.argv) > 1:
        fname = sys.argv[1]
        with open(fname, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        print("Provide JSON results file as argument.")
        sys.exit(1)

    conn = psycopg2.connect(DATABASE_URL)
    for r in data:
        url = r.get("url") or r.get("final_url")
        if not url:
            continue
        domain = url.split("//")[-1].split("/")[0]
        page_id = upsert_site_page(conn, domain, url)
        save_result(conn, page_id, r)

    conn.close()
    print("Saved to DB.")

if __name__ == "__main__":
    main()
