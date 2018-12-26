import queue
import tkinter as tk

import PIL.Image
import PIL.ImageTk

__HANGMAN_IMAGES_PREFIX__ = 'resources/images/'
__HANGMAN_IMAGES__ = ['hangman0.png', 'hangman1.png', 'hangman2.png',
                      'hangman3.png', 'hangman4.png', 'hangman5.png',
                      'hangman6.png']

__MSG_WIN_COLOR__ = "green"
__MSG_WARN_COLOR__ = "red"
__MSG_HINT_COLOR__ = "blue"

MAX_ERRORS = len(__HANGMAN_IMAGES__) - 1
WIN_MSG = 'Correct guess, this is the word!'
LOSS_MSG = 'You have run out of guesses, the word was: '
ALREADY_CHOSEN_MSG = 'You have already chosen '
NON_VALID_MSG = 'Please enter a valid letter'
HINT_MSG = 'Consider choosing: '
DEFAULT_MSG = ''

HINT = 1
LETTER = 2
PLAY_AGAIN = 3


class Hangman:
    def __init__(self, root):
        self.root = root

        root.protocol('WM_DELETE_WINDOW', self.callback_quit)
        root.after(200, self.poll)
        root.minsize(width=700, height=400)

        self.main_container = tk.Frame(root, width=350, height=300)
        self.main_container.pack(side="left", fill="both", expand=True)

        self.left_frame = tk.Frame(self.main_container)
        self.left_frame.pack(side="left", fill="x", expand=False)

        self.right_frame = tk.Frame(self.main_container)
        self.right_frame.pack(side="right", fill="x", expand=False)

        self.bottom_frame = tk.Frame(self.main_container)
        self.bottom_frame.pack(side="bottom", fill="x", expand=False)

        self.left_label = tk.Label(self.left_frame, bg='white')
        self.left_label.grid(row=0, column=0, sticky='W', padx=50, pady=50)

        self.l_pattern = tk.Label(self.right_frame, font=("Helvetica", 16), wraplength=400)
        self.l_pattern.grid(row=0, column=0, padx=50, pady=50)

        self.l_wrong_guess_lst = tk.Label(self.right_frame, font=("Helvetica", 16), wraplength=400)
        self.l_wrong_guess_lst.grid(row=1, column=0, padx=50, pady=20)

        self.choose_letter = tk.Frame(self.right_frame)
        self.choose_letter.grid(row=2, column=0, padx=5, pady=10)

        self.letter_label = tk.Label(self.choose_letter, text="Choose a letter: ", font=("Helvetica", 16),
                                     wraplength=400)

        self.letter_entry = tk.Entry(self.choose_letter, width=5)
        self.letter_entry.bind("<Return>", self.callback_letter)
        self.letter_label.grid(row=0, column=0, padx=5, pady=5)
        self.letter_entry.grid(row=0, column=1, padx=5, pady=5)

        self.msg_label = tk.Label(self.right_frame, font=("Helvetica", 18, "italic"), wraplength=400, width=30,
                                  justify=tk.LEFT)
        self.msg_label.grid(row=3, column=0, padx=50, pady=20)

        self.hint_b = tk.Button(self.right_frame, text="Get a hint!", width=20, command=self.callback_hint,
                                font=("Helvetica", 12, "bold"))

        self.play_again_b = tk.Button(self.right_frame, text="Play Again!", width=20, command=self.callback_play_again,
                                      font=("Helvetica", 16, "bold"))
        self.play_again_b_f = tk.Button(self.right_frame, text="No More!", width=20, command=self.callback_play_again_f,
                                        font=("Helvetica", 16, "bold"))

        self.root.resizable(width=tk.FALSE, height=tk.FALSE)

        self.input_queue = queue.Queue()
        self.task_queue = queue.Queue()

        self.ask_play = False
        self.pattern = ''
        self.wrong_guesses = list()
        self.error_counter = 0
        self.msg = ''
        self.msg_color = 'white'

    def poll(self):
        while not self.task_queue.empty():
            task = self.task_queue.get()
            task()
        self.root.after(200, self.poll)

    def add_task(self, task):
        self.task_queue.put(task)

    def get_input(self):
        return self.input_queue.get(block=True)

    def update_gui(self):
        image_file = __HANGMAN_IMAGES__[self.error_counter]
        image_obj = PIL.Image.open(__HANGMAN_IMAGES_PREFIX__ + image_file)
        photo = PIL.ImageTk.PhotoImage(image_obj)

        self.left_label.config(image=photo)
        self.left_label.image = photo  # keep a reference!
        self.l_pattern.config(text="Pattern: " + ' '.join(self.pattern))
        self.l_wrong_guess_lst.config(text="Wrong guesses: " + ','.join(self.wrong_guesses))

        if self.ask_play:
            self.play_again_b.grid(row=5, column=0, padx=5, pady=5)
            self.play_again_b_f.grid(row=10, column=0, padx=5, pady=5)
            self.hint_b.grid_remove()
            self.choose_letter.grid_remove()
        else:
            self.hint_b.grid(row=4, column=0, padx=5, pady=5)
            self.play_again_b.grid_remove()
            self.play_again_b_f.grid_remove()
            self.choose_letter.grid(row=2, column=0, padx=5, pady=10)

        self.msg_label.config(text=self.msg, fg=self.msg_color)

    def update_data(self, pattern, error_counter, wrong_guesses, msg, ask_play):
        self.pattern = pattern
        self.wrong_guesses = wrong_guesses
        self.error_counter = error_counter
        self.msg = msg
        self.ask_play = ask_play

        if self.msg.startswith(HINT_MSG):
            self.msg_color = __MSG_HINT_COLOR__
        elif self.msg == WIN_MSG:
            self.msg_color = __MSG_WIN_COLOR__
        else:
            self.msg_color = __MSG_WARN_COLOR__

    def callback_letter(self, _):
        letter = self.letter_entry.get()
        self.input_queue.put((LETTER, letter))
        self.letter_entry.delete(0, 'end')
        self.update_gui()

    def destroy(self):
        self.root.destroy()

    def callback_quit(self):
        self.root.destroy()

    def callback_hint(self):
        self.input_queue.put((HINT, True))

    def callback_play_again(self):
        self.ask_play = False
        self.input_queue.put((PLAY_AGAIN, True))

    def callback_play_again_f(self):
        self.ask_play = False
        self.input_queue.put((PLAY_AGAIN, False))
