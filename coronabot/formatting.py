def _indent(key, max_length):
    return " " * (max_length - len(key))


def format_stats(stats):
    text = ""
    max_length = max(len(x) for x in stats.keys())
    for key, value in stats.items():
        text += f"{key}: {_indent(key, max_length)}"
        if isinstance(value, dict):
            text += f"{value['total']} (+{value['new']})\n"
        else:
            text += f"{value}\n"
    return text
