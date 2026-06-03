import React, { useEffect, useMemo, useRef, useState } from "react";
import { createRoot } from "react-dom/client";
import { gsap } from "gsap";
import { apiJson, applyTheme, buildPayload, formatLabel, readJson, statusTone } from "./app-utils.js";
import "./styles.css";

const STORAGE_KEY = "articleops.form.v1";
const SETTINGS_KEY = "articleops.settings.v1";
const CONFIRM_TOKEN = "CONFIRM";

const LOCALES = [
  ["zh-CN", "简体中文"],
  ["zh-TW", "繁體中文"],
  ["ja-JP", "日本語"],
  ["ko-KR", "한국어"],
  ["en-US", "English"],
  ["fr-FR", "Français"],
  ["it-IT", "Italiano"],
];

const I18N = {
  "zh-CN": {
    dashboard: "任务模板工作台",
    control: "控制面板",
    back: "返回工作台",
    title: "生成通用定时发文指令",
    subtitle: "按实际产品条目生成 OpenClaw 模板，少于 5 篇也不自动补足。",
    planned: "计划篇数",
    filled: "已填产品",
    manual: "手动时间",
    generate: "生成模板",
    save: "保存批次",
    copy: "复制模板",
    params: "任务参数",
    timeline: "任务轨道",
    stats: "产品使用统计",
    result: "生成模板",
  },
  "zh-TW": {
    dashboard: "任務模板工作台",
    control: "控制面板",
    back: "返回工作台",
    title: "產生通用定時發文指令",
    subtitle: "按實際產品條目產生 OpenClaw 模板，少於 5 篇也不自動補足。",
    planned: "計畫篇數",
    filled: "已填產品",
    manual: "手動時間",
    generate: "產生模板",
    save: "儲存批次",
    copy: "複製模板",
    params: "任務參數",
    timeline: "任務軌道",
    stats: "產品使用統計",
    result: "產生模板",
  },
  "ja-JP": {
    dashboard: "タスクテンプレート",
    control: "コントロールパネル",
    back: "ワークベンチへ戻る",
    title: "汎用予約投稿指示を生成",
    subtitle: "実際の商品リストに基づいて OpenClaw テンプレートを生成します。",
    planned: "予定件数",
    filled: "入力済み商品",
    manual: "手動時刻",
    generate: "生成",
    save: "保存",
    copy: "コピー",
    params: "タスク設定",
    timeline: "タイムライン",
    stats: "商品統計",
    result: "生成結果",
  },
  "ko-KR": {
    dashboard: "작업 템플릿",
    control: "제어판",
    back: "작업대로 돌아가기",
    title: "범용 예약 게시 명령 생성",
    subtitle: "실제 제품 항목 기준으로 OpenClaw 템플릿을 생성합니다.",
    planned: "계획 수",
    filled: "입력 제품",
    manual: "수동 시간",
    generate: "생성",
    save: "저장",
    copy: "복사",
    params: "작업 설정",
    timeline: "작업 타임라인",
    stats: "제품 통계",
    result: "생성 결과",
  },
  "en-US": {
    dashboard: "Task Template Workbench",
    control: "Control Panel",
    back: "Back to Workbench",
    title: "Generate scheduled publishing prompts",
    subtitle: "Build an OpenClaw template from the actual product entries.",
    planned: "Planned",
    filled: "Products",
    manual: "Manual Times",
    generate: "Generate",
    save: "Save Batch",
    copy: "Copy",
    params: "Task Parameters",
    timeline: "Run Timeline",
    stats: "Product Usage",
    result: "Generated Prompt",
  },
  "fr-FR": {
    dashboard: "Atelier de modèles",
    control: "Panneau de contrôle",
    back: "Retour à l'atelier",
    title: "Générer les consignes de publication programmée",
    subtitle: "Créer un modèle OpenClaw depuis les produits réels.",
    planned: "Prévu",
    filled: "Produits",
    manual: "Horaires",
    generate: "Générer",
    save: "Enregistrer",
    copy: "Copier",
    params: "Paramètres",
    timeline: "Chronologie",
    stats: "Statistiques",
    result: "Invite générée",
  },
  "it-IT": {
    dashboard: "Banco modelli",
    control: "Pannello di controllo",
    back: "Torna al banco",
    title: "Genera prompt di pubblicazione programmata",
    subtitle: "Crea un modello OpenClaw dai prodotti reali.",
    planned: "Pianificati",
    filled: "Prodotti",
    manual: "Orari",
    generate: "Genera",
    save: "Salva",
    copy: "Copia",
    params: "Parametri",
    timeline: "Timeline",
    stats: "Statistiche",
    result: "Prompt generato",
  },
};

