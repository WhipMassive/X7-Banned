# -*- coding: utf-8 -*-
import discord
from discord.ext import commands, tasks
import os
import json

# ==============================
# AYARLAR
# ==============================
TOKEN = os.environ.get("TOKEN")
PREFIX = "!"
VOICE_CHANNEL_ID = 1508961875109482737
LOG_CHANNEL_ID = 1510274969144262806
BANLI_ROL_ADI = "banlı"
BANLI_DOSYA = "banli_kullanicilar.json"

# ==============================
# JSON'DAN YÜKLE
# ==============================
def banli_yukle():
    if os.path.exists(BANLI_DOSYA):
        with open(BANLI_DOSYA, "r") as f:
            return json.load(f)
    return [1345376000468455425]  # varsayılan liste

def banli_kaydet(liste):
    with open(BANLI_DOSYA, "w") as f:
        json.dump(liste, f)

BANLI_KULLANICILAR = banli_yukle()

# ==============================
# BOT KURULUMU
# ==============================
intents = discord.Intents.all()
bot = commands.Bot(command_prefix=PREFIX, intents=intents)

# ==============================
# BOT HAZIR
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Log botu açıldı: {bot.user}")
    stay_in_voice.start()

# ==============================
# SUNUCUDAN AYRILANLAR
# ==============================
@bot.event
async def on_member_remove(member):
    log_channel = bot.get_channel(LOG_CHANNEL_ID)
    banli_rol = discord.utils.get(member.guild.roles, name=BANLI_ROL_ADI)
    has_banli = banli_rol in member.roles if banli_rol else False
    if log_channel:
        embed = discord.Embed(title="📤 Kullanıcı Ayrıldı", color=0xff0000)
        embed.add_field(name="Kullanıcı", value=f"{member.mention} ({member})", inline=False)
        embed.add_field(name="ID", value=str(member.id), inline=True)
        embed.add_field(name="Banlı Rolü", value="⚠️ Evet" if has_banli else "✅ Hayır", inline=True)
        embed.set_thumbnail(url=member.display_avatar.url)
        await log_channel.send(embed=embed)

# ==============================
# SUNUCUYA GERİ DÖNENLER
# ==============================
@bot.event
async def on_member_join(member):
    if member.id in BANLI_KULLANICILAR:
        banli_rol = discord.utils.get(member.guild.roles, name=BANLI_ROL_ADI)
        if banli_rol:
            await member.add_roles(banli_rol, reason="Banlı kullanıcı geri döndü — otomatik rol")
            print(f"🔒 {member} geri döndü, banlı rolü verildi.")
        log_channel = bot.get_channel(LOG_CHANNEL_ID)
        if log_channel:
            embed = discord.Embed(title="🔄 Banlı Kullanıcı Geri Döndü!", color=0xff6600)
            embed.add_field(name="Kullanıcı", value=f"{member.mention} ({member})", inline=False)
            embed.add_field(name="ID", value=str(member.id), inline=True)
            embed.add_field(name="İşlem", value="⚠️ Banlı rolü otomatik verildi", inline=True)
            embed.set_thumbnail(url=member.display_avatar.url)
            await log_channel.send(embed=embed)

# ==============================
# BANLI KULLANICI EKLE/ÇIKAR
# ==============================
@bot.command(name="banla")
@commands.has_permissions(administrator=True)
async def banla(ctx, user_id: int):
    if user_id not in BANLI_KULLANICILAR:
        BANLI_KULLANICILAR.append(user_id)
        banli_kaydet(BANLI_KULLANICILAR)

        member = ctx.guild.get_member(user_id)
        if member:
            banli_rol = discord.utils.get(ctx.guild.roles, name=BANLI_ROL_ADI)
            if banli_rol:
                await member.add_roles(banli_rol, reason="Manuel banlandı")
            await ctx.send(f"✅ <@{user_id}> banlandı ve rol verildi.")
        else:
            await ctx.send(f"✅ `{user_id}` listeye eklendi. Sunucuya girince rol alacak.")
    else:
        await ctx.send(f"⚠️ Bu kullanıcı zaten listede.")

@bot.command(name="bankaldir")
@commands.has_permissions(administrator=True)
async def bankaldir(ctx, user_id: int):
    if user_id in BANLI_KULLANICILAR:
        BANLI_KULLANICILAR.remove(user_id)
        banli_kaydet(BANLI_KULLANICILAR)
        await ctx.send(f"✅ `{user_id}` listeden çıkarıldı.")
    else:
        await ctx.send(f"⚠️ Bu kullanıcı listede değil.")

# ==============================
# SES KANALINDA KAL
# ==============================
@tasks.loop(seconds=10)
async def stay_in_voice():
    channel = bot.get_channel(VOICE_CHANNEL_ID)
    if channel is None:
        print("❌ Ses kanalı bulunamadı!")
        return
    voice_client = discord.utils.get(bot.voice_clients, guild=channel.guild)
    if voice_client is None:
        await channel.connect()
        print("🔊 Ses kanalına bağlanıldı!")
    elif voice_client.channel.id != VOICE_CHANNEL_ID:
        await voice_client.move_to(channel)
        print("🔊 Doğru ses kanalına geçildi!")

@stay_in_voice.before_loop
async def before_stay():
    await bot.wait_until_ready()

# ==============================
# BOTU ÇALIŞTIR
# ==============================
bot.run(TOKEN)
