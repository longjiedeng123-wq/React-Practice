import asyncio
from playwright.async_api import async_playwright
from sanitize_albertsons import sanitize_albertsons_flipp_item, sanitize_albertsons_j4u_item

async def intercept_albertsons_ad():
    captured_payloads = []

    async def handle_response(response):
        # Target the Flipp API (circulars) and J4U API (personalized offers)
        is_flipp_api = "dam.flippenterprise.net" in response.url and "/products" in response.url
        is_j4u_api = "offerDefinitionByOfferIds" in response.url
        
        if is_flipp_api or is_j4u_api:
            print(f"\n✅ Intercepted Target API: {response.url}")
            try:
                data = await response.json()

                if is_flipp_api and isinstance(data, list):
                    for raw_item in data:
                        clean_item = sanitize_albertsons_flipp_item(raw_item)
                        if clean_item:
                            captured_payloads.append(clean_item)
                    print(f"Successfully captured {len(str(data))} bytes of JSON.")

                elif is_j4u_api and isinstance(data, list):
                    for raw_item in data:
                        clean_item = sanitize_albertsons_j4u_item(raw_item)
                        if clean_item:
                            sanitized_items.append(clean_item)
                    print(f"Successfully sanitized {len(sanitized_items)} J4U items.")
                    
                print(f"~~~~~~~~{captured_payloads}~~~~~~~~~")

            except Exception as e:
                pass # Ignore preflight or non-JSON responses

    

    async with async_playwright() as p:
        # Launch the browser in visible mode
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        page.on("response", handle_response)

        print("Navigating to Albertsons base URL...")
        await page.goto("https://www.albertsons.com/weeklyad")
        
        # Temporary pause to allow the page to render before our next step
        await page.wait_for_timeout(3000)

        cookie_btn = page.locator("button:has-text('Continue with all')")
        await cookie_btn.wait_for(state="visible", timeout=10000)
        await cookie_btn.click()
        await page.wait_for_timeout(3000)

        print("Clicking region text to open location modal...")
        location_btn = page.locator(".s_nav_fulfillment_address-text:visible").first
        await location_btn.wait_for(state="visible", timeout=10000)
        await location_btn.click()
        await page.wait_for_timeout(3000)

        print("Entering ZIP code...")
        zip_input = page.locator("input[placeholder*='ZIP Code']")
        await zip_input.wait_for(state="visible", timeout=10000)
        await zip_input.fill("92780")
        print("Submitting search...")

        captured_payloads.clear()

        await zip_input.press("Enter")
        await page.wait_for_timeout(3000)

        print("Selecting local store...")
        select_btn = page.get_by_text("Select", exact=True).first
        await select_btn.wait_for(state="visible", timeout=10000)
        await select_btn.click()
        await page.wait_for_timeout(3000)

        # Cleanup
        await browser.close()

    return captured_payloads
    


    