import pytest

from app.tools.weather import get_current_weather


@pytest.mark.asyncio
async def test_current_weather_requires_location() -> None:
    with pytest.raises(ValueError):
        await get_current_weather("")
        