from aiogram.fsm.state import State, StatesGroup

class EscrowState(StatesGroup):
    waiting_for_proof = State() # Пилот загружает доказательства (фото/отчет)
    waiting_for_approval = State() # Заказчик принимает или оспаривает работу
    waiting_for_dispute_reason = State() # Если оспаривает, нужно указать причину (жалобу)
