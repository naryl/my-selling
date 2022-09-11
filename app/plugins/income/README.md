Плагины вызываются сразу после добавления продажи

class Plugin:
	def __init__(self,app,dt,tm):
	    self.app=app
	    dt - дата добавления
	    tm - время добавления