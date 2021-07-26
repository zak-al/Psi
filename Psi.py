import re

from PIL import Image, ImageDraw, ImageFont

LINE_NUMBER_OFFSET = 20
INDENTATION = 60

FONT_SIZE = 25

indentation = lambda x: 30 + LINE_NUMBER_OFFSET + INDENTATION * x
line = lambda x: 30 + (FONT_SIZE * 3) * x

isdigit_regex = re.compile(r"(^-?[0-9]*\.?[0-9]*$)|(^[+|-]infinity$)")

tokeniser_regex = re.compile(r"(\s|\[|]|\(|\)|{|}|,|:|\||<=|>=|->|<-|<|>|\.)")

#isstring_regex = re.compile(r"""/"(?:[^"\\]|\\.)*"/""")
isstring_regex = re.compile(r"\"[^\"]*\"")

COMMENT_DELIMITER = "//"


class Backgrounds:
    black = (10, 10, 10)
    white = (245, 245, 245)


KEYWORDS = {"let", "rec", "if", "then", "else", "function", "Array", "Array2D", "Set", "for", "and", "or", "type", "match", "with"}
OPERATORS = {"=", "!=", "<", ">", "<=", ">=", "+", "-", "*", "/", ",", "..", "<-", "<<", ">>", "|", "&", "|", ":", "."}
BUILT_IN_IDENTIFIERS = {"min", "max", "Length", "int"}

KEYWORDS_SQL = {"CREATE", "TABLE", "IF", "NOT", "EXISTS", "NULL", "PRIMARY", "KEY", "INSERT", "INTO", "VALUES", "SELECT", "WHERE", "FROM"}
BUILT_IN_SQL = {"varchar", "int", "float"}


def isBracket(text):
    return text in ("(", ")", "[", "]", "{", "}")


def isNumericSequence(text):
    return re.search(isdigit_regex, text) is not None


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
              "line_number": (120, 144, 156),
              "__highlight": (220, 220, 220)}
}


LIGATURES = {
    "<=": u"\u2264",
    ">=": u"\u2265",
    "+infinity": u"+\u221E",
    "-infinity": u"-\u221E",
    "infinity": u"\u221E",
    "pi": u"\u03C0",
    "!=": u"\u2260",
    #"->": u"\u1F812"
}


parameters = {
    "INLINE_COMMENT_START": COMMENT_DELIMITER,
    "THEME": "light",
    "KEYWORDS": KEYWORDS,
    "OPERATORS": OPERATORS,
    "BACKGROUND": Backgrounds.white,
    "CODE_FONT": "RobotoMono-SemiBold.ttf",
    "LINE_NUMBERS_FONT": "RobotoMono-Light.ttf",
    "BUILT_IN_IDENTIFIERS": BUILT_IN_IDENTIFIERS,
}


def getColours():
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


def getOperators():
    return parameters["OPERATORS"]


def getBuiltinIdentifiers():
    return parameters["BUILT_IN_IDENTIFIERS"]


class Token:
    def setColour(self):
        Colour = getColours()
        operators = getOperators()
        built_in_identifiers = getBuiltinIdentifiers()

        keywords = parameters["KEYWORDS"]
        content = self.content

        if self.comment:
            self.colour = Colour["comment"]
        elif content in keywords:
            self.colour = Colour["keyword"]
        elif content in operators:
            self.colour = Colour["operator"]
        elif isNumericSequence(content):
            self.colour = Colour["num"]
        elif isString(content):
            self.colour = Colour["string"]
        elif isBracket(content):
            self.colour = Colour["brackets"]
        elif content in built_in_identifiers:
            self.colour = Colour["built-in"]
        else:
            self.colour = Colour["default"]

    def __init__(self, content: str, comment: bool = False, ligatures: bool = True):
        self.comment = comment
        self.content = content
        self.setColour()

        if ligatures:
            for sequence, replacement in LIGATURES.items():
                self.content = self.content.replace(sequence, replacement)


class PSnippet:
    def __init__(self, name: str, ligatures: bool = True):
        self.name = name
        self.lines = []
        self.background = parameters["BACKGROUND"]
        self.ligatures = ligatures

        self.colour = getColours()
        self.font = ImageFont.truetype(parameters["CODE_FONT"], FONT_SIZE)
        self.line_number_font = ImageFont.truetype(parameters["LINE_NUMBERS_FONT"], FONT_SIZE)

    def add(self, content: str, indentation_level: int = 0, highlighted: bool = False):
        tokens = []
        comment = False

        for tok in re.split(tokeniser_regex, content):
            comment = comment or tok == COMMENT_DELIMITER

            tokens.append(Token(tok, comment=comment, ligatures=self.ligatures))

        self.lines.append((indentation_level, tokens, highlighted))

    def print_line(self, d, indentation_level, height_offset, line_number, tokens):
        d.text(
            (LINE_NUMBER_OFFSET, height_offset),
            str(line_number + 1),
            fill=self.colour["line_number"],
            font=self.line_number_font
        )

        inline_horizontal_offset = self.font.getsize(str(len(self.lines)))[0]

        for token_number, token in enumerate(tokens):
            d.text(
                (indentation(indentation_level) + inline_horizontal_offset, height_offset),
                token.content,
                fill=token.colour,
                font=self.font
            )

            inline_horizontal_offset += self.font.getsize(token.content)[0]

    def generate(self, width: int = 1000):
        height = line(len(self.lines)) + line(0)
        image = Image.new("RGB", (width, height), color=self.background)

        highlighted_images = []

        d = ImageDraw.Draw(image)

        for line_number, (indentation_level, tokens, highlighted) in enumerate(self.lines):
            if highlighted:
                height_before = line(line_number)
                height_offset = ( (line(2) - line(1) ) - self.font.getsize(str(len(self.lines)))[1] ) // 2
                h_image = Image.new("RGB", (width, line(line_number + 1) - height_before), color=self.colour["__highlight"])
                h_d = ImageDraw.Draw(h_image)

                self.print_line(h_d, indentation_level, height_offset, line_number, tokens)

                highlighted_images.append((height_before - height_offset, h_image))
                h_image.save("aaa.png")
            else:
                self.print_line(d, indentation_level, line(line_number), line_number, tokens)

        for vertical_offset, img in highlighted_images:
            image.paste(img, (0, vertical_offset))

        image.save(f"{self.name}.png")
        print(f"Image successfully saved to {self.name}.png.")
