from Key import Key
import json
from collections import Counter, defaultdict
import random
from layout_renderer import render_keyboard
import matplotlib.pyplot as plt
import math


class KeyboardLayout:
    def __init__(self, layout, corpus):
        self.layout = {}
        with open(layout, "r") as f:
            layout_json = json.load(f)
            self.frequencies, self.bigrams = self.generate_frequencies(corpus)
            self.construct(layout_json)

    def get_key(self, location):
        """Returns a key given it's location."""
        return self.layout.get(location, None)

    def get_location(self, key: str):
        """Returns a location given either the base or shift."""
        for loc, k in self.layout.items():
            if k.base == key or k.shift == key:
                return loc
        return None

    def swap_keys(self, key1: Key, key2: Key):
        """Swaps the locations of 2 keys in the layout
        Silently fails if either key is immovable (shift, enter, backspace)
        """
        if key1.is_immovable or key2.is_immovable:
            return

        loc1 = key1.location
        loc2 = key2.location

        self.layout[loc1], self.layout[loc2] = self.layout[loc2], self.layout[loc1]

        # Update key locations
        key1.set_location(loc2)
        key2.set_location(loc1)

    def evaluate_bigram_score(self, same_finger_penalty=3.0, same_hand_penalty=1.5):
        """Complex scoring algorithm, scores the bigrams (combinations of 2 letters) from the dataset
        Punishes using the same finger (a lot) and same hand(a little) being used in the bigram
        """
        total_score = 0
        for bigram, freq in self.bigrams.items():
            loc1 = self.get_location(bigram[0])
            loc2 = self.get_location(bigram[1])

            if loc1 and loc2:
                key1 = self.layout[loc1]
                key2 = self.layout[loc2]

                # Old method
                # base_cost = key1.euclidean_distance(key2)

                penalty = 0
                finger1 = key1.get_finger()
                finger2 = key2.get_finger()

                if finger1 and finger2:
                    if finger1 == finger2:
                        penalty = same_finger_penalty
                    else:
                        hand1 = finger1.split("_")[0]
                        hand2 = finger2.split("_")[0]
                        if hand1 == hand2:
                            penalty = same_hand_penalty

                total_score += penalty * freq

        return total_score

    def evaluate_total_score(
        self,
        home_row_weight=1,
        finger_weight=1,
        bigram_weight=1,
        same_finger_penalty=3.0,
        same_hand_penalty=1.5,
    ):
        """Sums the scores from bigrams and the scoring function in key"""
        total_score = 0
        for key in self.layout.values():
            if key.frequency > 0:
                total_score += key.score(home_row_weight, finger_weight) * key.frequency
        bigram_score = self.evaluate_bigram_score(
            same_finger_penalty, same_hand_penalty
        )
        total_score += bigram_score * bigram_weight

        return total_score

    def __str__(self):
        return str(self.layout)

    def construct(self, layout_json):
        """Constructs a keyboard layout from a properly formed json file"""
        for row in layout_json["layout"]:
            for key_data in row:
                if "name" in key_data:
                    key = Key(
                        base=key_data["name"],
                        shift=key_data["name"],
                        is_immutable=True,
                        is_immovable=True,
                        location=(key_data["x"], key_data["y"]),
                        frequency=0,
                    )
                else:
                    key = Key(
                        base=key_data["base"],
                        shift=key_data["shift"],
                        is_immutable=(
                            key_data["base"].isalpha() and key_data["shift"].isalpha()
                        ),
                        location=(key_data["x"], key_data["y"]),
                        frequency=self.frequencies.get(key_data["base"].lower(), 0),
                    )
                self.layout[key.location] = key
        return self

    def swap_shifts(self, key1: Key, key2: Key):
        """Swaps only the shift layer for 2 keys
        Silently fails if either key is immutable (letters),
        either key is immovable, or either key doesn't change when shift is held"""
        if key1.is_immutable or key2.is_immutable:
            return
        if key1.base == key1.shift or key2.base == key2.shift:
            return
        if key1.is_immovable or key2.is_immovable:
            return

        key1_shift = key1.shift
        key2_shift = key2.shift

        key1.shift = key2_shift
        key2.shift = key1_shift

    def generate_frequencies(self, corpus):
        """Given a corpus of text as a string, generates the bigram and single letter frequencies"""
        single_frequencies = Counter()
        bigram_frequencies = Counter()
        lines = corpus.splitlines()
        for i in range(len(lines)):
            line = lines[i]
            for j in range(len(line) - 1):
                bigram = (line[j].lower(), line[j + 1].lower())
                bigram_frequencies[bigram] += 1
        for line in corpus:
            for char in line:
                char = char.lower()
                single_frequencies[char] += 1

        return single_frequencies, bigram_frequencies

    def write_json(self, filename="output_layout.json"):
        """Writes out a layout to a json file, for loading or visualizing"""
        rows_dict = defaultdict(list)
        for loc, key in self.layout.items():
            if loc is None or not isinstance(loc, tuple) or len(loc) != 2:
                print(f"Warning: Skipping key {key.base} with invalid location {loc}")
                continue
            x, y = loc
            key_data = {
                "base": key.base,
                "shift": key.shift,
                "x": x,
                "y": y,
            }
            if key.is_immovable:
                key_data = {"name": key.base, "x": x, "y": y}

            rows_dict[y].append(key_data)

        # Sort rows by y-coordinate
        sorted_rows = sorted(rows_dict.items())

        layout_json = {"layout": []}
        for y, keys_in_row in sorted_rows:
            sorted_keys_in_row = sorted(keys_in_row, key=lambda k: k["x"])
            layout_json["layout"].append(sorted_keys_in_row)

        try:
            with open(filename, "w") as f:
                json.dump(layout_json, f, indent=4)
            print(f"Layout successfully written to {filename}")
        except IOError as e:
            print(f"Error writing layout to {filename}: {e}")
        except TypeError as e:
            print(f"Error serializing layout data to JSON: {e}")


