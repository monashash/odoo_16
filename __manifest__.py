{
    'name': 'Purchase Request',
    'version': '1.0',
    'summary': 'Manage Purchase Requests',
    'description': """
        Purchase Request Module
    """,
    'category': 'Purchases',
    'author': 'mona khaled',
    'depends': ['purchase', 'mail'],
    'data': [
        'security/ir.model.access.csv',
        'views/purchase_request_views.xml',
        'views/reject_reason_wizard.xml',
        'data/mail_template.xml',
    ],
    'installable': True,
    'application': True,
}
