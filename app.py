# -*- coding: utf-8 -*-
"""
日本留学机构官网 - Flask 入口文件
功能：定义路由、提供静态数据给模板渲染
"""

from flask import Flask, render_template  # 导入 Flask 框架和模板渲染函数

# ========== 创建 Flask 应用实例 ==========
app = Flask(__name__)

# ========== 静态数据定义 ==========
# 以下数据后续可迁移至数据库，目前以 Python 字典/列表形式内联

# 核心优势数据（首页展示）
ADVANTAGES = [
    {
        "icon": "bi-mortarboard-fill",       # Bootstrap Icons 图标类名
        "title": "专业升学指导",
        "desc": "拥有多年日本留学申请经验，提供一对一升学规划，助力每位学生进入理想院校。"
    },
    {
        "icon": "bi-translate",
        "title": "日语能力培训",
        "desc": "从零基础到N1，系统化日语课程体系，搭配外教口语训练，快速提升语言能力。"
    },
    {
        "icon": "bi-building",
        "title": "优质院校资源",
        "desc": "与日本100+语言学校、大学建立合作关系，覆盖东京、大阪、京都等热门地区。"
    },
    {
        "icon": "bi-headset",
        "title": "全程跟踪服务",
        "desc": "从选校、申请、签证到赴日后的生活安顿，提供全流程无忧服务。"
    },
]

# 热门项目数据（首页推荐）
HOT_PROGRAMS = [
    {
        "title": "东京语言学校精选班",
        "category": "语言学校",
        "location": "东京",
        "fee": "约75万日元/年",
        "desc": "精选东京地区优质语言学校，小班授课，升学率高达95%。",
        "image": "hot1.svg"
    },
    {
        "title": "日本本科直通车项目",
        "category": "本科",
        "location": "全国",
        "fee": "约80-150万日元/年",
        "desc": "针对高中毕业生，提供EJU考试辅导+大学申请一站式服务。",
        "image": "hot2.svg"
    },
    {
        "title": "日本名校硕士研究计划",
        "category": "硕士",
        "location": "全国",
        "fee": "约50-100万日元/年",
        "desc": "针对本科毕业生，提供研究计划书指导、教授套磁及院校申请服务。",
        "image": "hot3.svg"
    },
]

# 留学项目完整列表（项目页展示）
ALL_PROGRAMS = [
    # 语言学校类
    {
        "id": 1, "title": "东京银星日本语学校",
        "category": "语言学校", "location": "东京",
        "fee": "约78万日元/年", "duration": "1-2年",
        "conditions": "高中以上学历，日语N5或150学时证明",
        "desc": "位于东京中央区，交通便利，国际化氛围浓厚，升学指导经验丰富。"
    },
    {
        "id": 2, "title": "大阪翼路学园",
        "category": "语言学校", "location": "大阪",
        "fee": "约72万日元/年", "duration": "1-2年",
        "conditions": "高中以上学历，日语N5或150学时证明",
        "desc": "大阪老牌语言学校，升学课程完善，每年大量学生考入国公立大学。"
    },
    {
        "id": 3, "title": "京都国际学院",
        "category": "语言学校", "location": "京都",
        "fee": "约70万日元/年", "duration": "1-2年",
        "conditions": "高中以上学历，日语N5或150学时证明",
        "desc": "位于文化古都京都，学习环境优雅，适合喜欢传统文化的学生。"
    },
    {
        "id": 4, "title": "福冈日本语学校",
        "category": "语言学校", "location": "其他地区",
        "fee": "约65万日元/年", "duration": "1-2年",
        "conditions": "高中以上学历，日语N5或150学时证明",
        "desc": "九州地区代表性语言学校，生活成本低，适合预算有限的学生。"
    },
    # 本科类
    {
        "id": 5, "title": "日本大学本科直申项目",
        "category": "本科", "location": "全国",
        "fee": "约80-150万日元/年", "duration": "4年",
        "conditions": "高中毕业，日语N2以上，EJU成绩",
        "desc": "针对日语达标的学生，直接申请日本大学本科，免去语言学校阶段。"
    },
    {
        "id": 6, "title": "SGU英语授课本科项目",
        "category": "本科", "location": "东京",
        "fee": "约100-180万日元/年", "duration": "4年",
        "conditions": "高中毕业，托福80+或雅思6.0+",
        "desc": "无需日语，以英语成绩申请日本顶尖大学SGU项目，适合英语优秀的学生。"
    },
    {
        "id": 7, "title": "美术/音乐类本科留学",
        "category": "本科", "location": "东京",
        "fee": "约100-200万日元/年", "duration": "4年",
        "conditions": "高中毕业，具备相关专业作品集，日语N2以上",
        "desc": "针对艺术类学生，提供作品集指导、考试培训和院校申请一条龙服务。"
    },
    # 硕士类
    {
        "id": 8, "title": "国公立大学研究生项目",
        "category": "硕士", "location": "全国",
        "fee": "约50-80万日元/年", "duration": "2-3年",
        "conditions": "本科毕业，日语N1或英语托福80+，有研究方向",
        "desc": "先以研究生（旁听生）身份入学，通过院内考试后转为正式修士。"
    },
    {
        "id": 9, "title": "私立大学修士直考项目",
        "category": "硕士", "location": "东京",
        "fee": "约80-150万日元/年", "duration": "2年",
        "conditions": "本科毕业，日语N1，有相关专业背景",
        "desc": "针对早稻田、庆应等私立名校，提供笔试面试全方位辅导。"
    },
    {
        "id": 10, "title": "SGU英语授课硕士项目",
        "category": "硕士", "location": "全国",
        "fee": "约50-120万日元/年", "duration": "2年",
        "conditions": "本科毕业，托福85+或雅思6.5+，GPA 3.0+",
        "desc": "全英语授课，无需日语，可申请东大、京大、东工大等顶尖学府。"
    },
]

