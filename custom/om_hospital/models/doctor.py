from odoo import models, fields, api, _


class HospitalDoctor(models.Model):  # Bệnh nhân
    _name = "hospital.doctor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Doctor"

    # Fields
    name = fields.Char(string="Name", required=True, tracking=True)
    age = fields.Integer(string="Age", tracking=True)
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    note = fields.Text(string="Description")
    image = fields.Binary(string="Doctor Image")
