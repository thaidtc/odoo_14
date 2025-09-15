from odoo import models, fields, api


class HospitalPatient(models.Model):  # Bệnh nhân
    _name = "hospital.patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Patient"

    # Fields
    name = fields.Char(string="Name", required=True)
    age = fields.Integer(string="Age")
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
