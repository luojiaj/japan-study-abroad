# -*- coding: utf-8 -*-
"""
日本留学机构官网 - Flask 入口文件
功能：定义路由、提供静态数据给模板渲染
"""

from flask import Flask, render_template  # 导入 Flask 框架和模板渲染函数

# 新增：本地知识库聊天所需
import json
import os
import re
from difflib import SequenceMatcher
from pathlib import Path

# 可选：本地开发时从 .env 加载环境变量（不要提交 .env）
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    # 未安装 python-dotenv 或没有 .env 时不影响运行
    pass

# ========== 创建 Flask 应用实例 ==========
app = Flask(__name__)

# ========== 静态数据定义 ==========
# 以下数据后续可迁移至数据库，目前以 Python 字典/列表形式内联

# 核心优势数据（首页展示）
ADVANTAGES = [
    {
        "icon": "bi-mortarboard-fill",       # Bootstrap Icons 图标类名
        "title": "本科/研究生升学规划",
        "desc": "结合你的背景与目标院校，提供从选校到申请材料的一对一规划，路径清晰、节奏可控。"
    },
    {
        "icon": "bi-journal-check",
        "title": "研究计划书与文书打磨",
        "desc": "研究计划书、CV、动机信等核心材料深度打磨，突出亮点与研究匹配度。"
    },
    {
        "icon": "bi-chat-dots-fill",
        "title": "教授套磁与面试辅导",
        "desc": "包含套磁策略、邮件修改与模拟面试，提高通过率与沟通效率。"
    },
    {
        "icon": "bi-headset",
        "title": "全流程支持（含签证/行前）",
        "desc": "从申请进度管理到签证、住宿与行前准备，全程跟进，关键节点不掉链子。"
    },
]

# 热门项目数据（首页推荐）
HOT_PROGRAMS = [
    {
        "title": "日本研究生入学方案（修士直考/研究生）",
        "category": "硕士",
        "location": "全日本",
        "fee": "定制报价",
        "desc": "聚焦研究生升学：研究计划书+套磁+笔面试辅导，匹配目标院校与教授方向。",
        "image": "hot1.svg"
    },
    {
        "title": "日本本科入学方案（EJU/直申/校内考）",
        "category": "本科",
        "location": "全日本",
        "fee": "定制报价",
        "desc": "根据目标与基础制定备考与申请路线，覆盖材料准备、院校申请与面试辅导。",
        "image": "hot2.svg"
    },
    {
        "title": "SGU 英语项目申请方案（本科/硕士）",
        "category": "SGU",
        "location": "全日本",
        "fee": "定制报价",
        "desc": "面向全英文授课项目：选校策略、材料打磨、推荐信与面试全套支持。",
        "image": "hot3.svg"
    },
]

# 简介页
# 简介页（保留原有的服务介绍）
# 简介页数据（项目官方简介）
INTRODUCTIONS = [
    {
        "title": "日本研究生入学（修士直考/研究生）简介",
        "category": "硕士",
        "desc": "日本研究生教育分为硕士课程与研究生（预科）阶段。申请侧重学术背景与研究潜力，核心环节包括研究计划书撰写、教授套磁及严格的入学考试，旨在选拔具备专业素养的研究型人才。",
        "image": "hot1.svg"
    },
    {
        "title": "日本本科入学（EJU/直申/校内考）简介",
        "category": "本科",
        "desc": "日本本科入学主要采用EJU（日本留学生考试）结合校内考（笔试/面试）的选拔模式。国公立大学通常要求较高的EJU成绩，私立大学选拔方式灵活多样，全面考察学生的学术基础与语言能力。",
        "image": "hot2.svg"
    },
    {
        "title": "SGU 英语项目申请（本科/硕士）简介",
        "category": "本科/硕士",
        "desc": "SGU（Super Global University）项目提供全英文授课学位课程，覆盖本科与硕士阶段。申请者无需日语基础，凭英语成绩及标化成绩直接申请，旨在吸引全球优秀人才，入学门槛较高。",
        "image": "hot3.svg"
    },
]


