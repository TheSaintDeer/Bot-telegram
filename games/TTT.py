def get_map():
    def check_line(x, y):
        if x % 2 == 1 or y % 2 == 1:
            return False
        else:
            return True

    map_cell = [check_line(x, y) for y in range(5) for x in range(5)]

    return map_cell
