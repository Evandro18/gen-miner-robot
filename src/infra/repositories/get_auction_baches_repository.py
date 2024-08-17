from datetime import datetime
from multiprocessing.sharedctypes import Value
from operator import is_
import re
from typing import AsyncIterable
from src.data.interceptor_state import InterceptorState
from src.infra.core.logging import Log
from src.domain.use_cases.entities.auction_entity import AuctionItemEntity
from playwright.async_api import async_playwright, Page


class AuctionBatchesExtractorRepository:
    async def __call__(
        self, page: Page, request_interceptor_state: InterceptorState
    ) -> AsyncIterable[AuctionItemEntity]:
        await page.wait_for_timeout(1000)
        select_vitrine = await page.query_selector("#buscaVitrine")
        await page.wait_for_selector("#buscaVitrine")
        if select_vitrine is None:
            raise ValueError("Select vitrine not found")

        await select_vitrine.click()
        btn_passo_1 = await page.query_selector("#btnPasso1")
        await page.wait_for_selector("#btnPasso1")
        if btn_passo_1 is None:
            raise ValueError("Button passo 1 not found")

        await page.evaluate("(element) => element.click()", btn_passo_1)
        state_select = await page.query_selector("#uf")
        await page.wait_for_selector("#uf")
        if state_select is None:
            raise ValueError("State select not found")

        uf_btn = await page.query_selector("#uf")
        if uf_btn is None:
            raise ValueError("UF button not found")

        await uf_btn.click()
        options = await page.query_selector_all("#uf option")
        size = len(options)

        for i in range(1, size):
            state_name = await page.evaluate(
                f"(element) => element.textContent", options[i]
            )
            await page.evaluate(
                f"(element) => element.selectedIndex = {i}", state_select
            )
            await page.evaluate(
                '(element) => element.dispatchEvent(new Event("change"))', state_select
            )

            loading = await page.query_selector("#loading")
            if loading is not None:
                await loading.wait_for_element_state("hidden")

            select_city = await page.query_selector("#cidadeVitrine")
            await page.wait_for_selector("#cidadeVitrine")
            if select_city is None:
                continue

            city_options = await page.query_selector_all("#cidadeVitrine option")
            city_size = len(city_options)
            for j in range(1, city_size):
                city_name = await page.evaluate(
                    f"(element) => element.textContent", city_options[j]
                )
                await page.evaluate(
                    f"(element) => element.selectedIndex = {j}", select_city
                )
                await page.evaluate(
                    '(element) => element.dispatchEvent(new Event("change"))',
                    select_city,
                )

                loading = await page.query_selector("#loading")
                if loading is not None:
                    await loading.wait_for_element_state("hidden")

                period_select = await page.query_selector("#periodoBusca")
                await page.wait_for_selector("#periodoBusca")
                if period_select is None:
                    continue

                period_options = await page.query_selector_all("#periodoBusca option")
                period_size = len(period_options)
                for k in range(1, period_size):
                    period_range = await page.evaluate(
                        f"(element) => element.textContent", period_options[k]
                    )
                    await page.evaluate(
                        f"(element) => element.selectedIndex = {k}", period_select
                    )
                    await page.evaluate(
                        '(element) => element.dispatchEvent(new Event("change"))',
                        period_select,
                    )

                    loading = await page.query_selector("#loading")
                    if loading is not None:
                        await loading.wait_for_element_state("hidden")

                    btn_search = await page.query_selector("#passo2Vitrine")
                    await page.wait_for_selector("#passo2Vitrine")
                    if btn_search is None:
                        continue

                    await page.evaluate("(element) => element.click()", btn_search)
                    loading = await page.query_selector("#loading")
                    if loading is not None:
                        await loading.wait_for_element_state("hidden")

                    # Pegar a paginação
                    pages = await page.query_selector_all(
                        "#resultadoVitrine #paginacao a:not([id])"
                    )

                    auction_item = AuctionItemEntity(
                        city=city_name, state=state_name, period=period_range
                    )

                    if len(pages) == 0:
                        yield auction_item
                        continue
                    for l in range(1, len(pages)):
                        await page.evaluate(f"(element) => element.click()", pages[l])
                        loading = await page.query_selector("#loading")
                        if loading is not None:
                            await loading.wait_for_element_state("hidden")

                        items = await page.query_selector_all(
                            "#resultadoVitrine2 .resultado-busca-preco span"
                        )
                        await page.wait_for_selector(
                            "#resultadoVitrine2 .resultado-busca-preco span"
                        )

                        if len(items) == 0:
                            yield auction_item
                            continue

                        for i in range(1, len(items)):
                            await page.evaluate(
                                f"(element) => element.click()", items[i]
                            )
                            jewelry = await extract_data_from_modal(
                                page, request_interceptor_state
                            )
                            close_btn = await page.query_selector(
                                "#modalResultadoDetalhe .close span"
                            )
                            if close_btn is None:
                                continue
                            await page.evaluate(
                                "(element) => element.click()", close_btn
                            )
                            value = 0.0
                            if "value" in jewelry:
                                str_value = re.sub(r"[^0-9\,]", "", jewelry["value"])
                                value = float(str_value.replace(",", "."))

                            del jewelry["value"]
                            yield AuctionItemEntity(
                                **jewelry,
                                min_bid_value=value,
                                state=auction_item.state,
                                city=auction_item.city,
                                period=auction_item.period,
                            )

                    should_continue = await change_options_step_two(page)
                    if should_continue:
                        continue

                should_continue = await change_options_step_two(page)
                if should_continue:
                    continue

            should_continue = await change_options_step_two(page)
            if should_continue:
                continue