const EXTRA_I18N = {
  "zh-CN": {
    appTagline: "OpenClaw 通用定时任务工作台",
    statusIdle: "等待生成",
    statusLoading: "正在生成 OpenClaw 任务模板",
    statusGenerated: "已生成 {count} 篇任务模板",
    statusSaved: "已保存批次 #{id}",
    statusCopied: "模板已复制到剪贴板",
    requestFailed: "请求失败",
    emptyProduct: "待填写产品",
    batchSetup: "批次设置",
    panelDesc: "设置时间窗口、最小间隔和产品列表。",
    startTime: "开始时间",
    endTime: "结束时间",
    taskCount: "任务数量",
    minInterval: "最小间隔",
    productAndManual: "产品与手动时间",
    pasteHint: "粘贴多行产品名可自动展开",
    productName: "产品名称",
    timelineKicker: "执行时间线",
    timelineDesc: "每个时间点都是独立单篇任务。",
    productPrefix: "产品",
    statsKicker: "使用均衡",
    statsDesc: "保存批次后用于观察产品发文密度。",
    noStats: "暂无保存记录。",
    promptKicker: "OpenClaw 提示词",
    resultDesc: "生成后复制整段文本发送给 OpenClaw。",
    resultPlaceholder: "生成结果会显示在这里。",
    tabDatabase: "数据库",
    tabSettings: "软件设置",
    tabDocs: "文档",
    databaseOverview: "数据库概览",
    loading: "读取中...",
    searchTable: "搜索当前表",
    refresh: "刷新",
    protectedCrud: "增删改查",
    crudHint: "写操作会先备份 SQLite。确认令牌：CONFIRM",
    rowId: "记录 ID",
    rowIdPlaceholder: "更新/删除需要 ID",
    create: "新增",
    update: "更新",
    delete: "删除",
    operationDone: "操作完成，已自动备份数据库。",
    settingsDesc: "语言、主题和强调色保存在浏览器本地。",
    language: "语言",
    theme: "主题",
    color: "颜色",
    themeSystem: "跟随系统",
    themeLight: "正常浅色",
    themeDark: "深色",
    accentCyan: "青色",
    accentGreen: "绿色",
    accentViolet: "紫色",
    accentAmber: "琥珀色",
    docsEmpty: "暂无文档。",
  },
  "zh-TW": {
    appTagline: "OpenClaw 通用定時任務工作台",
    statusIdle: "等待產生",
    statusLoading: "正在產生 OpenClaw 任務模板",
    statusGenerated: "已產生 {count} 篇任務模板",
    statusSaved: "已儲存批次 #{id}",
    statusCopied: "模板已複製到剪貼簿",
    requestFailed: "請求失敗",
    emptyProduct: "待填寫產品",
    batchSetup: "批次設定",
    panelDesc: "設定時間視窗、最小間隔和產品列表。",
    startTime: "開始時間",
    endTime: "結束時間",
    taskCount: "任務數量",
    minInterval: "最小間隔",
    productAndManual: "產品與手動時間",
    pasteHint: "貼上多行產品名可自動展開",
    productName: "產品名稱",
    timelineKicker: "執行時間線",
    timelineDesc: "每個時間點都是獨立單篇任務。",
    productPrefix: "產品",
    statsKicker: "使用均衡",
    statsDesc: "儲存批次後用於觀察產品發文密度。",
    noStats: "暫無儲存記錄。",
    promptKicker: "OpenClaw 提示詞",
    resultDesc: "產生後複製整段文字發送給 OpenClaw。",
    resultPlaceholder: "產生結果會顯示在這裡。",
    tabDatabase: "資料庫",
    tabSettings: "軟體設定",
    tabDocs: "文件",
    databaseOverview: "資料庫概覽",
    loading: "讀取中...",
    searchTable: "搜尋目前表",
    refresh: "重新整理",
    protectedCrud: "增刪改查",
    crudHint: "寫操作會先備份 SQLite。確認令牌：CONFIRM",
    rowId: "記錄 ID",
    rowIdPlaceholder: "更新/刪除需要 ID",
    create: "新增",
    update: "更新",
    delete: "刪除",
    operationDone: "操作完成，已自動備份資料庫。",
    settingsDesc: "語言、主題和強調色保存在瀏覽器本地。",
    language: "語言",
    theme: "主題",
    color: "顏色",
    themeSystem: "跟隨系統",
    themeLight: "正常淺色",
    themeDark: "深色",
    accentCyan: "青色",
    accentGreen: "綠色",
    accentViolet: "紫色",
    accentAmber: "琥珀色",
    docsEmpty: "暫無文件。",
  },
  "ja-JP": {
    appTagline: "OpenClaw 汎用予約タスク作業台",
    statusIdle: "生成待ち",
    statusLoading: "OpenClaw タスクテンプレートを生成中",
    statusGenerated: "{count} 件のテンプレートを生成しました",
    statusSaved: "バッチ #{id} を保存しました",
    statusCopied: "テンプレートをクリップボードへコピーしました",
    requestFailed: "リクエストに失敗しました",
    emptyProduct: "商品未入力",
    batchSetup: "バッチ設定",
    panelDesc: "時間範囲、最小間隔、商品リストを設定します。",
    startTime: "開始時刻",
    endTime: "終了時刻",
    taskCount: "タスク数",
    minInterval: "最小間隔",
    productAndManual: "商品と手動時刻",
    pasteHint: "複数行の商品名を貼り付けると自動展開します",
    productName: "商品名",
    timelineKicker: "実行タイムライン",
    timelineDesc: "各時刻は独立した単一記事タスクです。",
    productPrefix: "商品",
    statsKicker: "利用バランス",
    statsDesc: "保存後、商品の投稿計画密度を確認します。",
    noStats: "保存記録はありません。",
    promptKicker: "OpenClaw プロンプト",
    resultDesc: "生成後、全文をコピーして OpenClaw に送信します。",
    resultPlaceholder: "生成結果はここに表示されます。",
    tabDatabase: "データベース",
    tabSettings: "設定",
    tabDocs: "ドキュメント",
    databaseOverview: "データベース概要",
    loading: "読み込み中...",
    searchTable: "現在の表を検索",
    refresh: "更新",
    protectedCrud: "保護付き CRUD",
    crudHint: "書き込み前に SQLite をバックアップします。確認トークン：CONFIRM",
    rowId: "レコード ID",
    rowIdPlaceholder: "更新/削除には ID が必要です",
    create: "追加",
    update: "更新",
    delete: "削除",
    operationDone: "操作完了。データベースを自動バックアップしました。",
    settingsDesc: "言語、テーマ、アクセント色はブラウザに保存されます。",
    language: "言語",
    theme: "テーマ",
    color: "色",
    themeSystem: "システムに従う",
    themeLight: "ライト",
    themeDark: "ダーク",
    accentCyan: "シアン",
    accentGreen: "グリーン",
    accentViolet: "バイオレット",
    accentAmber: "アンバー",
    docsEmpty: "ドキュメントはありません。",
  },
  "ko-KR": {
    appTagline: "OpenClaw 범용 예약 작업대",
    statusIdle: "생성 대기",
    statusLoading: "OpenClaw 작업 템플릿 생성 중",
    statusGenerated: "템플릿 {count}개 생성됨",
    statusSaved: "배치 #{id} 저장됨",
    statusCopied: "템플릿을 클립보드에 복사했습니다",
    requestFailed: "요청 실패",
    emptyProduct: "제품 미입력",
    batchSetup: "배치 설정",
    panelDesc: "시간 범위, 최소 간격, 제품 목록을 설정합니다.",
    startTime: "시작 시간",
    endTime: "종료 시간",
    taskCount: "작업 수",
    minInterval: "최소 간격",
    productAndManual: "제품 및 수동 시간",
    pasteHint: "여러 줄 제품명을 붙여 넣으면 자동 확장됩니다",
    productName: "제품명",
    timelineKicker: "실행 타임라인",
    timelineDesc: "각 시간점은 독립 단일 글 작업입니다.",
    productPrefix: "제품",
    statsKicker: "사용 균형",
    statsDesc: "저장 후 제품 게시 계획 밀도를 확인합니다.",
    noStats: "저장 기록이 없습니다.",
    promptKicker: "OpenClaw 프롬프트",
    resultDesc: "생성 후 전체 텍스트를 복사해 OpenClaw 에 보냅니다.",
    resultPlaceholder: "생성 결과가 여기에 표시됩니다.",
    tabDatabase: "데이터베이스",
    tabSettings: "설정",
    tabDocs: "문서",
    databaseOverview: "데이터베이스 개요",
    loading: "읽는 중...",
    searchTable: "현재 표 검색",
    refresh: "새로고침",
    protectedCrud: "보호된 CRUD",
    crudHint: "쓰기 전에 SQLite 를 백업합니다. 확인 토큰: CONFIRM",
    rowId: "레코드 ID",
    rowIdPlaceholder: "업데이트/삭제에는 ID 필요",
    create: "추가",
    update: "수정",
    delete: "삭제",
    operationDone: "작업 완료. 데이터베이스가 자동 백업되었습니다.",
    settingsDesc: "언어, 테마, 강조색은 브라우저에 저장됩니다.",
    language: "언어",
    theme: "테마",
    color: "색상",
    themeSystem: "시스템 따름",
    themeLight: "라이트",
    themeDark: "다크",
    accentCyan: "시안",
    accentGreen: "그린",
    accentViolet: "바이올렛",
    accentAmber: "앰버",
    docsEmpty: "문서가 없습니다.",
  },
  "en-US": {
    appTagline: "OpenClaw generic scheduling workbench",
    statusIdle: "Ready",
    statusLoading: "Generating OpenClaw task template",
    statusGenerated: "Generated {count} task templates",
    statusSaved: "Saved batch #{id}",
    statusCopied: "Template copied to clipboard",
    requestFailed: "Request failed",
    emptyProduct: "Product pending",
    batchSetup: "Batch Setup",
    panelDesc: "Set the time window, minimum interval, and product list.",
    startTime: "Start time",
    endTime: "End time",
    taskCount: "Task count",
    minInterval: "Minimum interval",
    productAndManual: "Products and manual times",
    pasteHint: "Paste multiple product lines to expand automatically",
    productName: "Product name",
    timelineKicker: "Run Timeline",
    timelineDesc: "Each time point is an independent single-article task.",
    productPrefix: "Product",
    statsKicker: "Usage Balance",
    statsDesc: "Use saved batches to watch product publishing density.",
    noStats: "No saved records.",
    promptKicker: "OpenClaw Prompt",
    resultDesc: "Copy the generated text and send it to OpenClaw.",
    resultPlaceholder: "Generated result will appear here.",
    tabDatabase: "Database",
    tabSettings: "Settings",
    tabDocs: "Docs",
    databaseOverview: "Database Overview",
    loading: "Loading...",
    searchTable: "Search current table",
    refresh: "Refresh",
    protectedCrud: "Protected CRUD",
    crudHint: "Writes back up SQLite first. Confirmation token: CONFIRM",
    rowId: "Record ID",
    rowIdPlaceholder: "ID required for update/delete",
    create: "Create",
    update: "Update",
    delete: "Delete",
    operationDone: "Operation complete. Database backed up automatically.",
    settingsDesc: "Language, theme, and accent color are saved in the browser.",
    language: "Language",
    theme: "Theme",
    color: "Color",
    themeSystem: "Follow system",
    themeLight: "Light",
    themeDark: "Dark",
    accentCyan: "Cyan",
    accentGreen: "Green",
    accentViolet: "Violet",
    accentAmber: "Amber",
    docsEmpty: "No document.",
  },
  "fr-FR": {
    appTagline: "Atelier de planification OpenClaw générique",
    statusIdle: "Prêt",
    statusLoading: "Génération du modèle OpenClaw",
    statusGenerated: "{count} modèles générés",
    statusSaved: "Lot #{id} enregistré",
    statusCopied: "Modèle copié dans le presse-papiers",
    requestFailed: "Requête échouée",
    emptyProduct: "Produit à renseigner",
    batchSetup: "Configuration du lot",
    panelDesc: "Définir la fenêtre horaire, l'intervalle minimum et les produits.",
    startTime: "Début",
    endTime: "Fin",
    taskCount: "Nombre de tâches",
    minInterval: "Intervalle minimum",
    productAndManual: "Produits et horaires manuels",
    pasteHint: "Collez plusieurs lignes de produits pour les ajouter",
    productName: "Nom du produit",
    timelineKicker: "Chronologie",
    timelineDesc: "Chaque horaire est une tâche indépendante.",
    productPrefix: "Produit",
    statsKicker: "Équilibre d'utilisation",
    statsDesc: "Les lots enregistrés aident à surveiller la densité.",
    noStats: "Aucun enregistrement.",
    promptKicker: "Invite OpenClaw",
    resultDesc: "Copiez le texte généré et envoyez-le à OpenClaw.",
    resultPlaceholder: "Le résultat généré apparaîtra ici.",
    tabDatabase: "Base de données",
    tabSettings: "Paramètres",
    tabDocs: "Docs",
    databaseOverview: "Vue de la base",
    loading: "Chargement...",
    searchTable: "Rechercher dans la table",
    refresh: "Actualiser",
    protectedCrud: "CRUD protégé",
    crudHint: "Les écritures sauvegardent SQLite. Jeton : CONFIRM",
    rowId: "ID",
    rowIdPlaceholder: "ID requis pour modifier/supprimer",
    create: "Créer",
    update: "Modifier",
    delete: "Supprimer",
    operationDone: "Opération terminée. Base sauvegardée automatiquement.",
    settingsDesc: "Langue, thème et couleur sont enregistrés dans le navigateur.",
    language: "Langue",
    theme: "Thème",
    color: "Couleur",
    themeSystem: "Système",
    themeLight: "Clair",
    themeDark: "Sombre",
    accentCyan: "Cyan",
    accentGreen: "Vert",
    accentViolet: "Violet",
    accentAmber: "Ambre",
    docsEmpty: "Aucun document.",
  },
  "it-IT": {
    appTagline: "Banco di pianificazione OpenClaw generico",
    statusIdle: "Pronto",
    statusLoading: "Generazione modello OpenClaw",
    statusGenerated: "{count} modelli generati",
    statusSaved: "Batch #{id} salvato",
    statusCopied: "Modello copiato negli appunti",
    requestFailed: "Richiesta non riuscita",
    emptyProduct: "Prodotto da inserire",
    batchSetup: "Impostazione batch",
    panelDesc: "Imposta finestra oraria, intervallo minimo e prodotti.",
    startTime: "Inizio",
    endTime: "Fine",
    taskCount: "Numero attività",
    minInterval: "Intervallo minimo",
    productAndManual: "Prodotti e orari manuali",
    pasteHint: "Incolla più righe di prodotti per espandere",
    productName: "Nome prodotto",
    timelineKicker: "Timeline",
    timelineDesc: "Ogni orario è un'attività indipendente.",
    productPrefix: "Prodotto",
    statsKicker: "Bilanciamento uso",
    statsDesc: "I batch salvati aiutano a controllare la densità.",
    noStats: "Nessun record salvato.",
    promptKicker: "Prompt OpenClaw",
    resultDesc: "Copia il testo generato e invialo a OpenClaw.",
    resultPlaceholder: "Il risultato generato apparirà qui.",
    tabDatabase: "Database",
    tabSettings: "Impostazioni",
    tabDocs: "Documenti",
    databaseOverview: "Panoramica database",
    loading: "Caricamento...",
    searchTable: "Cerca nella tabella",
    refresh: "Aggiorna",
    protectedCrud: "CRUD protetto",
    crudHint: "Le scritture salvano prima SQLite. Token: CONFIRM",
    rowId: "ID record",
    rowIdPlaceholder: "ID richiesto per modifica/eliminazione",
    create: "Crea",
    update: "Modifica",
    delete: "Elimina",
    operationDone: "Operazione completata. Database salvato automaticamente.",
    settingsDesc: "Lingua, tema e colore sono salvati nel browser.",
    language: "Lingua",
    theme: "Tema",
    color: "Colore",
    themeSystem: "Sistema",
    themeLight: "Chiaro",
    themeDark: "Scuro",
    accentCyan: "Ciano",
    accentGreen: "Verde",
    accentViolet: "Viola",
    accentAmber: "Ambra",
    docsEmpty: "Nessun documento.",
  },
};

