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
        "location": "全国",
        "fee": "定制报价",
        "desc": "聚焦研究生升学：研究计划书+套磁+笔面试辅导，匹配目标院校与教授方向。",
        "image": "hot1.svg"
    },
    {
        "title": "日本本科入学方案（EJU/直申/校内考）",
        "category": "本科",
        "location": "全国",
        "fee": "定制报价",
        "desc": "根据目标与基础制定备考与申请路线，覆盖材料准备、院校申请与面试辅导。",
        "image": "hot2.svg"
    },
    {
        "title": "SGU 英语项目申请方案（本科/硕士）",
        "category": "SGU",
        "location": "全国",
        "fee": "定制报价",
        "desc": "面向全英文授课项目：选校策略、材料打磨、推荐信与面试全套支持。",
        "image": "hot3.svg"
    },
]

# 留学项目完整列表（项目页展示）
ALL_PROGRAMS = [
    # 本科类
    {
        "id": 1, "title": "日本本科入学（EJU备考 + 院校申请）",
        "category": "本科", "location": "全国",
        "fee": "约80-150万日元/年", "duration": "4年",
        "conditions": "高中毕业（或同等学历），按目标院校要求准备EJU/校内考等",
        "desc": "适合希望进入日本本科的同学：提供选校、备考规划、材料准备与面试辅导。"
    },
    {
        "id": 2, "title": "日本私立大学本科直考（校内考/面试）",
        "category": "本科", "location": "东京",
        "fee": "约100-180万日元/年", "duration": "4年",
        "conditions": "高中毕业，满足目标院校语言/学术要求",
        "desc": "针对私立名校本科入学：校内考策略、面试训练、材料细节把控。"
    },
    {
        "id": 3, "title": "SGU英语授课本科项目",
        "category": "SGU", "location": "东京",
        "fee": "约100-180万日元/年", "duration": "4年",
        "conditions": "高中毕业，托福80+或雅思6.0+，按项目要求准备材料",
        "desc": "无需日语，以英语成绩申请日本顶尖大学SGU项目，适合英语优秀的学生。"
    },
    # 硕士类
    {
        "id": 4, "title": "国公立大学研究生/修士升学（套磁+研究计划）",
        "category": "硕士", "location": "全国",
        "fee": "约50-80万日元/年", "duration": "2-3年",
        "conditions": "本科毕业，具备明确研究方向；按院校要求提供语言成绩",
        "desc": "先以研究生（旁听生）身份入学或直接修士直考，提供研究计划书与套磁支持。"
    },
    {
        "id": 5, "title": "私立大学修士直考项目",
        "category": "硕士", "location": "东京",
        "fee": "约80-150万日元/年", "duration": "2年",
        "conditions": "本科毕业，有相关专业背景；按目标院校要求准备",
        "desc": "针对早稻田、庆应等私立名校，提供笔试面试全方位辅导。"
    },
    {
        "id": 6, "title": "SGU英语授课硕士项目",
        "category": "SGU", "location": "全国",
        "fee": "约50-120万日元/年", "duration": "2年",
        "conditions": "本科毕业，托福85+或雅思6.5+，GPA 3.0+",
        "desc": "全英语授课，无需日语，可申请东大、京大、东工大等顶尖学府。"
    },
    {
        "id": 7, "title": "研究计划书精修与模拟面试（研究生/修士）",
        "category": "硕士", "location": "全国",
        "fee": "定制报价", "duration": "4-8周",
        "conditions": "明确专业方向与目标院校，提供现有材料或大纲",
        "desc": "适合已有目标院校的同学：强化研究逻辑、套磁表达与面试表现。"
    },
    {
        "id": 8, "title": "本科/研究生全流程签证与行前支持",
        "category": "服务", "location": "全国",
        "fee": "定制报价", "duration": "按进度",
        "conditions": "已获得录取/内诺或进入申请后期",
        "desc": "覆盖签证材料清单、时间线管理、住宿与行前准备建议，减少临门一脚风险。"
    },
]

