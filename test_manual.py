import asyncio
import json

from app.tools.weather import (
    get_current_weather,
    get_daily_forecast,
)


async def main() -> None:
    current = await get_current_weather("London")
    print("CURRENT WEATHER")
    print(json.dumps(current, indent=2))

    forecast = await get_daily_forecast(
        location="London",
        days=5,
    )
    print("\nFORECAST")
    print(json.dumps(forecast, indent=2))


if __name__ == "__main__":
    asyncio.run(main())