#     __ __     __  ___      _ ___
#    / // /__  / /_/ _ \____(_) _/_ __
#   / _  / _ \/ __/ // / __/ / _/ // /
#  /_//_/\___/\__/____/_/ /_/_/ \_, /
#                              /___/
#    Licensed under the GNU AGPLv3.


# Weather code to emoji mapping
WEATHER_ICONS = {
    "01d": "☀️", "01n": "🌙",
    "02d": "⛅", "02n": "☁️",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️",
    "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️",
}


def _format_temp(temp: float) -> str:
    """Format temperature with sign."""
    if temp > 0:
        return f"+{temp:.1f}°C"
    return f"{temp:.1f}°C"


def _format_wind(deg: float) -> str:
    """Convert wind degrees to direction."""
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    idx = round(deg / 45) % 8
    return dirs[idx]


async def weather_cmd(self):
    """Get current weather — usage: .weather <city>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.weather <city></code>\n\n"
            "📝 <b>Examples:</b>\n"
            "• <code>.weather Moscow</code>\n"
            "• <code>.weather London, UK</code>\n"
            "• <code>.weather Tokyo</code>"
        )
        return

    city = args[1].strip()
    status_msg = await message.edit(f"🌍 <b>Fetching weather for</b> <code>{city}</code>...")

    try:
        import aiohttp

        # Using wttr.in — free, no API key needed
        url = f"https://wttr.in/{city}?format=j1&lang=en"
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await status_msg.edit(
                        f"❌ <b>City not found!</b>\n\n"
                        f"🔍 <code>{city}</code>"
                    )
                    return
                data = await resp.json()

        current = data["current_condition"][0]
        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]

        temp = float(current["temp_C"])
        feels = float(current["FeelsLikeC"])
        humidity = current["humidity"]
        desc = current["weatherDesc"][0]["value"]
        wind_speed = current["windspeedKmph"]
        wind_dir = _format_wind(float(current["winddirDegree"]))
        visibility = current["visibility"]
        pressure = current["pressure"]
        uv = current["uvIndex"]
        icon_code = current["weatherIconUrl"][0]["value"].split(
            "/")[-1].replace(".png", "")
        icon = WEATHER_ICONS.get(icon_code, "🌡️")

        # Sunrise / sunset from today's astronomy
        astro = data["weather"][0]["astronomy"][0]
        sunrise = astro["sunrise"]
        sunset = astro["sunset"]

        result = (
            f"{icon} <b>Weather in {city_name}, {country}</b>\n"
            f"━━━━━━━━━━━━━━━\n\n"
            f"🌡️ <b>Temperature:</b> <code>{_format_temp(temp)}</code>\n"
            f"🤔 <b>Feels like:</b> <code>{_format_temp(feels)}</code>\n"
            f"📋 <b>Condition:</b> <code>{desc}</code>\n"
            f"💧 <b>Humidity:</b> <code>{humidity}%</code>\n"
            f"💨 <b>Wind:</b> <code>{wind_speed} km/h {wind_dir}</code>\n"
            f"👁️ <b>Visibility:</b> <code>{visibility} km</code>\n"
            f"📊 <b>Pressure:</b> <code>{pressure} hPa</code>\n"
            f"☀️ <b>UV Index:</b> <code>{uv}</code>\n\n"
            f"━━━━━━━━━━━━━━━\n"
            f"🌅 <b>Sunrise:</b> <code>{sunrise}</code>\n"
            f"🌇 <b>Sunset:</b> <code>{sunset}</code>"
        )

        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")


async def forecast_cmd(self):
    """Get 3-day weather forecast — usage: .forecast <city>"""
    message = self.message
    args = message.text.split(maxsplit=1)

    if len(args) < 2:
        await message.edit(
            "❌ <b>Usage:</b> <code>.forecast <city></code>\n\n"
            "📝 <b>Example:</b> <code>.forecast Moscow</code>"
        )
        return

    city = args[1].strip()
    status_msg = await message.edit(f"🌍 <b>Fetching forecast for</b> <code>{city}</code>...")

    try:
        import aiohttp

        url = f"https://wttr.in/{city}?format=j1&lang=en"
        timeout = aiohttp.ClientTimeout(total=10)

        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url) as resp:
                if resp.status != 200:
                    await status_msg.edit(f"❌ <b>City not found:</b> <code>{city}</code>")
                    return
                data = await resp.json()

        area = data["nearest_area"][0]
        city_name = area["areaName"][0]["value"]
        country = area["country"][0]["value"]

        result = f"📅 <b>3-Day Forecast — {city_name}, {country}</b>\n"
        result += "━━━━━━━━━━━━━━━\n\n"

        for day_data in data["weather"]:
            date = day_data["date"]
            max_t = day_data["maxtempC"]
            min_t = day_data["mintempC"]

            # Get most common weather description from hourly
            descs = [h["weatherDesc"][0]["value"] for h in day_data["hourly"]]
            main_desc = max(set(descs), key=descs.count)

            # Get icon from midday (index 4 = ~12:00)
            icon_code = day_data["hourly"][4]["weatherIconUrl"][0]["value"].split(
                "/")[-1].replace(".png", "")
            icon = WEATHER_ICONS.get(icon_code, "🌡️")

            # Average humidity & wind
            avg_hum = sum(int(h["humidity"])
                          for h in day_data["hourly"]) // len(day_data["hourly"])
            avg_wind = sum(int(h["windspeedKmph"])
                           for h in day_data["hourly"]) // len(day_data["hourly"])

            result += (
                f"{icon} <b>{date}</b>\n"
                f"  🌡️ <code>{_format_temp(float(min_t))} → {_format_temp(float(max_t))}</code>\n"
                f"  📋 <code>{main_desc}</code>\n"
                f"  💧 <code>{avg_hum}%</code> | 💨 <code>{avg_wind} km/h</code>\n\n"
            )

        result += "━━━━━━━━━━━━━━━"
        await status_msg.edit(result)

    except ImportError:
        await status_msg.edit(
            "❌ <b>aiohttp is required!</b>\n\n"
            "Install it: <code>pip install aiohttp</code>"
        )
    except Exception as e:
        await status_msg.edit(f"❌ <b>Error:</b> <code>{e}</code>")
