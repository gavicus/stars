import pygame, math
from model import Point, Star, Group, Faction

class Color:
  black = (0,0,0)
  white = (255,255,255)
  gray7 = (175,175,175)
  gray5 = (125,125,125)
  gray4 = (100,100,100)
  gray3 = (75,75,75)
  gray2 = (50,50,50)
  gray1 = (25,25,25)
  yellow = (255,255,0)

class Theme:
  void = Color.black
  star = Color.gray4
  hoveredStar = Color.white
  selectedStar = Color.yellow
  hoveredBack = Color.gray2
  detailBackground = Color.gray2
  detailText = Color.gray5
  sidebarBackground = Color.gray2
  buttonBackground = Color.black
  selectDestinationLine = Color.gray5
  destinationLine = Color.gray3

class Page:
  stars = 0
  starDetail = 1

class Button:
  def __init__(self, corner, text, commandString):
    self.width = 80
    self.height = 14
    self.corner = corner
    self.text = text
    self.commandString = commandString

  def containsPoint(self, point):
    if point.x < self.corner.x: return False
    if point.y < self.corner.y: return False
    if point.x > self.corner.x + self.width: return False
    if point.y > self.corner.y + self.height: return False
    return True

  def draw(self, surface):
    buttonWidth = 80
    buttonHeight = 14
    pygame.draw.rect(surface, Theme.buttonBackground, (self.corner.x, self.corner.y, buttonWidth, buttonHeight))
    myfont = pygame.font.SysFont('microsoftsansserif', 11)
    textsurface = myfont.render(self.text, False, Theme.detailText)
    surface.blit(textsurface, self.corner.tuple())

  def getCommandString(self):
    return self.commandString

class CommandMode:
  none = None
  chooseDestination = 1

