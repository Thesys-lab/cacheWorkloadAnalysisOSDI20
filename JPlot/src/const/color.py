
import itertools


##########################################################################################
COLOR_SOLID = itertools.cycle(("red", "blue", "green", "cyan", "magenta", "yellow", "black"))
COLOR_SOLID2 = itertools.cycle(('#000000', '#000088', "#008800", "#00ee00", "#ee0000", "#008888", "#0088ee", "#00ee88",
                "#00eeee", "#888800", "#88ee00", "#ee8800", "#eeee00", "#880088", "#8800ee", "#ee0088", "#ee00ee",
                "#444444", "#888888", "#0000ee", "#880000", "#004444", "#004488", "#0044ee", "#008844", "#00ee44",
                "#444400", "#448800", "#44ee00", "#884400", "#ee4400", "#440044", "#440088", "#4400ee", "#880044", "#ee0044", ))
# this is the color of matplotlib uses, it has two sets of color, one dark color, one light, good when need a lot of colors, not color-blind safe
COLOR1 = ((0.1216, 0.4667, 0.7059), (1, 0.498 , 0.0549), (0.1725, 0.6275, 0.1725), (0.8392, 0.1529, 0.1569), (0.5804, 0.4039, 0.7412), (0.549 , 0.3373, 0.2941), (0.8902, 0.4667, 0.7608), (0.498 , 0.498, 0.498 ), (0.7373, 0.7412, 0.1333), (0.0902, 0.7451, 0.8118),
                            (0.6824, 0.7804, 0.9098),(1, 0.7333, 0.4706),(0.5961, 0.8745, 0.5412),(1, 0.5961, 0.5882),(0.7725, 0.6902, 0.8353),(0.7686, 0.6118, 0.5804),(0.9686, 0.7137, 0.8235),(0.7804, 0.7804, 0.7804),(0.8588, 0.8588, 0.5529),(0.6196, 0.8549, 0.898))
COLOR_MORE = itertools.cycle(COLOR1)


##########################################################################################
COLOR_TWO = itertools.cycle((("#ca0020", "#0571b0")))
COLOR_TWO = itertools.cycle((("#0571b0", "#ca0020")))
COLOR_THREE = itertools.cycle((("#1b9e77", "#d95f02", "#7570b3")))
COLOR_THREE2 = itertools.cycle((("#66c2a5", "#fc8d62", "#8da0cb", )))
COLOR_FOUR = itertools.cycle(("#ca0020", "#f4a582", "#92c5de", "#0571b0"))


COLOR_FIVE = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', ))
COLOR_SIX = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5'))
COLOR_SEVEN = itertools.cycle(COLOR1[:7])
COLOR_EIGHT = itertools.cycle(COLOR1[:8])
COLOR_NINE = itertools.cycle(COLOR1[:9])
COLOR_TEN = itertools.cycle(COLOR1[:10])

# COLOR_SEVEN = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6'))
# COLOR_EIGHT = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7'))
# COLOR_NINE = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8'))
# COLOR_TEN = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'))

# this is a different set of colors, but it is really good color
# COLOR_MORE = itertools.cycle(('C0', 'C1', 'C2', 'C3', 'C4', 'C5', 'C6', 'C7', 'C8', 'C9'))


##########################################################################################
SINGLE_COLOR_NINE = itertools.cycle(reversed(("#f7fbff", "#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b" )))
SINGLE_COLOR_EIGHT = itertools.cycle(reversed(("#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#08519c", "#08306b" )))
SINGLE_COLOR_SEVEN = itertools.cycle(reversed(("#deebf7", "#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594" )))
SINGLE_COLOR_SIX = itertools.cycle(reversed(("#c6dbef", "#9ecae1", "#6baed6", "#4292c6", "#2171b5", "#084594", )))
SINGLE_COLOR_FIVE = itertools.cycle(reversed(("#c6dbef", "#9ecae1", "#6baed6", "#3182bd", "#08519c", )))
SINGLE_COLOR_FOUR = itertools.cycle(reversed(("#bdd7e7", "#6baed6", "#3182bd", "#08519c",)))
SINGLE_COLOR_THREE = itertools.cycle(reversed(("#bdd7e7", "#3182bd", "#08519c",)))
SINGLE_COLOR_TWO = itertools.cycle(reversed(("#bdd7e7", "#08519c",)))

##########################################################################################
BW_COLOR_THREE = itertools.cycle(reversed(("#cccccc", "#969696", "#525252", )))
BW_COLOR_FOUR = itertools.cycle(reversed(("#cccccc", "#969696", "#636363", "#252525", )))
BW_COLOR_FIVE = itertools.cycle(reversed(("#d9d9d9", "#bdbdbd", "#969696", "#636363", "#252525", )))
BW_COLOR_SIX = itertools.cycle(reversed(("#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", )))
BW_COLOR_SEVEN = itertools.cycle(reversed(("#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", )))
BW_COLOR_EIGHT = itertools.cycle(reversed(("#f0f0f0", "#d9d9d9", "#bdbdbd", "#969696", "#737373", "#525252", "#252525", "#000000",)))


##########################################################################################
COLORS = {
    2: COLOR_TWO, 3: COLOR_THREE, 4: COLOR_FOUR, 5: COLOR_FIVE, 6: COLOR_SIX, 7: COLOR_SEVEN, 8: COLOR_EIGHT, 9: COLOR_NINE, 10: COLOR_TEN
}

SINGLE_COLORS = {
    8: SINGLE_COLOR_EIGHT, 7: SINGLE_COLOR_SEVEN, 6: SINGLE_COLOR_SIX, 5: SINGLE_COLOR_FIVE, 4: SINGLE_COLOR_FOUR,
    3: SINGLE_COLOR_THREE, 2: SINGLE_COLOR_TWO,
}

BW_COLORS = {
    8: BW_COLOR_EIGHT, 7: BW_COLOR_SEVEN, 6: BW_COLOR_SIX, 5: BW_COLOR_FIVE, 4: BW_COLOR_FOUR, 3: BW_COLOR_THREE,
}

##########################################################################################
DEFAULT_COLOR = COLOR_MORE