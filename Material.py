class Material:

    def __init__(self, x=0, y=0, fx=1, fy=1, vx=1, vy=1):
        self.x = x  # position
        self.y = y
        self.vx = vx  # velocity
        self.vy = vy
        self.fx = fx  # force
        self.fy = fy

    def describe(self):
        print(f'Material: position x: {self.x} position y: {self.y} fx: {self.fx} fy: {self.fy} vx: {self.vx}'
              f' vy: {self.vy}')



