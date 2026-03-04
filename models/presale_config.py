# -*- coding: utf-8 -*-
from odoo import models, fields

class IncomingQueryMethod(models.Model):
    """
    Master data model for defining lead acquisition channels.
    Allows administrators to categorize queries by their origin (e.g., Upwork, Email).
    """
    _name = 'incoming.query.method'
    _description = 'Incoming Query Method'
    _order = 'sequence, name'

    name = fields.Char(
        string='Method Name',
        required=True,
        translate=True,
        help="Unique name for the acquisition channel (e.g., Fiverr, Direct Call)."
    )
    sequence = fields.Integer(
        default=10,
        help="Display priority for sorting in Kanban and Selection lists."
    )
    color = fields.Integer(
        string='Color',
        help="Color index (0-11) for visual representation in the UI boards."
    )
    active = fields.Boolean(
        default=True,
        help="Operational flag. Set to false to archive a method without breaking historical data."
    )


class LeadStatus(models.Model):
    """
    Workflow Stage Configuration.
    Defines the possible states for both Inquiries and Pipeline Leads.
    """
    _name = 'lead.status'
    _description = 'Lead Status'
    _order = 'sequence, name'

    name = fields.Char(
        string='Stage Name',
        required=True,
        translate=True,
        help="Descriptive name of the workflow stage (e.g., Contacted, Quotation Sent)."
    )
    sequence = fields.Integer(
        default=10,
        help="Numerical order used for the CRM pipeline progress bar."
    )
    color = fields.Integer(
        string='Color Index'
    )
    is_won_stage = fields.Boolean(
        string='Is Won Stage?',
        default=False,
        help="If checked, any lead entering this stage will be marked as WON in Odoo reporting."
    )
    is_lead_pipeline = fields.Boolean(
        string='Is Lead Pipeline?',
        default=True,
        help="Determines if this status is selectable in the Pipeline stage or just the Inquiry stage."
    )
    active = fields.Boolean(
        default=True
    )

class CurrentCondition(models.Model):
    """
    Micro-state tracking for Leads.
    Provides granular visibility into the health of a lead negotiation
    (e.g., Awaiting Feedback, Budget Confirmed).
    """
    _name = 'current.condition'
    _description = 'Current Condition'
    _order = 'sequence, name'

    name = fields.Char(
        string='Condition Name',
        required=True,
        translate=True,
        help="Internal status label for account management."
    )
    sequence = fields.Integer(
        default=10
    )
    color = fields.Integer(
        string='Color Index'
    )
    active = fields.Boolean(
        default=True
    )

