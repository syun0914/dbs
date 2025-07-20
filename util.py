import aiohttp
from time import time

city = 'Seosan,KR'


def get_image_url(data: dict) -> str:
    main = data['weather'][0]['main']
    detail = data['weather'][0]['id']
    code = None
    if main == 'Thunderstorm':
        code = '11'
    elif main == 'Drizzle' or detail in {520, 521, 522, 531}:
        code = '09'
    elif main == 'Snow' or detail == 511:
        code = '13'
    elif main == 'Rain':
        code = '10'
    elif main == 'Clear':
        code = '01'
    elif detail == 801:
        code = '02'
    elif detail == 802:
        code = '03'
    elif detail in {803, 804}:
        code = '04'
    day = (
        'd' if data['sys']['sunrise'] <= time() < data['sys']['sunset']
        else 'n'
    )
    return f'https://openweathermap.org/img/wn/{code}{day}@2x.png'


def get_pm10_level(pm10: float) -> str:
    if 0 <= pm10 < 20:
        return '매우 좋음'
    elif 20 <= pm10 < 50:
        return '좋음'
    elif 50 <= pm10 < 100:
        return '보통'
    elif 100 <= pm10 < 200:
        return '나쁨'
    elif pm10 >= 200:
        return '매우 나쁨'
    else:
        return '오류 발생'


def get_pm2_5_level(pm2_5: float) -> str:
    if 0 <= pm2_5 < 10:
        return '매우 좋음'
    elif 10 <= pm2_5 < 25:
        return '좋음'
    elif 25 <= pm2_5 < 50:
        return '보통'
    elif 50 <= pm2_5 < 75:
        return '나쁨'
    elif pm2_5 >= 75:
        return '매우 나쁨'
    else:
        return '오류 발생'


async def get_weather(city: str, key: str) -> dict:
    params = {
        'q': city,
        'appid': key,
        'units': 'metric'
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            'https://api.openweathermap.org/data/2.5/weather',
            params=params
        ) as resp:
            return await resp.json()


async def get_air_pollution(lat: float, lon: float, key: str) -> dict:
    params = {
        'lat': lat,
        'lon': lon,
        'appid': key
    }
    async with aiohttp.ClientSession() as sess:
        async with sess.get(
            'https://api.openweathermap.org/data/2.5/air_pollution',
            params=params
        ) as resp:
            return await resp.json()


def get_message(
    temp: float,
    humidity: float,
    pm10_level: str,  # 매우 좋음, 좋음, 보통, 나쁨, 매우 나쁨
    pm2_5_level: str,
    main: str,
    code: int
) -> str:
    msg = []
    if (
        temp >= 34 and humidity >= 45
        or temp >= 32 and humidity >= 70
        or temp >= 30 and humidity >= 95
    ):
        msg.append(f'폭염({temp:.1f}°C)입니다.')
    if temp <= 0:
        msg.append(f'추움 주의({temp:.1f}°C)입니다.')
    elif temp <= -8:
        msg.append(f'추움 경고({temp:.1f}°C)입니다.')
    elif temp <= -14:
        msg.append(f'한파 위험({temp:.1f}°C)입니다.')

    if pm10_level == "매우 좋음" :
        msg.append('미세먼지 짱 좋습니다. 안심안심')
    if pm10_level == "좋음":
        msg.append('미세먼지 좋습니다.')
    if pm10_level == "보통" :
        msg.append('미세먼지 보통입니다.') 
    if pm10_level == "나쁨" :
        msg.append('미세먼지 나쁨입니다. 마스크 착용 권고')
    if pm10_level == "매우 나쁨":
         msg.append('미세먼지 매우 나쁨. 마스크 안쓰면 죽어!')
    
    if pm2_5_level =="매우 좋음":
        msg.append('초미세먼지 짱 좋습니다. 안심안심')
    if pm2_5_level =="좋음":
        msg.append('초미세먼지 좋습니다. 이정도면 버텨!')
    if pm2_5_level =="보통":
         msg.append('보통입니다')
    if pm2_5_level =="나쁨":
         msg.append('초미세먼지 나쁨입니다. 마스크 착용 권고')
    if pm2_5_level =="매우 나쁨":
         msg.append('초미세먼지 매우 나쁨입니다. 마스크를 안쓰겠다고? 데엣 죽을지도?')
    
    if main == "천둥번개" :
        msg.append('번개가 친다구! 집밖은 위험해!')
    if main == "이슬비" :
        msg.append('쪼꼬미 이슬비 그래도 모발을 위해 우산은 챙기시길')
    if main == "비" :
        msg.append('비 내려! 우산 꼭 챙기세용')
    if main == "눈" :
        msg.append('하늘에서 눈이 내려와~')
    if main == "맑음" :
        msg.append('햇볕은 쨍쨍')
    if main =="구름" :
       msg.append('이런날 풋살 안하면 손해긴해') 
    if code == '박무' or code == '연무' or code == '안개':
       msg.append('안개가 있어용, 운전 조심~')  
    if code == "연기" :
       msg.append('연기가 있어요. 왜...일까요?')
    if code == "모래 먼지" or code == "모래" or code == "먼지":
       msg.append('황사 조심하세요')
    if code == "화산재":
       msg.append('화산재 조심! 펑!!')
    if code == "돌풍" or code == '토네이도':
       msg.append('바람조심!, 이상한 나라의 엘리스가 돼버렸!')
    
    return ' '.join(msg)