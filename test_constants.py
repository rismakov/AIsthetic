from streamlit.uploaded_file_manager import UploadedFile, UploadedFileRec

ONE_OF_EACH_ITEMS = {
    'tops': [UploadedFile(UploadedFileRec(
        id=1, name='top.jpeg', type='image/jpeg', data=b""
    ))],
    'bottoms': [UploadedFile(UploadedFileRec(
        id=2, name='bottom.jpeg', type='image/jpeg', data=b""
    ))],
    'dresses': [UploadedFile(UploadedFileRec(
        id=3, name='dress.jpeg', type='image/jpeg', data=b""
    ))],
    'outerwear': [UploadedFile(UploadedFileRec(
        id=4, name='outer.jpeg', type='image/jpeg', data=b""
    ))],
    'shoes': [UploadedFile(UploadedFileRec(
        id=5, name='shoes.jpeg', type='image/jpeg', data=b""
    ))],
    'hats': [UploadedFile(UploadedFileRec(
        id=6, name='hat.jpeg', type='image/jpeg', data=b""
    ))],
    'bags': [UploadedFile(UploadedFileRec(
        id=7, name='bag.jpeg', type='image/jpeg', data=b""
    ))],
}

ITEMS = {
    'tops': [],
    'bottoms': [
        # this does not exist in `ITEM_TAGS`
        UploadedFile(UploadedFileRec(
            id=114,
            name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg',
            type='image/jpeg',
            data=b""
            )
        ),
        # this does exist in `ITEM_TAGS`
        UploadedFile(UploadedFileRec(
            id=115,
            name='91_bas_su_ca_.jpg',
            type='image/jpeg',
            data=b""
            )
        )
    ],
    'dresses': [],
    'outerwear': [],
    'shoes': [],
    'hats': [],
    'bags': []
}

ITEMS_TAGS = {
    'hats': {
        'basic_fall_casual_hat.jpeg': {
            'style': ['Basic'],
            'season': ['Fall'],
            'occasion': ['Casual'],
        },
        'basic_warm_casual_fall_hat.jpeg': {
            'style': ['Basic'],
            'season': ['Winter', 'Fall'],
            'occasion': ['Casual', 'Work']
        },
        'statement_fall_causal_work_hat.jpeg': {
            'style': ['Statement'],
            'season': ['Fall'],
            'occasion': ['Casual', 'Work']
        }
    },
    'tops': {
        'black_vneck_bas_wo_ca_bar_su_sp_.webp': {
            'style': ['Basic'], 'season': [], 'occasion': []
        },
        'burgundy_thermal_bas_wi_wo_ca_bar_.webp': {
            'style': ['Basic'], 'season': ['Summer', 'Spring'],
            'occasion': ['Casual', 'Work']
        }
    },
    'bottoms': {
        '91_bas_su_ca_.jpg': {
            'style': ['Basic'],
            'season': ['Fall', 'Summer', 'Spring'],
            'occasion': ['Casual']
        }
    },
    'outerwear': {
        'outerwear_example.jpg': {
            'style': ['Statement'],
            'season': ['Fall', 'Winter'],
            'occasion': ['Bar/Dinner', 'Casual']
        }
    }
}

OUTFIT = {
    # Basic, Summer + Spring, Casual + Work
    'tops':  UploadedFile(UploadedFileRec(
        id=113,
        name='burgundy_thermal_bas_wi_wo_ca_bar_.webp',
        type='image/jpeg',
        data=b""
        )
    ),
    # Basic, Fall + Summer + Spring, Casual
    'bottoms': UploadedFile(UploadedFileRec(
        id=114,
        name='91_bas_su_ca_.jpg',
        type='image/jpeg',
        data=b""
        )
    ),
    # Statement, Fall + Winter, Bar/Dinner
    'outerwear': UploadedFile(UploadedFileRec(
        id=115,
        name='outerwear_example.jpg',
        type='image/jpeg',
        data=b""
        )
    ),
}

ITEMS2 = {
    'tops': [
        UploadedFile(UploadedFileRec(
            id=114,
            name='example_top.jpeg',
            type='image/jpeg',
            data=b""
            )
        )
    ],
    'bottoms': [
        UploadedFile(UploadedFileRec(
            id=114,
            name='example_bottom.jpeg',
            type='image/jpeg',
            data=b""
            )
        ),
        UploadedFile(UploadedFileRec(
            id=115,
            name='example_bottom2.jpeg',
            type='image/jpeg',
            data=b""
            )
        )
    ],
    'dresses': [],
    'outerwear': [
        UploadedFile(UploadedFileRec(
            id=114,
            name='example_outerwear.jpeg',
            type='image/jpeg',
            data=b""
            )
        ),
        UploadedFile(UploadedFileRec(
            id=114,
            name='example_outerwear2.jpeg',
            type='image/jpeg',
            data=b""
            )
        ),
    ],
    'shoes': [],
    'hats': [],
    'bags': []
}

