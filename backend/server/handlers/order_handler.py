import math
from io import BytesIO

from starlette.responses import StreamingResponse

from backend.cost_reporter.calculators.exeptions.item_size_exception import ItemSizeException
from backend.cost_reporter.calculators.sheet_calculator.item_placement_calculator.placement_optimizer import \
    PlacementOptimizer
from backend.cost_reporter.cost_reporter_factory import CostReporterFactory
from backend.instruction_maker.instruction_builder_factory import InstructionBuilderFactory
from backend.instruction_maker.instruction_model import InstructionModel
from backend.models import Status
from backend.models.order import Order
from backend.server.handlers.entity_handler import EntityHandler
from backend.server.models.change_payload import ChangePayload
from backend.server.models.order_payload import OrderPayload
from backend.storage.access_services.accessor_factory import AccessorFactory


class OrderHandler(EntityHandler):
    MODEL = Order

    def __init__(self):
        super().__init__(AccessorFactory.get_order_crud_accessor())

    async def delay(self, order_payload: OrderPayload):
        """
        Сохраняет заказ со статусом 'отложено'
        """
        factory = CostReporterFactory(
            edition_data=order_payload.edition,
            production_data=order_payload.production,
        )
        reporter = factory.create_reporter()
        cost_report = reporter.get_report()

        order = Order(
            status=Status(1),
            comment=order_payload.comment,
            cost_report=cost_report,
            edition=order_payload.edition,
            markup=order_payload.production.markup,
            paper_cost=order_payload.production.paper_cost
        )
        await self._service.add_models([order])

    async def accept(self, order_payload: OrderPayload) -> StreamingResponse:
        """
        Сохраняет заказ сос статусом 'в работе'

        :return инструкция для работника производства
        """
        # TODO добавить промежуточный слой в котором создаются
        #  репорты, ордеры, и инструкции, чтобы вынести логику создания
        #  из хэндлера и оставить только оркестровку
        factory = CostReporterFactory(
            edition_data=order_payload.edition,
            production_data=order_payload.production,
        )
        reporter = factory.create_reporter()
        cost_report = reporter.get_report()

        order = Order(
            status=Status(2),
            comment=order_payload.comment,
            cost_report=cost_report,
            edition=order_payload.edition,
            markup=order_payload.production.markup,
            paper_cost=order_payload.production.paper_cost
        )
        order = (await self._service.add_models([order]))[0]

        product_per_sheet = PlacementOptimizer(
            press_sheet=order_payload.production.press_sheet,
            list_size=order_payload.edition.list_size
        ).get_best_solution().get_items_count()

        try:
            sheet_count = order_payload.edition.count / product_per_sheet
        except ZeroDivisionError:
            raise ItemSizeException()
        sheet_count = math.ceil(sheet_count)

        instruction_model = InstructionModel(
            order_id=order.id,
            comment=order_payload.comment,
            density=order_payload.edition.density,
            press_sheet=order_payload.production.press_sheet,
            chroma=order_payload.edition.chroma,
            lamination=order_payload.edition.lamination,
            die_cutting=order_payload.edition.die_cutting,
            sheet_count=sheet_count,
            fitting_count=order_payload.production.sheet_by_fitting,
            edition_count=order_payload.edition.count,
            list_size=order_payload.edition.list_size,
            product_per_sheet=product_per_sheet
        )
        factory = InstructionBuilderFactory(instruction_model=instruction_model)

        builder = factory.make_instruction_builder()
        pdf_bytes = builder.build_pdf()
        return StreamingResponse(
            BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=instruction.pdf"}
        )

    async def change(self, change_payload: ChangePayload):
        order: Order = await self._service.get_model_by_id(change_payload.order_id)
        order.status = change_payload.new_status
        await self._service.update_models([order])

    async def get_all(self) -> list[MODEL]:
        return await super().get_all()

    async def get(self, id: int) -> MODEL:
        return await super().get(id)

    async def create(self, data: MODEL) -> MODEL:
        return await super().create(data)

    async def create_bulk(self, data: list[MODEL]) -> list[MODEL]:
        return await super().create_bulk(data)

    async def update(self, id: int, data: MODEL) -> MODEL:
        return await super().update(id, data)

    async def update_bulk(self, data: list[MODEL]) -> list[MODEL]:
        return await super().update_bulk(data)

    async def delete(self, id: int) -> dict:
        return await super().delete(id)
