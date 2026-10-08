from scholarly import scholarly
import json
from datetime import datetime, timezone
import os
import time

GOOGLE_SCHOLAR_ID = os.environ["GOOGLE_SCHOLAR_ID"]
MAX_ATTEMPTS = 3
WAIT_SECONDS = 30


def fetch_author():
    last_error = None

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            print(f"Attempt {attempt}/{MAX_ATTEMPTS}")

            # Google Scholar's author endpoint is queried directly.
            # No free proxy pool is used because unreliable public proxies
            # were the main source of intermittent crawler failures.
            author = scholarly.search_author_id(GOOGLE_SCHOLAR_ID)
            scholarly.fill(author, sections=["basics", "indices"])

            cited_by = author.get("citedby")
            if cited_by is None:
                raise RuntimeError("Google Scholar response does not contain 'citedby'.")

            print(f"Successfully retrieved citation count: {cited_by}")
            return author

        except Exception as exc:
            last_error = exc
            print(f"Attempt {attempt} failed: {exc}")
            if attempt < MAX_ATTEMPTS:
                time.sleep(WAIT_SECONDS)

    raise RuntimeError(f"Google Scholar crawler failed after {MAX_ATTEMPTS} attempts: {last_error}")


author = fetch_author()
updated = datetime.now(timezone.utc).isoformat()

# Keep the complete author record for compatibility with the existing data file.
author["updated"] = updated

os.makedirs("results", exist_ok=True)

with open("results/gs_data.json", "w", encoding="utf-8") as outfile:
    json.dump(author, outfile, ensure_ascii=False, indent=2)

shieldio_data = {
    "schemaVersion": 1,
    "label": "citations",
    "message": str(author["citedby"]),
}

with open("results/gs_data_shieldsio.json", "w", encoding="utf-8") as outfile:
    json.dump(shieldio_data, outfile, ensure_ascii=False, indent=2)

print(f"Updated Google Scholar citation data: {author['citedby']}")
print(f"Updated at: {updated}")
