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

class attribute_group(osv.osv):
    _inherit= "attribute.group"

    def _get_default_model(self, cr, uid, context=None):
        if context is None:
            context = {}
        if context.get('force_model', None):
            model_id = self.pool['ir.model'].search(cr, uid, [['model', '=', context['force_model']]], context=context)
        else:
            model_id = self.pool['ir.model'].search(cr, uid, [['model', '=', 'product.product']], context=context)

        if model_id:
            return model_id[0]
        else:
            return None

    _defaults = {
        'model_id': _get_default_model
    }

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
