{
    'name': 'Manual Attendance',
    'version': '14.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Manual attendance check-in/check-out system',
    'description': """
        Manual attendance system with check-in/check-out buttons
        and automatic cron job for attendance management.
    """,
    'author': 'ThaiDTC',
    'website': '',
    'depends': ['base', 'hr', 'hr_attendance'],
    'data': [
        'security/ir.model.access.csv',
        'data/cron_data.xml',
        'views/manual_attendance_views.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}