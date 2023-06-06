from pybricks.hubs import PrimeHub
from pybricks.pupdevices import ForceSensor
from pybricks.parameters import Button, Port, Color
from pybricks.tools import wait, StopWatch
from matrix_helper import MatrixHelper
from pixel_pics import PixelPics
from urandom import randint


class BrickSnake:
    """Implementation of the classic game "Snake" for the BrickBoyColor
    based on the Pybricks framework. As inspiration minor parts of the
    code of the game was generated by chat.openai.com and then adapted."""

    def __init__(self, display_res_x, display_res_y):
        # Basic variables
        self.__resolution = (display_res_x, display_res_y)
        self.__game_speed = 300  # work speed itself
        # self.slow_factor = 50  # reduce the speed of the snake
        # self.slow_counter = 0  # counter for slow_factor

        # Variables for game SNAKE
        self.__hardgame = False  # If True hitting the wall ends the game
        self.__direction = ()  # initial direction of snake
        self.__snake_head = ()  # snake head at game start
        self.__snake_body = []  # snake body at game start
        self.__lunch = ()
        # self.lunch = (randint(0, self.resolution[0] - 1),
        #               randint(0, self.resolution[1] - 1))  # initial position of lunch
        self.__render_on = ()
        self.__render_off = []
        self.__snake_had_lunch = None

        self.__game_counter = None
        self.__gameover = None
        self.__quit = False
        self.__reset = True

        # Initialize software and hardware
        self.__matrix = MatrixHelper(self.__resolution[0], self.__resolution[1])  # initialize driver for matrix
        self.__pixel_pics = PixelPics()  # initialize pixel drawings library
        self.__hub = PrimeHub()  # initialize LEGO Spike Prime Hub
        self.__button_L = ForceSensor(Port.E)  # initialize LEGO Spike Prime Force Sensor as left button
        self.__button_R = ForceSensor(Port.F)  # initialize LEGO Spike Prime Force Sensor as right button
        self.__hub_buttons = []  # initialize variable that holds info about pressed button

    @staticmethod
    def __wait(time):
        """ Part of generator function for using parallel computing without threads.
            Source: https://github.com/orgs/pybricks/discussions/356 """
        timer = StopWatch()
        while timer.time() < time:
            yield

    def __input_buttons(self):
        print("Get input")
        while True:
            # turn button taps to self.direction change
            if self.__button_L.touched():
                print("Left touched")
                # turn snake self.direction counter-clockwise
                if self.__direction == (1, 0):  # from right to left
                    self.__direction = (0, -1)
                elif self.__direction == (0, -1):  # from bottom to top
                    self.__direction = (-1, 0)
                elif self.__direction == (-1, 0):  # from left to right
                    self.__direction = (0, 1)
                elif self.__direction == (0, 1):  # from top to bottom
                    self.__direction = (1, 0)
            elif self.__button_R.touched():
                print("Right touched")
                # turn snake self.direction clockwise
                if self.__direction == (1, 0):  # from left to right
                    self.__direction = (0, 1)
                elif self.__direction == (0, 1):  # from top to bottom
                    self.__direction = (-1, 0)
                elif self.__direction == (-1, 0):  # from right to left
                    self.__direction = (0, -1)
                elif self.__direction == (0, -1):  # from bottom to top
                    self.__direction = (1, 0)
            yield

    def __show_something_on_hub(self):
        while True:
            # if self.button_L.touched():
            #     self.hub.display.icon(Icon.COUNTERCLOCKWISE)
            # elif self.button_R.touched():
            #     self.hub.display.icon(Icon.CLOCKWISE)
            # elif Button.BLUETOOTH in self.hub_buttons:
            #     self.hub.display.icon(Icon.ARROW_RIGHT_UP)
            # else:
            #     self.hub.display.icon(Icon.SQUARE)
            self.__hub.display.number(self.__game_counter)
            yield

    def __overule_hardgame(self):
        if not self.__hardgame:
            if self.__snake_head[0] == 6 and self.__direction == (1, 0):
                # from left to right reaching screen boarder
                self.__snake_head = (self.__snake_head[0] - 6, self.__snake_head[1])
            elif self.__snake_head[1] == 6 and self.__direction == (0, 1):
                # from top to bottom reaching screen boarder
                self.__snake_head = (self.__snake_head[0], self.__snake_head[1] - 6)
            elif self.__snake_head[0] == -1 and self.__direction == (-1, 0):
                # from right to left reaching screen boarder
                self.__snake_head = (self.__snake_head[0] + 6, self.__snake_head[1])
            elif self.__snake_head[1] == -1 and self.__direction == (0, -1):
                # from bottom to top reaching screen boarder
                self.__snake_head = (self.__snake_head[0], self.__snake_head[1] + 6)

    def __check_gameover(self):
        print("Check gameover")
        while True:
            if self.__snake_head[0] == -1 or \
                    self.__snake_head[1] == -1 or \
                    self.__snake_head[0] == self.__resolution[0] or \
                    self.__snake_head[1] == self.__resolution[1]:
                self.__gameover = True
                print(self.__gameover)
            yield

    def __check_snake_eats_itself(self):
        print("Check snake collision")
        while True:
            # if self.snake_head in self.snake_body:
            #     self.gameover = True
            if self.__snake_head in self.__snake_body[1:]:
                self.__gameover = True
            # print("Gameover:", self.__gameover)
            yield

    def __check_snake_had_lunch(self):
        print("Check snake lunch")
        while True:
            if self.__lunch == self.__snake_head:
                self.__hub.speaker.play_notes(["D2/8"], 200)
                self.__game_counter += 1
                self.__snake_had_lunch = True
                self.__lunch = (randint(0, self.__resolution[0] - 1), randint(0, self.__resolution[1] - 1))
            else:
                self.__snake_had_lunch = False
            yield

    def __snake_movement(self):
        print("Snake movement")
        while True:
            yield from self.__wait(self.__game_speed)
            # print("Start movement")
            self.__snake_head = (self.__snake_head[0] + self.__direction[0], self.__snake_head[1] + self.__direction[1])
            # print("Head @ start: ", self.__snake_head)
            self.__overule_hardgame()
            # print("Head after check: ", self.__snake_head)
            self.__snake_body.insert(0, self.__snake_head)
            # print("Body: ", self.snake_body)
            if not self.__snake_had_lunch:
                self.__render_off = self.__snake_body.pop()
            else:
                self.__render_off = ()
            self.__render_on = self.__snake_body.copy()
            # print("--------------------------------------------------------\n")

    def __render_matrix_display(self):
        print("Render matrix")
        while True:
            # print("Start rendering")
            # print(self.lunch)
            self.__matrix.pixel_on(self.__lunch[0], self.__lunch[1], Color.ORANGE)

            # print(self.render_off)
            if self.__render_off:
                self.__matrix.pixel_off(self.__render_off[0], self.__render_off[1])

            # print(self.render_on)
            self.__matrix.pixel_on(self.__render_on[0][0], self.__render_on[0][1], Color(h=235, s=80, v=60))
            for i in range(len(self.__render_on[1:])):
                self.__matrix.pixel_on(self.__render_on[i + 1][0], self.__render_on[i + 1][1], Color(h=235, s=80, v=50))
            # print("--------------------------------------------------------\n")
            yield

    def __set_game_settings(self):
        action = False  # set input status

        # Let's ask for how hard to play
        for char in "Hard Game?":  # that way we can speed up displaying the text rather than using hub.display.text()
            # self.hub.display.text("Hard game?")
            self.__hub.display.char(char)
            wait(250)
        while not action:
            pressed = self.__hub.buttons.pressed()
            if Button.RIGHT in pressed:
                self.__hub.display.char("Y")
                self.__hardgame = True
            elif Button.LEFT in pressed:
                self.__hub.display.char("N")
                self.__hardgame = False
            elif Button.BLUETOOTH in pressed:
                action = True

        action = False  # reset input status

        # Let's ask for how fast to play
        # self.hub.display.text("Difficulty?")
        for char in "Difficulty?":  # that way we can speed up displaying the text rather than using hub.display.text()
            # self.hub.display.text("Hard game?")
            self.__hub.display.char(char)
            wait(250)

        difficulty = 3  # set game speed to mid (1 - 5)

        while not action:
            pressed = self.__hub.buttons.pressed()
            self.__hub.display.char(str(difficulty))

            if Button.RIGHT in pressed:
                if difficulty < 5:
                    difficulty += 1
                    self.__game_speed -= 50
            elif Button.LEFT in pressed:
                if difficulty > 1:
                    difficulty -= 1
                    self.__game_speed += 50
            elif Button.BLUETOOTH in pressed:
                action = True
            wait(250)

    def __init_game(self):
        self.__hub.display.text("Snake", 200, 50)
        wait(1000)

        self.__hub.speaker.volume(35)  # set volume to non deafening

        # Ask for game settings
        self.__set_game_settings()

    def __init_snake(self):
        # Initialize snake and it's lunch
        self.__snake_head = (2, 2)  # snake head at game start
        self.__snake_body = [(1, 2), (0, 2)]  # snake body at game start
        self.__snake_body.insert(0, self.__snake_head)
        self.__render_on = self.__snake_body
        self.__lunch = (randint(0, self.__resolution[0] - 1),
                        randint(0, self.__resolution[1] - 1))  # initial position of lunch
        self.__direction = (1, 0)  # initial direction of snake
        self.__snake_had_lunch = False

        # Initialize or reset the control variables
        self.__game_counter = 0
        self.__gameover = False

    def __reset_game(self):
        action = False  # set input status
        self.__matrix.draw_pixel_graphic(self.__pixel_pics.smiley, Color.GREEN)
        for char in "Play again?":
            self.__hub.display.char(char)
            wait(250)
        while not action:
            pressed = self.__hub.buttons.pressed()
            if Button.RIGHT in pressed:
                self.__hub.display.char("Y")
                self.__matrix.matrix_off()
                self.__reset = True
                self.__quit = False
                action = True
            elif Button.LEFT in pressed:
                self.__hub.display.char("N")
                self.__reset = False
                action = True

    def gameplay(self):
        # self.__init_game()
        while self.__reset:
            self.__init_snake()
            while not self.__quit:
                tasks = [
                    self.__render_matrix_display(),
                    self.__show_something_on_hub(),
                    self.__input_buttons(),
                    self.__snake_movement(),
                    self.__check_snake_had_lunch(),
                    self.__check_snake_eats_itself(),
                    self.__check_gameover()
                ]

                while not self.__gameover:
                    for t in tasks:
                        next(t)
                    wait(100)

                # Here starts gameover action
                # if self.__gameover:
                #     self.__matrix.matrix_off()
                #     # make a sad sound
                #     self.__hub.speaker.play_notes(["B3/2", "B2/2"], 160)
                #     # show a grafik for game over
                #     self.__matrix.draw_pixel_graphic(self.__pixel_pics.smiley_sad, Color.RED)
                #     self.__hub.display.text("Game Over", 200, 50)
                #     wait(1500)  # wait one and a half seconds
                #     self.__quit = True
                wait(self.__game_speed)
            self.__reset_game()
        self.__matrix.matrix_off()


# Test the class
if __name__ == "__main__":
    snakegame = BrickSnake(6, 6)
    snakegame.gameplay()

# Leave the next line empty to fullfil PEP 8
