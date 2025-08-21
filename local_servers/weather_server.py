

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import requests
from mcp.server.fastmcp import FastMCP
from mcp.shared.exceptions import McpError
from mcp.types import ErrorData, INTERNAL_ERROR, INVALID_PARAMS

# Create MCP server instance
mcp = FastMCP("weather-assistant")

# Mock weather database for demo purposes
# In production, you'd connect to a real weather API like OpenWeatherMap
MOCK_WEATHER_DATA = {
    "new york": {
        "temperature": 22,
        "condition": "Partly Cloudy",
        "humidity": 65,
        "wind_speed": 12,
        "forecast": [
            {"day": "Today", "high": 25, "low": 18, "condition": "Partly Cloudy"},
            {"day": "Tomorrow", "high": 23, "low": 16, "condition": "Sunny"},
            {"day": "Day After", "high": 27, "low": 20, "condition": "Light Rain"}
        ]
    },
    "london": {
        "temperature": 15,
        "condition": "Rainy",
        "humidity": 80,
        "wind_speed": 8,
        "forecast": [
            {"day": "Today", "high": 17, "low": 12, "condition": "Rainy"},
            {"day": "Tomorrow", "high": 19, "low": 14, "condition": "Overcast"},
            {"day": "Day After", "high": 21, "low": 15, "condition": "Partly Cloudy"}
        ]
    },
    "tokyo": {
        "temperature": 28,
        "condition": "Sunny",
        "humidity": 55,
        "wind_speed": 6,
        "forecast": [
            {"day": "Today", "high": 30, "low": 24, "condition": "Sunny"},
            {"day": "Tomorrow", "high": 32, "low": 26, "condition": "Hot"},
            {"day": "Day After", "high": 29, "low": 23, "condition": "Partly Cloudy"}
        ]
    },
    "san francisco": {
        "temperature": 18,
        "condition": "Foggy",
        "humidity": 90,
        "wind_speed": 15,
        "forecast": [
            {"day": "Today", "high": 20, "low": 15, "condition": "Foggy"},
            {"day": "Tomorrow", "high": 22, "low": 17, "condition": "Partly Cloudy"},
            {"day": "Day After", "high": 24, "low": 18, "condition": "Sunny"}
        ]
    }
}

@mcp.tool()
def get_current_weather(city: str) -> str:
    """
    Get the current weather conditions for a specified city.
    
    This tool provides real-time weather information including temperature,
    conditions, humidity, and wind speed.
    
    Args:
        city: The name of the city to get weather for
        
    Returns:
        A formatted json with current weather information
        
    Example:
        get_current_weather("New York") returns current conditions for NYC
    """
    try:
        # Normalize city name for lookup
        city_key = city.lower().strip()
        
        if city_key not in MOCK_WEATHER_DATA:
            # Return a helpful error message
            available_cities = ", ".join(MOCK_WEATHER_DATA.keys()).title()
            return f" Weather data not available for '{city}'. Available cities: {available_cities}"
        
        weather = MOCK_WEATHER_DATA[city_key]
        
        # Format the response in a user-friendly way
        response = f"""🌤️ **Current Weather in {city.title()}**

🌡️ **Temperature**: {weather['temperature']}°C
☁️ **Condition**: {weather['condition']}
💧 **Humidity**: {weather['humidity']}%
💨 **Wind Speed**: {weather['wind_speed']} km/h

*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
        
        return response
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to retrieve weather data for {city}: {str(e)}"
            )
        ) from e

@mcp.tool()
def get_weather_forecast(city: str, days: int = 3) -> str:
    """
    Get a multi-day weather forecast for a specified city.
    
    Args:
        city: The name of the city to get forecast for
        days: Number of days to forecast (1-7, default: 3)
        
    Returns:
        A formatted string with weather forecast information
    """
    try:
        # Validate input parameters
        if days < 1 or days > 7:
            return "❌ Forecast days must be between 1 and 7"
            
        city_key = city.lower().strip()
        
        if city_key not in MOCK_WEATHER_DATA:
            available_cities = ", ".join(MOCK_WEATHER_DATA.keys()).title()
            return f"❌ Weather data not available for '{city}'. Available cities: {available_cities}"
        
        weather_data = MOCK_WEATHER_DATA[city_key]
        forecast = weather_data["forecast"][:days]
        
        # Format the forecast response
        response = f"📅 **{days}-Day Weather Forecast for {city.title()}**\n\n"
        
        for day_forecast in forecast:
            response += f"**{day_forecast['day']}**\n"
            response += f"   🌡️ High: {day_forecast['high']}°C | Low: {day_forecast['low']}°C\n"
            response += f"   ☁️ Condition: {day_forecast['condition']}\n\n"
        
        response += f"*Forecast generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
        
        return response
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to retrieve forecast for {city}: {str(e)}"
            )
        ) from e

@mcp.tool()
def compare_weather(city1: str, city2: str) -> str:
    """
    Compare current weather conditions between two cities.
    
    Args:
        city1: Name of the first city
        city2: Name of the second city
        
    Returns:
        A formatted comparison of weather between the two cities
    """
    try:
        city1_key = city1.lower().strip()
        city2_key = city2.lower().strip()
        
        # Check if both cities are available
        missing_cities = []
        if city1_key not in MOCK_WEATHER_DATA:
            missing_cities.append(city1)
        if city2_key not in MOCK_WEATHER_DATA:
            missing_cities.append(city2)
        
        if missing_cities:
            available_cities = ", ".join(MOCK_WEATHER_DATA.keys()).title()
            return f"❌ Weather data not available for: {', '.join(missing_cities)}. Available cities: {available_cities}"
        
        weather1 = MOCK_WEATHER_DATA[city1_key]
        weather2 = MOCK_WEATHER_DATA[city2_key]
        
        # Create comparison
        temp_diff = weather1["temperature"] - weather2["temperature"]
        temp_comparison = f"{city1.title()} is {abs(temp_diff):.1f}°C {'warmer' if temp_diff > 0 else 'cooler'}" if temp_diff != 0 else "Both cities have the same temperature"
        
        response = f"""⚖️ **Weather Comparison: {city1.title()} vs {city2.title()}**

