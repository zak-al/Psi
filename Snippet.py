import re
import sys

from PIL import Image, ImageDraw, ImageFont

LINE_NUMBER_OFFSET = 20
INDENTATION = 60

indentation = lambda x: 30 + LINE_NUMBER_OFFSET + INDENTATION * x
line = lambda x: 30 + (FONT_SIZE * 2) * x

isdigit_regex = re.compile(r"(^-?[0-9]*\.?[0-9]*$)|(^[+|-]infinity$)")
tokeniser_regex = re.compile(r"(\s|\[|]|\(|\)|{|})")
isstring_regex = re.compile(r"\"[^\"]+\"")

FONT_SIZE = 25

COMMENT_DELIMITER = "//"

class Backgrounds:
    black = (10, 10, 10)
    white = (245, 245, 245)


KEYWORDS = ("let", "rec", "if", "then", "else", "function", "Array", "Set", "for", "and", "or")


def isBracket(text):
    return text in ("(", ")", "[", "]", "{", "}")


def isOperator(text):
    if text in ("=", "<", ">", "<=", ">=", "+", "-", "*", "/", ",", "..", "<-"):
        return True


def isNumericSequence(text):
    return re.search(isdigit_regex, text) is not None


def isBuiltInFunction(text):
    return text in ("max", "min")


def isString(text):
    return re.search(isstring_regex, text) is not None


COLOURS = {
    "light": {"keyword": (61, 90, 254),
              "operator": (84, 110, 122),
              "num": (76, 175, 80),
              "built-in": (255, 87, 34),
              "brackets": (144, 164, 174),
              "comment": (144, 164, 174),
              "default": (170, 0, 255),
              "string": (76, 175, 80),
              "line_number": (120, 144, 156)}
}


LIGATURES = {
    "<=": u"\u2264",
    ">=": u"\u2265",
    "+infinity": u"+\u221E",
    "-infinity": u"-\u221E",
    "infinity": u"\u221E"
}


parameters = {
    "INLINE_COMMENT_START": COMMENT_DELIMITER,
    "THEME": "light",
    "KEYWORDS": KEYWORDS,
    "BACKGROUND": Backgrounds.white,
    "CODE_FONT": "Inconsolata-SemiBold.ttf",
    "LINE_NUMBERS_FONT": "Inconsolata-Light.ttf",
}

def getCoulours():
    if type(parameters["THEME"]) == str:
        if parameters["THEME"] not in COLOURS:
            print(
                f"""Error: theme should have type string and value in {COLOURS.keys()},
                or type dict and map token types to RGB colours.
                Got string with value {parameters["THEME"]} instead.""")

            raise Exception
        return COLOURS[parameters["THEME"]]
    else:
        return parameters["THEME"]


class Token:
    def setColour(self):
        Colour = getCoulours()
        keywords = parameters["KEYWORDS"]
        content = self.content

        if self.comment:
            self.colour = Colour["comment"]
        elif content in keywords:
            self.colour = Colour["keyword"]
        elif isOperator(content):
            self.colour = Colour["operator"]
        elif isNumericSequence(content):
            self.colour = Colour["num"]
        elif isString(content):
            self.colour = Colour["string"]
        elif isBracket(content):
            self.colour = Colour["brackets"]
        elif isBuiltInFunction(content):
            self.colour = Colour["built-in"]
        else:
            self.colour = Colour["default"]

    def __init__(self, content: str, comment=False, ligatures=True):
        self.comment = comment

        if ligatures:
            for sequence, replacement in LIGATURES.items():
                content = content.replace(sequence, replacement)

        self.content = content
        self.setColour()


class Snippet:
    def __init__(self, name: str, ligatures: bool = True):
        self.name = name
        self.lines = []
        self.background = parameters["BACKGROUND"]
        self.ligatures = ligatures

    def add(self, content: str, indentation_level=0):
        tokens = []
        comment = False

        for tok in re.split(tokeniser_regex, content):
            comment = comment or tok == COMMENT_DELIMITER

            tokens.append(Token(tok, comment=comment, ligatures=self.ligatures))

        self.lines.append((indentation_level, tokens))

    def generate(self, width=500):
        Colour = getCoulours()

        font = ImageFont.truetype(parameters["CODE_FONT"], FONT_SIZE)
        line_number_font = ImageFont.truetype(parameters["LINE_NUMBERS_FONT"], FONT_SIZE)

        height = line(len(self.lines)) + line(0)
        image = Image.new("RGB", (width, height), color=self.background)
        d = ImageDraw.Draw(image)

        for line_number, (indentation_level, tokens) in enumerate(self.lines):
            d.text(
                (LINE_NUMBER_OFFSET, line(line_number)),
                str(line_number + 1),
                fill=Colour["line_number"],
                font=line_number_font
            )

            inline_horizontal_offset = font.getsize(str(len(self.lines)))[0]

            for token_number, token in enumerate(tokens):
                d.text(
                    (indentation(indentation_level) + inline_horizontal_offset, line(line_number)),
                    token.content,
                    fill=token.colour,
                    font=font
                )

                inline_horizontal_offset += font.getsize(token.content)[0]

        image.save(f"{self.name}.png")