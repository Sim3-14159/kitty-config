# ruff: ignore[I001]
import time
import os
from kitty.fast_data_types import Screen, add_timer  # pyright: ignore[reportMissingImports]
from kitty.boss import get_boss  # pyright: ignore[reportMissingImports]
from kitty.tab_bar import (  # pyright: ignore[reportMissingImports]
    DrawData,
    ExtraData,
    TabBarData,
    # Formatter,
    draw_title,
    as_rgb,
    # draw_attributed_string,
)
from kitty.utils import color_as_int  # pyright: ignore[reportMissingImports]


CPU_CORES = os.cpu_count() or 1


def _draw_right_status(screen: Screen) -> int:
    # Text or info you want to display on the far right
    load1minute = os.getloadavg()[0]
    approxCPUpercentage = int(load1minute / CPU_CORES * 100)

    right_text = f" ~{approxCPUpercentage}% {time.strftime(' %-I:%M')} "

    right_length = len(right_text)

    # Calculate spaces needed to push text to the far edge
    draw_spaces = screen.columns - screen.cursor.x - right_length
    if draw_spaces > 0:
        screen.draw(" " * draw_spaces)

    screen.draw(right_text)
    return screen.cursor.x


def _redraw_tab_bar(_timer_id: int | None) -> None:
    boss = get_boss()
    if boss is None:
        return
    tm = boss.active_tab_manager
    if tm is not None:
        tm.mark_tab_bar_dirty()
        # Force Kitty's main loop to repaint the OS window immediately
        w = tm.active_window
        if w is not None:
            boss.child_monitor.wakeup()


timer_id = None


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
    global timer_id

    if timer_id is None:
        timer_id = add_timer(_redraw_tab_bar, 2.0, True)  # Redraw tab bar every 2 secs

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
            title_template="{fmt.fg.yellow}{bell_symbol}{fmt.fg.tab}"
            # + " {tab.active_exe}"
            # + " {title}"
            # active_title_template inherits title_template if nil
            + "{fmt.fg.orange}"
            + "{sup.num_windows + '"
            + layout_icon
            + "'+' ' if num_windows > 1 else ('  ' if title.startswith('tmux ') else '')}"
            # + "{sub.num_windows} {title} 󰉋 {tab.active_wd.rsplit('/')[-1] or '/'}"
            # + "{title.removeprefix('tmux ')}"
            + "{fmt.fg.tab}"
            + "{'\033[4m' if activity_symbol else ''}{title[0]+'\033[36m󰉋'+title[1] if len(title:=title.removeprefix('tmux ').rsplit('󰉋', 1)) > 1 else title[0]}"
            + "\033[24m"  # no underline
        )  # screen.draw(" ")
        draw_title(new_draw_data, screen, tab, index)

        extra = screen.cursor.x - before - max_title_length
        # print(f"extra:{extra}")
        if extra >= 0:
            screen.cursor.x -= extra + 3
            screen.draw("…")
        elif extra == -1:
            screen.cursor.x -= 2
            screen.draw("…")
        # screen.draw(" ")
        draw_sep(right_sep)
        draw_sep(" ")

        if is_last:
            screen.cursor.italic = False
            screen.cursor.bold = False
            screen.cursor.bg = as_rgb(color_as_int(draw_data.default_bg))
            _draw_right_status(screen)

    return screen.cursor.x
