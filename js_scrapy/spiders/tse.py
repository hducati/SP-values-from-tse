# -*- coding: utf-8 -*-
import scrapy
import json
from js_scrapy.items import JsScrapyItem
from scrapy.exceptions import CloseSpider


class TseSpider(scrapy.Spider):
    name = 'tse'
    allowed_hosts = ['inter04.tse.jus.br']
    start_urls = ['http://www.tse.jus.br/eleitor/estatisticas-de-eleitorado/consulta-quantitativo']

    def parse(self, response):
        self.min_row = 31

        iframe = response.css("#texto-conteudo div iframe::attr(src)").extract_first()
    
        yield scrapy.Request(iframe, callback=self.parse_contents)

    def parse_contents(self, response):
        self.page_instance = response.css("#pInstance::attr(value)").extract_first()
        self.page_id = response.css("#pPageSubmissionId::attr(value)").extract_first()
        
        page_protected = response.css("#pPageItemsProtected::attr(value)").extract_first()
        page_ck = response.css("input[data-for*=P0_LV_ABRANGENCIA]::attr(value)").extract_first()

        year = response.css("select.selectlist option::text").extract_first()
        month = response.css("#P0_SLS_MES_ELEQ option::attr(value)").extract_first()
        month = month.replace(month[0:4], year)

        form_data = {
            'p_flow_id': '2001',
            'p_flow_step_id': '109',
            'p_instance': str(self.page_instance),
            'p_page_submission_id': str(self.page_id),
            'p_request': 'P0_SLS_UF_MUN_ELEQ',
            'p_reload_on_submit': 'A',
            'p_json': json.dumps({'salt': str(self.page_id),
            'pageItems': {'itemsToSubmit': [{'n': 'P0_SLS_ANO_ELEQ', 'v': str(year)},
            {'n': 'P0_SLS_MES_ELEQ', 'v': str(month)},
            {'n': 'P0_SLS_ABRANGENCIA_ELEQ', 'v': 'M'},
            {'n': 'P0_SLS_UF_MUN_ELEQ', 'v': 'SP'},
            {'n': 'P0_LV_ABRANGENCIA', 'v': 'BRUMZ', 'ck': str(page_ck)}],
            'protected': str(page_protected), 'rowVersion': ''}})}

        yield scrapy.FormRequest(
                        url='http://inter04.tse.jus.br/ords/dwtse/wwv_flow.accept',
                        method='POST',
                        formdata=form_data,
                        callback=self.parse_results,
                    )

    def parse_results(self, response):
        values = response.css('tr.highlight-row td::text').extract()
        
        form_data = {
            'p_flow_id': '2001',
            'p_flow_step_id': '109',
            'p_instance': str(self.page_instance),
            'p_debug': '',
            'p_request': 'APXWGT',
            'p_widget_action': 'paginate',
            'p_pg_min_row': str(self.min_row),
            'p_pg_max_rows': '30',
            'p_pg_rows_fetched': '30',
            'x01': '31212748418837964',
            'p_widget_name': 'classic_report',
            'p_json': json.dumps({'salt': str(self.page_id)})
        }
        self.min_row += 30

        print(values)
        print('\n')

        if values:
            yield scrapy.FormRequest(
                        url='http://inter04.tse.jus.br/ords/dwtse/wwv_flow.ajax',
                        method='POST',
                        formdata=form_data,
                        callback=self.parse_results
                    )
        else:
            raise CloseSpider('No values available.')