function labelsFor(locale) {
  return { ...I18N["en-US"], ...EXTRA_I18N["en-US"], ...(I18N[locale] || {}), ...(EXTRA_I18N[locale] || {}) };
}

const defaultProducts = [
  "三丰粗糙度仪SJ-310",
  "泰勒霍普森 Surtronic S-116粗糙度仪",
  "MINITEST725 EPK涂层测厚仪",
  "",
  "",
];

function App() {
  const [settings, setSettings] = useState(() =>
    readJson(SETTINGS_KEY, { locale: "zh-CN", theme: "system", accent: "cyan" }),
  );
  const [view, setView] = useState(() => (window.location.hash === "#/control" ? "control" : "workbench"));
  const saved = readJson(STORAGE_KEY, null);
  const [form, setForm] = useState(
    saved || {
      startTime: "15:30",
      endTime: "16:30",
      taskCount: 5,
      intervalMin: 10,
      products: defaultProducts,
      manualTimes: ["", "", "", "", ""],
    },
  );
  const [result, setResult] = useState(null);
  const [stats, setStats] = useState([]);
  const [status, setStatus] = useState(() => labelsFor(settings.locale).statusIdle);
  const [busy, setBusy] = useState(false);
  const shellRef = useRef(null);
  const t = labelsFor(settings.locale);

  useEffect(() => {
    setStatus((current) => {
      const idleValues = Object.values(EXTRA_I18N).map((labels) => labels.statusIdle);
      return idleValues.includes(current) ? t.statusIdle : current;
    });
  }, [settings.locale, t.statusIdle]);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ schema: 1, data: form }));
  }, [form]);

  useEffect(() => {
    applyTheme(settings, SETTINGS_KEY);
  }, [settings]);

  useEffect(() => {
    const onHash = () => setView(window.location.hash === "#/control" ? "control" : "workbench");
    window.addEventListener("hashchange", onHash);
    return () => window.removeEventListener("hashchange", onHash);
  }, []);

  useEffect(() => {
    const ctx = gsap.context(() => {
      gsap.from(".reveal", { opacity: 0, y: 24, duration: 0.65, stagger: 0.05, ease: "power3.out" });
      gsap.to(".brand-orbit", { rotate: 360, transformOrigin: "50% 50%", duration: 20, ease: "none", repeat: -1 });
      gsap.to(".scan-line", { xPercent: 120, duration: 5.4, ease: "none", repeat: -1 });
    }, shellRef);
    return () => ctx.revert();
  }, [view]);

  useEffect(() => {
    apiJson("/api/products/stats?limit=8").then(setStats).catch(() => setStats([]));
  }, []);

  function updateSettings(patch) {
    setSettings((current) => ({ ...current, ...patch }));
  }

  function openControl() {
    window.location.hash = "#/control";
    setView("control");
  }

  function closeControl() {
    window.location.hash = "";
    setView("workbench");
  }

  return (
    <main ref={shellRef} className="shell">
      <div className="stage-backdrop" aria-hidden="true"><span className="scan-line" /></div>
      <AppBar
        status={status}
        settings={settings}
        updateSettings={updateSettings}
        t={t}
        view={view}
        openControl={openControl}
        closeControl={closeControl}
      />
      {view === "control" ? (
        <ControlPanel settings={settings} updateSettings={updateSettings} t={t} />
      ) : (
        <Workbench
          form={form}
          setForm={setForm}
          settings={settings}
          result={result}
          setResult={setResult}
          stats={stats}
          setStats={setStats}
          status={status}
          setStatus={setStatus}
          busy={busy}
          setBusy={setBusy}
          t={t}
        />
      )}
    </main>
  );
}

