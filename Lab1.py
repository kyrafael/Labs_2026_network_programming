import requests
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# National Bank of Ukraine API
API_URL = "https://bank.gov.ua/NBU_Exchange/exchange_site"

end_date = datetime.today()
start_date = end_date - timedelta(days=30)
params = {
    "start": start_date.strftime("%Y%m%d"),
    "end": end_date.strftime("%Y%m%d"),
    "valcode": "usd",
    "sort": "exchangedate",
    "order": "asc",
    "json": ""
}
def get_currency_rates(currency):
    params["valcode"] = currency
    response = requests.get(
        API_URL,
        params=params,
        timeout=15
    )
    response.raise_for_status()
    data = response.json()

    dates = []
    rates = []

    for item in data:
        date = datetime.strptime(
            item["exchangedate"], "%d.%m.%Y"
        )
        dates.append(date)
        rates.append(float(item["rate"]))

    return dates, rates
try:

    usd_dates, usd_rates = get_currency_rates("usd")
    eur_dates, eur_rates = get_currency_rates("eur")

    if not usd_rates or not eur_rates:
        raise ValueError("The API returned no data")

    plt.figure(figsize=(11, 6))

    plt.plot(
        usd_dates, usd_rates,
        label="USD / UAH",
        color="blue",
        marker="o",
        markersize=3
    )

    plt.plot(
        eur_dates, eur_rates,
        label="EUR / UAH",
        color="green",
        marker="o",
        markersize=3
    )

    plt.title("Exchange Rate Changes Over the Last 30 Days")
    plt.xlabel("Date")
    plt.ylabel("Exchange Rate (UAH)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig("currency_chart.png", dpi=300)
    plt.show()
    print("Exchange rate chart created successfully!")

except requests.RequestException as error:
    print("HTTP request error:", error)

except (ValueError, KeyError) as error:
    print("Data processing error:", error)