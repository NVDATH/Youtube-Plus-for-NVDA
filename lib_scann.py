# -*- coding: utf-8 -*-
"""
list_libs.py
ตรวจสอบ library ในโฟลเดอร์ lib ของ Add-on
และพิมพ์ชื่อ + version ถ้ามี
"""

import os
import sys
import pkgutil

# กำหนด path ของ lib
lib_dir = r"C:\Users\virus\AppData\Roaming\nvda\addons\Youtube Plus\globalPlugins\Youtube Plus\lib"

# เพิ่ม lib_dir เข้า sys.path
sys.path.insert(0, lib_dir)

print(f"Scanning libraries in: {lib_dir}\n")

# ไล่ทุก module / package
for finder, name, ispkg in pkgutil.iter_modules([lib_dir]):
    try:
        module = __import__(name)
        version = getattr(module, "__version__", "unknown")
    except Exception:
        version = "unknown"
    print(f"{name}=={version}")
