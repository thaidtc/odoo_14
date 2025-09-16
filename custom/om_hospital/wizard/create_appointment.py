from odoo import models, fields, api, _


class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment Wizard"

    # Fields
    name = fields.Char(string="Name", required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)

    def create_appointment_action(self):
        print("Button clicked: ", self)