import requests
import matplotlib.pyplot as plt

from config import OPENWEATHERMAP_KEY

city = 'Seosan,KR'


# 1. 날씨 정보 가져오기
weather_url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHERMAP_KEY}&units=metric'
weather_response = requests.get(weather_url)
weather_data = weather_response.json()
if weather_response.status_code == 200:
    temp = weather_data["main"]["temp"]
    print(weather_data["weather"][0])
    desc = weather_data["weather"][0]["description"]
    humidity = weather_data["main"]["humidity"]
    lat = weather_data["coord"]["lat"]
    lon = weather_data["coord"]["lon"]

    print(f"📍 {city}의 현재 기온: {temp}℃")
    print(f"☁️ 날씨 상태: {desc}")
    print(f"💧 상대 습도: {humidity}%")

    # 2. 대기 오염 정보 가져오기
    air_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={OPENWEATHERMAP_KEY}"
    air_response = requests.get(air_url)
    air_data = air_response.json()

    if air_response.status_code == 200:
        aqi = air_data["list"][0]["main"]["aqi"]
        pm2_5 = air_data["list"][0]["components"]["pm2_5"]
        pm10 = air_data["list"][0]["components"]["pm10"]

        aqi_status = {
            1: "좋음",
            2: "보통",
            3: "약간 나쁨",
            4: "나쁨",
            5: "매우 나쁨"
        }

        print(f"🌫 대기질 지수 (AQI): {aqi} ({aqi_status[aqi]})")
        print(f"🌬 PM2.5: {pm2_5} μg/m³")
        print(f"🌬 PM10 : {pm10} μg/m³")

        # 3. PM2.5 경고
        if pm2_5 > 50:
            print("⚠️ 경고: PM2.5 농도가 매우 높습니다! 마스크 착용을 권장합니다.")

        # 4. 시각화
        labels = ['PM2.5', 'PM10']
        values = [pm2_5, pm10]
        colors = ['red' if pm2_5 > 50 else 'green', 'orange']

        # plt.bar(labels, values, color=colors)
        # plt.title(f'{city} 대기 오염 수치')
        # plt.ylabel('μg/m³')
        # plt.ylim(0, max(values) + 20)
        # plt.grid(axis='y')
        # plt.show()
    else:
        print("❌ 대기 오염 정보를 가져오는 데 실패했습니다.")
else:
    print("❌ 날씨 정보를 가져오는 데 실패했습니다.")