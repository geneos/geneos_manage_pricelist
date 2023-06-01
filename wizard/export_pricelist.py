# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from io import StringIO, BytesIO
import base64
import csv
import codecs


class AccountingWriter(object):

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", delimiter=";", **kwds):
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, delimiter=delimiter, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        row = (x or '' for x in row)
        self.writer.writerow(row)
        data = self.queue.getvalue()
        data = self.encoder.encode(data)
        self.stream.write(data)
        self.queue.truncate(0)
        self.queue.seek(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)
        self.queue.close()


class WizardExportPricelist(models.TransientModel):
    _name = "wizard.export.pricelist.csv"
    _description = "Wizard Export PriceList CSV"

    pricelist_id = fields.Many2one(comodel_name="product.pricelist", string="Lista de Precios", required=True)
    categ_ids = fields.Many2many(comodel_name="product.category", string="Categorias")
    data = fields.Binary('Archivo', readonly=True)
    export_filename = fields.Char(
        string='Export CSV Filename', size=128, default='listadeprecios.csv')

    def crear_archivo(self):
        lista_precios = self.pricelist_id
        categorias = self.categ_ids
        filtro = [
            ('pricelist_id', '=', lista_precios),
            ('sale_ok', '=', True),
            ('active', '=', True),
        ]

        if categorias:
            filtro.append((
                ("categ_id", "in", categorias.mapped('id'))
            ))

        productos = self.env['product.template'].search(filtro)
        pricelist_items = self.env['product.pricelist.item']
        items = pricelist_items.search(
            [
                ('product_tmpl_id', 'in', productos.mapped('id'))
            ]
        )

        if not items:
            raise UserError(_('No existen productos para exportar.'))

        datos_csv = []
        #creo la primera linea
        content = []
        content.append('ID')
        content.append('Codigo Barras')
        content.append('Codigo')
        content.append('Nombre')
        content.append('Importe')
        datos_csv.append(content)
        for item in items:
            content = []
            barcode = str(item.product_tmpl_id.barcode)
            default_code = str(item.product_tmpl_id.default_code)
            name = str(item.product_tmpl_id.name)

            content.append(str(item.id))
            content.append(barcode)
            content.append(default_code)
            content.append(name)
            importe_sin_impuestos = item.fixed_price
            importe = '%.2f' % (importe_sin_impuestos)
            importe = importe.replace('.',',')
            content.append(importe)
            datos_csv.append(content)

        file_data = BytesIO()
        try:
            writer = AccountingWriter(file_data)
            writer.writerows(datos_csv)
            file_value = file_data.getvalue()
            self.write({'data': base64.encodebytes(file_value)})
        finally:
            file_data.close()


        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.export.pricelist.csv',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
        
