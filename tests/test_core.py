from datetime import time
import random

import pytest

from articleops_studio.scheduler import build_schedule_items, generate_random_times
from articleops_studio.templates import current_template_hash, render_schedule_text


FORBIDDEN_SITE_TOKEN = "chem" + "17"


def to_minutes(value: str) -> int:
    hour, minute = map(int, value.split(":"))
    return hour * 60 + minute


def test_generate_random_times_respects_min_interval() -> None:
    times = generate_random_times(
        start_time=time(10, 0),
        end_time=time(11, 30),
        task_count=5,
        min_interval=15,
        rng=random.Random(7),
    )

    assert len(times) == 5
    deltas = [
        to_minutes(next_time) - to_minutes(current_time)
        for current_time, next_time in zip(times, times[1:])
    ]
    assert min(deltas) >= 15


def test_build_schedule_items_requires_enough_products() -> None:
    with pytest.raises(ValueError, match="产品数量不足"):
        build_schedule_items(
            start_time=time(10, 0),
            end_time=time(11, 0),
            task_count=3,
            min_interval=10,
            products=["A", "B"],
        )


def test_render_schedule_text_contains_all_items() -> None:
    items = build_schedule_items(
        start_time=time(10, 0),
        end_time=time(10, 40),
        task_count=2,
        min_interval=10,
        products=["产品甲", "产品乙"],
        rng=random.Random(1),
    )

    result = render_schedule_text(items)

    assert "帮我设置通用定时发文任务" in result
    assert "任务：发布一篇文章" in result
    assert FORBIDDEN_SITE_TOKEN not in result.lower()
    assert "产品：产品甲" in result
    assert "产品：产品乙" in result


def test_render_schedule_text_uses_locale() -> None:
    items = build_schedule_items(
        start_time=time(10, 0),
        end_time=time(10, 40),
        task_count=1,
        min_interval=10,
        products=["产品甲"],
        rng=random.Random(1),
    )

    result = render_schedule_text(items, locale="en-US")

    assert "Please set up scheduled article publishing tasks" in result
    assert "Task: Publish one article" in result
    assert FORBIDDEN_SITE_TOKEN not in result.lower()
    assert "Product: 产品甲" in result
    assert current_template_hash("en-US") != current_template_hash("zh-CN")


def test_manual_times_are_used_and_validated() -> None:
    items = build_schedule_items(
        start_time=time(10, 0),
        end_time=time(12, 0),
        task_count=2,
        min_interval=10,
        products=["A", "B"],
        manual_times=["10:30", "10:45"],
    )

    assert [item.time_text for item in items] == ["10:30", "10:45"]


def test_manual_times_reject_short_interval() -> None:
    with pytest.raises(ValueError, match="手动时间间隔不能小于"):
        build_schedule_items(
            start_time=time(10, 0),
            end_time=time(12, 0),
            task_count=2,
            min_interval=20,
            products=["A", "B"],
            manual_times=["10:30", "10:45"],
        )