# ========== 新增：日本顶尖大学数据 ==========
# 包含旧帝国大学、早庆、东工大的详细申请信息
TOP_UNIVERSITIES = [
    {
        "name": "东京大学",
        "name_jp": "東京大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": "医学部6年+4年"},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考(高分)", "校内考(小论文+面试)", "SGU英语项目"], "eju_score_required": "700分以上"},
            "graduate": {"methods": ["联系教授获得内诺", "正式出愿", "入试"], "note": "需提前联系教授"}
        },
        "difficulty": {"level": 5, "stars": "★★★★★", "description": "日本最高峰，EJU需700分以上，校内考难度极大"},
        "tags": ["日本第一", "综合实力最强", "QS世界Top30"],
        "location": "东京都"
    },
    {
        "name": "京都大学",
        "name_jp": "京都大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "校内考(重视数学/理科基础)", "英语项目"], "eju_score_required": "680分以上"},
            "graduate": {"methods": ["AAO审查制度", "联系教授", "出愿"], "note": "需先进行AAO资格审查"}
        },
        "difficulty": {"level": 5, "stars": "★★★★★", "description": "关西第一学府，极度看重学术逻辑与基础能力"},
        "tags": ["诺贝尔奖得主最多", "学术氛围浓厚", "关西第一"],
        "location": "京都府"
    },
    {
        "name": "大阪大学",
        "name_jp": "大阪大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "面试为主"], "eju_score_required": "650分以上", "note": "部分学部有笔试"},
            "graduate": {"methods": ["联系教授", "出愿"], "note": "研究计划书要求高"}
        },
        "difficulty": {"level": 4, "stars": "★★★★☆", "description": "日本规模最大的国立大学之一，理科极强"},
        "tags": ["日本规模最大", "理科强校", "关西重镇"],
        "location": "大阪府"
    },
    {
        "name": "东北大学",
        "name_jp": "東北大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "校内考"], "eju_score_required": "650分以上"},
            "graduate": {"methods": ["材料审查", "面试"], "note": "拥有完善的英文项目"}
        },
        "difficulty": {"level": 4, "stars": "★★★★☆", "description": "东北地方霸主，材料学、理学世界顶尖"},
        "tags": ["材料学世界顶尖", "理学强校", "鲁迅母校"],
        "location": "宫城县"
    },
    {
        "name": "名古屋大学",
        "name_jp": "名古屋大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "面试"], "eju_score_required": "620分以上"},
            "graduate": {"methods": ["材料审查", "面试"], "note": "部分学部支持秋季入学，英语项目较多"}
        },
        "difficulty": {"level": 4, "stars": "★★★★", "description": "中部地区核心，丰田汽车合作紧密，工科强大"},
        "tags": ["中部地区核心", "工科强大", "丰田合作"],
        "location": "爱知县"
    },
    {
        "name": "九州大学",
        "name_jp": "九州大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "小论文", "面试"], "eju_score_required": "600分以上"},
            "graduate": {"methods": ["联系教授", "出愿"], "note": "需提前联系教授"}
        },
        "difficulty": {"level": 3, "stars": "★★★☆", "description": "九州地区第一，理工科实力雄厚"},
        "tags": ["九州地区第一", "理工科强", "工科传统名校"],
        "location": "福冈县"
    },
    {
        "name": "北海道大学",
        "name_jp": "北海道大学",
        "type": "国立",
        "category": "旧帝国大学",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "面试"], "eju_score_required": "600分以上", "note": "重视综合素质"},
            "graduate": {"methods": ["联系教授", "出愿"], "note": "农学、生命科学极强"}
        },
        "difficulty": {"level": 3, "stars": "★★★☆", "description": "北日本旗舰大学，校园优美，入学门槛相对七帝中稍低"},
        "tags": ["日本最大校园", "农学顶尖", "环境优美"],
        "location": "北海道"
    },
    {
        "name": "东京工业大学",
        "name_jp": "東京科学大学",
        "type": "国立",
        "category": "理工专精",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 282000, "annual_fee": 535800, "currency": "JPY", "note": "国立大学统一标准"},
        "application": {
            "undergraduate": {"methods": ["EJU留考(数学物理必考)", "面试"], "eju_score_required": "680分以上", "note": "分数要求极高"},
            "graduate": {"methods": ["材料审查", "面试"], "note": "极其看重研究计划书"}
        },
        "difficulty": {"level": 5, "stars": "★★★★★", "description": "日本理工科专精顶峰，媲美东大工学部"},
        "tags": ["理工科顶峰", "东工大", "纯理工院校"],
        "location": "东京都"
    },
    {
        "name": "早稻田大学",
        "name_jp": "早稲田大学",
        "type": "私立",
        "category": "私立双雄",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 200000, "annual_fee_range": {"min": 1100000, "max": 1750000}, "currency": "JPY", "note": "政治经济学部较贵，理工学部最贵"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "面试/小论文", "英语项目(SILS, TAISI)"], "eju_score_required": "650分以上(王牌学部)"},
            "graduate": {"methods": ["材料审查", "面试"], "note": "部分研究科可英文申请，对跨专业接受度高"}
        },
        "difficulty": {"level": 4, "stars": "★★★★☆", "description": "私立之首，政治经济、法学极难，部分学部适中"},
        "tags": ["私立之首", "政治经济强", "校友网络庞大", "中国人最熟悉"],
        "location": "东京都"
    },
    {
        "name": "庆应义塾大学",
        "name_jp": "慶應義塾大学",
        "type": "私立",
        "category": "私立双雄",
        "system": {"undergraduate": "4年", "master": "2年", "doctoral": "3年", "note": None},
        "tuition": {"entrance_fee": 200000, "annual_fee_range": {"min": 1100000, "max": 1900000}, "currency": "JPY", "note": "医学部学费极高，理工/经济较贵"},
        "application": {
            "undergraduate": {"methods": ["EJU留考", "书类筛选"], "eju_score_required": "650分以上(王牌学部)", "note": "部分学部仅需提交成绩，无笔试，侧重书类筛选"},
            "graduate": {"methods": ["GIGA项目", "英文申请"], "note": "英语项目成熟，看重出身校背景"}
        },
        "difficulty": {"level": 4, "stars": "★★★★☆", "description": "贵族大学，经济、医学、理工极强，校友网络强大"},
        "tags": ["贵族大学", "经济强校", "医学顶尖", "企业家校友多"],
        "location": "东京都/神奈川县"
    }
]


