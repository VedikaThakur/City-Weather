import streamlit as st
import requests
from typing import Dict, Any
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime, timedelta

# Streamlit page configuration
st.set_page_config(page_title="Real-Time Weather Predictor", layout="wide")

# Hardcoded API key (replace with your own OpenWeatherMap API key)
API_KEY = '2dfebf04778af8a55b1470a6b0d2d7f8'

# Function to fetch weather data from OpenWeatherMap
def get_weather_data(city: str) -> Dict[str, Any]:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 401:
            return {"error": "Invalid API key. Please check your OpenWeatherMap API key."}
        elif response.status_code == 404:
            return {"error": "City not found. Please check the city name."}
        else:
            return {"error": f"Error fetching data: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": f"Network error: {str(e)}"}

# Function to determine weather verdict based on conditions
def get_weather_verdict(weather_data: Dict[str, Any]) -> str:
    try:
        weather_main = weather_data.get('weather', [{}])[0].get('main', '').lower()
        if "rain" in weather_main:
            return "Rainy"
        elif "clear" in weather_main:
            return "Sunny"
        elif "cloud" in weather_main:
            return "Cloudy"
        elif "snow" in weather_main:
            return "Snowy"
        else:
            return "Partly Cloudy"
    except (IndexError, TypeError):
        return "Unknown"

# Function to create mock hourly data for plotting (based on current data)
def create_mock_hourly_data(weather_data: Dict[str, Any]) -> pd.DataFrame:
    current_temp = weather_data.get('main', {}).get('temp', 20.0)  # Default to 20.0 if missing
    current_humidity = weather_data.get('main', {}).get('humidity', 50.0)  # Default to 50.0
    times = [datetime.now() + timedelta(hours=i) for i in range(6)]
    temps = [current_temp + i * 0.5 for i in range(-3, 3)]  # Mock temp variation
    humidities = [current_humidity + i * 2 for i in range(-3, 3)]  # Mock humidity variation
    return pd.DataFrame({
        'Time': times,
        'Temperature (°C)': temps,
        'Humidity (%)': humidities
    })

# Streamlit UI
st.title("🌤️ Real-Time Weather Predictor")
st.write("Enter a city to get real-time weather data and predictions.")

# Input for city
city = st.text_input("Enter City Name", value="London")

if st.button("Get Weather"):
    if not city.strip():
        st.error("Please enter a valid city name.")
    else:
        weather_data = get_weather_data(city)
        if "error" in weather_data:
            st.error(weather_data["error"])
            if "API key" in weather_data["error"]:
                st.info("To fix this, ensure the API key in the code is valid. Sign up at https://openweathermap.org/ to get a free API key.")
        else:
            # Extract data with error handling
            try:
                main = weather_data.get('main', {})
                temp = main.get('temp', 'N/A')
                humidity = main.get('humidity', 'N/A')
                pressure = main.get('pressure', 'N/A')
                wind = weather_data.get('wind', {})
                wind_speed = wind.get('speed', 'N/A')
                weather = weather_data.get('weather', [{}])
                description = weather[0].get('description', 'N/A').capitalize() if weather else 'N/A'
                verdict = get_weather_verdict(weather_data)

                # Display current weather
                st.subheader(f"Weather in {city.capitalize()}")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Temperature", f"{temp} °C" if temp != 'N/A' else 'N/A')
                col2.metric("Humidity", f"{humidity}%" if humidity != 'N/A' else 'N/A')
                col3.metric("Pressure", f"{pressure} hPa" if pressure != 'N/A' else 'N/A')
                col4.metric("Wind Speed", f"{wind_speed} m/s" if wind_speed != 'N/A' else 'N/A')
                st.markdown(f"**Description**: {description}")
                st.markdown(f"**Verdict**: {verdict}")

                # Create and display graph
                st.subheader("6-Hour Weather Trend (Mock)")
                df = create_mock_hourly_data(weather_data)
                
                fig, ax1 = plt.subplots(figsize=(10, 5))
                ax1.plot(df['Time'], df['Temperature (°C)'], color='tab:red', label='Temperature (°C)')
                ax1.set_xlabel('Time')
                ax1.set_ylabel('Temperature (°C)', color='tab:red')
                ax1.tick_params(axis='y', labelcolor='tab:red')
                ax1.grid(True)

                ax2 = ax1.twinx()
                ax2.plot(df['Time'], df['Humidity (%)'], color='tab:blue', label='Humidity (%)')
                ax2.set_ylabel('Humidity (%)', color='tab:blue')
                ax2.tick_params(axis='y', labelcolor='tab:blue')

                plt.title(f"Weather Trend for {city.capitalize()}")
                fig.tight_layout()
                st.pyplot(fig)
            except (KeyError, TypeError, IndexError) as e:
                st.error(f"Error processing weather data: {str(e)}. Please try again or check the API response.")
