import pygame, sys, time
from math import atan2, degrees
from random import randint
from pygame.locals import *

def onSegment(p, q, r):
    # Given three colinear points p, q, r, the function checks if 
    # point q lies on line segment 'pr' 
    if ((q[0] <= max(p[0], r[0])) and (q[0] >= min(p[0], r[0])) and 
        (q[1] <= max(p[1], r[1])) and (q[1] >= min(p[1], r[1]))):
        return True
    return False
  
def orientation(p, q, r):
    # to find the orientation of an ordered triplet (p,q,r)
    # function returns the following values:
    # 0 : Colinear points
    # 1 : Clockwise points
    # 2 : Counterclockwise
      
    # See https://www.geeksforgeeks.org/orientation-3-ordered-points/amp/ 
    # for details of below formula. 
      
    val = (float(q[1] - p[1]) * (r[0] - q[0])) - (float(q[0] - p[0]) * (r[1] - q[1]))

    if (val > 0):
        # Clockwise orientation
        return 1
    elif (val < 0):
        # Counterclockwise orientation
        return 2
    else:
        # Colinear orientation
        return 0

def doIntersect(l1, l2):
    # The main function that returns true if 
    # the line segment 'p1q1' and 'p2q2' intersect. 
    p1 = l1[0]
    q1 = l1[1]
    p2 = l2[0]
    q2 = l2[1]  

    # Find the 4 orientations required for 
    # the general and special cases
    o1 = orientation(p1, q1, p2)
    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)
  
    # General case
    if ((o1 != o2) and (o3 != o4)):
        return True
  
    # Special Cases
    # p1 , q1 and p2 are colinear and p2 lies on segment p1q1
    if ((o1 == 0) and onSegment(p1, p2, q1)):
        return True
    # p1 , q1 and q2 are colinear and q2 lies on segment p1q1
    if ((o2 == 0) and onSegment(p1, q2, q1)):
        return True
    # p2 , q2 and p1 are colinear and p1 lies on segment p2q2
    if ((o3 == 0) and onSegment(p2, p1, q2)):
        return True
    # p2 , q2 and q1 are colinear and q1 lies on segment p2q2
    if ((o4 == 0) and onSegment(p2, q1, q2)):
        return True 
    # If none of the cases
    return False

def get_intersection_point(l1, l2):
    # Line–line intersection given two points on each line
    # from https://en.wikipedia.org/wiki/Line%E2%80%93line_intersection

    inpoint = None

    x1 = l1[0][0]
    y1 = l1[0][1]
    x2 = l1[1][0]
    y2 = l1[1][1]
    x3 = l2[0][0]
    y3 = l2[0][1]
    x4 = l2[1][0]
    y4 = l2[1][1]
    
    d = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)

    if (d != 0):
        px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4))/d 
        py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4))/d 

        inpoint = (int(px), int(py))
    
    return inpoint

def calcular_centroide_poly(poly):
    width = len(poly)
    if width == 0:
        return None

    x = 0
    y = 0

    for point in poly:
        x += point[0]
        y += point[1]

    return (int(x/width), int(y/width))

def sort_pontos_poly(poly):
    cx, cy = calcular_centroide_poly(poly)
    poly.sort(key=lambda x: degrees(atan2(x[0] - cx, x[1] - cy)))
    return poly

def calculate_area_proportion(rect_vertices, poly_vertices):
    rect_area = polygonArea(rect_vertices)
    poly_area = polygonArea(poly_vertices)
    prop = int((poly_area / rect_area) * 100)

    if rect_area == 0:
        return -1

    return prop

def score_and_reset(screen, bg_color):

    global draw_line, playercut_proportion, game_message

    if((playercut_proportion > slice_proportion - success_tolerance) and 
       (playercut_proportion < slice_proportion + success_tolerance)):
        game_message = "SUCCESS"
    else:
        game_message = "FAILED"
        
    # Reset game
    draw_game(pygame.display.get_surface(), white_color)

    time.sleep(3)

    game_message = ""
    playercut_proportion = 0
    draw_line = False

    generate_slice_proportion()
    clear_lists()
    init_square(300, (100, 50))
    draw_game(pygame.display.get_surface(), white_color)

def classify_points_positions(rect_indexes, line_pos):
    
    # line eq. y = ax + b
    x1 = line_pos[0][0]
    y1 = line_pos[0][1]
    x2 = line_pos[1][0]
    y2 = line_pos[1][1]

    a = (y2 - y1)/(x2 - x1)
    b = y1 - a * x1

    j = 0

    vertices = []

    for index in rect_indexes:
        poly_above = []
        poly_below = []

        poly_above.append(point_list[j])
        poly_above.append(point_list[j+1])
        poly_below.append(point_list[j])
        poly_below.append(point_list[j+1])

        r = rect_list[index]
        vertices = [r.topleft, r.topright, r.bottomright, r.bottomleft]
        
        for point in vertices:
            # unpack point
            px, py = point

            # check whether the point is in the plane above or below the line
            if (py >= a * px + b):
                vertices_above.append(point)
                poly_above.append(point)
            else:
                vertices_below.append(point)
                poly_below.append(point)
        
        poly_above = sort_pontos_poly(poly_above)
        poly_below = sort_pontos_poly(poly_below)

        poly_list.append(poly_above)
        poly_list.append(poly_below)
        poly_color.append((randint(0, 255), randint(0, 255), randint(0, 255)))
        poly_color.append((randint(0, 255), randint(0, 255), randint(0, 255)))

        j += 2

        global playercut_proportion
        playercut_proportion = calculate_area_proportion(vertices, poly_below)