function AppBar({ status, settings, updateSettings, t, view, openControl, closeControl }) {
  return (
    <header className="app-bar reveal">
      <div className="brand">
        <div className="logo-mark" aria-hidden="true"><span className="brand-orbit" /></div>
        <div><p>ArticleOps Studio</p><span>{t.appTagline}</span></div>
      </div>
      <div className="top-controls">
        <select value={settings.locale} onChange={(e) => updateSettings({ locale: e.target.value })}>
          {LOCALES.map(([code, label]) => <option key={code} value={code}>{label}</option>)}
        </select>
        <div className={`status-pill ${statusTone(status)}`}><span />{status}</div>
        <button onClick={view === "control" ? closeControl : openControl}>
          {view === "control" ? t.back : t.control}
        </button>
      </div>
    </header>
  );
}

function Workbench({ form, setForm, settings, result, setResult, stats, setStats, setStatus, busy, setBusy, t }) {
  const taskSlots = useMemo(() => {
    const count = Math.max(1, Math.min(Number(form.taskCount) || 1, 50));
    return Array.from({ length: count }, (_, index) => index);
  }, [form.taskCount]);
  const filledProducts = form.products.filter((item) => item.trim()).length;
  const manualTimeCount = form.manualTimes.filter((item) => item.trim()).length;
  const timelineItems = result?.items || taskSlots.map((_, index) => ({
    index: index + 1,
    time: form.manualTimes[index] || "--:--",
    product: form.products[index] || t.emptyProduct,
  }));
  const metrics = [
    { label: t.planned, value: taskSlots.length, accent: "blue" },
    { label: t.filled, value: filledProducts, accent: "teal" },
    { label: t.manual, value: manualTimeCount, accent: "amber" },
  ];

  function updateForm(patch) {
    setForm((current) => ({ ...current, ...patch }));
  }
  function updateArray(field, index, value) {
    setForm((current) => {
      const next = [...current[field]];
      next[index] = value;
      return { ...current, [field]: next };
    });
  }
  function syncTaskCount(nextCount) {
    const count = Math.max(1, Math.min(Number(nextCount) || 1, 50));
    setForm((current) => {
      const products = [...current.products];
      const manualTimes = [...current.manualTimes];
      while (products.length < count) products.push("");
      while (manualTimes.length < count) manualTimes.push("");
      return { ...current, taskCount: count, products: products.slice(0, count), manualTimes: manualTimes.slice(0, count) };
    });
  }
  function pasteProducts(event) {
    const text = event.clipboardData.getData("text");
    if (!text.includes("\n")) return;
    event.preventDefault();
    const lines = text.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
    if (!lines.length) return;
    setForm((current) => ({
      ...current,
      taskCount: lines.length,
      products: lines,
      manualTimes: Array.from({ length: lines.length }, (_, index) => current.manualTimes[index] || ""),
    }));
  }
  async function generate() {
    setBusy(true);
    setStatus(t.statusLoading);
    try {
      const payload = await apiJson("/api/schedules/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(buildPayload(form, settings)),
      });
      setResult(payload);
      setStatus(formatLabel(t.statusGenerated, { count: payload.items.length }));
      requestAnimationFrame(() => {
        gsap.fromTo(".timeline-card", { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.42, stagger: 0.045, ease: "power2.out" });
        gsap.fromTo(".result-text", { scale: 0.995 }, { scale: 1, duration: 0.36, ease: "power2.out" });
      });
    } catch (error) {
      setStatus(error.message);
    } finally {
      setBusy(false);
    }
  }
  async function saveBatch() {
    if (!result) return;
    setBusy(true);
    try {
      const payload = await apiJson("/api/schedules/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...buildPayload(form, settings), rendered_text: result.text }),
      });
      setStatus(formatLabel(t.statusSaved, { id: payload.batch_id }));
      setStats(await apiJson("/api/products/stats?limit=8"));
      gsap.fromTo(".stat-row", { opacity: 0.4, y: 8 }, { opacity: 1, y: 0, duration: 0.32, stagger: 0.035 });
    } catch (error) {
      setStatus(error.message);
    } finally {
      setBusy(false);
    }
  }
  async function copyResult() {
    if (!result?.text) return;
    await navigator.clipboard.writeText(result.text);
    setStatus(t.statusCopied);
    gsap.fromTo(".copy-button", { scale: 0.96 }, { scale: 1, duration: 0.24, ease: "back.out(3)" });
  }

  return (
    <>
      <section className="hero-strip reveal">
        <div><p className="eyebrow">{t.dashboard}</p><h1>{t.title}</h1><span>{t.subtitle}</span></div>
        <div className="metric-grid">{metrics.map((m) => <div className={`metric-card ${m.accent}`} key={m.label}><span>{m.label}</span><strong>{m.value}</strong></div>)}</div>
      </section>
      <section className="layout">
        <section className="control-panel panel reveal">
          <div className="panel-head"><p className="section-kicker">{t.batchSetup}</p><h2>{t.params}</h2><span>{t.panelDesc}</span></div>
          <div className="control-grid">
            <label>{t.startTime}<input type="time" value={form.startTime} onChange={(e) => updateForm({ startTime: e.target.value })} /></label>
            <label>{t.endTime}<input type="time" value={form.endTime} onChange={(e) => updateForm({ endTime: e.target.value })} /></label>
            <label>{t.taskCount}<input type="number" min="1" max="50" value={form.taskCount} onChange={(e) => syncTaskCount(e.target.value)} /></label>
            <label>{t.minInterval}<input type="number" min="1" max="720" value={form.intervalMin} onChange={(e) => updateForm({ intervalMin: e.target.value })} /></label>
          </div>
          <div className="product-list">
            <div className="list-title"><strong>{t.productAndManual}</strong><span>{t.pasteHint}</span></div>
            {taskSlots.map((_, index) => (
              <div className={`product-row ${form.products[index]?.trim() ? "ready" : ""}`} key={index}>
                <span>{index + 1}</span>
                <input value={form.manualTimes[index] || ""} placeholder="HH:mm" onChange={(e) => updateArray("manualTimes", index, e.target.value)} />
                <input value={form.products[index] || ""} placeholder={t.productName} onPaste={pasteProducts} onChange={(e) => updateArray("products", index, e.target.value)} />
              </div>
            ))}
          </div>
          <div className="actions">
            <button className="primary" disabled={busy} onClick={generate}><span className="button-icon">+</span>{t.generate}</button>
            <button disabled={busy || !result} onClick={saveBatch}>{t.save}</button>
          </div>
        </section>
        <aside className="side-stack">
          <section className="timeline-panel panel reveal">
            <div className="panel-head compact"><p className="section-kicker">{t.timelineKicker}</p><h2>{t.timeline}</h2><span>{t.timelineDesc}</span></div>
            <div className="timeline-list">{timelineItems.map((item) => <article className="timeline-card" key={`${item.index}-${item.time}-${item.product}`}><time>{item.time}</time><div><strong>{t.productPrefix} {item.index}</strong><p>{item.product}</p></div></article>)}</div>
          </section>
          <section className="stats-panel panel reveal">
            <div className="panel-head compact"><p className="section-kicker">{t.statsKicker}</p><h2>{t.stats}</h2><span>{t.statsDesc}</span></div>
            <div className="stats-list">{stats.length ? stats.map((item) => <div className="stat-row" key={item.product_name}><span>{item.product_name}</span><strong>{item.usage_count}</strong></div>) : <p className="empty">{t.noStats}</p>}</div>
          </section>
        </aside>
        <section className="result-panel panel reveal">
          <div className="panel-head compact result-head"><div><p className="section-kicker">{t.promptKicker}</p><h2>{t.result}</h2><span>{t.resultDesc}</span></div><button className="copy-button primary" disabled={!result} onClick={copyResult}>{t.copy}</button></div>
          <textarea className="result-text" readOnly value={result?.text || t.resultPlaceholder} />
        </section>
      </section>
    </>
  );
}

