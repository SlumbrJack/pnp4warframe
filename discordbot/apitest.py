import requests

response = requests.get("https://api.warframestat.us/pc/invasions")
print(response.status_code)
print(response.json()[0]["attackerReward"]["asString"])
print(len(response.json()))


#up next:
#check occasionally for a new invasion?
    #save looping for snapshot.
# refactor so theres 1 command
#maybe delete user message as well to keep chat lean
#"snapshot" command that gives a quick overview of warframe 
    #Earth, Cetus, Cambrion Drift, Fortuna
    #Alerts
    #Events
    #Invasions (Invasion Rewards: Orokin, Exilus, weapon parts, EXLCUDE Mutagen mass, fieldron, etc)
    #daily reset time
    #
#auto suggest commands
#alerts