# 留学项目完整列表（项目页展示）
ALL_PROGRAMS = [
    # 本科类
    {
        "id": 1, "title": "日本公立大学本科入学（EJU备考 + 院校申请）",
        "category": "本科", "location": "全日本",
        "fee": "1-3万元人民币", 
        "conditions": "高中毕业（或同等学历），按目标院校要求准备EJU/校内考等",
        "desc": "适合希望进入日本本科的同学：提供选校、备考规划、材料准备与面试辅导。"
    },
    {
        "id": 2, "title": "日本私立大学本科直考（校内考/面试）",
        "category": "本科", "location": "东京",
        "fee": "1-3万元人民币", 
        "conditions": "高中毕业，满足目标院校语言/学术要求",
        "desc": "针对私立名校本科入学：校内考策略、面试训练、材料细节把控。"
    },
    {
        "id": 3, "title": "SGU英语授课本科项目",
        "category": "SGU", "location": "东京",
        "fee": "2-3万元人民币", 
        "conditions": "高中毕业，托福80+或雅思6.0+，按项目要求准备材料",
        "desc": "无需日语，以英语成绩申请日本顶尖大学SGU项目，适合英语优秀的学生。"
    },
    # 硕士类
    {
        "id": 4, "title": "国公立大学研究生/修士升学（套磁+研究计划）",
        "category": "硕士", "location": "全日本",
        "fee": "2-3万元人民币", 
        "conditions": "本科毕业，具备明确研究方向；按院校要求提供语言成绩",
        "desc": "先以研究生（旁听生）身份入学或直接修士直考，提供研究计划书与套磁支持。"
    },
    {
        "id": 5, "title": "私立大学修士直考项目",
        "category": "硕士", "location": "东京",
        "fee": "1-3万元人民币", 
        "conditions": "本科毕业，有相关专业背景；按目标院校要求准备",
        "desc": "针对早稻田、庆应等私立名校，提供笔试面试全方位辅导。"
    },
    {
        "id": 6, "title": "SGU英语授课硕士项目",
        "category": "SGU", "location": "全日本",
        "fee": "2-3万元人民币", 
        "conditions": "本科毕业，托福85+或雅思6.5+，GPA 3.0+",
        "desc": "全英语授课，无需日语，可申请东大、京大、东工大等顶尖学府。"
    },
    {
        "id": 7, "title": "研究计划书精修与模拟面试（研究生/修士）",
        "category": "硕士", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "明确专业方向与目标院校，提供现有材料或大纲",
        "desc": "适合已有目标院校的同学：强化研究逻辑、套磁表达与面试表现。"
    },
    {
        "id": 8, "title": "本科/研究生全流程签证与行前支持",
        "category": "额外服务", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "已获得录取/内诺或进入申请后期",
        "desc": "覆盖签证材料清单、时间线管理、住宿与行前准备建议，减少临门一脚风险。"
    },
    {
        "id": 9, "title": "奖学金申请与学费减免申请",
        "category": "额外服务", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "已获得录取/内诺",
        "desc": "减轻日本留学的开销压力，提供奖学金申请策略、材料准备与申请跟进支持。"
    },
    {
        "id": 10, "title": "学校附近安心租房",
        "category": "额外服务", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "已获得录取/内诺",
        "desc": "根据学长经验与推荐，选择合适的租房平台与房源，提供租房流程指导与注意事项，确保安全顺利入住。"
    },
    {
        "id": 11, "title": "语言培训",
        "category": "额外服务", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "有无基础均可",
        "desc": "根据入学需要提供语言培训服务，本团队老师都是名校毕业或高分考生，能针对性提升日语或英语成绩。"
    },
    {
        "id": 12, "title": "专业课培训",
        "category": "硕士", "location": "全日本",
        "fee": "定制报价", 
        "conditions": "有无基础均可",
        "desc": "根据入学需要提供专业课培训服务，本团队老师都是名校毕业或高分考生，覆盖考试科目广泛能提供详细专业课辅导。"
    },
]

# 发展历程数据（关于我们页）
MILESTONES = [
    {"year": "2020", "event": "团队成立，专注日本研究生升学规划与申请辅导"},
    {"year": "2022", "event": "业务拓展至本科及硕士申请, 留学成功人数超10人"},
    {"year": "2024", "event": "开设线上日语培训课程，服务范围覆盖全日本"},
]

# 团队成员数据
TEAM_MEMBERS = [
    {
        "name": "罗老师",
        "role": "资深留学规划老师",
        "desc": "留日超7年，名古屋大学硕士毕业，深耕日本留学行业10年。",
        "avatar": "Teacher_luo.jpg"
    },
    {
        "name": "汪老师",
        "role": "资深文书撰写老师",
        "desc": "东京大学计算机专业硕士，擅长名校申请及研究计划书指导。",
        "avatar": "Teacher_wang.png"
    }
]

# 合作院校数据
PARTNER_SCHOOLS = [
    "东京大学", "京都大学", "大阪大学", "东北大学",
    "名古屋大学", "早稻田大学", "庆应义塾大学", "东京工业大学",
    "一桥大学", "神户大学", "筑波大学", "北海道大学",
]

# 联系方式数据
CONTACT_INFO = {
    "address": "上海市静安区南京西路688号15楼",
    "phone": "13367336095",
    "email": "luojiaj88@outlook.com",
    "wechat": "ljjsosmart",
    "hours": "周一至周五 9:00-20:00，周六 10:00-24:00",
}


# ========== 路由定义 ==========

@app.route("/")  # 首页路由
def index():
    """渲染首页模板，传入优势数据和热门项目"""
    return render_template(
        "index.html",
        advantages=ADVANTAGES,
        hot_programs=HOT_PROGRAMS,
    )


@app.route("/introduction")  # 简介路由
def introduction():
    """渲染首页模板，传入优势数据和热门项目"""
    return render_template(
        "introduction.html",
        introductions=INTRODUCTIONS,
        universities=TOP_UNIVERSITIES,
    )


@app.route("/programs")  # 留学项目页路由
def programs():
    """渲染留学项目页，传入所有项目数据"""
    return render_template(
        "programs.html",
        programs=ALL_PROGRAMS,
    )


