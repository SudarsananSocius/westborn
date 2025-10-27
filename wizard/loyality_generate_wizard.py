
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError, UserError
from odoo.tools import email_normalize


class LoyaltyCard(models.Model):
    _inherit = 'loyalty.card'

    assigned_points = fields.Integer(string="Assigned Points", readonly=True)
    email = fields.Char(related='partner_id.email', string="Email", store=True, readonly=True)
    user_id = fields.Many2one('res.users', string='User', compute='_compute_user_id', index=True, store=True)
    email_state = fields.Selection([
        ('ok', 'Valid'),
        ('ko', 'Invalid'),
        ('exist', 'Already Registered')],
        string='Status', compute='_compute_email_state', default='ok')
    is_portal = fields.Boolean('Is Portal', compute='_compute_is_portal', store=True)
    invitation_sent = fields.Boolean(string="Invitation Sent", default=False)
    credit_points = fields.Integer(string="eWallet Credits value", help="Credit points assigned for this loyalty card.")
    available_credits = fields.Integer(string="Available Credits", compute='_compute_available_credits', help="Available credit points of the loyalty card.")
    
    @api.depends('partner_id')
    def _compute_user_id(self):
        """ Compute the user linked to the partner of the loyalty card, if any. """
        for loyality_card_user in self:
            user = loyality_card_user.partner_id.with_context(active_test=False).user_ids
            loyality_card_user.user_id = user[0] if user else False
    
    @api.depends('email')
    def _compute_email_state(self):
        """ Compute the email state of portal users.
        'ok' if the email is valid and not used by another user,
        'exist' if the email is valid but already used by another user,
        'ko' if the email is not valid.
        """
        loyality_card_user = self.filtered(lambda user: email_normalize(user.email))
        (self - loyality_card_user).email_state = 'ko'

        existing_users = self.env['res.users'].with_context(active_test=False).sudo().search_read(
            self._get_similar_users_domain(loyality_card_user),
            self._get_similar_users_fields()
        )
        for portal_user in loyality_card_user:
            if next((user for user in existing_users if self._is_portal_similar_than_user(user, portal_user)), None):
                portal_user.email_state = 'exist'
                portal_user.invitation_sent = True
            else:
                portal_user.email_state = 'ok'

    @api.depends('points', 'use_count')
    def _compute_available_credits(self):
        """ Compute the available credits of the loyalty card. """
        for record in self:
            record.available_credits = int(round(record.points / 20,2))

    @api.onchange('credit_points')
    def _onchange_credit_points(self):
        """ On change of credit points, update the points granted field. """
        if self.credit_points < 0:
            raise ValidationError(_("The number of credit points must be positive."))
        self.points_granted = self.credit_points * 20
        
    
    @api.depends('user_id.is_portal_user')
    def _compute_is_portal(self):
        """ Compute whether the loyalty card is linked to a portal user. """
        for record in self:
            record.is_portal = record.user_id.is_portal_user


    def _update_partner_email(self):
        """Update partner email on portal action, if a new one was introduced and is valid."""
        email_normalized = email_normalize(self.email)
        if self.email_state == 'ok' and email_normalize(self.partner_id.email) != email_normalized:
            self.partner_id.write({'email': email_normalized})


    def _is_portal_similar_than_user(self, user, portal_user):
        """ Checks if the credentials of a portal user and a user are the same
        (users are distinct and their emails are similar).
        """
        return user['login'] == email_normalize(portal_user.email) and user['id'] != portal_user.user_id.id

    def _create_user(self):
        """ create a new user for wizard_user.partner_id
            :returns record of res.users
        """
        return self.env['res.users'].with_context(no_reset_password=True)._create_user_from_template({
            'email': email_normalize(self.email),
            'login': email_normalize(self.email),
            'partner_id': self.partner_id.id,
            'company_id': self.env.company.id,
            'company_ids': [(6, 0, self.env.company.ids)],
        })


    def _assert_user_email_uniqueness(self):
        """Check that the email can be used to create a new user."""
        self.ensure_one()
        if self.email_state == 'ko':
            raise UserError(_('The contact "%s" does not have a valid email.', self.partner_id.name))
        if self.email_state == 'exist':
            print(self.partner_id.name)

    def action_coupon_send(self):
        """ Override to set the invitation_sent field to True when sending the coupon
        to a portal user. """
        self._assert_user_email_uniqueness()
        res = super().action_coupon_send()
        if self.user_id:
            self.invitation_sent = True
            res.update({'invitation_sent': True})
        return res
    

    def _get_similar_users_domain(self, loyality_card_user):
        """ Returns the domain needed to find the users that have the same email
        as portal users.
        :param loyality_card_user: portal users that have an email address.
        """
        normalized_emails = [email_normalize(portal_user.email) for portal_user in loyality_card_user]
        return [('login', 'in', normalized_emails)]

    def _get_similar_users_fields(self):
        """ Returns a list of field elements to extract from users.
        """
        return ['id', 'login']
    
    def _send_email(self):
        """ send notification email to a new portal user """
        self.ensure_one()

        template = self.env.ref('auth_signup.portal_set_password_email')
        if not template:
            raise UserError(_('The template "Portal: new user" not found for sending email to the portal user.'))

        lang = self.user_id.sudo().lang
        partner = self.user_id.sudo().partner_id
        partner.signup_prepare()
        welcome_message = _("Welcome to our company's portal.")

        template.with_context(dbname=self.env.cr.dbname, lang=lang, welcome_message=welcome_message, medium='portalinvite').send_mail(self.user_id.id, force_send=True)

        return True
    
