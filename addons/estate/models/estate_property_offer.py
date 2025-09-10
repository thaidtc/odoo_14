from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError


class EstatePropertyOffer(models.Model):
    _name = "estate.property.offer"
    _description = "Estate Property Offer"
    _order = "price desc"

    price = fields.Float(string="Offer Price", required=True)
    status = fields.Selection(
        [("accepted", "Accepted"), ("refused", "Refused"), ("pending", "Pending")],
        string="Status",
        default="pending",
        copy=False,
    )
    validity = fields.Integer(string="Validity (days)", default=7)
    date_deadline = fields.Date(
        string="Deadline", compute="_compute_date_deadline", store=True
    )

    # ========= Relationship ==========
    partner_id = fields.Many2one("res.partner", string="Partner", required=True)
    property_id = fields.Many2one("estate.property", string="Property", required=True)
    property_type_id = fields.Many2one(
        comodel_name="estate.property.type",
        string="Property Type",
        related="property_id.property_type_id",
        store=True,
        readonly=True,
    )

    @api.depends("validity", "create_date")
    def _compute_date_deadline(self):
        for offer in self:
            if offer.create_date:
                create_date = fields.Datetime.from_string(offer.create_date)
                offer.date_deadline = create_date + timedelta(days=offer.validity)
            else:
                offer.date_deadline = False

    # CONSTRAINTS
    @api.constrains("price")
    def _check_offer_price(self):
        for offer in self:
            if offer.price <= 0:
                raise ValidationError("Offer price must be strictly positive!")

    # SQL CONSTRAINTS
    _sql_constraints = [
        (
            "check_offer_price_positive",
            "CHECK(price > 0)",
            "Offer price must be strictly positive!",
        ),
    ]

    def action_accept_offer(self):
        for offer in self:
            if offer.property_id.state == "sold":
                raise UserError("Cannot accept offer for a sold property!")
            if offer.property_id.state == "canceled":
                raise UserError("Cannot accept offer for a canceled property!")

            # KIỂM TRA CONSTRAINT KHI ACCEPT OFFER
            min_allowed_price = offer.property_id.expected_price * 0.9
            if offer.price < min_allowed_price:
                raise UserError(
                    f"Cannot accept offer! Price cannot be lower than 90% of expected price. "
                    f"Minimum allowed: {min_allowed_price:,.2f}"
                )

            other_offers = offer.property_id.offer_ids - offer
            other_offers.write({"status": "refused"})

            offer.status = "accepted"
            offer.property_id.state = "offer_accepted"
        return True

    def action_refuse_offer(self):
        for offer in self:
            if offer.status == "accepted":
                raise UserError("Cannot refuse an accepted offer!")
            offer.status = "refused"
        return True

    @api.model
    def create(self, vals):
        """Override create method để chặn tạo offer khi property không ở trạng thái phù hợp"""
        if "property_id" in vals:
            property_id = self.env["estate.property"].browse(vals["property_id"])
            if property_id.state in ["offer_accepted", "sold", "canceled"]:
                raise UserError(
                    "Cannot create offer for a property that is already accepted, sold or canceled!"
                )
        return super().create(vals)

    def write(self, vals):
        """Override write method để chặn chỉnh sửa offer khi property không ở trạng thái phù hợp"""
        if "property_id" in vals:
            property_id = self.env["estate.property"].browse(vals["property_id"])
            if property_id.state in ["offer_accepted", "sold", "canceled"]:
                raise UserError(
                    "Cannot modify offer for a property that is already accepted, sold or canceled!"
                )
        return super().write(vals)

    @api.onchange("property_id")
    def _onchange_property_id(self):
        """Hiển thị cảnh báo khi chọn property không phù hợp"""
        if self.property_id and self.property_id.state in [
            "offer_accepted",
            "sold",
            "canceled",
        ]:
            return {
                "warning": {
                    "title": "Invalid Property Selection",
                    "message": "Cannot create offer for a property that is already accepted, sold or canceled!",
                }
            }
