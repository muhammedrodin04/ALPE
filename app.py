import os
import sys
import json
import time
import threading
import random
import string
import uuid
from datetime import datetime
from hashlib import md5
import base64
import secrets
from bs4 import BeautifulSoup
import httpx
import requests
from user_agent import generate_user_agent
from flask import Flask, request, jsonify

# ==================== KALIN FONT DÖNÜŞÜMÜ ====================
def bold_text(text):
    """Normal metni Unicode kalın harflere çevirir (sadece harf ve rakamlar)"""
    bold_map = {
        'A': '𝐀', 'B': '𝐁', 'C': '𝐂', 'D': '𝐃', 'E': '𝐄', 'F': '𝐅', 'G': '𝐆', 'H': '𝐇', 'I': '𝐈', 'J': '𝐉',
        'K': '𝐊', 'L': '𝐋', 'M': '𝐌', 'N': '𝐍', 'O': '𝐎', 'P': '𝐏', 'Q': '𝐐', 'R': '𝐑', 'S': '𝐒', 'T': '𝐓',
        'U': '𝐔', 'V': '𝐕', 'W': '𝐖', 'X': '𝐗', 'Y': '𝐘', 'Z': '𝐙',
        'a': '𝐚', 'b': '𝐛', 'c': '𝐜', 'd': '𝐝', 'e': '𝐞', 'f': '𝐟', 'g': '𝐠', 'h': '𝐡', 'i': '𝐢', 'j': '𝐣',
        'k': '𝐤', 'l': '𝐥', 'm': '𝐦', 'n': '𝐧', 'o': '𝐨', 'p': '𝐩', 'q': '𝐪', 'r': '𝐫', 's': '𝐬', 't': '𝐭',
        'u': '𝐮', 'v': '𝐯', 'w': '𝐰', 'x': '𝐱', 'y': '𝐲', 'z': '𝐳',
        '0': '𝟎', '1': '𝟏', '2': '𝟐', '3': '𝟑', '4': '𝟒', '5': '𝟓', '6': '𝟔', '7': '𝟕', '8': '𝟖', '9': '𝟗',
        '#': '#', '@': '@', '.': '.', '_': '_', '-': '-', ' ': ' ', ':': ':', '/': '/', '?': '?', '=': '=', '&': '&'
    }
    return ''.join(bold_map.get(c, c) for c in text)

