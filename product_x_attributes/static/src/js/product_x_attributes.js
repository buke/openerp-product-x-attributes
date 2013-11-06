/*##############################################################################
#
#    Product X Attributes
#    Copyright 2013 wangbuke <wangbuke@gmail.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################*/

openerp.product_x_attributes = function(instance) {
    var _t = instance.web._t, _lt = instance.web._lt;
    instance.web.form.compute_domain = function(expr, fields) {
        if (! (expr instanceof Array))
            return !! expr;
        var stack = [];
        for (var i = expr.length - 1; i >= 0; i--) {
            var ex = expr[i];
            if (ex.length == 1) {
                var top = stack.pop();
                switch (ex) {
                    case '|':
                        stack.push(stack.pop() || top);
                        continue;
                    case '&':
                        stack.push(stack.pop() && top);
                        continue;
                    case '!':
                        stack.push(!top);
                        continue;
                    default:
                        throw new Error(_.str.sprintf(
                            _t("Unknown operator %s in domain %s"),
                            ex, JSON.stringify(expr)));
                }
            }

            var field = fields[ex[0]];
            if (!field) {
                throw new Error(_.str.sprintf(
                    _t("Unknown field %s in domain %s"),
                    ex[0], JSON.stringify(expr)));
            }
            var field_value = field.get_value ? field.get_value() : field.value;
            var op = ex[1];
            var val = ex[2];

            switch (op.toLowerCase()) {
                case '=':
                case '==':
                    stack.push(_.isEqual(field_value, val));
                    break;
                case '!=':
                case '<>':
                    stack.push(!_.isEqual(field_value, val));
                    break;
                case '<':
                    stack.push(field_value < val);
                    break;
                case '>':
                    stack.push(field_value > val);
                    break;
                case '<=':
                    stack.push(field_value <= val);
                    break;
                case '>=':
                    stack.push(field_value >= val);
                    break;
                case 'in':
                    if (!_.isArray(val)) val = [val];
                    stack.push(_(val).contains(field_value));
                    break;
                case 'not in':
                    if (!_.isArray(val)) val = [val];
                    stack.push(!_(val).contains(field_value));
                    break;
                case 'contains':
                    if (field.field.type === 'many2many'|| field.field.type === 'one2many'){
                        field_value = field.get("value");
                    }
                    if (!_.isArray(field_value)) field_value = [field_value];
                    stack.push(_(field_value).contains(val));
                    break;
                case 'not contains':
                    if (field.field.type === 'many2many'|| field.field.type === 'one2many'){
                        field_value = field.get("value");
                    }
                    if (!_.isArray(field_value)) field_value = [field_value];
                    stack.push(!_(field_value).contains(val));
                    break;

                default:
                    console.warn(
                        _t("Unsupported operator %s in domain %s"),
                        op, JSON.stringify(expr));
            }
        }
        return _.all(stack, _.identity);
    };

    instance.web.form.FieldMany2ManyTags = instance.web.form.FieldMany2ManyTags.extend({
        //get_search_result: function(search_val) {
             //this._super(search_val);
        //},
        get_search_result: function(search_val) {
            var self = this;

            var dataset = new instance.web.DataSet(this, this.field.relation, self.build_context());
            var blacklist = this.get_search_blacklist();
            this.last_query = search_val;

            return this.orderer.add(dataset.name_search(
                    search_val, new instance.web.CompoundDomain(self.build_domain(), [["id", "not in", blacklist]]),
                    'ilike', this.limit + 1, self.build_context())).then(function(data) {
                self.last_search = data;
                // possible selections for the m2o
                var values = _.map(data, function(x) {
                    x[1] = x[1].split("\n")[0];
                    return {
                        label: _.str.escapeHTML(x[1]),
                        value: x[1],
                        name: x[1],
                        id: x[0],
                    };
                });

                // search more... if more results that max
                if (values.length > self.limit) {
                    values = values.slice(0, self.limit);
                    values.push({
                        label: _t("Search More..."),
                        action: function() {
                            dataset.name_search(search_val, self.build_domain(), 'ilike', false).done(function(data) {
                                self._search_create_popup("search", data);
                            });
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                if (self.name !== "all_attribute_group_ids") {
                    // quick create
                    var raw_result = _(data.result).map(function(x) {return x[1];});
                    if (search_val.length > 0 && !_.include(raw_result, search_val)) {
                        values.push({
                            label: _.str.sprintf(_t('Create "<strong>%s</strong>"'),
                                $('<span />').text(search_val).html()),
                            action: function() {
                                self._quick_create(search_val);
                            },
                            classname: 'oe_m2o_dropdown_option'
                        });
                    }
                    // create...
                    values.push({
                        label: _t("Create and Edit..."),
                        action: function() {
                            self._search_create_popup("form", undefined, self._create_context(search_val));
                        },
                        classname: 'oe_m2o_dropdown_option'
                    });
                }

                return values;
            });
        },

    });
        //this._super(field_manager, node);

};

