def comment_magic_in_line(input, **kwargs):
    if input.startswith("%") or input.startswith("!"):
        input = "# " + input
    return input

def comment_magics(input, **kwargs):
    input_lines = input.split("\n")
    return "\n".join([comment_magic_in_line(line) for line in input_lines])

c = get_config()
c.Exporter.filters = {"comment_magics": comment_magics}