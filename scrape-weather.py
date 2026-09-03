# Web scraping: retrieve weather data from the web
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from datetime import datetime, timezone
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)

driver.get("https://www.timeanddate.com/weather/")

weather_table = WebDriverWait(driver, 20).until(
    EC.presence_of_element_located(
        (
            By.CSS_SELECTOR,
            "table.zebra.fw.tb-theme"
        )
    )
)

table_rows = weather_table.find_elements(
    By.CSS_SELECTOR,
    "tbody tr"
)

weather_data = []
scraped_at = datetime.now(timezone.utc).isoformat()

weather_data = driver.execute_script(
    """
    const rows = document.querySelectorAll(
        "table.zebra.fw.tb-theme tbody tr"
    );

    const records = [];

    for (const row of rows) {
        const cells = Array.from(
            row.querySelectorAll(":scope > td")
        );

        for (let start = 0; start + 3 < cells.length; start += 4) {
            const cityLink = cells[start].querySelector("a");
            const weatherIcon = cells[start + 2].querySelector("img");

            if (!cityLink) {
                continue;
            }

            records.push({
                "City": cityLink.textContent.trim(),
                "Local-Time": cells[start + 1].textContent.trim(),
                "Condition": weatherIcon
                    ? (weatherIcon.title || weatherIcon.alt || "")
                    : "",
                "Temperature": cells[start + 3].textContent.trim(),
                "Source-URL": cityLink.href
            });
        }
    }

    return records;
    """
)

for record in weather_data:
    record["Scraped-At"] = scraped_at

raw_weather_df = pd.DataFrame(weather_data)

raw_weather_df.to_csv(
    "raw_weather.csv",
    index=False
)

print("Raw weather data saved to raw_weather.csv")

driver.quit()

print(f"Number of city records found: {len(weather_data)}")

for record in weather_data[:5]:
    print(record)