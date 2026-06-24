# -*- coding: utf-8 -*-
from __future__ import annotations

import html
import json
import re
import warnings
from pathlib import Path

from pypdf import PdfReader


BASE = Path(__file__).resolve().parent
OUT = BASE / "index.html"
BASICS_JSON = BASE / "data" / "python_basics_pass_flow_cards_v3_plain_detailed.min.json"
BASICS_JSON_FALLBACK = BASE / "python_basics_pass_flow_cards.json"
MOBA_JSON = BASE / "data" / "python_moba_analogy_cards.json"
MOBA_JSON_FALLBACK = BASE / "python_moba_analogy_cards.json"
CODE_EXPLANATIONS_JSON = BASE / "data" / "code_explanations_final.min.json"

DOC_META = {
    "0fffcad7398027bbcb2596207e4aca56(1).pdf": {
        "id": "week9",
        "title": "第九周：复习第 1-3 部分",
        "range": "第 1-3 部分",
        "focus": "Python 基础、输入输出、表达式、条件判断",
        "summary": "适合先过基础语法和常见计算题，包含海伦公式、一元二次方程、邮费计算、整数拆分、奇偶判断等入门题。",
        "sections": [
            {"name": "第一部分：Python 基础知识", "desc": "变量、输入输出、算术运算、格式化输出、math 模块和基础数据转换。"},
            {"name": "第二部分：选择结构基础", "desc": "用 if / else 判断边界条件，处理奇偶、成绩、邮费、方程实根等题型。"},
            {"name": "第三部分：综合基础练习", "desc": "把表达式、条件判断和输出格式组合起来，训练考试常见的小程序。"},
        ],
        "topics": ["海伦公式", "一元二次方程", "大象喝水桶数", "邮费计算", "三位数反转", "整除与取余", "奇偶判断", "格式化输出"],
    },
    "56da02b3ee723a50851c58b0459a1e84(1).pdf": {
        "id": "week10",
        "title": "第十周：复习第 4-5 部分",
        "range": "第 4-5 部分",
        "focus": "for 循环、累加、字符串遍历、基础算法",
        "summary": "围绕 for 循环展开，重点是累加求和、阶乘、成绩统计、字符串统计、完数和图形打印。",
        "sections": [
            {"name": "第四部分：For 循环结构", "desc": "range、累加器、增强赋值、列表遍历、字符串遍历和循环中的条件分支。"},
            {"name": "第五部分：循环综合应用", "desc": "用循环解决统计、排序、数字规律、完数判断和星号图形输出。"},
        ],
        "topics": ["交错求和", "分数序列", "阶乘", "班级成绩统计", "Sn 数列", "元音计数", "学号年级统计", "完数", "金字塔图形"],
    },
    "3459e737b2ff0e9b096faaa9bcb445fd(1).pdf": {
        "id": "week11",
        "title": "第十一周：复习第 6-7 部分",
        "range": "第 6-7 部分",
        "focus": "while、break、循环 else、循环嵌套",
        "summary": "集中复习流程控制的进阶写法，尤其是 while True、循环 else、提前结束循环和多层循环打印图形。",
        "sections": [
            {"name": "第六部分：流程控制的其他语句", "desc": "登录验证、猜年龄、买房年限、回文数、水仙花数和血压测量。"},
            {"name": "第七部分：循环的嵌套", "desc": "星号金字塔、字符矩形、数字金字塔等双层循环输出题。"},
        ],
        "topics": ["登录验证", "猜年龄", "买房年限", "回文数", "水仙花数", "血压测量", "星号金字塔", "字符矩形", "数字金字塔"],
    },
    "python.pdf": {
        "id": "week12",
        "title": "第十二周：复习第 8-9 部分",
        "range": "第 8-9 部分",
        "focus": "列表、字典、字符串、随机模块",
        "summary": "适合最后整合组合数据类型，覆盖列表统计、选择排序、矩阵、字典增删改查、字符串处理和验证码生成。",
        "sections": [
            {"name": "第八部分：组合数据类型", "desc": "列表、二维列表、字典、遍历、排序、随机抽样和成绩字典。"},
            {"name": "第九部分：字符串与常用模块", "desc": "字符串统计、字符处理、随机验证码、random.choice 等常见综合题。"},
        ],
        "topics": ["列表求和平均", "最大值与方差", "选择排序", "矩阵对角线", "随机抽学号", "字典操作", "成绩排序", "字符串处理", "验证码"],
    },
}

MANUAL_CODE_BLOCKS = {
    ("0fffcad7398027bbcb2596207e4aca56(1).pdf", 8): [
        """x = eval(input("被除数："))
y = eval(input("除数："))
if y != 0:
    print(x / y)
else:
    print("除数不能为零")"""
    ],
    ("0fffcad7398027bbcb2596207e4aca56(1).pdf", 11): [
        """correct_username = "user"
username = input("请输入用户名：").strip()
if username.lower() == correct_username:
    print("登录成功！")
else:
    print("用户名错误，请重试。")"""
    ],
    ("0fffcad7398027bbcb2596207e4aca56(1).pdf", 21): [
        """import math

weight = int(input("请输入重量（克）："))
urgent = input("是否加急（y/n）：").strip().lower()

fee = 8
if weight > 1000:
    extra_weight = weight - 1000
    fee += math.ceil(extra_weight / 500) * 4

if urgent == "y":
    fee += 5

print("邮费为{}元".format(fee))"""
    ],
    ("0fffcad7398027bbcb2596207e4aca56(1).pdf", 37): [
        """scores = [68, 72, 55, 91, 48, 84]
fail_count = 0
max_score = scores[0]

for score in scores:
    if score < 60:
        fail_count += 1
    if score > max_score:
        max_score = score

print("不及格人数：", fail_count)
print("最高分：", max_score)"""
    ],
    ("0fffcad7398027bbcb2596207e4aca56(1).pdf", 40): [
        """top = eval(input("请输入上底："))
bottom = eval(input("请输入下底："))
height = eval(input("请输入高："))

area = (top + bottom) * height / 2
print("梯形面积为：{:.2f}".format(area))"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 11): [
        """n = int(input("请输入行数："))
for i in range(1, n + 1):
    for j in range(1, i + 1):
        print(j, end="")
    print()"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 12): [
        """s = 0
for i in range(2, 101, 2):
    s += i
print("1-100之间偶数的和为：", s)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 13): [
        """count = 0
for i in range(1, 101):
    if i % 3 == 0 and i % 5 == 0:
        count += 1
print("个数为：", count)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 14): [
        """n = int(input("请输入数据个数："))
min_num = eval(input("请输入第1个数："))

for i in range(2, n + 1):
    num = eval(input("请输入第{}个数：".format(i)))
    if num < min_num:
        min_num = num

print("最小值为：", min_num)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 15): [
        """s = input("请输入字符串：")
lower_count = 0
upper_count = 0
digit_count = 0
other_count = 0

for ch in s:
    if ch.islower():
        lower_count += 1
    elif ch.isupper():
        upper_count += 1
    elif ch.isdigit():
        digit_count += 1
    else:
        other_count += 1

print("小写字母：", lower_count)
print("大写字母：", upper_count)
print("数字字符：", digit_count)
print("其他字符：", other_count)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 19): [
        """n = int(input("请输入一个正整数："))
while n != 1:
    print(n, end=" ")
    if n % 2 == 1:
        n = n * 3 + 1
    else:
        n = n // 2
print(1)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 22): [
        """count = 0
total = 0
max_score = None
min_score = None

while True:
    score = eval(input("请输入成绩（负数结束）："))
    if score < 0:
        break
    count += 1
    total += score
    if max_score is None or score > max_score:
        max_score = score
    if min_score is None or score < min_score:
        min_score = score

if count == 0:
    print("没有输入成绩")
else:
    print("最高分：", max_score)
    print("最低分：", min_score)
    print("平均分：{:.2f}".format(total / count))"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 23): [
        """a = 2
b = 1
total = 0
count = 0

while total <= 20:
    total += a / b
    count += 1
    a, b = a + b, a

print("至少需要累加{}个数".format(count))"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 30): [
        """money = input("请输入金额：").strip()
value = eval(money[:-1])
unit = money[-1]

if unit == "$":
    result = value * 6
    print("{:.2f}R".format(result))
elif unit == "R":
    result = value / 6
    print("{:.2f}$".format(result))
else:
    print("输入格式错误")"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 31): [
        """minutes = int(input("请输入通话分钟数："))
is_package = input("是否固定套餐用户（y/n）：").strip().lower()

if is_package == "y":
    fee = 50
    if minutes > 300:
        fee += (minutes - 300) * 0.1
else:
    fee = minutes * 0.2

print("话费为：{:.2f}元".format(fee))"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 32): [
        """pm = eval(input("请输入PM2.5数值："))

if pm <= 35:
    level = "优"
elif pm <= 75:
    level = "良"
elif pm <= 115:
    level = "轻度污染"
elif pm <= 150:
    level = "中度污染"
elif pm <= 250:
    level = "重度污染"
else:
    level = "严重污染"

print("空气质量等级：", level)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 33): [
        """for i in range(1, 11):
    print(i)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 34): [
        """s = 0
for i in range(1, 101):
    s += i
print("1-100的累加和为：", s)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 39): [
        """n = int(input("请输入测量次数："))
current_hours = 0
max_hours = 0

for i in range(n):
    high = int(input("请输入收缩压："))
    low = int(input("请输入舒张压："))
    if 90 <= high <= 140 and 60 <= low <= 90:
        current_hours += 1
        if current_hours > max_hours:
            max_hours = current_hours
    else:
        current_hours = 0

print("最长正常小时数：", max_hours)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 40): [
        """for i in range(1, 10):
    for j in range(1, i + 1):
        print("{}*{}={}".format(j, i, i * j), end="\\t")
    print()"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 43): [
        """s = input("请输入一串数字：")
count = 0

for ch in s:
    if ch == "0":
        count += 1
    else:
        break

if count == len(s):
    print("输入的数字全部为0")
else:
    print("第一个非零数字前0的个数为：", count)"""
    ],
    ("56da02b3ee723a50851c58b0459a1e84(1).pdf", 44): [
        """for num in range(2, 51):
    for i in range(2, num):
        if num % i == 0:
            break
    else:
        print(num, end=" ")"""
    ],
    ("3459e737b2ff0e9b096faaa9bcb445fd(1).pdf", 4): [
        """n = input("请输入一个正整数：")
if n == n[::-1]:
    print("是回文数")
else:
    print("不是回文数")"""
    ],
    ("3459e737b2ff0e9b096faaa9bcb445fd(1).pdf", 5): [
        """count = 0
while True:
    n = int(input("请输入三位正整数（-1结束）："))
    if n == -1:
        break
    a = n // 100
    b = n // 10 % 10
    c = n % 10
    if 100 <= n <= 999 and a ** 3 + b ** 3 + c ** 3 == n:
        count += 1

print("水仙花数的个数为：", count)"""
    ],
    ("3459e737b2ff0e9b096faaa9bcb445fd(1).pdf", 9): [
        """n = int(input("请输入行数："))
x = 1
while x <= n:
    y = x
    while y >= 1:
        print(y, end="")
        y -= 1
    y = 2
    while y <= x:
        print(y, end="")
        y += 1
    print()
    x += 1"""
    ],
    ("python.pdf", 16): [
        """sentence = input("请输入英文句子：")
words = sentence.lower().split()
counts = {}

for word in words:
    word = word.strip(".,!?;:")
    if word:
        counts[word] = counts.get(word, 0) + 1

for word, count in counts.items():
    print(word, count)"""
    ],
}


CODE_START = re.compile(
    r"(import\s+\w+|from\s+\w+\s+import|[A-Za-z_]\w*\s*(?:[+\-*/%]?=)|"
    r"if\s+|elif\s+|else:|for\s+|while\s+|print\s*\(|break\b|continue\b|"
    r"return\s+|del\s+|try:|except\s+)"
)
CODE_LINE = re.compile(
    r"^(?:import\s+\w+|from\s+\w+\s+import|[A-Za-z_]\w*\s*(?:[+\-*/%]?=)|"
    r"if\s+.+:|elif\s+.+:|else:|for\s+.+:|while\s+.+:|print\s*\(.+\)|"
    r"break\b|continue\b|return\s+.+|del\s+.+|try:|except\s+.+:)"
)
METHOD_LINE = re.compile(r"^方法[一二三四五六七八九十]+：?$")
QUESTION_MARKER = re.compile(r"^(\d{1,2})(?:[、．]|\.\s+)")


