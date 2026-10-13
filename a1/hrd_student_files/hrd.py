import argparse
import sys

#====================================================================================

char_single = '2'

class Piece:
    """
    This represents a piece on the Hua Rong Dao puzzle.
    """

    def __init__(self, is_2_by_2, is_single, coord_x, coord_y, orientation):
        """
        :param is_2_by_2: True if the piece is a 2x2 piece and False otherwise.
        :type is_2_by_2: bool
        :param is_single: True if this piece is a 1x1 piece and False otherwise.
        :type is_single: bool
        :param coord_x: The x coordinate of the top left corner of the piece.
        :type coord_x: int
        :param coord_y: The y coordinate of the top left corner of the piece.
        :type coord_y: int
        :param orientation: The orientation of the piece (one of 'h' or 'v') 
            if the piece is a 1x2 piece. Otherwise, this is None
        :type orientation: str
        """

        self.is_2_by_2 = is_2_by_2
        self.is_single = is_single
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.orientation = orientation

    def set_coords(self, coord_x, coord_y):
        """
        Move the piece to the new coordinates. 

        :param coord: The new coordinates after moving.
        :type coord: int
        """
        self.coord_x = coord_x
        self.coord_y = coord_y

    def __repr__(self):
        return '{} {} {} {} {}'.format(self.is_2_by_2, self.is_single, \
            self.coord_x, self.coord_y, self.orientation)

class Board:
    """
    Board class for setting up the playing board.
    """

    def __init__(self, height, pieces):
        """
        :param pieces: The list of Pieces
        :type pieces: List[Piece]
        """

        self.width = 4
        self.height = height
        self.pieces = pieces

        # self.grid is a 2-d (size * size) array automatically generated
        # using the information on the pieces when a board is being created.
        # A grid contains the symbol for representing the pieces on the board.
        self.grid = []
        self.__construct_grid()

        self.blanks = []

    # customized eq for object comparison.
    def __eq__(self, other):
        if isinstance(other, Board):
            return self.grid == other.grid
        return False


    def __construct_grid(self):
        """
        Called in __init__ to set up a 2-d grid based on the piece location information.

        """

        for i in range(self.height):
            line = []
            for j in range(self.width):
                line.append('.')
            self.grid.append(line)

        for piece in self.pieces:
            if piece.is_2_by_2:
                self.grid[piece.coord_y][piece.coord_x] = '1'
                self.grid[piece.coord_y][piece.coord_x + 1] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x] = '1'
                self.grid[piece.coord_y + 1][piece.coord_x + 1] = '1'
            elif piece.is_single:
                self.grid[piece.coord_y][piece.coord_x] = char_single
            else:
                if piece.orientation == 'h':
                    self.grid[piece.coord_y][piece.coord_x] = '<'
                    self.grid[piece.coord_y][piece.coord_x + 1] = '>'
                elif piece.orientation == 'v':
                    self.grid[piece.coord_y][piece.coord_x] = '^'
                    self.grid[piece.coord_y + 1][piece.coord_x] = 'v'
      
    def display(self):
        """
        Print out the current board.

        """
        for i, line in enumerate(self.grid):
            for ch in line:
                print(ch, end='')
            print()

    def is_valid_move(self, piece, new_x, new_y):
        """
        Check if the move is valid for the given piece to the new coordinates.

        :param piece: The piece to move.
        :type piece: Piece
        :param new_x: The new x coordinate.
        :type new_x: int
        :param new_y: The new y coordinate.
        :type new_y: int
        :return: True if the move is valid, False otherwise.
        :rtype: bool
        """
        # Check if the new coordinates are within bounds
        if new_x < 0 or new_y < 0 or new_x >= self.width or new_y >= self.height:
            return False

        # Check if the target position is occupied by another piece
        for other_piece in self.pieces:
            if other_piece != piece:
                if (new_x == other_piece.coord_x and new_y == other_piece.coord_y) or \
                   (other_piece.is_2_by_2 and
                    ((new_x == other_piece.coord_x and new_y == other_piece.coord_y) or
                     (new_x == other_piece.coord_x + 1 and new_y == other_piece.coord_y) or
                     (new_x == other_piece.coord_x and new_y == other_piece.coord_y + 1) or
                     (new_x == other_piece.coord_x + 1 and new_y == other_piece.coord_y + 1))):
                    return False
        return True
    
    def generate_successors(self):
        """
        Generate all possible moves for the current board state.

        :return: A list of new Board states after valid moves.
        :rtype: List[Board]
        """
        moves = []
        for piece in self.pieces:
            # Check all four directions for possible moves
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                new_x = piece.coord_x + dx
                new_y = piece.coord_y + dy
                if self.is_valid_move(piece, new_x, new_y):
                    # Create a new board state with the piece moved
                    new_pieces = self.pieces.copy()
                    new_piece = Piece(piece.is_2_by_2, piece.is_single, new_x, new_y, piece.orientation)
                    new_pieces.remove(piece)
                    new_pieces.append(new_piece)
                    moves.append(Board(self.height, new_pieces))
        return moves

