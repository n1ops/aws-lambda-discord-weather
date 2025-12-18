import os
import json
import urllib.request
import urllib.error

# Open-Meteo forecast endpoint (no API key required)
OPEN_METEO_URL = (
    "https://api.open-meteo.com/v1/forecast"
    "?latitude={lat}&longitude={lon}"
    "&daily=weathercode,temperature_2m_max,temperature_2m_min,precipitation_probability_max"
    "&current_weather=true"
    "&temperature_unit=fahrenheit"
    "&wind_speed_unit=mph"
    "&timezone=America%2FNew_York"
)

def fetch_json(url: str) -> dict:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "aws-lambda-weather-bot/1.0",
            "Accept": "application/json"
        }
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))

def weathercode_to_text(code: int) -> str:
    if code == 0:
        return "Clear"
    if code in (1, 2):
        return "Partly Cloudy"
    if code == 3:
        return "Overcast"
    if code in (45, 48):
        return "Fog"
    if code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
        return "Rain"
    if code in (71, 73, 75, 85, 86):
        return "Snow"
    if code in (95, 96, 99):
        return "Thunderstorms"
    return "Mixed Conditions"

def post_to_discord(webhook_url: str, message: str) -> None:
    payload = json.dumps({"content": message}).encode("utf-8")

    req = urllib.request.Request(
        webhook_url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": "aws-lambda-weather-bot/1.0",
            "Accept": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            resp.read()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        raise RuntimeError(f"Discord webhook failed ({e.code}): {body}")

def lambda_handler(event, context):
    # Required environment variables (strip defensively)
    lat = os.environ["LAT"].strip()
    lon = os.environ["LON"].strip()
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"].strip()

    # Fetch weather
    data = fetch_json(OPEN_METEO_URL.format(lat=lat, lon=lon))

    current = data.get("current_weather", {})
    daily = data.get("daily", {})
    today = 0

    date = daily.get("time", [""])[today]
    high = daily.get("temperature_2m_max", [None])[today]
    low = daily.get("temperature_2m_min", [None])[today]
    precip_prob = daily.get("precipitation_probability_max", [None])[today]
    weather_code = daily.get("weathercode", [None])[today]

    condition = weathercode_to_text(int(weather_code)) if weather_code is not None else "Unknown"
    now_temp = current.get("temperature")
    wind = current.get("windspeed")

    precip_text = (
        "Precipitation unlikely"
        if precip_prob is not None and precip_prob < 30
        else f"Precipitation possible (max {precip_prob}%)"
    )

    message = (
        f"**Daily Weather — {date}**\n"
        f"Now: **{now_temp}°F**, wind **{wind} mph**\n"
        f"Today: **{condition}**\n"
        f"Low **{low}°F** / High **{high}°F**\n"
        f"{precip_text}"
    )

    post_to_discord(webhook_url, message)

    return {
        "status": "success",
        "date": date,
        "location": {"lat": lat, "lon": lon}
    }
