# The original category structure from the Movable Type site.
# Create django-treebeard categories by doing this:

# from pepysdiary.encyclopedia.models import Category
# Category.load_bulk(data, parent=None, keep_ids=True)

data = [
    {
        "id": 15,
        "data": {"title": "Art and literature", "slug": "art"},
        "children": [
            {"id": 66, "data": {"title": "Literature", "slug": "literature"}},
        ],
    },
    {
        "id": 79,
        "data": {"title": "Entertainment", "slug": "entertainent"},
        "children": [
            {"id": 136, "data": {"title": "Dancing", "slug": "dancing"}},
            {"id": 54, "data": {"title": "Fairs", "slug": "fairs"}},
            {"id": 48, "data": {"title": "Games", "slug": "games"}},
            {
                "id": 4,
                "data": {"title": "Music", "slug": "music"},
                "children": [
                    {"id": 33, "data": {"title": "Instruments", "slug": "instruments"}},
                    {"id": 240, "data": {"title": "Songs", "slug": "songs"}},
                ],
            },
            {"id": 50, "data": {"title": "Sports", "slug": "sports"}},
            {
                "id": 5,
                "data": {"title": "Theatre", "slug": "theatre"},
                "children": [{"id": 128, "data": {"title": "Plays", "slug": "plays"}}],
            },
        ],
    },
    {"id": 8, "data": {"title": "Fashion", "slug": "fashion"}},
    {
        "id": 173,
        "data": {"title": "Food and drink", "slug": "fooddrink"},
        "children": [
            {
                "id": 174,
                "data": {"title": "Drink", "slug": "drink"},
                "children": [
                    {
                        "id": 25,
                        "data": {"title": "Alcoholic drinks", "slug": "alcdrinks"},
                    },
                    {
                        "id": 24,
                        "data": {
                            "title": "Non-alcoholic drinks",
                            "slug": "nonalcoholic",
                        },
                    },
                ],
            },
            {
                "id": 10,
                "data": {"title": "Food", "slug": "food"},
                "children": [
                    {"id": 23, "data": {"title": "Baked goods", "slug": "baked"}},
                    {"id": 21, "data": {"title": "Dairy produce", "slug": "dairy"}},
                    {
                        "id": 22,
                        "data": {"title": "Fruit and vegetables", "slug": "fruitveg"},
                    },
                    {
                        "id": 19,
                        "data": {
                            "title": "Herbs, spices and condiments",
                            "slug": "herbs",
                        },
                    },
                    {"id": 18, "data": {"title": "Meta", "slug": "meat"}},
                    {"id": 20, "data": {"title": "Seafood/fish", "slug": "seafood"}},
                ],
            },
        ],
    },
    {"id": 77, "data": {"title": "Further reading", "slug": "further"}},
    {
        "id": 17,
        "data": {"title": "General reference", "slug": "reference"},
        "children": [{"id": 16, "data": {"title": "Maps", "slug": "maps"}}],
    },
    {"id": 52, "data": {"title": "Glossary", "slug": "glossary"}},
    {
        "id": 6,
        "data": {"title": "Government and law", "slug": "state"},
        "children": [
            {"id": 269, "data": {"title": "Bills and Acts", "slug": "acts"}},
            {"id": 37, "data": {"title": "Government", "slug": "government"}},
            {"id": 36, "data": {"title": "Law", "slug": "law"}},
            {
                "id": 35,
                "data": {"title": "Navy", "slug": "navy"},
                "children": [
                    {
                        "id": 126,
                        "data": {"title": "Naval equipment", "slug": "equipment"},
                    },
                ],
            },
        ],
    },
    {"id": 12, "data": {"title": "Holidays and events", "slug": "holidays"}},
    {
        "id": 13,
        "data": {"title": "Money and business", "slug": "money"},
        "children": [
            {"id": 95, "data": {"title": "Companies", "slug": "companies"}},
            {"id": 256, "data": {"title": "Types of coin", "slug": "coins"}},
        ],
    },
    {
        "id": 2,
        "data": {"title": "People", "slug": "people"},
        "children": [
            {
                "id": 91,
                "data": {"title": "Samuel Pepys", "slug": "samuel-pepys"},
                "children": [
                    {
                        "id": 133,
                        "data": {"title": "Pepys' household", "slug": "household"},
                        "children": [
                            {
                                "id": 134,
                                "data": {
                                    "title": "Pepys' servants (current)",
                                    "slug": "servants",
                                },
                            },
                            {
                                "id": 135,
                                "data": {
                                    "title": "Pepys' servants (past)",
                                    "slug": "servantspast",
                                },
                            },
                        ],
                    }
                ],
            },
        ],
    },
    {
        "id": 3,
        "data": {"title": "Places", "slug": "places"},
        "children": [
            {
                "id": 198,
                "data": {"title": "London", "slug": "london"},
                "children": [
                    {"id": 196, "data": {"title": "Areas of London", "slug": "areas"}},
                    {
                        "id": 31,
                        "data": {
                            "title": "Churches and cathedrals",
                            "slug": "churches",
                        },
                    },
                    {
                        "id": 26,
                        "data": {"title": "Coffee houses", "slug": "coffeehouses"},
                    },
                    {
                        "id": 199,
                        "data": {
                            "title": "Government buildings",
                            "slug": "government-buildings",
                        },
                    },
                    {
                        "id": 201,
                        "data": {"title": "Livery halls", "slug": "livery-halls"},
                    },
                    {
                        "id": 29,
                        "data": {
                            "title": "Other London buildings",
                            "slug": "buildings",
                        },
                    },
                    {
                        "id": 178,
                        "data": {"title": "Pepys' homes", "slug": "pepys-homes"},
                    },
                    {
                        "id": 200,
                        "data": {"title": "Royal buildings", "slug": "royal"},
                        "children": [
                            {
                                "id": 180,
                                "data": {
                                    "title": "Whitehall Palace - places within",
                                    "slug": "whitehall-palace",
                                },
                            },
                        ],
                    },
                    {
                        "id": 28,
                        "data": {"title": "Streets in London", "slug": "streets"},
                    },
                    {"id": 27, "data": {"title": "Taverns", "slug": "taverns"}},
                    {"id": 197, "data": {"title": "Theatres", "slug": "theatres"}},
                ],
            },
            {
                "id": 214,
                "data": {"title": "London environs", "slug": "environs"},
                "children": [
                    {
                        "id": 213,
                        "data": {
                            "title": "Deptford - places within",
                            "slug": "deptford",
                        },
                    },
                    {
                        "id": 211,
                        "data": {
                            "title": "Greenwich - places within",
                            "slug": "greenwich",
                        },
                    },
                    {
                        "id": 215,
                        "data": {
                            "title": "Vauxhall - places within",
                            "slug": "vauxhall",
                        },
                    },
                    {
                        "id": 204,
                        "data": {
                            "title": "Woolwich - places within",
                            "slug": "woolwich",
                        },
                    },
                ],
            },
            {
                "id": 30,
                "data": {"title": "Rest of Britain", "slug": "britain"},
                "children": [
                    {
                        "id": 203,
                        "data": {"title": "Barking - places within", "slug": "barking"},
                    },
                    {
                        "id": 207,
                        "data": {
                            "title": "Barnet, Hertfordshire - places within",
                            "slug": "barnet",
                        },
                    },
                    {
                        "id": 266,
                        "data": {"title": "Bath - places within", "slug": "bath"},
                    },
                    {
                        "id": 265,
                        "data": {"title": "Bristol - places within", "slug": "bristol"},
                    },
                    {
                        "id": 202,
                        "data": {
                            "title": "Cambridge - places within",
                            "slug": "cambridge",
                        },
                    },
                    {
                        "id": 216,
                        "data": {
                            "title": "Gravesend, Kent - places within",
                            "slug": "gravesend",
                        },
                    },
                    {
                        "id": 268,
                        "data": {
                            "title": "Guildford, Surrey - places within",
                            "slug": "guildford",
                        },
                    },
                    {
                        "id": 206,
                        "data": {
                            "title": "Hatfield, Hertfordshire - places within",
                            "slug": "hatfield",
                        },
                    },
                    {
                        "id": 267,
                        "data": {"title": "Oxford - places within", "slug": "oxford"},
                    },
                    {
                        "id": 212,
                        "data": {
                            "title": "Portsmouth, Hampshire - places within",
                            "slug": "portsmouth",
                        },
                    },
                    {
                        "id": 217,
                        "data": {
                            "title": "Rochester, Medway - places within",
                            "slug": "rochester",
                        },
                    },
                    {
                        "id": 210,
                        "data": {
                            "title": "Wanstead, Essex - places within",
                            "slug": "wanstead",
                        },
                    },
                    {"id": 209, "data": {"title": "Waterways", "slug": "waterways"}},
                    {
                        "id": 205,
                        "data": {
                            "title": "Welwyn, Hertfordshire - places within",
                            "slug": "welwyn",
                        },
                    },
                    {
                        "id": 208,
                        "data": {"title": "Windsor - places within", "slug": "windsor"},
                    },
                ],
            },
            {"id": 45, "data": {"title": "Rest of the world", "slug": "abroad"}},
        ],
    },
    {"id": 9, "data": {"title": "Religion", "slug": "religion"}},
    {
        "id": 11,
        "data": {"title": "Science, technology, health", "slug": "science"},
        "children": [
            {"id": 7, "data": {"title": "Health and medicine", "slug": "health"}},
            {
                "id": 270,
                "data": {
                    "title": "Scientific instruments",
                    "slug": "scientific-instruments",
                },
            },
        ],
    },
    {
        "id": 32,
        "data": {"title": "Travel and vehicles", "slug": "travel"},
        "children": [{"id": 34, "data": {"title": "Ships", "slug": "ships"}}],
    },
    {
        "id": 175,
        "data": {"title": "Work and education", "slug": "work"},
        "children": [
            {"id": 67, "data": {"title": "Education", "slug": "education"}},
            {"id": 14, "data": {"title": "Jobs and professions", "slug": "jobs"}},
        ],
    },
]
