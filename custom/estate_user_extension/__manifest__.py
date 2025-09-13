{
    'name': 'Estate User Extension',
    'version': '1.0',
    'category': 'Real Estate',
    'description': 'Extends Users with Real Estate Properties field',
    'depends': ['base', 'estate'],  # Phụ thuộc vào module estate
    'data': [
        'views/user_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
