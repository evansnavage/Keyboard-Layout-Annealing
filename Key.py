class Key:
    FINGER_RANGES = {
        # Left Hand
        "L_pinky": (
            0,
            1.5,
        ),
        "L_ring": (1.5, 2.8),
        "L_middle": (2.8, 4.0),
        "L_index": (4.0, 5.8),
        # Right Hand
        "R_index": (5.8, 8.0),
        "R_middle": (8.0, 9.8),
        "R_ring": (9.8, 11.8),
        "R_pinky": (
            11.8,
            15.0,
        ),
    }
    FINGER_COST = {
        "L_pinky": 1.5,
        "L_ring": 1.2,
        "L_middle": 1.1,
        "L_index": 1.0,
        "R_index": 1.0,
        "R_middle": 1.1,
        "R_ring": 1.2,
        "R_pinky": 1.5,
        "Unknown": 3.0,
    }

    def __init__(
        self,
        base,
        shift,
        is_immutable=False,
        is_immovable=False,
        location=None,
        frequency=0,
    ):
        self.base = base
        self.shift = shift
        self.is_immovable = is_immovable
        self.location = location
        self.is_immutable = is_immutable  # prevent desyncing a from A, but allow 7 to have a symbol other than & eventually
        self.frequency = frequency  # how often the key appears in the corpus

    def set_location(self, location):
        self.location = location

    def __repr__(self):
        return (
            f"Key(base='{self.base}', shift='{self.shift}', location={self.location})"
        )

    def distance_from_home_row(self):
        """How many rows away from the homerow the key is"""
        if self.location is None:
            return 100
        home_row = 2
        distance = home_row - self.location[1]
        return abs(distance)

    def euclidean_distance(self, other):
        if self.location is None or other.location is None:
            return float("inf")
        return (
            (self.location[0] - other.location[0]) ** 2
            + (self.location[1] - other.location[1]) ** 2
        ) ** 0.5

    def manhattan_distance(self, other):
        if self.location is None or other.location is None:
            return float("inf")
        return abs(self.location[0] - other.location[0]) + abs(
            self.location[1] - other.location[1]
        )

    def is_adjacent(self, other, threshold=1.5):
        """Determines if 2 keys are next to eachother, threshold determines how strict we are."""
        if self.location is None or other.location is None:
            return False
        distance = self.euclidean_distance(other)
        return distance < threshold

    def get_neighbors(self, keys):
        """Returns a list of all the keys surrounding a given key"""
        neighbors = []
        for key in keys:
            if self.is_adjacent(key):
                neighbors.append(key)
        return neighbors

    def get_finger(self):
        """Returns the key that should be used for typing it if touch typing."""
        if self.location is None:
            return None
        for finger, (start, end) in self.FINGER_RANGES.items():
            if start <= self.location[0] <= end:
                return finger
        return None

    def get_finger_cost(self):
        """Gets the finger for the key then the cost of typing with that finger"""
        finger = self.get_finger()
        if finger is None:
            return self.FINGER_COST["Unknown"]
        return self.FINGER_COST[finger]

    def score(self, HR_WEIGHT, FINGER_WEIGHT):
        """Returns the sum of finger expense and distance from homerow * the given weights"""
        score = self.distance_from_home_row() * HR_WEIGHT
        score += self.get_finger_cost() * FINGER_WEIGHT
        return score
