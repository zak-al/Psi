# PSI
_Psi_ helps you create simple pseudocode images.
It supports basic code highlighting, based on the following categories of tokens:
* keywords,
* operators,
* brackets,
* comments,
* numeric sequences,
* built-in identifiers,
* strings,
* _default_ (typically identifiers)

Keywords, operators and built-in identifiers can be customised by setting values in the `parameters` dictionary (`KEYWORDS`, `OPERATORS` and `BUILT_IN_IDENTIFIERS`, respectively).

Strings are necessarily delimited by double quotes `"` and treats escaped quotes as ordinary quotes.

For the moment, _Psi_ only supports inline comments. This means that a comment necessarily ends at the end of the line where it started.
By default, comments start with a double slash: `//`. This can be changed by modifying `parameters[INLINE_COMMENT_START]`.

### Themes, background

The theme determines syntax highlighting. For the moment, there only exists one theme: `light`.
A theme is represented by a dictionary which maps token_types to tuples representing RGB values between 0 and 255. For example:

```
"light": {"keyword": (61, 90, 254),
          "operator": (84, 110, 122),
          "num": (76, 175, 80),
          "built-in": (255, 87, 34),
          "brackets": (144, 164, 174),
          "comment": (144, 164, 174),
          "default": (170, 0, 255),
          "string": (76, 175, 80),
          "line_number": (120, 144, 156)}
```

You can create your own theme by setting `parameters[THEME]`. The default value is _light_, but it can be a dictionary as well.

Finally, the default background is light-grey: RGB(245, 245, 245). You can change it by setting `parameters["BACKGROUND"]`.
You can assign your own colour (represented by a tuple) or one of the values contained in class `Background`.
For the moment, these colours are `white` (default) and `black`, which is a "light black" with value (10, 10, 10).

### Ligatures

_Psi_ supports some simple ligatures. They include weak equalities (`<=` and `>=`) and infinity (`+infinity`, `-infinity` and `infinity`).
They are enabled by default, but can be disabled by passing `ligatures=False` to the constructor of `Snippet` (see below for a tutorial on how to create Snippets).

---

## Create your image

Here is how you can create an image:

1. Create a snippet. The constructor takes a single parameter: the name of the snippet. It will be used to name the image file, so you should avoid spaces and other fancy characters.

```
snippet = Psi.Snippet("fibonacci")
```
It takes an optional parameter, `ligatures`, of type `bool`.

2. Add lines with `Snippet.add`. It takes two parameters: the content (of type `str`) and the level of indentation (of type `int`, optional with default value 0):

```
snippet.add("function fibonacci x")
snippet.add("if x = 0 or x = 1 then x", 1)
snippet.add("else", 1)
snippet.add("fibonacci (x - 1) + fibonacci (x - 2)", 2)
```

3. Generate the image using `Snippet.generate`.
   Note that the height of the image is adaptive, but the width is not.
   You can adjust it by tweaking the parameter of `generate`
   (default value is 500 pixels):

```
snippet.generate(1000)
```

---

## Reasonable improvements I hope to implement someday:

- Support single-quoted strings
- A built-in dark theme, and some other themes
- Adaptive image width
