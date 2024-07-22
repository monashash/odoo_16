from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import date

class PurchaseRequest(models.Model):
    _name = 'purchase.request'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Purchase Request'
    
    name = fields.Char(string='Request Name', required=True)
    user_id = fields.Many2one('res.users', string='Requested by', required=True, default=lambda self: self.env.user)
    start_date = fields.Date(string='Start Date', default=fields.Date.context_today)
    end_date = fields.Date(string='End Date')
    rejection_reason = fields.Text(string='Rejection Reason', readonly=True, states={'reject': [('invisible', False)]}, invisible=True)
    order_line_ids = fields.One2many('purchase.request.line', 'purchase_request_id', string='Order Lines')
    total_price = fields.Float(string='Total Price', compute='_compute_total_price', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('to_be_approved', 'To be Approved'),
        ('approved', 'Approved'),
        ('reject', 'Rejected'),
        ('cancel', 'Cancelled')
    ], string='Status', readonly=True, default='draft')

    @api.depends('order_line_ids.total')
    def _compute_total_price(self):
        for request in self:
            request.total_price = sum(line.total for line in request.order_line_ids)

    def action_submit_for_approval(self):
        self.state = 'to_be_approved'

    def action_cancel(self):
        self.state = 'cancel'
        
    def send_notifications(self, group_xml_id, subject, body, user_id=False):
        partner_ids = []
        body = f"""<p>Hello,</p><p>Purchase Request ({self.name}) has been approved.</p>"""

  
        group = self.env.ref('purchase.group_purchase_manager')

        if group:
            users = self.env['res.users'].search([('groups_id', 'in', [group.id])])
            for user in users:
                partner_ids.append(user.partner_id.id)
            if user_id and user_id.partner_id.id not in partner_ids:
                partner_ids.append(user_id.partner_id.id)

            if partner_ids:
                create_values = {
                    'body_html': body,
                    'subject': subject,
                    'email_from': self.env.user.email,
                    'recipient_ids': [(4, pid) for pid in partner_ids],
                }
                mail = self.env['mail.mail'].sudo().create(create_values)
                mail.sudo().send()

    def action_approve(self):
        self.state = 'approved'
        for rec in self:
            template = self.env.ref("Purchase_Request.email_template_purchase_request_approved")
            subject = template._render_field('subject', self.ids, compute_lang=True)[self.id]
            body = template._render_field('body_html', self.ids, compute_lang=True)[self.id]
            rec.send_notifications([], subject, body, self.create_uid)         

             
        
    def action_reject(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reject Reason',
            'res_model': 'reject.reason.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_purchase_request_id': self.id},
        }

    def action_reset_to_draft(self):
        self.state = 'draft'
