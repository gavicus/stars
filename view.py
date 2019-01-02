import pygame, math
from model import Point

class Color:
  black = (0,0,0)
  white = (255,255,255)
  gray7 = (175,175,175)
  gray5 = (125,125,125)
  gray4 = (100,100,100)
  gray3 = (75,75,75)
  gray2 = (50,50,50)
  gray1 = (25,25,25)

class Theme:
  void = Color.black
  star = Color.gray4
  hoveredStar = Color.white
  hoveredBack = Color.gray2

class View:
  def __init__(self):

    # temporary
    x = 1800
    y = 1150
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

    self.screenSize = Point(300,200)
    self.screen = pygame.display.set_mode(self.screenSize.tuple())
    self.starMapShift = Point(self.screenSize.x//2, self.screenSize.y//2)
    self.starMapScale = 150
    self.hoveredStar = None

  def draw(self, starMap):
    self.screen.fill(Theme.void)
    self.drawStars(starMap)
    pygame.display.update()

  def drawStars(self, starMap):
    for star in starMap.stars:
      self.setScreenLoc(star)

    if self.hoveredStar:
      pygame.draw.circle(self.screen, Theme.hoveredBack, self.hoveredStar.screen.tuple(), 8)

    for star in starMap.stars:
      color = Theme.hoveredStar if star == self.hoveredStar else Theme.star
      pygame.draw.circle(self.screen, color, star.screen.tuple(), 0)

  def onClick(self, button):
    if self.hoveredStar:
      print('clicked:', self.hoveredStar.loc.tuple())

  def onMouseMove(self, position, starMap):
    point = Point.fromTuple(position)
    hovered = None
    dist = 0
    minDist = 10
    for star in starMap.stars:
      d = point.squareDist(star.screen)
      if d < minDist ** 2:
        if not hovered or d < dist:
          hovered = star
          dist = d
    changed = (hovered != self.hoveredStar)
    self.hoveredStar = hovered
    if changed:
      self.draw(starMap)

  def setScreenLoc(self, star):
    screen = Point(
      math.floor(star.loc.x * self.starMapScale) + self.starMapShift.x,
      math.floor(star.loc.y * self.starMapScale) + self.starMapShift.y
    )
    star.setScreen(screen)

  def shiftFocus(self, delta, starMap):
    self.starMapShift = self.starMapShift.add(delta)
    self.draw(starMap)

  def zoomIn(self, starMap):
    self.starMapScale += 10
    self.draw(starMap)

  def zoomOut(self, starMap):
    minScale = 50
    if self.starMapScale > minScale:
      self.starMapScale -= 10
      self.draw(starMap)
