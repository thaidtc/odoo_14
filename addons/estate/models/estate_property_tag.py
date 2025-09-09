from odoo import models, fields, api
from odoo.exceptions import ValidationError

class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Estate Property Tag'
    _order = 'name asc'
    
    name = fields.Char(string='Tag Name', required=True)
    color = fields.Integer(string='Color Index')
    property_ids = fields.Many2many('estate.property', string='Properties')
    
    _sql_constraints = [
        ('unique_tag_name', 'UNIQUE(name)', 'Property tag name must be unique!')
    ]

    @api.constrains('name')
    def _check_unique_name(self):
        for tag in self:
            if self.search_count([('name', '=ilike', tag.name), ('id', '!=', tag.id)]) > 0:
                raise ValidationError("Property tag name must be unique!")