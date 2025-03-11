# exp_system.py
import json
import os

EXP_RATE = 2.5
EXP_FILE = os.path.join(os.getcwd(), "exp_data.json")
EXP_ROLE_IDS = {
    10: 1345467425499385886, 20: 1345467017003536384, 30: 1345802923493298286,
    40: 1348597989760958544, 50: 1348597995775590450, 60: 1348597982093774869,
    70: 1348598235861880844, 80: 1348598239619711079, 90: 1348598231533355078, 100: 1348598227246645360
}

USER_EXP = {}
last_exp_data = None  # ใช้เก็บข้อมูล EXP ล่าสุด

# โหลดข้อมูล EXP จากไฟล์
def load_exp_data():
    global USER_EXP
    if os.path.exists(EXP_FILE):
        try:
            with open(EXP_FILE, "r") as f:
                USER_EXP = json.load(f)
                if not isinstance(USER_EXP, dict) or not USER_EXP:
                    USER_EXP = {}
        except (json.JSONDecodeError, ValueError):
            USER_EXP = {}

# เซฟข้อมูล EXP ไปยังไฟล์
def save_exp_data():
    global last_exp_data
    if USER_EXP != last_exp_data:  # ตรวจสอบว่า USER_EXP มีการเปลี่ยนแปลง
        with open(EXP_FILE, "w") as f:
            json.dump(USER_EXP, f, indent=4)
        last_exp_data = USER_EXP.copy()  # อัปเดตข้อมูล EXP ล่าสุด

# ฟังก์ชันสำหรับการอัปเดต EXP
def update_user_exp(user_id, exp, level):
    exp += EXP_RATE
    next_level_exp = (level ** 2) * 50
    if exp >= next_level_exp and level < 100:
        level += 1
        exp -= next_level_exp
    USER_EXP[str(user_id)] = (exp, level)
    save_exp_data()

# ฟังก์ชันเช็คและให้ role ตาม level
async def check_and_give_role(member, level):
    guild = member.guild
    for lvl, role_id in EXP_ROLE_IDS.items():
        role = guild.get_role(role_id)
        if level >= lvl and role and role not in member.roles:
            await member.add_roles(role)

# ฟังก์ชันดึงข้อมูล EXP ของ user
def get_user_exp(user_id):
    return USER_EXP.get(str(user_id), (0, 1))
