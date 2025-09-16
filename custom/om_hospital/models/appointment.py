from odoo import models, fields, api, _


class HospitalAppointment(models.Model):  # Cuộc hẹn
    _name = "hospital.appointment"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Appointment"

    # Fields
    name = fields.Char(string="Order Reference", required=True, readonly=True, copy=False, default=lambda self: _("New"))
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    age = fields.Integer(string="Age", related='patient_id.age')
    gender = fields.Selection(
        [
            ("male", "Male"),
            ("female", "Female"),
            ("other", "Other"),
        ],
        required=True,
        default="other",
    )
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("confirm", "Confirmed"),
            ("done", "Done"),
            ("cancel", "Cancelled"),
        ],
        default="draft",
        string="Status",
        tracking=True,
    )
    note = fields.Text(string="Description")
    date_appointment = fields.Date(string="Date")
    date_checkup = fields.Datetime(string="Check Up Time")

    def action_confirm(self):
        self.state = "confirm"

    def action_done(self):
        self.state = "done"

    def action_draft(self):
        self.state = "draft"

    def action_cancel(self):
        self.state = "cancel"

    @api.model
    def create(self, values):
        if not values.get("note"):
            values["note"] = "New Appointment"
        if values.get("name", _('New')) == _('New'):
            values["name"] = self.env['ir.sequence'].next_by_code('hospital.appointment') or _('New')
        result = super(HospitalAppointment, self).create(values)
        return result

    @api.onchange('patient_id')
    def onchange_patient_id(self):
        if self.patient_id:
            if self.patient_id.gender:
                self.gender = self.patient_id.gender
            if self.patient_id.note:
                self.note = self.patient_id.note
        else:
            self.gender = ''
            self.note = ''
