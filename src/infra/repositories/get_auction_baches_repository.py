import asyncio
import os
from typing import AsyncIterable

PYPPETEER_CHROMIUM_REVISION = '1263111'

os.environ['PYPPETEER_CHROMIUM_REVISION'] = PYPPETEER_CHROMIUM_REVISION

from pyppeteer import launch
from pyppeteer.page import Page

url = 'https://vitrinedejoias.caixa.gov.br/Paginas/Busca.aspx'

class ExtractorIterator:
    def __init__(self, extractor):
        self.extractor = extractor
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.extractor):
            result = self.extractor[self.index]
            self.index += 1
            return result
        raise StopIteration


async def search_auction_batches() -> AsyncIterable[dict[str, str]]:
    browser = await launch({ 'headless': True })
    page = await browser.newPage()
    await page.goto(url)

    select_vitrine = await page.querySelector('#buscaVitrine')
    await page.waitFor(1000)
    if select_vitrine is None:
        return
    
    await select_vitrine.click()
    await page.waitFor(1000)
    btn_passo_1 = await page.querySelector('#btnPasso1')
    await page.waitForSelector('#btnPasso1')
    if btn_passo_1 is None:
        return
    
    await page.evaluate('(element) => element.click()', btn_passo_1)
    await page.waitFor(1000)
    state_select = await page.querySelector('#uf')
    if state_select is None:
        return
    

    await page.waitFor(1000)
    options = await page.querySelectorAll('#uf option')
    await page.waitFor(1000)
    size = len(options)
    
    for i in range(1, size):
        state_name = await page.evaluate(f'(element) => element.textContent', options[i])
        await page.evaluate(f'(element) => element.selectedIndex = {i}', state_select)
        await page.waitFor(1000)
        await page.evaluate('(element) => element.dispatchEvent(new Event("change"))', state_select)
        await page.waitFor(1000)
        
        select_city = await page.querySelector('#cidadeVitrine')
        await page.waitFor(1000)
        if select_city is None:
            return
        
        city_options = await page.querySelectorAll('#cidadeVitrine option')
        await page.waitFor(1000)
        city_size = len(city_options)
        for j in range(1, city_size):
            city_name = await page.evaluate(f'(element) => element.textContent', city_options[j])
            if (j > 1):
                btn_alter_step_2 = await page.querySelector('#passo2 .validado a')
                await page.waitForSelector('#passo2 .validado a')

                if btn_alter_step_2 is None:
                    continue
                await page.evaluate('(element) => element.click()', btn_alter_step_2)
                await page.waitFor(1000)
            await page.evaluate(f'(element) => element.selectedIndex = {j}', select_city)
            await page.waitFor(1000)
            await page.evaluate('(element) => element.dispatchEvent(new Event("change"))', select_city)
            
            period_select = await page.querySelector('#periodoBusca')
            await page.waitFor(1000)
            if period_select is None:
                return
            
            period_options = await page.querySelectorAll('#periodoBusca option')
            await page.waitFor(1000)
            period_size = len(period_options)
            for k in range(1, period_size):
                period_range = await page.evaluate(f'(element) => element.textContent', period_options[k])
                await page.evaluate(f'(element) => element.selectedIndex = {k}', period_select)
                await page.waitFor(1000)
                await page.evaluate('(element) => element.dispatchEvent(new Event("change"))', period_select)
                
                btn_search = await page.querySelector("#passo2Vitrine")
                await page.waitForSelector("#passo2Vitrine")
                if btn_search is None:
                    return
                await page.evaluate('(element) => element.click()', btn_search)
                await page.waitFor(1000)
                
                # Pegar a paginação
                pages = await page.querySelectorAll('#resultadoVitrine #paginacao a:not([id])')
                await page.waitFor(1000)
                if len(pages) == 0:
                    continue
                for l in range(1, len(pages)):
                    await page.evaluate(f'(element) => element.click()', pages[l])
                    await page.waitFor(1000)
                    items = await page.querySelectorAll('#resultadoVitrine2 .resultado-busca-preco span')
                    await page.waitFor(1000)
                    if len(items) == 0:
                        continue

                    for i in range(1, len(items)):
                        await page.evaluate(f'(element) => element.click()', items[i])
                        await page.waitFor(1000)
                        jewelry = await extract_data_from_modal(page)
                        close_btn = await page.querySelector('#modalResultadoDetalhe .close span')
                        if close_btn is None:
                            continue
                        await page.evaluate('(element) => element.click()', close_btn)
                        
                        jewelry['state'] = state_name
                        jewelry['city'] = city_name
                        jewelry['period_range'] = period_range
                        yield jewelry
                        

    await browser.close()

async def extract_data_from_modal(page: Page):
    fields = await page.querySelectorAll('#modalResultadoDetalhe .modal-resultado-busca-campos span')
    await page.waitFor(1000)
    description = await page.evaluate('(element) => element.textContent', fields[0])
    batch_number = await page.evaluate('(element) => element.textContent', fields[1])
    contract_number = await page.evaluate('(element) => element.textContent', fields[2])
    centralizer = await page.evaluate('(element) => element.textContent', fields[3])
    bid_date = await page.evaluate('(element) => element.textContent', fields[4])
    result_date = await page.evaluate('(element) => element.textContent', fields[5])
    pick_up_location = await page.evaluate('(element) => element.textContent', fields[6])
    valueSelector = await page.querySelector('#modalResultadoDetalhe #modalResultadoValorLance span')
    await page.waitForSelector('#modalResultadoDetalhe #modalResultadoValorLance span')
    value = await page.evaluate('(element) => element.textContent', valueSelector)
    images: list[str] = []
    imgSelector = await page.querySelector('#modalResultadoDetalhe .resultado-busca-thumbnail img')
    await page.waitForSelector('#modalResultadoDetalhe .resultado-busca-thumbnail img')
    images.append(await page.evaluate('(element) => element.src', imgSelector))
    
    thumbnailsSelector = await page.querySelectorAll('#modalResultadoDetalhe .resultado-busca-miniaturas div img')
    await page.waitForSelector('#modalResultadoDetalhe .resultado-busca-miniaturas div img')
    thumbnailsUrl1 = await page.evaluate('(element) => element.src', thumbnailsSelector[0])
    thumbnailsUrl2 = await page.evaluate('(element) => element.src', thumbnailsSelector[1])
    images.extend([thumbnailsUrl1, thumbnailsUrl2])
    
    return {
        'description': description,
        'batch_number': batch_number,
        'contract_number': contract_number,
        'centralizer': centralizer,
        'bid_date': bid_date,
        'result_date': result_date,
        'pick_up_location': pick_up_location,
        'value': value,
        'images': images
    
    }