async def change_options_step_two(page: Page) -> bool:
    step_two_btn_selector = "#passo2 ul span[class='validado'] a"
    step_two_btn = await page.query_selector(step_two_btn_selector)
    if step_two_btn is None:
        return False

    is_visible = await step_two_btn.is_visible()
    if not is_visible:
        return False

    await step_two_btn.click()
    await page.wait_for_load_state()
    return True


async def extract_data_from_modal(
    page: Page, request_interceptor_state: InterceptorState
):
    fields = await page.query_selector_all(
        "#modalResultadoDetalhe .modal-resultado-busca-campos span"
    )
    await page.wait_for_timeout(1000)
    description = await page.evaluate("(element) => element.textContent", fields[0])
    batch_number = await page.evaluate("(element) => element.textContent", fields[1])
    contract_number = await page.evaluate("(element) => element.textContent", fields[2])
    centralizer = await page.evaluate("(element) => element.textContent", fields[3])
    bid_date = await page.evaluate("(element) => element.textContent", fields[4])
    result_date = await page.evaluate("(element) => element.textContent", fields[5])
    pick_up_location = await page.evaluate(
        "(element) => element.textContent", fields[6]
    )
    valueSelector = await page.query_selector(
        "#modalResultadoDetalhe #modalResultadoValorLance span"
    )
    # await page.wait_for_selector('#modalResultadoDetalhe #modalResultadoValorLance span')
    value = await page.evaluate("(element) => element.textContent", valueSelector)
    images: list[str] = []

    try:
        img_selector = await page.query_selector(
            "#modalResultadoDetalhe .resultado-busca-thumbnail img"
        )
        images.append(await page.evaluate("(element) => element.src", img_selector))
        thumbnails_selector = await page.query_selector_all(
            "#modalResultadoDetalhe .resultado-busca-miniaturas div img"
        )
        thumbnailsUrl1 = await page.evaluate(
            "(element) => element.src", thumbnails_selector[0]
        )
        thumbnailsUrl2 = await page.evaluate(
            "(element) => element.src", thumbnails_selector[1]
        )
        images.extend([thumbnailsUrl1, thumbnailsUrl2])
    except Exception as e:
        Log.error(f"Error on extract thumbnails: {e}")
    selector_actions = "#modalResultadoDetalhe .action a"
    actions = await page.query_selector_all(selector_actions)
    await page.wait_for_selector(selector_actions)
    edital_action = actions[1]
    catalog_action = actions[2]

    await page.evaluate("(element) => element.click()", edital_action)
    url_edital_action = request_interceptor_state.get(key="url")
    await page.evaluate("(element) => element.click()", catalog_action)
    url_catalog_action = request_interceptor_state.get(key="url")
    docs = [url_edital_action, url_catalog_action]
    return {
        "description": description,
        "batch_number": batch_number,
        "contract_number": contract_number,
        "centralizer": centralizer,
        "bid_date": bid_date,
        "result_date": result_date,
        "pick_up_location": pick_up_location,
        "value": value,
        "images": images,
        "documents": [d for d in docs if d is not None],
    }
