# AWS Lambda Discord Weather Bot

A lightweight AWS Lambda function that sends a concise daily weather summary
to a Discord channel using a webhook.

The function runs on a schedule (via Amazon EventBridge Scheduler), retrieves
current conditions and a same-day forecast from Open-Meteo, and posts a
human-readable summary to Discord.

---

## Features

- Serverless (AWS Lambda)
- Scheduled daily execution
- No API keys required (Open-Meteo)
- Discord webhook integration
- Handles current conditions + daily forecast
- Safe secret handling via environment variables
- Designed to run reliably with minimal maintenance

---

## Example Output

Daily Weather — 2025-12-17
Now: 34°F, wind 5 mph
Today: Partly Cloudy
Low 28°F / High 42°F
Precipitation unlikely