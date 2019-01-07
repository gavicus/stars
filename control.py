import pygame
import view, model

class Control:
  def __init__(self):
    self.model = model.Model()
    self.view = view.View(self.model, self.viewCallback)
    self.view.draw()
    self.mouseButtons = [None,0,0,0,0,0]
    self.mouseLast = [None,0,0,0,0,0]
    self.loop()

  def loop(self):
    button = None
    drag = False
    while True:
      for event in pygame.event.get():
        if event.type == pygame.MOUSEMOTION:
          if self.mouseButtons[1]:
            eventPos = model.Point.fromTuple(event.pos)
            delta = model.Point.subtract(eventPos, self.mouseLast[button]) if self.mouseLast[button] else 0
            if delta:
              drag = True
              self.shiftFocus(delta)
              self.mouseLast[button] = eventPos
          self.onMouseMove(event.pos)
        elif event.type == pygame.QUIT:
          pygame.quit()
          quit()
        elif event.type == pygame.MOUSEBUTTONDOWN:
          if button == 4:
            self.view.zoomIn()
          if button == 5:
            self.view.zoomOut()
          else:
            drag = False
            button = event.button
            self.mouseButtons[button] = 1
            self.mouseLast[button] = model.Point.fromTuple(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
          button = event.button
          if button < 4: # not mousewheel
            self.mouseButtons[button] = 0
            self.mouseLast[button] = 0
            if not drag: self.onClick(button)
            drag = False
        elif event.type == pygame.KEYUP:
          if event.key == 27:
            pygame.quit()
            quit()
          else:
            print ('Key code', event.key, 'has not been bound.')

  def onClick(self, button):
    self.view.onClick(button)

  def onMouseMove(self, position):
    self.view.onMouseMove(position)

  def shiftFocus(self, delta):
    self.view.shiftFocus(delta)

  def viewCallback(self, data):
    print('viewCallback', data)


if __name__ == '__main__':
  control = Control()