# 发展历程数据（关于我们页）
MILESTONES = [
    {"year": "2015", "event": "机构成立，专注日本本科与研究生升学规划与申请辅导"},
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
    "phone": "13367336095",
    "email": "luojiaj88@outlook.com",
    "wechat": "ljjsosmart",
    "hours": "周一至周五 9:00-18:00，周六 10:00-18:00",
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


# ========== 本地知识库聊天（免费） ==========
KB_DIR = Path(__file__).resolve().parent / "kb"
KB_DOCS_DIR = KB_DIR / "docs"
KB_FAQ_PATH = KB_DIR / "faq.json"

# 统一追加的服务提示语
SERVICE_SUFFIX = "\n\n如需更多服务，请咨询人工客服～"

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
    answer = (answer or "").strip()
    if not answer:
        return SERVICE_SUFFIX.strip()
    if not handoff:
        return answer
    if "如需更多服务，请咨询人工客服" in answer:
        return answer
    return answer + SERVICE_SUFFIX


def _handoff_message() -> str:
    wechat = (CONTACT_INFO.get("wechat") or "").strip()
    return HANDOFF_TEMPLATE.format(wechat=wechat or "")


def _get_session_state(session_id: str | None) -> dict:
    if not session_id:
        return {"intent": None, "slots": {}}
    state = SESSION_STORE.get(session_id)
    if state is None:
        if len(SESSION_STORE) >= SESSION_LIMIT:
            SESSION_STORE.pop(next(iter(SESSION_STORE)))
        state = {"intent": None, "slots": {}}
        SESSION_STORE[session_id] = state
    return state


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


def _normalize_uncertain(answer: str) -> str:
    """把模型输出的‘不确定/需要人工’类话术收敛成站点统一的精简版本。"""
    a = (answer or "").strip()
    if not a:
        return ""
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
    """本地免费聊天接口：
    - 优先匹配 FAQ
    - 次选：从 docs 文档中摘录相关段落
    - 否则：建议转人工
    """
    from flask import request, jsonify

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    session_id = (payload.get("session_id") or "").strip()
    state = _get_session_state(session_id)
    _update_state(question, state)

    faq = _load_faq()
    fallback = faq.get("fallback") or "这个问题可能比较复杂，建议转人工客服。"

    # 统一使用更精简的转人工提示
    fallback = _handoff_message()

    debug = bool((request.args.get('debug') or '').strip())

    if not question:
        return jsonify({"answer": "请先输入你的问题。", "handoff": False})

    if _is_greeting_or_generic(question, state):
        return jsonify({"answer": GUIDE_PROMPT, "handoff": False, "source": "guide"})

    follow_up = _needs_more_info(question, state)
    if follow_up:
        return jsonify({"answer": follow_up, "handoff": False, "source": "followup"})

    score, item = _best_faq_answer(question, faq.get("items", []))

    # 1) FAQ 高置信命中：直接答
    if item and score >= 0.78:
        return jsonify({"answer": item.get("a", ""), "handoff": False, "source": "faq"})

    docs_text = _load_docs_text()

    # 2) 若启用豆包：用“Top FAQ 候选 + 文档最相关段落”作为知识库上下文，让 LLM 生成自然回答
    if _doubao_enabled():
        # Top FAQ 作为上下文（覆盖同义问法）
        top_faq = _top_faq_context(question, faq.get("items", []), k=5)
        faq_ctx_parts = []
        for s, it in top_faq:
            # 放宽阈值：同义/泛问法也能召回到相关FAQ
            if s < 0.35:
                continue
            faq_ctx_parts.append(f"Q: {it.get('q','')}\nA: {it.get('a','')}")
        faq_ctx = "\n\n".join(faq_ctx_parts)

        best_para, best_score, _ = _doc_best_paragraph(question, docs_text)
        doc_ctx = best_para if (best_para and best_score >= 0.16) else ""

        kb_ctx = "\n\n".join([c for c in [faq_ctx, doc_ctx] if c.strip()])

        # 兜底：如果召回不到上下文，就给一个 FAQ 摘要，让模型至少知道你们能回答什么
        if not kb_ctx.strip():
            all_items = faq.get("items", [])
            preview = []
            for it in all_items[:12]:
                q = (it.get("q") or "").strip()
                a = (it.get("a") or "").strip()
                if q and a:
                    preview.append(f"Q: {q}\nA: {a}")
            if preview:
                kb_ctx = "\n\n".join(preview)

        if kb_ctx.strip():
            prompt = (
                "【知识库】\n"
                f"{kb_ctx}\n\n"
                "【用户问题】\n"
                f"{question}\n\n"
                "要求：\n"
                "1) 必须严格基于知识库回答，禁止补充知识库之外的信息。\n"
                "2) 若知识库信息不足以回答，请直接输出：不确定，需要人工客服确认。\n"
                "3) 输出尽量精简、条理清晰。\n"
            )
            llm_answer, llm_err = _doubao_chat(prompt)
            if llm_answer:
                normalized = _normalize_uncertain(llm_answer)
                need_handoff = normalized == _handoff_message()
                resp = {
                    "answer": _append_suffix_once(normalized, handoff=need_handoff),
                    "handoff": need_handoff,
                    "source": "doubao",
                    "llm_enabled": True,
                    "kb_ctx_len": len(kb_ctx),
                }
                if debug:
                    resp["llm_error"] = llm_err
                return jsonify(resp)
            # LLM 调用失败也给出原因（debug 模式）
            if debug:
                return jsonify({
                    "answer": _append_suffix_once(fallback, handoff=True),
                    "handoff": True,
                    "source": "fallback",
                    "llm_enabled": True,
                    "llm_error": llm_err,
                })

    # 3) 不启用 LLM 或 LLM 没拿到结果：回退到文档摘录
    doc_ans = _doc_based_answer(question, docs_text)
    if doc_ans:
        return jsonify({"answer": doc_ans, "handoff": False, "source": "docs"})


    # 4) 最终回退：转人工
    return jsonify({"answer": _append_suffix_once(fallback, handoff=True), "handoff": True, "source": "fallback"})


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
