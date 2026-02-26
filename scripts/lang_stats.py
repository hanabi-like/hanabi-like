import requests
import matplotlib.pyplot as plt
import os

USERNAME = os.environ["GITHUB_ACTOR"]
TOKEN = os.environ["GITHUB_TOKEN"]

headers = {
    "Authorization": f"token {TOKEN}"
}

# 获取所有仓库
repos = []
page = 1

while True:
    url = f"https://api.github.com/users/{USERNAME}/repos?per_page=100&page={page}"
    r = requests.get(url, headers=headers).json()

    if not r:
        break

    repos.extend(r)
    page += 1

language_totals = {}

# 汇总语言
for repo in repos:
    langs = requests.get(repo["languages_url"], headers=headers).json()

    for lang, size in langs.items():
        language_totals[lang] = language_totals.get(lang, 0) + size

# 过滤太小占比
language_totals = dict(
    sorted(language_totals.items(), key=lambda x: x[1], reverse=True)
)

# 生成图表
plt.figure(figsize=(6,6))
plt.pie(
    language_totals.values(),
    labels=language_totals.keys(),
    autopct='%1.1f%%'
)

plt.title("All Repository Language Distribution")

os.makedirs("assets", exist_ok=True)
plt.savefig("assets/languages.svg", format="svg")