# 发展历程数据（关于我们页）
MILESTONES = [
    {"year": "2015", "event": "机构成立，专注日本语言学校申请服务"},
    {"year": "2017", "event": "业务拓展至本科及硕士申请，累计服务学生突破500人"},
    {"year": "2019", "event": "与日本50+院校建立官方合作关系"},
    {"year": "2021", "event": "开设线上日语培训课程，服务范围覆盖全国"},
    {"year": "2023", "event": "合作院校突破100所，累计服务学生超过3000人"},
    {"year": "2025", "event": "全新官网上线，持续深耕日本留学服务"},
]

# 团队成员数据
TEAM_MEMBERS = [
    {
        "name": "田中老师",
        "role": "创始人 / 首席留学顾问",
        "desc": "留日10年，东京大学硕士毕业，深耕日本留学行业15年。",
        "avatar": "team1.svg"
    },
    {
        "name": "王老师",
        "role": "升学指导主管",
        "desc": "早稻田大学教育学硕士，擅长名校申请及研究计划书指导。",
        "avatar": "team2.svg"
    },
    {
        "name": "佐藤老师",
        "role": "日语教学总监",
        "desc": "日本籍资深教师，持有日语教育能力检定证书，教学经验丰富。",
        "avatar": "team3.svg"
    },
    {
        "name": "李老师",
        "role": "签证及生活顾问",
        "desc": "熟悉日本签证政策及生活指南，为学生提供赴日前后全方位支持。",
        "avatar": "team4.svg"
    },
]

# 合作院校数据
PARTNER_SCHOOLS = [
    "东京大学", "京都大学", "大阪大学", "东北大学",
    "名古屋大学", "早稻田大学", "庆应义塾大学", "东京工业大学",
    "一桥大学", "神户大学", "筑波大学", "北海道大学",
]

# 联系方式数据
CONTACT_INFO = {
    "address": "上海市静安区南京西路1234号XX大厦15楼",
    "phone": "021-1234-5678",
    "email": "info@japan-study.example.com",
    "wechat": "JapanStudy2025",
    "hours": "周一至周五 9:00-18:00，周六 10:00-16:00",
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


# ========== 启动入口 ==========
if __name__ == "__main__":
    # debug=True 开启调试模式，修改代码后自动重启
    # host="0.0.0.0" 允许外部访问（本地开发可改为 "127.0.0.1"）
    app.run(debug=True, host="127.0.0.1", port=5000)
