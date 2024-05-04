def calculate_frequencies(incidents, attribute):
    """
    Calculate the frequencies of a given attribute (location or nature) in the incidents.
    """
    from collections import Counter
    values = [incident[attribute] for incident in incidents]
    frequencies = Counter(values)
    return frequencies

def assign_ranks(frequencies):
    """
    Assign ranks to each unique value based on its frequency, handling ties appropriately.
    """
    # Sort items based on frequency, then by the value itself for consistent ordering
    sorted_items = sorted(frequencies.items(), key=lambda x: (-x[1], x))
    ranks = {}
    current_rank = 1
    for i, (value, freq) in enumerate(sorted_items, start=1):
        # If it's the first item or if the current frequency is different from the previous one,
        # update the current rank to be the current position (i).
        if i == 1 or freq < sorted_items[i-2][1]:
            current_rank = i
        ranks[value] = current_rank
    return ranks

