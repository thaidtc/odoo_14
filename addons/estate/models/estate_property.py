from odoo import models, fields, api
from datetime import timedelta
from odoo.exceptions import ValidationError, UserError


class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Estate Property"

    # Các trường cơ bản
    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.today() + timedelta(days=90),
    )
    expected_price = fields.Float(string="Expected Price", required=True)
    selling_price = fields.Float(string="Selling Price", readonly=True, copy=False)
    bedrooms = fields.Integer(string="Bedrooms", default=2)
    living_area = fields.Integer(string="Living Area (sqm)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Garden")
    garden_area = fields.Integer(string="Garden Area (sqm)")
    garden_orientation = fields.Selection(
        string="Garden Orientation",
        selection=[
            ("north", "North"),
            ("south", "South"),
            ("east", "East"),
            ("west", "West"),
        ],
    )

    active = fields.Boolean(string="Active", default=True)

    state = fields.Selection(
        string="Status",
        selection=[
            ("new", "New"),
            ("offer_received", "Offer Received"),
            ("offer_accepted", "Offer Accepted"),
            ("sold", "Sold"),
            ("canceled", "Canceled"),
        ],
        required=True,
        copy=False,
        default="new",
    )

    # CALCULATED FIELDS
    total_area = fields.Integer(
        string="Total Area (m²)", compute="_compute_total_area", store=True
    )

    best_price = fields.Float(
        string="Best Offer", compute="_compute_best_price", store=True
    )

    # ========= Relationship ==========
    property_type_id = fields.Many2one("estate.property.type", string="Property Type")
    buyer_id = fields.Many2one("res.partner", string="Buyer", copy=False)
    salesperson_id = fields.Many2one(
        "res.users", string="Salesperson", default=lambda self: self.env.user
    )
    tag_ids = fields.Many2many("estate.property.tag", string="Tags")
    offer_ids = fields.One2many("estate.property.offer", "property_id", string="Offers")

    # METHODS
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for record in self:
            if record.offer_ids:
                valid_offers = record.offer_ids.filtered(lambda o: o.price > 0)
                if valid_offers:
                    record.best_price = max(valid_offers.mapped("price"))
                else:
                    record.best_price = 0.0
            else:
                record.best_price = 0.0

    # ONCHANGE METHODS
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # onChange valid - return message
    @api.onchange("date_availability")
    def _onchange_date_availability(self):
        print("=== ONCHANGE TRIGGERED ===")  # Debug
        self.ensure_one()
        for record in self:
            if record.date_availability:
                today = fields.Date.today()
                print(
                    f"Selected date: {self.date_availability}, Today: {today}"
                )  # Debug
                if record.date_availability < today:
                    print("=== WARNING SHOULD SHOW ===")  # Debug
                    return {
                        "warning": {
                            "title": "Invalid Date",
                            "message": "The availability date cannot be set before today! Please select a future date.",
                        }
                    }

    # CONSTRAINTS - Chặn submit form
    @api.constrains("date_availability")
    def _check_date_availability(self):
        for record in self:
            if record.date_availability:
                if record.date_availability < fields.Date.today():
                    raise ValidationError(
                        "The availability date cannot be set before today! Please select a future date."
                    )

    # ACTION METHODS

    def action_set_canceled(self):
        """SET CANCELED"""
        for record in self:
            if record.state == "sold":
                raise UserError("Cannot cancel a sold property!")
            record.state = "canceled"
            record.active = False
        return True

    def action_set_sold(self):
        """SET SOLD"""
        for record in self:
            if record.state == "canceled":
                raise UserError("Cannot sell a canceled property!")
            if not record.offer_ids:
                raise UserError("Cannot sell a property without any offers!")

            accepted_offer = record.offer_ids.filtered(lambda o: o.status == "accepted")
            if not accepted_offer:
                raise UserError("Cannot sell without an accepted offer!")

            # KIỂM TRA CONSTRAINT TRƯỚC KHI SET SOLD
            min_allowed_price = record.expected_price * 0.9
            if accepted_offer.price < min_allowed_price:
                raise UserError(
                    f"Cannot accept offer! Selling price cannot be lower than 90% of expected price. "
                    f"Minimum allowed: {min_allowed_price:,.2f}"
                )

            record.state = "sold"
            record.selling_price = accepted_offer.price
            record.buyer_id = accepted_offer.partner_id
        return True

    # PRICE CONSTRAINTS
    @api.constrains("expected_price", "selling_price")
    def _check_selling_price_vs_expected(self):
        """
        Kiểm tra giá bán không thấp hơn 90% giá kỳ vọng
        Chỉ kiểm tra khi selling_price > 0 (đã có offer accepted)
        """
        for record in self:
            if record.selling_price > 0 and record.expected_price > 0:
                min_allowed_price = record.expected_price * 0.9
                if record.selling_price < min_allowed_price:
                    raise ValidationError(
                        f"Selling price cannot be lower than 90% of expected price! "
                        f"Minimum allowed: {min_allowed_price:,.2f}"
                    )

    @api.constrains("expected_price", "selling_price")
    def _check_prices(self):
        for record in self:
            if record.expected_price <= 0:
                raise ValidationError("Expected price must be strictly positive!")
            if record.selling_price < 0:
                raise ValidationError("Selling price cannot be negative!")

    # SQL CONSTRAINTS
    _sql_constraints = [
        (
            "check_expected_price_positive",
            "CHECK(expected_price > 0)",
            "Expected price must be strictly positive!",
        ),
        (
            "check_selling_price_positive",
            "CHECK(selling_price >= 0)",
            "Selling price must be positive!",
        ),
    ]
