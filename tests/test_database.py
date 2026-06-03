from datetime import time

from articleops_studio.database import connect, init_database, list_product_stats, save_schedule_batch
from articleops_studio.scheduler import build_schedule_items
from articleops_studio.templates import render_schedule_text


def test_save_schedule_updates_product_usage(tmp_path) -> None:
    db_path = tmp_path / "articleops.sqlite"
    init_database(db_path)
    items = build_schedule_items(
        start_time=time(10, 0),
        end_time=time(11, 0),
        task_count=2,
        min_interval=10,
        products=["产品甲", "产品乙"],
    )

    batch_id = save_schedule_batch(
        items=items,
        start_time="10:00",
        end_time="11:00",
        interval_min=10,
        rendered_text=render_schedule_text(items),
        db_path=db_path,
    )

    stats = list_product_stats(db_path=db_path)
    assert batch_id > 0
    assert {row["product_name"]: row["usage_count"] for row in stats} == {"产品甲": 1, "产品乙": 1}
    with connect(db_path) as db:
        row = db.execute("SELECT template_locale FROM schedule_batches WHERE id = ?", (batch_id,)).fetchone()
        assert row["template_locale"] == "zh-CN"
