# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import date


class CrmLeadInherit(models.Model):
    """
    Core business model for the Pre-Sale module.
    Inherits from Odoo's native 'crm.lead' to provide a specialized workflow for
    incoming queries and senior-level pipeline management.

    Key functional areas:
    - Isolation of pre-sale records via 'is_presale' flag.
    - Automated lead promoting (Inquiry -> Pipeline).
    - Advanced cross-model data mapping for sale order generation.
    - Status-driven 'WON' automation.
    """
    _inherit = 'crm.lead'

    # -------------------------------------------------------------------------
    # PERSISTENCE & DATA MAPPING
    # -------------------------------------------------------------------------

    name = fields.Char(
        string='Label',
        default=lambda self: f"Query / {fields.Date.today()}",
        help="Internal identification label for the record."
    )

    is_presale = fields.Boolean(
        string='Is Pre-Sale',
        default=False,
        index=True,
        help="Architectural flag to isolate these records from standard CRM views."
    )

    entry_date = fields.Date(
        string='Entry Date',
        default=fields.Date.today,
        readonly=True,
        store=True,
        tracking=True,
        index=True,
        help="Immutable record creation date for audit and reporting."
    )

    # -------------------------------------------------------------------------
    # RELATIONSHIPS (MASTER DATA)
    # -------------------------------------------------------------------------

    incoming_query_method_id = fields.Many2one(
        comodel_name='incoming.query.method',
        string='Query Method',
        tracking=True,
        index=True,
        help="The channel through which the inquiry was received (e.g., Fiverr, Upwork)."
    )

    method_color = fields.Integer(
        related='incoming_query_method_id.color',
        string='Method Color',
        help="Dynamic UI color code fetched from the method master data."
    )

    lead_status_id = fields.Many2one(
        comodel_name='lead.status',
        string='Lead Status',
        tracking=True,
        index=True,
        help="Workflow stage identifier."
    )

    status_color = fields.Integer(
        related='lead_status_id.color',
        string='Status Color'
    )

    project_category_id = fields.Many2one(
        comodel_name='product.template',
        string='Project Category',
        tracking=True,
        help="Linked product template used for automated quotation generation."
    )

    current_condition_id = fields.Many2one(
        comodel_name='current.condition',
        string='Current Condition',
        tracking=True,
        help="Detailed health/progress status of the lead negotiation."
    )

    condition_color = fields.Integer(
        related='current_condition_id.color',
        string='Condition Color'
    )

    # -------------------------------------------------------------------------
    # LEAD PROFILE & CLIENT METRIC FIELDS
    # -------------------------------------------------------------------------

    profile_id = fields.Many2one(
        comodel_name='bd.profile',
        string='Profile',
        domain="[('platform_source_id', '=', platform_source_id)]",
        tracking=True,
        help="Specific client profile related to the platform source."
    )

    platform_source_id = fields.Many2one(
        comodel_name='bd.platform_source',
        string='Platform Source',
        tracking=True,
        help="The originating platform for the client profile."
    )

    amount = fields.Float(
        string='Amount',
        tracking=True,
        help="Estimated financial value associated with the query/lead."
    )

    job_link = fields.Char(
        string='Job Link',
        tracking=True,
        help="Direct reference or URL to the original job posting."
    )

    meeting_link = fields.Char(
        string='Meeting Link',
        tracking=True,
        help="Link to the scheduled video call or meeting room."
    )

    priority = fields.Selection([
        ('0', 'No Priority'),
        ('1', 'Low'),
        ('2', 'Medium'),
        ('3', 'High'),
        ('4', 'Very High'),
        ('5', 'Critical'),
    ], string='Priority', default='0', tracking=True,
       help="User-defined importance level (0-5 stars).")

    # -------------------------------------------------------------------------
    # COMPUTED FIELDS & UI HELPERS
    # -------------------------------------------------------------------------

    conversion_status = fields.Selection([
        ('query', 'Query'),
        ('converted', 'Converted'),
    ], string='Conversion Status', compute='_compute_conversion_status', store=True,
       help="Internal state tracking for the pre-sale record lifecycle.")

    quote_link = fields.Char(string='Quote Link', tracking=True)
    quote_display_text = fields.Char(string='Quote Label', tracking=True)
    quote_html = fields.Html(
        string='Quote Interface',
        compute='_compute_quote_html',
        help="Technological helper to render specialized links in the form/list views."
    )

    account_name = fields.Char(string='Account Name', tracking=True)
    client_link = fields.Char(string='Client Link', tracking=True)
    note = fields.Text(string='Internal Notes', tracking=True)

    # -------------------------------------------------------------------------
    # BUSINESS LOGIC (COMPUTES & HELPERS)
    # -------------------------------------------------------------------------

    @api.depends('type')
    def _compute_conversion_status(self):
        """
        Determines the conversion state of the record.
        'Query' for initial leads, 'Converted' once promoted to opportunities.
        """
        for lead in self:
            lead.conversion_status = 'converted' if lead.type == 'opportunity' else 'query'

    @api.depends('quote_link', 'quote_display_text')
    def _compute_quote_html(self):
        """
        Professional UI helper: Renders a clickable font-awesome icon and label
        for external document links. Ensures a smooth UX for account managers.
        """
        for lead in self:
            if lead.quote_link:
                text = lead.quote_display_text or lead.quote_link
                lead.quote_html = f'<a href="{lead.quote_link}" target="_blank" style="text-decoration:none;"><i class="fa fa-file-text-o"></i> {text}</a>'
            else:
                lead.quote_html = False

    def action_incoming_query_back(self):
        """
        UI Navigation helper: Returns the action for the Incoming Query dashboard,
        enabling a seamless 'Back' experience for users.
        """
        action = self.env.ref('beto_crm.action_incoming_query').read()[0]
        return action

    def _prepare_opportunity_quotation_context(self):
        """
        ADVID/ERP Optimization: Overrides standard context preparation to inject
        custom pre-sale metadata into new Sale Orders. This eliminates redundant
        manual data entry for sales teams.
        """
        quotation_context = super(CrmLeadInherit, self)._prepare_opportunity_quotation_context()
        
        # Inject platform mapping
        if self.platform_source_id:
            quotation_context['default_platform_source_id'] = self.platform_source_id.id
        if self.profile_id:
            quotation_context['default_profile_id'] = self.profile_id.id
        
        # Inject project category as the primary product line
        if self.project_category_id:
            variant = self.project_category_id.product_variant_id
            if variant:
                quotation_context['default_order_line'] = [(0, 0, {
                    'product_id': variant.id, 
                    'product_uom_qty': 1.0,
                    'sequence': 1,
                })]
        return quotation_context

    def action_create_lead_from_query(self):
        """
        Core Workflow Transition: Promotes an initial Inquiry to the Lead Pipeline.
        Updates internal record state (type/is_presale) and redirects the user
        to the specialized Pipeline Form view.
        """
        self.ensure_one()
        # Atomic database operation to ensure data consistency
        self.write({
            'type': 'opportunity', 
            'is_presale': True,
        })
        return {
            'name': 'Lead Pipeline',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'res_id': self.id,
            'view_mode': 'form',
            'view_id': self.env.ref('beto_crm.view_custom_lead_pipeline_form').id,
            'target': 'current',
        }

    def _handle_won_status_transition(self):
        """
        Internal Business Rule: Intercepts Lead Status changes. If the new status
        is marked as a 'WON' stage in configuration, invokes Odoo's native CRM
        logic to finalize the deal and update reporting KPIs.
        """
        to_mark_won = self.filtered(lambda l: l.lead_status_id.is_won_stage and l.probability < 100)
        if to_mark_won:
            to_mark_won.action_set_won()

    # -------------------------------------------------------------------------
    # CRUD OVERRIDES
    # -------------------------------------------------------------------------

    @api.model_create_multi
    def create(self, vals_list):
        """
        High-performance create override. Handles batch record initialization,
        automated naming conventions, and initial workflow triggers.
        """
        today = fields.Date.today()
        for vals in vals_list:
            vals.setdefault('entry_date', today)
            if not vals.get('name'):
                vals['name'] = f'Query / {today}'
            vals.setdefault('user_id', self.env.uid)
        
        leads = super(CrmLeadInherit, self).create(vals_list)
        leads._handle_won_status_transition()
        return leads

    def write(self, vals):
        """
        Standard write override to ensure custom business rules (like automated WON triggers)
        are enforced upon record updates.
        """
        res = super(CrmLeadInherit, self).write(vals)
        if 'lead_status_id' in vals:
            self._handle_won_status_transition()
        return res

