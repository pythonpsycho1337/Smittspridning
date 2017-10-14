import os, sys, time, random, platform
from collections import deque

#Example call: py contamination.py 0.01 0.01 0 400 30 0,0;5,5;22,22;15,15

# States
HEALTHY = 1
SICK = 2
DEAD = 3
IMMUNE = 4

class Individual:
	def __init__(self, parrent,state):
		self.state = state											# Set initial States
		self.days = 0												# Variable to count sick days
		self.parrent = parrent										# Ref to parrent
	def __str__(self):
		if self.state == HEALTHY:									# Healthy -> H
			return "H"
		if self.state == SICK:										# Sick -> S
			return "S"
		if self.state == DEAD:										# Dead -> D
			return "D"
		if self.state == IMMUNE:									# Immune -> I
			return "I"

	# Try to be infected
	#
	# Input:
	# 	probabilty, the probabilty of being infected
	def tryToInfect(self,probabilty):
		if self.state == HEALTHY and random.random() < probabilty: 	#
			self.state = SICK									 	# Change state to SICK
			self.parrent.numOfSick += 1								# Increment number of sick
			return 1
		return 0
	# Try to Die
	#
	# Input:
	# 	probabilty, the probabilty of dying
	def tryToDie(self,probabilty):
		if self.state != SICK:										# Not infected
			return 0
		if random.random() < probabilty:							#
			self.state = DEAD										# Change state to DEAD
			self.parrent.numOfSick -= 1								# Decrement number of sick
			self.parrent.numOfDeath += 1							# Increment number of dead
			return 1
		return 0
	# Try to becomde immune
	#
	# Input:
	# 	minSickDays, minimum of sick days before the disease is cureable
	#	maxSickDays, maximun of days being sick, after that a individual will become immune
	def tryToBI(self, minSickDays, maxSickDays):
		if self.state != SICK:										# Disease not cureable yet
			return 0
		r = random.random()
		probabilty = self.immuneProbilty(minSickDays, maxSickDays, self.days)
		if r < probabilty:											# Chance of becoming immune
			self.state = IMMUNE										# Change state to IMMUNE
			self.parrent.numOfSick -= 1								# Decrement number of sick
			self.parrent.numOfImmune += 1							# Increment number of immune
			return 1
		return 0

	@staticmethod
	def immuneProbilty(minSickDays, maxSickDays, days):
		if days < minSickDays:										# Disease not cureable yet
			return 0
		if days < maxSickDays:
			return (1.0/(maxSickDays-minSickDays))
		return 1

	# Generate a list with all neighbours for a individual
	#
	# Input:
	# 	iCoordinates, Coordinates for one individual
	#	gridDimension, size of the grid
	# Return
	#	List of neighbours's coordinates (maximun size of list 8)
	@staticmethod
	def popleftNeighbours(iCoordinates,gridDimension):
		coords = []													# Initalize list for neighbours
		for x in range(iCoordinates[0]-1,iCoordinates[0]+2):
			if(x < 0 or x >= gridDimension):						# Skip ff coordinates is out of range
				continue
			for y in range(iCoordinates[1]-1,iCoordinates[1]+2):
				if(y < 0 or y >= gridDimension or x == iCoordinates[0] and y == iCoordinates[1]):
					continue
				coords.append([x,y])								# append coordinates
		return coords