### Scoring Parameters
home_row_weight = 1.0
finger_weight = 1.0
bigram_weight = 1.0

# Multiplied by the weights to make each contribute equally
# With each weight = 1 the score for Dvorak should be 30,000 +/- 5, Qwerty gets ~46,000; If not i've screwed up one of the scoring parameters
home_row_balance_factor = 0.012034
finger_balance_factor = 0.003825
bigram_balance_factor = 0.007701

# Penalties
same_finger_penalty = 4.0
same_hand_penalty = 1.5

# Apply those balance factors from earlier
home_row_weight *= home_row_balance_factor
finger_weight *= finger_balance_factor
bigram_weight *= bigram_balance_factor

### Annealing Parameters
temperature = (
    2**40 - 1
)  # starting temperature, higher is correlated with better results but takes longer
cooling_rate = 0.995  # temperature is multiplied by this each iteration, 0.95-0.999 give various levels of good in exchange for time

iterations = math.ceil(
    math.log(1 / temperature) / math.log(cooling_rate)
)  # calculate how many iterations it'll take
print(f"Number of iterations: {iterations:.2f}")

verbose = False  # Prints each swap made and the effect, very cool to look at but not useful and slow
random.seed(1)
corpus_file = "./Processed Corpi/corpusJava.txt"

### Manual Testing the Score Function
with open(corpus_file, "r") as f:
    corpus = f.read()
qwerty = KeyboardLayout("./qwerty.json", corpus)
qwerty_score = qwerty.evaluate_total_score(
    home_row_weight=home_row_weight,
    finger_weight=finger_weight,
    bigram_weight=bigram_weight,
    same_finger_penalty=same_finger_penalty,
    same_hand_penalty=same_hand_penalty,
)
print(f"Total Score (QWERTY): {qwerty_score:.2f}")
dvorak = KeyboardLayout("./dvorak.json", corpus)
dvorak_score = dvorak.evaluate_total_score(
    home_row_weight=home_row_weight,
    finger_weight=finger_weight,
    bigram_weight=bigram_weight,
    same_finger_penalty=same_finger_penalty,
    same_hand_penalty=same_hand_penalty,
)
print(f"Total Score (Dvorak): {dvorak_score:.2f}")

print(f"Dvorak Improvement: {(qwerty_score - dvorak_score) / qwerty_score * 100:.2f}%")


def should_accept(new_score, current_score, temperature):
    """Helper function, returns true if the new score is better or randomly based on how high the temperature is"""
    return new_score < current_score or random.random() < math.exp(
        (current_score - new_score) / temperature
    )


