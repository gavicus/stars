import math, random

class Point:
  def __init__(self, x, y):
    self.x = x
    self.y = y

  def add(self, p):
    return Point(self.x + p.x, self.y + p.y)
  
  def collides(self, p, minDist):
    return self.squareDist(p) <= minDist ** 2

  def floor(self):
    return Point(math.floor(self.x), math.floor(self.y))

  def magnitude(self):
    return math.sqrt(self.x**2 + self.y**2)

  def multiply(self, m):
    return Point(self.x*m, self.y*m)

  def normal(self):
    mag = self.magnitude()
    if mag == 0:
      return Point(0,0)
    return Point(self.x / mag, self.y / mag)

  def round(self, digits):
    return Point(round(self.x, digits), round(self.y, digits))

  def squareDist(self, p):
    dx2 = (p.x - self.x) ** 2
    dy2 = (p.y - self.y) ** 2
    return dx2 + dy2

  def string(self):
    return "(" + str(self.x) + ", " + str(self.y) + ")"

  def subtract(self, p):
    return Point(self.x - p.x, self.y - p.y)
  
  def tuple(self):
    return (self.x, self.y)

  @staticmethod
  def fromTuple(t):
    return Point(t[0], t[1])

class Star:
  def __init__(self, p):
    self.name = None
    self.loc = p

  def setScreen(self, p):
    self.screen = p

class StarMap:
  def __init__(self):
    self.stars = []
    self.starNames = [
      "Alderaan","Amon Shek","Anacreon","Aquaria","Ariel","Arrakis","Bellerophon","Betelgeuse","Caladan",
      "Capella","Caprica","Coruscant","Dantooine","Eridani","Fomalhaut",
      "Gemenon","Giedi Prime","Gliese","Haven","Iota","Ix","Jakku","Jiangyin","Kobol",
      "Lambda","Mintaka","Miranda","Pegasus","Persephone","Romulus","Salusa Secundus","Tatooine",
      "Vulcan","Whitefall",
    ]
    self.nameIndex = 0

  def genRandPolar(self):
    def pickPoint():
      theta = math.pi * 2 * random.random()
      dist = random.random()
      return Point(dist * math.cos(theta), dist * math.sin(theta))

    def pointOk(p):
      minDist = 0.012
      for star in self.stars:
        if star.loc.collides(p, minDist):
          return False
      return True

    count = 100
    maxRetries = 5
    for star in range(0, count):
      p = pickPoint()
      retries = 0
      while not pointOk(p):
        retries += 1
        if retries > maxRetries:
          raise RuntimeError('maxRetries exceeded')
        p = pickPoint()
      star = Star(p)
      star.name = self.genStarName()
      self.stars.append(star)

  def genStarName(self):
    if self.nameIndex < len(self.starNames):
      self.nameIndex += 1
      return self.starNames[self.nameIndex-1]
    else:
      return self.randomName()

  def randomName(self):
    cs = "bcdfghjklmnpqrstvwxz"
    ccs = ["ch","sh","th","ck"]
    vs = "aeiouy"
    vvs = ["ea","ae","oo","ow"]
    def getConsonant():
      roll = random.randint(1,len(cs)+len(ccs))
      if roll < len(ccs):
        return ccs[random.randint(0,len(ccs)-1)]
      return cs[random.randint(0,len(cs)-1)]
    def getVowel():
      roll = random.randint(1,len(vs)+len(vvs))
      if roll < len(vvs):
        return vvs[random.randint(0,len(vvs)-1)]
      return vs[random.randint(0,len(vs)-1)]
    def getStart():
      start = ""
      roll = random.randint(1,4)
      if roll > 1:
        start += getConsonant()
      start += getVowel()
      return start
    def getEnd():
      end = getConsonant()
      roll = random.randint(1,2)
      if roll > 1:
        end += getVowel()
      return end
    def getSylable():
      cons = getConsonant()
      vow = getVowel()
      return cons + vow
    def getMiddle():
      roll = random.randint(1,6)
      if roll == 6:
        return ""
      elif roll > 3:
        return getSylable() + getSylable()
      else:
        return getSylable()
    name = getStart() + getMiddle() + getEnd()
    return name[0].upper() + name[1:]

  def genRoundGrid(self):
    wedges = 48
    rings = 6
    for ring in range(0, rings):
      for wedge in range(0, wedges):
        theta = math.pi * 2 / wedges * wedge
        dist = 1 / rings * (ring + 1)
        x = dist * math.cos(theta)
        y = dist * math.sin(theta)
        star = Star(Point(x,y))
        self.stars.append(star)

class Model:
  def __init__(self):
    self.starMap = StarMap()
    # self.starMap.genRoundGrid()
    self.starMap.genRandPolar()