@app.route("/about")  # 关于我们页路由
def about():
    """渲染关于我们页，传入发展历程、团队、合作院校数据"""
    return render_template(
        "about.html",
        milestones=MILESTONES,
        team=TEAM_MEMBERS,
        partners=PARTNER_SCHOOLS,
    )


@app.route("/contact")  # 联系方式页路由
def contact():
    """渲染联系方式页，传入联系信息"""
    return render_template(
        "contact.html",
        info=CONTACT_INFO,
    )


# ========== 在线留言存储 ==========
MESSAGES_FILE = Path(__file__).resolve().parent / "data" / "messages.json"


@app.post("/api/contact-message")
def api_contact_message():
    """接收在线留言，追加保存到 data/messages.json"""
    from flask import request, jsonify
    from datetime import datetime

    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    phone = (payload.get("phone") or "").strip()
    email = (payload.get("email") or "").strip()
    program = (payload.get("program") or "").strip()
    message = (payload.get("message") or "").strip()

    # 基本校验
    if not name or not phone or not message:
        return jsonify({"ok": False, "error": "姓名、联系电话和留言内容不能为空"}), 400

    # 手机号校验：必须是中国手机号（1[3-9]开头，共11位）
    if not re.match(r"^1[3-9]\d{9}$", phone):
        return jsonify({"ok": False, "error": "手机号格式有误，请输入11位中国手机号"}), 400

    record = {
        "name": name,
        "phone": phone,
        "email": email,
        "program": program,
        "message": message,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 读取 → 追加 → 写回
    MESSAGES_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        if MESSAGES_FILE.exists():
            data = json.loads(MESSAGES_FILE.read_text(encoding="utf-8") or "[]")
        else:
            data = []
    except (json.JSONDecodeError, OSError):
        data = []

    data.append(record)
    MESSAGES_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    return jsonify({"ok": True, "message": "留言已提交，我们会尽快联系您！"})


# ========== 本地知识库聊天（免费） ==========
KB_DIR = Path(__file__).resolve().parent / "kb"
KB_DOCS_DIR = KB_DIR / "docs"
KB_FAQ_PATH = KB_DIR / "faq.json"

# 统一追加的服务提示语 - 新策略：所有回答都附加微信建议（不强制转人工）
SERVICE_SUFFIX = "\n\n如需更专业的咨询，请添加客服微信：ljjsosmart"

# 转人工时更精简的提示（会自动拼接微信号）
HANDOFF_TEMPLATE = "具体详情可以咨询留学客服哦，客服微信：{wechat}"
GUIDE_PROMPT = (
    "你好，欢迎咨询日本留学。\n"
    "请问你想了解哪一类项目？\n"
    "1) 本科（EJU/直申/校内考）\n"
    "2) 修士/研究生（研究计划/套磁/考试）\n"
    "3) SGU 英语项目\n"
    "4) 语言学习/行前签证\n"
    "你也可以直接说目标学校/专业/时间点。"
)
FOLLOW_UP_PROMPTS = {
    "undergrad": "方便补充下你的目标专业/学校、入学时间，以及是否有日语或英语成绩吗？",
    "grad": "方便补充下你的研究方向/目标学校、计划入学时间，以及语言成绩情况吗？",
    "sgu": "方便补充下目标学校/专业、入学时间，以及托福/雅思成绩吗？",
    "visa": "方便说明目前进度（是否已拿到录取/内诺）以及预计出发时间吗？",
    "generic": "为了更准确给建议，麻烦补充：目标项目、本科/修士、意向学校或专业、以及计划入学时间。",
}

# FAQ 同义词/别称扩展：提升召回
FAQ_SYNONYMS: dict[str, list[str]] = {
    "修士": ["硕士"],
    "硕士": ["修士"],
    "研究生": ["旁听生", "预科"],
    "套磁": ["联系导师", "导师邮件"],
    "研究计划书": ["研究计划", "rp", "research", "proposal"],
    "sgu": ["英文项目", "英语项目", "英文授课", "英语授课"],
    "eju": ["留考"],
    "jlpt": ["日语等级", "n1", "n2", "n3"],
    "托福": ["toefl"],
    "雅思": ["ielts"],
    "托业": ["toeic"],
    "出愿": ["报名", "申请", "网申"],
    "募集要项": ["招生简章", "募集简章"],
    "合格": ["录取", "通过", "offer"],
    "内诺": ["预录取", "口头录取"],
    "研究科": ["研究院", "学院"],
    "学部": ["本科", "学院"],
    "笔试": ["考试"],
    "面试": ["口试", "面谈"],
    "推荐信": ["推荐函", "推荐人"],
    "语言成绩": ["日语成绩", "英语成绩"],
    "gpa": ["绩点"],
    "学费": ["学杂费", "学费金额"],
    "奖学金": ["学费减免", "奖助学金"],
    "宿舍": ["住宿", "学生宿舍"],
    "签证": ["留学签", "在留"],
    "在留": ["coe", "在留资格"],
}

SESSION_LIMIT = 500
SESSION_STORE: dict[str, dict] = {}
HISTORY_MAX_TURNS = 8
HISTORY_MAX_CHARS = 2000
MAX_TURNS_PER_SESSION = 50 #单词会话最多交互轮数，超过后建议转人工
TURN_LIMIT_MESSAGE = "如需咨询更多信息，请添加客服微信:ljjsosmart。"
ENABLE_LLM = False
INFO_QUERY_MARKERS = [
    "是什么", "什么意思", "含义", "流程", "费用", "条件", "要求", "材料",
    "准备", "怎么", "如何", "多久", "时间", "对比", "区别",
]
KNOWN_SCHOOLS = [
    "东京大学", "京都大学", "大阪大学", "东北大学", "名古屋大学", "早稻田大学",
    "庆应义塾大学", "东京工业大学", "一桥大学", "神户大学", "筑波大学", "北海道大学",
]
MAJOR_HINTS = ["计算机", "软件", "人工智能", "经济", "商科", "教育", "设计", "传媒", "医学", "法律"]

CJK_RE = re.compile(r"[\u4e00-\u9fff]")
TOKEN_SPLIT_RE = re.compile(r"[^a-z0-9\u4e00-\u9fff]+")
DOC_HEADING_RE = re.compile(r"^#{1,6}\s+")
DOC_LIST_RE = re.compile(r"^\s*[-*+]\s+")


def _load_faq():
    if not KB_FAQ_PATH.exists():
        return {
            "welcome": "你好，我是樱路留学助手。",
            "fallback": "问题较复杂，建议转人工客服。",
            "items": [],
        }
    with KB_FAQ_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def _append_suffix_once(answer: str, *, handoff: bool = False) -> str:
    """确保所有答案都附加服务提示语。"""
    answer = (answer or "").strip()
    if not answer:
        return SERVICE_SUFFIX.strip()

    # 避免重复追加提示
    wechat = (CONTACT_INFO.get("wechat") or "").strip()
    if SERVICE_SUFFIX.strip() in answer or "如需更专业的咨询" in answer:
        return answer
    if wechat and wechat in answer:
        return answer

    return answer + SERVICE_SUFFIX


def _handoff_message() -> str:
    wechat = (CONTACT_INFO.get("wechat") or "").strip()
    return HANDOFF_TEMPLATE.format(wechat=wechat or "")


def _get_session_state(session_id: str | None) -> dict:
    if not session_id:
        return {"intent": None, "slots": {}, "history": [], "turns": 0}
    state = SESSION_STORE.get(session_id)
    if state is None:
        if len(SESSION_STORE) >= SESSION_LIMIT:
            SESSION_STORE.pop(next(iter(SESSION_STORE)))
        state = {"intent": None, "slots": {}, "history": [], "turns": 0}
        SESSION_STORE[session_id] = state
    else:
        state.setdefault("history", [])
        state.setdefault("turns", 0)
    return state


def _increment_turns(state: dict) -> int:
    state["turns"] = int(state.get("turns") or 0) + 1
    return state["turns"]


def _append_history(state: dict, role: str, content: str) -> None:
    history = state.setdefault("history", [])
    text = (content or "").strip()
    if not text:
        return
    history.append({"role": role, "content": text})
    if len(history) > HISTORY_MAX_TURNS:
        del history[:len(history) - HISTORY_MAX_TURNS]


def _history_context(state: dict) -> str:
    history = state.get("history") or []
    parts = []
    total = 0
    for item in history:
        role = item.get("role") or ""
        content = (item.get("content") or "").strip()
        if not content:
            continue
        prefix = "用户" if role == "user" else "助手"
        line = f"{prefix}：{content}"
        total += len(line)
        parts.append(line)
        if total >= HISTORY_MAX_CHARS:
            break
    return "\n".join(parts).strip()


def _record_turn(state: dict, question: str, answer: str) -> None:
    _append_history(state, "user", question)
    _append_history(state, "assistant", answer)


def _detect_intent(text: str) -> str | None:
    qn = _normalize_text(text)
    if not qn:
        return None
    if any(k in qn for k in ["sgu", "英文项目", "英语项目", "英文授课", "英语授课"]):
        return "sgu"
    if any(k in qn for k in ["本科", "学部", "eju", "留考", "高中", "高三"]):
        return "undergrad"
    if any(k in qn for k in ["修士", "研究生", "研究计划", "套磁", "导师", "旁听生"]):
        return "grad"
    if any(k in qn for k in ["签证", "在留", "coe", "行前"]):
        return "visa"
    return None


def _extract_slots(text: str, state: dict) -> None:
    qn = _normalize_text(text)
    slots = state.setdefault("slots", {})

    if any(k in qn for k in ["最终学历", "学历", "gpa", "绩点"]):
        if "大专" in qn:
            slots["education"] = "大专"
        elif "本科" in qn or "大学" in qn:
            slots["education"] = "本科"
        elif "研究生" in qn or "硕士" in qn:
            slots["education"] = "硕士"

    year_match = re.search(r"20\d{2}", qn)
    if year_match:
        slots["time"] = year_match.group(0)
    elif any(k in qn for k in ["明年", "今年", "下半年", "上半年", "春季", "秋季", "入学"]):
        slots["time"] = "已提供"

    if any(k in qn for k in ["托福", "雅思", "jlpt", "n1", "n2", "n3", "成绩"]):
        slots["score"] = "已提供"

    if any(k in qn for k in MAJOR_HINTS) or "专业" in qn or "方向" in qn:
        slots["major"] = "已提供"

    for name in KNOWN_SCHOOLS:
        if name in qn:
            slots["school"] = name
            break
    if "学校" in qn or "院校" in qn or "大学" in qn:
        if "学校" in qn or "院校" in qn:
            slots.setdefault("school", "已提供")


def _update_state(question: str, state: dict) -> None:
    if not question:
        return
    intent = _detect_intent(question)
    if intent:
        state["intent"] = intent
    _extract_slots(question, state)


def _is_greeting_or_generic(question: str, state: dict) -> bool:
     qn = _normalize_text(question)
     if not qn:
         return True
     greetings = ["你好", "您好", "hi", "hello", "哈喽", "在吗", "在么"]
     intents = ["想申请", "申请", "咨询", "了解", "留学", "日本留学"]
     specifics = [
         "本科", "修士", "研究生", "sgu", "英语项目", "英文项目", "语言", "签证",
         "研究计划", "套磁", "eju", "jlpt", "托福", "雅思",
     ]
     if state.get("intent"):
         return False
     has_greet = any(g in qn for g in greetings)
     has_intent = any(i in qn for i in intents)
     has_specific = any(s in qn for s in specifics)
     tokens = _tokenize(qn)
     return (has_greet or has_intent) and not has_specific and len(tokens) <= 6


def _needs_more_info(question: str, state: dict) -> str | None:
     qn = _normalize_text(question)
     if not qn:
         return FOLLOW_UP_PROMPTS["generic"]

     if any(m in qn for m in INFO_QUERY_MARKERS):
         return None

     intent = state.get("intent") or _detect_intent(qn)
     slots = state.get("slots", {})

     undergrad = intent == "undergrad"
     grad = intent == "grad"
     sgu = intent == "sgu"
     visa = intent == "visa"

     has_school = bool(slots.get("school"))
     has_major = bool(slots.get("major"))
     has_time = bool(slots.get("time"))
     has_score = bool(slots.get("score"))

     is_background_only = any(k in qn for k in ["最终学历", "学历", "gpa", "绩点"]) and not intent

     if is_background_only:
         return FOLLOW_UP_PROMPTS["generic"]

     if undergrad and not (has_school or has_major or has_time):
         return FOLLOW_UP_PROMPTS["undergrad"]
     if grad and not (has_major or has_time):
         return FOLLOW_UP_PROMPTS["grad"]
     if sgu and not (has_major or has_time or has_score):
         return FOLLOW_UP_PROMPTS["sgu"]
     if visa and not has_time:
         return FOLLOW_UP_PROMPTS["visa"]

     if any(k in qn for k in ["咨询", "想申请", "了解", "留学"]):
         if not (has_school or has_major or has_time):
             return FOLLOW_UP_PROMPTS["generic"]

     return None


def _normalize_text(s: str) -> str:
    s = (s or "").strip().lower()
    s = re.sub(r"[^\w\u4e00-\u9fff]+", " ", s)
    s = re.sub(r"\s+", " ", s)
    return s


def _tokenize(text: str) -> set[str]:
    norm = _normalize_text(text)
    if not norm:
        return set()

    tokens: set[str] = set()
    for chunk in TOKEN_SPLIT_RE.split(norm):
        if not chunk:
            continue
        if CJK_RE.search(chunk):
            tokens.add(chunk)
            if len(chunk) >= 2:
                for i in range(len(chunk) - 1):
                    tokens.add(chunk[i:i + 2])
        else:
            if len(chunk) >= 2:
                tokens.add(chunk)

    expanded = set(tokens)
    for t in tokens:
        for s in FAQ_SYNONYMS.get(t, []):
            norm_s = _normalize_text(s)
            if norm_s:
                expanded.add(norm_s)
    return expanded


def _faq_score(question: str, candidate: str) -> float:
    qn = _normalize_text(question)
    cn = _normalize_text(candidate)
    if not qn or not cn:
        return 0.0

    seq = SequenceMatcher(None, qn, cn).ratio()
    if cn in qn or qn in cn:
        seq = max(seq, 0.92)

    q_tokens = _tokenize(qn)
    c_tokens = _tokenize(cn)
    if not q_tokens or not c_tokens:
        return seq

    overlap = len(q_tokens & c_tokens)
    query_hit = overlap / max(1, len(q_tokens))
    coverage = overlap / max(1, len(c_tokens))
    token_score = 0.65 * query_hit + 0.35 * coverage

    score = max(seq, 0.55 * seq + 0.45 * token_score)
    if overlap >= 2:
        score = min(1.0, score + 0.03)
    return min(1.0, score)


def _best_faq_answer(question: str, faq_items: list[dict]):
    best = (0.0, None)
    for item in faq_items:
        q = item.get("q", "")
        if not q:
            continue
        score = _faq_score(question, q)
        if score > best[0]:
            best = (score, item)
    return best


def _top_faq_context(question: str, faq_items: list[dict], k: int = 3) -> list[tuple[float, dict]]:
    scored: list[tuple[float, dict]] = []
    for item in faq_items:
        q = item.get("q", "")
        if not q:
            continue
        score = _faq_score(question, q)
        scored.append((score, item))
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:k]