def score(layout: KeyboardLayout):
    """Wrapper for this 7 line function call"""
    return layout.evaluate_total_score(
        home_row_weight=home_row_weight,
        finger_weight=finger_weight,
        bigram_weight=bigram_weight,
        same_finger_penalty=same_finger_penalty,
        same_hand_penalty=same_hand_penalty,
    )


def anneal(
    temperature,
    cooling_rate,
    starting_layout,
    allow_shift_layer_swaps=False,
    verbose=False,
):
    """Main loop
    Score
    Modify
    Score
    ...
    Less likely to accept changes that decrease score as temperature goes down
    """
    scores_over_time = []
    top10_changes = []
    current_score = score(starting_layout)
    best_layout = starting_layout
    best_score = current_score

    iteration_count = 0

    while temperature > 1:
        locations = list(starting_layout.layout.keys())
        loc1, loc2 = random.sample(locations, 2)
        key1 = starting_layout.layout[loc1]
        key2 = starting_layout.layout[loc2]

        did_shift_swap = False

        if random.random() < 0.5 and allow_shift_layer_swaps:
            starting_layout.swap_shifts(key1, key2)
            did_shift_swap = True
        else:
            starting_layout.swap_keys(key1, key2)

        new_score = score(starting_layout)

        improvement = (current_score - new_score) / current_score * 100

        if should_accept(new_score, current_score, temperature):
            if verbose:
                print(
                    f"Accepted | Swapping {key1.base} and {key2.base} | Improvement: {improvement:.2f}%"
                )
            current_score = new_score
            if current_score < best_score:
                best_score = current_score
                best_layout = starting_layout
                # filling in the top 10 changes we made, comment at the bottom of file as to why this is unused
                if len(top10_changes) < 10:
                    top10_changes.append((key1, key2, improvement))
                else:
                    min_improvement = min(top10_changes, key=lambda x: x[2])[2]
                    if improvement > min_improvement:
                        top10_changes.remove(min(top10_changes, key=lambda x: x[2]))
                        top10_changes.append((key1, key2, improvement))
            scores_over_time.append(1 / new_score)
        else:
            if verbose:
                print(
                    f"Declined | Swapping {key1.base} and {key2.base} | Improvement: {improvement:.2f}%"
                )
            if did_shift_swap:
                starting_layout.swap_shifts(key1, key2)
            else:
                starting_layout.swap_keys(key1, key2)

        # Cool down the temperature
        temperature *= cooling_rate

        iteration_count += 1
        percentage_done = iteration_count / iterations * 100
        if iteration_count % 50:
            # Print progress bar
            bar_length = 50
            filled_length = int(bar_length * percentage_done / 100)
            bar = "=" * filled_length + "-" * (bar_length - filled_length)
            print(
                f"\rProgress: [{bar}] {percentage_done:.2f}% | Temperature: {temperature:.2f}",
                end="",
            )

    qwerty_improvement = (qwerty_score - best_score) / qwerty_score * 100

    return best_layout, best_score, qwerty_improvement, scores_over_time, top10_changes


random.seed(400)

best_layout, best_score, improvement, scores_over_time, top10_changes = anneal(
    temperature, cooling_rate, dvorak, True
)
print(f"Best Layout Score: {best_score:.2f}")
print(f"Best Layout Improvement over qwerty: {improvement:.2f}%")
best_layout.write_json("best_annealed_layout.json")

with open("best_annealed_layout.json", "r") as f:
    keyboard_layout_json = f.read()
keyboard_layout = json.loads(keyboard_layout_json)
render_keyboard(keyboard_layout)

### This isn't the best changes compared to qwerty, but compared to the previous state
### So it's acually not super useful
# print("TOP 10 CHANGES:")
# top10_changes.sort(key=lambda x: x[2], reverse=True)
# for change in top10_changes:
#     key1, key2, improvement = change
#     print(f"Swapped {key1.base} and {key2.base} | Improvement: {improvement:.2f}%")

plt.title("Score^-1 over Time (Higher is Better)")
plt.plot(scores_over_time)
plt.axhline(
    y=1 / qwerty_score,
    color="r",
    linestyle="--",
    label=f"QWERTY (1/{qwerty_score:.2f})",
)
plt.axhline(
    y=1 / dvorak_score,
    color="g",
    linestyle="--",
    label=f"Dvorak (1/{dvorak_score:.2f})",
)
plt.xlabel("Iteration")
plt.ylabel("Score^-1")
plt.legend()
plt.show()
