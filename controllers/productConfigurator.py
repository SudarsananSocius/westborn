from odoo.http import route
from odoo.addons.sale.controllers.product_configurator import SaleProductConfiguratorController
from odoo.addons.website_sale.controllers.main import WebsiteSale


class WestbornProductConfiguratorController(SaleProductConfiguratorController, WebsiteSale):
    
    @route(
        route='/website_sale/product_configurator/get_values',
        type='jsonrpc',
        auth='public',
        website=True,
        readonly=True,
    )
    def custom_sale_product_configurator_get_values(self, *args, **kwargs):
        self._populate_currency_and_pricelist(kwargs)
        res = super().sale_product_configurator_get_values(*args, **kwargs)
        for product in res['products']:
            product_template_id = product.get('product_tmpl_id')
            if product_template_id:
                product_id = self.env['product.template'].browse(product_template_id)
                if product_id:
                    product['credit_value'] = product_id.credit_value
        return res