# ==================== DİL DOSYASI ====================
MESSAGES = {
    'tr': {
        'welcome': "𝐇𝐨ş 𝐠𝐞𝐥𝐝𝐢𝐧! 𝐋ü𝐭𝐟𝐞𝐧 𝐛𝐢𝐫 𝐢ş𝐥𝐞𝐦 𝐬𝐞ç𝐢𝐧:",
        'reset_link_btn': "🔗 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃[𝐋𝐈𝐍𝐊]",
        'reset_auto_btn': "⚡ 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐀𝐔𝐓𝐎[𝐀𝐏𝐏]",
        'about_btn': "ℹ️ 𝐇𝐚𝐤𝐤ı𝐧𝐝𝐚",
        'language_btn': "🌐 𝐃𝐢𝐥 𝐃𝐞ğ𝐢ş𝐭𝐢𝐫",
        'ask_mail': "📧 𝐋ü𝐭𝐟𝐞𝐧 𝐞-𝐩𝐨𝐬𝐭𝐚 𝐚𝐝𝐫𝐞𝐬𝐢𝐧𝐢𝐳𝐢 𝐯𝐞𝐲𝐚 𝐤𝐮𝐥𝐥𝐚𝐧ı𝐜ı 𝐚𝐝ı𝐧ı𝐳ı 𝐠𝐢𝐫𝐢𝐧:",
        'ask_link': "🔗 𝐋ü𝐭𝐟𝐞𝐧 𝐬ı𝐟ı𝐫𝐥𝐚𝐦𝐚 𝐥𝐢𝐧𝐤𝐢𝐧𝐢 𝐠ö𝐧𝐝𝐞𝐫𝐢𝐧:",
        'sending': "⏳ 𝐒ı𝐟ı𝐫𝐥𝐚𝐦𝐚 𝐞-𝐩𝐨𝐬𝐭𝐚𝐬ı 𝐠ö𝐧𝐝𝐞𝐫𝐢𝐥𝐢𝐲𝐨𝐫...",
        'sent': "✅ 𝐒ı𝐟ı𝐫𝐥𝐚𝐦𝐚 𝐞-𝐩𝐨𝐬𝐭𝐚𝐬ı 𝐠ö𝐧𝐝𝐞𝐫𝐢𝐥𝐝𝐢! {}",
        'failed': "❌ 𝐆ö𝐧𝐝𝐞𝐫𝐢𝐥𝐞𝐦𝐞𝐝𝐢: {}",
        'processing': "⏳ 𝐋𝐢𝐧𝐤 𝐢ş𝐥𝐞𝐧𝐢𝐲𝐨𝐫...",
        'success_auto': "✅ 𝐒𝐢𝐟𝐫𝐞 𝐛𝐚𝐬𝐚𝐫𝐲𝐥𝐚 𝐝𝐞𝐠𝐢𝐬𝐭𝐢𝐫𝐢𝐥𝐝𝐢!\n𝐊𝐮𝐥𝐥𝐚𝐧𝐢𝐜𝐢: {}\n𝐘𝐞𝐧𝐢 𝐬𝐢𝐟𝐫𝐞: {}",
        'fail_auto': "❌ 𝐈𝐬𝐥𝐞𝐦 𝐛𝐚𝐬𝐚𝐫𝐬𝐢𝐳: {}",
        'about': "𝐘𝐈𝐊𝐈𝐌 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐑𝐞𝐬𝐞𝐭 𝐓𝐨𝐨𝐥\n\n"
                 "🔥 𝐆𝐞𝐥𝐢𝐬𝐭𝐢𝐫𝐢𝐜𝐢: @AURAPY44\n"
                 "📢 𝐊𝐚𝐧𝐚𝐥: t.me/YIKIMTOOL\n"
                 "🚀 𝐒𝐮𝐫𝐮𝐦: 1.0\n\n"
                 "𝐁𝐮 𝐛𝐨𝐭, 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐡𝐞𝐬𝐚𝐩 𝐤𝐮𝐫𝐭𝐚𝐫𝐦𝐚 𝐢𝐬𝐥𝐞𝐦𝐥𝐞𝐫𝐢 𝐢𝐜𝐢𝐧 𝐲𝐚𝐩𝐢𝐥𝐦𝐢𝐬𝐭𝐢𝐫. 𝐊𝐨𝐭𝐮𝐲𝐞 𝐤𝐮𝐥𝐥𝐚𝐧𝐢𝐦𝐝𝐚𝐧 𝐬𝐨𝐫𝐮𝐦𝐥𝐮 𝐝𝐞𝐠𝐢𝐥𝐢𝐳.",
        'choose_lang': "🌐 𝐋ü𝐭𝐟𝐞𝐧 𝐝𝐢𝐥𝐢𝐧𝐢𝐳𝐢 𝐬𝐞ç𝐢𝐧:",
        'lang_changed': "✅ 𝐃𝐢𝐥 𝐓ü𝐫𝐤𝐜𝐞 𝐨𝐥𝐚𝐫𝐚𝐤 𝐝𝐞𝐟𝐢𝐬𝐭𝐢𝐫𝐢𝐥𝐝𝐢."
    },
    'en': {
        'welcome': "𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐨𝐨𝐬𝐞 𝐚𝐧 𝐚𝐜𝐭𝐢𝐨𝐧:",
        'reset_link_btn': "🔗 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃[𝐋𝐈𝐍𝐊]",
        'reset_auto_btn': "⚡ 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐀𝐔𝐓𝐎[𝐀𝐏𝐏]",
        'about_btn': "ℹ️ 𝐀𝐛𝐨𝐮𝐭",
        'language_btn': "🌐 𝐂𝐡𝐚𝐧𝐠𝐞 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞",
        'ask_mail': "📧 𝐏𝐥𝐞𝐚𝐬𝐞 𝐞𝐧𝐭𝐞𝐫 𝐲𝐨𝐮𝐫 𝐞𝐦𝐚𝐢𝐥 𝐨𝐫 𝐮𝐬𝐞𝐫𝐧𝐚𝐦𝐞:",
        'ask_link': "🔗 𝐏𝐥𝐞𝐚𝐬𝐞 𝐬𝐞𝐧𝐝 𝐭𝐡𝐞 𝐫𝐞𝐬𝐞𝐭 𝐥𝐢𝐧𝐤:",
        'sending': "⏳ 𝐒𝐞𝐧𝐝𝐢𝐧𝐠 𝐫𝐞𝐬𝐞𝐭 𝐞𝐦𝐚𝐢𝐥...",
        'sent': "✅ 𝐑𝐞𝐬𝐞𝐭 𝐞𝐦𝐚𝐢𝐥 𝐬𝐞𝐧𝐭! {}",
        'failed': "❌ 𝐅𝐚𝐢𝐥𝐞𝐝 𝐭𝐨 𝐬𝐞𝐧𝐝: {}",
        'processing': "⏳ 𝐏𝐫𝐨𝐜𝐞𝐬𝐬𝐢𝐧𝐠 𝐥𝐢𝐧𝐤...",
        'success_auto': "✅ 𝐏𝐚𝐬𝐬𝐰𝐨𝐫𝐝 𝐜𝐡𝐚𝐧𝐠𝐞𝐝 𝐬𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲!\n𝐔𝐬𝐞𝐫𝐧𝐚𝐦𝐞: {}\n𝐍𝐞𝐰 𝐩𝐚𝐬𝐬𝐰𝐨𝐫𝐝: {}",
        'fail_auto': "❌ 𝐎𝐩𝐞𝐫𝐚𝐭𝐢𝐨𝐧 𝐟𝐚𝐢𝐥𝐞𝐝: {}",
        'about': "𝐘𝐈𝐊𝐈𝐌 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐑𝐞𝐬𝐞𝐭 𝐓𝐨𝐨𝐥\n\n"
                 "🔥 𝐃𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫: @AURAPY44\n"
                 "📢 𝐂𝐡𝐚𝐧𝐧𝐞𝐥: t.me/YIKIMTOOL\n"
                 "🚀 𝐕𝐞𝐫𝐬𝐢𝐨𝐧: 1.0\n\n"
                 "𝐓𝐡𝐢𝐬 𝐛𝐨𝐭 𝐢𝐬 𝐦𝐚𝐝𝐞 𝐟𝐨𝐫 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐚𝐜𝐜𝐨𝐮𝐧𝐭 𝐫𝐞𝐜𝐨𝐯𝐞𝐫𝐲 𝐩𝐫𝐨𝐜𝐞𝐬𝐬𝐞𝐬. 𝐖𝐞 𝐚𝐫𝐞 𝐧𝐨𝐭 𝐫𝐞𝐬𝐩𝐨𝐧𝐬𝐢𝐛𝐥𝐞 𝐟𝐨𝐫 𝐦𝐢𝐬𝐮𝐬𝐞.",
        'choose_lang': "🌐 𝐏𝐥𝐞𝐚𝐬𝐞 𝐜𝐡𝐨𝐨𝐬𝐞 𝐲𝐨𝐮𝐫 𝐥𝐚𝐧𝐠𝐮𝐚𝐠𝐞:",
        'lang_changed': "✅ 𝐋𝐚𝐧𝐠𝐮𝐚𝐠𝐞 𝐜𝐡𝐚𝐧𝐠𝐞𝐝 𝐭𝐨 𝐄𝐧𝐠𝐥𝐢𝐬𝐡."
    },
    'ar': {
        'welcome': "𝐀𝐡𝐥𝐚𝐧! 𝐘𝐞𝐫𝐣𝐚 𝐚𝐥𝐚𝐤𝐡𝐢𝐲𝐚𝐫 𝐦𝐧 𝐚𝐥𝐚𝐦𝐫 𝐚𝐥𝐭𝐚𝐥𝐢:",
        'reset_link_btn': "🔗 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃[𝐋𝐈𝐍𝐊] (إعادة تعيين عبر الرابط)",
        'reset_auto_btn': "⚡ 𝐑𝐄𝐒𝐄𝐓 𝐏𝐀𝐒𝐒𝐖𝐎𝐑𝐃 𝐀𝐔𝐓𝐎[𝐀𝐏𝐏] (تلقائي)",
        'about_btn': "ℹ️ 𝐌𝐞𝐥𝐨𝐮𝐦𝐚𝐭",
        'language_btn': "🌐 𝐓𝐠𝐢𝐲𝐢𝐫 𝐚𝐥𝐥𝐠𝐚",
        'ask_mail': "📧 𝐘𝐞𝐫𝐣𝐚 𝐞𝐝𝐱𝐚𝐥 𝐛𝐫𝐢𝐝𝐤 𝐚𝐥𝐚𝐥𝐤𝐭𝐫𝐨𝐧𝐢 𝐚𝐰 𝐚𝐬𝐦 𝐚𝐥𝐦𝐬𝐭𝐜𝐡𝐝𝐦:",
        'ask_link': "🔗 𝐘𝐞𝐫𝐣𝐚 𝐞𝐫𝐬𝐚𝐥 𝐫𝐚𝐛𝐭 𝐚𝐥𝐚𝐜𝐭𝐲𝐚𝐝𝐞:",
        'sending': "⏳ 𝐉𝐚𝐫𝐢 𝐞𝐫𝐬𝐚𝐥 𝐛𝐫𝐢𝐝 𝐚𝐥𝐚𝐜𝐭𝐲𝐚𝐝𝐞...",
        'sent': "✅ 𝐓𝐦 𝐞𝐫𝐬𝐚𝐥 𝐛𝐫𝐢𝐝 𝐚𝐥𝐚𝐜𝐭𝐲𝐚𝐝𝐞! {}",
        'failed': "❌ 𝐅𝐞𝐬𝐡𝐥 𝐟𝐲 𝐚𝐥𝐞𝐫𝐬𝐚𝐥: {}",
        'processing': "⏳ 𝐉𝐚𝐫𝐢 𝐦𝐜𝐚𝐥𝐠𝐞 𝐚𝐥𝐫𝐚𝐛𝐭...",
        'success_auto': "✅ 𝐓𝐦 𝐭𝐠𝐢𝐲𝐢𝐫 𝐚𝐥𝐜𝐥𝐦𝐞 𝐛𝐧𝐠𝐚𝐡!\n𝐀𝐬𝐦 𝐚𝐥𝐦𝐬𝐭𝐜𝐡𝐝𝐦: {}\n𝐀𝐥𝐜𝐥𝐦𝐞 𝐚𝐥𝐣𝐝𝐲𝐝𝐞: {}",
        'fail_auto': "❌ 𝐅𝐞𝐬𝐡𝐥 𝐚𝐥𝐜𝐦𝐥𝐞: {}",
        'about': "𝐘𝐈𝐊𝐈𝐌 𝐀𝐝𝐚𝐞 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦 𝐥𝐞𝐬𝐭𝐜𝐫𝐣𝐚𝐝𝐞 𝐚𝐥𝐜𝐜𝐥𝐦𝐞 𝐚𝐥𝐦𝐫𝐞\n\n"
                 "🔥 𝐀𝐥𝐦𝐛𝐫𝐦𝐣: @AURAPY44\n"
                 "📢 𝐀𝐥𝐪𝐧𝐚𝐞: t.me/YIKIMTOOL\n"
                 "🚃 𝐀𝐥𝐚𝐬𝐝𝐚𝐫: 1.0\n\n"
                 "𝐇𝐝𝐚 𝐚𝐥𝐛𝐨𝐭 𝐦𝐬𝐦𝐦 𝐥𝐦𝐜𝐚𝐥𝐠𝐞 𝐞𝐬𝐭𝐜𝐫𝐣𝐚𝐝𝐞 𝐡𝐬𝐚𝐛𝐚𝐭 𝐈𝐧𝐬𝐭𝐚𝐠𝐫𝐚𝐦. 𝐋𝐚 𝐧𝐭𝐡𝐦𝐥 𝐦𝐬𝐰𝐨𝐥𝐲𝐞 𝐞𝐬𝐚𝐞 𝐚𝐥𝐚𝐬𝐭𝐱𝐝𝐚𝐦.",
        'choose_lang': "🌐 𝐘𝐞𝐫𝐣𝐚 𝐚𝐥𝐚𝐤𝐡𝐢𝐲𝐚𝐫 𝐚𝐥𝐥𝐠𝐞 𝐚𝐥𝐤𝐡𝐚𝐬𝐞 𝐛𝐤:",
        'lang_changed': "✅ 𝐓𝐦 𝐚𝐥𝐭𝐠𝐢𝐲𝐢𝐫 𝐚𝐥𝐚 𝐚𝐥𝐥𝐠𝐞 𝐚𝐥𝐜𝐫𝐛𝐲𝐞."
    }
}