def detect_line_collision(line_pos):
    indexes_of_crossed_rects = []

    i = 0
    
    for r in rect_list:
        crossed = 0
        top_line = [r.topleft, r.topright]
        right_line = [r.topright, r.bottomright]
        bottom_line = [r.bottomright, r.bottomleft]
        left_line = [r.bottomleft, r.topleft]

        if doIntersect(line_pos, top_line):
            p = get_intersection_point(line_pos, top_line)
            point_list.append(p)
            crossed += 1
        
        if doIntersect(line_pos, right_line):
            p = get_intersection_point(line_pos, right_line)
            point_list.append(p)
            crossed += 1
        
        if doIntersect(line_pos, bottom_line):
            p = get_intersection_point(line_pos, bottom_line)
            point_list.append(p)
            crossed += 1

        if doIntersect(line_pos, left_line):
            p = get_intersection_point(line_pos, left_line)
            point_list.append(p)
            crossed += 1

        if crossed > 1:
            indexes_of_crossed_rects.append(i)

        i += 1

    if len(indexes_of_crossed_rects) > 0:
        classify_points_positions(indexes_of_crossed_rects, line_pos)

def draw_all_rects():
    font = pygame.font.SysFont(None, 24)
    
    for i in range(len(rect_list)):
        pygame.draw.rect(pygame.display.get_surface(), color_list[i], rect_list[i])
        if draw_rect_labels:
            img = font.render(str(i), True, (0,0,0))
            screen.blit(img, rect_list[i].topleft)

def get_random_rect():
    screen_w, screen_h = pygame.display.get_surface().get_size() 
    r_w, r_h = (300, 300)
    colliding = True

    while colliding:
        r_left = 9999
        r_top = 9999

        while (r_left + r_w > screen_w):
            r_left = randint(0, screen_w)
        while (r_top + r_h > screen_h):
            r_top = randint(0, screen_h)
        
        r = pygame.Rect(r_left, r_top, r_w, r_h)

        if (r.collidelist(rect_list) == -1):
            colliding = False

    return r

def get_square(side, position):
    return pygame.Rect(position[0], position[1], side, side)

def draw_game(screen, bg_color):
    screen.fill(bg_color)
    draw_all_rects()

    if draw_hud:
        goal = font.render("Cut: " + str(slice_proportion) + "% / " + str(100 - slice_proportion) + "%", True, (0,0,0))
        score = font.render("Player: " + str(playercut_proportion) + "% / " + str(100 - playercut_proportion) + "%", True, (0,0,0))
        screen.blit(goal, (50, 400))
        screen.blit(score, (280, 400))

    if draw_line:
        pygame.draw.line(screen, line_color, pos[0], pos[1])
    
    if draw_vertices_points:
        if len(point_list) > 0:
            for p in point_list:
                pygame.draw.circle(screen, red_color, p, 5)

        if len(vertices_above) > 0:
            for p in vertices_above:
                pygame.draw.circle(screen, green_color, p, 5)
        
        if len(vertices_below) > 0:
            for p in vertices_below:
                pygame.draw.circle(screen, blue_color, p, 5)
    
    if len(game_message) > 0:
            if game_message == "SUCCESS":
                icon = font.render(game_message, True, (0,255,0))
                screen.blit(icon, (200, 370))
            if game_message == "FAILED":
                icon = font.render(game_message, True, (255,0,0))
                screen.blit(icon, (215, 370))

    if len(poly_list) > 0:
        for i in range(len(poly_list)):
            pygame.draw.polygon(screen, poly_color[i], poly_list[i])


    pygame.display.update()
    
def clear_lists():
    global point_list 
    global vertices_above 
    global vertices_below 
    global poly_list
    global poly_color

    point_list = []
    vertices_above = []
    vertices_below = []
    poly_list = []
    poly_color = []

def generate_slice_proportion():
    global slice_proportion
    slice_proportion = randint(5, 95)

def polygonArea(poly):
 
    # Initialze area
    area = 0.0
    n = len(poly)
 
    # Calculate value of shoelace formula
    j = n - 1
    for i in range(0, n):
        area += (poly[j][0] + poly[i][0]) * (poly[j][1] - poly[i][1])
        j = i   # j is previous vertex to i
 
    # Return absolute value
    return int(abs(area / 2.0))

def init_square(side, pos):
    global rect_list, color_list

    rect_list = []
    color_list = []

    color_list.append((randint(0, 255), randint(0, 255), randint(0, 255)))
    rect_list.append(get_square(side, pos))

### MAIN

pygame.init()
pygame.display.set_caption("Cutting Rects Game")
clock = pygame.time.Clock()

screen_w, screen_h = (500, 450)
screen = pygame.display.set_mode((screen_w, screen_h))
font = pygame.font.SysFont(None, 30)

rect_list = []
color_list = []
point_list = []

vertices_above = []
vertices_below = []

poly_list = []
poly_color = []

white_color = (255, 255, 255)
red_color = (255, 0, 0)
green_color = (0, 255, 0)
blue_color = (0, 0, 255)
line_color = (125, 125, 125)
initial_pos = (0, 0)
end_pos = (0, 0)
pos = [initial_pos, end_pos]
slice_proportion = 10
playercut_proportion = 0
success_tolerance = 5
game_message = ""

draw_line = True
draw_rect_labels = False
draw_vertices_points = False
draw_hud = True
draw_icon = True

init_square(300, (100, 50))
generate_slice_proportion()

while True:
    for event in pygame.event.get():

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                initial_pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                end_pos = pygame.mouse.get_pos()
                pos = [initial_pos, end_pos]
                draw_line = True
                detect_line_collision(pos)
                if len(point_list) > 1:
                    score_and_reset(screen, white_color)
                clear_lists()
                
                
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
               
    draw_game(screen, white_color)
    clock.tick(10)