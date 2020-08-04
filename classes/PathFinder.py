# coding=utf-8
from libs.pathfinding.pathfinding.core.diagonal_movement import DiagonalMovement
from libs.pathfinding.pathfinding.core.grid import Grid
from libs.pathfinding.pathfinding.finder.a_star import AStarFinder
from libs.pathfinding.pathfinding.finder.finder import ExecutionTimeException, GridTooSmallError


class MobPathFinding(AStarFinder):
    def __init__(self, heuristic=None, weight=1,
                 diagonal_movement=DiagonalMovement.only_when_no_obstacle,
                 time_limit=0.0001,  # Minecraft needs a insanely fast pathfinding algorithm, and the game itself
                 # uses A*
                 max_runs=None):
        super().__init__(heuristic=heuristic,
                         weight=weight,
                         diagonal_movement=diagonal_movement,
                         time_limit=time_limit,
                         max_runs=max_runs)

    def find_path(self, start: tuple = None, end: tuple = None, grid=None):
        if not start or not end:
            raise TypeError("Need a start and end point!")
        elif grid is None:
            raise GridTooSmallError("No grid passed to pathfinder!")
        elif len(grid) < 1 or len(grid[0]) < 1:
            raise GridTooSmallError("Grid is too small!")

        if type(grid) == type(["testlist"]):
            grid = Grid(matrix=grid)
            start = grid.node(*start)
            end = grid.node(*end)

        try:
            path = super().find_path(start, end, grid)
        except ExecutionTimeException:
            return None
        return path[0]
