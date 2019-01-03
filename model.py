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

  def squareDist(self, p):
    dx2 = (p.x - self.x) ** 2
    dy2 = (p.y - self.y) ** 2
    return dx2 + dy2

  def subtract(self, p):
    return Point(self.x - p.x, self.y - p.y)
  
  def tuple(self):
    return (self.x, self.y)

  @staticmethod
  def fromTuple(t):
    return Point(t[0], t[1])

class Star:
  def __init__(self, p):
    self.loc = p

  def setScreen(self, p):
    self.screen = p

class StarMap:
  def __init__(self):
    self.stars = []

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

    count = 200
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
      self.stars.append(star)

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
