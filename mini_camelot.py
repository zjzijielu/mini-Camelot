import argparse
import numpy as np
import time

from tkinter import *


class MiniCamelotUI(Frame):

    WIDTH = 200
    HEIGHT = 350

    MARGIN = 20

    def __init__(self, parent, game):
        self.game = game
        self.parent = parent
        Frame.__init__(self, parent)

        self.i, self.j = -1, -1

        self.__initUI()


    def __initUI(self):
        self.parent.title("Mini Camelot")
        self.pack(fill=BOTH, expand=1)
        self.canvas = Canvas(self, width=self.WIDTH, height=self.HEIGHT)
        self.canvas.pack(fill=BOTH, side=TOP)
        restart_button = Button(self, text="Restart game", comman=self.__restart_game)
        restart_button.pack(fill=BOTH, side=BOTTOM)

        self.__draw_grid()
        self.__draw_map()

        self.canvas.bind("<Button-1>", self.__cell_clicked)

    def __draw_victory(self,winner):
        # create a oval (which will be a circle)
        winner_list = ["Player", "Computer", "Draw"]
        winner = winner_list[winner-1]
        print(winner, type(winner))
        x0 = y0 = MARGIN * 5/2
        x1 = y1 = MARGIN * 8
        self.canvas.create_oval(x0, y0, x1, y1, tags="oldmap", fill="dark orange",
            outline="orange")
        # create text
        x = y = MARGIN * 6
        self.canvas.create_text(x, y, text=winner + " wins!", tags="oldmap", fill="white",
            font=("Arial", 18))

    def __draw_grid(self):
        """
        Draw the grid based on 15*8 grid
        every square MARGIN*MARGIN

        """
        MARGIN = self.MARGIN
        for i in range(4):
            x0 = (4-i) * MARGIN + MARGIN
            y0 = i * MARGIN
            x1 = 160-(4-i)*MARGIN + MARGIN
            y1 = i * MARGIN
            self.canvas.create_line(x0, y0, x1, y1)

            for j in range(3-i, 5+i+1):
                x0 = j * MARGIN + MARGIN
                y0 = (i+1) * MARGIN
                x1 = j * MARGIN + MARGIN
                y1 = 80
                self.canvas.create_line(x0, y0, x1, y1)

        for i in range(4, 4+9):
            x0 = 0 + MARGIN
            y0 = i * MARGIN
            x1 = 160 + MARGIN
            y1 = i * MARGIN
            self.canvas.create_line(x0, y0, x1, y1)

        for i in range(9):
            x0 = i * MARGIN + MARGIN
            y0 = 80
            x1 = i * MARGIN + MARGIN
            y1 = 80 + MARGIN*8
            self.canvas.create_line(x0, y0, x1, y1)

        for i in range(3):
            x0 = (i+1) * MARGIN + MARGIN
            y0 = (i+13)* MARGIN
            x1 = 160-(i+1)*MARGIN + MARGIN
            y1 = (i+13) * MARGIN
            self.canvas.create_line(x0, y0, x1, y1)

            for j in range(7-i, i, -1):
                x0 = j * MARGIN + MARGIN
                y0 = 80 + MARGIN*8
                x1 = j * MARGIN + MARGIN
                y1 = (i+13) * MARGIN
                self.canvas.create_line(x0, y0, x1, y1)

    def __draw_map(self):
        self.canvas.delete("oldmap")
        for i in range(14):
            for j in range(8):
                answer = self.game.map[i][j]
                if answer == 1 or answer == 2:
                    x = (j+1) * MARGIN
                    y = (i+1) * MARGIN

                    x0 = x+5
                    y0 = y+5
                    x1 = x+15
                    y1 = y+15

                    color = "black" if answer == 2 else "white"
                    self.canvas.create_oval(x0, y0, x1, y1, outline="black", tag = "oldmap", fill=color, width=2)

    def __select_cell(self, i, j):
        #print(i, j)
        x = (j+1) * MARGIN
        y = (i+1) * MARGIN

        x0 = x+5
        y0 = y+5
        x1 = x+15
        y1 = y+15

        self.canvas.create_oval(x0, y0, x1, y1, outline="red", tag = "oldmap", fill="white", width=2)

    def __deselect_cell(self, i, j):
        #print(i, j)
        x = (j+1) * MARGIN
        y = (i+1) * MARGIN

        x0 = x+5
        y0 = y+5
        x1 = x+15
        y1 = y+15
        self.canvas.create_oval(x0, y0, x1, y1, outline="black", tags="oldmap", fill="white", width=2)

    # checking if capture move is possible
    def __check_capture(self):
        if self.j+2 <8 and self.game.map[self.i][self.j+2] == 0 and self.game.map[self.i][self.j+1] == 2:
            return True
        elif self.j-2 >= 0 and self.game.map[self.i][self.j-2] == 0 and self.game.map[self.i][self.j-1] == 2:
            return True
        elif self.i+2<14 and self.game.map[self.i+2][self.j] == 0 and self.game.map[self.i+1][self.j] == 2:
            return True
        elif self.i-2>=0 and self.game.map[self.i-2][self.j] == 0 and self.game.map[self.i-1][self.j] == 2:
            return True
        return False

    def __check_valid(self,i, j):
        # checking if the move is valid
        if self.__check_capture():
            print("capture possible")
            if abs(self.i-i) + abs(self.j-j) == 2:
                print("can capture")
                return True
        elif self.game.map[i][j] == 0:
            if abs(self.i - i) == 1 and self.j - j == 0:
                return True
            elif self.i-i == 0 and abs(self.j - j) == 1:
                return True
            else:
                middle_i = int((self.i + i)/2)
                middle_j = int((self.j + j)/2)
                if self.game.map[middle_i][middle_j] == 1:
                    return True


    def alphabeta_cutoff_search(self, state, d=5, cutoff_test = None, eval_fn = None):
        
        player = 2
        
        global dep
        global node
        global min_pru
        global max_pru
        global t1
        t1 = time.time()
        node = 0
        dep = 0
        min_pru = 0
        max_pru = 0
        
        
        def max_value(state, alpha, beta, depth):
            global node
            global max_pru
            global t1
            current_time = time.time()
            used_time = current_time - t1
            #print(used_time)
            #print(used_time > 10)
            if cutoff_test(state, depth, used_time):
                global dep
                dep = depth
                return eval_fn(state)
            v = -1000
            for a in self.game.actions(state, 2):
                node += 1
                #print(state)
                #print(self.game.result(state, a, 1))
                v = max(v, min_value(self.game.result(state, a, 2), alpha, beta, depth+1))
                if v >= beta:
                    max_pru += 1    
                    return v
                alpha = max(alpha, v)
            return v

        def min_value(state, alpha, beta, depth):
            global node
            global min_pru
            global t1
            current_time = time.time()
            used_time = current_time - t1
            #print(used_time)
            if cutoff_test(state, depth, used_time):
                global dep
                dep = depth
                return eval_fn(state)
            v = 1000
            for a in self.game.actions(state, 1):
                node += 1
                #print(self.game.result(state, a, 2))
                v = min(v, max_value(self.game.result(state, a, 1), alpha, beta, depth+1))
                #print(v)
                if v <= alpha:
                    min_pru += 1
                    return v
                beta = min(beta, v)
            return v

        cutoff_test = (cutoff_test or
                   (lambda state, depth, time: depth > d or
                    game.terminal_test(state) or time > 10))
        eval_fn = eval_fn or (lambda state: game.utility(state))
        best_score = -1000
        beta = 1000
        best_action = None
        #t1 = time.time()
        state = state[::]
        for a in self.game.actions(state, 2):
            v = min_value(self.game.result(state, a, 2), best_score, beta, 1)
            if v > best_score:
                best_score = v
                best_action = a
        t2 = time.time()
        print("node generated:", node)
        print("maximum depth reached:", dep)
        print("times of prunning in MAX-VALUE:", max_pru)
        print("times of prunning in MIN-VALUE:", min_pru)
        print("alphabeta used time", t2-t1)
        return best_action


    def __cell_clicked(self, event):
        if self.game.game_over:
            return

        x, y = event.x, event.y

        if (MARGIN < x < WIDTH - MARGIN and MARGIN < y < HEIGHT - MARGIN):
            self.canvas.focus_set()

            # get row and col numbers from x,y coordinates
            i = y // 20 - 1
            j = x // 20 - 1

            # if cell has was selected already - deselect
            print("Valid actions: \n", self.game.actions(self.game.map, 1))
            if (i , j) == (self.i, self.j):
                self.i, self.j = -1, -1
                self.__deselect_cell(i, j)
            elif self.i != -1 and self.j != -1:
                #print(i, j)
                #print(self.i, self.j)

                if self.__check_valid(i, j):
                    self.game.map[self.i][self.j] = 0
                    self.game.map[i][j] = 1
                    if self.game.map[int((self.i+i)/2)][int((self.j+j)/2)] == 2:
                        self.game.map[int((self.i+i)/2)][int((self.j+j)/2)] = 0
                    self.i, self.j = -1, -1
                    self.__draw_map()
                    # check_win
                    winner = self.game.terminal_test(self.game.map)
                    if winner != None:
                        self.game.game_over = True
                    print(self.game.game_over)
                    if self.game.game_over:
                        self.__draw_victory(winner)
                    else:
                    # computer moves
                        state = [i[:] for i in self.game.map]
                        computer_action = self.alphabeta_cutoff_search(state)
                        self.game.map = self.game.result(self.game.map, computer_action, 2)
                        self.__draw_map()
                        winner = self.game.terminal_test(self.game.map)
                        if winner != None:
                            self.game.game_over = True
                        print(self.game.game_over)

            elif self.game.map[i][j] == 1:
                self.i, self.j = i, j
                self.__select_cell(i, j)



    def __restart_game(self):
        print("restarting")
        self.game.start()
        self.__draw_grid()
        self.__draw_map()


