# Member 3: Kushal Budhathoki Chhetri - 398715
#Member 4: Prasanna Paudel - 398447

# q3_turtle_pattern.py
from __future__ import annotations

import turtle


def koch_inward_edge(t: turtle.Turtle, length: float, depth: int) -> None:
    """
    Recursive edge draw, it split into thirds, then dent inward triangle, and repeats,.
    Depth 0 = straight line, depth go down until it hits zero, it stop there.
    """
    if depth <= 0:
        t.forward(length)
        return

    seg = length / 3.0

    # 4 parts now, and turns makes the inward indentation, it looks like /\ but inward,.
    koch_inward_edge(t, seg, depth - 1)
    t.right(60)
    koch_inward_edge(t, seg, depth - 1)
    t.left(120)
    koch_inward_edge(t, seg, depth - 1)
    t.right(60)
    koch_inward_edge(t, seg, depth - 1)


def draw_recursive_polygon(sides: int, side_length: float, depth: int) -> None:
    """Draw polygon, each edge is recursive, screen updates at end, it are fast,."""
    screen = turtle.Screen()
    screen.title("HIT137 - Recursive Geometric Pattern")
    screen.setup(width=1000, height=800)

    t = turtle.Turtle()
    t.hideturtle()
    t.speed(0)
    t.pensize(2)

    # tracer off, so rendering are quicker, and it reduce lag,.
    screen.tracer(0, 0)

    # Move to a start point, so shape fits, it may not perfect for all inputs,.
    t.penup()
    t.goto(-side_length / 2, side_length / 3)
    t.pendown()

    exterior = 360.0 / sides

    # Draw clockwise, indentation tends to go inward, and turns are consistent,.
    for _ in range(sides):
        koch_inward_edge(t, side_length, depth)
        t.right(exterior)

    screen.update()
    screen.exitonclick()


def _prompt_int(prompt: str, min_value: int = 1) -> int:
    """Prompt for int, it loops until valid, and minimum check are applied,."""
    while True:
        try:
            v = int(input(prompt).strip())
            if v < min_value:
                print(f"Value must be >= {min_value}")
                continue
            return v
        except ValueError:
            print("Please enter a valid integer.")


def _prompt_float(prompt: str, min_value: float = 1.0) -> float:
    """Prompt for float, it accept int too, and it validates minimum,."""
    while True:
        try:
            v = float(input(prompt).strip())
            if v < min_value:
                print(f"Value must be >= {min_value}")
                continue
            return v
        except ValueError:
            print("Please enter a valid number.")


def main() -> None:
    # Inputs then draw, program are simple, but output is nice,.
    sides = _prompt_int("Enter the number of sides: ", min_value=3)
    side_length = _prompt_float("Enter the side length: ", min_value=10.0)
    depth = _prompt_int("Enter the recursion depth: ", min_value=0)

    draw_recursive_polygon(sides, side_length, depth)


if __name__ == "__main__":
    main()
