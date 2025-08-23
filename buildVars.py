# -*- coding: UTF-8 -*-
# buildVars.py - variables used by SCons when building the addon.

# Add-on information variables
addon_info = {
    # ชื่อ add-on
    "addon_name": "YoutubePlus",

    # เวอร์ชัน (ต้องตรงกับ manifest.ini)
    "addon_version": "2025.8.22",

    # ผู้พัฒนา
    "addon_author": "NVDA_TH <nvdainth@gmail.com>, assisted by A.I.",

    # สรุปสั้น ๆ
    "addon_summary": "YouTube Plus can monitor a live chat, view comments and more.",

    # คำอธิบายละเอียด
    "addon_description": (
        "A complete toolkit for YouTube. Allows NVDA users to monitor live chat in real-time, "
        "view/search comments and live chat replays, get detailed video information, and download "
        "videos (MP4) or audio (M4A). Features automatic URL detection and background processing "
        "to keep NVDA responsive."
    ),

    # หน้าเว็บโปรเจ็กต์
    "addon_url": "https://nvda.in.th",

    # ไฟล์เอกสารหลัก (จะแนบในแพ็กเกจด้วย)
    "addon_docFileName": "readme.html",

    # เวอร์ชัน NVDA ขั้นต่ำและล่าสุดที่ทดสอบแล้ว
    "addon_minimumNVDAVersion": "2025.1",
    "addon_lastTestedNVDAVersion": "2025.2",

    # ช่องอัปเดต (None = ไม่มี auto update)
    "addon_updateChannel": None,
}

# รายชื่อไฟล์/โฟลเดอร์ที่ต้องเอาไปแพ็ก (ยกเว้นบางไฟล์อัตโนมัติ)
# ค่า default จะรวมทั้ง addon/ และ manifest.ini
# แต่ถ้ามีไฟล์อื่นนอกเหนือจากนั้นก็ใส่เพิ่มที่นี่ได้
pythonSources = [
    "addon/globalPlugins",
]

# รายชื่อไฟล์เพิ่มเติมที่ควร copy ไปใน dist (เช่นเอกสาร)
i18nSources = []
docFiles = ["readme.html"]

# รายชื่อ test files (ถ้าไม่มีปล่อยว่างได้)
tests = []
excludedFiles = [] 