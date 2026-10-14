import argparse
import heapq
import itertools

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
        destination_cells = self._piece_cells(piece, new_x, new_y)
        for x, y in destination_cells:
            if x < 0 or y < 0 or x >= self.width or y >= self.height:
                return False

        for other_piece in self.pieces:
            if other_piece is piece:
                continue
            if set(destination_cells).intersection(self._piece_cells(other_piece)):
                return False
        return True

    @staticmethod
    def _piece_cells(piece, coord_x=None, coord_y=None):
        x = piece.coord_x if coord_x is None else coord_x
        y = piece.coord_y if coord_y is None else coord_y
        if piece.is_2_by_2:
            return [(x, y), (x + 1, y), (x, y + 1), (x + 1, y + 1)]
        if piece.is_single:
            return [(x, y)]
        if piece.orientation == 'h':
            return [(x, y), (x + 1, y)]
        return [(x, y), (x, y + 1)]

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
                    new_pieces = [
                        Piece(
                            existing_piece.is_2_by_2,
                            existing_piece.is_single,
                            new_x if existing_piece is piece else existing_piece.coord_x,
                            new_y if existing_piece is piece else existing_piece.coord_y,
                            existing_piece.orientation
                        )
                        for existing_piece in self.pieces
                    ]
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
    :param algo: dfs or astar
    :type algo: str
    """
    # read the board from the file
    board, goal_board = read_from_file(in_file_name)

    def heuristic(state):
        return manhattan_distance(state, goal_board)

    initial_state = State(board, heuristic, 0, 0)

    if algo == 'dfs':
        solution = dfs(initial_state, goal_board)
    elif algo == 'astar':
        solution = astar(initial_state, goal_board)
    else:
        raise ValueError("Unsupported search algorithm: {}".format(algo))

    if solution is None:
        raise ValueError("No solution found for {}".format(in_file_name))

    with open(out_file_name, "w") as output_file:
        for state in get_solution(solution):
            output_file.write(grid_to_string(state.board.grid))
            output_file.write("\n")


def _piece_shape(piece):
    if piece.is_2_by_2:
        return (2, 2)
    if piece.is_single:
        return (1, 1)
    if piece.orientation == 'h':
        return (2, 1)
    return (1, 2)


def manhattan_distance(state, goal_board):
    """
    Calculate an admissible matching-distance heuristic for the board.

    Pieces with the same shape are interchangeable in the board
    representation, so match them to goal positions at minimum total distance.
    :param state: The state to calculate the heuristic for.
    :type state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: A lower bound on the number of moves to the goal.
    :rtype: int
    """
    current_groups = {}
    goal_groups = {}
    for piece in state.board.pieces:
        current_groups.setdefault(_piece_shape(piece), []).append(
            (piece.coord_x, piece.coord_y)
        )
    for piece in goal_board.pieces:
        goal_groups.setdefault(_piece_shape(piece), []).append(
            (piece.coord_x, piece.coord_y)
        )

    if current_groups.keys() != goal_groups.keys():
        raise ValueError("Current and goal boards have different piece shapes")

    total_distance = 0
    for shape, current_positions in current_groups.items():
        goal_positions = goal_groups[shape]
        if len(current_positions) != len(goal_positions):
            raise ValueError("Current and goal boards have different piece counts")

        costs = {0: 0}
        for current_x, current_y in current_positions:
            next_costs = {}
            for mask, cost in costs.items():
                for index, (goal_x, goal_y) in enumerate(goal_positions):
                    bit = 1 << index
                    if mask & bit:
                        continue
                    next_mask = mask | bit
                    distance = abs(current_x - goal_x) + abs(current_y - goal_y)
                    candidate = cost + distance
                    if candidate < next_costs.get(next_mask, float("inf")):
                        next_costs[next_mask] = candidate
            costs = next_costs
        total_distance += costs[(1 << len(goal_positions)) - 1]
    return total_distance


def is_goal_state(state, goal_board):
    """
    Check if the given state is a goal state.

    :param state: The state to check.
    :type state: State
    :param goal_board: The goal board.
    :type goal_board: Board
    :return: True if the given state is a goal state, False otherwise.
    :rtype: bool
    """
    return state.board.grid == goal_board.grid


def _state_key(state):
    return tuple(tuple(row) for row in state.board.grid)


def generate_successors(state):
    """
    Generate child states linked to the state being expanded.

    :param state: The current state.
    :type state: State
    :return: The legal one-move successor states.
    :rtype: List[State]
    """
    return [
        State(board, state.hfn, 0, state.depth + 1, state)
        for board in state.board.generate_successors()
    ]


def _root_state(initial_state):
    return State(initial_state.board, initial_state.hfn, 0, 0)


def dfs(initial_state, goal_board):
    """
    Return the first goal state found by depth-first search, or None.

    Multi-path pruning skips configurations already explored or in the frontier.
    """
    root = _root_state(initial_state)
    frontier = [root]
    frontier_keys = {_state_key(root)}
    explored = set()

    while frontier:
        state = frontier.pop()
        key = _state_key(state)
        frontier_keys.remove(key)
        if is_goal_state(state, goal_board):
            return state
        explored.add(key)

        for successor in generate_successors(state):
            successor_key = _state_key(successor)
            if successor_key not in explored and successor_key not in frontier_keys:
                frontier.append(successor)
                frontier_keys.add(successor_key)
    return None


def astar(initial_state, goal_board):
    """
    Return an optimal goal state found by A* search, or None if unreachable.
    """
    root = _root_state(initial_state)
    if root.hfn is None:
        raise ValueError("A* search requires a heuristic function")
    root.f = root.hfn(root)
    counter = itertools.count()
    frontier = [(root.f, 0, next(counter), root)]
    best_cost = {_state_key(root): 0}
    expanded_cost = {}

    while frontier:
        _, cost, _, state = heapq.heappop(frontier)
        key = _state_key(state)
        if cost != best_cost.get(key):
            continue
        if cost >= expanded_cost.get(key, float("inf")):
            continue
        if is_goal_state(state, goal_board):
            return state
        expanded_cost[key] = cost

        for successor in generate_successors(state):
            successor_key = _state_key(successor)
            successor_cost = cost + 1
            if successor_cost >= best_cost.get(successor_key, float("inf")):
                continue

            best_cost[successor_key] = successor_cost
            successor.f = successor_cost + successor.hfn(successor)
            heapq.heappush(
                frontier,
                (successor.f, successor_cost, next(counter), successor)
            )
    return None


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