def normalize_text(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\s*(第[一二三四五六七八九十]+部分)", r"\n\1", text)
    text = re.sub(r"\s*(\d{1,2}[、．]\s*|\d{1,2}\.\s+)", r"\n\1", text)
    text = re.sub(r"\s*(答案：|方法[一二三四五六七八九十]+：|提示：)", r"\n\1", text)
    text = re.sub(r"\s+(?=(?:import\s+\w+|from\s+\w+\s+import|[A-Za-z_]\w*\s*(?:[+\-*/%]?=)|if\s+|elif\s+|else:|for\s+|while\s+|print\s*\(|break\b|continue\b|return\s+|del\s+|try:|except\s+))", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_code_line(line: str) -> str | None:
    line = line.strip()
    if METHOD_LINE.match(line):
        return line
    match = CODE_START.search(line)
    if not match:
        return None
    line = line[match.start():].strip()
    line = re.split(r"\s+(?=\d{1,2}[、．]\s|\d{1,2}\.\s+)|\s+(?=第[一二三四五六七八九十]+部分)|\s+(?=答案：|方法[一二三四五六七八九十]+：|提示：)", line)[0].strip()
    return line if CODE_LINE.match(line) else None


def clean_question(line: str) -> str | None:
    line = line.strip()
    if not re.match(r"^\d{1,2}(?:[、．]\s*|\.\s+)", line):
        return None
    line = re.sub(r"\s+", " ", line)
    line = re.split(r"\s*(答案：|方法[一二三四五六七八九十]+：|提示：|import\s+\w+|[A-Za-z_]\w*\s*(?:[+\-*/%]?=))", line)[0]
    line = line.strip()
    return (line[:150] + "…") if len(line) > 150 else line


def question_number(title: str) -> int | None:
    match = QUESTION_MARKER.match(title.strip())
    return int(match.group(1)) if match else None


def extract_question_titles(text: str) -> list[dict]:
    normalized = normalize_text(text)
    found = []
    seen = set()
    for line in normalized.splitlines():
        title = clean_question(line)
        if not title:
            continue
        number = question_number(title)
        if number is None or number in seen:
            continue
        seen.add(number)
        found.append({"number": number, "title": title})
    return found


def extract_code_blocks(text: str) -> list[dict]:
    normalized = normalize_text(text)
    lines = normalized.splitlines()
    blocks: list[tuple[str, list[str]]] = []
    current: list[str] = []
    current_question = ""
    block_question = ""

    for line in lines:
        question = clean_question(line)
        if question:
            current_question = question

        code = clean_code_line(line)
        if code:
            if not current:
                block_question = current_question
            current.append(code)
            continue
        if current:
            blocks.append((block_question, current))
            current = []
            block_question = ""

    if current:
        blocks.append((block_question, current))

    merged: list[dict] = []
    seen: set[str] = set()
    for question, block in blocks:
        if len(block) == 1 and len(block[0]) < 8:
            continue
        code = "\n".join(block)
        code = re.sub(r"\n{3,}", "\n\n", code).strip()
        if code and code not in seen:
            seen.add(code)
            merged.append({"question": question or "本页延续题目", "code": code})
    return merged[:12]


def page_title(text: str, page_no: int) -> str:
    normalized = normalize_text(text)
    for line in normalized.splitlines():
        line = line.strip()
        if re.match(r"^(第[一二三四五六七八九十]+周|第[一二三四五六七八九十]+部分|\d{1,2}[、．]|\d{1,2}\.\s+)", line):
            return line[:54]
    return f"第 {page_no} 页"


def page_paragraphs(text: str) -> list[str]:
    normalized = normalize_text(text)
    paragraphs = [item.strip() for item in normalized.splitlines() if item.strip()]
    return paragraphs[:36]


def load_docs() -> list[dict]:
    docs = []
    for filename, meta in DOC_META.items():
        reader = PdfReader(str(BASE / filename))
        pages = []
        questions = []
        questions_by_number = {}
        last_question = None
        for index, page in enumerate(reader.pages, start=1):
            raw = page.extract_text() or ""
            page_questions = extract_question_titles(raw)
            code_blocks = extract_code_blocks(raw)
            pages.append(
                {
                    "number": index,
                    "title": page_title(raw, index),
                    "paragraphs": page_paragraphs(raw),
                    "codeBlocks": code_blocks,
                }
            )
            for item in page_questions:
                existing = questions_by_number.get(item["number"])
                if existing:
                    if len(item["title"]) > len(existing["title"]):
                        existing["title"] = item["title"]
                    if index not in existing["sourcePages"]:
                        existing["sourcePages"].append(index)
                    last_question = existing
                    continue
                last_question = {
                    "number": item["number"],
                    "title": item["title"],
                    "codeBlocks": [],
                    "sourcePages": [index],
                }
                questions_by_number[item["number"]] = last_question
                questions.append(last_question)
            for block in code_blocks:
                question = block.get("question") or "本页延续题目"
                q_no = question_number(question)
                target = questions_by_number.get(q_no) if q_no is not None else None
                if target is None and question != "本页延续题目":
                    target = next((item for item in reversed(questions) if item["title"] == question), None)
                if target is None:
                    target = last_question
                if target is None:
                    target = {
                        "number": len(questions) + 1,
                        "title": question,
                        "codeBlocks": [],
                        "sourcePages": [index],
                    }
                    questions.append(target)
                    if q_no is not None:
                        questions_by_number[q_no] = target
                target["codeBlocks"].append(block["code"])
                if index not in target["sourcePages"]:
                    target["sourcePages"].append(index)
                last_question = target
        item = dict(meta)
        item["file"] = filename
        item["pages"] = pages
        item["questions"] = questions
        item["pageCount"] = len(pages)
        item["questionCount"] = len(questions)
        for question in item["questions"]:
            manual_blocks = MANUAL_CODE_BLOCKS.get((filename, question["number"]))
            if manual_blocks and not question.get("codeBlocks"):
                question["codeBlocks"] = manual_blocks
        docs.append(item)
    return docs


def load_basics() -> dict:
    path = BASICS_JSON if BASICS_JSON.exists() else BASICS_JSON_FALLBACK
    if not path.exists():
        return {"title": "Python 新手训练营", "subtitle": "", "sourceNotes": "", "fieldLabels": {}, "sections": []}
    raw = json.loads(path.read_text(encoding="utf-8"))
    sections = raw.get("sections", []) if isinstance(raw, dict) else raw
    merged_sections = merge_moba_cards(sections if isinstance(sections, list) else [])
    field_labels = dict(raw.get("fieldLabels", {}) if isinstance(raw, dict) else {})
    field_labels["teacherTalk"] = "提醒"
    field_labels.pop("plainExplainLong", None)
    return sanitize_basics_text(
        {
            "title": raw.get("title", "Python 新手训练营") if isinstance(raw, dict) else "Python 新手训练营",
            "subtitle": raw.get("subtitle", "") if isinstance(raw, dict) else "",
            "sourceNotes": raw.get("sourceNotes", "") if isinstance(raw, dict) else "",
            "fieldLabels": field_labels,
            "sections": merged_sections,
        }
    )


def load_code_explanations() -> dict:
    if not CODE_EXPLANATIONS_JSON.exists():
        return {"schemaVersion": "1.0.0", "questions": []}
    raw = json.loads(CODE_EXPLANATIONS_JSON.read_text(encoding="utf-8"))
    if isinstance(raw, dict):
        return raw
    return {"schemaVersion": "1.0.0", "questions": raw if isinstance(raw, list) else []}


def load_moba_cards() -> list[dict]:
    path = MOBA_JSON if MOBA_JSON.exists() else MOBA_JSON_FALLBACK
    if not path.exists():
        return []
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    cards = raw.get("cards", []) if isinstance(raw, dict) else []
    return cards if isinstance(cards, list) else []


def merge_moba_cards(sections: list[dict]) -> list[dict]:
    extra_fields = ["analogyTitle", "analogy", "mobaTip", "codeMapping", "commonMistakes", "miniExample", "coreConcept"]
    moba_cards = load_moba_cards()
    by_id = {str(card.get("id", "")): card for card in moba_cards if card.get("id")}
    by_title = {str(card.get("title", "")): card for card in moba_cards if card.get("title")}
    merged = []
    for section in sections:
        item = dict(section)
        extra = by_id.get(str(item.get("id", ""))) or by_title.get(str(item.get("title", ""))) or {}
        for field in extra_fields:
            if field in extra and field not in item:
                item[field] = extra[field]
        merged.append(item)
    return merged


def sanitize_basics_text(value):
    replacements = {
        "\u53ca\u683c": "入门通关",
        "\u4fdd\u547d": "核心",
        "\u6551\u547d": "核心",
        "\u5dee\u751f": "新手",
        "\u5b66\u6e23": "新手",
        "\u6302\u79d1": "未达成条件",
    }
    if isinstance(value, str):
        for old, new in replacements.items():
            value = value.replace(old, new)
        return value
    if isinstance(value, list):
        return [sanitize_basics_text(item) for item in value]
    if isinstance(value, dict):
        return {key: sanitize_basics_text(item) for key, item in value.items()}
    return value


def render_html(data: list[dict], basics: dict, code_explanations: dict) -> str:
    data_json = json.dumps(data, ensure_ascii=True)
    basics_json = json.dumps(basics, ensure_ascii=True)
    code_explanations_json = json.dumps(code_explanations, ensure_ascii=True)
    code_explanations_json_tag = code_explanations_json.replace("</", "<\\/")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Python 开始学吧</title>
  <style>
    @import url("https://fonts.cdnfonts.com/css/ibm-3270");

    :root {{
      --ink: #172033;
      --muted: #667085;
      --line: rgba(26, 41, 66, 0.14);
      --paper: #f7f9fd;
      --panel: rgba(255, 255, 255, 0.78);
      --accent: #2968ff;
      --accent-soft: #eaf1ff;
      --green: #157a5b;
      --rose: #b43b5b;
      --amber: #a96600;
      --code: rgba(9, 16, 31, 0.78);
      --code-font-size: 16px;
      --basics-font-size: 15px;
      --shadow: 0 26px 70px rgba(28, 45, 82, 0.14);
      --mono: "JetBrains Mono", "IBM 3270", "IBM Plex Mono", Consolas, monospace;
      --stage-width: 1112px;
      --library-width: 688px;
    }}

    * {{ box-sizing: border-box; }}

    body {{
      margin: 0;
      color: var(--ink);
      font-family: var(--mono);
      background: #ffffff;
      overflow-x: auto;
    }}

    body::before {{
      content: none;
    }}

    body:not(.app-started) .shell,
    body:not(.app-started) .memory-entry {{
      visibility: hidden;
      pointer-events: none;
    }}

    body.app-basics {{
      overflow-x: hidden;
    }}

    body.app-basics .shell,
    body.app-basics .left-bg-zone,
    body.app-basics .memory-entry,
    body.app-basics .return-start-fixed,
    body.app-basics .start-gate {{
      display: none;
    }}

    /* edition signature card */
    .edition-signature-card {{
      position: fixed;
      right: 22px;
      top: 50%;
      width: clamp(96px, 6.2vw, 118px);
      z-index: 1200;
      pointer-events: none;
      opacity: 0.62;
      transform: translateY(-50%);
      filter: saturate(0.92) brightness(0.98) contrast(0.96) blur(0.2px);
    }}

    .edition-signature-card.is-raised {{
      transform: translateY(-72%);
    }}

    .edition-signature-card::before {{
      content: "";
      position: absolute;
      inset: -12px;
      border-radius: 24px;
      background:
        radial-gradient(circle at 50% 48%, rgba(96, 165, 250, 0.14), rgba(96, 165, 250, 0) 64%),
        radial-gradient(circle at 46% 54%, rgba(255, 255, 255, 0.15), rgba(255, 255, 255, 0) 58%);
      filter: blur(10px);
    }}

    .edition-signature-card img {{
      position: relative;
      display: block;
      width: 100%;
      height: auto;
      object-fit: contain;
      border: 0;
      box-shadow: none;
      border-radius: 18px;
      -webkit-mask-image:
        radial-gradient(circle at center, rgba(0, 0, 0, 1) 48%, rgba(0, 0, 0, 0.82) 66%, rgba(0, 0, 0, 0.42) 82%, rgba(0, 0, 0, 0) 100%);
      mask-image:
        radial-gradient(circle at center, rgba(0, 0, 0, 1) 48%, rgba(0, 0, 0, 0.82) 66%, rgba(0, 0, 0, 0.42) 82%, rgba(0, 0, 0, 0) 100%);
    }}

    /* desktop pet */
    .desktop-pet {{
      position: fixed;
      left: calc(100vw - 156px);
      top: calc(100vh - 168px);
      width: 124px;
      height: 124px;
      z-index: 9999;
      display: grid;
      place-items: center;
      cursor: grab;
      user-select: none;
      touch-action: none;
      filter: drop-shadow(0 14px 18px rgba(15, 23, 42, 0.18));
      animation: petIdleFloat 3.8s ease-in-out infinite;
    }}

    .desktop-pet.dragging {{
      cursor: grabbing;
      animation: none;
      filter: drop-shadow(0 20px 24px rgba(15, 23, 42, 0.25));
    }}

    .desktop-pet.pet-action-jump {{
      animation: petJump 760ms cubic-bezier(.2,.8,.2,1) 1;
    }}

    .desktop-pet.pet-action-sleep {{
      animation: petSleepNod 1.35s ease-in-out 1;
    }}

    .desktop-pet.pet-action-spin {{
      animation: petIdleFloat 3.8s ease-in-out infinite;
    }}

    .desktop-pet-img {{
      width: 118px;
      height: 118px;
      object-fit: contain;
      image-rendering: pixelated;
      image-rendering: crisp-edges;
      pointer-events: none;
    }}

    .desktop-pet.pet-action-spin .desktop-pet-img {{
      animation: petSpin 840ms steps(8) 1;
    }}

    .desktop-pet-bubble {{
      position: absolute;
      right: 8px;
      bottom: calc(100% + 14px);
      width: max-content;
      max-width: min(340px, calc(100vw - 42px));
      padding: 15px 18px;
      border: 4px solid #111;
      border-radius: 3px;
      color: #141414;
      background: #fff;
      box-shadow:
        6px 6px 0 rgba(17, 17, 17, 0.16),
        0 18px 36px rgba(15, 23, 42, 0.14);
      font-family: var(--mono);
      font-size: 15px;
      line-height: 1.55;
      opacity: 0;
      transform: translateY(8px) scale(0.98);
      pointer-events: none;
      transition: opacity 160ms ease, transform 160ms ease;
    }}

    .desktop-pet-bubble::after {{
      content: "";
      position: absolute;
      right: 34px;
      bottom: -13px;
      width: 18px;
      height: 18px;
      background: #fff;
      border-right: 4px solid #111;
      border-bottom: 4px solid #111;
      transform: rotate(45deg);
    }}

    .desktop-pet-bubble.show {{
      opacity: 1;
      transform: translateY(0) scale(1);
    }}

    @keyframes petIdleFloat {{
      0%, 100% {{ transform: translateY(0); }}
      50% {{ transform: translateY(-5px); }}
    }}

    @keyframes petJump {{
      0%, 100% {{ transform: translateY(0) scale(1); }}
      35% {{ transform: translateY(-34px) scale(1.04, 0.96); }}
      62% {{ transform: translateY(0) scale(0.96, 1.04); }}
      78% {{ transform: translateY(-10px) scale(1.02, 0.98); }}
    }}

    @keyframes petSleepNod {{
      0%, 100% {{ transform: translateY(0) rotate(0deg); }}
      25% {{ transform: translateY(3px) rotate(-3deg); }}
      55% {{ transform: translateY(6px) rotate(3deg); }}
      78% {{ transform: translateY(2px) rotate(-2deg); }}
    }}

    @keyframes petSpin {{
      0% {{ transform: rotate(0deg) scale(1); }}
      50% {{ transform: rotate(180deg) scale(1.08); }}
      100% {{ transform: rotate(360deg) scale(1); }}
    }}

    /* game landing page */
    .start-gate {{
      position: fixed;
      inset: 0;
      z-index: 120;
      display: grid;
      place-items: center;
      padding: 28px;
      color: #f8fbff;
      background:
        linear-gradient(90deg, rgba(7, 13, 24, 0.88), rgba(9, 18, 34, 0.64) 46%, rgba(7, 13, 24, 0.92)),
        radial-gradient(circle at 50% 48%, rgba(41,104,255,0.24), transparent 34%),
        url("assets/landing-start.jpg") center / cover no-repeat;
      overflow: hidden;
    }}

    .start-gate::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(rgba(255,255,255,0.04) 50%, rgba(0,0,0,0.08) 50%),
        radial-gradient(circle at 50% 50%, transparent 0 34%, rgba(0,0,0,0.46) 72%);
      background-size: 100% 4px, 100% 100%;
      pointer-events: none;
    }}

    .start-card {{
      position: relative;
      display: grid;
      justify-items: center;
      gap: 14px;
      width: min(620px, calc(100vw - 40px));
      padding: clamp(34px, 6vw, 64px);
      border: 1px solid rgba(184,243,255,0.34);
      border-radius: 8px;
      background: rgba(8, 16, 31, 0.48);
      box-shadow: 0 0 0 1px rgba(255,255,255,0.08) inset, 0 28px 90px rgba(0,0,0,0.42);
      backdrop-filter: blur(14px) saturate(1.25);
      text-align: center;
    }}

    .start-kicker {{
      margin: 0;
      color: #B8F3FF;
      font-size: 13px;
      font-weight: 800;
      letter-spacing: 0;
    }}

    .start-card h1 {{
      margin: 0;
      font-size: clamp(34px, 7vw, 72px);
      line-height: 1.04;
      letter-spacing: 0;
      text-shadow: 0 0 30px rgba(125,183,255,0.42);
    }}

    .start-card p {{
      margin: 0;
      color: rgba(248,251,255,0.76);
      line-height: 1.7;
    }}

    .start-button {{
      min-width: min(340px, 100%);
      min-height: 58px;
      margin-top: 10px;
      border: 1px solid rgba(184,243,255,0.7);
      border-radius: 8px;
      color: #08101f;
      background: linear-gradient(135deg, #ffffff, #B8F3FF 62%, #7DB7FF);
      cursor: pointer;
      font-size: 22px;
      font-weight: 900;
      box-shadow: 0 0 30px rgba(125,183,255,0.32);
    }}

    .start-button:hover {{
      box-shadow: 0 0 42px rgba(184,243,255,0.58);
      transform: translateY(-1px);
    }}

    body.app-started .start-gate {{
      display: none;
    }}

    .start-actions {{
      position: relative;
      display: grid;
      grid-template-columns: minmax(280px, 620px) minmax(260px, 360px);
      gap: 18px;
      align-items: stretch;
      width: min(1040px, calc(100vw - 40px));
    }}

    .start-actions .start-card {{
      width: auto;
    }}

    .landing-visual {{
      position: relative;
      min-height: 360px;
      border: 1px solid rgba(184,243,255,0.3);
      border-radius: 8px;
      overflow: hidden;
      background:
        linear-gradient(180deg, rgba(8,16,31,0.08), rgba(8,16,31,0.34)),
        url("assets/basics-entry.jpg") center / cover no-repeat;
      box-shadow: 0 24px 70px rgba(0,0,0,0.34);
    }}

    .landing-visual::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(rgba(255,255,255,0.04) 50%, rgba(0,0,0,0.08) 50%),
        radial-gradient(circle at 50% 34%, rgba(184,243,255,0.12), transparent 34%),
        linear-gradient(180deg, transparent 42%, rgba(4,10,22,0.72));
      background-size: 100% 4px, 100% 100%, 100% 100%;
      pointer-events: none;
    }}

    /* basics entry */
    .basics-entry-card {{
      position: absolute;
      right: 16px;
      bottom: 16px;
      max-width: 250px;
      display: grid;
      gap: 10px;
      padding: 16px 18px;
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 8px;
      color: #f8fbff;
      background: rgba(15, 23, 42, 0.68);
      backdrop-filter: blur(14px) saturate(1.12);
      box-shadow: 0 18px 40px rgba(0,0,0,0.28);
      cursor: pointer;
      transition: transform 180ms ease, box-shadow 180ms ease, border-color 180ms ease;
    }}

    .basics-entry-card::before {{
      content: none;
    }}

    .basics-entry-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(184,243,255,0.64);
      box-shadow: 0 22px 56px rgba(41,104,255,0.26);
    }}

    .basics-entry-card h2 {{
      margin: 0;
      font-size: 22px;
      line-height: 1.2;
      letter-spacing: 0;
      text-shadow: 0 0 24px rgba(184,243,255,0.32);
    }}

    .basics-entry-card p {{
      margin: 0;
      color: rgba(248,251,255,0.78);
      line-height: 1.6;
      font-size: 13px;
    }}

    .basics-entry-card button {{
      justify-self: start;
      min-height: 38px;
      padding: 0 16px;
      border: 1px solid rgba(184,243,255,0.7);
      border-radius: 8px;
      color: #08101f;
      background: linear-gradient(135deg, #ffffff, #B8F3FF 70%);
      cursor: pointer;
      font-weight: 900;
    }}

    button, input {{ font: inherit; }}

    .shell {{
      min-height: 100vh;
      display: grid;
      grid-template-columns: var(--library-width) minmax(var(--stage-width), max-content);
      min-width: calc(var(--library-width) + var(--stage-width));
      position: relative;
      background: transparent;
    }}

    .left-bg-zone {{
      position: fixed;
      left: 0;
      top: 0;
      width: var(--library-width);
      height: 100vh;
      pointer-events: none;
      overflow: hidden;
      isolation: isolate;
      background: transparent;
      z-index: 0;
    }}

    .left-bg-zone::before {{
      content: "";
      position: absolute;
      inset: -12px -18px -12px -14px;
      background-image: url("assets/sidebar-bg.jpg");
      background-size: cover;
      background-position: center left;
      background-repeat: no-repeat;
      filter: blur(3px) saturate(0.82) brightness(0.96) contrast(0.92);
      transform: scale(1.04);
      opacity: 0.72;
      -webkit-mask-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 1) 0%,
        rgba(0, 0, 0, 0.88) 38%,
        rgba(0, 0, 0, 0.42) 72%,
        rgba(0, 0, 0, 0) 100%
      );
      mask-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 1) 0%,
        rgba(0, 0, 0, 0.88) 38%,
        rgba(0, 0, 0, 0.42) 72%,
        rgba(0, 0, 0, 0) 100%
      );
    }}

    .left-bg-zone::after {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(
          to right,
          rgba(15, 23, 42, 0.32) 0%,
          rgba(30, 41, 59, 0.22) 42%,
          rgba(248, 250, 252, 0.12) 72%,
          rgba(248, 250, 252, 0) 100%
        ),
        linear-gradient(
          180deg,
          rgba(255, 255, 255, 0.12) 0%,
          rgba(210, 226, 238, 0.06) 34%,
          rgba(255, 255, 255, 0) 100%
        ),
        radial-gradient(
          circle at 18% 28%,
          rgba(255, 255, 255, 0.18),
          rgba(255, 255, 255, 0) 42%
        ),
        repeating-linear-gradient(
          120deg,
          rgba(255,255,255,0.035) 0 1px,
          rgba(255,255,255,0) 1px 13px
        );
      backdrop-filter: blur(1.5px);
      -webkit-backdrop-filter: blur(1.5px);
      -webkit-mask-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 0.96) 0%,
        rgba(0, 0, 0, 0.78) 45%,
        rgba(0, 0, 0, 0.28) 76%,
        rgba(0, 0, 0, 0) 100%
      );
      mask-image: linear-gradient(
        to right,
        rgba(0, 0, 0, 0.96) 0%,
        rgba(0, 0, 0, 0.78) 45%,
        rgba(0, 0, 0, 0.28) 76%,
        rgba(0, 0, 0, 0) 100%
      );
    }}

    .library-sidebar {{
      position: sticky;
      top: 0;
      grid-column: 1;
      z-index: 10;
      width: 58px;
      height: 100vh;
      padding: 22px 14px;
      color: #f9fbff;
      overflow: hidden;
      background:
        linear-gradient(90deg, rgba(17,27,45,0.96), rgba(22,39,68,0.92) 72%, rgba(255,255,255,0.0)),
        linear-gradient(110deg, rgba(255,255,255,0.16), transparent 35%);
      border-right: 1px solid rgba(255,255,255,0.2);
      box-shadow: 20px 0 70px rgba(42, 75, 138, 0.12);
      transition: width 420ms cubic-bezier(.2,.8,.2,1), box-shadow 420ms ease;
    }}

    .library-sidebar::before {{
      content: "▦";
      position: absolute;
      top: 20px;
      left: 18px;
      color: #203454;
      width: 28px;
      height: 28px;
      display: grid;
      place-items: center;
      border-radius: 8px;
      background: rgba(255,255,255,0.88);
      box-shadow: 0 0 30px rgba(255,255,255,0.38);
    }}

    .library-sidebar::after {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      display: none;
    }}

    .library-sidebar:hover,
    .library-sidebar:focus-within,
    .library-sidebar.is-open {{
      width: var(--library-width);
      box-shadow: none;
    }}

    .library-sidebar:hover::after,
    .library-sidebar:focus-within::after,
    .library-sidebar.is-open::after {{
      display: none;
    }}

    .side-content {{
      min-width: 330px;
      height: 100%;
      opacity: 0;
      transform: translateX(-18px);
      transition: opacity 260ms ease 120ms, transform 360ms cubic-bezier(.2,.8,.2,1) 80ms;
      overflow-y: auto;
      padding: 24px 8px 32px 18px;
      pointer-events: none;
    }}

    .library-sidebar:hover .side-content,
    .library-sidebar:focus-within .side-content,
    .library-sidebar.is-open .side-content {{
      opacity: 1;
      transform: translateX(0);
      pointer-events: auto;
    }}

    .brand {{ display: grid; gap: 8px; margin-bottom: 28px; }}
    .brand h1 {{ margin: 0; font-size: 28px; line-height: 1.15; letter-spacing: 0; text-shadow: 0 0 18px rgba(255,255,255,0.18); }}
    .brand p {{ margin: 0; color: #b7c0d4; line-height: 1.7; font-size: 14px; }}

    .stat-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 10px;
      margin-bottom: 28px;
    }}

    .stat {{
      border: 1px solid rgba(255, 255, 255, 0.16);
      border-radius: 8px;
      padding: 12px;
      background: rgba(255, 255, 255, 0.07);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.08);
    }}

    .stat strong {{ display: block; font-size: 22px; margin-bottom: 2px; }}
    .stat span {{ color: #b7c0d4; font-size: 12px; }}

    .xp-shell {{
      height: 8px;
      margin: -16px 0 24px;
      border: 1px solid rgba(184,243,255,0.22);
      border-radius: 999px;
      background: rgba(255,255,255,0.08);
      overflow: hidden;
    }}

    .xp-bar {{
      height: 100%;
      width: 0%;
      border-radius: inherit;
      background: linear-gradient(90deg, #7DB7FF, #B8F3FF, #B7F7C4);
      box-shadow: 0 0 16px rgba(184,243,255,0.48);
      transition: width 360ms ease;
    }}

    .return-start {{
      min-height: 34px;
      border: 1px solid rgba(184,243,255,0.32);
      border-radius: 8px;
      color: #eaf4ff;
      background: rgba(255,255,255,0.06);
      cursor: pointer;
      font-size: 12px;
      font-weight: 800;
    }}

    .return-start:hover {{
      color: #08101f;
      background: #B8F3FF;
      box-shadow: 0 0 20px rgba(184,243,255,0.36);
    }}

    .return-start-fixed {{
      position: fixed;
      top: 12px;
      left: 72px;
      z-index: 60;
      display: none;
      min-height: 32px;
      padding: 0 12px;
      border: 1px solid rgba(184,243,255,0.34);
      border-radius: 8px;
      color: #eaf4ff;
      background: rgba(8,16,31,0.72);
      backdrop-filter: blur(10px);
      cursor: pointer;
      font-size: 12px;
      font-weight: 800;
      box-shadow: 0 12px 30px rgba(8,16,31,0.16);
    }}

    body.app-started .return-start-fixed {{
      display: block;
    }}

    .return-start-fixed:hover {{
      color: #08101f;
      background: #B8F3FF;
    }}
    .nav-title {{ margin: 0 0 10px; color: #cbd4e8; font-size: 13px; font-weight: 700; }}

    .chapter-nav {{ display: grid; gap: 8px; }}
    .basics-side-nav {{
      display: grid;
      gap: 7px;
      margin: 18px 0 14px;
    }}

    .basics-side-nav button {{
      min-height: 34px;
      padding: 8px 10px;
      border: 1px solid rgba(184,243,255,0.18);
      border-radius: 8px;
      color: rgba(248,251,255,0.86);
      background: rgba(255,255,255,0.055);
      cursor: pointer;
      text-align: left;
      font-size: 12px;
      font-weight: 800;
    }}

    .basics-side-nav button:hover {{
      color: #0b1324;
      border-color: rgba(184,243,255,0.58);
      background: rgba(184,243,255,0.88);
      box-shadow: 0 0 22px rgba(184,243,255,0.22);
    }}

    .chapter-nav button {{
      width: 100%;
      min-height: 42px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      padding: 10px 12px;
      border: 1px solid rgba(255, 255, 255, 0.14);
      border-radius: 8px;
      color: #f9fbff;
      background: transparent;
      cursor: pointer;
      text-align: left;
    }}
    .chapter-nav button.active, .chapter-nav button:hover {{ background: #f9fbff; color: #182033; }}
    .chapter-nav small {{ color: inherit; opacity: 0.68; white-space: nowrap; }}

    .detail-tabs {{
      display: flex;
      gap: 8px;
      padding: 12px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.96);
    }}

    .detail-tabs button {{
      min-height: 34px;
      padding: 0 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: #fff;
      cursor: pointer;
      font-weight: 900;
    }}

    .detail-tabs button.active,
    .detail-tabs button:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
      box-shadow: 0 10px 24px rgba(41,104,255,0.18);
    }}

    main {{
      position: relative;
      z-index: 1;
      grid-column: 2;
      padding: 34px clamp(18px, 4vw, 58px) 42px;
      min-width: var(--stage-width);
      background: #ffffff;
    }}

    .topbar {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) minmax(240px, 360px);
      gap: 18px;
      align-items: end;
      margin-bottom: 16px;
    }}

    .headline h2 {{
      margin: 0 0 8px;
      font-size: clamp(24px, 3vw, 34px);
      line-height: 1.12;
      letter-spacing: 0;
    }}

    .headline p {{ margin: 0; color: var(--muted); line-height: 1.55; font-size: 14px; }}

    .search {{
      display: flex;
      align-items: center;
      min-height: 42px;
      padding: 0 12px;
      gap: 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: var(--panel);
    }}

    .search span {{ color: var(--accent); font-weight: 700; }}
    .search input {{ width: 100%; border: 0; outline: 0; color: var(--ink); background: transparent; }}

    .doc-strip {{
      display: grid;
      grid-template-columns: 1fr;
      gap: 10px;
      margin: 16px 0;
    }}

    .doc-card {{
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 8px;
      color: #f8fbff;
      background: rgba(255,255,255,0.08);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.12);
      cursor: pointer;
      transition: transform 150ms ease, box-shadow 150ms ease, border-color 150ms ease;
    }}

    .doc-card.active, .doc-card:hover {{
      transform: translateX(4px);
      color: #172033;
      border-color: rgba(255,255,255,0.62);
      background: rgba(255,255,255,0.9);
      box-shadow: 0 14px 34px rgba(255,255,255,0.18), 0 0 22px rgba(184,243,255,0.22);
    }}

    .doc-card header {{ display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }}
    .doc-card h3 {{ margin: 0; font-size: 15px; line-height: 1.32; letter-spacing: 0; }}
    .doc-card p {{
      margin: 0;
      color: currentColor;
      opacity: 0.72;
      line-height: 1.45;
      font-size: 12px;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .badge {{
      flex: 0 0 auto;
      padding: 4px 7px;
      border-radius: 999px;
      background: var(--accent-soft);
      color: var(--accent);
      font-size: 11px;
      font-weight: 700;
      white-space: nowrap;
    }}

    .side-meta {{
      display: none;
      gap: 8px;
      margin: 16px 0;
      padding: 14px;
      border: 1px solid rgba(255,255,255,0.18);
      border-radius: 8px;
      background: rgba(255,255,255,0.08);
    }}

    .side-meta h3 {{
      margin: 0;
      color: #fff;
      font-size: 18px;
      line-height: 1.3;
    }}

    .side-meta p {{
      margin: 0;
      color: rgba(255,255,255,0.74);
      line-height: 1.55;
      font-size: 12px;
    }}

    .question-list {{
      display: grid;
      gap: 7px;
      padding-bottom: 28px;
    }}

    .question-list h4 {{
      margin: 6px 0 4px;
      color: #f9fbff;
      font-size: 13px;
      letter-spacing: 0;
    }}

    .question-list button {{
      width: 100%;
      min-height: 34px;
      padding: 8px 10px;
      border: 1px solid rgba(255,255,255,0.16);
      border-radius: 8px;
      color: rgba(255,255,255,0.82);
      background: rgba(255,255,255,0.06);
      cursor: pointer;
      text-align: left;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }}

    .question-list button.active,
    .question-list button:hover {{
      color: #172033;
      background: rgba(255,255,255,0.92);
      border-color: rgba(255,255,255,0.68);
    }}

    .detail {{
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.84);
      backdrop-filter: blur(8px);
      box-shadow: var(--shadow);
      overflow: hidden;
      width: var(--stage-width);
      min-width: var(--stage-width);
    }}

    .detail-head {{
      padding: 16px 18px;
      border-bottom: 1px solid var(--line);
      background: #fbfcff;
    }}

    .detail-head h3 {{ margin: 0 0 6px; font-size: 22px; letter-spacing: 0; }}
    .detail-head p {{ margin: 0; color: var(--muted); line-height: 1.55; font-size: 14px; }}

    .detail-meta, .tags {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-top: 14px;
    }}

    .detail-meta span, .tags span {{
      padding: 6px 9px;
      border-radius: 999px;
      font-size: 12px;
      font-weight: 700;
      border: 1px solid var(--line);
      background: #fff;
    }}

    .detail-meta span:nth-child(1) {{ color: var(--green); background: #e8f5f0; border-color: #cbe7dc; }}
    .detail-meta span:nth-child(2) {{ color: var(--rose); background: #fdebf0; border-color: #f2c7d3; }}
    .detail-meta span:nth-child(3) {{ color: var(--amber); background: #fff2dc; border-color: #f1d7ad; }}

    .sections {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 14px;
      padding: 12px 18px;
      border-bottom: 1px solid var(--line);
    }}

    .section-item {{
      border-left: 4px solid var(--accent);
      padding: 4px 0 4px 14px;
    }}

    .section-item h4 {{ margin: 0 0 4px; font-size: 15px; letter-spacing: 0; }}
    .section-item p {{ margin: 0; color: var(--muted); line-height: 1.55; font-size: 13px; }}

    .page-toolbar {{
      position: sticky;
      top: 0;
      z-index: 4;
      display: flex;
      align-items: center;
      gap: 8px;
      overflow-x: auto;
      padding: 10px 18px;
      border-bottom: 1px solid var(--line);
      background: rgba(255, 255, 255, 0.94);
      backdrop-filter: blur(10px);
    }}

    .pager-button {{
      flex: 0 0 auto;
      min-width: 76px;
      min-height: 34px;
      border: 1px solid var(--accent);
      border-radius: 8px;
      color: var(--accent);
      background: #fff;
      cursor: pointer;
      font-weight: 700;
    }}

    .pager-button:disabled {{
      color: #a5adbd;
      border-color: var(--line);
      cursor: not-allowed;
    }}

    .page-chips {{
      display: flex;
      gap: 8px;
      overflow-x: auto;
      min-width: 0;
      padding-bottom: 2px;
    }}

    .page-chips button {{
      flex: 0 0 auto;
      min-width: 48px;
      min-height: 36px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: var(--ink);
      cursor: pointer;
    }}

    .page-chips button.active, .page-chips button:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
    }}

    .pages {{
      overflow-x: auto;
      overflow-y: visible;
      padding: 18px;
      position: relative;
      z-index: 2;
      background: #ffffff;
    }}

    .page-track {{
      display: flex;
      width: max-content;
    }}

    .page-card {{
      flex: 0 0 calc(var(--stage-width) - 36px);
      min-width: calc(var(--stage-width) - 36px);
      width: calc(var(--stage-width) - 36px);
      min-height: 790px;
      padding: 22px 22px 76px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.86);
      box-shadow: none;
    }}

    .page-card.focused {{ border-color: var(--accent); box-shadow: 0 0 0 3px rgba(36, 107, 254, 0.12); }}

    .basics-panel {{
      padding: 18px;
      background: #ffffff;
    }}

    .basics-head {{
      display: grid;
      gap: 8px;
      margin-bottom: 14px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.88);
    }}

    .basics-head h3 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
    }}

    .basics-head p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.6;
      font-size: 13px;
    }}

    .basics-filters {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin: 0 0 14px;
    }}

    .basics-filters button {{
      min-height: 32px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 999px;
      color: var(--ink);
      background: #fff;
      cursor: pointer;
      font-size: 12px;
      font-weight: 900;
    }}

    .basics-filters button.active,
    .basics-filters button:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
    }}

    .basics-grid {{
      display: grid;
      gap: 14px;
    }}

    .basic-card {{
      display: grid;
      gap: 12px;
      padding: 16px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.92);
      box-shadow: 0 18px 45px rgba(28,45,82,0.08);
    }}

    .basic-card header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
    }}

    .basic-card h4 {{
      margin: 0;
      font-size: 18px;
      letter-spacing: 0;
    }}

    .basic-card .group-label {{
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }}

    .level-tag {{
      flex: 0 0 auto;
      padding: 5px 9px;
      border: 1px solid rgba(41,104,255,0.18);
      border-radius: 999px;
      color: var(--accent);
      background: var(--accent-soft);
      font-size: 12px;
      font-weight: 900;
    }}

    .basic-goal,
    .basic-summary,
    .basic-output,
    .mini-task {{
      margin: 0;
      color: var(--muted);
      line-height: 1.65;
      font-size: 13px;
    }}

    .basic-points {{
      display: grid;
      gap: 6px;
      margin: 0;
      padding-left: 18px;
      color: #2b3850;
      font-size: 13px;
      line-height: 1.55;
    }}

    .basic-code {{
      overflow: hidden;
      border: 1px solid #1f2a3d;
      border-radius: 8px;
      background: rgba(8, 16, 31, 0.94);
    }}

    .basic-code header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      color: #DDEBFF;
      border-bottom: 1px solid rgba(255,255,255,0.12);
      font-size: 12px;
      font-weight: 900;
    }}

    .copy-code {{
      min-height: 28px;
      padding: 0 10px;
      border: 1px solid rgba(184,243,255,0.34);
      border-radius: 6px;
      color: #B8F3FF;
      background: rgba(255,255,255,0.06);
      cursor: pointer;
      font-size: 12px;
      font-weight: 900;
    }}

    .copy-code:hover {{
      color: #08101f;
      background: #B8F3FF;
    }}

    .basic-code-tools {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}

    .basic-code-font {{
      min-height: 28px;
      padding: 0 9px;
      border: 1px solid rgba(184,243,255,0.26);
      border-radius: 6px;
      color: #DDEBFF;
      background: rgba(255,255,255,0.04);
      cursor: pointer;
      font-size: 12px;
      font-weight: 900;
    }}

    .basic-code-font:hover {{
      color: #08101f;
      background: #DDEBFF;
    }}

    .basic-code pre {{
      margin: 0;
      padding: 14px;
      overflow-x: auto;
      color: #DDEBFF;
      font-family: var(--mono);
      font-size: var(--basics-code-font-size, 16px);
      line-height: 1.55;
      white-space: pre;
    }}

    .exam-tip {{
      margin: 0;
      padding: 10px 12px;
      border: 1px solid #cfe1ff;
      border-radius: 8px;
      color: #244166;
      background: #f0f6ff;
      line-height: 1.6;
      font-size: 13px;
      font-weight: 800;
    }}

    /* basics page */
    .basics-page {{
      position: relative;
      min-height: 100vh;
      display: none;
      overflow-x: hidden;
      padding: 22px clamp(18px, 4vw, 58px) 48px;
      background: #f8fafc;
      color: var(--ink);
    }}

    body.app-basics .basics-page {{
      display: block;
    }}

    /* basics background */
    .basics-page::before {{
      content: "";
      position: fixed;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(90deg, rgba(248,250,252,0.14) 0%, rgba(248,250,252,0.72) 36%, rgba(248,250,252,0.96) 64%, rgba(248,250,252,1) 100%),
        url("assets/basics-bg.jpg");
      background-size: cover;
      background-position: left center;
      background-repeat: no-repeat;
      filter: blur(8px) saturate(0.65) brightness(1.05) contrast(0.82);
      opacity: 0.62;
      z-index: 0;
    }}

    .basics-page > * {{
      position: relative;
      z-index: 1;
    }}

    .basics-topbar {{
      display: grid;
      grid-template-columns: auto auto minmax(0, 1fr) auto;
      gap: 10px;
      align-items: center;
      max-width: 1240px;
      margin: 0 auto 18px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.82);
      backdrop-filter: blur(14px);
      box-shadow: var(--shadow);
    }}

    .basics-topbar h1 {{
      margin: 0;
      font-size: 24px;
      letter-spacing: 0;
    }}

    .basics-nav-button,
    .basics-font button {{
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: #fff;
      cursor: pointer;
      font-weight: 900;
    }}

    .basics-nav-button:hover,
    .basics-font button:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
    }}

    .basics-font {{
      display: inline-flex;
      gap: 6px;
    }}

    .basics-layout {{
      max-width: 1240px;
      margin: 0 auto;
      display: grid;
      grid-template-columns: 210px minmax(0, 1fr);
      gap: 18px;
      align-items: start;
    }}

    .basics-directory {{
      position: sticky;
      top: 18px;
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.82);
      backdrop-filter: blur(14px);
    }}

    .basics-dir-title {{
      margin: 0 0 4px;
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }}

    .basics-directory button {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      min-height: 36px;
      padding: 0 12px;
      border: 1px solid transparent;
      border-radius: 8px;
      color: var(--ink);
      background: transparent;
      cursor: pointer;
      text-align: left;
      font-weight: 900;
    }}

    .basics-directory small {{
      color: inherit;
      opacity: 0.72;
      font-family: var(--mono);
    }}

    .basics-directory button.active,
    .basics-directory button:hover {{
      color: #fff;
      border-color: var(--accent);
      background: var(--accent);
      box-shadow: 0 12px 26px rgba(41,104,255,0.18);
    }}

    .basics-reader {{
      display: grid;
      gap: 14px;
      font-size: var(--basics-font-size);
    }}

    .training-cards {{
      display: grid;
      gap: 16px;
    }}

    .training-head {{
      padding: 20px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.88);
      backdrop-filter: blur(12px);
      box-shadow: var(--shadow);
    }}

    .training-head h2 {{
      margin: 0 0 8px;
      font-size: 30px;
      letter-spacing: 0;
    }}

    .training-head p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.65;
      font-size: var(--basics-font-size);
    }}

    .training-card {{
      display: grid;
      gap: 14px;
      padding: 18px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.9);
      backdrop-filter: blur(10px);
      box-shadow: 0 18px 45px rgba(28,45,82,0.08);
    }}

    .training-card header {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 14px;
    }}

    .training-card h3 {{
      margin: 4px 0 0;
      font-size: calc(var(--basics-font-size) + 5px);
      letter-spacing: 0;
    }}

    .training-card h4 {{
      margin: 0 0 8px;
      font-size: calc(var(--basics-font-size) + 1px);
      letter-spacing: 0;
    }}

    .training-card p,
    .training-card li,
    .mapping-table,
    .mistake-list {{
      font-size: var(--basics-font-size);
      line-height: 1.65;
    }}

    .training-card-v3 {{
      gap: 16px;
    }}

    .plain-quick-take {{
      max-width: 820px;
      margin: 10px 0 0;
      padding: 10px 12px;
      border-left: 4px solid var(--accent);
      border-radius: 8px;
      background: #eef5ff;
      color: #12345a;
      font-weight: 900;
      line-height: 1.65;
    }}

    .plain-section {{
      display: grid;
      gap: 10px;
    }}

    .plain-section h4 {{
      margin: 0;
      color: #17233a;
      font-size: calc(var(--basics-font-size) + 1px);
      letter-spacing: 0;
    }}

    .plain-long p {{
      max-width: 880px;
      margin: 0;
      color: #334155;
      line-height: 1.85;
    }}

    .step-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
      gap: 10px;
    }}

    .step-card {{
      padding: 12px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fbff;
    }}

    .step-card span {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 34px;
      height: 24px;
      border-radius: 999px;
      background: #e8f0ff;
      color: #245ef5;
      font-family: var(--mono);
      font-size: 12px;
      font-weight: 900;
    }}

    .step-card p {{
      margin: 8px 0 0;
      color: #334155;
    }}

    .core-pattern {{
      display: grid;
      gap: 8px;
      padding: 12px;
      border: 1px solid #cfe1ff;
      border-radius: 8px;
      background: #f4f8ff;
    }}

    .core-pattern code {{
      display: block;
      overflow-x: auto;
      color: #18365f;
      font-family: var(--mono);
      white-space: pre;
    }}

    .plain-analogy {{
      padding: 12px 14px;
      border: 1px solid rgba(41,104,255,0.16);
      border-radius: 8px;
      background: linear-gradient(135deg, #f6fbff, #fff);
      color: #17355f;
    }}

    .plain-analogy p {{
      margin: 0;
    }}

    .reader-code-box summary {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 8px 10px;
      color: #DDEBFF;
      border-bottom: 1px solid rgba(255,255,255,0.12);
      font-size: 12px;
      font-weight: 900;
      cursor: pointer;
    }}

    .reader-code-box:not([open]) summary {{
      border-bottom: 0;
    }}

    .warning-list {{
      padding: 12px 14px;
      border-color: #fed7aa;
      border-radius: 8px;
      background: #fff7ed;
      color: #7c2d12;
    }}

    .warning-list h4 {{
      color: #9a3412;
    }}

    .soft-tip {{
      margin: 0;
      padding: 10px 12px;
      border: 1px solid #dbeafe;
      border-radius: 8px;
      background: #f8fbff;
      color: #244166;
      font-size: calc(var(--basics-font-size) - 1px);
      line-height: 1.65;
    }}

    .teacherTalk {{
      border-color: #e2e8f0;
      background: #f1f5f9;
      color: #334155;
    }}

    .mini-task-detail {{
      padding: 10px 12px;
      border: 1px dashed #cbd5e1;
      border-radius: 8px;
      background: #fff;
    }}

    .mini-task-detail summary {{
      color: #244166;
      font-weight: 900;
      cursor: pointer;
    }}

    .mini-task-detail p {{
      margin: 10px 0 0;
      color: #334155;
    }}

    /* moba analogy */
    .moba-box {{
      padding: 12px 14px;
      border: 1px solid rgba(41,104,255,0.18);
      border-radius: 8px;
      color: #17355f;
      background: linear-gradient(135deg, #edf6ff, #f8fbff);
    }}

    .moba-box h4 {{
      margin: 0 0 6px;
      font-size: var(--basics-font-size);
      letter-spacing: 0;
    }}

    .moba-box p {{
      margin: 0 0 6px;
    }}

    .moba-box p:last-child {{
      margin-bottom: 0;
      font-weight: 800;
    }}

    /* vscode-like reader */
    .editor-box {{
      border: 1px solid #1f2a3d;
      border-radius: 8px;
      overflow: hidden;
      background: #0f1728;
      box-shadow: 0 20px 42px rgba(15,23,40,0.18);
    }}

    .editor-box header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 8px 10px;
      color: #DDEBFF;
      border-bottom: 1px solid rgba(255,255,255,0.12);
      font-size: 12px;
      font-weight: 900;
    }}

    .editor-box pre {{
      margin: 0;
      padding: 14px;
      overflow-x: auto;
      color: #DDEBFF;
      font-family: var(--mono);
      font-size: var(--basics-code-font-size, 16px);
      line-height: 1.58;
      white-space: pre;
    }}

    .mapping-table {{
      display: grid;
      gap: 6px;
    }}

    .mapping-row {{
      display: grid;
      grid-template-columns: minmax(180px, 0.72fr) minmax(180px, 1fr);
      gap: 10px;
      align-items: start;
      padding: 8px 10px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #f8fbff;
    }}

    .mapping-row code {{
      font-family: var(--mono);
      color: #244166;
      word-break: break-word;
    }}

    .mistake-list {{
      padding: 12px 14px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      color: #334155;
    }}

    .mistake-list ul {{
      margin: 0;
      padding-left: 18px;
    }}

    .mini-example {{
      border: 1px solid var(--line);
      border-radius: 8px;
      overflow: hidden;
      background: #fff;
    }}

    .mini-example h4 {{
      margin: 0;
      padding: 9px 12px;
      border-bottom: 1px solid var(--line);
      color: var(--muted);
      font-size: 12px;
      font-weight: 900;
    }}

    .mini-example pre {{
      margin: 0;
      padding: 12px;
      overflow-x: auto;
      font-family: var(--mono);
      font-size: var(--basics-font-size);
      line-height: 1.58;
      white-space: pre;
    }}

    /* basics edition shelf redesign */
    .basics-page {{
      padding: 18px clamp(16px, 3vw, 44px) 44px;
      background: #f4f4f2;
      color: #111827;
    }}

    .basics-page::before {{
      background:
        radial-gradient(circle at 50% 18%, rgba(255,255,255,0.92), rgba(255,255,255,0.2) 34%, rgba(210,213,216,0.26) 68%, rgba(244,244,242,0.9) 100%),
        linear-gradient(180deg, rgba(255,255,255,0.96), rgba(232,232,229,0.82)),
        url("assets/basics-bg.jpg");
      background-size: cover;
      background-position: center left;
      filter: blur(14px) saturate(0.55) brightness(1.18) contrast(0.82);
      opacity: 0.22;
    }}

    .basics-topbar {{
      max-width: 1180px;
      margin-bottom: 14px;
      padding: 10px 12px;
      border-color: rgba(17,24,39,0.1);
      border-radius: 26px;
      background: rgba(242,242,240,0.78);
      backdrop-filter: blur(20px) saturate(1.05);
      box-shadow: 0 12px 38px rgba(15,23,42,0.08);
    }}

    .basics-topbar h1 {{
      font-size: 18px;
      font-weight: 900;
    }}

    .basics-nav-button,
    .basics-font button {{
      min-height: 32px;
      border-radius: 999px;
      border-color: rgba(17,24,39,0.12);
      background: rgba(255,255,255,0.82);
      box-shadow: none;
      font-size: 13px;
    }}

    .basics-nav-button:hover,
    .basics-font button:hover {{
      color: #fff;
      border-color: #111;
      background: #111;
      transform: translateY(-1px);
    }}

    .basics-layout {{
      max-width: 1180px;
      grid-template-columns: 1fr;
      gap: 14px;
    }}

    .basics-stage {{
      width: min(1180px, calc(100vw - 72px));
      margin: 0 auto;
    }}

    .basics-page[data-view="gallery"] .basics-topbar,
    .basics-page[data-view="gallery"] .basics-stage {{
      width: min(1380px, calc(100vw - 72px));
      max-width: none;
    }}

    .basics-gallery-view,
    .basics-detail-view {{
      display: grid;
      gap: 14px;
    }}

    .basics-gallery-view[hidden],
    .basics-detail-view[hidden] {{
      display: none !important;
    }}

    .basics-page[data-view="gallery"] .basics-font {{
      display: none;
    }}

    .basics-directory {{
      position: relative;
      top: auto;
      min-height: 520px;
      padding: 26px 28px 22px;
      border: 1px solid rgba(17,24,39,0.12);
      border-radius: 28px;
      background:
        radial-gradient(circle at 50% 34%, rgba(255,255,255,0.96), rgba(255,255,255,0.24) 44%, transparent 64%),
        linear-gradient(180deg, rgba(247,247,245,0.94), rgba(214,214,211,0.94));
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.92),
        0 36px 80px rgba(17,24,39,0.16);
      overflow: hidden;
    }}

    .basics-gallery-view {{
      min-height: 760px;
      padding: 32px 38px 28px;
      border: 1px solid rgba(17,24,39,0.12);
      border-radius: 34px;
      background:
        radial-gradient(circle at 46% 18%, rgba(255,255,255,0.98), rgba(255,255,255,0.5) 31%, transparent 58%),
        linear-gradient(180deg, rgba(246,246,244,0.97), rgba(223,223,219,0.96));
      box-shadow:
        inset 0 1px 0 rgba(255,255,255,0.9),
        0 38px 84px rgba(15,23,42,0.14);
      overflow: hidden;
    }}

    .basics-directory::before,
    .basics-directory::after {{
      content: "";
      position: absolute;
      left: 74px;
      right: 74px;
      height: 16px;
      border-radius: 999px;
      background: linear-gradient(180deg, #ffffff, #c9c9c5);
      box-shadow: 0 18px 34px rgba(17,24,39,0.2);
      pointer-events: none;
    }}

    .basics-directory::before {{ top: 254px; }}
    .basics-directory::after {{ top: 432px; }}

    .basics-gallery-view .editions-head {{
      position: relative;
      z-index: 2;
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 18px;
      margin-bottom: 8px;
    }}

    .basics-dir-title {{
      margin: 0 0 4px;
      color: rgba(17,24,39,0.62);
      font-size: 13px;
      font-weight: 800;
    }}

    .editions-head h2 {{
      margin: 0;
      font-size: clamp(28px, 4vw, 52px);
      line-height: 0.98;
      letter-spacing: 0;
      font-weight: 950;
    }}

    .editions-copy {{
      position: relative;
      z-index: 2;
      width: min(340px, 72%);
      margin: 0;
      color: rgba(17,24,39,0.72);
      font-size: 14px;
      line-height: 1.55;
    }}

    .basics-directory .all-editions {{
      width: auto;
      min-height: 34px;
      padding: 0 15px;
      border-radius: 999px;
      color: #111827;
      background: rgba(255,255,255,0.72);
      border-color: rgba(17,24,39,0.14);
      box-shadow: none;
    }}

    .basics-directory .all-editions.active,
    .basics-directory .all-editions:hover {{
      color: #fff;
      border-color: #111;
      background: #111;
    }}

    .album-shelf {{
      position: relative;
      z-index: 2;
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: center;
      gap: 34px 38px;
      margin: 24px auto 0;
      width: min(1240px, 100%);
    }}

    .album-card {{
      position: relative;
      flex: 0 0 280px;
      aspect-ratio: var(--cover-ratio, 4 / 3);
      min-height: 190px;
      padding: 0;
      display: block;
      border: 0;
      border-radius: 22px;
      color: #fff;
      text-align: left;
      cursor: pointer;
      overflow: hidden;
      background: rgba(15,23,42,0.14);
      box-shadow:
        0 20px 40px rgba(17,24,39,0.18),
        0 2px 0 rgba(255,255,255,0.82);
      transform-origin: bottom center;
      transition: transform 220ms ease, filter 220ms ease, opacity 220ms ease, box-shadow 220ms ease;
    }}

    .album-card:not(.active) {{
      opacity: 0.82;
      filter: saturate(0.92) contrast(0.96);
    }}

    .album-card.active {{
      flex-basis: 390px;
      min-height: 270px;
      opacity: 1;
      filter: saturate(1.04) contrast(1.02);
      box-shadow:
        0 34px 76px rgba(17,24,39,0.27),
        0 0 0 1px rgba(255,255,255,0.78);
    }}

    .part-cover-media {{
      position: absolute;
      inset: 0;
      width: 100%;
      aspect-ratio: var(--cover-ratio, 4 / 3);
      overflow: hidden;
      background:
        radial-gradient(circle at 50% 40%, rgba(255,255,255,0.1), transparent 54%),
        rgba(15,23,42,0.18);
    }}

    .part-cover-media img {{
      width: 100%;
      height: 100%;
      display: block;
      object-fit: var(--cover-fit, cover);
      object-position: var(--object-position, center);
      transform: scale(1.01);
    }}

    .album-card::before {{
      content: "";
      position: absolute;
      inset: 0;
      background:
        linear-gradient(180deg, rgba(15,23,42,0.02) 0%, rgba(15,23,42,0.28) 48%, rgba(15,23,42,0.78) 100%),
        linear-gradient(rgba(255,255,255,0.06) 50%, rgba(0,0,0,0.06) 50%);
      background-size: 100% 100%, 100% 5px;
      opacity: 0.9;
      pointer-events: none;
      z-index: 1;
    }}

    .album-card::after {{
      content: "";
      position: absolute;
      inset: 0;
      border-radius: inherit;
      border: 1px solid rgba(255,255,255,0.3);
      box-shadow: inset 0 1px 0 rgba(255,255,255,0.34);
      pointer-events: none;
      z-index: 3;
    }}

    .album-select {{
      position: absolute;
      inset: 0;
      z-index: 2;
      display: grid;
      align-content: space-between;
      width: 100%;
      padding: 18px;
      border: 0;
      color: inherit;
      background: transparent;
      cursor: pointer;
      text-align: left;
      font: inherit;
    }}

    .album-meta {{
      align-self: end;
      display: grid;
      gap: 5px;
      max-width: calc(100% - 78px);
    }}

    .album-card .album-select > * {{
      position: relative;
      z-index: 2;
    }}

    .album-card:hover,
    .album-card.active {{
      transform: translateY(-10px) scale(1.025);
    }}

    .album-index {{
      align-self: start;
      width: max-content;
      padding: 5px 9px;
      border: 1px solid rgba(255,255,255,0.24);
      border-radius: 999px;
      background: rgba(15,23,42,0.34);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      font-size: 11px;
      font-weight: 900;
      text-transform: uppercase;
      opacity: 0.92;
    }}

    .album-card strong {{
      font-size: 22px;
      line-height: 1.12;
      letter-spacing: 0;
      text-shadow: 0 1px 14px rgba(0,0,0,0.32);
    }}

    .album-card.active strong {{
      font-size: 29px;
    }}

    .album-card small {{
      color: rgba(255,255,255,0.78);
      font-size: 12px;
      font-weight: 800;
    }}

    .album-meta em {{
      color: rgba(255,255,255,0.72);
      font-size: 12px;
      line-height: 1.35;
      font-style: normal;
      font-weight: 700;
    }}

    .album-open {{
      position: absolute;
      right: 16px;
      bottom: 16px;
      padding: 8px 12px;
      border: 0;
      border-radius: 999px;
      color: #fff;
      background: rgba(17,24,39,0.78);
      font-size: 12px;
      font-weight: 900;
      opacity: 0.94;
      cursor: pointer;
      transition: transform 180ms ease, background 180ms ease, opacity 180ms ease;
      z-index: 4;
    }}

    .album-open:hover {{
      background: #111827;
      transform: translateY(-2px);
    }}

    .album-timeline {{
      position: relative;
      z-index: 2;
      display: grid;
      grid-template-columns: repeat(7, minmax(0, 1fr));
      gap: 12px;
      margin: 40px 54px 0;
      padding-top: 14px;
      border-top: 1px solid rgba(17,24,39,0.16);
    }}

    .album-timeline button {{
      display: grid;
      gap: 2px;
      color: rgba(17,24,39,0.64);
      font-size: 11px;
      padding: 0;
      border: 0;
      background: transparent;
      text-align: left;
      cursor: pointer;
    }}

    .album-timeline button.active {{
      color: #111827;
      font-weight: 900;
    }}

    .album-timeline b {{
      font-size: 11px;
      line-height: 1;
    }}

    .album-timeline small {{
      line-height: 1.15;
    }}

    .basics-reader {{
      gap: 12px;
    }}

    .training-head {{
      display: flex;
      align-items: flex-end;
      justify-content: space-between;
      gap: 18px;
      padding: 18px 20px;
      border-color: rgba(17,24,39,0.1);
      border-radius: 22px;
      background: rgba(255,255,255,0.78);
      box-shadow: 0 18px 42px rgba(17,24,39,0.08);
    }}

    .training-head h2 {{
      margin-bottom: 0;
      font-size: clamp(24px, 3vw, 38px);
      line-height: 1;
    }}

    .training-head p {{
      font-size: 12px;
      font-weight: 900;
      text-transform: uppercase;
      color: rgba(17,24,39,0.58);
    }}

    .training-head span {{
      max-width: 520px;
      color: rgba(17,24,39,0.62);
      font-size: 13px;
      line-height: 1.55;
    }}

    .back-gallery {{
      min-height: 34px;
      padding: 0 14px;
      border: 1px solid rgba(17,24,39,0.12);
      border-radius: 999px;
      color: #111827;
      background: rgba(255,255,255,0.84);
      cursor: pointer;
      font-weight: 900;
      flex: 0 0 auto;
    }}

    .back-gallery:hover {{
      color: #fff;
      border-color: #111;
      background: #111;
    }}

    .training-cards {{
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 12px;
    }}

    .training-card {{
      gap: 10px;
      padding: 14px;
      border-color: rgba(17,24,39,0.1);
      border-radius: 18px;
      background: rgba(255,255,255,0.82);
      box-shadow: 0 14px 34px rgba(17,24,39,0.07);
    }}

    .training-card h3 {{
      font-size: calc(var(--basics-font-size) + 3px);
    }}

    .code-head {{
      display: flex;
      align-items: flex-start;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 10px;
    }}

    .code-panel h4 {{
      margin: 0 0 12px;
      font-size: 18px;
      letter-spacing: 0;
    }}

    .code-zoom {{
      display: inline-flex;
      gap: 6px;
      padding: 4px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      flex: 0 0 auto;
    }}

    .code-zoom button {{
      min-width: 34px;
      min-height: 30px;
      border: 0;
      border-radius: 6px;
      color: var(--ink);
      background: transparent;
      cursor: pointer;
      font-weight: 800;
    }}

    .code-zoom button:hover {{
      color: #fff;
      background: var(--accent);
    }}

    .source-note {{
      margin: -6px 0 14px;
      color: var(--muted);
      font-size: 13px;
    }}

    .code-panel {{
      display: grid;
      align-content: start;
      gap: 12px;
      max-width: none;
      margin: 0 auto;
      width: 100%;
      min-width: 0;
    }}

    .code-card {{
      position: relative;
      border: 1px solid #222b3e;
      border-radius: 8px;
      overflow: hidden;
      background:
        linear-gradient(90deg, rgba(8, 14, 27, 0.86), rgba(8, 14, 27, 0.72)),
        url("kitten-crt-bg.jpg") center / cover no-repeat;
      backdrop-filter: blur(18px) saturate(1.18);
      user-select: none;
      margin-top: 22px;
      width: 100%;
      min-height: 640px;
      box-shadow: 0 24px 70px rgba(17, 27, 45, 0.26);
    }}

    .code-card::before {{
      content: "";
      position: absolute;
      inset: 0;
      pointer-events: none;
      background:
        linear-gradient(rgba(255,255,255,0.04) 50%, rgba(0,0,0,0.06) 50%),
        radial-gradient(circle at 18% 12%, rgba(184,243,255,0.16), transparent 28%);
      background-size: 100% 4px, 100% 100%;
      opacity: 0.55;
    }}

    .code-card header {{
      display: none;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      color: #cbd5e1;
      border-bottom: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 12px;
    }}

    .code-card + .code-card {{
      margin-top: 34px;
    }}

    .question-line {{
      padding: 10px 12px;
      color: #eef4ff;
      background: #172237;
      border-bottom: 1px solid rgba(255, 255, 255, 0.12);
      font-size: 15px;
      font-weight: 700;
      line-height: 1.55;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      -webkit-box-orient: vertical;
      overflow: hidden;
    }}

    .code-card pre {{
      margin: 0;
      padding: 28px 24px 42px;
      color: #DDEBFF;
      font-family: "JetBrains Mono", "IBM 3270", "IBM Plex Mono", Consolas, "Courier New", monospace;
      font-size: var(--code-font-size);
      line-height: 1.58;
      white-space: pre-wrap;
      word-break: break-word;
      cursor: crosshair;
      position: relative;
      z-index: 1;
      min-height: 640px;
      width: 100%;
    }}

    .tok-keyword {{ color: #7DB7FF; font-weight: 700; }}
    .tok-func {{ color: #B8F3FF; }}
    .tok-string {{ color: #B7F7C4; }}
    .tok-number {{ color: #FFD6A5; }}
    .tok-comment {{ color: #7E8CA8; font-style: italic; }}
    .tok-error {{ color: #FF6B9A; }}
    .method-label {{
      color: #B8F3FF;
      font-weight: 800;
      letter-spacing: 0;
      margin: 10px 0 4px;
      text-shadow: 0 0 14px rgba(184,243,255,0.42);
    }}

    .code-line {{
      display: block;
      min-height: 1.58em;
      border-radius: 4px;
      padding: 0 3px;
    }}

    .code-line.picked {{
      color: #ffffff;
      background: rgba(36, 107, 254, 0.38);
      box-shadow: inset 3px 0 0 #7fb0ff;
    }}

    .selection-box {{
      position: fixed;
      z-index: 30;
      display: none;
      border: 1px solid #6ea4ff;
      background: rgba(36, 107, 254, 0.14);
      pointer-events: none;
    }}

    .read-menu {{
      position: fixed;
      z-index: 40;
      display: none;
      min-width: 112px;
      padding: 6px;
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 18px 40px rgba(29, 36, 51, 0.2);
    }}

    .read-menu button {{
      width: 100%;
      min-height: 34px;
      border: 0;
      border-radius: 6px;
      color: var(--ink);
      background: transparent;
      cursor: pointer;
      text-align: left;
      font-weight: 700;
    }}

    .read-menu button:hover {{
      color: #fff;
      background: var(--accent);
    }}

    .read-panel {{
      position: absolute;
      top: 18px;
      right: 18px;
      z-index: 12;
      display: none;
      width: min(520px, calc(100% - 36px));
      border: 1px solid var(--line);
      border-radius: 8px;
      background: #fff;
      overflow: hidden;
      box-shadow: 0 26px 70px rgba(17, 27, 45, 0.24);
    }}

    .read-panel.show {{
      display: block;
    }}

    .read-panel section {{
      padding: 14px;
    }}

    .read-panel section + section {{
      border-top: 1px solid var(--line);
    }}

    .read-panel h5 {{
      margin: 0 0 8px;
      font-size: 14px;
      letter-spacing: 0;
    }}

    .read-title-row {{
      display: flex;
      align-items: center;
      gap: 8px;
      margin-bottom: 8px;
    }}

    .read-title-row h5 {{
      margin: 0;
    }}

    .important-badge {{
      display: inline-flex;
      align-items: center;
      min-height: 22px;
      padding: 2px 8px;
      border-radius: 999px;
      color: #0f3c7a;
      background: #e9f2ff;
      border: 1px solid #bad1ff;
      font-size: 12px;
      font-weight: 900;
      white-space: nowrap;
    }}

    .read-panel p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.68;
      font-size: 13px;
    }}

    .read-panel ul {{
      margin: 8px 0 0;
      padding-left: 18px;
      color: var(--muted);
      line-height: 1.6;
      font-size: 13px;
    }}

    .read-panel li + li {{
      margin-top: 5px;
    }}

    .read-panel code {{
      padding: 1px 5px;
      border-radius: 5px;
      color: #123a7a;
      background: #eaf1ff;
      font-family: Consolas, "SFMono-Regular", Menlo, monospace;
      font-size: 12px;
    }}

    .inline-teach-frame {{
      position: absolute;
      left: 12px;
      right: 12px;
      top: calc(100% - 8px);
      z-index: 9;
      display: none !important;
      grid-template-columns: 1fr 1fr;
      border: 1px solid #b9c7df;
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 22px 55px rgba(29, 36, 51, 0.24);
      pointer-events: none;
      overflow: hidden;
    }}

    .code-card:hover {{
      overflow: hidden;
    }}

    .code-card:hover .inline-teach-frame,
    .code-card.hovering .inline-teach-frame,
    .code-card:focus-within .inline-teach-frame {{
      display: none !important;
    }}

    .inline-teach-frame section {{
      padding: 14px;
    }}

    .inline-teach-frame section + section {{
      border-left: 1px solid var(--line);
      background: #fbfcff;
    }}

    .inline-teach-frame h5 {{
      margin: 0 0 8px;
      color: var(--ink);
      font-size: 14px;
      letter-spacing: 0;
    }}

    .inline-teach-frame p {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      font-family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif;
      font-size: 13px;
      white-space: normal;
    }}

    .hint-list {{
      display: grid;
      gap: 7px;
      color: var(--muted);
      font-size: 13px;
      line-height: 1.55;
    }}

    .hint-list p {{
      margin: 0;
    }}

    .hint-list code {{
      padding: 1px 5px;
      border-radius: 5px;
      color: #123a7a;
      background: #eaf1ff;
      font-family: Consolas, "SFMono-Regular", Menlo, monospace;
      font-size: 12px;
    }}

    .line-hints {{
      display: grid;
      gap: 6px;
      margin-bottom: 10px;
      padding-bottom: 10px;
      border-bottom: 1px solid var(--line);
    }}

    .line-hints p {{
      margin: 0;
      padding: 6px 8px;
      border-radius: 6px;
      color: #31405a;
      background: #f0f5ff;
      font-size: 12px;
      line-height: 1.5;
    }}

    .empty-code {{
      margin: 0;
      color: var(--muted);
      line-height: 1.7;
      font-size: 14px;
    }}

    .actions {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      padding: 0 22px 22px;
    }}

    .actions a {{
      min-height: 40px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 9px 13px;
      border: 1px solid var(--line);
      border-radius: 8px;
      color: var(--ink);
      background: #fff;
      text-decoration: none;
    }}

    .actions a.primary {{ color: #fff; border-color: var(--accent); background: var(--accent); }}

    .teach-popover {{
      position: fixed;
      z-index: 20;
      width: min(620px, calc(100vw - 28px));
      display: none;
      grid-template-columns: 1fr 1fr;
      gap: 0;
      border: 1px solid #b9c7df;
      border-radius: 8px;
      background: #fff;
      box-shadow: 0 22px 55px rgba(29, 36, 51, 0.24);
      overflow: hidden;
      pointer-events: none;
    }}

    .teach-popover.show {{ display: grid; }}
    .teach-box {{ padding: 14px; }}
    .teach-box + .teach-box {{ border-left: 1px solid var(--line); background: #fbfcff; }}
    .teach-box h5 {{ margin: 0 0 8px; font-size: 14px; letter-spacing: 0; }}
    .teach-box p {{ margin: 0; color: var(--muted); line-height: 1.7; font-size: 13px; }}

    mark {{ padding: 0 2px; border-radius: 3px; color: inherit; background: #fff0a8; }}

    .memory-entry {{
      position: fixed;
      right: 24px;
      bottom: 24px;
      z-index: 35;
      width: 96px;
      height: 96px;
      padding: 0;
      border: 1px solid rgba(255,255,255,0.55);
      border-radius: 50%;
      background: #0a1020;
      overflow: hidden;
      cursor: pointer;
      box-shadow: 0 22px 58px rgba(17, 27, 45, 0.28);
    }}

    .memory-entry img {{
      width: 100%;
      height: 100%;
      object-fit: cover;
      display: block;
    }}

    .memory-panel {{
      position: fixed;
      right: 24px;
      bottom: 132px;
      z-index: 34;
      display: none;
      width: min(430px, calc(100vw - 48px));
      border: 1px solid var(--line);
      border-radius: 8px;
      background: rgba(255,255,255,0.96);
      box-shadow: 0 26px 72px rgba(17,27,45,0.26);
      overflow: hidden;
    }}

    .memory-panel.show {{ display: block; }}
    .memory-panel header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px 14px;
      border-bottom: 1px solid var(--line);
      font-weight: 800;
    }}
    .memory-panel header button {{
      border: 0;
      background: transparent;
      cursor: pointer;
      font-weight: 900;
      color: var(--muted);
    }}
    .memory-panel textarea {{
      width: 100%;
      min-height: 180px;
      border: 0;
      outline: 0;
      resize: vertical;
      padding: 14px;
      color: var(--ink);
      font-family: var(--mono);
      font-size: 14px;
      line-height: 1.65;
      background: #fbfcff;
    }}
    .memory-panel footer {{
      display: flex;
      justify-content: space-between;
      gap: 10px;
      padding: 10px 14px 14px;
      color: var(--muted);
      font-size: 12px;
    }}

    .practice-overlay {{
      position: fixed;
      inset: 0;
      z-index: 80;
      display: none;
      padding: 28px;
      background:
        linear-gradient(90deg, rgba(4,8,18,0.92), rgba(8,15,29,0.78)),
        url("code-memory-entry.jpg") right bottom / min(42vw, 520px) auto no-repeat,
        #050915;
      color: #DDEBFF;
    }}

    .practice-overlay.show {{ display: grid; }}

    .practice-shell {{
      display: grid;
      grid-template-columns: minmax(260px, 0.62fr) minmax(420px, 1fr);
      grid-template-rows: minmax(0, 1fr) 190px;
      gap: 16px;
      width: min(1420px, 100%);
      height: min(860px, 100%);
      margin: auto;
    }}

    .practice-card {{
      border: 1px solid rgba(184, 243, 255, 0.22);
      border-radius: 8px;
      background: rgba(12, 22, 42, 0.72);
      backdrop-filter: blur(18px) saturate(1.16);
      box-shadow: 0 24px 74px rgba(0,0,0,0.34);
      overflow: hidden;
    }}

    .practice-problem {{
      padding: 18px;
      overflow: auto;
    }}

    .practice-problem h2 {{
      margin: 0 0 12px;
      font-size: 22px;
      line-height: 1.35;
      letter-spacing: 0;
    }}

    .practice-problem p {{
      margin: 0 0 12px;
      color: #9db0cc;
      line-height: 1.75;
      font-family: "Microsoft YaHei", Arial, sans-serif;
    }}

    .practice-main {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      min-width: 0;
    }}

    .practice-toolbar {{
      display: flex;
      flex-wrap: wrap;
      align-items: center;
      justify-content: space-between;
      gap: 10px;
      padding: 12px;
      border-bottom: 1px solid rgba(184, 243, 255, 0.18);
    }}

    .practice-toolbar span {{
      color: #B8F3FF;
      font-weight: 800;
    }}

    .practice-buttons {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
    }}

    .practice-buttons button,
    .memory-panel footer button {{
      min-height: 34px;
      padding: 0 12px;
      border: 1px solid rgba(184, 243, 255, 0.28);
      border-radius: 8px;
      color: #DDEBFF;
      background: rgba(125, 183, 255, 0.14);
      cursor: pointer;
      font-weight: 800;
    }}

    .practice-buttons button:disabled {{
      cursor: not-allowed;
      opacity: 0.48;
    }}

    .practice-buttons button:hover:not(:disabled) {{
      background: rgba(125, 183, 255, 0.28);
    }}

    .practice-editor {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 220px;
      gap: 12px;
      padding: 12px;
      min-height: 0;
    }}

    .practice-editor textarea,
    .practice-output pre {{
      width: 100%;
      height: 100%;
      margin: 0;
      border: 1px solid rgba(184, 243, 255, 0.18);
      border-radius: 8px;
      outline: 0;
      color: #DDEBFF;
      background: rgba(5, 10, 22, 0.78);
      font-family: "JetBrains Mono", Consolas, monospace;
      font-size: 15px;
      line-height: 1.65;
      resize: none;
    }}

    .practice-editor textarea {{ padding: 14px; }}

    .practice-input {{
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 8px;
      min-height: 0;
    }}

    .practice-input label {{
      color: #9db0cc;
      font-size: 13px;
      font-weight: 800;
    }}

    .practice-output {{
      grid-column: 1 / -1;
      display: grid;
      grid-template-rows: auto minmax(0, 1fr);
      gap: 8px;
      padding: 12px;
      min-height: 0;
    }}

    .practice-output h3 {{
      margin: 0;
      font-size: 15px;
      color: #B8F3FF;
      letter-spacing: 0;
    }}

    .practice-output pre {{
      padding: 12px;
      white-space: pre-wrap;
      overflow: auto;
    }}

    .py-status {{
      color: #FFD6A5;
      font-size: 13px;
      font-weight: 800;
    }}

    /* reward toast */
    .reward-toast {{
      position: fixed;
      top: 22px;
      right: 24px;
      z-index: 140;
      display: grid;
      gap: 8px;
      pointer-events: none;
    }}

    .reward-toast .toast {{
      min-width: 190px;
      padding: 10px 14px;
      border: 1px solid rgba(184,243,255,0.48);
      border-radius: 8px;
      color: #f8fbff;
      background: rgba(8, 16, 31, 0.84);
      box-shadow: 0 18px 42px rgba(8, 16, 31, 0.26), 0 0 28px rgba(125,183,255,0.22);
      backdrop-filter: blur(12px);
      animation: rewardPop 1.55s ease forwards;
    }}

    .reward-toast strong {{
      display: block;
      font-size: 14px;
      letter-spacing: 0;
    }}

    .reward-toast span {{
      display: block;
      margin-top: 2px;
      color: #B8F3FF;
      font-size: 12px;
      font-weight: 800;
    }}

    @keyframes rewardPop {{
      0% {{ opacity: 0; transform: translateY(-10px) scale(0.98); }}
      16% {{ opacity: 1; transform: translateY(0) scale(1); }}
      76% {{ opacity: 1; transform: translateY(0) scale(1); }}
      100% {{ opacity: 0; transform: translateY(-8px) scale(0.98); }}
    }}

    @media (max-width: 1180px) {{
      .doc-strip {{ grid-template-columns: 1fr; }}
      .page-card {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 900px) {{
      .shell {{ grid-template-columns: var(--library-width) minmax(var(--stage-width), max-content); }}
      .library-sidebar {{ width: 58px; }}
      .chapter-nav {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .read-panel.show {{ grid-template-columns: 1fr; }}
      .read-panel section + section {{ border-left: 0; border-top: 1px solid var(--line); }}
      .start-actions {{ grid-template-columns: 1fr; }}
      .basics-layout {{ grid-template-columns: 1fr; }}
      .basics-directory {{
        position: static;
        min-height: auto;
        overflow: hidden;
      }}
      .basics-directory::before,
      .basics-directory::after {{ display: none; }}
      .basics-page[data-view="gallery"] .basics-topbar,
      .basics-page[data-view="gallery"] .basics-stage {{
        width: min(100%, calc(100vw - 28px));
      }}
      .basics-gallery-view {{
        min-height: 680px;
        padding: 24px 20px;
        border-radius: 24px;
      }}
      .album-shelf {{
        gap: 24px;
      }}
      .album-card {{
        flex-basis: min(330px, 46vw);
      }}
      .album-card.active {{
        flex-basis: min(420px, 86vw);
      }}
      .album-timeline {{ grid-template-columns: repeat(2, minmax(0, 1fr)); margin-left: 0; margin-right: 0; }}
      .training-head {{ align-items: flex-start; flex-direction: column; }}
      .training-cards {{ grid-template-columns: 1fr; }}
      .basics-dir-title {{ display: none; }}
      .basics-topbar {{ grid-template-columns: 1fr 1fr auto; }}
      .basics-topbar h1 {{ grid-column: 1 / -1; grid-row: 1; }}
      .mapping-row {{ grid-template-columns: 1fr; }}
    }}

    @media (max-width: 640px) {{
      .library-sidebar {{ padding: 22px 14px; }}
      .doc-strip, .chapter-nav, .stat-grid {{ grid-template-columns: 1fr; }}
      .headline h2 {{ font-size: 30px; }}
      .detail-head h3 {{ font-size: 22px; }}
      .basics-page {{ padding: 12px; }}
      .basics-topbar {{ grid-template-columns: 1fr; border-radius: 18px; }}
      .basics-font {{ justify-content: flex-start; }}
      .basics-directory {{ padding: 18px; border-radius: 20px; }}
      .editions-head {{ flex-direction: column; }}
      .editions-copy {{ width: 100%; }}
      .album-shelf {{ gap: 18px; }}
      .album-card,
      .album-card.active {{
        flex-basis: min(100%, 360px);
        min-height: 220px;
      }}
      .album-timeline {{ display: none; }}
      .sections, .page-toolbar {{ padding-left: 14px; padding-right: 14px; }}
      .inline-teach-frame {{
        position: static;
        margin: 0 10px 10px;
        grid-template-columns: 1fr;
      }}
      .inline-teach-frame section + section {{ border-left: 0; border-top: 1px solid var(--line); }}
      .teach-popover {{ grid-template-columns: 1fr; }}
      .teach-box + .teach-box {{ border-left: 0; border-top: 1px solid var(--line); }}
      .desktop-pet {{
        width: 96px;
        height: 96px;
        left: calc(100vw - 118px);
        top: calc(100vh - 128px);
      }}
      .desktop-pet-img {{
        width: 92px;
        height: 92px;
      }}
      .desktop-pet-bubble {{
        right: -4px;
        max-width: min(280px, calc(100vw - 28px));
        padding: 12px 14px;
        font-size: 13px;
      }}
      .edition-signature-card {{
        right: 12px;
        width: 78px;
      }}
      .edition-signature-card.is-raised {{
        transform: translateY(-84%);
      }}
    }}
  </style>
</head>
<body>
  <section class="start-gate" id="startGate" aria-label="Python 开始学吧启动页">
    <div class="start-actions">
      <div class="start-card">
        <p class="start-kicker">PYTHON FINAL DUNGEON</p>
        <h1>Python 开始学吧</h1>
        <p>从零基础开始，刷题、读代码、通关 Python。</p>
        <button class="start-button" id="startButton" type="button">Python 开始学吧</button>
        <p>点击开始闯关</p>
      </div>
      <div class="landing-visual" aria-label="Python 新手训练营视觉入口">
        <section class="basics-entry-card" id="basicsEntry" tabindex="0" aria-label="Python 新手训练营入口">
          <h2>Python 新手训练营</h2>
          <p>先学会看懂，再开始刷题</p>
          <button id="enterBasicsBtn" type="button">进入训练营</button>
        </section>
      </div>
    </div>
  </section>

  <div class="left-bg-zone" aria-hidden="true"></div>

  <div class="shell">
    <aside class="library-sidebar">
      <div class="side-content">
        <div class="brand">
          <h1>Python 开始学吧</h1>
          <p>从零基础开始，刷题、读代码、通关 Python。</p>
          <button class="return-start" id="returnStart" type="button">返回开始页</button>
        </div>
        <label class="search" for="searchInput">
          <span>⌕</span>
          <input id="searchInput" type="search" placeholder="搜索章节、题型、代码">
        </label>
        <div class="stat-grid">
          <div class="stat"><strong id="progressPercent">0%</strong><span>当前进度</span></div>
          <div class="stat"><strong id="unlockedCount">0</strong><span>已解锁关卡</span></div>
          <div class="stat"><strong id="todayCount">0</strong><span>今日刷题数</span></div>
          <div class="stat"><strong id="xpLevel">Lv.1</strong><span>经验等级</span></div>
        </div>
        <div class="xp-shell" aria-label="经验值进度"><div class="xp-bar" id="xpBar"></div></div>
        <p class="nav-title">章节巡检</p>
        <nav class="chapter-nav" id="chapterNav"></nav>
        <section class="doc-strip" id="docStrip"></section>
        <section class="side-meta" id="sideMeta"></section>
        <section class="question-list" id="questionList"></section>
      </div>
    </aside>

    <main>
      <article class="detail" id="detail"></article>
    </main>
  </div>

  <button class="return-start-fixed" id="returnStartFixed" type="button">返回开始页</button>

  <section class="basics-page" id="basicsPage" aria-label="Python 新手训练营">
    <header class="basics-topbar">
      <button class="basics-nav-button" type="button" id="basicsHome">返回首页</button>
      <button class="basics-nav-button" type="button" id="basicsLibrary">返回题库</button>
      <h1>Python 新手训练营</h1>
      <div class="basics-font" aria-label="基础内容字号调节">
        <button type="button" data-basics-font="-1">A-</button>
        <button type="button" data-basics-font="1">A+</button>
      </div>
    </header>
    <div class="basics-stage">
      <section class="basics-gallery-view" id="basicsGalleryView" aria-label="训练营 Part 专辑入口"></section>
      <section class="basics-detail-view" id="basicsDetailView" aria-label="训练营知识卡片" hidden></section>
    </div>
  </section>

  <div class="teach-popover" id="teachPopover">
    <section class="teach-box">
      <h5>简单基础语法</h5>
      <p id="syntaxText"></p>
    </section>
    <section class="teach-box">
      <h5>算法是什么</h5>
      <p id="algorithmText"></p>
    </section>
  </div>

  <div class="selection-box" id="selectionBox"></div>
  <div class="read-menu" id="readMenu">
    <button type="button" id="readSelection">读取</button>
  </div>

  <div class="reward-toast" id="rewardToast" aria-live="polite"></div>

  <div class="edition-signature-card" id="editionSignatureCard" aria-hidden="true">
    <img src="./assets/edition-signature-card.png" alt="">
  </div>

  <div id="desktopPet" class="desktop-pet" aria-label="desktop pet">
    <img id="desktopPetImg" class="desktop-pet-img" src="./assets/pet-idle.png" alt="desktop pet" draggable="false">
    <div id="desktopPetBubble" class="desktop-pet-bubble" hidden></div>
  </div>

  <button class="memory-entry" id="memoryEntry" type="button" title="代码自默区域">
    <img src="code-memory-entry.jpg" alt="代码自默入口">
  </button>
  <section class="memory-panel" id="memoryPanel">
    <header>
      <span>代码自默区域</span>
      <button type="button" id="memoryClose" title="关闭">×</button>
    </header>
    <textarea id="memoryText" spellcheck="false" placeholder="在这里默写当前题目的代码；可以先看题目，再把答案遮住自己写一遍。"></textarea>
    <footer>
      <button type="button" id="memoryPrompt">插入当前题目</button>
      <span>独立练习，不影响原页面布局</span>
    </footer>
  </section>

  <section class="practice-overlay" id="practiceOverlay" aria-label="自我检测练习区">
    <div class="practice-shell">
      <aside class="practice-card practice-problem">
        <h2 id="practiceTitle">自我检测 / 试试手</h2>
        <p id="practiceDesc">选择一道题后，在右侧默写 Python 代码。需要输入的题，把输入数据逐行写在输入框里。</p>
        <p id="practiceSource"></p>
      </aside>
      <section class="practice-card practice-main">
        <div class="practice-toolbar">
          <span id="pyStatus">Python 环境加载中...</span>
          <div class="practice-buttons">
            <button type="button" id="runPractice" disabled>运行代码</button>
            <button type="button" id="resetPractice">重置代码</button>
            <button type="button" id="nextPractice">下一题</button>
            <button type="button" id="closePractice">返回学习页</button>
          </div>
        </div>
        <div class="practice-editor">
          <textarea id="practiceCode" spellcheck="false"></textarea>
          <div class="practice-input">
            <label for="practiceInput">输入数据（每行一次 input）</label>
            <textarea id="practiceInput" spellcheck="false" placeholder="例如：&#10;3&#10;4&#10;5"></textarea>
          </div>
        </div>
      </section>
      <section class="practice-card practice-output">
        <h3>运行结果输出区</h3>
        <pre id="practiceOutput">等待运行...</pre>
      </section>
    </div>
  </section>

  <script src="./pyodide/pyodide.js"></script>
  <script id="codeExplanationsJson" type="application/json">{code_explanations_json_tag}</script>
  <script>
    const docs = {data_json};
    const basicsData = {basics_json};
    const codeExplanationsData = JSON.parse(document.querySelector("#codeExplanationsJson")?.textContent || "{{\\"questions\\":[]}}");
    const basicsCards = Array.isArray(basicsData.sections) ? basicsData.sections : [];
    const defaultBasicsFieldLabels = {{
      quickTake: "一句话先懂",
      plainExplainLong: "展开讲讲",
      stepByStep: "一步一步看",
      corePattern: "核心写法",
      plainAnalogy: "通俗理解",
      readerCode: "代码怎么读",
      commonMistakes: "常见翻车点",
      memoryHook: "记忆钩子",
      teacherTalk: "提醒",
      miniTask: "顺手练一下"
    }};
    const basicsFieldLabels = {{ ...defaultBasicsFieldLabels, ...(basicsData.fieldLabels || {{}}) }};
    const defaultBasicsRenderOrder = [
      "quickTake",
      "plainExplainLong",
      "stepByStep",
      "corePattern",
      "plainAnalogy",
      "readerCode",
      "commonMistakes",
      "memoryHook",
      "teacherTalk",
      "miniTask"
    ];
    const codeExplanationQuestions = Array.isArray(codeExplanationsData.questions) ? codeExplanationsData.questions : [];
    const codeExplanationByQuestion = new Map(codeExplanationQuestions.map((item) => [String(item.questionId || ""), item]));
    const state = {{ selected: docs[0].id, filter: "all", keyword: "", activePage: 1, basicsGroup: "基础语法" }};
    const startGate = document.querySelector("#startGate");
    const startButton = document.querySelector("#startButton");
    const basicsEntry = document.querySelector("#basicsEntry");
    const basicsPage = document.querySelector("#basicsPage");
    const basicsHome = document.querySelector("#basicsHome");
    const basicsLibrary = document.querySelector("#basicsLibrary");
    const basicsGalleryView = document.querySelector("#basicsGalleryView");
    const basicsDetailView = document.querySelector("#basicsDetailView");
    const returnStart = document.querySelector("#returnStart");
    const returnStartFixed = document.querySelector("#returnStartFixed");
    const rewardToast = document.querySelector("#rewardToast");
    const progressPercent = document.querySelector("#progressPercent");
    const unlockedCount = document.querySelector("#unlockedCount");
    const todayCount = document.querySelector("#todayCount");
    const xpLevel = document.querySelector("#xpLevel");
    const xpBar = document.querySelector("#xpBar");
    const desktopPet = document.querySelector("#desktopPet");
    const desktopPetImg = document.querySelector("#desktopPetImg");
    const desktopPetBubble = document.querySelector("#desktopPetBubble");
    const editionSignatureCard = document.querySelector("#editionSignatureCard");
    const chapterNav = document.querySelector("#chapterNav");
    const docStrip = document.querySelector("#docStrip");
    const sideMeta = document.querySelector("#sideMeta");
    const questionList = document.querySelector("#questionList");
    const detail = document.querySelector("#detail");
    const searchInput = document.querySelector("#searchInput");
    const popover = document.querySelector("#teachPopover");
    const syntaxText = document.querySelector("#syntaxText");
    const algorithmText = document.querySelector("#algorithmText");
    const selectionBox = document.querySelector("#selectionBox");
    const readMenu = document.querySelector("#readMenu");
    const readSelection = document.querySelector("#readSelection");
    const memoryEntry = document.querySelector("#memoryEntry");
    const memoryPanel = document.querySelector("#memoryPanel");
    const memoryClose = document.querySelector("#memoryClose");
    const memoryText = document.querySelector("#memoryText");
    const memoryPrompt = document.querySelector("#memoryPrompt");
    const practiceOverlay = document.querySelector("#practiceOverlay");
    const practiceTitle = document.querySelector("#practiceTitle");
    const practiceDesc = document.querySelector("#practiceDesc");
    const practiceSource = document.querySelector("#practiceSource");
    const pyStatus = document.querySelector("#pyStatus");
    const runPractice = document.querySelector("#runPractice");
    const resetPractice = document.querySelector("#resetPractice");
    const nextPractice = document.querySelector("#nextPractice");
    const closePractice = document.querySelector("#closePractice");
    const practiceCode = document.querySelector("#practiceCode");
    const practiceInput = document.querySelector("#practiceInput");
    const practiceOutput = document.querySelector("#practiceOutput");
    const selectionState = {{
      dragging: false,
      startX: 0,
      startY: 0,
      activePre: null,
      selectedCode: "",
      selectedPanel: null
    }};
    const sidebar = document.querySelector(".library-sidebar");
    let savedCodeFontSize = 16;
    try {{ savedCodeFontSize = Number(localStorage.getItem("pythonReviewCodeFontSize") || 16); }} catch (error) {{}}
    let codeFontSize = savedCodeFontSize;
    codeFontSize = Math.min(28, Math.max(12, codeFontSize));
    document.documentElement.style.setProperty("--code-font-size", `${{codeFontSize}}px`);
    let savedBasicsFontSize = 15;
    try {{ savedBasicsFontSize = Number(localStorage.getItem("basicsFontSize") || 15); }} catch (error) {{}}
    let basicsFontSize = Math.min(22, Math.max(13, savedBasicsFontSize));
    document.documentElement.style.setProperty("--basics-font-size", `${{basicsFontSize}}px`);
    let savedBasicsCodeFontSize = 16;
    try {{ savedBasicsCodeFontSize = Number(localStorage.getItem("basicsCodeFontSize") || 16); }} catch (error) {{}}
    let basicsCodeFontSize = Math.min(28, Math.max(12, savedBasicsCodeFontSize));
    document.documentElement.style.setProperty("--basics-code-font-size", `${{basicsCodeFontSize}}px`);
    let pyodideReady = false;
    let pyodideRuntime = null;
    let pyodideLoading = null;

    const chapters = [
      {{ id: "all", label: "全部资料", count: "4 份" }},
      {{ id: "week9", label: "第 1-3 部分", count: "基础" }},
      {{ id: "week10", label: "第 4-5 部分", count: "for" }},
      {{ id: "week11", label: "第 6-7 部分", count: "while" }},
      {{ id: "week12", label: "第 8-9 部分", count: "数据" }}
    ];

    const basicsParts = [
      {{ id: "syntax", part: "Part 01", group: "基础语法", title: "基础语法", subtitle: "Syntax Basics", en: "Syntax Basics", desc: "先理解代码从哪里开始，往哪里执行。", cover: "./assets/part-01.jpg", aspectRatio: "4 / 3", coverFit: "contain", objectPosition: "center" }},
      {{ id: "io", part: "Part 02", group: "输入输出", title: "输入输出", subtitle: "Input & Output", en: "Input & Output", desc: "把键盘输入接住，再把结果清楚交出来。", cover: "./assets/part-02.jpg", aspectRatio: "16 / 10", coverFit: "cover", objectPosition: "center" }},
      {{ id: "condition", part: "Part 03", group: "条件语句", title: "条件语句", subtitle: "Condition Control", en: "Condition Control", desc: "用 if / elif / else 让程序学会分路。", cover: "./assets/part-03.jpg", aspectRatio: "4 / 3", coverFit: "cover", objectPosition: "center top" }},
      {{ id: "loop", part: "Part 04", group: "循环语句", title: "循环语句", subtitle: "Loop Control", en: "Loop Control", desc: "让重复任务自动跑起来，不再手写十遍。", cover: "./assets/part-04.jpg", aspectRatio: "4 / 3", coverFit: "contain", objectPosition: "center" }},
      {{ id: "control", part: "Part 05", group: "循环控制", title: "循环控制", subtitle: "Break & Continue", en: "Break & Continue", desc: "知道什么时候继续，什么时候收手。", cover: "./assets/part-05.jpg", aspectRatio: "4 / 3", coverFit: "cover", objectPosition: "center" }},
      {{ id: "template", part: "Part 06", group: "综合模板", title: "综合模板", subtitle: "Problem Templates", en: "Problem Templates", desc: "把常见期末题拆成可复用套路。", cover: "./assets/part-06.jpg", aspectRatio: "4 / 3", coverFit: "contain", objectPosition: "center" }},
      {{ id: "data", part: "Part 07", group: "基础数据", title: "基础数据", subtitle: "Basic Data", en: "Basic Data", desc: "看懂字符串、列表、字典这些常用容器。", cover: "./assets/part-07.jpg", aspectRatio: "4 / 3", coverFit: "cover", objectPosition: "center" }}
    ];

    /* progress state */
    const progressKey = "pythonReviewProgressV1";
    const todayStamp = new Date().toISOString().slice(0, 10);

    function loadProgress() {{
      try {{
        const saved = JSON.parse(localStorage.getItem(progressKey) || "{{}}");
        return {{
          visited: Array.isArray(saved.visited) ? saved.visited : [],
          today: saved.todayDate === todayStamp && Array.isArray(saved.today) ? saved.today : [],
          todayDate: todayStamp,
          xp: Number(saved.xp || 0),
          section: saved.section || state.selected
        }};
      }} catch (error) {{
        return {{ visited: [], today: [], todayDate: todayStamp, xp: 0, section: state.selected }};
      }}
    }}

    let progressState = loadProgress();

    function saveProgress() {{
      try {{ localStorage.setItem(progressKey, JSON.stringify(progressState)); }} catch (error) {{}}
    }}

    function totalQuestionCount() {{
      return docs.reduce((sum, doc) => sum + doc.questions.length, 0);
    }}

    function activeQuestion() {{
      const doc = selectedDoc();
      return doc.questions.find((question) => question.number === state.activePage) || doc.questions[0];
    }}

    function activeQuestionKey() {{
      const doc = selectedDoc();
      const question = activeQuestion();
      return `${{doc.id}}:Q${{String(question.number).padStart(2, "0")}}`;
    }}

    function updateProgressUI() {{
      const total = Math.max(1, totalQuestionCount());
      const unlocked = progressState.visited.length;
      const percent = Math.min(100, Math.round((unlocked / total) * 100));
      const level = Math.max(1, Math.floor(progressState.xp / 100) + 1);
      if (progressPercent) progressPercent.textContent = `${{percent}}%`;
      if (unlockedCount) unlockedCount.textContent = unlocked;
      if (todayCount) todayCount.textContent = progressState.today.length;
      if (xpLevel) xpLevel.textContent = `Lv.${{level}}`;
      if (xpBar) xpBar.style.width = `${{progressState.xp % 100}}%`;
    }}

    function showReward(title, subtitle = "经验 +10") {{
      if (!rewardToast) return;
      const toast = document.createElement("div");
      toast.className = "toast";
      toast.innerHTML = `<strong>${{escapeHtml(title)}}</strong><span>${{escapeHtml(subtitle)}}</span>`;
      rewardToast.appendChild(toast);
      window.setTimeout(() => toast.remove(), 1700);
    }}

    /* desktop pet */
    const petPositionKey = "pythonDesktopPetPosition";
    const petRandomMessageMaxDelay = 90000;
    const petRandomMessageMinDelay = 10000;
    // 桌宠随机鼓励台词：这里改文字即可，90 秒内随机抽一句弹出。
    const encouragementMessages = [
      "学 Python 就像吃火锅，越煮越香，wyx 你再涮两下就熟了！",
      "加油！",
      "再试试呗~",
      "别急，代码也是一行一行通关的。",
      "休息一下眼睛也行，但别忘了回来打怪。",
      "放宽心！",
      "包没问题的！",
      "再咬咬牙吧！",
      "累了就去看花！"
    ];
    let petIdleTimer = null;
    let petMessageTimer = null;
    let petActionTimer = null;
    let petDragState = null;

    function clampPetPosition(x, y) {{
      if (!desktopPet) return {{ x: 0, y: 0 }};
      const rect = desktopPet.getBoundingClientRect();
      const width = rect.width || 124;
      const height = rect.height || 124;
      const margin = 10;
      return {{
        x: Math.min(Math.max(margin, x), Math.max(margin, window.innerWidth - width - margin)),
        y: Math.min(Math.max(margin, y), Math.max(margin, window.innerHeight - height - margin))
      }};
    }}

    function rectsOverlap(a, b) {{
      return a.left < b.right && a.right > b.left && a.top < b.bottom && a.bottom > b.top;
    }}

    function updateSignatureCardPosition() {{
      if (!editionSignatureCard || !desktopPet) return;
      editionSignatureCard.classList.remove("is-raised");
      const petRect = desktopPet.getBoundingClientRect();
      const cardRect = editionSignatureCard.getBoundingClientRect();
      if (!rectsOverlap(cardRect, petRect)) return;
      editionSignatureCard.classList.add("is-raised");
    }}

    function setPetPosition(x, y) {{
      if (!desktopPet) return;
      const next = clampPetPosition(x, y);
      desktopPet.style.left = `${{next.x}}px`;
      desktopPet.style.top = `${{next.y}}px`;
      updateSignatureCardPosition();
    }}

    function savePetPosition() {{
      if (!desktopPet) return;
      const rect = desktopPet.getBoundingClientRect();
      try {{
        localStorage.setItem(petPositionKey, JSON.stringify({{ x: Math.round(rect.left), y: Math.round(rect.top) }}));
      }} catch (error) {{}}
    }}

    function loadPetPosition() {{
      if (!desktopPet) return;
      try {{
        const saved = JSON.parse(localStorage.getItem(petPositionKey) || "null");
        if (saved && Number.isFinite(saved.x) && Number.isFinite(saved.y)) {{
          setPetPosition(saved.x, saved.y);
          return;
        }}
      }} catch (error) {{}}
      setPetPosition(window.innerWidth - 156, window.innerHeight - 168);
    }}

    function hidePetMessage() {{
      if (!desktopPetBubble) return;
      desktopPetBubble.classList.remove("show");
      window.clearTimeout(petMessageTimer);
      petMessageTimer = window.setTimeout(() => {{
        desktopPetBubble.hidden = true;
      }}, 180);
    }}

    function showPetMessage(text) {{
      if (!desktopPetBubble) return;
      window.clearTimeout(petMessageTimer);
      desktopPetBubble.textContent = text;
      desktopPetBubble.hidden = false;
      requestAnimationFrame(() => desktopPetBubble.classList.add("show"));
      petMessageTimer = window.setTimeout(hidePetMessage, 7000);
    }}

    function randomPetMessageDelay() {{
      return petRandomMessageMinDelay + Math.floor(Math.random() * (petRandomMessageMaxDelay - petRandomMessageMinDelay + 1));
    }}

    function startPetIdleTimer() {{
      window.clearTimeout(petIdleTimer);
      petIdleTimer = window.setTimeout(() => {{
        if (!petDragState) {{
          const text = encouragementMessages[Math.floor(Math.random() * encouragementMessages.length)];
          showPetMessage(text);
        }}
        startPetIdleTimer();
      }}, randomPetMessageDelay());
    }}

    function resetPetIdleTimer() {{
      if (desktopPetImg && !petDragState) desktopPetImg.src = "./assets/pet-idle.png";
      hidePetMessage();
    }}

    function playPetAction(action) {{
      if (!desktopPet || petDragState) return;
      window.clearTimeout(petActionTimer);
      desktopPet.classList.remove("pet-action-sleep", "pet-action-jump", "pet-action-spin");
      void desktopPet.offsetWidth;
      // 桌宠双击动作台词：sleep / spin / jump 分别对应睡觉、转圈、蹦跳。
      if (action === "sleep") {{
        desktopPet.classList.add("pet-action-sleep");
        if (desktopPetImg) desktopPetImg.src = "./assets/pet-sleep.png";
        showPetMessage("呼...再学一小会儿就休息。");
      }} else if (action === "spin") {{
        desktopPet.classList.add("pet-action-spin");
        if (desktopPetImg) desktopPetImg.src = "./assets/pet-walk.png";
        showPetMessage("转一圈，思路也转通一点！");
      }} else {{
        desktopPet.classList.add("pet-action-jump");
        if (desktopPetImg) desktopPetImg.src = "./assets/pet-walk.png";
        showPetMessage("好耶，继续冲！王一西加油哇！");
      }}
      petActionTimer = window.setTimeout(() => {{
        desktopPet.classList.remove("pet-action-sleep", "pet-action-jump", "pet-action-spin");
        if (desktopPetImg && !petDragState) desktopPetImg.src = "./assets/pet-idle.png";
      }}, action === "sleep" ? 1350 : 900);
    }}

    function playRandomPetAction() {{
      const actions = ["sleep", "jump", "spin"];
      playPetAction(actions[Math.floor(Math.random() * actions.length)]);
    }}

    function nudgePet() {{
      if (!desktopPet || petDragState || !desktopPetBubble.hidden) return;
      const rect = desktopPet.getBoundingClientRect();
      const dx = Math.round((Math.random() - 0.5) * 28);
      const dy = Math.round((Math.random() - 0.5) * 18);
      if (desktopPetImg) desktopPetImg.src = "./assets/pet-walk.png";
      setPetPosition(rect.left + dx, rect.top + dy);
      window.setTimeout(() => {{
        if (desktopPetImg && !petDragState) desktopPetImg.src = "./assets/pet-idle.png";
        savePetPosition();
      }}, 900);
    }}

    function makePetDraggable() {{
      if (!desktopPet) return;
      desktopPet.addEventListener("dragstart", (event) => event.preventDefault());
      const startDrag = (clientX, clientY, pointerId = null) => {{
        const rect = desktopPet.getBoundingClientRect();
        petDragState = {{
          pointerId,
          offsetX: clientX - rect.left,
          offsetY: clientY - rect.top
        }};
        desktopPet.classList.add("dragging");
        if (desktopPetImg) desktopPetImg.src = "./assets/pet-walk.png";
      }};
      const moveDrag = (clientX, clientY) => {{
        if (!petDragState) return;
        setPetPosition(clientX - petDragState.offsetX, clientY - petDragState.offsetY);
      }};
      const stopDrag = () => {{
        if (!petDragState) return;
        petDragState = null;
        desktopPet.classList.remove("dragging");
        if (desktopPetImg) desktopPetImg.src = "./assets/pet-idle.png";
        savePetPosition();
      }};
      desktopPet.addEventListener("pointerdown", (event) => {{
        if (event.button !== 0) return;
        event.preventDefault();
        hidePetMessage();
        startDrag(event.clientX, event.clientY, event.pointerId);
        desktopPet.setPointerCapture(event.pointerId);
      }});
      desktopPet.addEventListener("pointermove", (event) => {{
        if (!petDragState || petDragState.pointerId !== event.pointerId) return;
        moveDrag(event.clientX, event.clientY);
      }});
      const stopPointerDrag = (event) => {{
        if (!petDragState || petDragState.pointerId !== event.pointerId) return;
        stopDrag();
      }};
      desktopPet.addEventListener("pointerup", stopPointerDrag);
      desktopPet.addEventListener("pointercancel", stopPointerDrag);
      desktopPet.addEventListener("dblclick", (event) => {{
        event.preventDefault();
        playRandomPetAction();
      }});
      desktopPet.addEventListener("mousedown", (event) => {{
        if (event.button !== 0 || petDragState) return;
        event.preventDefault();
        hidePetMessage();
        startDrag(event.clientX, event.clientY, "mouse");
      }});
      document.addEventListener("mousemove", (event) => {{
        if (!petDragState || petDragState.pointerId !== "mouse") return;
        moveDrag(event.clientX, event.clientY);
      }});
      document.addEventListener("mouseup", () => {{
        if (!petDragState || petDragState.pointerId !== "mouse") return;
        stopDrag();
      }});
    }}

    function initDesktopPet() {{
      if (!desktopPet || !desktopPetImg || !desktopPetBubble) return;
      loadPetPosition();
      makePetDraggable();
      ["keydown", "scroll"].forEach((eventName) => {{
        document.addEventListener(eventName, () => {{
          hidePetMessage();
        }}, {{ passive: true }});
      }});
      window.addEventListener("resize", () => {{
        const rect = desktopPet.getBoundingClientRect();
        setPetPosition(rect.left, rect.top);
        savePetPosition();
        updateSignatureCardPosition();
      }});
      window.setInterval(nudgePet, 12000);
      startPetIdleTimer();
      updateSignatureCardPosition();
    }}

    function unlockActiveQuestion(message = "") {{
      const question = activeQuestion();
      const key = activeQuestionKey();
      const label = `Q${{String(question.number).padStart(2, "0")}}`;
      let subtitle = "经验 +2";
      if (!progressState.visited.includes(key)) {{
        progressState.visited.push(key);
        progressState.xp += 10;
        subtitle = "经验 +10";
      }} else {{
        progressState.xp += 2;
      }}
      if (!progressState.today.includes(key)) progressState.today.push(key);
      progressState.section = selectedDoc().id;
      saveProgress();
      updateProgressUI();
      showReward(message || `${{label}} 已解锁`, subtitle);
    }}

    function enterApp(withReward = false) {{
      document.body.classList.remove("app-basics");
      document.body.classList.add("app-started");
      if (withReward) {{
        showReward("代码关卡启动", "经验 +10");
        unlockActiveQuestion();
      }}
    }}

    function showQuestionBankPage() {{
      enterApp(true);
    }}

    function openBasicsPage(group = "基础语法") {{
      state.basicsGroup = group;
      document.body.classList.add("app-basics");
      document.body.classList.remove("app-started");
      showBasicsGallery();
      showReward("Python 新手训练营", "基础关卡启动");
    }}

    function showBasicsPage() {{
      openBasicsPage("基础语法");
    }}

    function openLibrary() {{
      enterApp(false);
      render();
      showReward("返回题库大厅", "继续刷题");
    }}

    function showLandingPage() {{
      document.body.classList.remove("app-basics");
      document.body.classList.remove("app-started");
    }}

    function returnToStart() {{
      showLandingPage();
    }}

    function escapeHtml(value) {{
      return String(value).replace(/[&<>"']/g, (char) => ({{ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#039;" }}[char]));
    }}

    function includesKeyword(doc, keyword) {{
      if (!keyword) return true;
      const haystack = [
        doc.title, doc.range, doc.focus, doc.summary, doc.file,
        ...doc.sections.map((item) => `${{item.name}} ${{item.desc}}`),
        ...doc.topics,
        ...doc.pages.flatMap((page) => [
          page.title,
          ...page.paragraphs,
          ...page.codeBlocks.flatMap((item) => typeof item === "string" ? [item] : [item.question, item.code])
        ]),
        ...doc.questions.flatMap((question) => [question.title, ...question.codeBlocks])
      ].join(" ").toLowerCase();
      return haystack.includes(keyword.toLowerCase());
    }}

    function highlight(text) {{
      const safe = escapeHtml(text);
      const keyword = state.keyword.trim();
      if (!keyword) return safe;
      const escaped = keyword.replace(/[.*+?^${{}}()|[\\]\\\\]/g, "\\\\$&");
      return safe.replace(new RegExp(escaped, "gi"), (match) => `<mark>${{match}}</mark>`);
    }}

    function highlightCodeLine(line) {{
      if (/^方法[一二三四五六七八九十]+：?$/.test(line.trim())) {{
        return `<span class="method-label">${{escapeHtml(line.trim())}}</span>`;
      }}
      let safe = escapeHtml(line || " ");
      safe = safe.replace(/(#.*)$/g, '<span class="tok-comment">$1</span>');
      safe = safe.replace(/(&quot;.*?&quot;|&#039;.*?&#039;)/g, '<span class="tok-string">$1</span>');
      safe = safe.replace(/\\b(\\d+(?:\\.\\d+)?)\\b/g, '<span class="tok-number">$1</span>');
      safe = safe.replace(/\\b(import|from|if|elif|else|for|while|break|continue|return|in|and|or|not|True|False|None|del)\\b/g, '<span class="tok-keyword">$1</span>');
      safe = safe.replace(/\\b([A-Za-z_]\\w*)(?=\\()/g, '<span class="tok-func">$1</span>');
      safe = safe.replace(/\\b(error|Error|except)\\b/g, '<span class="tok-error">$1</span>');
      return safe;
    }}

    function visibleDocs() {{
      return docs.filter((doc) => (state.filter === "all" || doc.id === state.filter) && includesKeyword(doc, state.keyword.trim()));
    }}

    function selectedDoc() {{
      return docs.find((doc) => doc.id === state.selected) || docs[0];
    }}

    function setCodeFontSize(nextSize) {{
      codeFontSize = Math.min(28, Math.max(12, nextSize));
      document.documentElement.style.setProperty("--code-font-size", `${{codeFontSize}}px`);
      try {{ localStorage.setItem("pythonReviewCodeFontSize", String(codeFontSize)); }} catch (error) {{}}
    }}

    function setBasicsFontSize(nextSize) {{
      basicsFontSize = Math.min(22, Math.max(13, nextSize));
      document.documentElement.style.setProperty("--basics-font-size", `${{basicsFontSize}}px`);
      try {{ localStorage.setItem("basicsFontSize", String(basicsFontSize)); }} catch (error) {{}}
    }}

    function setBasicsCodeFontSize(nextSize) {{
      basicsCodeFontSize = Math.min(28, Math.max(12, nextSize));
      document.documentElement.style.setProperty("--basics-code-font-size", `${{basicsCodeFontSize}}px`);
      try {{ localStorage.setItem("basicsCodeFontSize", String(basicsCodeFontSize)); }} catch (error) {{}}
    }}

    function renderNav() {{
      chapterNav.innerHTML = chapters.map((chapter) => `
        <button type="button" class="${{state.filter === chapter.id ? "active" : ""}}" data-filter="${{chapter.id}}">
          <span>${{chapter.label}}</span>
          <small>${{chapter.count}}</small>
        </button>
      `).join("");
    }}

    function renderDocStrip() {{
      const list = visibleDocs();
      if (!list.some((doc) => doc.id === state.selected) && list[0]) state.selected = list[0].id;
      docStrip.innerHTML = list.map((doc) => `
        <section class="doc-card ${{doc.id === state.selected ? "active" : ""}}" data-id="${{doc.id}}" tabindex="0">
          <header>
            <h3>${{highlight(doc.range)}}</h3>
            <span class="badge">${{doc.questionCount}} 题</span>
          </header>
          <p>${{highlight(doc.summary)}}</p>
          <div class="tags">
            <span>${{highlight(doc.focus)}}</span>
          </div>
        </section>
      `).join("") || `<section class="doc-card"><h3>没有匹配的资料</h3><p>换一个关键词试试看。</p></section>`;
    }}

    function renderSideMeta() {{
      sideMeta.innerHTML = "";
    }}

    function renderQuestionList() {{
      const doc = selectedDoc();
      questionList.innerHTML = `
        <h4>题目巡检</h4>
        ${{doc.questions.map((question) => `
          <button type="button" class="${{question.number === state.activePage ? "active" : ""}}" data-side-question="${{question.number}}">
            Q${{String(question.number).padStart(2, "0")}} · ${{highlight(question.title)}}
          </button>
        `).join("")}}
      `;
    }}

    function sourceNotesText() {{
      const notes = basicsData.sourceNotes;
      if (Array.isArray(notes)) return notes.join("、");
      return notes || "Python3基础语法、条件控制、循环语句";
    }}

    function cardSearchText(card) {{
      return [
        card.group,
        card.title,
        card.goal,
        card.summary,
        ...(card.points || [])
      ].filter(Boolean).join(" ");
    }}

    function cardsForGroup(group) {{
      if (group === "全部") return basicsCards;
      if (group === "输入输出") {{
        return basicsCards.filter((card) => /输入|输出|input|print|类型转换/.test(cardSearchText(card)));
      }}
      if (group === "基础数据") {{
        return basicsCards.filter((card) => /变量|类型|数据|列表|字典|字符串|int|float|str/.test(cardSearchText(card)));
      }}
      return basicsCards.filter((card) => card.group === group);
    }}

    function activePart() {{
      return basicsParts.find((part) => part.group === state.basicsGroup) || basicsParts[0];
    }}

    function renderBasicsGallery() {{
      const active = activePart();
      basicsGalleryView.innerHTML = `
        <div class="editions-head">
          <div>
            <p class="basics-dir-title">Python Editions</p>
            <h2>训练目录</h2>
          </div>
          <p class="editions-copy">选择一个 Part 作为当前专辑；点击 Open 才进入知识卡片阅读页。</p>
        </div>
        <div class="album-shelf">
          ${{basicsParts.map((part, index) => `
            <article
              class="album-card part-cover-card ${{active.id === part.id ? "active" : ""}}"
              data-part-id="${{part.id}}"
              style="--cover-ratio: ${{part.aspectRatio || "4 / 3"}}; --cover-fit: ${{part.coverFit || "cover"}}; --object-position: ${{part.objectPosition || "center"}};"
            >
              <div class="part-cover-media" aria-hidden="true">
                <img src="${{part.cover}}" alt="" loading="lazy">
              </div>
              <button class="album-select" type="button" data-part-select="${{part.id}}" aria-label="选中 ${{escapeHtml(part.group)}}">
                <span class="album-index">${{escapeHtml(part.part || `Part ${{String(index + 1).padStart(2, "0")}}`)}}</span>
                <span class="album-meta">
                  <strong>${{escapeHtml(part.title || part.group)}}</strong>
                  <small>${{escapeHtml(part.subtitle || part.en)}} · ${{cardsForGroup(part.group).length}} cards</small>
                  <em>${{escapeHtml(part.desc || "")}}</em>
                </span>
              </button>
              <button class="album-open" type="button" data-part-open="${{part.id}}">Open</button>
            </article>
          `).join("")}}
        </div>
        <div class="album-timeline">
          ${{basicsParts.map((part, index) => `
            <button type="button" class="${{active.id === part.id ? "active" : ""}}" data-part-select="${{part.id}}">
              <b>${{escapeHtml(part.part || `Part ${{String(index + 1).padStart(2, "0")}}`)}}</b>
              <small>${{escapeHtml(part.group)}}<br>${{escapeHtml(part.subtitle || part.en)}}</small>
            </button>
          `).join("")}}
        </div>
      `;
    }}

    function renderBasicsDetail() {{
      const part = activePart();
      const cards = cardsForGroup(part.group);
      basicsDetailView.innerHTML = `
        <section class="training-head">
          <button class="back-gallery" type="button" data-back-gallery>返回 Gallery</button>
          <div>
            <p>Part ${{String(basicsParts.indexOf(part) + 1).padStart(2, "0")}} · ${{escapeHtml(part.en)}}</p>
            <h2>${{escapeHtml(part.group)}}</h2>
          </div>
        </section>
        <div class="training-cards">
          ${{cards.map(renderTrainingCard).join("") || `<section class="training-card"><p>这一组还没有训练卡片。</p></section>`}}
        </div>
      `;
    }}

    function showBasicsGallery() {{
      basicsPage.dataset.view = "gallery";
      basicsGalleryView.hidden = false;
      basicsDetailView.hidden = true;
      renderBasicsGallery();
    }}

    function showBasicsDetail(partId = activePart().id) {{
      const part = basicsParts.find((item) => item.id === partId) || activePart();
      state.basicsGroup = part.group;
      basicsPage.dataset.view = "detail";
      basicsGalleryView.hidden = true;
      basicsDetailView.hidden = false;
      renderBasicsDetail();
    }}

    function renderBasicsPage() {{
      showBasicsGallery();
    }}

    function cardRenderOrder(card) {{
      const order = card?.ui?.renderOrder;
      return Array.isArray(order) && order.length ? order : defaultBasicsRenderOrder;
    }}

    function fieldLabel(field) {{
      if (field === "teacherTalk") return "提醒";
      return basicsFieldLabels[field] || field;
    }}

    function isEmptyField(value) {{
      if (value == null) return true;
      if (Array.isArray(value)) return value.length === 0;
      if (typeof value === "object") return !Object.keys(value).length;
      return String(value).trim() === "";
    }}

    function listFromValue(value) {{
      if (Array.isArray(value)) return value;
      if (typeof value === "string") return value.split(String.fromCharCode(10)).filter(Boolean);
      if (value && typeof value === "object") return [value.text || value.title || JSON.stringify(value)];
      return [];
    }}

    function renderTrainingCard(card) {{
      const rawId = String(card.id || card.title || "");
      const id = escapeHtml(rawId);
      const badge = card?.ui?.badge || card.level || "入门";
      return `
        <section class="training-card training-card-v3">
          <header>
            <div>
              <p class="group-label">${{escapeHtml(card.group || "基础内容")}}</p>
              <h3>${{escapeHtml(card.title || "未命名训练")}}</h3>
              ${{card.quickTake ? `<p class="plain-quick-take">${{escapeHtml(card.quickTake)}}</p>` : ""}}
            </div>
            <span class="level-tag">${{escapeHtml(badge)}}</span>
          </header>
          ${{card.goal ? `<p class="basic-goal"><b>目标：</b>${{escapeHtml(card.goal)}}</p>` : ""}}
          ${{cardRenderOrder(card).filter((field) => field !== "quickTake").map((field) => renderBasicsField(card, field, id)).join("")}}
        </section>
      `;
    }}

    function renderBasicsField(card, field, id) {{
      const value = card[field];
      if (isEmptyField(value)) return "";
      const label = fieldLabel(field);
      if (field === "plainExplainLong") {{
        return "";
      }}
      if (field === "stepByStep") {{
        return `
          <section class="plain-section">
            <h4>${{escapeHtml(label)}}</h4>
            <div class="step-grid">
              ${{listFromValue(value).map((item, index) => `<div class="step-card"><span>${{String(index + 1).padStart(2, "0")}}</span><p>${{escapeHtml(item)}}</p></div>`).join("")}}
            </div>
          </section>
        `;
      }}
      if (field === "corePattern") {{
        return `
          <section class="plain-section">
            <h4>${{escapeHtml(label)}}</h4>
            <div class="core-pattern">
              ${{listFromValue(value).map((item) => `<code>${{escapeHtml(item)}}</code>`).join("")}}
            </div>
            ${{card.code ? renderCodeBlock(card, id) : ""}}
          </section>
        `;
      }}
      if (field === "plainAnalogy") {{
        const text = typeof value === "object" ? (value.text || value.title || "") : String(value);
        return `<section class="plain-section plain-analogy"><h4>${{escapeHtml(label)}}</h4><p>${{escapeHtml(text)}}</p></section>`;
      }}
      if (field === "readerCode") {{
        const text = listFromValue(value).join(String.fromCharCode(10));
        return `
          <details class="editor-box reader-code-box">
            <summary><span>${{escapeHtml(label)}}</span><button class="copy-code" type="button" data-copy-id="${{id}}" data-copy-kind="reader">复制</button></summary>
            <pre><code>${{escapeHtml(text)}}</code></pre>
          </details>
        `;
      }}
      if (field === "commonMistakes") {{
        return `<section class="plain-section mistake-list warning-list"><h4>${{escapeHtml(label)}}</h4><ul>${{listFromValue(value).map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul></section>`;
      }}
      if (field === "memoryHook" || field === "teacherTalk") {{
        return `<p class="soft-tip ${{field}}"><b>${{escapeHtml(label)}}：</b>${{escapeHtml(value)}}</p>`;
      }}
      if (field === "miniTask") {{
        return `<details class="mini-task-detail"><summary>${{escapeHtml(label)}}</summary><p>${{escapeHtml(value)}}</p></details>`;
      }}
      return `<section class="plain-section"><h4>${{escapeHtml(label)}}</h4><p>${{escapeHtml(typeof value === "string" ? value : JSON.stringify(value))}}</p></section>`;
    }}

    function renderMobaBox(card) {{
      if (!card.analogy && !card.mobaTip && !card.analogyTitle) return "";
      return `
        <section class="moba-box">
          <h4>${{escapeHtml(card.analogyTitle || "对战式理解")}}</h4>
          ${{card.analogy ? `<p>${{escapeHtml(card.analogy)}}</p>` : ""}}
          ${{card.mobaTip ? `<p class="moba-tip">${{escapeHtml(card.mobaTip)}}</p>` : ""}}
        </section>
      `;
    }}

    function renderEditorBox(card, id) {{
      const lines = [];
      if (card.coreConcept) lines.push(`# 核心：${{card.coreConcept}}`);
      if (card.summary) lines.push(`# 一句话：${{card.summary}}`);
      (card.points || []).slice(0, 4).forEach((point) => lines.push(`# 要点：${{point}}`));
      if (card.examTip) lines.push(`# 考点：${{card.examTip}}`);
      return `
        <section class="editor-box">
          <header>
            <span>VS Code 式速读</span>
            <button class="copy-code" type="button" data-copy-id="${{id}}" data-copy-kind="reader">复制</button>
          </header>
          <pre><code>${{escapeHtml(lines.join(String.fromCharCode(10)))}}</code></pre>
        </section>
      `;
    }}

    function renderCodeBlock(card, id) {{
      return `
        <section class="basic-code">
          <header>
            <span>代码例子</span>
            <div class="basic-code-tools">
              <button class="basic-code-font" type="button" data-basics-code-font="-1">A-</button>
              <button class="basic-code-font" type="button" data-basics-code-font="1">A+</button>
              <button class="copy-code" type="button" data-copy-id="${{id}}" data-copy-kind="code">复制</button>
            </div>
          </header>
          <pre><code>${{escapeHtml(card.code || "")}}</code></pre>
        </section>
      `;
    }}

    function renderCodeMapping(card) {{
      const rows = Array.isArray(card.codeMapping) ? card.codeMapping : [];
      if (!rows.length) return "";
      return `
        <section class="mapping-table">
          <h4>代码对应关系</h4>
          ${{rows.map((row) => `
            <div class="mapping-row">
              <code>${{escapeHtml(row.code || row.key || "")}}</code>
              <span>${{escapeHtml(row.meaning || row.value || row.text || "")}}</span>
            </div>
          `).join("")}}
        </section>
      `;
    }}

    function renderMistakes(card) {{
      const mistakes = Array.isArray(card.commonMistakes) ? card.commonMistakes : [];
      if (!mistakes.length) return "";
      return `
        <section class="mistake-list">
          <h4>常见卡点</h4>
          <ul>${{mistakes.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul>
        </section>
      `;
    }}

    function basicCardById(id) {{
      return basicsCards.find((card) => String(card.id || card.title || "") === String(id));
    }}

    async function copyText(text) {{
      if (navigator.clipboard?.writeText) {{
        await navigator.clipboard.writeText(text);
        return;
      }}
      const textarea = document.createElement("textarea");
      textarea.value = text;
      textarea.setAttribute("readonly", "");
      textarea.style.position = "fixed";
      textarea.style.left = "-9999px";
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      textarea.remove();
    }}

    function renderDetail() {{
      const doc = selectedDoc();
      const pdfSrc = encodeURI(doc.file);
      let activeIndex = doc.questions.findIndex((question) => question.number === state.activePage);
      if (activeIndex < 0) activeIndex = Math.min(Math.max(state.activePage, 1), doc.questions.length) - 1;
      const activeQuestion = doc.questions[activeIndex];
      state.activePage = activeQuestion.number;
      const questionHtml = `
        <div class="page-toolbar">
          <button class="pager-button" type="button" data-page-action="prev" ${{activeIndex === 0 ? "disabled" : ""}}>上一题</button>
          <div class="page-chips">
            ${{doc.questions.map((question) => `<button class="${{question.number === state.activePage ? "active" : ""}}" type="button" data-page="${{question.number}}">Q${{String(question.number).padStart(2, "0")}}</button>`).join("")}}
          </div>
          <button class="pager-button" type="button" data-page-action="next" ${{activeIndex === doc.questions.length - 1 ? "disabled" : ""}}>下一题</button>
        </div>
        <div class="pages">
          <div class="page-track">
            ${{renderQuestion(activeQuestion)}}
          </div>
        </div>
        <div class="actions">
          <a class="primary" href="${{pdfSrc}}" target="_blank" rel="noopener">打开原 PDF</a>
          <a href="${{pdfSrc}}" download>下载 PDF</a>
        </div>
      `;
      detail.innerHTML = questionHtml;
    }}

    function renderCodeLines(code) {{
      return code.split(String.fromCharCode(10)).map((line, index) => `<span class="code-line" data-line="${{index + 1}}">${{highlightCodeLine(line || " ")}}</span>`).join("");
    }}

    function renderQuestion(question) {{
      const mergedCode = question.codeBlocks.join(String.fromCharCode(10) + String.fromCharCode(10));
      const codeHtml = mergedCode ? `
        <section class="code-card">
          <pre tabindex="0" data-code="${{escapeHtml(mergedCode)}}"><code>${{renderCodeLines(mergedCode)}}</code></pre>
        </section>
      ` : `<p class="empty-code">这一题没有识别到完整代码片段。</p>`;

      return `
        <section class="page-card" id="page-${{question.number}}">
          <div class="code-panel">
            <div class="code-head">
              <h4>Q${{String(question.number).padStart(2, "0")}}：${{highlight(question.title)}}</h4>
              <div class="code-zoom" aria-label="代码字体缩放">
                <button type="button" data-code-zoom="-1" title="缩小代码字体">A-</button>
                <button type="button" data-code-zoom="1" title="放大代码字体">A+</button>
              </div>
            </div>
            <p class="source-note">来源 PDF 第 ${{question.sourcePages.join("、")}} 页</p>
            ${{codeHtml}}
            <div class="read-panel" data-read-panel>
              <section data-code-explanation>
                <div class="read-title-row">
                  <h5>代码讲解</h5>
                </div>
                <p>框选代码后右键读取，就在这里显示讲解。</p>
              </section>
            </div>
          </div>
        </section>
      `;
    }}

    function pairHint(lines) {{
      const text = lines.join(String.fromCharCode(10));
      if (/import\\s+/.test(text)) return "准备工具：先导入模块，像开局先买基础装备。";
      if (/input\\(/.test(text)) return "读取输入：向用户要数据，后面代码才能计算。";
      if (/int\\(|float\\(|eval\\(/.test(text)) return "转换类型：把键盘输入的文字变成数字。";
      if (/if\\s+/.test(text)) return "条件判断：满足条件才执行，像能开团才上。";
      if (/else:|elif\\s+/.test(text)) return "分支兜底：条件不满足时走另一条路线。";
      if (/for\\s+/.test(text)) return "固定循环：按次数重复，像清一波又一波兵。";
      if (/while\\s+/.test(text)) return "条件循环：只要条件还成立就继续执行。";
      if (/\\+=|-=/.test(text)) return "累加更新：把本轮结果加到总数里。";
      if (/\\*=/.test(text)) return "连乘更新：常用于阶乘或乘积类题。";
      if (/append\\(/.test(text)) return "加入列表：把新数据放进队伍末尾。";
      if (/print\\(/.test(text)) return "输出结果：把答案显示到屏幕上。";
      if (/sqrt|\\*\\*/.test(text)) return "公式计算：把前面变量代入数学公式。";
      return "处理中间变量：这一段在为最终答案铺路。";
    }}

    function lineHints(code) {{
      const lines = code.split(String.fromCharCode(10)).map((line) => line.trim()).filter(Boolean);
      if (!lines.length) return "";
      const groups = [];
      for (let i = 0; i < lines.length && groups.length < 5; i += 2) {{
        const pair = lines.slice(i, i + 2);
        groups.push(`<p><b>第 ${{i + 1}}-${{i + pair.length}} 行</b>：${{pairHint(pair)}}</p>`);
      }}
      return groups.join("");
    }}

    function explainSyntax(code) {{
      const tips = [];
      if (/import\\s+math/.test(code)) tips.push(["<code>import math</code>", "带一个数学装备栏，后面才能用 <code>math.sqrt()</code> 开平方。"]);
      if (/import\\s+random/.test(code)) tips.push(["<code>import random</code>", "像随机匹配队友，后面可用 <code>randint</code> 或 <code>choice</code> 随机抽。"]);
      if (/input\\(/.test(code)) tips.push(["<code>input()</code>", "让玩家在键盘输入数据；输入默认是文字，不是数字。"]);
      if (/eval\\(|int\\(|float\\(/.test(code)) tips.push(["<code>int/float/eval</code>", "把输入文字变成可计算数值，像把金币换成真正能买装备的钱。"]);
      if (/if\\s+/.test(code)) tips.push(["<code>if 条件:</code>", "满足条件才放技能；例如血量低于 30% 才回城。"]);
      if (/else:/.test(code)) tips.push(["<code>else:</code>", "条件不满足就走备用方案，相当于打不过就撤退。"]);
      if (/for\\s+/.test(code)) tips.push(["<code>for i in range(n):</code>", "固定重复 n 次，像连续清 n 波兵线。"]);
      if (/while\\s+/.test(code)) tips.push(["<code>while 条件:</code>", "只要条件还成立就继续，像水晶没破就继续守。"]);
      if (/break/.test(code)) tips.push(["<code>break</code>", "目标完成立刻退出循环，像拿到主宰就结束这轮刷野。"]);
      if (/append\\(/.test(code)) tips.push(["<code>list.append(x)</code>", "把 x 放进列表尾部，像把新英雄加入队伍。"]);
      if (/\\.split\\(/.test(code)) tips.push(["<code>字符串.split()</code>", "把一串输入按空格或逗号拆开，像把五人队伍拆成单个英雄。"]);
      if (/\\.sort\\(|sorted\\(/.test(code)) tips.push(["<code>sort()</code>", "给列表排序；<code>reverse=True</code> 就从高到低排战力。"]);
      if (/print\\(/.test(code)) tips.push(["<code>print()</code>", "把最终结果显示出来，像结算面板展示评分。"]);
      if (!tips.length) tips.push(["看结构", "先找输入、处理、输出三步；零基础先别背，先会认。"]);
      const picked = tips.slice(0, 5).map(([name, desc]) => `<p><b>${{name}}</b>：${{desc}}</p>`);
      picked.push(`<p><b>最基本写法</b>：<code>x = input()</code>、<code>if x:</code>、<code>print(x)</code></p>`);
      return picked.join("");
    }}

    function explainAlgorithm(code) {{
      if (/sqrt|海伦|p\\*\\(p-a\\)/.test(code)) return `<p><b>思路</b>：先检查三边能不能成团，再套海伦公式。</p><p><b>王者类比</b>：阵容不合法不能开局，合法才计算战力。</p><p><b>题解模板</b>：输入 → 判断合法 → 代公式 → 输出。</p>`;
      if (/b\\*b-4\\*a\\*c|sqrt\\(p\\)/.test(code)) return `<p><b>思路</b>：先算判别式 Δ，Δ≥0 才能继续求根。</p><p><b>王者类比</b>：先看能不能开团，条件够了再放大招。</p><p><b>模板</b>：<code>d=b*b-4*a*c</code>，再 <code>if d>=0:</code>。</p>`;
      if (/for\\s+.+range/.test(code) && /\\+=|-=/.test(code)) return `<p><b>思路</b>：用一个变量攒结果，每轮循环更新一次。</p><p><b>最基本 for</b>：<code>for i in range(5): print(i)</code></p><p><b>王者类比</b>：每清一波兵，金币总数加一次。</p>`;
      if (/factorial|\\*=/.test(code)) return `<p><b>思路</b>：从 1 开始连乘，循环一次乘一个数。</p><p><b>模板</b>：<code>s=1</code>，<code>for i in range(1,n+1): s*=i</code></p>`;
      if (/max\\(|min\\(|average|平均|score/.test(code)) return `<p><b>思路</b>：先收集成绩，再算总分、平均分、最高最低。</p><p><b>模板</b>：列表保存数据，<code>sum(nums)/len(nums)</code> 求平均。</p>`;
      if (/while\\s+True|break/.test(code)) return `<p><b>思路</b>：一直循环，成功时用 <code>break</code> 停。</p><p><b>最基本 while</b>：<code>while True:</code>，满足条件就 <code>break</code>。</p><p><b>王者类比</b>：没推掉水晶就继续打，推掉立刻结束。</p>`;
      if (/for\\s+.+for\\s+|矩阵|range\\(3\\)/s.test(code)) return `<p><b>思路</b>：外层管第几行，内层管这一行打印什么。</p><p><b>模板</b>：<code>for i in range(m):</code> 里面再写 <code>for j in range(n):</code>。</p>`;
      if (/\\[::?-1\\]|回文/.test(code)) return `<p><b>思路</b>：把字符串反过来，比一比是否相同。</p><p><b>模板</b>：<code>s == s[::-1]</code>。</p>`;
      if (/append\\(|list|numbers|列表/.test(code)) return `<p><b>思路</b>：先把多个数据装进列表，再遍历处理。</p><p><b>模板</b>：<code>nums=[]</code>，<code>nums.append(x)</code>。</p>`;
      if (/dict|\\.items\\(|\\.keys\\(|del\\s+/.test(code)) return `<p><b>思路</b>：字典用 key 找 value，像英雄名对应位置。</p><p><b>模板</b>：<code>d["数学"]="L01"</code>，<code>for k,v in d.items():</code>。</p>`;
      if (/random|randint|choice/.test(code)) return `<p><b>思路</b>：从范围或字符池里随机抽。</p><p><b>王者类比</b>：像随机分路或随机英雄。</p><p><b>模板</b>：<code>random.choice(pool)</code>。</p>`;
      return `<p><b>通用题解</b>：输入数据 → 设置变量 → 判断/循环处理 → 输出答案。</p><p><b>零基础抓手</b>：先找 <code>input</code>、<code>if/for/while</code>、<code>print</code>。</p>`;
    }}

    function showPopover(event, code) {{
      syntaxText.innerHTML = lineHints(code) + explainSyntax(code);
      algorithmText.innerHTML = explainAlgorithm(code);
      popover.classList.add("show");
      movePopover(event);
    }}

    function movePopover(event) {{
      const margin = 14;
      const rect = popover.getBoundingClientRect();
      let left = event.clientX + 18;
      let top = event.clientY + 18;
      if (left + rect.width > window.innerWidth - margin) left = window.innerWidth - rect.width - margin;
      if (top + rect.height > window.innerHeight - margin) top = event.clientY - rect.height - 18;
      popover.style.left = `${{Math.max(margin, left)}}px`;
      popover.style.top = `${{Math.max(margin, top)}}px`;
    }}

    function hidePopover() {{
      popover.classList.remove("show");
    }}

    function clearPickedLines() {{
      document.querySelectorAll(".code-line.picked").forEach((line) => line.classList.remove("picked"));
      selectionState.selectedCode = "";
      selectionState.selectedPanel = null;
    }}

    function rectsIntersect(a, b) {{
      return !(a.right < b.left || a.left > b.right || a.bottom < b.top || a.top > b.bottom);
    }}

    function normalizeRect(x1, y1, x2, y2) {{
      return {{
        left: Math.min(x1, x2),
        top: Math.min(y1, y2),
        right: Math.max(x1, x2),
        bottom: Math.max(y1, y2),
        width: Math.abs(x2 - x1),
        height: Math.abs(y2 - y1)
      }};
    }}

    function drawSelectionBox(rect) {{
      selectionBox.style.display = "block";
      selectionBox.style.left = `${{rect.left}}px`;
      selectionBox.style.top = `${{rect.top}}px`;
      selectionBox.style.width = `${{rect.width}}px`;
      selectionBox.style.height = `${{rect.height}}px`;
    }}

    function hideReadMenu() {{
      readMenu.style.display = "none";
    }}

    function hideReadPanels() {{
      document.querySelectorAll("[data-read-panel].show").forEach((panel) => panel.classList.remove("show"));
    }}

    function showReadMenu(x, y) {{
      readMenu.style.display = "block";
      const rect = readMenu.getBoundingClientRect();
      const left = Math.min(x, window.innerWidth - rect.width - 12);
      const top = Math.min(y, window.innerHeight - rect.height - 12);
      readMenu.style.left = `${{Math.max(12, left)}}px`;
      readMenu.style.top = `${{Math.max(12, top)}}px`;
    }}

    function updatePickedLines(rect) {{
      if (!selectionState.activePre) return;
      const lines = [...selectionState.activePre.querySelectorAll(".code-line")];
      const picked = [];
      lines.forEach((line) => {{
        const lineRect = line.getBoundingClientRect();
        const isPicked = rectsIntersect(rect, lineRect);
        line.classList.toggle("picked", isPicked);
        if (isPicked) picked.push(line.textContent);
      }});
      selectionState.selectedCode = picked.join(String.fromCharCode(10)).trim();
      selectionState.selectedPanel = selectionState.activePre.closest(".code-panel")?.querySelector("[data-read-panel]");
    }}

    function normalizeForMatch(text) {{
      return String(text || "")
        .replace(/[\u201c\u201d]/g, '"')
        .replace(/[\u2018\u2019]/g, "'")
        .replace(/\s+/g, "")
        .toLowerCase();
    }}

    function normalizeCodeShape(text) {{
      return normalizeForMatch(String(text || "").replace(/(["']).*?\\1/g, ""));
    }}

    function currentQuestionId() {{
      const question = currentQuestion();
      return `${{state.selected}}-Q${{String(question.number).padStart(2, "0")}}`;
    }}

    function matchExplanationBlock(questionId, selectedCode) {{
      const questionExplanation = codeExplanationByQuestion.get(questionId);
      if (!questionExplanation || !Array.isArray(questionExplanation.blocks)) return null;
      const selected = normalizeForMatch(selectedCode);
      const selectedShape = normalizeCodeShape(selectedCode);
      let best = null;
      let bestScore = -1;

      questionExplanation.blocks.forEach((block) => {{
        const candidates = [];
        if (Array.isArray(block.match)) candidates.push(...block.match);
        if (block.selectedCode) candidates.push(block.selectedCode);
        candidates.forEach((candidate) => {{
          const normalized = normalizeForMatch(candidate);
          const shaped = normalizeCodeShape(candidate);
          if (!normalized && !shaped) return;
          const hit =
            (normalized && (selected.includes(normalized) || normalized.includes(selected))) ||
            (shaped && (selectedShape.includes(shaped) || shaped.includes(selectedShape)));
          if (!hit) return;
          const score = Math.max(normalized.length, shaped.length);
          if (score > bestScore) {{
            best = block;
            bestScore = score;
          }}
        }});
      }});

      return best;
    }}

    function renderLineByLine(items) {{
      if (!Array.isArray(items) || !items.length) return "";
      return `
        <section>
          <h5>逐行理解</h5>
          <ul>
            ${{items.map((item) => {{
              if (typeof item === "string") return `<li>${{escapeHtml(item)}}</li>`;
              return `<li><code>${{escapeHtml(item.code || "")}}</code>：${{escapeHtml(item.explain || "")}}</li>`;
            }}).join("")}}
          </ul>
        </section>
      `;
    }}

    function renderStringList(title, items) {{
      if (!Array.isArray(items) || !items.length) return "";
      return `
        <section>
          <h5>${{escapeHtml(title)}}</h5>
          <ul>${{items.map((item) => `<li>${{escapeHtml(item)}}</li>`).join("")}}</ul>
        </section>
      `;
    }}

    function renderExplanationBlock(block) {{
      if (!block) {{
        return `
          <section>
            <div class="read-title-row"><h5>暂未匹配到讲解</h5></div>
            <p>当前划选内容没有命中新版解释数据里的 match。可以多框选一两行完整代码再右键读取。</p>
          </section>
        `;
      }}
      return `
        <section>
          <div class="read-title-row">
            <h5>${{escapeHtml(block.title || "代码讲解")}}</h5>
            ${{block.important ? `<span class="important-badge">重点讲解</span>` : ""}}
          </div>
          <p>${{escapeHtml(block.explain || "")}}</p>
        </section>
        ${{renderLineByLine(block.lineByLine)}}
        ${{block.gameStyleExplain ? `<section><h5>形象理解</h5><p>${{escapeHtml(block.gameStyleExplain)}}</p></section>` : ""}}
        ${{renderStringList("常见错误", block.commonMistakes)}}
        ${{block.examTip ? `<section><h5>考点提醒</h5><p>${{escapeHtml(block.examTip)}}</p></section>` : ""}}
      `;
    }}

    function readPickedCode() {{
      const code = selectionState.selectedCode.trim();
      const panel = selectionState.selectedPanel;
      if (!code || !panel) return;
      const target = panel.querySelector("[data-code-explanation]");
      const block = matchExplanationBlock(currentQuestionId(), code);
      if (target) target.innerHTML = renderExplanationBlock(block);
      panel.classList.add("show");
      hideReadMenu();
    }}

    function currentQuestion() {{
      const doc = selectedDoc();
      return doc.questions.find((item) => item.number === state.activePage) || doc.questions[0];
    }}

    function starterCode(question) {{
      return `# ${{question.title}}${{String.fromCharCode(10)}}# 在这里默写你的 Python 代码${{String.fromCharCode(10)}}`;
    }}

    function isFileProtocol() {{
      return location.protocol === "file:";
    }}

    function pyodideServerHint() {{
      return [
        "当前是 file:// 方式打开，Python 运行环境可能无法加载。",
        "请双击“启动本地服务器.bat”，然后访问：",
        "http://localhost:8000/index.html",
        "",
        "服务器窗口不要关闭。"
      ].join("\\n");
    }}

    function isPyodideLoadError(error) {{
      const message = String(error && error.message ? error.message : error || "");
      return isFileProtocol() || /pyodide|dynamically imported module|Failed to fetch|loadPyodide|python_stdlib|wasm/i.test(message);
    }}

    function formatPyodideLoadError(error) {{
      const message = String(error && error.message ? error.message : error || "");
      const lines = [
        "Python 运行环境加载失败。",
        "",
        pyodideServerHint()
      ];
      if (!isFileProtocol()) {{
        lines.push("", "请确认 pyodide 文件夹完整，并且页面是通过本地服务器打开。");
      }}
      if (message) {{
        lines.push("", "浏览器原始提示：", message);
      }}
      return lines.join("\\n");
    }}

    function formatPracticeError(error) {{
      if (isPyodideLoadError(error)) return formatPyodideLoadError(error);
      return String(error && error.message ? error.message : error);
    }}

    function showFileProtocolWarning() {{
      if (!isFileProtocol() || pyodideReady) return false;
      pyStatus.textContent = "请使用本地服务器打开";
      practiceOutput.textContent = pyodideServerHint();
      runPractice.disabled = true;
      return true;
    }}

    function renderPracticeQuestion(resetCode = true) {{
      const question = currentQuestion();
      practiceTitle.textContent = `Q${{String(question.number).padStart(2, "0")}}：${{question.title}}`;
      practiceDesc.textContent = question.codeBlocks.length
        ? "请先不要看答案，尝试根据题目默写代码；需要输入的数据写在右侧输入框。"
        : "这题暂时没有识别到完整代码答案，可以先根据题目自行练习。";
      practiceSource.textContent = `来源 PDF 第 ${{question.sourcePages.join("、")}} 页`;
      if (resetCode) practiceCode.value = starterCode(question);
      practiceOutput.textContent = pyodideReady ? "等待运行..." : "Python 环境加载中...";
      showFileProtocolWarning();
    }}

    async function ensurePyodide() {{
      if (pyodideReady) return pyodideRuntime;
      if (showFileProtocolWarning()) {{
        throw new Error(pyodideServerHint());
      }}
      if (pyodideLoading) return pyodideLoading;
      pyodideLoading = (async () => {{
        pyStatus.textContent = "Python 环境加载中...";
        runPractice.disabled = true;
        if (typeof loadPyodide !== "function") {{
          throw new Error("没有找到 ./pyodide/pyodide.js，请确认 pyodide 文件夹已随页面一起复制。");
        }}
        pyodideRuntime = await loadPyodide({{ indexURL: "./pyodide/" }});
        pyodideReady = true;
        pyStatus.textContent = "Python 环境已就绪";
        runPractice.disabled = false;
        return pyodideRuntime;
      }})().catch((error) => {{
        pyStatus.textContent = "Python 环境加载失败";
        practiceOutput.textContent = formatPyodideLoadError(error);
        pyodideLoading = null;
        throw error;
      }});
      return pyodideLoading;
    }}

    async function runPracticeCode() {{
      practiceOutput.textContent = pyodideReady ? "运行中..." : "Python 环境加载中...";
      runPractice.disabled = true;
      try {{
        const py = await ensurePyodide();
        const stdout = [];
        const stderr = [];
        py.setStdout({{ batched: (text) => stdout.push(text) }});
        py.setStderr({{ batched: (text) => stderr.push(text) }});
        py.globals.set("__codex_input_lines", practiceInput.value.split(/\\r?\\n/));
        py.runPython(`
import builtins
_codex_inputs = list(__codex_input_lines)
def input(prompt=""):
    print(prompt, end="")
    if _codex_inputs:
        return _codex_inputs.pop(0)
    return ""
builtins.input = input
`);
        await py.runPythonAsync(practiceCode.value);
        const output = [...stdout, ...stderr].join("\\n").trim();
        practiceOutput.textContent = output || "代码运行完成，没有输出。";
      }} catch (error) {{
        practiceOutput.textContent = formatPracticeError(error);
      }} finally {{
        if (pyodideReady) runPractice.disabled = false;
      }}
    }}

    function render() {{
      renderNav();
      renderDocStrip();
      renderSideMeta();
      renderQuestionList();
      renderDetail();
      updateProgressUI();
    }}

    chapterNav.addEventListener("click", (event) => {{
      const button = event.target.closest("button[data-filter]");
      if (!button) return;
      state.filter = button.dataset.filter;
      if (state.filter !== "all") state.selected = state.filter;
      state.activePage = 1;
      render();
      showReward(`进入${{button.querySelector("span")?.textContent || "章节"}}`, "章节巡检 +10");
      unlockActiveQuestion();
    }});

    docStrip.addEventListener("click", (event) => {{
      const card = event.target.closest(".doc-card[data-id]");
      if (!card) return;
      state.selected = card.dataset.id;
      state.activePage = 1;
      render();
      const doc = selectedDoc();
      showReward(`进入${{doc.range}}`, "资料库 +10");
      unlockActiveQuestion();
    }});

    searchInput.addEventListener("input", (event) => {{
      state.keyword = event.target.value;
      render();
    }});

    detail.addEventListener("click", (event) => {{
      const doc = selectedDoc();
      const action = event.target.closest("button[data-page-action]");
      if (action) {{
        const currentIndex = Math.max(0, doc.questions.findIndex((question) => question.number === state.activePage));
        const nextIndex = Math.min(Math.max(currentIndex + (action.dataset.pageAction === "next" ? 1 : -1), 0), doc.questions.length - 1);
        state.activePage = doc.questions[nextIndex].number;
        renderQuestionList();
        renderDetail();
        unlockActiveQuestion();
        return;
      }}
      const zoom = event.target.closest("button[data-code-zoom]");
      if (zoom) {{
        setCodeFontSize(codeFontSize + Number(zoom.dataset.codeZoom));
        return;
      }}
      const button = event.target.closest("button[data-page]");
      if (!button) return;
      state.activePage = Number(button.dataset.page);
      renderQuestionList();
      renderDetail();
      unlockActiveQuestion();
    }});

    questionList.addEventListener("click", (event) => {{
      const button = event.target.closest("button[data-side-question]");
      if (!button) return;
      state.activePage = Number(button.dataset.sideQuestion);
      renderQuestionList();
      renderDetail();
      unlockActiveQuestion();
    }});

    detail.addEventListener("mousedown", (event) => {{
      const pre = event.target.closest("pre[data-code]");
      if (!pre || event.button !== 0) return;
      event.preventDefault();
      hideReadMenu();
      clearPickedLines();
      selectionState.dragging = true;
      selectionState.startX = event.clientX;
      selectionState.startY = event.clientY;
      selectionState.activePre = pre;
      drawSelectionBox(normalizeRect(event.clientX, event.clientY, event.clientX, event.clientY));
    }});

    document.addEventListener("mousemove", (event) => {{
      if (!selectionState.dragging) return;
      const rect = normalizeRect(selectionState.startX, selectionState.startY, event.clientX, event.clientY);
      drawSelectionBox(rect);
      updatePickedLines(rect);
    }});

    detail.addEventListener("wheel", (event) => {{
      const codeCard = event.target.closest(".code-card");
      if (!codeCard || !event.ctrlKey) return;
      event.preventDefault();
      const delta = event.deltaY < 0 ? 1 : -1;
      setCodeFontSize(codeFontSize + delta);
    }}, {{ passive: false }});

    document.addEventListener("mouseup", () => {{
      if (!selectionState.dragging) return;
      selectionState.dragging = false;
      selectionBox.style.display = "none";
    }});

    detail.addEventListener("contextmenu", (event) => {{
      const pre = event.target.closest("pre[data-code]");
      if (!pre || !selectionState.selectedCode.trim()) return;
      event.preventDefault();
      showReadMenu(event.clientX, event.clientY);
    }});

    document.addEventListener("click", (event) => {{
      if (!event.target.closest("#readMenu")) hideReadMenu();
    }});

    readSelection.addEventListener("click", readPickedCode);

    document.addEventListener("keydown", (event) => {{
      if (event.key === "Escape") {{
        hideReadMenu();
        hideReadPanels();
        clearPickedLines();
      }}
    }});

    sidebar.addEventListener("pointerenter", () => sidebar.classList.add("is-open"));
    sidebar.addEventListener("pointerleave", () => sidebar.classList.remove("is-open"));
    sidebar.addEventListener("click", (event) => {{
      if (event.clientX < 72) sidebar.classList.toggle("is-open");
    }});
    document.addEventListener("click", (event) => {{
      if (event.clientX < 72) sidebar.classList.toggle("is-open");
      if (event.clientX > 430 && !event.target.closest(".library-sidebar")) sidebar.classList.remove("is-open");
    }});

    document.addEventListener("pointermove", (event) => {{
      if (event.clientX < 72) sidebar.classList.add("is-open");
      if (event.clientX > 430) sidebar.classList.remove("is-open");
    }});

    memoryEntry.addEventListener("click", () => {{
      practiceOverlay.classList.add("show");
      renderPracticeQuestion(true);
      showReward("代码关卡启动", "自我检测 +10");
      ensurePyodide().catch(() => {{}});
      practiceCode.focus();
    }});

    memoryClose.addEventListener("click", () => memoryPanel.classList.remove("show"));

    memoryPrompt.addEventListener("click", () => {{
      const doc = selectedDoc();
      const question = doc.questions.find((item) => item.number === state.activePage) || doc.questions[0];
      const prefix = `# ${{String(question.number).padStart(2, "0")}}：${{question.title}}${{String.fromCharCode(10)}}`;
      if (!memoryText.value.startsWith(prefix)) memoryText.value = prefix + memoryText.value;
      memoryText.focus();
    }});

    closePractice.addEventListener("click", () => practiceOverlay.classList.remove("show"));
    resetPractice.addEventListener("click", () => renderPracticeQuestion(true));
    runPractice.addEventListener("click", runPracticeCode);
    nextPractice.addEventListener("click", () => {{
      const doc = selectedDoc();
      const currentIndex = Math.max(0, doc.questions.findIndex((question) => question.number === state.activePage));
      const nextIndex = (currentIndex + 1) % doc.questions.length;
      state.activePage = doc.questions[nextIndex].number;
      renderQuestionList();
      renderDetail();
      unlockActiveQuestion();
      renderPracticeQuestion(true);
    }});

    basicsEntry.addEventListener("click", showBasicsPage);
    basicsEntry.addEventListener("keydown", (event) => {{
      if (event.key !== "Enter" && event.key !== " ") return;
      event.preventDefault();
      showBasicsPage();
    }});
    basicsHome.addEventListener("click", returnToStart);
    basicsLibrary.addEventListener("click", openLibrary);

    basicsPage.addEventListener("click", (event) => {{
      const selectButton = event.target.closest("button[data-part-select]");
      if (selectButton) {{
        const part = basicsParts.find((item) => item.id === selectButton.dataset.partSelect);
        if (!part) return;
        state.basicsGroup = part.group;
        renderBasicsGallery();
        showReward(`选中${{part.group}}`, "点击 Open 进入");
        return;
      }}
      const openButton = event.target.closest("button[data-part-open]");
      if (openButton) {{
        showBasicsDetail(openButton.dataset.partOpen);
        showReward(`进入${{activePart().group}}`, "知识卡片");
        return;
      }}
      const backGallery = event.target.closest("button[data-back-gallery]");
      if (backGallery) {{
        showBasicsGallery();
        showReward("返回 Gallery", "训练目录");
        return;
      }}
      const fontButton = event.target.closest("button[data-basics-font]");
      if (fontButton) {{
        setBasicsFontSize(basicsFontSize + Number(fontButton.dataset.basicsFont));
        return;
      }}
      const codeFontButton = event.target.closest("button[data-basics-code-font]");
      if (codeFontButton) {{
        setBasicsCodeFontSize(basicsCodeFontSize + Number(codeFontButton.dataset.basicsCodeFont));
        return;
      }}
      const copyButton = event.target.closest("button[data-copy-id]");
      if (copyButton) {{
        const card = basicCardById(copyButton.dataset.copyId);
        const text = copyButton.dataset.copyKind === "reader"
          ? listFromValue(card?.readerCode).join(String.fromCharCode(10))
          : (card?.code || (Array.isArray(card?.corePattern) ? card.corePattern.join(String.fromCharCode(10)) : (card?.corePattern || "")));
        copyText(text).then(() => showReward("已复制", "代码已进入剪贴板"))
          .catch(() => showReward("复制失败", "请手动选中复制"));
      }}
    }});

    basicsPage.addEventListener("wheel", (event) => {{
      const codePanel = event.target.closest(".basic-code, .editor-box, .mini-example");
      if (!codePanel || !event.ctrlKey) return;
      event.preventDefault();
      setBasicsCodeFontSize(basicsCodeFontSize + (event.deltaY < 0 ? 1 : -1));
    }}, {{ passive: false }});

    render();
    renderBasicsPage();
    updateProgressUI();
    initDesktopPet();
    startButton.addEventListener("click", showQuestionBankPage);
    returnStart.addEventListener("click", returnToStart);
    returnStartFixed.addEventListener("click", returnToStart);
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    warnings.filterwarnings("ignore")
    OUT.write_text(render_html(load_docs(), load_basics(), load_code_explanations()), encoding="utf-8")
    print(f"Wrote {OUT}")
