from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import time

def get_soup(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    driver.get(url)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup, driver

def get_roster(url):
    soup, driver = get_soup(url)
    roster = []
    
    coach_section = soup.find("table", class_="coach-table")
    if coach_section:
        try:
            coach_name = coach_section.find("div", class_="text-ellipsis")
            coach_img = coach_section.find("img", class_="playerBox-bodyshot")
            
            if coach_name and coach_img:
                roster.append({
                    "name": coach_name.text.strip(),
                    "role": "coach",
                    "img": coach_img.get('src', '')
                })
        except Exception as e:
            print(f"Error parsing coach: {e}")
    
    players_section = soup.find("table", class_="players-table")
    if players_section:
        tbody = players_section.find("tbody")
        if tbody:
            for player in tbody.find_all("tr"):
                try:
                    first_cell = player.find("td", class_="playersBox-first-cell")
                    if first_cell:
                        name = first_cell.find("div", class_="text-ellipsis")
                        img = first_cell.find("img", class_="playerBox-bodyshot")
                        status = player.find("div", class_="player-status")
                        
                        if all([name, img, status]):
                            roster.append({
                                "name": name.text.strip(),
                                "role": "player",
                                "img": img.get('src', ''),
                                "status": status.text.strip()
                            })
                except Exception as e:
                    print(f"Error parsing player: {e}")
    
    driver.quit()
    return roster

def get_events(url):
    soup, driver = get_soup(url)
    events = []
    
    events_section = soup.find("div", class_="upcoming-events-holder")
    if events_section:
        for event in events_section.find_all("div", class_="content"):
            try:
                name = event.find("div", class_="eventbox-eventname")
                date_container = event.find("div", class_="eventbox-date")
                
                if name and date_container:
                    start_date = date_container.find("span")
                    end_date = None
                    
                    for date in date_container.find_all("span"):
                        if date.find("span"):
                            end_date = date.find("span")
                            break
                    
                    event_data = {
                        "name": name.text.strip(),
                        "start_date": start_date.text.strip() if start_date else "",
                        "end_date": end_date.text.strip() if end_date else ""
                    }
                    events.append(event_data)
            except Exception as e:
                print(f"Error parsing event: {e}")
    
    driver.quit()
    return events

def get_upcoming_matches(url):
    soup, driver = get_soup(url)
    matches = []
    
    try:
        h2 = soup.find('h2', string=lambda text: text and 'Upcoming matches for FURIA' in text)
        if h2:
            matches_section = h2.find_next()
            if matches_section:
                for match in matches_section.find_all("tr", class_="team-row"):
                    try:
                        team1 = match.find("a", class_="team-1")
                        team2 = match.find("a", class_="team-2")
                        team_logos = match.find_all("img", class_="team-logo")
                        date_cell = match.find("td", class_="date-cell")
                        
                        if all([team1, team2, len(team_logos) >= 2, date_cell]):
                            matches.append({
                                "team1": team1.text.strip(),
                                "team2": team2.text.strip(),
                                "logo1": team_logos[0].get('src', ''),
                                "logo2": team_logos[1].get('src', ''),
                                "date": date_cell.find("span").text.strip() if date_cell.find("span") else ""
                            })
                    except Exception as e:
                        print(f"Error parsing upcoming match: {e}")
    except Exception as e:
        print(f"Error finding upcoming matches section: {e}")
    
    driver.quit()
    return matches if matches else "No matches"

def get_recent_matches(url):
    soup, driver = get_soup(url)
    matches = []
    
    try:
        h2 = soup.find('h2', string=lambda text: text and 'Recent results for FURIA' in text)
        if h2:
            matches_section = h2.find_next()
            if matches_section:
                for match in matches_section.find_all("tr", class_="team-row"):
                    try:
                        team1 = match.find("a", class_="team-1")
                        team2 = match.find("a", class_="team-2")
                        team_logos = match.find_all("img", class_="team-logo")
                        scores = match.find_all("span", class_="score")
                        date_cell = match.find("td", class_="date-cell")
                        
                        if all([team1, team2, len(team_logos) >= 2, len(scores) >= 2, date_cell]):
                            matches.append({
                                "team1": team1.text.strip(),
                                "team2": team2.text.strip(),
                                "logo1": team_logos[0].get('src', ''),
                                "logo2": team_logos[1].get('src', ''),
                                "score1": scores[0].text.strip(),
                                "score2": scores[1].text.strip(),
                                "date": date_cell.find("span").text.strip() if date_cell.find("span") else ""
                            })
                    except Exception as e:
                        print(f"Error parsing recent match: {e}")
    except Exception as e:
        print(f"Error finding recent matches section: {e}")
    
    driver.quit()
    return matches if matches else "No matches"

if __name__ == "__main__":
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