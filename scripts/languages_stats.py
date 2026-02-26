import requests
import os

# ========= 自动获取 GitHub 用户名 =========
USERNAME = os.environ.get("GITHUB_ACTOR")
if not USERNAME:
    USERNAME = input("请输入你的 GitHub 用户名：")

OUTPUT = "assets/languages.svg"
os.makedirs("assets", exist_ok=True)

# ========= 获取所有仓库 =========
language_bytes = {}
page = 1
while True:
    repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
    repos = requests.get(repos_url).json()
    if not repos:
        break
    for repo in repos:
        if repo["fork"]:
            continue
        langs = requests.get(repo["languages_url"]).json()
        for lang, size in langs.items():
            language_bytes[lang] = language_bytes.get(lang, 0) + size
    page += 1

# ========= 排序 & 总量 =========
sorted_langs = sorted(language_bytes.items(), key=lambda x: x[1], reverse=True)
total = sum(language_bytes.values())

# ========= SVG 参数 =========
svg_width = 100       # 内部坐标系 0-100
gap = 10
top_margin = 5
bar_start_x = 25
bar_max_width = 70    # 最大长度占 viewBox 宽度
text_font_size = 3

num_langs = len(sorted_langs)
svg_height = top_margin + gap * num_langs + 5

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

# ========= 绘制柱状图 =========
for lang, size in sorted_langs:
    percent = size / total
    bar_len = percent * bar_max_width
    percent_text = f"{percent*100:.1f}%"

    svg += f'<text x="1" y="{y}">{lang}</text>'
    svg += f'<rect x="{bar_start_x}" y="{y-4}" width="{bar_len}" height="{gap*0.8}" rx="1" fill="#58a6ff"/>'
    svg += f'<text x="{bar_start_x + bar_len + 1}" y="{y}">{percent_text}</text>'

    y += gap

svg += "</svg>"

# ========= 写入文件 =========
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print(f"SVG generated successfully for user {USERNAME}!")