def _doc_paragraph_score(question_tokens: set[str], para: str) -> tuple[float, int]:
    para_tokens = _tokenize(para)
    if not question_tokens or not para_tokens:
        return 0.0, 0
    overlap = len(question_tokens & para_tokens)
    if overlap == 0:
        return 0.0, 0
    query_hit = overlap / max(1, len(question_tokens))
    coverage = overlap / max(1, len(para_tokens))
    score = 0.7 * query_hit + 0.3 * coverage
    return score, overlap


def _doc_best_paragraph(question: str, doc_chunks: list[dict]):
    """返回最相关的段落（而不是直接生成答案），用于给 LLM 做上下文。"""
    if not doc_chunks:
        return None, 0.0, 0
    question_tokens = _tokenize(question)
    if not question_tokens:
        return None, 0.0, 0

    best_score = 0.0
    best_para = None
    best_overlap = 0
    for chunk in doc_chunks:
        text = chunk.get("text") or ""
        if not text:
            continue
        score, overlap = _doc_paragraph_score(question_tokens, text)
        weight = float(chunk.get("weight") or 1.0)
        title = (chunk.get("title") or "").strip()
        title_bonus = 0.0
        if title:
            title_score, _ = _doc_paragraph_score(question_tokens, title)
            title_bonus = min(0.12, title_score * 0.12)

        weighted = score * weight + title_bonus
        if weighted > best_score:
            best_score = weighted
            best_para = text
            best_overlap = overlap

    return best_para, best_score, best_overlap


