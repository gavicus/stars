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
  detailBackground = Color.gray2
  detailText = Color.gray5

class Page:
  stars = 0
  starDetail = 1

class View:
  def __init__(self):
    pygame.font.init()

    # temporary
    x = 1800
    y = 1150
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

    self.starMap = None
    self.screenSize = Point(300,200)
    self.screen = pygame.display.set_mode(self.screenSize.tuple())
    self.starMapShift = Point(self.screenSize.x//2, self.screenSize.y//2)
    self.starMapScale = 150
    self.hoveredStar = None
    self.selectedStar = None
    self.zoomIncrement = 10
    self.currentPage = Page.stars

  def draw(self, starMap):
    if starMap:
      self.starMap = starMap
    if self.currentPage == Page.stars:
      self.screen.fill(Theme.void)
      self.drawStars(starMap)
    elif self.currentPage == Page.starDetail:
      self.screen.fill(Theme.detailBackground)
      self.drawStarDetail(self.selectedStar)

    pygame.display.update()

  def drawStars(self, starMap):
    for star in starMap.stars:
      self.setScreenLoc(star)

    if self.hoveredStar:
      pygame.draw.circle(self.screen, Theme.hoveredBack, self.hoveredStar.screen.tuple(), 8)

    for star in starMap.stars:
      color = Theme.hoveredStar if star == self.hoveredStar else Theme.star
      pygame.draw.circle(self.screen, color, star.screen.tuple(), 0)

  def drawStarDetail(self, star):
    margin = 10
    lineHeight = 15
    cursor = Point(margin, margin)
    roundLoc = star.loc.round(2)
    self.drawText(roundLoc.string(), cursor.tuple(), Theme.detailText)
    cursor.y += lineHeight
    self.drawText(star.name, cursor.tuple(), Theme.detailText)

  def drawText(self, text, pos, color):
    myfont = pygame.font.SysFont('microsoftsansserif', 12)
    textsurface = myfont.render(text, False, color)
    self.screen.blit(textsurface, pos)

  def onClick(self, button):
    if self.currentPage == Page.stars:
      if self.hoveredStar:
        self.selectedStar = self.hoveredStar
        self.currentPage = Page.starDetail
        self.draw(None)
    elif self.currentPage == Page.starDetail:
        self.currentPage = Page.stars
        self.draw(self.starMap)

  def onMouseMove(self, position, starMap):
    if self.currentPage == Page.stars:
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

  def getZoomShiftChange(self):
    center = Point(self.screenSize.x//2, self.screenSize.y//2)
    vector = self.starMapShift.subtract(center)
    normal = vector.normal()
    shiftChange = normal.multiply(self.zoomIncrement/2)
    return shiftChange.floor()
    
  def zoomIn(self, starMap):
    self.starMapScale += self.zoomIncrement
    self.starMapShift = self.starMapShift.add(self.getZoomShiftChange())
    self.draw(starMap)

  def zoomOut(self, starMap):
    minScale = 50
    if self.starMapScale > minScale:
      self.starMapScale -= self.zoomIncrement
    self.starMapShift = self.starMapShift.subtract(self.getZoomShiftChange())
    self.draw(starMap)
