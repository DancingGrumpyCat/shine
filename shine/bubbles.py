from collections import namedtuple

Position = namedtuple('Position', ['x', 'y'])

class Bubble:
    @classmethod
    def from_json(cls, data):
        uuid = data["uuid"]
        position = Position(data["position"]["x"], data["position"]["y"])
        name = data["name"]
        formula = parse_formula(data["formula"])

        return cls(uuid, position, name, formula)

    def __init__(self, uuid, position, name, formula):
        self.uuid = uuid
        self.position = position
        self.name = name
        self.formula = formula

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Bubble({self.uuid}, {self.position}, {self.name}, {self.formula})"

def parse_formula(formula):
    match formula["type"]:
        case "literal_string":
            return StringLiteral(formula["value"])
        # case "number_literal":
        #     return NumberLiteral(formula["value"])
        case "reference":
            return Reference(formula["value"])
        case "function_call":
            return FunctionCall(
                parse_formula(formula["function"]),
                parse_formula(formula["argument"]))

class Formula:
    type = "generic_formula"

    def eval(self, universe: dict[str, Bubble]):
        raise NotImplementedError("eval() must be implemented by subclasses")

class StringLiteral(Formula):
    type = "string_literal"

    def __init__(self, value):
        self.value = value

    def eval(self, universe):
        return self.value

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"StringLiteral({self.value})"

class Reference(Formula):
    type = "reference"

    def __init__(self, value):
        self.value = value

    def eval(self, universe):
        found = None

        # try to find by UUID
        from_uuid = universe.get(self.value)
        if from_uuid is not None:
            found = from_uuid

        # try to find by name
        for bubble in universe.values():
            if bubble.name == self.value:
                found = bubble

        if found is None:
            raise ValueError(f"Reference to non-existent bubble: {self.value}")
        if found.formula is None:
            raise ValueError(f"Reference to bubble with no formula: {self.value}")
        return found.formula.eval(universe)

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"Reference({self.value})"

class FunctionCall(Formula):
    type = "function_call"

    def __init__(self, function, argument):
        self.function = function
        self.argument = argument

    def eval(self, universe):
        return self.function.eval(universe)(self.argument.eval(universe))

    def __str__(self):
        return repr(self)

    def __repr__(self):
        return f"FunctionCall({self.function}, {self.argument})"