def _doc_based_answer(question: str, docs_text: str):
    """极简文档检索：按关键词命中句子/段落。

    目标：只回答常见问题；不追求生成式回答，避免胡编。
    """
    if not docs_text:
        return None
    best_para, best_score, best_overlap = _doc_best_paragraph(question, docs_text)

    if not best_para or (best_score < 0.18 and best_overlap < 2):
        return None

    return best_para[:480] + ("…" if len(best_para) > 480 else "")


def _doubao_enabled() -> bool:
    return bool(os.getenv("DOUBAO_API_KEY")) and bool(os.getenv("DOUBAO_ENDPOINT"))


def _doubao_chat(prompt: str) -> tuple[str | None, str | None]:
    """返回 (answer, error). error 仅用于调试，不包含敏感信息。"""
    endpoint = os.getenv("DOUBAO_ENDPOINT", "").strip()
    api_key = os.getenv("DOUBAO_API_KEY", "").strip()
    model = os.getenv("DOUBAO_MODEL", "").strip() or "doubao-pro-32k"
    endpoint_id = os.getenv("DOUBAO_ENDPOINT_ID", "").strip()
    if not endpoint or not api_key:
        return None, "missing endpoint or api_key"

    try:
        import requests  # type: ignore
    except Exception:
        return None, "missing requests"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
        # 新增：指定接入点ID（关键！）
        "X-Volc-Endpoint-Id": endpoint_id,
    }
    payload = {
        "model": endpoint_id,
        "messages": [
            {
                "role": "system",
                "content": (
                    "你是樱路留学机构的智能问答助手。\n"
                    "你必须严格基于【知识库】内容回答，禁止编造。\n"
                    "如果知识库没有覆盖或信息不足，请直接说‘不确定/需要人工客服确认’，并建议转人工。\n"
                    "回答用简体中文，尽量简洁明了。"
                ),
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.2,
    }

    try:
        r = requests.post(endpoint, headers=headers, json=payload, timeout=18)
        if r.status_code != 200:
            return None, f"http {r.status_code}: {r.text[:200]}"
        data = r.json()
        content = (((data.get("choices") or [{}])[0].get("message") or {}).get("content") or "").strip()
        return (content or None), None
    except Exception as e:
        return None, f"exception: {type(e).__name__}"


def _normalize_uncertain(answer: str, *, allow_handoff: bool = True) -> str:
    """把模型输出的‘不确定/需要人工’类话术收敛成站点统一的精简版本。"""
    a = (answer or "").strip()
    if not a:
        return ""
    if not allow_handoff:
        return a
    uncertain_markers = [
        "不确定",
        "无法确定",
        "需要人工",
        "建议转人工",
        "转人工",
        "人工客服确认",
        "进一步咨询",
    ]
    if any(m in a for m in uncertain_markers):
        return _handoff_message()
    return a


@app.post("/api/chat")
def api_chat():
    """新策略聊天接口：
    1. FAQ 高置信命中 -> 直接用FAQ答
    2. 知识库有部分命中 + LLM启用 -> LLM基于知识库上下文生成答案
    3. 知识库无命中 + LLM启用 -> LLM自由回答用户问题
    4. 知识库无命中 + LLM未启用 -> 建议转人工
    """
    from flask import request, jsonify

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    session_id = (payload.get("session_id") or "").strip()
    state = _get_session_state(session_id)
    _update_state(question, state)

    faq = _load_faq()
    debug = bool((request.args.get('debug') or '').strip())

    if not question:
        return jsonify({"answer": "请先输入你的问题。", "handoff": False})

    turns = _increment_turns(state)
    if turns > MAX_TURNS_PER_SESSION:
        return jsonify({"answer": TURN_LIMIT_MESSAGE, "handoff": True, "source": "limit"})

    if _is_greeting_or_generic(question, state):
        answer = GUIDE_PROMPT
        _record_turn(state, question, answer)
        return jsonify({"answer": answer, "handoff": False, "source": "guide"})

    follow_up = _needs_more_info(question, state)
    if follow_up:
        answer = follow_up
        _record_turn(state, question, answer)
        return jsonify({"answer": answer, "handoff": False, "source": "followup"})

    score, item = _best_faq_answer(question, faq.get("items", []))

    # 1) FAQ 高置信命中：直接答
    if item and score >= 0.78:
        answer = item.get("a", "")
        answer = _append_suffix_once(answer, handoff=False)
        _record_turn(state, question, answer)
        return jsonify({"answer": answer, "handoff": False, "source": "faq"})

    docs_text = _load_docs_text()
    history_ctx = _history_context(state)
    # 2) 查文档和FAQ做上下文
    top_faq = _top_faq_context(question, faq.get("items", []), k=5)

    # 评估知识库命中度
    faq_ctx_parts = []
    for s, it in top_faq:
        if s >= 0.35:  # 放宽阈值
            faq_ctx_parts.append(f"Q: {it.get('q','')}\nA: {it.get('a','')}")

    best_para, best_score, _ = _doc_best_paragraph(question, docs_text)
    doc_ctx = best_para if (best_para and best_score >= 0.16) else ""

    kb_ctx = "\n\n".join([c for c in ["\n\n".join(faq_ctx_parts), doc_ctx] if c.strip()])
    has_kb_content = bool(kb_ctx.strip())

    # 3) 如果启用 LLM，让模型来决定如何回答
    if ENABLE_LLM and _doubao_enabled():
        if has_kb_content:
            # 知识库有内容：基于知识库回答
            prompt = (
                "【历史对话】\n"
                f"{history_ctx}\n\n"
                "【知识库参考】\n"
                f"{kb_ctx}\n\n"
                "【用户问题】\n"
                f"{question}\n\n"
                "要求：\n"
                "1) 优先基于知识库内容回答。\n"
                "2) 如果知识库有相关内容，按知识库信息如实回答。\n"
                "3) 如果知识库信息不足，可补充专业知识但需指出是个人建议。\n"
                "4) 保持简洁、条理清晰。\n"
            )
        else:
            # 知识库无内容：让AI自由回答
            prompt = (
                "【历史对话】\n"
                f"{history_ctx}\n\n"
                "【用户问题】\n"
                f"{question}\n\n"
                "你是日本留学咨询的专业顾问。请根据你的知识专业回答用户问题。\n"
                "如果关键信息不足，先给出通用建议，并提出1-2个澄清问题。\n"
                "回答要简洁、实用、条理清晰，不要建议转人工。"
            )

        llm_answer, llm_err = _doubao_chat(prompt)
        if llm_answer:
            # LLM的回答如果表示不确定，改为转人工提示
            normalized = _normalize_uncertain(llm_answer, allow_handoff=has_kb_content)
            answer = _append_suffix_once(normalized, handoff=False)
            _record_turn(state, question, answer)
            resp = {
                "answer": answer,
                "handoff": normalized == _handoff_message(),
                "source": "llm_kb" if has_kb_content else "llm_free",
                "llm_enabled": True,
            }
            if debug:
                resp["kb_available"] = has_kb_content
                resp["kb_ctx_len"] = len(kb_ctx)
            return jsonify(resp)

        # LLM调用失败：转人工或使用文档摘录
        if debug:
            answer = _append_suffix_once(_handoff_message(), handoff=True)
            _record_turn(state, question, answer)
            return jsonify({
                "answer": answer,
                "handoff": True,
                "source": "error",
                "llm_enabled": True,
                "llm_error": llm_err,
            })

    # 4) 不启用LLM：尝试文档摘录，否则转人工
    if has_kb_content:
        doc_ans = _doc_based_answer(question, docs_text)
        if doc_ans:
            answer = _append_suffix_once(doc_ans, handoff=False)
            _record_turn(state, question, answer)
            return jsonify({"answer": answer, "handoff": False, "source": "docs"})

    # 5) 最终转人工
    answer = _append_suffix_once(_handoff_message(), handoff=True)
    _record_turn(state, question, answer)
    return jsonify({"answer": answer, "handoff": True, "source": "fallback"})



def _split_markdown_chunks(text: str, source: str) -> list[dict]:
    if not text:
        return []

    lines = text.splitlines()
    chunks: list[dict] = []
    buffer: list[str] = []
    current_title = ""
    current_weight = 1.0

    def flush_buffer():
        nonlocal buffer, chunks, current_title, current_weight
        content = "\n".join([l.rstrip() for l in buffer]).strip()
        if content:
            chunks.append({
                "text": content,
                "title": current_title,
                "weight": current_weight,
                "source": source,
            })
        buffer = []

    for line in lines:
        if DOC_HEADING_RE.match(line):
            flush_buffer()
            current_title = line.lstrip("#").strip()
            current_weight = 1.25
            continue
        if DOC_LIST_RE.match(line):
            flush_buffer()
            item = DOC_LIST_RE.sub("", line).strip()
            if item:
                chunks.append({
                    "text": item,
                    "title": current_title,
                    "weight": 1.1,
                    "source": source,
                })
            continue
        if not line.strip():
            flush_buffer()
            continue
        buffer.append(line)

    flush_buffer()
    return chunks


def _load_docs_text() -> list[dict]:
    if not KB_DOCS_DIR.exists():
        return []
    chunks: list[dict] = []
    for p in sorted(KB_DOCS_DIR.glob("**/*")):
        if p.is_file() and p.suffix.lower() in {".md", ".txt"}:
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            source = str(p.relative_to(KB_DOCS_DIR))
            if p.suffix.lower() == ".md":
                chunks.extend(_split_markdown_chunks(text, source))
            else:
                if text.strip():
                    chunks.append({
                        "text": text.strip(),
                        "title": "",
                        "weight": 1.0,
                        "source": source,
                    })
    return chunks


@app.get("/api/debug/env")
def api_debug_env():
    """仅用于本地调试：检查豆包环境变量是否载入。

    不返回 DOUBAO_API_KEY 原文，只返回是否存在与长度。
    """
    from flask import jsonify

    key = os.getenv("DOUBAO_API_KEY") or ""
    return jsonify({
        "doubao": {
            "endpoint_set": bool(os.getenv("DOUBAO_ENDPOINT")),
            "model": os.getenv("DOUBAO_MODEL"),
            "api_key_set": bool(key),
            "api_key_len": len(key),
        }
    })


# ========== 启动入口 ==========
if __name__ == "__main__":
    # debug=True 开启调试模式，修改代码后自动重启
    # host="0.0.0.0" 允许外部访问（本地开发可改为 "127.0.0.1"）
    # 注意：use_reloader=True 会启动子进程，IDE 断点可能不命中。
    app.run(debug=True, use_reloader=False, host="127.0.0.1", port=5000)