📊 **Temperature**
   • {city1.title()}: {weather1['temperature']}°C
   • {city2.title()}: {weather2['temperature']}°C
   • {temp_comparison}

☁️ **Conditions**
   • {city1.title()}: {weather1['condition']}
   • {city2.title()}: {weather2['condition']}

💧 **Humidity**
   • {city1.title()}: {weather1['humidity']}%
   • {city2.title()}: {weather2['humidity']}%

💨 **Wind Speed**
   • {city1.title()}: {weather1['wind_speed']} km/h
   • {city2.title()}: {weather2['wind_speed']} km/h

*Comparison made: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"""
        
        return response
        
    except Exception as e:
        raise McpError(
            ErrorData(
                code=INTERNAL_ERROR,
                message=f"Failed to compare weather between {city1} and {city2}: {str(e)}"
            )
        ) from e

@mcp.resource("weather://cities")
def list_available_cities() -> str:
    """
    List all cities for which weather data is available.
    
    This resource provides a reference of supported locations.
    """
    cities = list(MOCK_WEATHER_DATA.keys())
    response = "🏙️ **Available Cities for Weather Data**\n\n"
    
    for i, city in enumerate(cities, 1):
        response += f"{i}. {city.title()}\n"
    
    response += f"\n*Total: {len(cities)} cities available*"
    response += f"\n*Data last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*"
    
    return response

@mcp.prompt()
def weather_assistant_prompt() -> str:
    """
    A specialized prompt for weather-related assistance.
    
    This prompt configures the assistant to be helpful with weather queries
    and provides guidance on available capabilities.
    """
    print(f"prompt is being used {datetime}")
    return """You are a helpful weather assistant with access to weather information tools. 

                **Your capabilities include:**

                 **Current Weather**: Use `get_current_weather(city)` to get current conditions
                 **Forecasts**: Use `get_weather_forecast(city, days)` for multi-day predictions  
                 **Comparisons**: Use `compare_weather(city1, city2)` to compare conditions
                 **Available Cities**: Reference the `weather://cities` resource for supported locations

                **Available cities**: New York, London, Tokyo, San Francisco

                **Tips for great weather assistance:**
                - Always provide specific, actionable information
                - Include relevant details like temperature, conditions, and humidity
                - Suggest appropriate clothing or activities based on conditions
                - Offer comparisons when helpful
                - Be conversational and helpful in your responses

                Please help users with their weather-related questions using these tools!
            """

if __name__ == "__main__":
    print(" Weather Assistant MCP Server Starting...")
    print("=" * 50)
    print(" Server will run on stdio (for Claude Desktop)")
    print(" Available cities: New York, London, Tokyo, San Francisco")
    print(" Available tools:")
    print("   • get_current_weather(city)")
    print("   • get_weather_forecast(city, days)")
    print("   • compare_weather(city1, city2)")
    print(" Available resources:")
    print("   • weather://cities")
    print(" Available prompts:")
    print("   • weather_assistant_prompt")
    print("\n To use with Claude Desktop:")
    print("   1. Add server to Claude Desktop config")
    print("   2. Restart Claude Desktop")
    print("   3. Ask about weather in any supported city")
    print("\n Starting server...")
    
    # Run the server using stdio transport (standard for Claude Desktop)
    mcp.run(transport="stdio")
