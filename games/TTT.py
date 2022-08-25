def get_map():

    class Cell:
        def __init__(self, x, y):
            self.x = x
            self.y = y
            self.field = False

    def check_line(grid_cell, x, y):
        if x % 2 == 1 or y % 2 == 1:
            return False
        else:
            return True

    grid_cell = [Cell(x, y) for x in range(5) for y in range(5)]    

    map_cell = [check_line(grid_cell, x, y) for y in range(5) for x in range(5)]