# ==================== KULLANICI VERİLERİ (geçici) ====================
user_lang = {}          # {user_id: 'tr/en/ar'}
user_state = {}         # {user_id: {'action': 'reset_link'/'reset_auto', 'lang': ...}}
# action: 'reset_link' -> mail bekliyor, 'reset_auto' -> link bekliyor

# ==================== TELEGRAM BOT AYARLARI ====================
TOKEN = "8788109162:AAG4W_dc8ja8yzex7VR4z6UyrBplm-NoQXE"
API_URL = f"https://api.telegram.org/bot{TOKEN}"

# ==================== ORİJİNAL KOD 1: RESET PASSWORD[LINK] (DÜZELTİLMİŞ) ====================
def send_recovery(mail):
    try:
        headers = {
            "user-agent": generate_user_agent(),
            "x-ig-app-id": "936619743392459",
            "x-requested-with": "XMLHttpRequest",
            "x-instagram-ajax": "1032099486",
            "x-csrftoken": "missing",
            "x-asbd-id": "359341",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/accounts/password/reset/",
            "accept-language": "en-US",
            "priority": "u=1, i",
        }
        # Orijinal kodda httpx.Client(http2=True) kullanılmış, biz de aynısını yapalım
        with httpx.Client(http2=True, headers=headers, timeout=20) as client:
            r = client.post(
                "https://www.instagram.com/api/v1/web/accounts/account_recovery_send_ajax/",
                data={"email_or_username": mail}
            )
        
        # Önce JSON olarak parse etmeyi dene
        try:
            response = r.json()
        except Exception as json_err:
            # JSON değilse yanıtın ilk kısmını hata olarak döndür
            return {"success": False, "error": f"Invalid JSON response: {r.text[:200]}"}
        
        # Orijinal mantık: contact_point varsa başarılı, yoksa hata
        if 'contact_point' in response:
            return {"success": True, "message": response.get('contact_point', 'Email sent')}
        elif 'message' in response:
            return {"success": False, "error": response['message']}
        else:
            return {"success": False, "error": "Unknown response: " + str(response)}
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== ORİJİNAL KOD 2: RESET PASSWORD AUTO[APP] (AYNEN) ====================
def generate_device_info():
    ANDROID_ID = f"android-{''.join(random.choices(string.hexdigits.lower(), k=16))}"
    USER_AGENT = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    WATERFALL_ID = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp())
    nums = ''.join([str(random.randint(1, 100)) for _ in range(4)])
    PASSWORD = f'#PWD_INSTAGRAM:0:{timestamp}:@AURAPY44.{nums}'
    return ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD

