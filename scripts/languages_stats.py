import requests
import os

USERNAME = os.environ["GITHUB_ACTOR"]
OUTPUT = "assets/languages.svg"

repos_url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100"

repos = requests.get(repos_url).json()

language_bytes = {}

# 获取所有仓库语言数据
for repo in repos:
    if repo["fork"]:
        continue

    lang_url = repo["languages_url"]
    langs = requests.get(lang_url).json()

    for lang, size in langs.items():
        language_bytes[lang] = language_bytes.get(lang, 0) + size

# 排序
sorted_langs = sorted(language_bytes.items(),
                      key=lambda x: x[1],
                      reverse=True)

total = sum(language_bytes.values())

# ===== SVG 参数 =====
bar_max_width = 400
bar_height = 18
gap = 28
left_margin = 140

svg_height = gap * len(sorted_langs) + 40

svg = f'''
<svg width="700" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
<style>
    text {{
        font-family: Arial, sans-serif;
        font-size: 14px;
        fill: #c9d1d9;
    }}
</style>
'''

y = 30

for lang, size in sorted_langs:
    percent = size / total
    bar_width = percent * bar_max_width
    percent_text = f"{percent*100:.1f}%"

    svg += f'''
    <text x="10" y="{y}">{lang}</text>

    <rect x="{left_margin}" y="{y-14}"
          width="{bar_width}"
          height="{bar_height}"
          rx="6"
          fill="#58a6ff"/>

    <text x="{left_margin + bar_width + 10}" y="{y}">
        {percent_text}
    </text>
    '''

    y += gap

svg += "</svg>"

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write(svg)

print("SVG generated!")
