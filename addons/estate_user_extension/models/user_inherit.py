from odoo import models, fields

class InheritedResUsers(models.Model):
    _inherit = "res.users"

    property_ids = fields.One2many(
        comodel_name='estate.property',  # Model đích
        inverse_name='salesperson_id',   # Trường Many2one trong estate.property trỏ về res.users
        string='Properties',
        domain=[('state', '=', 'available')]  # Chỉ hiển thị các property có state = 'available'
    )