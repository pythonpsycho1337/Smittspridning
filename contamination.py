import os, sys, time, random, platform

#Example call: python contamination.py 0.5 0.1 5 10 0,0;1,1;2,2

class Individual:
	def __init__(self,state):
		self.state = state #-2=Immune -1=Dead 0=healthy 0<x = Ill where x is days left as ill
		self.nextState = state
	def __str__(self):
		return ["I","-","O","*"][min(self.state,1)+2]
	def tryToInfect(self,probabilty,days):
		if self.state != 0:#not healthy
			return 0
		if random.random() < probabilty: #Infected
			self.nextState = days
			return 1
	def tryToDie(self,probabilty):
		if self.state <= 0:#Not infected
			return 0
		r = random.random()
		if r < probabilty:
			self.nextState = -1;
			return 1
	def tryToBI(self):#Try to become immune
		if self.state <= 0 or self.nextState == -1:#Not infected
			return
		if self.state == 1:
			self.nextState = -2
		else:
			self.nextState -= 1;
	@staticmethod
	def getNeighbours(iCoordinates,gridDimension):
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
			self.probCont = float(params[1]) #Probability of contamination
			self.probDeath = float(params[2]) #Probability of death
			self.sickDays = int(params[3]) #How long an Individual is sick
			self.gridDimension = int(params[4] )#The dimensions of the grid
			self.generateGrid(self.parseCoordinates(params[5])) #Generate the grid using the coordinates of the sick Individuals
		else:
			out = "Usage: python contamination.py <Probability of contamination> <Probability of death> <Sick time> "
			out += "<Grid dimensions><Coordinates of sick Individuals>"
			out+="\nCoordinates are specified in the following format x,y;x2,y2 where x=0,y=0 is in the top left corner.\nExample: 1,2;1,3"
			print out
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
				self.Grid[row].append(Individual(0))
		for i in range(0,len(sickCoord)):#Set sick Individuals
			self.Grid[sickCoord[i][0]][sickCoord[i][1]].state = self.sickDays
	def displayInfo(self):
		print "probCont="+str(self.probCont)+"\tprobDeath="+str(self.probDeath)+"\tsickDays"+str(self.sickDays)+"\tgridDimension="+str(self.gridDimension)
	def displayGrid(self):
		out = ""
		for row in range(0,self.gridDimension):
			for col in range(0,self.gridDimension):
				out += " " + str(self.Grid[row][col])
			out +="\n"
		print(out)
	def displayStats(self):#TODO
		print ""
		
	def run(self):
		clearTerminal()
		self.displayInfo()
		self.displayGrid()
		self.displayStats()
		time.sleep(0.5)
		#animate("Press enter to continue...\n")
		#raw_input()
		self.playOneDay()
		self.run()
	def playOneDay(self):
		for row in range(0,self.gridDimension): #Infection phase
			for col in range(0,self.gridDimension):
				if self.Grid[row][col].state > 0:#If infected
					for cord in Individual.getNeighbours([row,col],self.gridDimension):
						self.Grid[cord[0]][cord[1]].tryToInfect(self.probCont,self.sickDays)
				
		for row in range(0,self.gridDimension): #Death phase
			for col in range(0,self.gridDimension):
				self.Grid[row][col].tryToDie(self.probDeath)
				self.Grid[row][col].tryToBI()#Try to become immune		
		
		for row in range(0,self.gridDimension): #Update states
			for col in range(0,self.gridDimension):
				self.Grid[row][col].state = self.Grid[row][col].nextState

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