def acer(mid="", user_agent=""):
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Bloks-Version-Id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
        "X-Mid": mid,
        "User-Agent": user_agent,
        "Content-Length": "9481"
    }

def id_user(user_id):
    try:
        url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
        headers = {"User-Agent": "Instagram 219.0.0.12.117 Android"}
        r = requests.get(url, headers=headers)
        return r.json()["user"]["username"]
    except:
        return None

def purna(reset_link):
    try:
        ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
        uidb36 = reset_link.split("uidb36=")[1].split("&token=")[0]
        token = reset_link.split("&token=")[1].split(":")[0]

        url = "https://i.instagram.com/api/v1/accounts/password_reset/"
        data = {
            "source": "one_click_login_email",
            "uidb36": uidb36,
            "device_id": ANDROID_ID,
            "token": token,
            "waterfall_id": WATERFALL_ID
        }
        r = requests.post(url, headers=acer(user_agent=USER_AGENT), data=data)
        
        if "user_id" not in r.text:
            return {"success": False, "error": f"Error in reset request: {r.text}"}

        mid = r.headers.get("Ig-Set-X-Mid")
        resp_json = r.json()
        user_id = resp_json.get("user_id")
        cni = resp_json.get("cni")
        nonce_code = resp_json.get("nonce_code")
        challenge_context = resp_json.get("challenge_context")

        url2 = "https://i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/"
        data2 = {
            "user_id": str(user_id),
            "cni": str(cni),
            "nonce_code": str(nonce_code),
            "bk_client_context": '{"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}',
            "challenge_context": str(challenge_context),
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "get_challenge": "true"
        }
        r2 = requests.post(url2, headers=acer(mid, USER_AGENT), data=data2).text
        
        challenge_context_final = r2.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]

        data3 = {
            "is_caa": "False",
            "source": "",
            "uidb36": "",
            "error_state": {"type_name":"str","index":0,"state_id":1048583541},
            "afv": "",
            "cni": str(cni),
            "token": "",
            "has_follow_up_screens": "0",
            "bk_client_context": {"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"},
            "challenge_context": challenge_context_final,
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "enc_new_password1": PASSWORD,
            "enc_new_password2": PASSWORD
        }
        
        requests.post(url2, headers=acer(mid, USER_AGENT), data=data3)
        new_password = PASSWORD.split(":")[-1]
        
        username = id_user(user_id)
        return {
            "success": True,
            "password": new_password,
            "user_id": user_id,
            "username": username
        }
    except Exception as e:
        return {"success": False, "error": str(e)}