class miniCamelotGame(object):
    """
    A Mini Camelot game, in charge of storing the state of the board and
    checking which player wins.
    """

    def __init__(self):
        self.start_map = [[-1]*3+[0]*2+[-1]*3, [-1]*2+[0]*4+[-1]*2, [-1]+[0]*6+
                          [-1], [0]*8, [0,0,1,1,1,1,0,0],
        [0,0,0,1,1,0,0,0],[0]*8,[0]*8, [0,0,0,2,2,0,0,0], [0,0,2,2,2,2,0,0],
        [0]*8, [-1]+[0]*6+[-1], [-1]*2+[0]*4+[-1]*2, [-1]*3+[0]*2+[-1]*3]

    def start(self):
        self.game_over = False
        self.winner = None
        self.map = [[-1]*3+[0]*2+[-1]*3, [-1]*2+[0]*4+[-1]*2, [-1]+[0]*6+[-1], 
                    [0]*8, [0,0,1,1,1,1,0,0],
        [0,0,0,1,1,0,0,0],[0]*8,[0]*8, [0,0,0,2,2,0,0,0], [0,0,2,2,2,2,0,0],
        [0]*8, [-1]+[0]*6+[-1], [-1]*2+[0]*4+[-1]*2, [-1]*3+[0]*2+[-1]*3]

    def count(self, game_map):
        num_1 = 0
        num_2 = 0
        for i in game_map:
            num_1 += i.count(1)
            num_2 += i.count(2)
        return num_1, num_2

    def terminal_test(self, state):
        winner = None
        num_1, num_2 = self.count(state)
        if num_1 == 1:
            winner = 2
        if num_2 == 1:
            winner = 1
        if state[1][3:5] == [2,2]:
            winner = 2 # Computer
        elif state[-1][3:5] == [1,1]:
            winner = 1 # Player
        elif num_1 == 0:
            if num_2 > 1:
                winner = 2 # Computer
            else:
                winner = 3 # Draw
        elif num_2 == 0:
            self.game_over = True
            if num_1 > 1:
                winner = 1 # Player
            else:
                winner = 0 # Draw
        return winner


    def utility(self, state):
        val = 0
        
        # checking if win or draw occurs:
        num_1, num_2 = self.count(state)
        if num_1 and num_2 == 1:
            return 0 # draw
        if num_1 == 0 and num_2 >= 2:
            return 1000
        if num_1 >= 2 and num_2 == 0:
            return -1000
        
        # checking if the first row contains any black piece
        num_1_in_row1= int(state[0][3] == 2) + int(state[0][4] == 2)
        # if the first row contians two black pieces, then return teh 
        # maximum utility
        if num_1_in_row1 == 2:
            return 1000
        else:
            val += 500 * num_1_in_row1
        
        # checking if the last row contains any white piece
        num_2_in_last_row = int(state[0][3] == 2) + int(state[0][4] == 2)
        # if the first row contians two black pieces, then return teh 
        # maximum utility
        if num_2_in_last_row == 2:
            return 1000
        else:
            val -= 500 * num_2_in_last_row
        for i in range(1, 7):
            for j in range(8):
                if state[i][j] == 2:
                    val += 10*(7-i)
        for i in range(7, 13):
            for j in range(8):
                if state[i][j] == 1:
                    val -= i*10
        
        val -= (6-num_2) * 150
        val -= 50 * num_1
        return val


    def actions(self, state, player):
        actions = []
        opponent = 3-player
        new_map = np.array(state)
        positions = np.asarray(np.where(new_map == player)).T
        #print(positions)
        if_capture = False
        for i in positions:
            if i[0] == 0:
                continue
            x, y = i
            # list possible capture
            if x-2>=0 and self.map[x-2][y] == 0 and self.map[x-1][y] == opponent:
                actions.append(((x, y),(x-2, y)))
                if_capture = True
            if x+2<14 and self.map[x+2][y] == 0 and self.map[x+1][y] == opponent:
                actions.append(((x, y),(x+2, y)))
                if_capture = True
            if y-2>=0 and self.map[x][y-2] == 0 and self.map[x][y-1] == opponent:
                actions.append(((x, y),(x, y-2)))
                if_capture = True
            if y+2<8 and self.map[x][y+2] == 0 and self.map[x][y+1] == opponent:
                actions.append(((x, y),(x, y+2)))
                if_capture = True

        if if_capture == False:
            for i in positions:
                #print(i)
                if i[0] == 0:
                    continue
                x, y = i
                # list all possible plain moves:
                if y-1 >= 0 and self.map[x][y-1] == 0:
                    actions.append(((x, y),(x, y-1)))
                if y+1 < 8 and self.map[x][y+1] == 0:
                    actions.append(((x, y),(x, y+1)))
                if x-1 >= 0 and self.map[x-1][y] == 0:
                    actions.append(((x, y),(x-1, y)))
                if x+1 < 8 and self.map[x+1][y] == 0:
                    actions.append(((x, y),(x+1, y)))

                # list all possible catering moves
                if x-2>=0 and self.map[x-2][y] == 0 and self.map[x-1][y] == player:
                    actions.append(((x, y),(x-2, y)))
                if x+2<14 and self.map[x+2][y] == 0 and self.map[x+1][y] == player:
                    actions.append(((x, y),(x+2, y)))
                if y-2>=0 and self.map[x][y-2] == 0 and self.map[x][y-1] == player:
                    actions.append(((x, y),(x, y-2)))
                if y+2<8 and self.map[x][y+2] == 0 and self.map[x][y+1] == player:
                    actions.append(((x, y),(x, y+2)))
        return actions

    def result(self, state, action, player):
        #print(player)
        #print(action)
        opponent = 3-player
        (i, j) = action[0]
        (new_i, new_j) = action[1]
        new_state = [i[:] for i in state]
        if new_state[int((i+new_i)/2)][int((j+new_j)/2)] == opponent:
            new_state[int((i+new_i)/2)][int((j+new_j)/2)] = 0
        new_state[i][j] = 0
        new_state[new_i][new_j] = player
        return new_state


if __name__ == "__main__":
    game = miniCamelotGame()
    game.start()

    root = Tk()
    MiniCamelotUI(root, game)
    root.mainloop()
