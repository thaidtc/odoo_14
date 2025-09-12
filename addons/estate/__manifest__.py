{
    'name': 'Estate Management',
    'version': '1.0',
    'summary': 'Module quản lý bất động sản',
    'description': """
        Module quản lý bất động sản trong Odoo 14
        Quản lý properties, hợp đồng, khách hàng
    """,
    'author': 'ThaiDTC_Dev',
    'website': '',
    'category': 'Real Estate',
    'depends': ['base', 'mail'],
    'data': [
        # Các file XML sẽ được thêm sau
        'security/res_groups.xml', # Định nghĩa nhóm người dùng
        'security/ir.model.access.csv', # Quyền truy cập cho các mô hình
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/estate_property_offer_views.xml',
        'views/estate_property_views.xml', # Giao diện người dùng cho mô hình estate.property
        'views/buyer_report_views.xml',
        'views/estate_menu_views.xml',
    ],
    'demo': [
        # Dữ liệu demo
        'demo/demo.xml', # Dữ liệu mẫu cho mô hình estate.property
    ],
    'installable': True,
    'application': True,  # Quan trọng: biến module thành ứng dụng
    'auto_install': False,
    'license': 'LGPL-3',
}
