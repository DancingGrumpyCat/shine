import json
import shine.bubbles as bubbles
from pathlib import Path

path_to_example_json = Path(__file__).parent / 'example.json'
with open(path_to_example_json, 'r') as f:
    example_data = json.load(f)

def test_parse_bubbles():
    example_bubbles = [
        bubbles.Bubble.from_json(data)
        for data in example_data
    ]
    assert len(example_bubbles) == 2

def test_eval_bubbles():
    # parse bubbles

    example_bubbles = [
        bubbles.Bubble.from_json(data)
        for data in example_data
    ]

    universe = {
        bubble.uuid: bubble
        for bubble in example_bubbles
    }

    # create builtin

    class StrlenFormula(bubbles.Formula):
        def eval(self, universe):
            return len

    universe["immaterial-uuid"] = bubbles.Bubble(
        uuid="immaterial-uuid",
        position=(0, 0),
        name="strlen",
        formula=StrlenFormula()
    )

    # evaluation

    bubble = universe["this-is-another-uuid"]
    result = bubble.formula.eval(universe)
    assert result == len("Hello, world!")
