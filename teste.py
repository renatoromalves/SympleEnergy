
import requests
from io import BytesIO
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.layout import LAParams
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup


class Teste():
    def __init__(self):
        self.URL = 'https://simpleenergy.com.br/teste/'
        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36'
        self.s = requests.Session()
        self.headers = {'user-agent': USER_AGENT}
        self._get_pag_inicial()

    def _get_pag_inicial(self):
        self.PAG_INICIAL = self.s.get(self.URL, headers=self.headers)

    def _get_pag_arquivos(self, cod_pag):
        soup = BeautifulSoup(self.PAG_INICIAL.content, features='lxml')
        csrf = self._get_csrf(soup)
        payload = {'csrf': csrf, 'codigo': cod_pag}
        pag_arq = self.s.post(self.URL, data=payload, headers=self.headers)
        return pag_arq

    def _get_page_links(self, content):
        soup = BeautifulSoup(content, features='lxml')
        return soup.findAll('a')

    def _get_csrf(self, soup):
        csrf = soup.find('input')['value']
        return csrf

    def _extract_pdf(self, link):
        pdf = self.s.get(self.URL+link, headers=self.headers).content
        with BytesIO(bytes(pdf)) as fp:
            rsrcmgr = PDFResourceManager()
            outfp = BytesIO()
            laparams = LAParams()
            device = TextConverter(rsrcmgr, outfp, laparams=laparams)
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            pages = list(PDFPage.get_pages(fp))
            for page in pages:
                interpreter.process_page(page)
            texto = str(outfp.getvalue(), 'utf-8').strip()
        return texto

    def _extract_txt(self, link):
        txt = self.s.get(self.URL+link, headers=self.headers)
        return txt.text

    def _convert_hex_to_int(self, value):
        return int(value, base=16)

    def _sort_dict(self, dict, by_value: bool):
        """by_value: if true, sorts by dict values
           if false sorts by keys"""
        return {k: v for k, v in sorted(dict.items(), key=lambda item: item[int(by_value)])}

    def extrair_dados(self, lista_codigos: list):
        docs_finais = dict()
        for codigo in lista_codigos:
            # desnecessário diante da não invalidação de token após o uso
            # self.get_pag_inicial()
            pag_arq = self._get_pag_arquivos(codigo).content
            links = self._get_page_links(pag_arq)
            for link in links:
                nome_arq = link['href']
                if nome_arq.endswith('.txt'):
                    inner_text = self._extract_txt(link['href'])
                elif nome_arq.endswith('.pdf'):
                    inner_text = self._extract_pdf(link['href'])
                docs_finais.update(
                    {nome_arq: self._convert_hex_to_int(inner_text)})

        # ordenação final:
        docs_finais = self._sort_dict(docs_finais, False)
        docs_finais = self._sort_dict(docs_finais, True)
        return docs_finais


def main():
  leitura_captura = Teste()
  lista_codigos = [321465, 98465]
  resultado = leitura_captura.extrair_dados(lista_codigos)
  return resultado

if __name__ == "__main__":
  print(main())
