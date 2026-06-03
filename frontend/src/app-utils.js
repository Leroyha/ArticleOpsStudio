export function formatLabel(template, values = {}) {
  return String(template).replace(/\{(\w+)\}/g, (_, key) => values[key] ?? "");
}

export function readJson(key, fallback) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return fallback;
    const parsed = JSON.parse(raw);
    if (parsed.schema !== 1) return fallback;
    return parsed.data;
  } catch {
    return fallback;
  }
}

export function normalizeTime(value) {
  return value || "";
}

export function buildPayload(form, settings) {
  const products = form.products.map((item) => item.trim()).filter(Boolean);
  const manualTimes = form.manualTimes.map((item) => item.trim()).filter(Boolean);
  return {
    start_time: normalizeTime(form.startTime),
    end_time: normalizeTime(form.endTime),
    task_count: Number(form.taskCount),
    interval_min: Number(form.intervalMin),
    products,
    manual_times: manualTimes.length ? manualTimes : null,
    locale: settings.locale,
  };
}

export function statusTone(status) {
  if (/失败|錯誤|错误|阻断|不足|失效|异常|fail|error|échouée|non riuscita/i.test(status)) return "danger";
  if (/正在|生成中|產生中|loading|generating|génération|generazione|생성 중|生成中/i.test(status)) return "busy";
  if (/已生成|已保存|已儲存|已复制|複製|コピー|저장됨|복사|saved|generated|copied|générés|enregistré|copié|generati|salvato|copiato/i.test(status)) return "success";
  return "idle";
}

export function applyTheme(settings, settingsKey) {
  const root = document.documentElement;
  root.dataset.theme = settings.theme;
  root.dataset.accent = settings.accent;
  localStorage.setItem(settingsKey, JSON.stringify({ schema: 1, data: settings }));
}

export async function apiJson(url, options) {
  const response = await fetch(url, { cache: "no-store", ...options });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || "Request failed");
  return payload;
}
