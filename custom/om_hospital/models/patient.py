from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

class HospitalPatient(models.Model):  # Bệnh nhân
    _name = "hospital.patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Hospital Patient"
    _order = "id desc"

    # Fields
    name = fields.Char(string="Name", required=True, tracking=True)
    reference = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default=lambda self: _("New"),
    )
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
    responsible_id = fields.Many2one("res.partner", string="Responsible")
    appointment_count = fields.Integer(string="Appointment Count", compute="_compute_appointment_count")
    image = fields.Binary(string="Patient Image")
    appointment_ids = fields.One2many('hospital.appointment', 'patient_id', string="Appointments")

    def _compute_appointment_count(self):
        for record in self:
            appointment_count = self.env['hospital.appointment'].search_count([('patient_id', '=', record.id)])
            record.appointment_count = appointment_count

    def action_confirm(self):
        for record in self:
            record.state = "confirm"

    def action_done(self):
        for record in self:
            record.state = "done"

    def action_draft(self):
        for record in self:
            record.state = "draft"

    def action_cancel(self):
        for record in self:
            record.state = "cancel"

    @api.model
    def create(self, values):
        if not values.get("note"):
            values["note"] = "New Patient"
        if values.get("reference", _('New')) == _('New'):
            values["reference"] = self.env['ir.sequence'].next_by_code('hospital.patient') or _('New')
        result = super(HospitalPatient, self).create(values)
        return result
    
    @api.model
    def default_get(self, fields_list):
        result = super(HospitalPatient, self).default_get(fields_list)
        if not result.get('note'):
            result['note'] = "New Patient"
        return result

    @api.constrains('name')
    def _check_name(self):
        for record in self:
            patients = self.env['hospital.patient'].search([('name', '=', record.name), ('id', '!=', record.id)])
            if patients:
                raise ValidationError(_("Name '%s' is already exist. Patient name must be unique.") % (record.name))

    @api.constrains('age')
    def _check_age(self):
        for record in self:
            if record.age <= 0:
                raise ValidationError(_("Age must be positive."))

    def name_get(self):
        result = []
        for record in self:
            name = f"{record.name} ({record.reference})"
            result.append((record.id, name))
        return result