ITEMS_TAGS2 = {
    'tops': {
        'example_top.jpeg': {
            'style': ['Basic'],
            'season': ['Summer', 'Spring', 'Fall'],
            'occasion': ['Casual', 'Bar/Dinner']
        },
    },
    'bottoms': {
        'example_bottom.jpeg': {
            'style': ['Basic'],
            'season': ['Fall', 'Summer', 'Spring'],
            'occasion': ['Casual']
        },
        'example_bottom2.jpeg': {
            'style': ['Statement'],
            'season': ['Winter', 'Summer', 'Spring'],
            'occasion': ['Casual', 'Bar/Dinner']
        }
    },
    'outerwear': {
        'example_outerwear.jpeg': {
            'style': ['Basic'],
            'season': ['Fall', 'Winter', 'Summer'],
            'occasion': ['Bar/Dinner']
        },
        'example_outerwear2.jpeg': {
            'style': ['Statement'],
            'season': ['Fall', 'Winter'],
            'occasion': ['Bar/Dinner', 'Casual']
        }
    }
}

TEST_OUTFITS_LIST = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='black_ruched_top.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Spring'},
            'occasion': {'Casual', 'Work'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='black_ruched_top.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )), 
        'tags': {
            'season': {'Winter', 'Fall'},
            'occasion': {'Casual', 'Bar/Dinner'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=6, name='black_vneck_bas_wo_ca_bar_su_sp_.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {'season': {'Spring'}, 'occasion': {'Casual', 'Work'}, 'is_statement': False},
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=6, name='black_vneck_bas_wo_ca_bar_su_sp_.webp', type='image/webp', data=b""
        )), 
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )), 
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )), 
        'tags': {'season': {'Summer'}, 'occasion': {'Casual', 'Work'}, 'is_statement': False},
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=12, name='white_buttondown_bas_wo_ca_sp_fa_.webp', type='image/webp', data=b""
        )), 
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )), 
        'outerwear': UploadedFile(UploadedFileRec(id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b"")),
        'tags': {
            'season': {'Summer'}, 
            'occasion': {'Casual', 'Work'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=12, name='white_buttondown_bas_wo_ca_sp_fa_.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer'},
            'occasion': {'Casual', 'Work'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=13, name='white_shortsleeve.jpeg', type='image/jpeg', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer'},
            'occasion': {'Casual', 'Work'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=13, name='white_shortsleeve.jpeg', type='image/jpeg', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer', 'Spring'},
            'occasion': {'Bar/Dinner', 'Work'},
            'is_statement': False
        }
    }
]

SUMMER_DINNER_OUTFITS = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=13, name='white_shortsleeve.jpeg', type='image/jpeg', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer', 'Spring'},
            'occasion': {'Bar/Dinner', 'Work'},
            'is_statement': False
        }
    }
]

SPRING_WORK_OUTFITS = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='black_ruched_top.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Spring'},
            'occasion': {'Casual', 'Work'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=6, name='black_vneck_bas_wo_ca_bar_su_sp_.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {'season': {'Spring'}, 'occasion': {'Casual', 'Work'}, 'is_statement': False},
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=13, name='white_shortsleeve.jpeg', type='image/jpeg', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer', 'Spring'},
            'occasion': {'Bar/Dinner', 'Work'},
            'is_statement': False
        }
    }
]

SPRING_WORK_OUTFITS_2 = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=6, name='black_vneck_bas_wo_ca_bar_su_sp_.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=24, name='beige-zara-linen-blazer-with-rolled-up-sleeves-4_bas_su_sp_ca_wo_bar_.jpeg', type='image/jpeg', data=b""
        )),
        'tags': {'season': {'Spring'}, 'occasion': {'Casual', 'Work'}, 'is_statement': False},
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=13, name='white_shortsleeve.jpeg', type='image/jpeg', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Summer', 'Spring'},
            'occasion': {'Bar/Dinner', 'Work'},
            'is_statement': False
        }
    }
]

WINTER_CASUAL_OUTFITS = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='black_ruched_top.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='jeans_bas_ca_wo_su_sp_wi_fa_.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='cab copy_bas_su_sp_ca_wo_.jpg', type='image/jpeg', data=b""
        )), 
        'tags': {
            'season': {'Winter', 'Fall'},
            'occasion': {'Casual', 'Bar/Dinner'},
            'is_statement': False
        }
    }
]

TEST_OUTFITS_FOR_RECENTLY_WORN = [
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='top_1.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='bottom_1.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='outerwear.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Winter', 'Fall'},
            'occasion': {'Casual', 'Bar/Dinner'},
            'is_statement': False
        }
    },
    {
        'tops': UploadedFile(UploadedFileRec(
            id=3, name='top_2.webp', type='image/webp', data=b""
        )),
        'bottoms': UploadedFile(UploadedFileRec(
            id=17, name='bottom_2.jpeg', type='image/jpeg', data=b""
        )),
        'outerwear': UploadedFile(UploadedFileRec(
            id=25, name='outerwear.jpg', type='image/jpeg', data=b""
        )),
        'tags': {
            'season': {'Winter', 'Fall'},
            'occasion': {'Casual', 'Bar/Dinner'},
            'is_statement': False
        }
    }
]
