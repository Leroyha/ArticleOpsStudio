from __future__ import annotations

from dataclasses import dataclass
from datetime import time
import random
from typing import Sequence


MINUTES_PER_DAY = 24 * 60


@dataclass(frozen=True, slots=True)
class ScheduleItem:
    index: int
    time_text: str
    product_name: str


def time_to_minutes(value: time) -> int:
    return value.hour * 60 + value.minute


def parse_time_text(value: str) -> int:
    try:
        hour_text, minute_text = value.strip().replace("：", ":").split(":", maxsplit=1)
        hour = int(hour_text)
        minute = int(minute_text)
    except ValueError as exc:
        raise ValueError(f"时间格式不正确：{value}") from exc

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(f"时间超出范围：{value}")
    return hour * 60 + minute


def minutes_to_time(minutes: int) -> str:
    if not 0 <= minutes < MINUTES_PER_DAY:
        raise ValueError("生成的时间超出了当天范围。")
    hour, minute = divmod(minutes, 60)
    return f"{hour:02d}:{minute:02d}"


def _random_composition(total: int, parts: int, rng: random.Random) -> list[int]:
    if total < 0:
        raise ValueError("剩余可分配时间不能为负数。")
    if parts <= 0:
        raise ValueError("分段数量必须大于 0。")
    if parts == 1:
        return [total]

    dividers = sorted(rng.sample(range(total + parts - 1), parts - 1))
    result: list[int] = []
    previous = -1
    for divider in dividers:
        result.append(divider - previous - 1)
        previous = divider
    result.append(total + parts - 2 - previous)
    return result


def generate_random_times(
    start_time: time,
    end_time: time,
    task_count: int,
    min_interval: int,
    rng: random.Random | None = None,
) -> list[str]:
    start_minute = time_to_minutes(start_time)
    end_minute = time_to_minutes(end_time)

    if start_minute >= end_minute:
        raise ValueError("开始时间必须早于结束时间。")
    if task_count <= 0:
        raise ValueError("定时任务数量必须大于 0。")
    if min_interval <= 0:
        raise ValueError("最小间隔必须大于 0。")

    total_span = end_minute - start_minute
    min_required = (task_count - 1) * min_interval
    if min_required > total_span:
        raise ValueError(f"{task_count} 个任务至少需要 {min_required} 分钟，当前时间范围不足。")

    random_source = rng or random.Random()
    slack = total_span - min_required
    padding = _random_composition(slack, task_count + 1, random_source)

    current = start_minute + padding[0]
    times = [minutes_to_time(current)]

    for index in range(1, task_count):
        current += min_interval + padding[index]
        times.append(minutes_to_time(current))

    return times


def validate_manual_times(times: Sequence[str], task_count: int, min_interval: int) -> list[str]:
    if len(times) != task_count:
        raise ValueError(f"手动时间数量不一致：需要 {task_count} 个，实际提供 {len(times)} 个。")
    if min_interval <= 0:
        raise ValueError("最小间隔必须大于 0。")

    minute_values = [parse_time_text(value) for value in times]
    for previous, current in zip(minute_values, minute_values[1:], strict=False):
        if current <= previous:
            raise ValueError("手动时间必须按从早到晚递增。")
        if current - previous < min_interval:
            raise ValueError(f"手动时间间隔不能小于 {min_interval} 分钟。")
    return [minutes_to_time(value) for value in minute_values]


def build_schedule_items(
    start_time: time,
    end_time: time,
    task_count: int,
    min_interval: int,
    products: Sequence[str],
    manual_times: Sequence[str] | None = None,
    rng: random.Random | None = None,
) -> list[ScheduleItem]:
    if len(products) < task_count:
        raise ValueError(f"产品数量不足：需要 {task_count} 个，实际提供 {len(products)} 个。")

    cleaned_products = [product.strip() for product in products[:task_count]]
    if any(not product for product in cleaned_products):
        raise ValueError("产品名称不能为空。")

    if manual_times:
        times = validate_manual_times(manual_times, task_count=task_count, min_interval=min_interval)
    else:
        times = generate_random_times(
            start_time=start_time,
            end_time=end_time,
            task_count=task_count,
            min_interval=min_interval,
            rng=rng,
        )

    return [
        ScheduleItem(index=index, time_text=time_text, product_name=product_name)
        for index, (time_text, product_name) in enumerate(
            zip(times, cleaned_products, strict=True),
            start=1,
        )
    ]
