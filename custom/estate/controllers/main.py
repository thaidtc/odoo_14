from odoo import http
from odoo.http import request
import json

class EstateController(http.Controller):

    # Route đơn giản nhất: Trang giới thiệu
    @http.route('/estate/intro', type='http', auth='public', website=True)
    def estate_introduction(self, **kwargs):
        # Lấy thông tin công ty
        company = request.env['res.company'].sudo().search([], limit=1)
        # Render template 'estate_intro_template' và truyền biến 'company' vào
        return request.render('estate.estate_intro_template', {
            'company': company
        })
    
     # Route cho API JSON
    @http.route('/api/estate/properties', type='http', auth='public', methods=['GET'], csrf=False)
    def estate_properties_api(self, **kwargs):
        try:
            # Lấy tham số limit, mặc định là 20
            limit = int(kwargs.get('limit', 20))
            domain = []  # Filter mặc định

            # Truy vấn database
            properties = request.env['estate.property'].sudo().search(domain, limit=limit)
            
            # Chuẩn bị dữ liệu JSON
            property_list = []
            for prop in properties:
                property_list.append({
                    'id': prop.id,
                    'name': prop.name,
                    'expected_price': prop.expected_price,
                    'best_price': prop.best_price,
                    'state': prop.state,
                })
            
            # Tạo response
            response_data = {
                'status': 200,
                'message': 'Success',
                'count': len(property_list),
                'data': property_list
            }

            # Trả về JSON
            return request.make_response(
                json.dumps(response_data),
                headers=[('Content-Type', 'application/json')]
            )
        except Exception as e:
            # Trả về lỗi nếu có exception
            error_data = {'status': 500, 'error': str(e)}
            return request.make_response(
                json.dumps(error_data),
                headers=[('Content-Type', 'application/json')],
                status=500
            )