Started as a final project for Introduction to Computational Mathematics; Now occasionally devours an evening adding a new feature.

Requires matplotlib.

Simulated Annealing algorithm that generates keyboard layouts that succeed on a few heuristics. At the moment those are:

    - Move Frequent Characters to the Homerow
    - Frequent Bigrams should alternate hands as often as possible
    - Stronger fingers should be used more often than weaker ones

The weights and parameters for all of the heuristics are relatively easily to modify, but are split between files.

Coming "Soon":

    - Progress Bar ✅
    - Fix verbose mode
    - Easier to configure parameters and weights
    - Heatmap for key comfort instead of guessing based on row and finger
    - Export to QMK json format
    - Actually test the generated keyboards; is it worth switching keyboard layouts specific to use cases?
    - More Corpi

Haven't provided any corpi becasue of licenses, but the program expects them as single text files with a hardcoded path. I've provided a couple of scripts that I threw together to quickly make corpi workable with this limitation.