# ==================== TELEGRAM API İŞLEMLERİ ====================
def send_message(chat_id, text, reply_markup=None):
    url = f"{API_URL}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"SendMessage error: {e}")

def answer_callback(callback_id, text):
    url = f"{API_URL}/answerCallbackQuery"
    payload = {'callback_query_id': callback_id, 'text': text}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"AnswerCallback error: {e}")

def edit_message(chat_id, message_id, text, reply_markup=None):
    url = f"{API_URL}/editMessageText"
    payload = {
        'chat_id': chat_id,
        'message_id': message_id,
        'text': text,
        'parse_mode': 'HTML'
    }
    if reply_markup:
        payload['reply_markup'] = json.dumps(reply_markup)
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"EditMessage error: {e}")

# ==================== BUTONLAR ====================
def main_menu_keyboard(lang):
    keyboard = {
        "inline_keyboard": [
            [
                {"text": MESSAGES[lang]['reset_link_btn'], "callback_data": "reset_link"},
                {"text": MESSAGES[lang]['reset_auto_btn'], "callback_data": "reset_auto"}
            ],
            [
                {"text": MESSAGES[lang]['about_btn'], "callback_data": "about"},
                {"text": MESSAGES[lang]['language_btn'], "callback_data": "choose_lang"}
            ]
        ]
    }
    return keyboard

