from flag import flag
from jinja2 import Environment
from jinja2 import PackageLoader
from jinja2 import select_autoescape


def datetimeformat(value, fmt="%Y-%m-%d %H:%M"):
    return value.strftime(fmt)


def _indent(key, max_length):
    return " " * (max_length - len(key))


def format_stats(stats, country_info, last_updated):
    template = _env.get_template("stats.j2")

    return template.render(
        stats=stats, country_info=country_info, last_updated=last_updated
    )


_env = Environment(
    loader=PackageLoader("coronabot", "templates"),
    autoescape=select_autoescape(["html", "xml"]),
    lstrip_blocks=True,
    trim_blocks=True,
)
_env.filters["flag"] = flag
_env.filters["pad"] = _indent
_env.filters["datetimeformat"] = datetimeformat