class ContaminationSimulation:
	def __init__(self,params):
		if len(params) >= 5:
			self.day = 0											# Counter for days
			self.numOfSick = 0										# Counter for number of sick
			self.numOfDeath = 0										# Counter for number of dead
			self.numOfImmune = 0									# Counter for number of immune
			self.prevNumOfSick = 0
			self.prevNumOfDeath = 0
			self.prevNumOfImmune = 0

			self.queue = deque()									# Queue for sick individuals
			self.probCont = float(params[1]) 						# Probability of contamination
			self.probDeath = float(params[2]) 						# Probability of death
			self.minSickDays = int(params[3])						# Minimum days an Individual is sick
			self.maxSickDays = int(params[4]) 						# Maximun days an Individual is sick
			self.gridDimension = int(params[5] )					# The dimensions of the grid
			self.generateGrid(self.parseCoordinates(params[6])) 	# Generate the grid using the coordinates of the sick Individuals

		else:														# Error message for incorrect input
			out = "Usage: python contamination.py <Probability of contamination> <Probability of death> <Min Sick Days> <Max Sick Days> "
			out += "<Grid dimensions><Coordinates of sick Individuals>"
			out+="\nCoordinates are specified in the following format x,y;x2,y2 where x=0,y=0 is in the top left corner.\nExample: 1,2;1,3"
			print (out)
			sys.exit(0)
	# parseCoordinates
	# Parse coordinates from a string
	#	Cstr = CoordinatesString, string to parse
	# Return:
	# 	List of Parsed Coordinates
	@staticmethod
	def parseCoordinates(Cstr):								#Cstr = CoordinatesString
		coordinates = []
		Cstr = Cstr.split(";")										# Split string on ;
		for i in range(0,len(Cstr)):								# For every coord
			coord = Cstr[i].split(",")								# # Split string on ,
			coord[0] = int(coord[0])								# coord x
			coord[1] = int(coord[1])								# coord y
			coordinates.append(coord)								# Append to result
		return coordinates											# Return list of coordinates
	# generateGrid
	# Generate poplulation grid
	# Input:
	#	List of coordinates to sick individuals
	def generateGrid(self,sickCoord):
		self.Grid = []
		for row in range(0,self.gridDimension):						# Create grid with healthy Individuals as default
			self.Grid.append([])
			for col in range(0,self.gridDimension):
				self.Grid[row].append(Individual(self,HEALTHY))		# Create new HEALTHY individual
		for i in range(0,len(sickCoord)):							# Set sick Individuals
			self.Grid[sickCoord[i][0]][sickCoord[i][1]].state = SICK# Set individual to sick
			self.queue.append(sickCoord[i])							# Append to queue of sick individuals
			self.numOfSick += 1										# Increment number of sick

	# display
	# Display current state of the simulation
	def display(self):
		clearTerminal()												# Clear terminal window
		self.displayInfo()											# Display information about the simulation
		self.displayGrid()											# Display poplulation grid
		self.displayStats()											# Display current statistics

	# displayInfo
	# Display information about the simulation
	def displayInfo(self):
		print ("probCont="+str(self.probCont)+"\tprobDeath="+str(self.probDeath)+"\tminSickDays = "+str(self.minSickDays)+"\tmaxSickDays = "+str(self.maxSickDays) +"\tgridDimension="+str(self.gridDimension))

	# displayGrid
	# Display poplulation grid
	def displayGrid(self):
		out = ""
		for row in range(0,self.gridDimension):
			for col in range(0,self.gridDimension):
				out += " " + str(self.Grid[row][col])
			out +="\n"
		print(out)
		return out

	# displayStats
	# Display current statistics
	def displayStats(self):
		total = self.gridDimension * self.gridDimension				# Size of poplulation
		dead = (self.numOfDeath - self.prevNumOfDeath)				# Number of dead for a day
		immune = (self.numOfImmune - self.prevNumOfImmune)			# Number of immune for a day
		infected = (self.numOfSick - self.prevNumOfSick) 			# Number of infected for a day
		healthy = total - self.numOfSick - self.numOfDeath - self.numOfImmune	# Total number of healthy individual
		print ("Day: " +  str(self.day))
		print ("Total: \tHealthy " + str(healthy) + " \tSick " + str(self.numOfSick) + "\tDead " + str(self.numOfDeath) + "\tImmune " + str(self.numOfImmune))
		print ("Today: \tInfected " + str(self.infected) + "\tDead " + str(dead) + "\tImmune " + str(immune))
	# run
	#	Run simulation
	def run(self):
		self.infected = 0
		self.display()												# Display initial state

		#animate("Press enter to continue...\n")
		#raw_inappend()
		while len(self.queue) != 0:									# Run until no individuals are sick
			#time.sleep(0.5)
			self.nextQueue = deque()								# Create queue for next day
			while len(self.queue) != 0:								# One day, go trough every sick Individual
				self.playOneDay(self.queue.popleft())				# Run sick individual runtine
			self.queue = self.nextQueue
			self.day += 1											# Increment day
			self.display()											# Display current state
			self.prevNumOfSick = self.numOfSick						# Save previous values
			self.prevNumOfDeath = self.numOfDeath
			self.prevNumOfImmune = self.numOfImmune
			self.infected = 0

	# palyOneDay
	# Input:
	# 	individual, individual to simulate
	def playOneDay(self, individual):
		x = individual[0]
		y = individual[1]
		for cord in Individual.popleftNeighbours([x,y],self.gridDimension):
			if self.Grid[cord[0]][cord[1]].tryToInfect(self.probCont) == 1:
				self.nextQueue.append(cord)
				self.infected += 1

		self.Grid[x][y].tryToDie(self.probDeath)					# Try to die
		self.Grid[x][y].tryToBI(self.minSickDays, self.maxSickDays)	# Try to become immune
		if self.Grid[x][y].state == SICK:
			self.nextQueue.append(individual)
			self.Grid[x][y].days += 1

def animate(text):
	for i in range(0,len(text)):
		sys.stdout.write(text[i])
		time.sleep(0.01)

