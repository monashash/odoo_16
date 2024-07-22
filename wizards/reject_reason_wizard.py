from odoo import models, fields, api

class RejectReasonWizard(models.TransientModel):
    _name = 'reject.reason.wizard'
    _description = 'Reject Reason Wizard'

    rejection_reason = fields.Text(string='Rejection Reason', required=True)
    purchase_request_id = fields.Many2one('purchase.request', string='Purchase Request', required=True)

    def action_confirm(self):
        self.purchase_request_id.write({
            'state': 'reject',
            'rejection_reason': self.rejection_reason,
        })
        return {'type': 'ir.actions.act_window_close'}
