from odoo import models, fields, api, _


class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment Wizard"

    # Fields
    date_appointment = fields.Date(string='Date', required=True)
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)

    def create_appointment_action(self):
        values = {
            'patient_id': self.patient_id.id,
            'date_appointment': self.date_appointment,
        }
        self.env['hospital.appointment'].create(values)
