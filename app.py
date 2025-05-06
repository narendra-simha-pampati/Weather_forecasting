import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
from datetime import datetime

# Your OpenWeatherMap API key
API_KEY = "3a34e2e4157d880a49b2b2c2f801b992"

# Function to fetch current weather
def get_current_weather(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None, f"Error fetching current weather for {city}: {response.status_code}"
    data = response.json()
    return pd.DataFrame([{
        'ds': datetime.now().date(),
        'temp': data['main']['temp'],
        'max_temp': data['main']['temp_max']
    }]), None

# Function to fetch 5-day forecast
def get_forecast(city, api_key):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
    response = requests.get(url)
    if response.status_code != 200:
        return None, f"Error fetching forecast for {city}: {response.status_code}"
    data = response.json()
    forecast_data = []
    for entry in data['list']:
        date = datetime.fromtimestamp(entry['dt']).date()
        max_temp = entry['main']['temp_max']
        rain_chance = entry.get('pop', 0) * 100
        forecast_data.append({'ds': date, 'max_temp': max_temp, 'rain_chance': rain_chance})
    
    df = pd.DataFrame(forecast_data)
    daily_forecast = df.groupby('ds').agg({
        'max_temp': 'max',
        'rain_chance': 'max'
    }).reset_index()
    return daily_forecast, None

# Streamlit app
st.title("My Weather Forecast")
city = st.text_input("City:", value="New York City", placeholder="Type a city name (e.g., London, Tokyo)")
if st.button("Get Weather"):
    if not city:
        st.error("Please enter a city name.")
    else:
        # Current weather
        df_current, current_error = get_current_weather(city, API_KEY)
        if df_current is not None:
            st.subheader(f"Current Weather in {city} (as of today)")
            st.write(f"Temperature: {df_current['temp'].iloc[0]}°C")
            st.write(f"Max Temperature Today: {df_current['max_temp'].iloc[0]}°C")
        else:
            st.error(current_error)

        # Forecast
        df_forecast, forecast_error = get_forecast(city, API_KEY)
        if df_forecast is not None:
            st.subheader(f"Weather Forecast for {city} (Next 5 Days)")
            st.write("Note: Free API limits to 5 days; paid plan needed for 10 days.")
            st.dataframe(df_forecast[['ds', 'max_temp', 'rain_chance']].rename(
                columns={'ds': 'Date', 'max_temp': 'Max Temp (°C)', 'rain_chance': 'Rain Chance (%)'}
            ).head(5))

            # Plot
            st.subheader(f"Weather Forecast Plot for {city}")
            plt.figure(figsize=(10, 6))
            plt.plot(df_forecast['ds'], df_forecast['max_temp'], label='Max Temperature (°C)', marker='o')
            plt.twinx()
            plt.plot(df_forecast['ds'], df_forecast['rain_chance'], label='Rain Chance (%)', color='orange', marker='o')
            plt.title(f'Weather Forecast for {city}')
            plt.xlabel('Date')
            plt.legend()
            st.pyplot(plt.gcf())
        else:
            st.error(forecast_error)
