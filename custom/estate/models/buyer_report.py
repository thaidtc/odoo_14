# -*- coding: utf-8 -*-

from odoo import models, fields, api, tools

class EstatePropertyBuyerReport(models.Model):
    _name = "estate.property.buyer.report"
    _description = "Real Estate Buyer Statistics Report"
    _auto = False  # Điều này báo cho Odoo biết KHÔNG tự động tạo bảng
    _rec_name = 'buyer_id'  # Trường sẽ được dùng làm tên cho bản ghi

    buyer_id = fields.Many2one('res.partner', string='Buyer', readonly=True)
    email = fields.Char(string='Email', readonly=True)
    state_offer_accepted = fields.Integer(string='Property Accepted', readonly=True)
    state_sold = fields.Integer(string='Property Sold', readonly=True)
    state_canceled = fields.Integer(string='Property Canceled', readonly=True)
    offers_accepted = fields.Integer(string='Offers Accepted', readonly=True)
    offers_refused = fields.Integer(string='Offers Refused', readonly=True)
    max_offer_price = fields.Float(string='Max Price Offer', readonly=True)
    min_offer_price = fields.Float(string='Min Price Offer', readonly=True)

    def init(self):
        # Hàm init này sẽ chạy khi module được cài đặt hoặc cập nhật
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute(f"""
            CREATE OR REPLACE VIEW {self._table} AS
            SELECT
                row_number() OVER () as id, -- Odoo bắt buộc phải có trường id
                prop.buyer_id,
                partner.email as email,
                COUNT(CASE WHEN prop.state = 'offer_accepted' THEN 1 END) as state_offer_accepted,
                COUNT(CASE WHEN prop.state = 'sold' THEN 1 END) as state_sold,
                COUNT(CASE WHEN prop.state = 'canceled' THEN 1 END) as state_canceled,
                COUNT(CASE WHEN offer.status = 'accepted' THEN 1 END) as offers_accepted,
                COUNT(CASE WHEN offer.status = 'refused' THEN 1 END) as offers_refused,
                MAX(offer.price) as max_offer_price,
                MIN(offer.price) as min_offer_price
            FROM
                estate_property prop
            LEFT JOIN
                estate_property_offer offer ON prop.id = offer.property_id
            LEFT JOIN
                res_partner partner ON prop.buyer_id = partner.id
            WHERE
                prop.buyer_id IS NOT NULL -- Chỉ lấy những property đã có người mua
            GROUP BY
                prop.buyer_id, partner.email
        """)