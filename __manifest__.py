{
    'name': 'Beto CRM: Pre-Sale & Inquiry Management',
    'version': '1.0.1',
    'category': 'Sales/CRM',
    'summary': 'Advanced workflow for lead inquiries and pre-sale pipeline management.',
    'description': """
Beto CRM: Pre-Sale Module
=========================
A professional extension for Odoo CRM designed to manage high-volume client inquiries
and transition them into a structured sales pipeline.

Key Features:
-------------
* **Incoming Query Management**: Capture and track inquiries from multiple channels (Fiverr, Upwork, etc.).
* **Presale Pipeline**: Specialized Kanban and List views for pre-sale opportunity tracking.
* **Automated Lead Promotion**: Easily convert basic inquiries into full pipeline leads with one click.
* **Sales Integration**: Seamlessly generate Odoo Sale Orders with pre-mapped platform and profile data.
* **Master Data Control**: Centralized configuration for acquisition methods, lead stages, and health conditions.
* **Aesthetic Excellence**: Clean UI with dynamic color coding and high-usability star ratings.

Technical Architecture:
----------------------
* Uses native Odoo CRM inheritance for maximum compatibility.
* Implements non-stored computed fields for UI color performance.
* Automated status transitions and 'WON' stage triggering.
    """,
    'author': 'Betopia Group (SK Meher)',
    'website': 'https://www.betopiagroup.com',
    'license': 'LGPL-3',
    'depends': [
        'crm', 
        'hr', 
        'bd_portal', 
        'sale_crm'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/incoming_query_views.xml',
        'views/lead_pipeline_views.xml',
        'views/pre_sale_menu_views.xml',
        'views/crm_isolation_views.xml',
        'views/presale_config_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
