import {
    ProductConfiguratorDialog
} from '@sale/js/product_configurator_dialog/product_configurator_dialog';
import { _t } from '@web/core/l10n/translation';
import { patch } from '@web/core/utils/patch';
import { user } from "@web/core/user";
import { onWillStart } from "@odoo/owl";
import { Product } from '@sale/js/product/product';
import { AddToCartNotification } from "@website_sale/js/notification/add_to_cart_notification/add_to_cart_notification";




patch(ProductConfiguratorDialog.prototype, {
    setup() {
        super.setup(...arguments);
        onWillStart(async () => {
            this.hasGroupAdmin = await user.hasGroup("westborn.group_beneficiary_admin");
        });
    },

    /**
     * Check whether all selected products can be sold.
     *
     * @return {Boolean} - Whether all selected products can be sold.
     */

    /**
     * Check whether to show the "shop" buttons in the dialog footer.
     *
     * @return {Boolean} - Whether to show the "shop" buttons in the dialog footer.
     */

    get totalMessage() {
        if (this.env.isFrontend) {
            // To be translated, the title must be repeated here. Indeed, only
            // translations of "frontend modules" are fetched in the context of
            // website. The original definition of the title is in "sale", which
            // is not a frontend module.
            if (!this.hasGroupAdmin) {
                return _t("Total Credits :%s", this.getFormattedCredits());
            }
            else {
            return _t("Total: %s", this.getFormattedTotal());
            }
        }
        return super.totalMessage(...arguments);
    },
    getFormattedCredits() {
        const total_credits = (this.state.products || []).reduce(
            (sum, product) => sum + product.credit_value * product.quantity,
            0
        );
        return total_credits;
    },

});




patch(Product.prototype, {
    setup() {
        super.setup(...arguments);
        onWillStart(async () => {
            this.hasGroupAdmin = await user.hasGroup("westborn.group_beneficiary_admin");
        });
    },
        /**
     * Return the price, in the format of the given currency.
     *
     * @return {String} - The price, in the format of the given currency.
     */
    getFormattedPrice() {
        if (!this.hasGroupAdmin) {
            return this.props.credit_value || 0;
        }
        else {
            return super.getFormattedPrice(...arguments);
        }
    }

});

patch(AddToCartNotification.prototype, {
    setup() {
        super.setup(...arguments);
        onWillStart(async () => {
            this.mainLines[0].credit_point = await this.env.services.orm.call('sale.order.line', 'get_line_total_credit', [this.mainLines[0].id]);
            this.hasGroupAdmin = await user.hasGroup("westborn.group_beneficiary_admin");
        });
    },
     /**
     * Return the price, in the format of the sale order currency.
     *
     * @param {Object} line - The line element for which to return the formatted price.
     * @return {String} - The price, in the format of the sale order currency.
     */
    getFormattedPrice(line) {
        if (!this.hasGroupAdmin) {
            return line.credit_point + " Credits"|| 0 + " Credits";
        }
        return super.getFormattedPrice(line);
    }
});
