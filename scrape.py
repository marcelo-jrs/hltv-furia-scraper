from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

def get_soup(url):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--remote-debugging-port=9222")
    
    # Automatic driver management
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    time.sleep(3)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup, driver


def get_roster(url):
    try:
        soup, driver = get_soup(url)
        roster = []
        coach_section = soup.find("div", class_="teamCoach-wrapper")
        coach_name = coach_section.find("div", class_="text-ellipsis").text.strip()
        coach_img = coach_section.find("img", class_="playerBox-bodyshot")['src']
        roster.append({
            "name": coach_name,
            "role": "coach",
            "img": coach_img
        })
        players_section = soup.find("table", class_="players-table")
        for player in players_section.find("tbody").find_all("tr"):
            first_cell = player.find("td", class_="playersBox-first-cell")
            name = first_cell.find("div", class_="text-ellipsis").text.strip()
            img = first_cell.find("img", class_="playerBox-bodyshot")['src']
            status = player.find("div", class_="player-status").text.strip()
            roster.append({
                "name": name,
                "role": "player",
                "img": img,
                "status": status
            })
    finally:
        driver.quit()
    return roster

def get_events(url):
    try:
        soup, driver = get_soup(url)
        events = []
        events_section = soup.find("div", class_="upcoming-events-holder")
        for event in events_section.find_all("div", class_="content"):
            name = event.find("div", class_="eventbox-eventname").text.strip()
            date_container = event.find("div", class_="eventbox-date")
            start_date = date_container.find("span").text.strip()
            for date in date_container.find_all("span"):
                if date.find("span"):
                    end_date = date.find("span").text.strip()
            events.append({
                "name": name,
                "start_date": start_date,
                "end_date": end_date
            })
    finally:            
        driver.quit()
    return events

def get_upcoming_matches(url):
    try:
        soup, driver = get_soup(url)
        matches = []
        h2 = soup.find('h2', string='Upcoming matches for FURIA')
        if h2:
            matches_section = h2.find_next()
        for match in matches_section.find_all("tr", class_="team-row"):
            team1_name = match.find("a", class_="team-1").text.strip()
            team2_name = match.find("a", class_="team-2").text.strip()
            team_logos = match.find_all("img", class_="team-logo")
            logo1 = team_logos[0]['src']
            logo2 = team_logos[1]['src']
            date = match.find("td", class_="date-cell").find("span").text.strip()
            matches.append({
                "team1": team1_name,
                "team2": team2_name,
                "logo1": logo1,
                "logo2": logo2,
                "date": date
            })
    finally:
        driver.quit()
    return matches

def get_recent_matches(url):
    try:
        soup, driver = get_soup(url)
        matches = []
        h2 = soup.find('h2', string='Recent results for FURIA')
        if h2:
            matches_section = h2.find_next()
        for match in matches_section.find_all("tr", class_="team-row"):
            team1_name = match.find("a", class_="team-1").text.strip()
            team2_name = match.find("a", class_="team-2").text.strip()
            team_logos = match.find_all("img", class_="team-logo")
            logo1 = team_logos[0]['src']
            logo2 = team_logos[1]['src']
            scores = match.find_all("span", class_="score")
            score1 = scores[0].text.strip()
            score2 = scores[1].text.strip()
            date = match.find("td", class_="date-cell").find("span").text.strip()
            matches.append({
                "team1": team1_name,
                "team2": team2_name,
                "logo1": logo1,
                "logo2": logo2,
                "score1": score1,
                "score2": score2,
                "date": date
            })
    finally:
        driver.quit()
    return matches

roster_url = "https://www.hltv.org/team/8297/furia#tab-rosterBox"
matches_url = "https://www.hltv.org/team/8297/furia#tab-matchesBox"
events_url = "https://www.hltv.org/team/8297/furia#tab-eventsBox"

data = {
    "roster": get_roster(roster_url),
    "recent_matches": get_recent_matches(matches_url),
    "upcoming_matches": get_upcoming_matches(matches_url),
    "events": get_events(events_url)
}

with open("data.json", "w") as f:
    json.dump(data, f, indent=2)