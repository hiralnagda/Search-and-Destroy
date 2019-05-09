from collections import OrderedDict
from graphics import *
from random import randint


import operator
import sys


def compute_cost(current_cell, window, px_size):
    cost = OrderedDict()
    x, y = current_cell
    for xpos in range(0, window, px_size):
        for ypos in range(0, window, px_size):
            cost[(xpos, ypos)] = (abs(ypos - y) + abs(xpos - x))/px_size
    del cost[current_cell]
    return cost


def normalize(belief):
    total = 0

    for key, value in belief.items():
        total += value

    for key, value in belief.items():
        belief[key] = belief[key] / total

    return belief


def return_target_found(target_found, max_prob_cell):
    # Check if the search will find the target

    rnum = randint(0, 100) / 100
    if rnum <= target_found[max_prob_cell]:
        return True
    else:
        return False


def return_f_neg(false_neg, max_prob_cell):
    # Check if the cell will return a false negative

    rnum = randint(0, 100)/100
    if rnum <= false_neg[max_prob_cell]:
        return True
    else:
        return False


def choose_target(size, px_size):
    # Generate a random number between 0 and size - 1
    x = randint(0, size - 1)
    x = x * px_size

    y = randint(0, size - 1)
    y = y * px_size

    cell = (x, y)
    return cell


def bayesian_update_rule_1(belief, false_neg):
    # Update the belief matrix by Rule 1

    # Sort the belief matrix by values (i.e. Probability of target in cell)
    temp_list = sorted(belief.items(), key=operator.itemgetter(1), reverse=True)

    # Find the cell with max probability
    max_prob_cell = temp_list[0][0]

    # Perform Bayesian update
    belief[max_prob_cell] = belief[max_prob_cell] * false_neg[max_prob_cell]
    return belief


def bayesian_update_rule_2(belief, target_found):
    # Update the belief matrix by Rule 2

    # Sort the belief matrix by values (i.e. Probability of target in cell)
    temp_list = sorted(belief.items(), key=operator.itemgetter(1), reverse=True)

    # Find the cell with max probability
    max_prob_cell = temp_list[0][0]

    # Perform Bayesian update
    belief[max_prob_cell] = belief[max_prob_cell] * target_found[max_prob_cell]
    return belief


def set_false_neg_values(terrain):
    # print(terrain)
    if terrain == 0:
        return 0.1
    elif terrain == 1:
        return 0.3
    elif terrain == 2:
        return 0.7
    else:
        return 0.9


def tiles(win, position, px_size, path_prob):
    # flat (white) - 0
    # hilly (brown) - 1
    # forested (green) - 2
    # caves (grey) - 3
    path_value = 0
    x, y = position
    rect = Rectangle(Point(x, y), Point(x + px_size, y + px_size))
    if 0 <= path_prob <= 0.2:
        rect.setFill("white")
        path_value = 0
    elif path_prob <= 0.5:
        rect.setFill("brown")
        path_value = 1
    elif path_prob <= 0.8:
        rect.setFill("green")
        path_value = 2
    elif path_prob <= 1:
        rect.setFill("grey")
        path_value = 3
    rect.draw(win)
    return path_value


def getNeighbours(target_cell, size):
    neighbours = []
    px_size = 10
    window = (px_size * size)
    x, y = target_cell
    dx = [0, 0, -1 * px_size, px_size]
    dy = [px_size, -1 * px_size, 0, 0]
    padding = 0

    for i in range(0, 4, 1):
        row = x + dx[i]
        col = y + dy[i]

        if row < padding or col < padding:
            continue

        if row > window - px_size or col > window - px_size:
            continue

        neighbours.append((row, col))

    return neighbours


def getBorderTerrains(target_cell,board_tiles,size):
    nbors=getNeighbours(target_cell,size)
    if len(nbors) == 4 :
        nbor_index = randint(0, 3)
    if len(nbors) == 3 :
        nbor_index = randint(0, 2)
    if len(nbors) == 2 :
        nbor_index = randint(0, 1)
    new_target_cell = nbors[nbor_index]

    return board_tiles[target_cell], board_tiles[new_target_cell], new_target_cell


def neighbourType(typ, board_tiles, cell, size):
    # Returns a list of neigbours of type "typ"
    nborlist = getNeighbours(cell,size)
    ret_nbors = []
    for item in nborlist:
        if board_tiles[item] == typ:
            ret_nbors.append(item)
    return ret_nbors


def updateMovingBelief(target_cell,board_tiles,belief , type1, type2, size):
    count_type = {}
    belief_copy = belief.copy()
    print(type1)
    print(type2)
    # for cell in board_tiles:     # print(board_tiles[cell])

        # count = 0
        # if board_tiles[cell] == type1:
        #     nbor = neighbourType(type2, board_tiles, cell, size)
        #     count_type[cell] = len(nbor)
        # elif board_tiles[cell] == type2:
        #     nbor = neighbourType(type1, board_tiles, cell, size)
        #     count_type[cell] = len(nbor)
        # else:
        #     count_type[cell] = 0


    for cell in board_tiles:
        prob = 0
        if board_tiles[cell] == type1:
            nbors = neighbourType(type2, board_tiles, cell, size)
            for nbor in nbors:
                prob = prob + belief_copy[nbor]
        elif board_tiles[cell] == type2:
            nbors = neighbourType(type1, board_tiles, cell, size)
            for nbor in nbors:
                prob = prob + belief_copy[nbor]

        belief[cell] = prob

    return belief