class View:
  def __init__(self, model, callback):
    pygame.font.init()

    # temporary
    x = 1800
    y = 1150
    import os
    os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x,y)

    self.model = model
    self.screenSize = Point(300,200)
    self.mapSize = Point(self.screenSize.y, self.screenSize.y)
    self.screen = pygame.display.set_mode(self.screenSize.tuple())
    self.starMapShift = Point(self.mapSize.x//2, self.mapSize.y//2)
    self.starMapScale = 150
    self.hoveredStar = None
    self.selectedStar = None
    self.focusObject = None
    self.zoomIncrement = 10
    self.currentPage = Page.stars
    self.buttons = []
    self.hoveredButton = None
    self.callback = callback
    self.commandMode = None
    self.commandGroup = None
    self.mouseLast = None

  def draw(self):
    if self.currentPage == Page.stars:
      self.screen.fill(Theme.void)
      self.drawStars()
      self.drawSidebar()
    elif self.currentPage == Page.starDetail:
      self.screen.fill(Theme.detailBackground)
      self.drawStarDetail(self.selectedStar)

    pygame.display.update()

  def drawStars(self):
    for star in self.model.starMap.stars:
      self.setScreenLoc(star)

    if self.hoveredStar:
      pygame.draw.circle(self.screen, Theme.hoveredBack, self.hoveredStar.screen.tuple(), 8)

    for star in self.model.starMap.stars:
      color = Theme.selectedStar if star == self.selectedStar else Theme.hoveredStar if star == self.hoveredStar else Theme.star
      radius = 0
      if len(star.docked) > 0:
        pygame.draw.line(self.screen, color, (star.screen.x-1, star.screen.y), (star.screen.x+1, star.screen.y))
        pygame.draw.line(self.screen, color, (star.screen.x, star.screen.y-1), (star.screen.x, star.screen.y+1))
      else:
        pygame.draw.circle(self.screen, color, star.screen.tuple(), radius)

    if self.commandMode == CommandMode.chooseDestination:
      origin = self.commandGroup.getScreenLocation()
      dest = self.mouseLast
      if self.hoveredStar:
        dest = self.hoveredStar.screen
      if origin and dest:
        pygame.draw.line(self.screen, Theme.selectDestinationLine, origin.tuple(), dest.tuple())

    for faction in self.model.factions:
      for group in faction.groups:
        if group.destination:
          dest = Point(0,0)
          if group.destination.__class__ == Star:
            dest = group.destination.screen
          else:
            dest = self.mapToScreenLoc(group.destination)
          if group.isDocked():
            groupScreen = group.loc.screen
          else:
            groupScreen = group.screen
          pygame.draw.line(self.screen, Theme.destinationLine, groupScreen.tuple(), dest.tuple())


  def drawSidebar(self):
    pygame.draw.rect(
      self.screen, Theme.sidebarBackground,
      (self.mapSize.x, 0, self.screenSize.x-self.mapSize.x, self.mapSize.y)
    )
    if self.commandMode == CommandMode.chooseDestination:
      if self.hoveredStar:
        margin = 10
        lineHeight = 15
        cursor = Point(self.mapSize.x + margin, margin)
        roundLoc = self.hoveredStar.loc.round(2)
        self.drawText(roundLoc.string(), cursor.tuple(), Theme.detailText)
        cursor.y += lineHeight
        self.drawText(self.hoveredStar.getDisplayName(), cursor.tuple(), Theme.detailText)
        cursor.y += lineHeight
        dist = math.sqrt(self.hoveredStar.loc.squareDist(self.commandGroup.getMapLocation()))
        dist = round(dist, 2)
        distLine = "distance: " + str(dist)
        self.drawText(distLine, cursor.tuple(), Theme.detailText)
    elif self.focusObject: # selected object among many at one location
      if self.focusObject.__class__ == Star:
        self.drawSidebarStar(self.focusObject)
      elif self.focusObject.__class__ == Group:
        self.drawSidebarGroup(self.focusObject)
    elif self.selectedStar:
      if len(self.selectedStar.docked) > 0:
        self.drawSidebarMenu()
      else:
        self.drawSidebarStar(self.selectedStar)

  def drawSidebarMenu(self):
    margin = 5
    lineHeight = 18
    cursor = Point(self.mapSize.x + margin, margin)
    self.buttons = []
    self.buttons.append( Button(cursor.copy(), self.selectedStar.getDisplayName(), "focus:" + str(self.selectedStar.id)) )
    for docked in self.selectedStar.docked:
      cursor.y += lineHeight
      self.buttons.append( Button(cursor.copy(), docked.getDisplayName(), "focus:" + str(docked.id)) )
    for btn in self.buttons: btn.draw(self.screen)

  def drawSidebarGroup(self, group):
    margin = 10
    lineHeight = 15
    cursor = Point(self.mapSize.x + margin, margin)
    self.drawText(group.getDisplayName(), cursor.tuple(), Theme.detailText)
    if group.faction == self.model.currentFaction:
      self.buttons = []
      for command in ["move group", "manage group"]:
        cursor.y += lineHeight
        self.buttons.append(Button(cursor.copy(), command, command + ":" + str(group.id)))
      for btn in self.buttons: btn.draw(self.screen)

  def drawSidebarStar(self, star):
    margin = 10
    lineHeight = 15
    cursor = Point(self.mapSize.x + margin, margin)
    roundLoc = star.loc.round(2)
    self.drawText(roundLoc.string(), cursor.tuple(), Theme.detailText)
    cursor.y += lineHeight
    self.drawText(star.getDisplayName(), cursor.tuple(), Theme.detailText)

  def drawStarDetail(self, star):
    margin = 10
    lineHeight = 15
    cursor = Point(margin, margin)
    roundLoc = star.loc.round(2)
    self.drawText(roundLoc.string(), cursor.tuple(), Theme.detailText)
    cursor.y += lineHeight
    self.drawText(star.name, cursor.tuple(), Theme.detailText)
    if len(star.docked) > 0:
      cursor.y += lineHeight
      self.drawText('groups:', cursor.tuple(), Theme.detailText)
      cursor.x += margin
      for group in star.docked:
        cursor.y += lineHeight
        self.drawText(group.getDisplayName(), cursor.tuple(), Theme.detailText)
      cursor.x -= margin

  def drawText(self, text, pos, color):
    myfont = pygame.font.SysFont('microsoftsansserif', 11)
    textsurface = myfont.render(text, False, color)
    self.screen.blit(textsurface, pos)

  def findNearestStar(self, point, maxDist=10000):
    if point.x > self.mapSize.x:
      return None
    hovered = None
    dist = 0
    for star in self.model.starMap.stars:
      d = point.squareDist(star.screen)
      if d < maxDist ** 2:
        if not hovered or d < dist:
          hovered = star
          dist = d
    return hovered

  def onButton(self, command, data):
    print("onButton",command,data)
    if command == 'focus':
      self.focusObject = self.model.getObjectById(int(data))
      self.draw()
    elif command == 'move group':
      self.commandGroup = self.model.getObjectById(int(data))
      self.commandMode = CommandMode.chooseDestination
      self.draw()

  def onClick(self, button):
    self.focusObject = None
    if self.currentPage == Page.stars:
      if self.hoveredButton:
        command, data = self.hoveredButton.getCommandString().split(':')
        self.onButton(command,data)
      elif self.commandMode == CommandMode.chooseDestination:
        if self.hoveredStar:
          self.commandGroup.destination = self.hoveredStar
        else:
          self.commandGroup.destination = self.screenToMapLoc(self.mouseLast)
        self.commandMode = CommandMode.none
        self.draw()
      elif self.hoveredStar:
        self.selectedStar = self.hoveredStar
        self.draw()
      else:
        self.selectedStar = None
        self.draw()
    elif self.currentPage == Page.starDetail:
      self.currentPage = Page.stars
      self.draw()

  def onMouseMove(self, position):
    point = Point.fromTuple(position)
    self.mouseLast = point
    if self.currentPage == Page.stars:

      # check buttons
      self.hoveredButton = None
      for button in self.buttons:
        if button.containsPoint(point):
          self.hoveredButton = button
          return

      hovered = self.findNearestStar(point, 10)
      changed = (hovered != self.hoveredStar)
      self.hoveredStar = hovered

      if self.commandMode:
        if self.commandMode == CommandMode.chooseDestination:
          changed = True

      if changed:
        self.draw()

  def screenToMapLoc(self, loc):
    x = (loc.x - self.starMapShift.x) / self.starMapScale
    y = (loc.y - self.starMapShift.y) / self.starMapScale
    return Point(x,y)

  def mapToScreenLoc(self, loc):
    return Point(
      math.floor(loc.x * self.starMapScale) + self.starMapShift.x,
      math.floor(loc.y * self.starMapScale) + self.starMapShift.y
    )

  def setScreenLoc(self, star):
    star.setScreen(self.mapToScreenLoc(star.loc))

  def shiftFocus(self, delta):
    self.starMapShift = self.starMapShift.add(delta)
    self.draw()

  def getZoomShiftChange(self):
    center = Point(self.mapSize.x//2, self.mapSize.y//2)
    vector = self.starMapShift.subtract(center)
    normal = vector.normal()
    shiftChange = normal.multiply(self.zoomIncrement/2)
    return shiftChange.floor()
    
  def zoomIn(self):
    self.starMapScale += self.zoomIncrement
    self.starMapShift = self.starMapShift.add(self.getZoomShiftChange())
    self.draw()

  def zoomOut(self):
    minScale = 50
    if self.starMapScale > minScale:
      self.starMapScale -= self.zoomIncrement
    self.starMapShift = self.starMapShift.subtract(self.getZoomShiftChange())
    self.draw()
