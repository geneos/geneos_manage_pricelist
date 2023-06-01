# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from io import StringIO, BytesIO
import base64
import tempfile
import csv
from decimal import Decimal



class WizardImportPricelist(models.TransientModel):
    _name = "wizard.import.pricelist.csv"
    _description = "Wizard Import PriceList CSV"

    update_meli = fields.Boolean('Actualizar Precios en MELI')
    data = fields.Binary('Archivo', required=True)
    import_filename = fields.Char(
        string='Import CSV Filename', size=128, default='')



    def crear_archivo(self):
        total_success_import_record = 0
        total_failed_record = 0
        list_of_failed_record = ''
        datafile = self.data
        productos_importados = []
        try:
            file_path = tempfile.gettempdir() + '/import.csv'
            f = open(file_path, 'wb+')
            f.write(base64.decodebytes(datafile))
            f.close()

            archive = csv.DictReader(open(file_path), delimiter=";")
            archive_lines = [line for line in archive]
            count = 1
            for line in archive_lines:
                try:
                    count += 1
                    importe = Decimal((str(line.get('Importe')).replace(',','.')))
                    valores = {
                        'id': line.get('ID') or '',
                        'fixed_price': importe or ''
                    }
                    producto_item = self.env['product.pricelist.item'].search(
                        [
                            ('id', '=', line.get('ID', ''))
                        ], limit=1)
                    if producto_item:
                        producto_item.write(valores)
                        productos_importados.append(producto_item.product_id.id)
                    total_success_import_record += 1
                except:
                    total_failed_record += 1
                    list_of_failed_record += line
        except Exception as e:
            list_of_failed_record += str(e)

        #actualizo en ML el precio
        if self.update_meli:
            #company = self.env.user.company_id
            #apistate = self.env['meli.util'].get_new_instance(company)
            #company.cron_meli_process_post_price(meli=apistate)
            producto_item = self.env['product.product'].search(productos_importados)
            for item in producto_item:
                item.product_post_price()



        return {
            'type': 'ir.actions.act_window',
            'res_model': 'wizard.import.pricelist.csv',
            'view_mode': 'form',
            'res_id': self.id,
            'views': [(False, 'form')],
            'target': 'new',
        }
