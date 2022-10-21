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
        'beret_bas_ca_wo_bar_fa_wi_.jpeg': {
            'style': 'Basic',
            'season': ['Fall'],
            'occasion': ['Casual'],
        },
        'hat_st_fa_ca_wo_.jpeg': {
            'style': 'Basic',
            'season': ['Winter', 'Fall'],
            'occasion': ['Casual', 'Work']
        },
        'plaid_st_sp_fa_ca_wo.png': {
            'style': 'Statement',
            'season': ['Fall'],
            'occasion': ['Casual', 'Work']
        }
    },
    'tops': {
        'black_vneck_bas_wo_ca_bar_su_sp_.webp': {
            'style': 'Basic', 'season': [], 'occasion': []
        },
        'burgundy_thermal_bas_wi_wo_ca_bar_.webp': {
            'style': 'Basic', 'season': ['Summer', 'Spring'],
            'occasion': ['Casual', 'Work']
        }
    },
    'bottoms': {
        '91_bas_su_ca_.jpg': {
            'style': 'Basic',
            'season': ['Fall', 'Summer', 'Spring'],
            'occasion': ['Casual']
        }
    },
    'outerwear': {
        'outerwear_example.jpg': {
            'style': 'Statement',
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
    )
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
            'style': 'Basic',
            'season': ['Summer', 'Spring', 'Fall'],
            'occasion': ['Casual', 'Bar/Dinner']
        },
    },
    'bottoms': {
        'example_bottom.jpeg': {
            'style': 'Basic',
            'season': ['Fall', 'Summer', 'Spring'],
            'occasion': ['Casual']
        },
        'example_bottom2.jpeg': {
            'style': 'Statement',
            'season': ['Winter', 'Summer', 'Spring'],
            'occasion': ['Casual', 'Bar/Dinner']
        }
    },
    'outerwear': {
        'example_outerwear.jpeg': {
            'style': 'Basic',
            'season': ['Fall', 'Winter', 'Summer'],
            'occasion': ['Bar/Dinner']
        },
        'example_outerwear2.jpeg': {
            'style': 'Statement',
            'season': ['Fall', 'Winter'],
            'occasion': ['Bar/Dinner', 'Casual']
        }
    }
}
