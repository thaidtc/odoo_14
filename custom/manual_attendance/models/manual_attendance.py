from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import logging
from datetime import datetime, timedelta

_logger = logging.getLogger(__name__)

class ManualAttendance(models.Model):
  _name = 'manual.attendance'
  _description = 'Manual Attendance'
  _order = 'check_time desc'

  name = fields.Char(string='Reference', compute='_compute_name', store=True)
  employee_id = fields.Many2one(
      'hr.employee', 
      string='Employee', 
      required=True,
      default=lambda self: self._default_employee()
  )
  check_time = fields.Datetime(
        string='Check Time', 
        default=fields.Datetime.now,
        required=True
    )
  attendance_type = fields.Selection([
      ('check_in', 'Check In'),
      ('check_out', 'Check Out'),
      ('auto_check_out', 'Auto Check Out')
  ], string='Type', required=True, default='check_in')
  status = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('processed', 'Processed to HR')
    ], string='Status', default='draft', required=True)
    
  notes = fields.Text(string='Notes')
  ip_address = fields.Char(string='IP Address')
  location = fields.Char(string='Location')

   # Related fields from employee
  department_id = fields.Many2one(
      'hr.department', 
      string='Department', 
      related='employee_id.department_id',
      store=True
  )
  job_id = fields.Many2one(
      'hr.job', 
      string='Job Position', 
      related='employee_id.job_id',
      store=True
  )


  @api.depends('employee_id', 'check_time', 'attendance_type')
  def _compute_name(self):
        for record in self:
            if record.employee_id and record.check_time:
                time_str = record.check_time.strftime('%Y%m%d_%H%M%S')
                record.name = f"{record.employee_id.name}_{time_str}_{record.attendance_type}"
            else:
                record.name = "New"

  def _default_employee(self):
        """Get default employee for current user"""
        user = self.env.user
        employee = self.env['hr.employee'].search([
            ('user_id', '=', user.id)
        ], limit=1)
        return employee.id if employee else False
  
  # BUTTON ACTIONS
  def action_check_in(self):
        """Button action for manual check-in"""
        self.ensure_one()
        
        # Check if already checked in today
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        existing_checkin = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('check_time', '>=', today_start),
            ('attendance_type', '=', 'check_in'),
            ('status', 'in', ['confirmed', 'processed'])
        ])
        
        if existing_checkin:
            raise UserError(_("You have already checked in today!"))
        
        # Create check-in record
        attendance = self.create({
            'employee_id': self.employee_id.id,
            'check_time': datetime.now(),
            'attendance_type': 'check_in',
            'status': 'confirmed',
            'ip_address': self.env.context.get('ip_address', 'Manual'),
            'location': self.env.context.get('location', 'Manual Entry')
        })
        
        # Auto create HR attendance
        attendance.action_create_hr_attendance()
        
        message = _("✅ Check-in successful at %s") % attendance.check_time.strftime('%H:%M:%S')
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Check In'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
  
  def action_check_out(self):
        """Button action for manual check-out"""
        self.ensure_one()
        
        # Find today's check-in
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        checkin_today = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('check_time', '>=', today_start),
            ('attendance_type', '=', 'check_in'),
            ('status', 'in', ['confirmed', 'processed'])
        ], order='check_time desc', limit=1)
        
        if not checkin_today:
            raise UserError(_("You haven't checked in today!"))
        
        # Check if already checked out
        checkout_today = self.search([
            ('employee_id', '=', self.employee_id.id),
            ('check_time', '>=', today_start),
            ('attendance_type', '=', 'check_out'),
            ('status', 'in', ['confirmed', 'processed'])
        ])
        
        if checkout_today:
            raise UserError(_("You have already checked out today!"))
        
        # Create check-out record
        attendance = self.create({
            'employee_id': self.employee_id.id,
            'check_time': datetime.now(),
            'attendance_type': 'check_out',
            'status': 'confirmed',
            'ip_address': self.env.context.get('ip_address', 'Manual'),
            'location': self.env.context.get('location', 'Manual Entry')
        })
        
        # Auto create HR attendance
        attendance.action_create_hr_attendance()
        
        # Calculate working hours
        working_hours = attendance.check_time - checkin_today.check_time
        hours = working_hours.total_seconds() / 3600
        
        message = _("✅ Check-out successful! Working hours: %.2f hours") % hours
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Check Out'),
                'message': message,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.act_window_close'},
            }
        }
  
  def action_create_hr_attendance(self):
        """Create HR Attendance record"""
        hr_attendance_model = self.env['hr.attendance']
        
        for record in self:
            if record.status == 'processed':
                continue
                
            if record.attendance_type == 'check_in':
                # Create check-in record
                hr_attendance_model.create({
                    'employee_id': record.employee_id.id,
                    'check_in': record.check_time,
                })
                record.status = 'processed'
                
            elif record.attendance_type == 'check_out':
                # Find open check-in and close it
                open_checkin = hr_attendance_model.search([
                    ('employee_id', '=', record.employee_id.id),
                    ('check_out', '=', False),
                ], order='check_in desc', limit=1)
                
                if open_checkin:
                    open_checkin.write({'check_out': record.check_time})
                    record.status = 'processed'
                else:
                    # Create check-out only record
                    hr_attendance_model.create({
                        'employee_id': record.employee_id.id,
                        'check_out': record.check_time,
                    })
                    record.status = 'processed'
    
  def action_view_today_attendance(self):
        """View today's attendance records"""
        today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        return {
            'type': 'ir.actions.act_window',
            'name': _("Today's Attendance"),
            'res_model': 'manual.attendance',
            'view_mode': 'tree,form',
            'domain': [
                ('employee_id', '=', self.employee_id.id),
                ('check_time', '>=', today_start),
                ('check_time', '<', today_end)
            ],
            'context': {'create': False}
        }
  
  # CRON JOBS
  def auto_check_out_cron(self):
        """Cron job: Auto check-out for employees who forgot to check out"""
        _logger.info("🔄 Auto check-out cron job started")
        
        try:
            # Find employees who checked in but didn't check out today
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Get all check-ins today without check-outs
            checkins_today = self.search([
                ('check_time', '>=', today_start),
                ('attendance_type', '=', 'check_in'),
                ('status', 'in', ['confirmed', 'processed'])
            ])
            
            employees_with_checkin = checkins_today.mapped('employee_id')
            
            checkouts_today = self.search([
                ('check_time', '>=', today_start),
                ('attendance_type', '=', 'check_out'),
                ('status', 'in', ['confirmed', 'processed'])
            ])
            
            employees_with_checkout = checkouts_today.mapped('employee_id')
            
            # Employees who forgot to check out
            employees_forgot_checkout = employees_with_checkin - employees_with_checkout
            
            auto_checkout_count = 0
            
            for employee in employees_forgot_checkout:
                # Auto check-out at 18:00 or current time if later
                auto_checkout_time = datetime.now().replace(hour=18, minute=0, second=0, microsecond=0)
                if datetime.now() > auto_checkout_time:
                    auto_checkout_time = datetime.now()
                
                # Create auto check-out record
                attendance = self.create({
                    'employee_id': employee.id,
                    'check_time': auto_checkout_time,
                    'attendance_type': 'auto_check_out',
                    'status': 'confirmed',
                    'notes': 'Auto check-out by system'
                })
                
                # Create HR attendance record
                attendance.action_create_hr_attendance()
                auto_checkout_count += 1
            
            _logger.info("✅ Auto check-out completed. Processed %d employees", auto_checkout_count)
            
        except Exception as e:
            _logger.error("❌ Auto check-out cron error: %s", e)
        
        return True
  
  def cleanup_old_attendance_cron(self):
        """Cron job: Cleanup attendance records older than 90 days"""
        _logger.info("🧹 Cleanup old attendance cron job started")
        
        try:
            cutoff_date = datetime.now() - timedelta(days=90)
            old_records = self.search([
                ('check_time', '<', cutoff_date),
                ('status', '=', 'processed')
            ])
            
            deleted_count = len(old_records)
            old_records.unlink()
            
            _logger.info("🗑️ Cleanup completed. Deleted %d old records", deleted_count)
            
        except Exception as e:
            _logger.error("❌ Cleanup cron error: %s", e)
        
        return True
  
  def generate_daily_report_cron(self):
        """Cron job: Generate daily attendance report"""
        _logger.info("📊 Daily attendance report cron job started")
        
        try:
            yesterday = datetime.now() - timedelta(days=1)
            yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
            yesterday_end = yesterday_start + timedelta(days=1)
            
            # Get yesterday's attendance data
            yesterday_attendance = self.search([
                ('check_time', '>=', yesterday_start),
                ('check_time', '<', yesterday_end)
            ])
            
            report_data = {
                'date': yesterday_start.strftime('%Y-%m-%d'),
                'total_records': len(yesterday_attendance),
                'check_ins': len(yesterday_attendance.filtered(lambda x: x.attendance_type == 'check_in')),
                'check_outs': len(yesterday_attendance.filtered(lambda x: x.attendance_type == 'check_out')),
                'auto_check_outs': len(yesterday_attendance.filtered(lambda x: x.attendance_type == 'auto_check_out')),
            }
            
            _logger.info("📈 Daily Report %s: %s", report_data['date'], report_data)
            
        except Exception as e:
            _logger.error("❌ Daily report cron error: %s", e)
        
        return True
  

  def test_cron_job(self):
        _logger.info("✅ Test cron job running at %s", datetime.now())
        # Add your actual cron job logic here
        return True