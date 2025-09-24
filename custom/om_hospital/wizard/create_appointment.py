from odoo import models, fields, api, _


class CreateAppointmentWizard(models.TransientModel):
    _name = "create.appointment.wizard"
    _description = "Create Appointment Wizard"

    @api.model
    def default_get(self, fields):
        res = super(CreateAppointmentWizard, self).default_get(fields)
        patient_id = self._context.get('active_id')
        if patient_id:
            res['patient_id'] = patient_id
        return res

    # Fields
    date_appointment = fields.Date(string='Date')
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)
    doctor_id = fields.Many2one('hospital.doctor', string='Doctor', required=True)

    def create_appointment_action(self):
        values = {
            'patient_id': self.patient_id.id,
            'doctor_id': self.doctor_id.id,
            'date_appointment': self.date_appointment,
        }
        new_appointment = self.env['hospital.appointment'].create(values)
        print('---> ', new_appointment)
        return {
            'name': _('Appointment'),
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'hospital.appointment',
            'res_id': new_appointment.id
        }
    
    def view_appointment_action(self):
        action = self.env.ref('om_hospital.appointment_action').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id)]

        # action = self.env['ir.actions.actions']._for_xml_id('om_hospital.appointment_action')
        # action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hospital.appointment',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'target': 'current'
        }    
        # return action
