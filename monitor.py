import asyncio
import json
import os
from playwright.async_api import async_playwright

TARGET_DATE = "2026-03-10"
URL = "https://www.marriott.com/search/availabilityCalendar.mi?propertyCode=BOMRM&flexibleDateSearch=true&t-start=2026-03-01&t-end=2026-03-02&lengthOfStay=1&roomCount=1&numAdultsPerRoom=2"

async def check_availability():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        available = False

        async def handle_response(response):
            nonlocal available
            if "phoenixShopADFSearchProductsByProperty" in response.url:
                try:
                    data = await response.json()
                    edges = data["data"]["search"]["calendarSearchByProperty"]["edges"]
                    for edge in edges:
                        if edge["node"]["startDate"] == TARGET_DATE:
                            available = True
                except:
                    pass

        page.on("response", handle_response)

        await page.goto(URL)
        await page.wait_for_timeout(8000)

        await browser.close()

        return available

if __name__ == "__main__":
    result = asyncio.run(check_availability())

    if result:
        print("AVAILABLE")
        # Optional: send Telegram alert
    else:
        print("Not available")
