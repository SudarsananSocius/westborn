import { useSubEnv } from '@odoo/owl';
import {
    ProductConfiguratorDialog
} from '@sale/js/product_configurator_dialog/product_configurator_dialog';
import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';
import { user } from "@web/core/user";
import { Component, onWillStart, onWillRender } from "@odoo/owl";
import { Product } from '@sale/js/product/product';
import { useService } from "@web/core/utils/hooks";



// patch(ProductConfiguratorDialog, {
//     props: {
//         ...ProductConfiguratorDialog.props,
//         isFrontend: { type: Boolean, optional: true },
//         options: {
//             ...ProductConfiguratorDialog.props.options,
//             shape: {
//                 ...ProductConfiguratorDialog.props.options.shape,
//                 isMainProductConfigurable: { type: Boolean, optional: true },
//                 isBuyNow: { type: Boolean, optional: true },
//             },
//         },
//     },
// });

patch(ProductConfiguratorDialog.prototype, {
    setup() {
        this.orm = useService("orm");
        super.setup(...arguments);
        console.log("Patched ProductConfiguratorDialog for portal");

        onWillStart(async () => {
            console.log("On will start called");
            this.hasGroupAdmin = await user.hasGroup("Brightpath_UK.group_beneficiary_admin");
        });
        onWillRender(async () => {
            console.log("On will render called");
            if (this.hasGroupAdmin) {
                this.fetchProducts();
            }
        });
    },
    async fetchProducts() {
        this.product_list = [];
            console.log("On will render called", this);
            for (let i=0; i<this.state.products.length; i++) {
                let product_id = this.state.products[i].product_tmpl_id;
                var product = await this.orm.searchRead('product.template',[['id', '=', product_id]],['credit_value'],{ limit: 1 });
                if (product.length > 0) {
                    this.product_list.push({
                        'id': product_id,
                        'credit_value': product[0].credit_value,
                        'quantity': this.state.products[i].quantity,
                    });
                }
            }
            const total_field = document.querySelector('.o_configurator_price_total');
            if (total_field) {
                total_field.innerText = this.product_list.reduce((acc, product) =>  "Total Credits : "+ ((product.credit_value * product.quantity )|| 0), 0);
            }
    },

});




patch(Product.prototype, {
    setup() {
        this.orm = useService("orm");
        super.setup(...arguments);
        console.log("Patched ProductConfiguratorDialog for portal");
        onWillStart(async () => {
            this.hasGroupAdmin = await user.hasGroup("Brightpath_UK.group_beneficiary_admin");
        });
        onWillRender(async () => {
            console.log("On will render called");
            if (this.hasGroupAdmin) {
                this.fetchProducts();
            }
        });
    },
    async fetchProducts() {
        this.product_list = [];
            console.log("On will render called", this);
            for (let i=0; i<this.state.products.length; i++) {
                let product_id = this.state.products[i].product_tmpl_id;
                var product = await this.orm.searchRead('product.template',[['id', '=', product_id]],['credit_value'],{ limit: 1 });
                if (product.length > 0) {
                    this.product_list.push({
                        'id': product_id,
                        'credit_value': product[0].credit_value,
                        'quantity': this.state.products[i].quantity,
                    });
                }
            }
            const total_field = document.querySelector('.o_configurator_price_total');
            if (total_field) {
                total_field.innerText = this.product_list.reduce((acc, product) =>  "Total Credits : "+ ((product.credit_value * product.quantity )|| 0), 0);
            }
    },
});
