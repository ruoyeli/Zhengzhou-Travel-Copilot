import httpx
from langchain_core.tools import tool

WEATHER_MAP = {
    0: "晴天", 1: "基本晴朗", 2: "部分多云", 3: "阴天",
    51: "小毛毛雨", 53: "毛毛雨", 61: "小雨", 63: "中雨",
    65: "大雨", 71: "小雪", 73: "中雪", 75: "大雪",
    80: "阵雨", 95: "雷暴"
}

@tool
async def get_weather(city: str) -> str:
    """
    当用户询问任何天气、温度、是否适合出行时必须调用此工具。
    city参数只填城市名（如郑州），不填景点名。
    """
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            # 第一步：城市转坐标
            geo_res = await client.get(
                "https://geocoding-api.open-meteo.com/v1/search",
                params={"name": city, "count": 1, "language": "zh", "format": "json"}
            )
            geo_data = geo_res.json()
            if not geo_data.get("results"):
                return f"未找到城市：{city}"

            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            city_name = geo_data["results"][0]["name"]

            # 第二步：查询真实天气
            weather_res = await client.get(
                "https://api.open-meteo.com/v1/forecast",
                params={
                    "latitude": lat,
                    "longitude": lon,
                    "daily": "weathercode,temperature_2m_max,temperature_2m_min",
                    "timezone": "Asia/Shanghai",
                    "forecast_days": 3
                }
            )
            daily = weather_res.json()["daily"]

            result = f"{city_name} 未来3天天气（数据来源：Open-Meteo）：\n"
            for i in range(3):
                desc = WEATHER_MAP.get(daily["weathercode"][i], "未知天气")
                result += (
                    f"  {daily['time'][i]}："
                    f"{desc}，"
                    f"{daily['temperature_2m_min'][i]}°C ~ "
                    f"{daily['temperature_2m_max'][i]}°C\n"
                )
            return result

        except Exception as e:
            return f"天气查询失败：{e}"