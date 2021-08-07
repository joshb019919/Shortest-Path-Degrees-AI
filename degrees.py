import csv
import sys

from util import Node, StackFrontier, QueueFrontier

# Maps names to a set of corresponding person_ids
names = {}

# Maps person_ids to a dictionary of: name, birth, movies (a set of movie_ids)
people = {}

# Maps movie_ids to a dictionary of: title, year, stars (a set of person_ids)
movies = {}


def load_data(directory):
    """
    Load data from CSV files into memory.
    """
    # Load people
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row["id"]] = {
                "name": row["name"],
                "birth": row["birth"],
                "movies": set()
            }
            if row["name"].lower() not in names:
                names[row["name"].lower()] = {row["id"]}
            else:
                names[row["name"].lower()].add(row["id"])

    # Load movies
    with open(f"{directory}/movies.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row["id"]] = {
                "title": row["title"],
                "year": row["year"],
                "stars": set()
            }

    # Load stars
    with open(f"{directory}/stars.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                people[row["person_id"]]["movies"].add(row["movie_id"])
                movies[row["movie_id"]]["stars"].add(row["person_id"])
            except KeyError:
                pass


def main():
    if len(sys.argv) > 2:
        sys.exit("Usage: python degrees.py [directory]")
    directory = sys.argv[1] if len(sys.argv) == 2 else "large"

    # Load data from files into memory
    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    source = person_id_for_name(input("Name: "))
    if source is None:
        sys.exit("Person not found.")
    target = person_id_for_name(input("Name: "))
    if target is None:
        sys.exit("Person not found.")

    path = shortest_path(source, target)

    if path is None:
        print("Not connected.")
    else:
        degrees = len(path)
        print(f"{degrees} degrees of separation.")
        path = [(None, source)] + path
        for i in range(degrees):
            person1 = people[path[i][1]]["name"]
            person2 = people[path[i + 1][1]]["name"]
            movie = movies[path[i + 1][0]]["title"]
            print(f"{i + 1}: {person1} and {person2} starred in {movie}")


def shortest_path(source, target):
    """
    Returns the shortest list of (movie_id, person_id) pairs
    that connect the source to the target.

    If no possible path, returns None.

    Idea is copied from maze.py from the video's source code, and
    altered to fit the breadth-first search parameters and the
    requirements of this assignment.

    (as per "You’re welcome to borrow and adapt any code from the
    lecture examples. We’ve already provided you with a file util.py
    that contains the lecture implementations for Node, StackFrontier,
    and QueueFrontier, which you’re welcome to use (and modify if you’d
    like).")
    """
    # Use a queue so that the search is depth-first
    frontier = QueueFrontier()

    # Start with a source node using None as parent, so as to have
    # something at the "end" against which to check.
    start = Node(source, None, None)
    frontier.add(start)

    # Initialize a list to be the eventual path from source to target
    # and a set of already-explored neighbors
    path = list()
    explored = set()

    # Loop till path from source-target discovered or frontier empty
    while True:
        if frontier.empty():

            # No more paths to try and path not found
            return None

        # Store whole node from the removal process
        node = frontier.remove()

        # Mark node as explored
        explored.add(node.state)

        # Add neighbors to frontier
        neighbors = neighbors_for_person(node.state)

        # Each neighbor contains a movie_id and person_id tuple
        for movie, id in neighbors:

            # Keep from being able to "go backwards" in the tree by
            # limiting the search to values not already explored and
            # not already added to the frontier
            if not frontier.contains_state(id) and id not in explored:

                # Assemble each child node out of the cast id (current
                # state), entire parent node for backwards search, and
                # the movie id as the action
                child = Node(state=id, parent=node, action=movie)

                # If node is the goal, then we have a solution
                if child.state == target:

                    # Once a goal is found, backtrack till that "end" check,
                    # appending the required tuples as it goes
                    while child.parent is not None:
                        path.append((child.action, child.state))

                        # Set the node to its parent, stored whole in the next
                        # section for this exact usage
                        child = child.parent

                    # Reverse path tuples to display from source to target
                    path.reverse()
                    return path

                frontier.add(child)


def person_id_for_name(name):
    """
    Returns the IMDB id for a person's name,
    resolving ambiguities as needed.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for person_id in person_ids:
            person = people[person_id]
            name = person["name"]
            birth = person["birth"]
            print(f"ID: {person_id}, Name: {name}, Birth: {birth}")
        try:
            person_id = input("Intended Person ID: ")
            if person_id in person_ids:
                return person_id
        except ValueError:
            pass
        return None
    else:
        return person_ids[0]


def neighbors_for_person(person_id):
    """
    Returns (movie_id, person_id) pairs for people
    who starred with a given person.

    Action function.
    """
    movie_ids = people[person_id]["movies"]
    neighbors = set()
    for movie_id in movie_ids:
        for person_id in movies[movie_id]["stars"]:
            neighbors.add((movie_id, person_id))
    return neighbors


if __name__ == "__main__":
    main()
