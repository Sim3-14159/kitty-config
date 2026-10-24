# from kitty.fast_data_types import Screen
# from kitty.tab_bar import (
#     DrawData,
#     TabBarData,
#     ExtraData,
#     draw_tab_with_powerline,
#     draw_title,
# )
#
#
# def draw_tab(
#     draw_data: DrawData,
#     screen: Screen,
#     tab: TabBarData,
#     before: int,
#     max_title_length: int,
#     index: int,
#     is_last: bool,
#     extra_data: ExtraData,
# ) -> int:
#     """
#     Kitty's DrawData is defined here:
#     https://github.com/kovidgoyal/kitty/blob/master/kitty/tab_bar.py#L58
#     """
#
#     layout_icon = ""
#     if tab.layout_name == "tall":
#         layout_icon = " "
#     elif tab.layout_name == "vertical":
#         layout_icon = " "
#     elif tab.layout_name == "horizontal":
#         layout_icon = " "
#     elif tab.layout_name == "stack":
#         layout_icon = " "
#     elif tab.layout_name == "fat":
#         layout_icon = " "
#     elif tab.layout_name == "grid":
#         layout_icon = " "
#     elif tab.layout_name == "splits":
#         layout_icon = " "
#
#     new_draw_data = draw_data._replace(
#         title_template="{fmt.fg.red}{bell_symbol}{activity_symbol}{fmt.fg.tab}"
#         # + "{sup.index}󰘳  "
#         # + layout_icon
#         # + "{sub.num_windows}"
#         # + " "
#         # + "󰉋 {tab.active_wd.rsplit('/', 1)[-1] or '/'}"
#         # + " "
#         # + " {tab.active_exe}"
#         # + " {title}"
#         # active_title_template inherits title_template if nil
#         + "{sup.num_windows + '"
#         + layout_icon
#         + "'+' ' if num_windows > 1 else ('  ' if title.startswith('tmux ') else '')}"
#         # + "{sub.num_windows} {title} 󰉋 {tab.active_wd.rsplit('/')[-1] or '/'}"
#         + "{title.removeprefix('tmux ')}"
#     )
#
#     return draw_tab_with_powerline(
#         new_draw_data, screen, tab, before, max_title_length, index, is_last, extra_data
#     )

from kitty.fast_data_types import Screen
from kitty.tab_bar import (
    DrawData,
    ExtraData,
    TabBarData,
    Formatter,
    draw_title,
    as_rgb,
    draw_attributed_string,
)
from kitty.utils import color_as_int


def draw_tab(
    draw_data: DrawData,
    screen: Screen,
    tab: TabBarData,
    before: int,
    max_title_length: int,
    index: int,
    is_last: bool,
    extra_data: ExtraData,
) -> int:

    orig_fg = screen.cursor.fg
    orig_bg = screen.cursor.bg
    left_sep, right_sep = ("", "")

    def draw_sep(which: str) -> None:
        screen.cursor.bg = as_rgb(color_as_int(draw_data.default_bg))
        screen.cursor.fg = orig_bg
        screen.draw(which)
        screen.cursor.bg = orig_bg
        screen.cursor.fg = orig_fg

    if max_title_length <= 1:
        screen.draw("…")
    elif max_title_length == 2:
        screen.draw("…|")
    elif max_title_length < 6:
        draw_sep(left_sep)
        screen.draw(
            (" " if max_title_length == 5 else "")
            + "…"
            + (" " if max_title_length >= 4 else "")
        )
        draw_sep(right_sep)
    else:
        layout_icon = ""
        if tab.layout_name == "tall":
            layout_icon = " "
        elif tab.layout_name == "vertical":
            layout_icon = " "
        elif tab.layout_name == "horizontal":
            layout_icon = " "
        elif tab.layout_name == "stack":
            layout_icon = " "
        elif tab.layout_name == "fat":
            layout_icon = " "
        elif tab.layout_name == "grid":
            layout_icon = " "
        elif tab.layout_name == "splits":
            layout_icon = " "

        draw_sep(left_sep)
        new_draw_data = draw_data._replace(
            title_template="{fmt.fg.red}{bell_symbol}{activity_symbol}{fmt.fg.tab}"
            # + "{sup.index}󰘳  "
            # + layout_icon
            # + "{sub.num_windows}"
            # + " "
            # + "󰉋 {tab.active_wd.rsplit('/', 1)[-1] or '/'}"
            # + " "
            # + " {tab.active_exe}"
            # + " {title}"
            # active_title_template inherits title_template if nil
            + "{sup.num_windows + '"
            + layout_icon
            + "'+' ' if num_windows > 1 else ('  ' if title.startswith('tmux ') else '')}"
            # + "{sub.num_windows} {title} 󰉋 {tab.active_wd.rsplit('/')[-1] or '/'}"
            # + "{title.removeprefix('tmux ')}"
            + "{title[0]+'\033[36m󰉋'+title[1] if len(title:=title.removeprefix('tmux ').rsplit('󰉋', 1)) > 1 else title[0]}"
        )  # screen.draw(" ")
        draw_title(new_draw_data, screen, tab, index)

        extra = screen.cursor.x - before - max_title_length
        print(f"extra:{extra}")
        if extra >= 0:
            screen.cursor.x -= extra + 3
            screen.draw("…")
        elif extra == -1:
            screen.cursor.x -= 2
            screen.draw("…")
        # screen.draw(" ")
        draw_sep(right_sep)
        draw_sep(" ")

    return screen.cursor.x