class LoyaltyHistory(models.Model):
    _inherit = 'loyalty.history'

    credit_point = fields.Integer(string="eWallet Credits", help="Credit points assigned for this loyalty history.")

    @api.depends('points')
    def _compute_credit_point(self):
        """ Compute the credit points based on the loyalty history points. """
        for record in self:
            record.credit_point = int(record.points / 20)
    
class LoyaltyCardGenerateWizard(models.TransientModel):
    _inherit = 'loyalty.generate.wizard'
    _description = "Loyalty Card Generate Wizard"

    credit_points = fields.Integer(string="eWallet Credits value", help="Credit points assigned for this loyalty card.")

    @api.onchange('points_granted')
    def _onchange_credit_points(self):
        """ On change of credit points, update the points granted field. """
        user_partner_id = self.env.user.partner_id.id
        cards = self.env['loyalty.card'].search([
            ('partner_id', '=', user_partner_id),
            ('points', '>', 0)
        ])
        assigned_points = sum(self.env['loyalty.card'].search([('create_uid', '=', self.env.user.id)]).mapped('available_credits'))
        total_points = sum(card.points for card in cards)
        available_points = total_points - assigned_points
        
        if self.points_granted < 0:
            raise ValidationError(_("The number of credit points must be positive."))
        self.credit_points = self.points_granted // 20

    
    def generate_coupons(self):
        """ Override to check that the user has enough points to assign the requested
        amount of points to the generated loyalty card. """
        res = super().generate_coupons()
        # partners = self._get_partners()
        user_partner_id = self.env.user.partner_id.id
        cards = self.env['loyalty.card'].search([
            ('partner_id', '=', user_partner_id),
            ('points', '>', 0)
        ])
        assigned_points = sum(self.env['loyalty.card'].search([('create_uid', '=', self.env.user.id)]).mapped('available_credits'))
        total_points = sum(card.points for card in cards)
        available_points = total_points - assigned_points
        if total_points < (self.points_granted + assigned_points):
            raise ValidationError(_("You can only assign a number of points less than or equal to your available points (%s).") % available_points)
        if self.points_granted <= 0:
            raise ValidationError(_("The number of points to redeem must be positive."))
        res.assigned_points = self.points_granted
        return res
    

class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'


    def action_send_mail(self):
        """ Used for action button that do not accept arguments. """
        self._action_send_mail(auto_commit=False)
        active_id = self.env.context.get('active_id')
        if active_id and self.env.context.get('default_model') == 'loyalty.card':
            card = self.env['loyalty.card'].browse(active_id)
            card.invitation_sent = True
        return super().action_send_mail()