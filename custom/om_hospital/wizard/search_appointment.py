from odoo import models, fields, api, _


class SearchAppointmentWizard(models.TransientModel):
    _name = "search.appointment.wizard"
    _description = "Search Appointment Wizard"

    # Fields
    patient_id = fields.Many2one('hospital.patient', string='Patient', required=True)

    def search_appointment_action_m1(self):
        action = self.env.ref('om_hospital.appointment_action').read()[0]
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action
    
    def search_appointment_action_m2(self):
        action = self.env['ir.actions.actions']._for_xml_id('om_hospital.appointment_action')
        action['domain'] = [('patient_id', '=', self.patient_id.id)]
        return action 
    
    def search_appointment_action_m3(self):
        return {
            'name': 'Appointments',
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'hospital.appointment',
            'domain': [('patient_id', '=', self.patient_id.id)],
            'target': 'current'
        }
