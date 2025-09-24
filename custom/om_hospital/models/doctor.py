from odoo import models, fields, api, _


class HospitalDoctor(models.Model):
    _name = "hospital.doctor"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Doctor"
    _rec_name = "doctor_name"

    # Fields
    doctor_name = fields.Char(string="Name", required=True, tracking=True)
    name = fields.Char(related="doctor_name", store=True, index=True)
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
    appointment_count = fields.Integer(string="Appointments", compute="_compute_appointment_count")
    active = fields.Boolean(string="Active", default=True)

    def _compute_appointment_count(self):
        for record in self:
            appointment_count = self.env['hospital.appointment'].search_count([('doctor_id', '=', record.id)])
            record.appointment_count = appointment_count

    def copy(self, default=None):
        default = dict(default or {})
        default.update(
            {
                "doctor_name": _("%s (copy)") % self.doctor_name,
                "note": "Copied record",
            }
        )
        return super(HospitalDoctor, self).copy(default)