class State:
    """
    State class wrapping a Board with some extra current state information.
    Note that State and Board are different. Board has the locations of the pieces. 
    State has a Board and some extra information that is relevant to the search: 
    heuristic function, f value, current depth and parent.
    """

    def __init__(self, board, hfn, f, depth, parent=None):
        """
        :param board: The board of the state.
        :type board: Board
        :param hfn: The heuristic function.
        :type hfn: Optional[Heuristic]
        :param f: The f value of current state.
        :type f: int
        :param depth: The depth of current state in the search tree.
        :type depth: int
        :param parent: The parent of current state.
        :type parent: Optional[State]
        """
        self.board = board
        self.hfn = hfn
        self.f = f
        self.depth = depth
        self.parent = parent

def read_from_file(filename):
    """
    Load initial board from a given file.

    :param filename: The name of the given file.
    :type filename: str
    :return: (initial_board, goal_board)
    :rtype: (Board, Board)
    """

    puzzle_file = open(filename, "r")

    line_index = 0
    pieces = []
    final_pieces = []
    final = False
    found_2by2 = False
    finalfound_2by2 = False
    height_ = 0

    for line in puzzle_file:
        height_ += 1
        if line == '\n':
            if not final:
                height_ = 0
                final = True
                line_index = 0
            continue
        if not final: #initial board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if found_2by2 == False:
                        pieces.append(Piece(True, False, x, line_index, None))
                        found_2by2 = True
        else: #goal board
            for x, ch in enumerate(line):
                if ch == '^': # found vertical piece
                    final_pieces.append(Piece(False, False, x, line_index, 'v'))
                elif ch == '<': # found horizontal piece
                    final_pieces.append(Piece(False, False, x, line_index, 'h'))
                elif ch == char_single:
                    final_pieces.append(Piece(False, True, x, line_index, None))
                elif ch == '1':
                    if finalfound_2by2 == False:
                        final_pieces.append(Piece(True, False, x, line_index, None))
                        finalfound_2by2 = True
        line_index += 1
        
    puzzle_file.close()
    board = Board(height_, pieces)
    goal_board = Board(height_, final_pieces)
    return board, goal_board


def grid_to_string(grid):
    string = ""
    for i, line in enumerate(grid):
        for ch in line:
            string += ch
        string += "\n"
    return string


def solve_puzzle(in_file_name, out_file_name, algo):
    """
    Solve the puzzle using the given type of algorithm.

    :param in_file_name: name of file to read puzzle from (e.g. "med1.txt")
    :type in_file_name: str
    :param out_file_name: name of file to write solution to
    :type out_file_name: str
    :param algo: dfs or a_star
    :type algo: str
    """
    # read the board from the file
    board, goal_board = read_from_file(in_file_name)

    #An example of how to write solutions to the outputfile. (This is not a correct solution, of course).
    #with open(args.outputfile, 'w') as sys.stdout:
    #    board.display()
    #    print("")
    #    goal_board.display()
    if algo == 'dfs': # Use DFS and follow GSA w/ pruning pseudocode
        from a1.hrd_student_files.dfs import dfs
        dfs(board, goal_board, out_file_name)
        explored = {}
        frontier = {}
        #TODO: Implement DFS and write the solution to the output file after finishing helper
        

def manhattan_distance(state):
    """
    Calculate the Manhattan distance of the main piece to the goal position (top left corner of the board).
    Heuristic function.

    :param state: The state to calculate the Manhattan distance for.
    :type state: State
    :return: The Manhattan distance.
    :rtype: int
    """
    # Find the main piece (2x2 piece)
    for piece in state.board.pieces:
        if piece.is_2_by_2:
            main_piece = piece
            break

    # Calculate the Manhattan distance to the goal position (0, 0)
    distance = abs(main_piece.coord_x - 0) + abs(main_piece.coord_y - 0)
    return distance

def is_goal_state(state):
    """
    Check if the given state is a goal state.

    :param state: The state to check.
    :type state: State
    :return: True if the given state is a goal state, False otherwise.
    :rtype: bool
    """
    return state.board.grid == goal_board.grid


def get_solution(goal_state):
    """
    Get the solution path from the initial state to the goal state.

    :param goal_state: The goal state.
    :type goal_state: State
    :return: A list of states representing the solution path.
    :rtype: List[State]
    """
    solution_path = []
    current_state = goal_state
    while current_state is not None:
        solution_path.append(current_state)
        current_state = current_state.parent
    solution_path.reverse()  # Reverse to get the path from initial to goal
    return solution_path

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--inputfile",
        type=str,
        required=True,
        help="The input file that contains the puzzles."
    )
    parser.add_argument(
        "--outputfile",
        type=str,
        required=True,
        help="The output file that contains the solution."
    )
    parser.add_argument(
        "--algo",
        type=str,
        required=True,
        choices=['astar', 'dfs'],
        help="The searching algorithm."
    )
    args = parser.parse_args()
    
    solve_puzzle(args.inputfile, args.outputfile, args.algo)

