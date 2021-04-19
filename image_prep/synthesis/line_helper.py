
def solve_for_y(p1, p2, x):
    slope = get_slope(p1, p2)
    yintercept = get_yintercept(p1, p2, slope)

    if slope != None and yintercept != None:
        return float(slope) * x + float(yintercept)
    else:
        return None
        # raise Exception('Can not solve on a vertical line')


def get_slope(p1, p2):
    x1 = p1[0]
    x2 = p2[0]
    y1 = p1[1]
    y2 = p2[1]
    try:
        return (float(y2)-y1)/(float(x2)-x1)
    except ZeroDivisionError:
        # line is vertical
        return None


def get_yintercept(p1, p2, slope):
    x1 = p1[0]
    y1 = p1[1]
    
    if slope != None:
        return y1 - slope * x1
    else:
        return None