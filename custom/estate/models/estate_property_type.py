from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstatePropertyType(models.Model):
    _name = 'estate.property.type'
    _description = 'Estate Property Type'
    _order = 'name asc'
    
    name = fields.Char(string='Type Name', required=True)
    sequence = fields.Integer(string='Sequence', default=1)

    property_ids = fields.One2many('estate.property', 'property_type_id', string='Properties')
    offer_ids = fields.One2many(
        string='Offers',
        comodel_name='estate.property.offer',
        inverse_name='property_type_id'
    )
    offer_count = fields.Integer(
        string='Number of Offers',
        compute='_compute_offer_count',
        store=True
    )
    
    # SQL CONSTRAINTS
    _sql_constraints = [
        ('unique_type_name', 'UNIQUE(name)', 'Property type name must be unique!')
    ]

    # COMPUTE METHOD
    @api.depends('offer_ids')
    def _compute_offer_count(self):
        """Tính số lượng offers cho property type"""
        print("=== _compute_offer_count CALLED ===")  # DEBUG
        for record in self:
            print(f"Computing offer_count for: {record.name}, offers: {len(record.offer_ids)}")  # DEBUG
            record.offer_count = len(record.offer_ids)

    # CONSTRAINT METHOD
    @api.constrains('name')
    def _check_unique_name(self):
        """Kiểm tra tên type duy nhất"""
        print("=== _check_unique_name CALLED ===")  # DEBUG
        for record in self:
            print(f"Checking uniqueness for: {record.name}")  # DEBUG
            if self.search_count([('name', '=ilike', record.name), ('id', '!=', record.id)]) > 0:
                raise ValidationError("Property type name must be unique!")
            
    def action_view_offers(self):
        """Mở danh sách offers filtered theo property type"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': f'Offers - {self.name}',
            'res_model': 'estate.property.offer',
            'view_mode': 'tree,form',
            'domain': [('property_type_id', '=', self.id)],
            'context': {
                'default_property_type_id': self.id,
                'search_default_group_by_property_id': 1,
                'search_default_group_by_status': 1,
            },
            'target': 'current',
        }