def build_maze(size):
    board_tiles = OrderedDict()
    false_neg = OrderedDict()
    target_found = OrderedDict()
    belief = OrderedDict()
    px_size = 10
    window = (px_size * size)
    win = GraphWin('Probabilistic Search', window, window)
    for xpos in range(0, window, px_size):
        for ypos in range(0, window, px_size):
            path_prob = randint(0, 100) / 100
            position = (xpos, ypos)
            board_tiles[position] = tiles(win, position, px_size, path_prob)
            belief[position] = 1 / (size * size)
            false_neg[position] = set_false_neg_values(board_tiles[position])
            target_found[position] = 1 - false_neg[position]
    # print(board_tiles)
    inp = input('Enter "1" for Rule 1, "2" for Rule 2, "3" for Rule 3 (Question 4) & "4" for Rule 4 (Moving Target) ')
    # Set the target at a position
    target_cell = choose_target(size, px_size)
    if inp == "1":
        # Rule 1
        count = 0
        while True:
            # Check if the cell with max prob will return a false negative
            count += 1
            # Sort the belief matrix by values (i.e. Probability of target in cell)
            temp_list = sorted(belief.items(), key=operator.itemgetter(1), reverse=True)
            # Find the cell with max probability
            max_prob_cell = temp_list[0][0]
            print(max_prob_cell, belief[max_prob_cell])
            f_neg_val = return_f_neg(false_neg, max_prob_cell)
            if max_prob_cell == target_cell and not f_neg_val:
                print('Target found by Rule 1!', 'Count: ', count)
                break
            else:
                # Call the Bayesian update formula by rule 1 and normalize it
                belief = bayesian_update_rule_1(belief, false_neg)
                belief = normalize(belief)
    elif inp == "2":
        # Rule 2
        count = 0
        while True:
            # Check if the cell with max prob will return a false negative
            count += 1
            # Sort the belief matrix by values (i.e. Probability of target in cell)
            temp_list = sorted(belief.items(), key=operator.itemgetter(1), reverse=True)
            # Find the cell with max probability
            max_prob_cell = temp_list[0][0]
            print(max_prob_cell, belief[max_prob_cell])
            target_found_val = return_target_found(target_found, max_prob_cell)
            if max_prob_cell == target_cell and target_found_val:
                print('Target found by Rule 2!', 'Count: ', count)
                break
            else:
                # Call the Bayesian update formula by rule 2 and normalize it
                belief = bayesian_update_rule_2(belief, target_found)
                belief = normalize(belief)
    elif inp == "3":
        # Rule 3
        count = 0
        current_cell = max_prob_cell = (0, 0)
        while True:
            dummy_belief = OrderedDict()
            # Find the cost from the current cell to all the cells
            cost_dict = compute_cost(current_cell, window, px_size)
            f_neg_val = return_f_neg(false_neg, max_prob_cell)
            if max_prob_cell == target_cell and not f_neg_val:
                count += 1
                print('Target found by Rule 3!', 'Count: ', count)
                break
            else:
                for key, value in cost_dict.items():
                    dummy_belief[key] = (belief[key] * target_found[key]) / cost_dict[key]
                dummy_belief[current_cell] = belief[current_cell] * target_found[current_cell]
                # Sort the dummy belief matrix by values (i.e. Probability of target in cell)
                temp_list = sorted(dummy_belief.items(), key=operator.itemgetter(1), reverse=True)
                # Find the cell with max probability
                max_prob_cell = temp_list[0][0]
                xs, ys = current_cell
                xd, yd = max_prob_cell
                # Perform Bayesian update
                belief[max_prob_cell] = belief[max_prob_cell] * target_found[max_prob_cell]
                belief = normalize(belief)
                count += abs(yd - ys) + abs(xd - xs)
                current_cell = max_prob_cell
                print('Current cell: ', belief[current_cell])
    elif inp =="4":

        count = 0
        while True:
            # Transition

            # Check if the cell with max prob will return a false negative
            count += 1
            # Sort the belief matrix by values (i.e. Probability of target in cell)
            temp_list = sorted(belief.items(), key=operator.itemgetter(1), reverse=True)
            # Find the cell with max probability
            max_prob_cell = temp_list[0][0]
            print(max_prob_cell, belief[max_prob_cell])
            f_neg_val = return_f_neg(false_neg, max_prob_cell)
            if max_prob_cell == target_cell and not f_neg_val:
                print('Target found by Rule 1!', 'Count: ', count)
                break
            else:
                # Call the Bayesian update formula by rule 1 and normalize it
                belief = bayesian_update_rule_1(belief, false_neg)
                # uncomment the below statement for rule 2 and comment above statement
                # belief = bayesian_update_rule_2(belief, false_neg)
                belief = normalize(belief)
                type1, type2, target_cell = getBorderTerrains(target_cell, board_tiles, size)
                belief = updateMovingBelief(target_cell, board_tiles, belief, type1, type2, size)
                # Rule4


    else:
        sys.exit("Invalid input !")

    win.getMouse()

build_maze(50)