def clearTerminal():
	if sys.platform == "win32":
		os.system("cls")
	else:
		os.system("clear")

if __name__ == "__main__":
	random.seed(3)
	cS = ContaminationSimulation(sys.argv)
	cS.run()

import unittest

class TestStringMethods(unittest.TestCase):
	def test_infect(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,HEALTHY)
		self.assertTrue(individual.tryToInfect(1.0))

	def test_infect_zero(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,HEALTHY)
		self.assertFalse(individual.tryToInfect(0.0))

	def test_infect_dead(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,DEAD)
		self.assertFalse(individual.tryToInfect(1.0))

	def test_infect_immune(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,IMMUNE)
		self.assertFalse(individual.tryToInfect(1.0))

	def test_infect_sick(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,SICK)
		self.assertFalse(individual.tryToInfect(1.0))
	def test_BI(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,SICK)
		individual.days = 10
		self.assertTrue(individual.tryToBI(5,8))
	def test_BI_zero(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,SICK)
		individual.days = 0
		self.assertFalse(individual.tryToBI(5,8))
	def test_BI_dead(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,DEAD)
		individual.days = 10
		self.assertFalse(individual.tryToBI(5,8))
	def test_BI_healty(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,HEALTHY)
		individual.days = 10
		self.assertFalse(individual.tryToBI(5,8))
	def test_BI_immune(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,IMMUNE)
		individual.days = 10
		self.assertFalse(individual.tryToBI(5,8))
	def test_die(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,SICK)
		individual.days = 10
		self.assertTrue(individual.tryToDie(1.0))
	def test_die_zero(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,SICK)
		individual.days = 0
		self.assertFalse(individual.tryToDie(0.0))
	def test_die_dead(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,DEAD)
		individual.days = 10
		self.assertFalse(individual.tryToDie(1.0))
	def test_die_healty(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,HEALTHY)
		individual.days = 10
		self.assertFalse(individual.tryToDie(1.0))
	def test_die_immune(self):
		self.day = 0											# Counter for days
		self.numOfSick = 0										# Counter for number of sick
		self.numOfDeath = 0										# Counter for number of dead
		self.numOfImmune = 0									# Counter for number of immune
		individual = Individual(self,IMMUNE)
		individual.days = 10
		self.assertFalse(individual.tryToDie(1.0))
	def test_cs_sick(self):
		random.seed(3)
		cS = ContaminationSimulation([0.0,1.0, 0.0, 0, 5, 5, "1,2"])
		cS.run()
		self.assertEqual(cS.numOfImmune, 25)
	def test_cs_dead(self):
		random.seed(3)
		cS = ContaminationSimulation([0.0,1.0, 1.0, 0, 5, 5, "1,2"])
		cS.run()
		self.assertEqual(cS.numOfDeath, 25)
	def test_cs_grid(self):
		random.seed(3)
		cS = ContaminationSimulation([0.0,1.0, 1.0, 0, 5, 3, "1,2"])
		self.assertEqual(cS.displayGrid(), " H H H\n H H S\n H H H\n")
	def test_cs_grid2(self):
		random.seed(3)
		cS = ContaminationSimulation([0.0,1.0, 1.0, 0, 5, 3, "1,2;1,1"])
		self.assertEqual(cS.displayGrid(), " H H H\n H S S\n H H H\n")
	def test_get_neighbours(self):
		self.assertEqual(Individual.popleftNeighbours([0,0], 3), [[0,1],[1,0],[1,1]])
	def test_get_neighbours2(self):
		self.assertEqual(Individual.popleftNeighbours([1,1], 3), [[0,0],[0,1],[0,2],[1,0],[1,2],[2,0],[2,1],[2,2]])
	def test_get_neighbours3(self):
		self.assertEqual(Individual.popleftNeighbours([2,2], 3), [[1,1],[1,2],[2,1]])
	def test_immune_prob(self):
		self.assertEqual(Individual.immuneProbilty(2,4,0), 0)
	def test_immune_prob2(self):
		self.assertEqual(Individual.immuneProbilty(2,4,3), 0.5)
	def test_immune_prob3(self):
		self.assertEqual(Individual.immuneProbilty(0,100,3), 0.01)
	def test_immune_prob4(self):
		self.assertEqual(Individual.immuneProbilty(2,4,6), 1)
	def test_parse_coordinates(self):
		self.assertEqual(ContaminationSimulation.parseCoordinates("0,0;0,1;1,1"), [[0,0],[0,1],[1,1]])
	def test_parse_coordinates(self):
		self.assertEqual(ContaminationSimulation.parseCoordinates("0,0"), [[0,0]])




#if __name__ == '__main__':
#    unittest.main()
