import logging

from src.balance_report_service import BalanceReportService
from src.dialog_history import DialogHistory
from src.extraction_result import ExtractionResult
from src.llm_client import LLMClient
from src.transaction_store import TransactionStore

logger = logging.getLogger(__name__)

FALLBACK_MESSAGE = "Извини, сейчас не могу ответить. Попробуй чуть позже."
UNSUPPORTED_INPUT_MESSAGE = (
    "Не удалось распознать транзакцию. Укажи сумму, тип операции и описание."
)


class ChatService:
    def __init__(
        self,
        llm_client: LLMClient,
        system_prompt: str = "",
        history: DialogHistory | None = None,
        transaction_store: TransactionStore | None = None,
        report_service: BalanceReportService | None = None,
    ) -> None:
        self._llm = llm_client
        self._system_prompt = system_prompt
        self._history = history
        self._transaction_store = transaction_store or TransactionStore()
        self._report_service = report_service or BalanceReportService()

    async def handle_text(self, user_id: int, user_text: str) -> str:
        past = self._history.get(user_id) if self._history else []
        try:
            result = await self._llm.extract_from_text(
                user_text,
                system_prompt=self._system_prompt,
                history=past,
            )
        except Exception:
            logger.exception("LLM request failed")
            return FALLBACK_MESSAGE

        answer = self._apply_result(user_id, result)
        if self._history:
            self._history.add(user_id, "user", user_text)
            self._history.add(user_id, "assistant", answer)
        return answer

    async def handle_image(self, user_id: int, image_bytes: bytes, caption: str = "") -> str:
        try:
            result = await self._llm.extract_from_image(
                image_bytes=image_bytes,
                caption=caption,
                system_prompt=self._system_prompt,
            )
        except ValueError:
            logger.exception("Image validation failed")
            return "Не удалось обработать изображение. Попробуй отправить чек меньшего размера."
        except Exception:
            logger.exception("VLM request failed")
            return FALLBACK_MESSAGE
        return self._apply_result(user_id, result)

    def _apply_result(self, user_id: int, result: ExtractionResult) -> str:
        if result.action == "transaction" and result.transaction:
            self._transaction_store.add(user_id, result.transaction)
            tx = result.transaction
            direction = "доход" if tx.direction == "income" else "расход"
            return (
                "Транзакция сохранена:\n"
                f"- Дата: {tx.occurred_at.strftime('%Y-%m-%d %H:%M')}\n"
                f"- Тип: {direction}\n"
                f"- Сумма: {tx.amount:.2f}\n"
                f"- Категория: {tx.category}\n"
                f"- Описание: {tx.description}"
            )

        if result.action == "report":
            period = result.period if result.period in {"day", "week", "month"} else "month"
            items = self._transaction_store.list_by_period(user_id, period=period)
            return self._report_service.build(period, items)

        return UNSUPPORTED_INPUT_MESSAGE
