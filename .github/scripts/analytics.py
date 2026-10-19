import os
import json
import urllib.request
import urllib.parse
from collections import defaultdict


USERNAME = "asimmudassar541-ship-it"
TOKEN = os.environ.get("GITHUB_API_TOKEN")
API = "https://api.github.com"


def github_api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USERNAME,
    }

    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"

    request = urllib.request.Request(url, headers=headers)

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode())


def get_all_repositories():
    repositories = []
    page = 1

    while True:
        url = (
            f"{API}/user/repos"
            f"?per_page=100"
            f"&page={page}"
            f"&visibility=all"
            f"&affiliation=owner"
            f"&sort=updated"
        )

        data = github_api(url)

        if not data:
            break

        repositories.extend(data)

        if len(data) < 100:
            break

        page += 1

    return repositories


def get_commit_count(owner, repo):
    total = 0
    page = 1

    while True:
        query = urllib.parse.urlencode({
            "author": USERNAME,
            "per_page": 100,
            "page": page,
        })

        url = f"{API}/repos/{owner}/{repo}/commits?{query}"

        try:
            data = github_api(url)
        except Exception as error:
            print(f"Could not read commits from {repo}: {error}")
            return total

        if not data:
            break

        total += len(data)

        if len(data) < 100:
            break

        page += 1

    return total


def get_repository_languages(owner, repo):
    url = f"{API}/repos/{owner}/{repo}/languages"

    try:
        return github_api(url)
    except Exception as error:
        print(f"Could not read languages from {repo}: {error}")
        return {}


def create_svg(stats, languages):
    width = 900
    height = 330

    language_items = sorted(
        languages.items(),
        key=lambda item: item[1],
        reverse=True
    )[:8]

    total_bytes = sum(value for _, value in language_items)

    if total_bytes == 0:
        language_items = [("No data", 1)]
        total_bytes = 1

    language_colors = {
        "JavaScript": "#F7DF1E",
        "TypeScript": "#3178C6",
        "HTML": "#E34F26",
        "CSS": "#1572B6",
        "Python": "#3776AB",
        "Java": "#ED8B00",
        "C": "#A8B9CC",
        "C++": "#00599C",
        "C#": "#239120",
        "PHP": "#777BB4",
        "Dart": "#0175C2",
        "Kotlin": "#7F52FF",
        "Swift": "#F05138",
        "Go": "#00ADD8",
        "Rust": "#DEA584",
        "Shell": "#89E051",
        "Vue": "#41B883",
        "Jupyter Notebook": "#DA5B0B",
    }

    bar_x = 470
    bar_y = 105
    bar_width = 340
    bar_height = 18

    segments = []
    current_x = bar_x

    for language, value in language_items:
        percentage = (value / total_bytes) * 100
        segment_width = bar_width * (percentage / 100)

        color = language_colors.get(language, "#8B949E")

        segments.append(
            f'<rect x="{current_x:.2f}" '
            f'y="{bar_y}" '
            f'width="{segment_width:.2f}" '
            f'height="{bar_height}" '
            f'fill="{color}" />'
        )

        current_x += segment_width

    language_rows = []
    row_y = 155

    for language, value in language_items[:5]:
        percentage = (value / total_bytes) * 100
        color = language_colors.get(language, "#8B949E")

        language_rows.append(
            f'''
            <circle cx="480" cy="{row_y}" r="5" fill="{color}" />

            <text x="495"
                  y="{row_y + 5}"
                  fill="#C9D1D9"
                  font-size="14"
                  font-family="Arial, sans-serif">
                {language}
            </text>

            <text x="820"
                  y="{row_y + 5}"
                  fill="#C9D1D9"
                  font-size="14"
                  text-anchor="end"
                  font-family="Arial, sans-serif">
                {percentage:.2f}%
            </text>
            '''
        )

        row_y += 27

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg"
    width="{width}"
    height="{height}"
    viewBox="0 0 {width} {height}">

    <rect width="100%"
          height="100%"
          rx="18"
          fill="#0D1117"
          stroke="#30363D"
          stroke-width="1"/>

    <text x="35"
          y="45"
          fill="#00E5FF"
          font-size="22"
          font-weight="bold"
          font-family="Arial, sans-serif">
        ASIM MUDASAR'S GITHUB ANALYTICS
    </text>

    <text x="35"
          y="72"
          fill="#8B949E"
          font-size="13"
          font-family="Arial, sans-serif">
        Real GitHub repository data • All-time commit history
    </text>

    <line x1="35"
          y1="90"
          x2="865"
          y2="90"
          stroke="#30363D"/>

    <text x="45"
          y="130"
          fill="#C9D1D9"
          font-size="14"
          font-weight="bold"
          font-family="Arial, sans-serif">
        ALL-TIME COMMITS
    </text>

    <text x="45"
          y="180"
          fill="#00E5FF"
          font-size="38"
          font-weight="bold"
          font-family="Arial, sans-serif">
        {stats["commits"]}
    </text>

    <text x="45"
          y="205"
          fill="#8B949E"
          font-size="13"
          font-family="Arial, sans-serif">
        commits across owned repositories
    </text>

    <text x="45"
          y="245"
          fill="#C9D1D9"
          font-size="14"
          font-weight="bold"
          font-family="Arial, sans-serif">
        REPOSITORIES
    </text>

    <text x="45"
          y="282"
          fill="#7C3AED"
          font-size="30"
          font-weight="bold"
          font-family="Arial, sans-serif">
        {stats["repositories"]}
    </text>

    <text x="150"
          y="282"
          fill="#8B949E"
          font-size="13"
          font-family="Arial, sans-serif">
        owned repositories
    </text>

    <text x="470"
          y="80"
          fill="#C9D1D9"
          font-size="14"
          font-weight="bold"
          font-family="Arial, sans-serif">
        MOST USED LANGUAGES
    </text>

    {''.join(segments)}

    {''.join(language_rows)}

    <text x="865"
          y="305"
          fill="#484F58"
          font-size="10"
          text-anchor="end"
          font-family="Arial, sans-serif">
        Updated automatically by GitHub Actions
    </text>

    </svg>'''

    return svg


def main():
    os.makedirs("profile", exist_ok=True)

    print("Fetching GitHub repositories...")

    repositories = get_all_repositories()

    owned_repositories = [
        repo
        for repo in repositories
        if not repo.get("fork", False)
    ]

    print(f"Found {len(owned_repositories)} owned repositories.")

    total_commits = 0
    language_totals = defaultdict(int)

    for repo in owned_repositories:
        owner = repo["owner"]["login"]
        name = repo["name"]

        print(f"Processing: {name}")

        total_commits += get_commit_count(owner, name)

        languages = get_repository_languages(owner, name)

        for language, byte_count in languages.items():
            language_totals[language] += byte_count

    stats = {
        "commits": total_commits,
        "repositories": len(owned_repositories),
    }

    print(f"Total commits: {total_commits}")
    print(f"Total repositories: {len(owned_repositories)}")

    svg = create_svg(stats, language_totals)

    with open(
        "profile/analytics.svg",
        "w",
        encoding="utf-8"
    ) as file:
        file.write(svg)

    print("Analytics generated successfully!")


if __name__ == "__main__":
    main()