def language_keyboard():
    keyboard = {
        "inline_keyboard": [
            [
                {"text": "🇹🇷 Türkçe", "callback_data": "lang_tr"},
                {"text": "🇬🇧 English", "callback_data": "lang_en"},
                {"text": "🇸🇦 العربية", "callback_data": "lang_ar"}
            ]
        ]
    }
    return keyboard

# ==================== MESAJ İŞLEYİCİ ====================
def handle_message(chat_id, text, user_id):
    lang = user_lang.get(user_id, 'en')
    state = user_state.get(user_id)

    # Eğer state varsa ve text gönderildiyse
    if state:
        action = state.get('action')
        if action == 'reset_link':
            # Mail gönder
            send_message(chat_id, bold_text(MESSAGES[lang]['sending']))
            result = send_recovery(text)
            if result['success']:
                msg = MESSAGES[lang]['sent'].format(result['message'])
            else:
                msg = MESSAGES[lang]['failed'].format(result['error'])
            send_message(chat_id, bold_text(msg))
            # State temizle ve ana menüye dön
            del user_state[user_id]
            send_message(chat_id, bold_text(MESSAGES[lang]['welcome']), main_menu_keyboard(lang))
        elif action == 'reset_auto':
            # Link işle
            send_message(chat_id, bold_text(MESSAGES[lang]['processing']))
            result = purna(text.strip())
            if result.get('success'):
                username = result.get('username', 'Unknown')
                new_pass = result.get('password', '')
                # Şifreyi normal fontla göstermek için bold_text'i sadece sabit metne uygula
                # Ama daha kolay: tüm mesajı bold yapıp şifreyi <code> ile gösterelim
                msg = (bold_text(MESSAGES[lang]['success_auto'].split('{}')[0]) + 
                       f"<code>{username}</code>" + 
                       bold_text(MESSAGES[lang]['success_auto'].split('{}')[1].split('{}')[0]) + 
                       f"<code>{new_pass}</code>")
                send_message(chat_id, msg)
            else:
                error = result.get('error', 'Unknown error')
                msg = bold_text(MESSAGES[lang]['fail_auto'].format(error))
                send_message(chat_id, msg)
            del user_state[user_id]
            send_message(chat_id, bold_text(MESSAGES[lang]['welcome']), main_menu_keyboard(lang))
        else:
            # Bilinmeyen state, temizle
            del user_state[user_id]
            send_message(chat_id, bold_text(MESSAGES[lang]['welcome']), main_menu_keyboard(lang))
    else:
        # State yoksa normal mesaj /start komutu bekler, ama yine de ana menü gönder
        send_message(chat_id, bold_text(MESSAGES[lang]['welcome']), main_menu_keyboard(lang))

