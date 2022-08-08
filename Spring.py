class Spring:
    def __init__(self, i=1, j=1, length=1, nx=1, ny=1):
        self.i = i  # point 1 index
        self.j = j  # point 2 index
        self.length = length  # rest length
        self.nx = nx  # normal vector
        self.ny = ny

    def describe(self):
        print(f'Point1: {self.i} Point2: {self.j} Length: {self.length} nx: {self.nx} ny: {self.ny}')
