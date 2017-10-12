import os, sys, time, random, platform
from collections import deque

#Example call: py contamination.py 0.01 0.01 0 400 30 0,0;5,5;22,22;15,15

HEALTHY = 1
SICK = 2
DEAD = 3
IMMUNE = 4

class Individual:
	def __init__(self, parrent,state):
		self.state = state #-2=Immune -1=Dead 0=healthy 0<x = Ill where x is days left as ill
		self.days = 0
		self.parrent = parrent
	def __str__(self):
		if self.state == HEALTHY:
			return "H"
		if self.state == SICK:
			return "S"
		if self.state == DEAD:
			return "D"
		if self.state == IMMUNE:
			return "I"
	def tryToInfect(self,probabilty):
		if self.state == HEALTHY and random.random() < probabilty: #Infected
			self.state = SICK
			self.parrent.numOfSick += 1
			return 1
	def tryToDie(self,probabilty, minSickDays):
		if self.days <= minSickDays:
			return 0
		if self.state != SICK:#Not infected
			return 0
		r = random.random()
		if r < probabilty:
			self.state = DEAD
			self.parrent.numOfSick -= 1
			self.parrent.numOfDeath += 1
			return 1
	def tryToBI(self, minSickDays, maxSickDays):#Try to become immune
		if self.state != SICK or self.days <= minSickDays:
			return 0

		if random.random() < (1/(maxSickDays-minSickDays)) or self.days > maxSickDays:
			self.state = IMMUNE
			self.parrent.numOfSick -= 1
			self.parrent.numOfImmune += 1
			return 1
		return 0
	@staticmethod
	def popleftNeighbours(iCoordinates,gridDimension):
		coords = []
		for x in range(iCoordinates[0]-1,iCoordinates[0]+2):
			if(x < 0 or x >= gridDimension):
				continue
			for y in range(iCoordinates[1]-1,iCoordinates[1]+2):
				if(y < 0 or y >= gridDimension or x == iCoordinates[0] and y == iCoordinates[1]):
					continue
				coords.append([x,y])
		return coords
class ContaminationSimulation:
	def __init__(self,params):
		if len(params) >= 4:
			self.day = 0
			self.numOfSick = 0
			self.numOfDeath = 0
			self.numOfImmune = 0
			self.prevNumOfSick = 0
			self.prevNumOfDeath = 0
			self.prevNumOfImmune = 0
			self.queue = deque()
			self.probCont = float(params[1]) #Probability of contamination
			self.probDeath = float(params[2]) #Probability of death
			self.minSickDays = int(params[3])
			self.maxSickDays = int(params[4]) #How long an Individual is sick
			self.gridDimension = int(params[5] )#The dimensions of the grid
			self.generateGrid(self.parseCoordinates(params[6])) #Generate the grid using the coordinates of the sick Individuals
		else:
			out = "Usage: python contamination.py <Probability of contamination> <Probability of death> <Min Sick Days> <Max Sick Days> "
			out += "<Grid dimensions><Coordinates of sick Individuals>"
			out+="\nCoordinates are specified in the following format x,y;x2,y2 where x=0,y=0 is in the top left corner.\nExample: 1,2;1,3"
			print (out)
			sys.exit(0)
	def parseCoordinates(self,Cstr):#Cstr = CoordinatesString
		coordinates = []
		Cstr = Cstr.split(";")
		for i in range(0,len(Cstr)):
			coord = Cstr[i].split(",")
			coord[0] = int(coord[0])
			coord[1] = int(coord[1])
			coordinates.append(coord)
		return coordinates

	def generateGrid(self,sickCoord):
		self.Grid = []
		for row in range(0,self.gridDimension):#Create grid with healthy Individuals as default
			self.Grid.append([])
			for col in range(0,self.gridDimension):
				self.Grid[row].append(Individual(self,HEALTHY))
		for i in range(0,len(sickCoord)):#Set sick Individuals
			self.Grid[sickCoord[i][0]][sickCoord[i][1]].state = SICK
			self.queue.append(sickCoord[i])
			self.numOfSick += 1

	def display(self):
		clearTerminal()
		self.displayInfo()
		self.displayGrid()
		self.displayStats()
	def displayInfo(self):
		print ("probCont="+str(self.probCont)+"\tprobDeath="+str(self.probDeath)+"\tminSickDays = "+str(self.minSickDays)+"\tmaxSickDays = "+str(self.maxSickDays) +"\tgridDimension="+str(self.gridDimension))

	def displayGrid(self):
		out = ""
		for row in range(0,self.gridDimension):
			for col in range(0,self.gridDimension):
				out += " " + str(self.Grid[row][col])
			out +="\n"
		print(out)
	def displayStats(self):
		total = self.gridDimension * self.gridDimension
		dead = (self.numOfDeath - self.prevNumOfDeath)
		immune = (self.numOfImmune - self.prevNumOfImmune)
		infected = (self.numOfSick - self.prevNumOfSick) #+ dead + immune
		healthy = total - self.numOfSick - self.numOfDeath - self.numOfImmune
		print ("Day: " +  str(self.day))
		print ("Total: \tHealthy " + str(healthy) + " \tSick " + str(self.numOfSick) + "\tDead " + str(self.numOfDeath) + "\tImmune " + str(self.numOfImmune))
		print ("Today: \tInfected " + str(self.infected) + "\tDead " + str(dead) + "\tImmune " + str(immune))

	def run(self):

		self.infected = 0
		self.display()

		#animate("Press enter to continue...\n")
		#raw_inappend()
		while len(self.queue) != 0:
			#time.sleep(0.5)
			self.nextQueue = deque()
			while len(self.queue) != 0:
				self.playOneDay(self.queue.popleft())
			self.queue = self.nextQueue
			self.day += 1
			self.display()
			self.prevNumOfSick = self.numOfSick
			self.prevNumOfDeath = self.numOfDeath
			self.prevNumOfImmune = self.numOfImmune
			self.infected = 0

		self.display()


	def playOneDay(self, individual):
		for cord in Individual.popleftNeighbours([individual[0],individual[1]],self.gridDimension):
			if self.Grid[cord[0]][cord[1]].tryToInfect(self.probCont) == 1:
				self.nextQueue.append(cord)
				self.infected += 1

		self.Grid[individual[0]][individual[1]].tryToDie(self.probDeath, self.minSickDays)
		self.Grid[individual[0]][individual[1]].tryToBI(self.minSickDays, self.maxSickDays)#Try to become immune
		if self.Grid[individual[0]][individual[1]].state == SICK:
			self.nextQueue.append(individual)
			self.Grid[individual[0]][individual[1]].days += 1

class Test():
	def paramTest():
		pass

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
