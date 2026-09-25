"""Style proposal engine: vague user style description → N distinct, presentable directions.

用户的正常情况：能描述个大概（"温暖一点、专业但别死板"），说不了那么工程化，
对排版布局也没有严格描述。本模块把这种模糊描述映射为若干个彼此可区分的风格方向，
附可落码 pattern 与参考条目，并给出多版本的统一呈现契约与对照页模板，
让 agent 生成 version-a/b/c… 后用同一张对照页呈现给用户。
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# 每个风格标签的"体感档案"：family 用于多样性保证，其余字段直接给 agent 当设计约束。
STYLE_PROFILES: dict[str, dict[str, str]] = {
    "极简克制": {"family": "素雅纸感", "feel": "留白多、层级靠字号与间距、全站只有一个强调色", "palette": "白/纸底 + 墨字 + 单一强调色", "type": "系统无衬线或克制衬线", "layout": "宽留白、hairline 分隔、少卡片", "suited": "内容型、工具型、文档、想显得专业可信", "avoid": "需要强情绪或促销氛围的页面"},
    "编辑风": {"family": "素雅纸感", "feel": "纸面杂志感：衬线大字、规则线、期号/图注语法", "palette": "米纸底 + 墨色 + 朱砂/砖红点缀", "type": "宋体/衬线标题 + 黑体正文", "layout": "报头三段式、双细线、编号目录、首字下沉", "suited": "博客、品牌、文化机构、想有人文温度", "avoid": "强促销、高转化的电商场"},
    "拟物质感": {"family": "素雅纸感", "feel": "实体感：统一光源下的一致阴影/高光，可按压、可内陷", "palette": "暖灰/米色底 + 材质色", "type": "系统字体 + 少量蚀刻铭牌字", "layout": "面板化、旋钮/拨档/屏幕井等控件语言", "suited": "工具、硬件品牌、想要手感和记忆点", "avoid": "内容极多的信息密集页"},
    "新粗野主义": {"family": "高声量", "feel": "大声量：硬黑描边、实色硬投影、撞色色块、按压回弹", "palette": "高饱和撞色（酸黄/粉/蓝）+ 黑", "type": "粗黑无衬线，大写/高字重", "layout": "贴纸、跑马灯、黑框区块、不规整拼贴", "suited": "年轻品牌、活动、潮流电商、想被记住", "avoid": "银行/医疗等严肃信任场景"},
    "渐变高饱和": {"family": "高声量", "feel": "色彩驱动：大渐变、高饱和、氛围光斑", "palette": "命名渐变（角度+色标）为主角，正文深墨保对比", "type": "几何无衬线 + 渐变裁切字", "layout": "渐变 hero、彩色分区、发光 CTA", "suited": "创意产品、发布页、想要情绪冲击", "avoid": "长时间阅读的内容页（视觉疲劳）"},
    "俏皮可爱": {"family": "高声量", "feel": "好玩：大圆角、bouncy 微交互、emoji/贴纸、拟人元素", "palette": "马卡龙糖果色 + 白", "type": "圆体感无衬线", "layout": "圆角卡、波浪分隔、漂浮装饰", "suited": "面向 C 端年轻用户、教育、社区", "avoid": "高端商务、奢侈品"},
    "暗色友好": {"family": "暗夜科技", "feel": "深底发光：近黑底、一色一义的高亮强调、代码感", "palette": "#0a0a0a 系底 + 霓虹强调（绿/琥珀/青）", "type": "等宽点缀 + 无衬线正文", "layout": "终端语汇、网格蒙版、辉光边缘", "suited": "开发者产品、技术品牌、终端文化", "avoid": "老年用户为主的消费场景"},
    "游戏UI科幻HUD": {"family": "暗夜科技", "feel": "HUD 仪表化：状态框、角标、扫描线、数据密布", "palette": "深底 + 荧光青/橙双色", "type": "方形等宽、大写标签", "layout": "角框、状态条、雷达/仪表元素", "suited": "游戏、电竞、科幻主题", "avoid": "日常内容页（信息过载）"},
    "3D着色器": {"family": "暗夜科技", "feel": "实时图形：WebGL/shader 驱动的动态视觉主角", "palette": "深底 + shader 渐变", "type": "极简无衬线让位给视觉", "layout": "全屏画布 + 悬浮 UI", "suited": "创意工作室、产品发布、视觉实验", "avoid": "性能敏感、降级要求高的页面"},
    "液态玻璃": {"family": "材质光泽", "feel": "折射：实时透镜弯曲背后内容，流动的光", "palette": "透明着色 + 亮边高光", "type": "无衬线，粗细对比大", "layout": "悬浮玻璃层、透镜跟随光标", "suited": "消费电子、发布页、想要苹果系质感", "avoid": "需兼容旧浏览器的主力页（有降级）"},
    "玻璃拟态": {"family": "材质光泽", "feel": "磨砂浮层：backdrop-filter 毛玻璃 + 1px 亮边", "palette": "渐变底 + 半透明白面板", "type": "无衬线 + 渐变裁切标题", "layout": "浮层卡片、胶囊导航、色斑漂移", "suited": "SaaS、活动页、现代感产品", "avoid": "文本超长阅读页（对比度难保）"},
    "全息金属质感": {"family": "材质光泽", "feel": "衍射光泽：彩虹衍射带、金属拉丝、视角变化", "palette": "深底 + 虹彩高光", "type": "细长无衬线大写", "layout": "全息徽章、箔面卡、镜面分区", "suited": "收藏/会员/限量感、音乐潮流", "avoid": "大量正文的页面"},
    "物理光照": {"family": "材质光泽", "feel": "仪器感：一个光源向量统辖全部阴影/高光/表面", "palette": "暖灰面板 + 光源色温一致", "type": "系统字体 + LCD 井等宽", "layout": "面板、chamfer 倒角、凹凸面、LED", "suited": "硬件/仪表品牌、想要独特记忆点", "avoid": "内容优先的文档页"},
    "微交互": {"family": "节奏动感", "feel": "手感：状态过渡细腻、反馈即动效（克制不喧宾）", "palette": "中性底 + 单强调", "type": "系统字体", "layout": "常规布局 + 高质量状态动画", "suited": "任何产品的打磨层（与其他风格叠加）", "avoid": "单独作为整页风格（是叠加维度）"},
    "动效密集": {"family": "节奏动感", "feel": "动起来：滚动叙事、入场编排、背景动效", "palette": "深浅皆可，动效是主角", "type": "无衬线", "layout": "分段叙事、视差、stagger 入场", "suited": "发布页、作品集、讲故事", "avoid": "文档/工具页（干扰阅读）"},
    "文字背景特效": {"family": "节奏动感", "feel": "字是视觉：大字动画、背景特效层", "palette": "深底 + 高对比文字特效", "type": "超大标题字", "layout": "文字主导 hero、跑马灯、字符渐变", "suited": "品牌口号页、专辑/活动主打", "avoid": "正文阅读页"},
    "点阵粒子": {"family": "节奏动感", "feel": "点阵语言：单色点阵、粒子波次、像素游戏感", "palette": "严格单色（墨/纸反转）", "type": "等宽或点阵字", "layout": "点阵装饰、波次加载、半调图案", "suited": "AI/agent 产品、极客文化", "avoid": "暖情感场景"},
    "商务克制": {"family": "商业可信", "feel": "可信：中性灰阶、无障碍优先、清晰层级", "palette": "白/浅灰 + 深蓝/墨 + 单强调", "type": "无衬线，标准字阶", "layout": "栅格严格、表格清晰、对比度高", "suited": "B2B、企业官网、后台、无障碍要求高", "avoid": "需要情绪感染力的消费品牌"},
    "电商实感": {"family": "商业可信", "feel": "转化导向：商品是主角、价格/评分/CTA 清晰", "palette": "白底 + 品牌色点缀", "type": "无衬线，价格数字突出", "layout": "商品卡网格、促销条、保障行", "suited": "网店、 marketplace、课程售卖", "avoid": "非交易类内容页"},
}

FEEL_KEYWORDS: list[tuple[str, str]] = [
    ("温暖", "编辑风"), ("温度", "拟物质感"), ("人文", "编辑风"), ("杂志", "编辑风"), ("印刷", "编辑风"), ("书卷", "编辑风"), ("文气", "编辑风"), ("warm", "编辑风"), ("cozy", "拟物质感"), ("editorial", "编辑风"), ("复古", "编辑风"), ("怀旧", "编辑风"),
    ("专业", "商务克制"), ("清爽", "极简克制"), ("干净", "极简克制"), ("简洁", "极简克制"), ("极简", "极简克制"), ("克制", "极简克制"), ("整洁", "极简克制"), ("利落", "极简克制"), ("clean", "极简克制"), ("minimal", "极简克制"),
    ("靠谱", "商务克制"), ("正式", "商务克制"), ("企业", "商务克制"), ("商务", "商务克制"), ("可靠", "商务克制"), ("无障碍", "商务克制"), ("b2b", "商务克制"), ("corporate", "商务克制"), ("严肃", "商务克制"),
    ("酷", "暗色友好"), ("科技", "暗色友好"), ("极客", "暗色友好"), ("黑客", "暗色友好"), ("终端", "暗色友好"), ("代码感", "暗色友好"), ("dark", "暗色友好"), ("tech", "暗色友好"),
    ("科幻", "游戏UI科幻HUD"), ("未来感", "游戏UI科幻HUD"), ("hud", "游戏UI科幻HUD"), ("游戏", "游戏UI科幻HUD"), ("电竞", "游戏UI科幻HUD"), ("futuristic", "游戏UI科幻HUD"),
    ("炫", "渐变高饱和"), ("醒目", "渐变高饱和"), ("高饱和", "渐变高饱和"), ("渐变", "渐变高饱和"), ("彩色", "渐变高饱和"), ("gradient", "渐变高饱和"), ("vibrant", "渐变高饱和"), ("大胆", "新粗野主义"),
    ("大胆", "新粗野主义"), ("张扬", "新粗野主义"), ("潮流", "新粗野主义"), ("街头", "新粗野主义"), ("撞色", "新粗野主义"), ("brutal", "新粗野主义"), ("bold", "新粗野主义"), ("潮", "新粗野主义"),
    ("活泼", "俏皮可爱"), ("可爱", "俏皮可爱"), ("有趣", "俏皮可爱"), ("轻快", "俏皮可爱"), ("年轻", "俏皮可爱"), ("童趣", "俏皮可爱"), ("playful", "俏皮可爱"), ("cute", "俏皮可爱"),
    ("高级", "拟物质感"), ("质感", "拟物质感"), ("精致", "拟物质感"), ("手感", "拟物质感"), ("实体", "物理光照"), ("光影", "物理光照"), ("立体", "物理光照"), ("仪器", "物理光照"), ("premium", "拟物质感"),
    ("梦幻", "玻璃拟态"), ("通透", "玻璃拟态"), ("轻盈", "玻璃拟态"), ("玻璃", "玻璃拟态"), ("毛玻璃", "玻璃拟态"), ("glass", "玻璃拟态"), ("dreamy", "玻璃拟态"), ("液态", "液态玻璃"), ("流体", "液态玻璃"),
    ("金属", "全息金属质感"), ("镭射", "全息金属质感"), ("全息", "全息金属质感"), ("holographic", "全息金属质感"), ("chrome", "全息金属质感"), ("箔", "全息金属质感"),
    ("动效", "动效密集"), ("动画", "动效密集"), ("活力", "动效密集"), ("滚动叙事", "动效密集"), ("motion", "动效密集"),
    ("粒子", "点阵粒子"), ("像素", "点阵粒子"), ("点阵", "点阵粒子"), ("波点", "点阵粒子"), ("pixel", "点阵粒子"), ("agent感", "点阵粒子"),
    ("电商", "电商实感"), ("商城", "电商实感"), ("转化", "电商实感"), ("网店", "电商实感"), ("ecommerce", "电商实感"), ("卖货", "电商实感"),
    ("大字", "文字背景特效"), ("标语", "文字背景特效"), ("口号", "文字背景特效"),
    ("光标", "微交互"), ("反馈", "微交互"), ("细节", "微交互"), ("打磨", "微交互"),
    ("3d", "3D着色器"), ("webgl", "3D着色器"), ("shader", "3D着色器"), ("着色器", "3D着色器"), ("实时图形", "3D着色器"),
]

FAMILIES: dict[str, list[str]] = {}
for _tag, _prof in STYLE_PROFILES.items():
    FAMILIES.setdefault(_prof["family"], []).append(_tag)

PAGE_TYPES: dict[str, dict[str, Any]] = {
    "storefront": {"aliases": ["store", "shop", "电商", "商城", "网店", "店面"], "prefer": ["电商实感", "极简克制", "俏皮可爱", "商务克制", "新粗野主义"], "avoid": ["游戏UI科幻HUD"]},
    "blog": {"aliases": ["博客", "手记", "专栏", "blog"], "prefer": ["编辑风", "极简克制", "暗色友好", "俏皮可爱"], "avoid": ["电商实感"]},
    "docs": {"aliases": ["docs", "文档", "文档站", "帮助中心", "api 文档"], "prefer": ["极简克制", "暗色友好", "商务克制", "编辑风"], "avoid": ["俏皮可爱", "动效密集"]},
    "event": {"aliases": ["event", "活动", "报名", "沙龙", "meetup", "发布会"], "prefer": ["新粗野主义", "渐变高饱和", "暗色友好", "编辑风", "俏皮可爱"], "avoid": []},
    "brochure": {"aliases": ["brochure", "折页", "工作室", "公司页", "portfolio", "作品集"], "prefer": ["编辑风", "极简克制", "拟物质感", "玻璃拟态", "新粗野主义"], "avoid": ["游戏UI科幻HUD"]},
    "landing": {"aliases": ["landing", "落地页", "官网", "产品页"], "prefer": ["极简克制", "渐变高饱和", "暗色友好", "新粗野主义", "物理光照"], "avoid": []},
    "dashboard": {"aliases": ["dashboard", "后台", "控制台", "面板"], "prefer": ["商务克制", "暗色友好", "极简克制"], "avoid": ["俏皮可爱", "新粗野主义"]},
}

_NEGATION = re.compile(r"(不要|别用|避免|不来|别整|不要用)\s*([^\s，。,.;；！!]{1,10})")


def _resolve_page_type(page_type: str | None, description: str) -> tuple[str | None, bool]:
    raw = (page_type or "").strip().lower()
    if raw in PAGE_TYPES:
        return raw, True
    low = description.lower()
    for pt, conf in PAGE_TYPES.items():
        if raw == pt or raw in conf["aliases"]:
            return pt, True
        for a in conf["aliases"]:
            if a in low or a in description:
                return pt, False  # 从描述里推断的
    return (raw or None), False


def _negated_tags(description: str) -> set[str]:
    avoid: set[str] = set()
    for m in _NEGATION.finditer(description):
        frag = m.group(2).lower()
        core = re.sub(r"(风格|风|感|系|调)$", "", frag) or frag
        for tag, prof in STYLE_PROFILES.items():
            if core in tag.lower() or tag.lower() in core:
                avoid.add(tag)
    return avoid


def _match_scores(description: str, page_type: str | None, avoid: set[str]) -> tuple[dict[str, int], list[str]]:
    low = description.lower()
    scores: dict[str, int] = {}
    matched: list[str] = []
    for kw, tag in FEEL_KEYWORDS:
        if tag in avoid:
            continue
        if kw in low or kw in description:
            scores[tag] = scores.get(tag, 0) + 2
            if kw not in matched:
                matched.append(kw)
    for tag, prof in STYLE_PROFILES.items():
        if tag in avoid:
            continue
        if tag in description or tag in low:
            scores[tag] = scores.get(tag, 0) + 3
    fit = PAGE_TYPES.get(page_type or {}, {})
    for tag in fit.get("prefer", []):
        if tag not in avoid:
            scores[tag] = scores.get(tag, 0) + 1
    return scores, matched


def _select_diverse(scores: dict[str, int], page_type: str | None, avoid: set[str], count: int) -> list[str]:
    fit = PAGE_TYPES.get(page_type or {}, {})
    ranked = sorted(scores.items(), key=lambda kv: (-kv[1], kv[0]))
    chosen: list[str] = []
    used_families: set[str] = set()

    def take(tag: str) -> None:
        chosen.append(tag)
        used_families.add(STYLE_PROFILES[tag]["family"])

    for tag, _s in ranked:
        if len(chosen) >= count:
            return chosen
        if tag in chosen or tag in avoid:
            continue
        if STYLE_PROFILES[tag]["family"] not in used_families:
            take(tag)
    # 第一轮补位：严格跨家族（场景适配清单优先，再按分数序）
    for tag in fit.get("prefer", []) + [t for t, _s in ranked] + list(STYLE_PROFILES.keys()):
        if len(chosen) >= count:
            return chosen
        if tag in chosen or tag in avoid:
            continue
        if STYLE_PROFILES[tag]["family"] not in used_families:
            take(tag)
    # 最后手段：家族用尽仍不够（count>6 才可能），允许同家族补位
    for tag, _s in ranked:
        if len(chosen) >= count:
            break
        if tag in chosen or tag in avoid:
            continue
        take(tag)
    return chosen


def _patterns_for_style(tag: str, items: list[dict[str, Any]], routes: dict[str, dict[str, str]]) -> list[str]:
    pattern_ids: list[str] = []
    for it in items:
        if tag not in (it.get("style") or []):
            continue
        route = routes.get(it.get("id") or "", {})
        for p in (route.get("pattern_ids") or "").split(";"):
            p = p.strip()
            if p and p not in pattern_ids:
                pattern_ids.append(p)
    return pattern_ids[:4]


def _reference_items(tag: str, items: list[dict[str, Any]], limit: int = 3) -> list[dict[str, Any]]:
    """质量位（按归档/免费/权重排序）+ 1 个长尾探索位（按日轮换，让同风格的低曝光条目有机会被 surfaced）。"""
    cand = [i for i in items if tag in (i.get("style") or [])]
    cand.sort(key=lambda i: (not i.get("has_archive"), i.get("access_cost") != "free", i.get("weight") == "L"))
    if not cand:
        return []
    ranked = cand[: max(1, limit - 1)]
    out = [
        {"id": i.get("id", ""), "title": (i.get("title") or "")[:60], "why": (i.get("summary") or "")[:70]}
        for i in ranked
    ]
    if limit >= 3 and len(cand) > len(ranked):
        import datetime as _dt

        pool = [i for i in cand if i not in ranked]
        pick = pool[(_dt.date.today().timetuple().tm_yday + len(tag)) % len(pool)]
        out.append(
            {
                "id": pick.get("id", ""),
                "title": (pick.get("title") or "")[:60],
                "why": "长尾探索位：同风格下较少被推荐的条目，实现前可用 list_catalog 复核",
                "explore": True,
            }
        )
    return out


def propose_styles(
    description: str,
    *,
    page_type: str | None = None,
    count: int = 4,
    framework: str | None = None,
    items: list[dict[str, Any]],
    routes: dict[str, dict[str, str]],
    data_root: Path | None = None,
) -> dict[str, Any]:
    count = max(2, min(int(count or 4), 5))
    page_type, inferred = _resolve_page_type(page_type, description or "")
    avoid = _negated_tags(description or "")
    scores, matched_keywords = _match_scores(description or "", page_type, avoid)
    chosen = _select_diverse(scores, page_type, avoid, count)

    directions: list[dict[str, Any]] = []
    for i, tag in enumerate(chosen):
        prof = STYLE_PROFILES[tag]
        directions.append(
            {
                "version": chr(ord("A") + i),
                "name": f"{prof['family']} · {tag}",
                "style_tags": [tag],
                "feel_line": prof["feel"],
                "palette": prof["palette"],
                "typography": prof["type"],
                "layout": prof["layout"],
                "suited_when": prof["suited"],
                "avoid_when": prof["avoid"],
                "pattern_ids": _patterns_for_style(tag, items, routes),
                "reference_items": _reference_items(tag, items),
            }
        )

    flow = [
        "1. 先把方向摘要（version/name/feel_line）呈现给用户；用户选定一个方向，或让全部生成。",
        "2. 每个方向生成一个单文件页面，文件名 version-a.html / version-b.html …（内容要求各版本完全一致，只改风格层）。",
        f"3. framework 约束：{framework or '未指定（默认单文件 HTML，内联 CSS/JS，无外部资源）'}。所有版本遵守同一约束。",
        "4. 用返回的 presentation_template 生成 index.html 统一对照页，链接各版本。",
        "5. 若环境可截图，在对照页每节加缩略图；不可截图则纯链接+文字说明。",
        "6. 重要：提案只是入口不是全部。方向确定后、动手实现前，用 list_catalog(style=<选定方向的标签>, granularity=component/effect/technique) 检索该方向下的全部条目——同风格下往往还有提案未列出的组件库/技法/效果，按 highlights 挑选补充。",
    ]

    return {
        "description": description,
        "page_type": page_type,
        "page_type_inferred": inferred,
        "framework": framework or "未指定",
        "matched_keywords": matched_keywords,
        "diversity_rule": "每个方向来自不同风格家族（family），保证一眼可区分；用户可指定 count（2-5）。",
        "directions": directions,
        "implementation_flow": flow,
        "presentation_contract": {
            "file_naming": {d["version"]: f"version-{d['version'].lower()}.html" for d in directions},
            "index": "index.html",
            "rules": ["各版本内容要求完全一致，仅风格层不同", "对照页每节：版本字母+方向名+一句话感受+入口链接", "页脚注明各版本 style_tags"],
        },
        "template": _presentation_template(description, page_type, directions),
    }


# ---- 组合指引：跨维度（风格×模式×组件库×效果）自由组合时的顺序/冲突/许可规则 ----

FAMILY_CLASH: dict[tuple[str, str], str] = {
    ("高声量", "暗夜科技"): "高饱和撞色与深底霓虹会互相打架——选定一个作主氛围，另一个只取单点元素（如粗野按钮用在暗页）",
    ("素雅纸感", "高声量"): "留白纸感与大声量气质相反；除非刻意做'克制版粗野'（黑描边但低饱和），不建议整页混用",
    ("素雅纸感", "材质光泽"): "可以（拟物纸面很好看），但必须统一光源向量与色温，否则阴影方向不一致会露馅",
    ("高声量", "材质光泽"): "全息/玻璃的精致感会被撞色压住；只建议在粗野页里做单张'箔面卡'点缀",
}

_LICENSE_NOTES: dict[str, str] = {
    "MIT": "保留版权与许可声明即可",
    "Apache-2.0": "保留 LICENSE 与 NOTICE 声明",
    "CC0-1.0": "公有领域，无义务（仍建议署名）",
    "MIT+Commons-Clause": "代码可自由使用，但不得将该库本身作为产品转售（Commons Clause 限制）",
    "MIT+CommonsClause": "代码可自由使用，但不得将该库本身作为产品转售（Commons Clause 限制）",
    "custom-non-redistribution": "可嵌入自己的应用，不得把组件集合原样再分发",
    "AGPL-3.0": "网络服务场景有开源义务——coss ui 仅 apps/ui 部分为 MIT，引用前核对来源文件许可",
    "unspecified": "许可未标注：使用前先到仓库核实",
    "proprietary": "专有来源：只用自写摘要和原站链接，不复制实现或媒体",
    "unknown": "许可未知：使用前先到仓库核实，不要当作可再分发",
    "AGPL-3.0+MIT-subtrees": "仓库主体与子树许可不同，引用前核对具体文件",
    "CC-BY-NC-4.0": "须署名，且不得用于商业用途",
    "GPL-3.0": "衍生作品须按 GPL-3.0 提供对应源码",
    "IPA-1.0": "字体许可：嵌入或再分发前核对 IPA 条款，不把字体文件当素材包再分发",
    "ISC": "保留版权与许可声明即可",
    "OFL-1.1": "字体可嵌入文档；不要把字体文件单独抽出再分发",
    "PolyForm-Noncommercial-1.0.0": "仅限非商业使用",
    "conflicting-CC-BY-vendor-terms": "许可声明互相冲突：默认不复制、不托管",
    "mixed-oss-icons+proprietary-app": "图标与应用许可不同，只用已标明的开源部分",
}


def combine_guide(
    style_tags: list[str],
    framework: str | None = None,
    item_ids: list[str] | None = None,
    items: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    tags = [t for t in style_tags if t in STYLE_PROFILES] or list(STYLE_PROFILES.keys())[:1]
    families = list(dict.fromkeys(STYLE_PROFILES[t]["family"] for t in tags))
    framework = framework or "未指定（默认单文件 HTML）"

    clash_warnings = []
    for i in range(len(families)):
        for j in range(i + 1, len(families)):
            key = (families[i], families[j])
            note = FAMILY_CLASH.get(key) or FAMILY_CLASH.get((families[j], families[i]))
            if note:
                clash_warnings.append(f"{families[i]} × {families[j]}：{note}")

    license_obligations = []
    if item_ids and items is not None:
        by_id = {i.get("id"): i for i in items}
        seen = set()
        for iid in item_ids:
            lic = ((by_id.get(iid) or {}).get("license") or "unspecified").strip()
            note = _LICENSE_NOTES.get(lic, _LICENSE_NOTES["unspecified"])
            if lic not in seen:
                seen.add(lic)
                license_obligations.append(
                    {"license": lic, "items": [iid], "obligation": note}
                )
            else:
                next(o for o in license_obligations if o["license"] == lic)["items"].append(iid)

    return {
        "style_tags": tags,
        "families": families,
        "framework": framework,
        "assembly_order": [
            "① 设计契约先行：先用 pattern design-contract（或你的 DESIGN.md）定下 token 事实来源（色板/字阶/圆角/间距/阴影比例）",
            "② tokens 落地：把契约变量写入 :root 命名空间（建议 --项目前缀-*），这是唯一事实来源",
            "③ 组件引入：从组件库复制需要的组件，把它们的硬编码色值/圆角全部替换为你的 token 引用（shadcn 系组件天然吃 CSS 变量，直接映射即可）",
            "④ 单效果叠加：effect 库（光束/光标/玻璃/数字滚动）按需引入，先写 prefers-reduced-motion 降级再加动效",
            "⑤ 微交互打磨：用 098 类工艺规则审查（高频操作弱动效、低频操作可带惊喜），最后统一检查对比度",
        ],
        "token_rules": [
            "唯一事实来源：tokens 只从一个基准取（设计契约或选定的 pattern），其余库的变量重命名并入你的命名空间，禁止两个库各自定义语义相同的变量（如两个 --accent）",
            "每个维度只保留一套刻度：圆角/间距/阴影各一个体系；引入新库时先对齐刻度再改样式",
            "改库不改构：'复制即拥有'的组件库遵守改样式不改 DOM 结构，升级时才能平滑 diff",
        ],
        "clash_warnings": clash_warnings or ["所选风格家族之间无明显冲突"],
        "license_obligations": license_obligations
        or [{"license": "-", "items": [], "obligation": "未指定条目；混用多个库时逐个核对其 license 字段并聚合义务"}],
        "mixing_examples": [
            "设计规范(DESIGN.md/002) + 组件库(071 电商) + 效果(060 过渡)：契约定 token → 组件换肤 → 状态过渡打磨 —— 典型安全组合",
            "物理光照(001 token) + 电商组件：光源向量统一后，商品卡的阴影全部由 token 派生 —— 效果统一的关键是只允许 token 派生阴影",
            "新粗野主义组件 + 暗色底：取粗野的描边/按压语法，色板换成暗色系 —— 见 clash 规则'只取单点元素'",
        ],
    }


def _presentation_template(description: str, page_type: str | None, directions: list[dict[str, Any]]) -> str:
    sections = []
    for d in directions:
        fn = f"version-{d['version'].lower()}.html"
        tags = " / ".join(d["style_tags"])
        sections.append(
            f'<a href="{fn}"><span class="cap"><b>版本 {d["version"]} · {d["name"]}</b>'
            f'{d["feel_line"]}<br><small>配色：{d["palette"]} ｜ 字体：{d["typography"]}</small></span></a>'
        )
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>风格提案 · {description[:24]}</title>
<style>
body{{margin:0;font-family:-apple-system,"PingFang SC",sans-serif;background:#111;color:#eee}}
header{{padding:32px 40px;border-bottom:1px solid #333}}
h1{{font-size:20px;margin:0 0 6px}} p{{color:#999;font-size:13px;margin:0}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;padding:24px 40px}}
a{{display:block;text-decoration:none;color:#ddd;background:#1b1b1b;border:1px solid #2a2a2a;border-radius:8px;padding:14px}}
a:hover{{border-color:#666}}
.cap{{display:block;line-height:1.7}} .cap b{{color:#fff;display:block;font-size:14px;margin-bottom:4px}}
small{{color:#888}}
footer{{padding:16px 40px;color:#666;font-size:12px;border-top:1px solid #222}}
</style></head><body>
<header><h1>风格提案 · {description[:40]}</h1>
<p>页面类型：{page_type or "未指定（按描述推断）"} ｜ 以下 {len(directions)} 个方向彼此来自不同风格家族。点入查看各版本实现。</p></header>
<div class="grid">
{chr(10).join(sections)}
</div>
<footer>各版本内容完全一致，仅风格层不同。版本 style_tags：{"；".join(d["version"] + "=" + tags for d, tags in [(d, " / ".join(d["style_tags"])) for d in directions])}</footer>
<!-- agent 使用说明：生成 version-a/b/c.html 后本对照页即可用；若能截图，在每个 <a> 内 <img> 前置缩略图 -->
</body></html>"""