function ControlPanel({ settings, updateSettings, t }) {
  const [tab, setTab] = useState("database");
  return (
    <section className="control-console reveal">
      <div className="console-nav panel">
        {["database", "settings", "docs"].map((item) => (
          <button key={item} className={tab === item ? "primary" : ""} onClick={() => setTab(item)}>
            {item === "database" ? t.tabDatabase : item === "settings" ? t.tabSettings : t.tabDocs}
          </button>
        ))}
      </div>
      {tab === "database" && <DatabasePanel t={t} />}
      {tab === "settings" && <SettingsPanel settings={settings} updateSettings={updateSettings} t={t} />}
      {tab === "docs" && <DocsPanel t={t} />}
    </section>
  );
}

function DatabasePanel({ t }) {
  const [summary, setSummary] = useState(null);
  const [table, setTable] = useState("schedule_batches");
  const [rows, setRows] = useState(null);
  const [search, setSearch] = useState("");
  const [editText, setEditText] = useState("{}");
  const [rowId, setRowId] = useState("");
  const [message, setMessage] = useState("");

  async function refresh(nextTable = table) {
    const nextSummary = await apiJson("/api/admin/database/summary");
    setSummary(nextSummary);
    const data = await apiJson(`/api/admin/database/tables/${nextTable}/rows?page_size=50&search=${encodeURIComponent(search)}`);
    setRows(data);
  }

  useEffect(() => { refresh().catch((error) => setMessage(error.message)); }, []);

  async function write(kind) {
    try {
      const values = JSON.parse(editText || "{}");
      if (!values || Array.isArray(values) || typeof values !== "object") {
        throw new Error("写入内容必须是 JSON 对象。");
      }
      if ((kind === "update" || kind === "delete") && !rowId.trim()) {
        throw new Error("更新或删除需要先填写记录 ID。");
      }
      if (kind === "delete" && !window.confirm("确认删除这条记录？删除前会自动备份数据库。")) {
        return;
      }
      if (kind === "create") {
        await apiJson(`/api/admin/database/tables/${table}/rows`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ values, confirm: CONFIRM_TOKEN }) });
      } else if (kind === "update") {
        await apiJson(`/api/admin/database/tables/${table}/rows/${rowId}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ values, confirm: CONFIRM_TOKEN }) });
      } else if (kind === "delete") {
        await apiJson(`/api/admin/database/tables/${table}/rows/${rowId}?confirm=${CONFIRM_TOKEN}`, { method: "DELETE" });
      }
      setMessage(t.operationDone);
      await refresh();
    } catch (error) {
      setMessage(error.message);
    }
  }

  return (
    <section className="admin-grid">
      <div className="panel admin-panel">
        <div className="panel-head compact"><p className="section-kicker">Database</p><h2>{t.databaseOverview}</h2><span>{summary?.path || t.loading}</span></div>
        <div className="table-list">
          {summary?.tables?.map((item) => <button key={item.name} className={table === item.name ? "primary" : ""} onClick={() => { setTable(item.name); refresh(item.name); }}>{item.name}<strong>{item.count}</strong></button>)}
        </div>
        <div className="db-tools">
          <input value={search} placeholder={t.searchTable} onChange={(e) => setSearch(e.target.value)} />
          <button onClick={() => refresh()}>{t.refresh}</button>
        </div>
        <p className="empty">{message}</p>
      </div>
      <div className="panel admin-panel data-panel">
        <div className="panel-head compact"><p className="section-kicker">Rows</p><h2>{table}</h2><span>{rows?.total ?? 0} rows</span></div>
        <div className="data-table">
          <table>
            <thead><tr>{rows?.columns?.map((column) => <th key={column.name}>{column.name}</th>)}</tr></thead>
            <tbody>{rows?.rows?.map((row) => <tr key={row.id || JSON.stringify(row)} onClick={() => { setRowId(String(row.id || "")); setEditText(JSON.stringify(row, null, 2)); }}>{rows.columns.map((column) => <td key={column.name}>{String(row[column.name] ?? "")}</td>)}</tr>)}</tbody>
          </table>
        </div>
      </div>
      <div className="panel admin-panel">
        <div className="panel-head compact"><p className="section-kicker">Protected CRUD</p><h2>{t.protectedCrud}</h2><span>{t.crudHint}</span></div>
        <label>{t.rowId}<input value={rowId} onChange={(e) => setRowId(e.target.value)} placeholder={t.rowIdPlaceholder} /></label>
        <textarea className="json-editor" value={editText} onChange={(e) => setEditText(e.target.value)} />
        <div className="actions"><button onClick={() => write("create")}>{t.create}</button><button onClick={() => write("update")}>{t.update}</button><button onClick={() => write("delete")}>{t.delete}</button></div>
      </div>
    </section>
  );
}

function SettingsPanel({ settings, updateSettings, t }) {
  return (
    <section className="panel admin-panel">
      <div className="panel-head compact"><p className="section-kicker">Settings</p><h2>{t.tabSettings}</h2><span>{t.settingsDesc}</span></div>
      <div className="settings-grid">
        <label>{t.language}<select value={settings.locale} onChange={(e) => updateSettings({ locale: e.target.value })}>{LOCALES.map(([code, label]) => <option key={code} value={code}>{label}</option>)}</select></label>
        <label>{t.theme}<select value={settings.theme} onChange={(e) => updateSettings({ theme: e.target.value })}><option value="system">{t.themeSystem}</option><option value="light">{t.themeLight}</option><option value="dark">{t.themeDark}</option></select></label>
        <label>{t.color}<select value={settings.accent} onChange={(e) => updateSettings({ accent: e.target.value })}><option value="cyan">{t.accentCyan}</option><option value="green">{t.accentGreen}</option><option value="violet">{t.accentViolet}</option><option value="amber">{t.accentAmber}</option></select></label>
      </div>
    </section>
  );
}

function DocsPanel({ t }) {
  const [docs, setDocs] = useState([]);
  const [active, setActive] = useState(null);
  const [content, setContent] = useState("");
  useEffect(() => {
    apiJson("/api/docs").then((payload) => {
      setDocs(payload.documents || []);
      if (payload.documents?.[0]) loadDoc(payload.documents[0].slug);
    }).catch(() => setDocs([]));
  }, []);
  async function loadDoc(slug) {
    const doc = await apiJson(`/api/docs/${encodeURIComponent(slug)}`);
    setActive(doc.slug);
    setContent(doc.content);
  }
  return (
    <section className="docs-grid">
      <aside className="panel admin-panel doc-list">{docs.map((doc) => <button key={doc.slug} className={active === doc.slug ? "primary" : ""} onClick={() => loadDoc(doc.slug)}>{doc.slug}</button>)}</aside>
      <article className="panel admin-panel doc-view"><pre>{content || t.docsEmpty}</pre></article>
    </section>
  );
}

createRoot(document.getElementById("root")).render(<App />);
