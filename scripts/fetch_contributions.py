"""Paso 4 (lo corre GitHub Actions todos los días): baja tu calendario público de
contribuciones (sin token) -> data/contributions.json"""
import json, os, re
import requests
from bs4 import BeautifulSoup
from common import USERNAME, DATA


def main():
    url = f"https://github.com/users/{USERNAME}/contributions"
    html = requests.get(url, timeout=30, headers={"User-Agent": "profile-readme-bot"}).text
    soup = BeautifulSoup(html, "html.parser")
    tips = {}
    for t in soup.select("tool-tip"):
        m = re.match(r"\s*(\d+|No) contribution", t.get_text())
        if t.get("for") and m:
            tips[t["for"]] = 0 if m.group(1) == "No" else int(m.group(1))
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        days.append({"date": td["data-date"], "level": int(td.get("data-level", 0)), "count": tips.get(td.get("id"), None)})
    days.sort(key=lambda d: d["date"])
    total = None
    h = soup.find(id="js-contribution-activity-description") or soup.find("h2")
    if h:
        m = re.search(r"([\d,.]+)\s+contribution", h.get_text())
        if m:
            total = int(re.sub(r"[,.]", "", m.group(1)))
    if total is None:
        total = sum(d["count"] or 0 for d in days)
    if not days:
        raise SystemExit("No se encontraron días: ¿cambió el HTML de GitHub?")
    with open(os.path.join(DATA, "contributions.json"), "w") as f:
        json.dump({"username": USERNAME, "total": total, "days": days}, f, indent=1)
    print(f"OK -> {len(days)} días, {total} contribuciones")


if __name__ == "__main__":
    main()
