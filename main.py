import discord
from discord import app_commands, Interaction, Color
from discord.ext import tasks
from datetime import datetime
import asyncio

from config import OPENWEATHERMAP_KEY, DISCORD_TOKEN
from util import (
    get_weather,
    get_image_url,
    get_air_pollution,
    get_pm10_level,
    get_pm2_5_level,
    get_message
)
from i18n_kr import MAIN_KR, DETAIL_KR


global alarm
alarm = {
    # server_id: {'channel': channel_id, 'hour': 9, 'minute': 10}
}


class DiscordClient(discord.Client):
    def __init__(self):
         super().__init__(intents = discord.Intents.all())
         self.synced = False
    async def on_ready(self):
         await self.wait_until_ready()
         if not self.synced: 
            await tree.sync() 
            self.synced = True
            every_write_forum.start()


client = DiscordClient()
tree = app_commands.CommandTree(client)

@tasks.loop(minutes=1)
async def every_write_forum():
    dt = datetime.now()
    for k in alarm:
        if dt.hour == alarm[k]['hour'] and dt.minute == alarm[k]['minute']:
            channel = client.get_guild(k).get_channel(alarm[k]['channel'])
            await channel.send(embed=weather_embed())
    await asyncio.sleep(1)


@tree.command(name='hello', description="봇이 'Hello!'를 출력합니다.") 
async def slash(interaction: Interaction):
    await interaction.response.send_message("Hello!", ephemeral=False)


async def weather_embed():
    data = await get_weather('Seosan,KR', OPENWEATHERMAP_KEY)
    weather = data['weather'][0]
    lat, lon = data['coord']['lat'], data['coord']['lon']
    components = (await get_air_pollution(
        lat, lon, OPENWEATHERMAP_KEY
    ))['list'][0]['components']
    pm10, pm2_5 = components['pm10'], components['pm2_5']
    pm10_level = get_pm10_level(pm10)
    pm2_5_level = get_pm2_5_level(pm2_5)
    temp, humidity = data['main']['temp'], data['main']['humidity']
    main, code = MAIN_KR[weather['main']], DETAIL_KR[weather['id']]

    embed = discord.Embed(
        title='📍 충남 서산의 날씨',
        description=get_message(
            temp, humidity, pm10_level, pm2_5_level, main, code
        ),
        color=Color.gold()
    )
    embed.add_field(
        name='기온', value=f"{temp:.1f}°C", inline=True
    )
    embed.add_field(
        name=f'날씨({main})', value=code, inline=True
    )
    embed.add_field(
        name='습도', value=f"{humidity}%", inline=True
    )
    embed.add_field(
        name=f'미세먼지({pm10_level})',
        value=f'{pm10} μg/m³',
        inline=True
    )
    embed.add_field(
        name=f'초미세먼지({pm2_5_level})',
        value=f'{pm2_5} μg/m³',
        inline=True
    )
    embed.set_thumbnail(url=get_image_url(data))
    embed.set_footer(text='제공: OpenWeather')
    return embed


@tree.command(name='날씨', description='☁️ 현재 날씨 정보를 불러옵니다.')
async def weather(interaction: Interaction):
    await interaction.response.send_message(embed=await weather_embed())


@tree.command(name='설정', description='날씨 정보를 보낼 시각을 설정합니다.')
async def set_alarm(interaction: Interaction, hour: int, minute: int):
    alarm[interaction.guild_id] = {
        'channel': interaction.channel_id,
        'hour': hour, 'minute': minute
    }
    embed = discord.Embed(title='알람 설정 내용', color=Color.gold())
    embed.add_field(
        name='서버 ID', value=str(interaction.guild_id), inline=False
    )
    embed.add_field(
        name=f'채널 ID', value=str(interaction.channel_id), inline=False
    )
    embed.add_field(
        name='설정 시각', value=f'매일 {hour}시 {minute}분', inline=True
    )
    print(alarm)
    await interaction.response.send_message(embed=embed)


@tree.command(name="embed", description="embed 테스트")
async def mkembed(interaction: Interaction):
    embed = discord.Embed(title="정재영", color=Color.gold())
    embed.add_field(name="바보력",value="100%",inline=False)
    embed.add_field(name="생년월일",value="2007년 10월 26일",inline=False)
    embed.add_field(name="키",value="약 2 m",inline=False)
    embed.set_thumbnail(url=interaction.user.avatar)
    embed.set_footer(text="정재영 바보")
    await interaction.response.send_message(embed=embed)

client.run(DISCORD_TOKEN)
