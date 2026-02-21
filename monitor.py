import asyncio
import os
import requests
from playwright.async_api import async_playwright

TARGET_DATES = {
    "2026-03-09",
    "2026-03-10",
    "2026-03-11",
    "2026-03-12",
    "2026-03-13",
}

URL = "https://www.marriott.com/search/availabilityCalendar.mi?propertyCode=BOMRM&flexibleDateSearch=true&t-start=2026-03-01&t-end=2026-03-02&lengthOfStay=1&roomCount=1&numAdultsPerRoom=2"


async def check_availability():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        found_dates = set()

        async def handle_response(response):
            nonlocal found_dates
            if "phoenixShopADFSearchProductsByProperty" in response.url:
                try:
                    data = await response.json()
                    edges = data["data"]["search"]["calendarSearchByProperty"]["edges"]
                    for edge in edges:
                        start_date = edge["node"]["startDate"]
                        if start_date in TARGET_DATES:
                            found_dates.add(start_date)
                except Exception:
                    pass

        page.on("response", handle_response)

        await page.goto(URL)
        await page.wait_for_timeout(8000)

        await browser.close()

        return found_dates


def send_telegram(message):
    token = os.environ["TELEGRAM_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat_id, "text": message},
    )


if __name__ == "__main__":
    available_dates = asyncio.run(check_availability())

    if available_dates:
        msg = f"Marriott AVAILABLE for: {', '.join(sorted(available_dates))}"
        print(msg)
        if "TELEGRAM_TOKEN" in os.environ:
            send_telegram(msg)
    else:
        print("None of the target dates are available.")
