#Unit mm
class parameter():
	def __init__(self):
         self.layerthickness=0.8#0.025-0.1
         self.diameter=1.5
         self.overlap=self.diameter*0.4
         self.beam_dia=1.5
         self.offset=self.beam_dia/4.0
         self.tolerance=0.2