def handle_callback(chat_id, message_id, user_id, callback_id, data):
    lang = user_lang.get(user_id, 'en')
    
    if data == "reset_link":
        user_state[user_id] = {'action': 'reset_link'}
        send_message(chat_id, bold_text(MESSAGES[lang]['ask_mail']))
        answer_callback(callback_id, "🔗 Link seçildi")
    elif data == "reset_auto":
        user_state[user_id] = {'action': 'reset_auto'}
        send_message(chat_id, bold_text(MESSAGES[lang]['ask_link']))
        answer_callback(callback_id, "⚡ Otomatik seçildi")
    elif data == "about":
        about_text = bold_text(MESSAGES[lang]['about'])
        send_message(chat_id, about_text)
        answer_callback(callback_id, "ℹ️ Hakkında")
    elif data == "choose_lang":
        edit_message(chat_id, message_id, bold_text(MESSAGES[lang]['choose_lang']), language_keyboard())
        answer_callback(callback_id, "🌐 Dil seçimi")
    elif data.startswith("lang_"):
        new_lang = data.split("_")[1]
        user_lang[user_id] = new_lang
        edit_message(chat_id, message_id, bold_text(MESSAGES[new_lang]['lang_changed']), main_menu_keyboard(new_lang))
        answer_callback(callback_id, f"Dil {new_lang} olarak ayarlandı")
    else:
        answer_callback(callback_id, "Bilinmeyen işlem")

# ==================== POLLING DÖNGÜSÜ ====================
def bot_polling():
    print("Bot polling başladı...")
    offset = 0
    while True:
        try:
            url = f"{API_URL}/getUpdates"
            params = {'offset': offset, 'timeout': 30}
            resp = requests.get(url, params=params, timeout=35)
            data = resp.json()
            if data['ok']:
                for update in data['result']:
                    offset = update['update_id'] + 1
                    
                    if 'message' in update:
                        msg = update['message']
                        chat_id = msg['chat']['id']
                        user_id = msg['from']['id']
                        if 'text' in msg:
                            text = msg['text']
                            if text.startswith('/start'):
                                lang = user_lang.get(user_id, 'en')
                                send_message(chat_id, bold_text(MESSAGES[lang]['welcome']), main_menu_keyboard(lang))
                            else:
                                handle_message(chat_id, text, user_id)
                    
                    if 'callback_query' in update:
                        cb = update['callback_query']
                        cb_id = cb['id']
                        chat_id = cb['message']['chat']['id']
                        message_id = cb['message']['message_id']
                        user_id = cb['from']['id']
                        data = cb['data']
                        handle_callback(chat_id, message_id, user_id, cb_id, data)
        except Exception as e:
            print(f"Polling hatası: {e}")
            time.sleep(5)

# ==================== FLASK UYGULAMASI ====================
app = Flask(__name__)

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YIKIM TOOL - Instagram Reset</title>
        <style>
            body {
                margin: 0;
                height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                background: linear-gradient(135deg, #1a0033, #330066);
                font-family: Arial, Helvetica, sans-serif;
                color: white;
            }
            .container {
                text-align: center;
            }
            h1 {
                font-size: 6rem;
                margin: 0;
                text-shadow: 0 0 20px #ff00ff, 0 0 40px #00ffff;
                letter-spacing: 8px;
            }
            .status {
                font-size: 3.5rem;
                color: #00ff88;
                margin: 20px 0;
                font-weight: bold;
                text-shadow: 0 0 15px #00ff88;
            }
            .info {
                font-size: 1.4rem;
                opacity: 0.8;
                margin-top: 40px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>YIKIM TOOL</h1>
            <div class="status">BOT AKTİF</div>
            <div class="info">Instagram Reset Sistemi çalışıyor • 7/24 Online</div>
        </div>
    </body>
    </html>
    """

@app.route('/health')
def health():
    return jsonify({"status": "ok"}), 200

# ==================== ANA FONKSİYON ====================
if __name__ == '__main__':
    # Bot polling thread'ini başlat
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()
    
    print("Flask sunucusu başlatılıyor...")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False, use_reloader=False)