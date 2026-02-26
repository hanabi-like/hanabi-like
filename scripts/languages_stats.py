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

# ========= 最大语言字节数 =========
max_size = sorted_langs[0][1]

# ===== SVG 参数 =====
bar_max_width = 500
bar_height = 20
gap = 30
left_margin = 150
top_margin = 20
svg_width = bar_max_width + left_margin * 2
svg_height = gap * len(sorted_langs) + top_margin * 2

svg = f'''
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
<style>
    text {{
        font-family: Arial, sans-serif;
        font-size: 15px;
        fill: #c9d1d9;
    }}
</style>
'''

y = top_margin + bar_height

for lang, size in sorted_langs:
    percent = size / total
    bar_width = size / max_size * bar_max_width
    percent_text = f"{percent*100:.1f}%"

    svg += f'''
    <text x="20" y="{y}">{lang}</text>

    <rect x="{left_margin}" y="{y - bar_height}"
          width="{bar_width}"
          height="{bar_height}"
          rx="5"
          fill="#58a6ff"/>

    <text x="{left_margin + bar_width + 20}" y="{y}">
        {percent_text}
    </text>
    '''

    y += gap

svg += "</svg>"

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print("SVG generated!")
