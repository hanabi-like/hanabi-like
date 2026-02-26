import requests
import os

# ========= 自动获取 GitHub 用户名 =========
USERNAME = os.environ.get("GITHUB_ACTOR")
if not USERNAME:
    USERNAME = input("请输入你的 GitHub 用户名：")

OUTPUT = "assets/languages.svg"
os.makedirs("assets", exist_ok=True)

# ========= 获取所有仓库语言（分页） =========
language_bytes = {}
page = 1
while True:
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
    repos = requests.get(repos_url).json()
    if not repos:
        break
    for repo in repos:
        if repo.get("fork"):
            continue
        langs = requests.get(repo["languages_url"]).json()
        for lang, size in langs.items():
            language_bytes[lang] = language_bytes.get(lang, 0) + size
    page += 1

# ========= 排序 & 总量 =========
sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)
total = sum(language_bytes.values())

if not sorted_langs:
    print("没有找到语言数据！")
    exit(1)

# ========= SVG 参数 =========
svg_width = 100       # 内部坐标系横向范围 0-100
gap = 10              # 每行间距
top_margin = 5
bar_start_x = 25      # 横向柱状图起点
bar_max_width = 70    # 最大柱状图长度占 viewBox 横向百分比
num_langs = len(sorted_langs)
svg_height = top_margin + gap * num_langs + 5  # 自动顶/底留白

# 字体和柱状图高度自适应
bar_height = gap * 0.8                # 柱状图占行高 80%
text_font_size = bar_height * 0.6     # 字体占柱状图高 60%

# ========= SVG 开始 =========
svg = f'''<svg viewBox="0 0 {svg_width} {svg_height}" width="100%" preserveAspectRatio="xMinYMin meet" xmlns="http://www.w3.org/2000/svg">
<style>
text {{
    font-family: Arial, sans-serif;
    font-size: {text_font_size};
    fill: #c9d1d9;
}}
</style>
'''

y = top_margin + gap / 2

# 最大语言字节数，用于比例缩放
max_size = sorted_langs[0][1]

# ========= 绘制柱状图 =========
for lang, size in sorted_langs:
    percent = size / total
    # 最大语言占满 bar_max_width，其余按比例
    bar_len = size / max_size * bar_max_width
    percent_text = f"{percent*100:.1f}%"

    # 语言名称
    svg += f'<text x="1" y="{y}">{lang}</text>'
    # 横向柱状图
    svg += f'<rect x="{bar_start_x}" y="{y - bar_height / 2}" width="{bar_len}" height="{bar_height}" rx="1" fill="#58a6ff"/>'
    # 百分比文字
    svg += f'<text x="{bar_start_x + bar_len + 1}" y="{y}">{percent_text}</text>'

    y += gap

svg += "</svg>"

# ========= 写入文件 =========
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"SVG generated successfully for user {USERNAME}!")
