# the import allows Microsoft Excel files to be read by python
import pandas as pd

class City():
    def __init__(self, name, state, long, lat, adjacent):
        #assumes name and state are strings, long and lat are numbers formated 12/34/56 and 123/45/67 respectively, and adjacent is a string split by word1/word2
        self.name = name
        self.state = state
        # longitude and latitude are split into a list in order of degrees, minutes, and seconds
        self.long = long.split("/")
        self.lat = lat.split("/")
        # travelState includes adjacent states and the state the City is in
        self.travelState = adjacent.split("/")
        self.travelState.append(self.state)
        self.travelCity = {}
        
    def __str__(self):
        if self.name == "Washington DC":
            # Washington DC would be printed as "Washington DC, Washington DC, so an exception is made to prevent redundancy
            return "Washington DC"
        else:
            return self.name + ", " + self.state
        
class Map():
    def __init__(self):
        # creates list of strings and a dict of Cities for each string
        self.states = []
        self.cities = {}
        
    def addCity(self, name, state, long, lat, adjacent):
        # adds City to self.cities to make referring to adjacent Cities easier
        newCity = City(name, state, long, lat, adjacent)
        if state not in self.states:
            # makes sure there are only 49 states max in self.states
            # Hawaii and Alaska are excluded because they aren't directly next to any states and Washington DC counts as a state so it can be traveled to correctly
            self.states.append(state)
            self.cities[state] = [newCity]
        else:
            self.cities[state].append(newCity)
            
    def createMap(self):
        # creates weighted edges between the Cities
        if len(self.states) == 0:
            pass
        else:
            # checks for each City which states are adjacent and adds weighted edges for each City in the state
            for state1 in self.states:
                for city1 in self.cities[state1]:
                    for state2 in self.states:
                        if state2 in city1.travelState:
                            for city2 in self.cities[state2]:
                                if not city2.name == city1.name:
                                    # converts DMS units into miles to find distance
                                    latMiles1 = (int(city1.long[0]) + int(city1.long[1])/60 + int(city1.long[2])/3600) * 54.6
                                    latMiles2 = (int(city2.long[0]) + int(city2.long[1])/60 + int(city2.long[2])/3600) * 54.6
                                    longMiles1 = (int(city1.lat[0]) + int(city1.lat[1])/60 + int(city1.lat[2])/3600) * 54.6
                                    longMiles2 = (int(city2.lat[0]) + int(city2.lat[1])/60 + int(city2.lat[2])/3600) * 54.6
                                    distance = ((latMiles1 - latMiles2) ** 2 + (longMiles1 - longMiles2) ** 2) ** (1/2)
                                    city1.travelCity[city2] = distance
      
    def dijekstras(self, city, cityDict, path):
        # uses Dijekstra's algorithm to find the shortest path from the City to each of the Cities in self.cities
        # the inputted City is the current location on the shortest path
        tempPathDict = {}
        for tempCity in city.travelCity:
            # tempCity is one of the Cities adjacent to the inputted City
            tempPath = []
            for pathCity in path:
                tempPath.append(pathCity)
            tempPath.append(tempCity)
            tempPathDict[tempCity] = tempPath
            # value is the current shortest path from the inputted City and city1 from self.shortestPath
            value = cityDict[city][0]
            if city.travelCity[tempCity] + value < cityDict[tempCity][0]:
                # sets the shortest path to be the inputted path with the tempCity at the end
                # recursively runs until the shortest path from city1 to all cities in self.cities is found
                cityDict[tempCity][0] = city.travelCity[tempCity] + value
                cityDict[tempCity][1] = tempPath
                self.dijekstras(tempCity, cityDict, tempPath)
    
    def shortestPath(self, city1, city2):
        # assumes city1 and city2 are strings of Cities in self.cities
        cityDict = {}
        for state in self.states:
            for city in self.cities[state]:
                if city.name == city1:
                    # makes the path from city1 to itself 0 miles and finds the node with the same name
                    city1Node = city
                    cityDict[city] = [0, [city1Node]]
                else:
                    # sets the value as 9000000 since it is significantly larger than the distance from California to Maine
                    cityDict[city] = [9000000, []]
                    if city.name == city2:
                        # finds the node with the name of city2
                        city2Node = city
        # sets path so a list of the Cities traveled in the shortest path can be printed later
        path = [city1Node]
        self.dijekstras(city1Node, cityDict, path)
        # returns a list of length 2 and the starting City
        # cityDict[city2Node][0] is the length of the shortest path in miles
        # cityDict[city2Node][1] is the Cities traveled in order in the shortest path
        return cityDict[city2Node]
        
def main():
    infile = pd.read_excel('City Information.xlsx', 'Sheet1')
    mainMap = Map()
    
    # creates 5 lists so the information can be easy stored and turned into Cities
    cityList = []
    stateList = []
    longList = []
    latList = []
    adjList = []
    
    for city in infile["Name of City"]:
         cityList.append(city)
    for state in infile["State"]:
        stateList.append(state)
    for long in infile["Longitude"]:
        longList.append(long)
    for lat in infile["Latitude"]:
        latList.append(lat)
    for adj in infile["Adjacent States"]:
        adjList.append(adj)
        
    for i in range(len(cityList)):
        # turns all of the information into Cities
        city = cityList[i]
        state = stateList[i]
        long = longList[i]
        lat = latList[i]
        adj = adjList[i]
        mainMap.addCity(city, state, long, lat, adj)
        
    mainMap.createMap()
    
    print("This program uses Dijekstra's algorithm to travel")
    print("from one city to another using adjacent states.")
    print("The cities that will work are in the listed in the")
    print("Microsoft Word document. Just use the city name and")
    print("not the state.")
    # expects strings of two cities
    # the input is case sensitive and requires spaces when applicable
    inputStart = input("Choose the starting city: ")
    inputEnd = input("Choose the ending city: ")
    
    path = mainMap.shortestPath(inputStart, inputEnd)
    
    print("\n\nThe shortest path between " + inputStart + " and " + inputEnd + " is " + str(round(path[0], 2)) + " miles\n")
    print("The cities traveled in the path are: \n")
    for i in range(len(path[1])):
        if path[1][i].name == inputStart:
            print(str(path[1][i]) + " 0 miles from itself\n")
        else:
            # prints the City and the distance traveled from the previous City to the current City
            print(str(path[1][i]) + " " + str(round(path[1][i].travelCity[path[1][i-1]], 2)) + " miles from " + str(path[1][i-1]) + "\n")
        
main()
    
    