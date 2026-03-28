import logging
from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from bot.states.contract import ContractCreateStates

router = Router()
logger = logging.getLogger(__name__)

@router.message(F.text == "📄 Договор ИИ")
async def start_contract_creation(message: types.Message, state: FSMContext):
    await state.set_state(ContractCreateStates.waiting_for_lessor)
    await message.answer(
        "📝 <b>Генерация AI-Договора Аренды</b>\n\n"
        "Для составления юридически грамотного договора нужно ответить на 6 вопросов.\n\n"
        "<b>Шаг 1/6:</b> Введите ФИО Арендодателя (кто сдает оборудование):",
        parse_mode="HTML"
    )

@router.message(ContractCreateStates.waiting_for_lessor, F.text)
async def process_lessor(message: types.Message, state: FSMContext):
    await state.update_data(lessor_name=message.text)
    await state.set_state(ContractCreateStates.waiting_for_lessee)
    await message.answer("<b>Шаг 2/6:</b> Введите ФИО Арендатора (кто берет в аренду):", parse_mode="HTML")

@router.message(ContractCreateStates.waiting_for_lessee, F.text)
async def process_lessee(message: types.Message, state: FSMContext):
    await state.update_data(lessee_name=message.text)
    await state.set_state(ContractCreateStates.waiting_for_item)
    await message.answer("<b>Шаг 3/6:</b> Опишите предмет аренды (Например: Квадрокоптер DJI Mavic 3 Cine, серийный номер XXXXXX):", parse_mode="HTML")

@router.message(ContractCreateStates.waiting_for_item, F.text)
async def process_item(message: types.Message, state: FSMContext):
    await state.update_data(item_name=message.text)
    await state.set_state(ContractCreateStates.waiting_for_price)
    await message.answer("<b>Шаг 4/6:</b> Укажите стоимость аренды (Например: 5000 рублей за сутки):", parse_mode="HTML")

@router.message(ContractCreateStates.waiting_for_price, F.text)
async def process_price(message: types.Message, state: FSMContext):
    await state.update_data(price=message.text)
    await state.set_state(ContractCreateStates.waiting_for_deposit)
    await message.answer("<b>Шаг 5/6:</b> Укажите сумму или предмет залога (Например: Паспорт РФ и 15000 рублей):", parse_mode="HTML")

@router.message(ContractCreateStates.waiting_for_deposit, F.text)
async def process_deposit(message: types.Message, state: FSMContext):
    await state.update_data(deposit=message.text)
    await state.set_state(ContractCreateStates.waiting_for_dates)
    await message.answer("<b>Шаг 6/6:</b> Укажите конкретные даты аренды (Например: с 10.05.2026 по 15.05.2026):", parse_mode="HTML")

@router.message(ContractCreateStates.waiting_for_dates, F.text)
async def process_dates(message: types.Message, state: FSMContext):
    await state.update_data(dates=message.text)
    
    # Generate Invoice
    from aiogram.types import LabeledPrice
    price_stars = 100 # 100 Telegram Stars
    prices = [LabeledPrice(label="Генерация Договора (ИИ)", amount=price_stars)]
    
    await message.answer_invoice(
        title="Договор аренды (ИИ-Генерация)",
        description=f"Стоимость создания юридического документа: {price_stars} ⭐️.\nПосле оплаты вы гарантированно получите готовый .docx файл.",
        payload=f"generate_contract_{message.from_user.id}",
        currency="XTR",
        prices=prices,
        provider_token="" # empty for Telegram Stars
    )
    # We leave the state as is, so data is preserved for successful_payment

@router.pre_checkout_query(lambda query: query.invoice_payload.startswith("generate_contract_"))
async def process_contract_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@router.message(F.successful_payment, lambda message: message.successful_payment.invoice_payload.startswith("generate_contract_"))
async def process_contract_successful_payment(message: types.Message, state: FSMContext):
    data = await state.get_data()
    # FSM state data is retrieved
    lessor_name = data.get("lessor_name", "Не указан")
    lessee_name = data.get("lessee_name", "Не указан")
    item_name = data.get("item_name", "Не указан")
    price = data.get("price", "Не указана")
    deposit = data.get("deposit", "Не указан")
    dates = data.get("dates", "Не указаны")
    
    wait_msg = await message.answer("⏳ <i>ИИ юрист составляет ваш договор. Это займет около 10-15 секунд...</i>", parse_mode="HTML")
    
    from bot.services.contract_generator import generate_docx_contract
    file_buffer = await generate_docx_contract(lessor_name, lessee_name, item_name, price, deposit, dates)
    
    # Send document
    from aiogram.types import BufferedInputFile
    doc = BufferedInputFile(file_buffer.read(), filename="Contract_RentBot.docx")
    
    await wait_msg.delete()
    await message.answer_document(
        document=doc,
        caption="✅ <b>Ваш договор готов!</b>\nПожалуйста, ознакомьтесь с ним и подпишите при передаче оборудования.",
        parse_mode="HTML"
    )
    await state.clear()
