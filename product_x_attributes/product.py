# -*- coding: utf-8 -*-
##############################################################################
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
##############################################################################

from openerp.osv import osv, fields
from lxml import etree
import json

class product_category(osv.osv):
    _inherit = "product.category"

    _columns = {
        'attribute_group_id': fields.many2one('attribute.group', 'Default Attribute Group'),
#        'property_attribute_group_id': fields.property(
            #'attribute.group',
            #type='many2one',
            #relation='attribute.group',
            #string="Default Attribute Group",
            #view_load=True,),
    }

class product_product(osv.osv):
    _inherit = "product.product"

    def _get_attr_grp_ids(self, cr, uid, ids, field_names, arg=None, context=None):
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            product_attr_groups = [ag.id for ag in product.attribute_group_ids]
            categ_attr_groups = [product.categ_id.attribute_group_id.id] if product.categ_id.attribute_group_id else []
            attribute_group_ids =list(set(product_attr_groups + categ_attr_groups))

            res[product.id] = attribute_group_ids
        return res

    def _set_attr_grp_ids(self, cr, uid, ids, field_names, value, arg=None, context=None):
        self.pool.get('product.product').write(cr, uid, ids, {"attribute_group_ids": value})
        return True

    _columns = {
        'attribute_group_ids': fields.many2many('attribute.group', 'product_attr_grp_rel', 'product_id', 'grp_id', 'Attribute Groups'),
        'all_attribute_group_ids': fields.function(_get_attr_grp_ids, fnct_inv=_set_attr_grp_ids,
            type='many2many', relation='attribute.group', string='Attribute Groups'),
    }

    def onchange_categ_id(self, cr, uid, ids, categ_id):
        if categ_id:
            categ = self.pool.get('product.category').browse(cr,uid, categ_id)
            attr_group_ids = [categ.attribute_group_id.id] if categ.attribute_group_id else []
            return {'value': {'all_attribute_group_ids': attr_group_ids}}
        return False

    def _fix_size_bug(self, cr, uid, result, context=None):
    #When created a field text dynamicaly, its size is limited to 64 in the view.
    #The bug is fixed but not merged
    #https://code.launchpad.net/~openerp-dev/openerp-web/6.1-opw-579462-cpa/+merge/128003
    #TO remove when the fix will be merged
        for field in result['fields']:
            if result['fields'][field]['type'] == 'text':
                if 'size' in result['fields'][field]: del result['fields'][field]['size']
        return result

    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        if context is None:
            context = {}
        result = super(product_product, self).fields_view_get(cr, uid, view_id,view_type,context,toolbar=toolbar, submenu=submenu)
        if view_type == 'form':
            eview = etree.fromstring(result['arch'])
            attribute_group_ids = self.pool.get('attribute.group').search(cr, uid, [])
            attributes_notebook, toupdate_fields = self.pool.get('attribute.attribute')._build_attributes_notebook(cr, uid, attribute_group_ids, context=context)
            result['fields'].update(self.fields_get(cr, uid, toupdate_fields, context))

            for i in range(len(attributes_notebook)):
                attributes_notebook[i].set('modifiers', json.dumps({"invisible":[("all_attribute_group_ids","not contains",attribute_group_ids[i])]}))

            attr_page = eview.xpath("//page[@class='custom_attributes']" )[0]
            attr_page.append(attributes_notebook)

            result['arch'] = etree.tostring(eview, pretty_print=True)
            result = self._fix_size_bug(cr, uid, result, context=context)
        return result

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
