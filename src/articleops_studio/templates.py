from __future__ import annotations

from collections.abc import Sequence
from hashlib import sha256
from textwrap import dedent

from .scheduler import ScheduleItem


CURRENT_TEMPLATE_NAME = "openclaw-scheduled-article-publish"
CURRENT_TEMPLATE_VERSION = "2026.06.03"
DEFAULT_LOCALE = "zh-CN"
SUPPORTED_LOCALES = ("zh-CN", "zh-TW", "ja-JP", "ko-KR", "en-US", "fr-FR", "it-IT")


TEMPLATE_BODY = dedent(
    """\
    帮我设置通用定时发文任务。

    任务批次：
    本次包含若干篇定时发文任务，通常为 5 篇，也可能少于或多于 5 篇。请按我列出的实际条目创建任务，不要自动补足到 5 篇，不要跳过任何一篇。

    任务性质：
    每个时间点都是一个独立的单篇文章发布任务。
    不要合并成批次队列，不做批次总汇总。
    每篇到点后独立执行、独立验收、独立记账、独立收尾、独立发送飞书群单篇回执。

    执行依据：
    必须读取并严格遵守当前目标发布平台对应的发文流程、账号状态和提交规则。

    执行方式：
    - 使用 cron 定时触发，每个时间点创建一个独立任务。
    - 每篇任务到点后按当前目标发布平台的完整发文流程执行。
    - 浏览器必须使用 browser profile=user，开始前先 warmup。
    - 不并发抢浏览器；每篇开始前检查是否已有发布/browser 任务执行中。
    - 如果浏览器已被占用，不要覆盖当前页面，不要抢占任务；按当前规则记录为阻断/失败/待确认，并发送该篇单篇回执。

    账号与页面上下文：
    - 不做固定账号、公司名、文章来源、所在地区校验。
    - 当前浏览器里使用哪个账号，就按当前账号继续执行。
    - 只确认当前目标后台处于可发文状态。
    - 如果未登录、登录失效、验证码、权限异常，则按当前规则中止、记账并回执。
    - 不主动修改、清空或覆盖文章来源、所在地区、账号信息。

    产品定位：
    - 每篇先同步/查询 SQLite products 表。
    - 按用户给出的产品名或型号定位产品。
    - 优先选择有 products.product_doc_path 的记录。
    - 再按 product_doc_path 读取对应产品资料作为文章资料来源。
    - 如果 SQLite 查不到或资料文件不存在，按当前资料不足规则处理，不要编造硬参数。

    发文要求：
    - 每篇都重新进入目标后台的新增文章空白页。
    - 如果出现“是否打开上次未发布的内容/是否恢复草稿”弹窗，必须点取消/不恢复；必要时重新进入添加文章页。
    - 标题、文章分类、正文、标签、所属类别等必要字段必须字段级串行填写。
    - 每个字段填写后必须页面读回确认，不能批量注入后直接提交。
    - 正文必须写入当前肉眼可见的正文编辑器，并读回正文长度。
    - 不能只依赖本地变量、隐藏字段或编辑器内部实例判断正文已填写。
    - 默认正文长度按当前发布规则执行，除非我明确要求短文。

    提交前硬闸门：
    发布前必须通过当前发布流程的提交前校验：
    - 标题已读回；
    - 文章分类/栏目已读回；
    - 正文可见编辑器已读回，且正文不为空；
    - 正文包含当前产品名、品牌或型号；
    - 标签已逐个读回；
    - 所属类别已逐级读回；
    - 敏感词预检已完成；
    - 提交前校验脚本或人工复核返回允许提交。

    任一关键证据不足，禁止点击发布，按阻断/失败记账并发送该篇回执。

    成功判定：
    cron run ok 只代表定时任务被触发，不代表文章发布成功。
    发布成功只能以页面成功提示、成功回调或管理列表复核到最终标题为准。

    终态要求：
    每篇无论成功、失败、提交结果未知、被提交前硬闸门阻断，都必须：
    1. 写入对应发布记录；
    2. 按最终标题反查 SQLite，确认本篇记录存在；
    3. 执行收尾流程，删除本篇 payload/草稿临时文件，移动 run evidence，并只保留最新两篇；
    4. 发送飞书群单篇短回执。

    回执要求：
    每篇进入终态后立刻发送该篇短回执，不等其它篇完成。
    回执至少包含：
    - 状态；
    - 产品；
    - 标题；
    - 计划时间；
    - 完成时间；
    - 成功证据或失败/阻断原因；
    - 记录 id 或未写入原因。

    请按下面实际列表设置定时任务：
    """
)


LOCALIZED_TEMPLATE_BODIES = {
    "zh-CN": TEMPLATE_BODY,
    "zh-TW": dedent(
        """\
        請幫我設定通用定時發文任務。

        任務批次：
        本次包含若干篇定時發文任務，通常為 5 篇，也可能少於或多於 5 篇。請只按照實際條目建立任務，不要自動補足到 5 篇，也不要跳過任何一篇。

        核心要求：
        - 每個時間點都是獨立的單篇文章發布任務，不合併批次隊列。
        - 每篇到點後獨立執行、驗收、記帳、收尾，並獨立發送飛書群單篇回執。
        - 必須遵守目前目標發布平台對應的發文流程、帳號狀態和提交規則。
        - 使用 cron 定時觸發；瀏覽器必須使用 browser profile=user，開始前先 warmup。
        - 不並發搶瀏覽器；開始前檢查是否已有發布/browser 任務執行中。
        - 不做固定帳號、公司名、文章來源、所在地區校驗；沿用目前瀏覽器帳號。
        - 每篇先同步/查詢 SQLite products 表，再按 products.product_doc_path 讀取產品資料。
        - 不編造硬參數；資料不足時按目前規則阻斷、記帳並回執。
        - 每篇重新進入目標後台新增文章空白頁；如有恢復草稿彈窗，必須取消/不恢復。
        - 標題、文章分類、正文、標籤、所屬類別必須欄位級串行填寫並讀回確認。
        - 正文必須寫入肉眼可見的正文編輯器，不能只依賴隱藏欄位或編輯器內部實例。
        - 發布前必須通過提交前校驗；任一關鍵證據不足，禁止點擊發布。
        - cron run ok 不等於文章發布成功；成功只能以頁面成功提示、成功回調或管理列表復核最終標題為準。
        - 無論成功、失敗、提交結果未知或被硬閘門阻斷，都必須寫入對應發布記錄，反查確認，執行收尾流程，並發送單篇回執。

        請按下面實際列表設定定時任務：
        """
    ),
    "ja-JP": dedent(
        """\
        汎用の予約投稿タスクを設定してください。

        この依頼には複数の予約投稿タスクが含まれます。通常は 5 件ですが、増減する場合があります。実際に列挙された項目だけを作成し、自動で補完せず、どの項目もスキップしないでください。

        実行ルール：
        - 各時刻は独立した単一記事公開タスクです。バッチキューへ統合しないでください。
        - 各記事は独立して実行、検収、記録、後処理し、Feishu グループへ単一記事の返信を送信してください。
        - 対象公開プラットフォームの公開手順、アカウント状態、送信ルールに厳密に従ってください。
        - cron で各時刻に独立タスクを起動します。browser profile=user を使い、開始前に warmup してください。
        - 開始前に公開/browser タスクが実行中か確認してください。
        - 固定アカウント、会社名、記事ソース、地域は検証しません。現在のブラウザアカウントを使ってください。
        - SQLite products 表を同期/検索し、products.product_doc_path から製品資料を読みます。
        - ハードパラメータを捏造しないでください。資料不足の場合は現在のルールに従い、阻断/失敗として記録し返信してください。
        - 毎回対象バックエンドの新規記事空白ページへ入り、草稿復元ダイアログはキャンセルしてください。
        - タイトル、分類、本文、タグ、所属カテゴリはフィールド単位で順番に入力し、入力後に画面から読み戻して確認してください。
        - cron run ok は記事公開成功を意味しません。成功判定は成功表示、成功コールバック、または管理一覧での最終タイトル確認に限定します。

        以下の実リストに従って予約タスクを設定してください：
        """
    ),
    "ko-KR": dedent(
        """\
        범용 예약 게시 작업을 설정해 주세요.

        이번 작업은 여러 개의 예약 게시 작업을 포함합니다. 보통 5건이지만 더 적거나 많을 수 있습니다. 실제로 나열된 항목만 생성하고, 자동으로 채우지 말며, 어떤 항목도 건너뛰지 마세요.

        실행 규칙:
        - 각 시간점은 독립적인 단일 글 게시 작업입니다. 배치 큐로 합치지 마세요.
        - 각 글은 독립 실행, 검수, 기록, 마무리 후 Feishu 그룹에 단일 글 회신을 보내야 합니다.
        - 대상 게시 플랫폼의 게시 절차, 계정 상태, 제출 규칙을 엄격히 따라야 합니다.
        - cron 으로 각 시간점에 독립 작업을 트리거합니다. browser profile=user 를 사용하고 시작 전 warmup 을 수행하세요.
        - 시작 전 게시/browser 작업이 실행 중인지 확인하세요.
        - 고정 계정, 회사명, 글 출처, 지역 검증은 하지 않습니다. 현재 브라우저 계정을 그대로 사용하세요.
        - SQLite products 테이블을 동기화/조회하고 products.product_doc_path 로 제품 자료를 읽습니다.
        - 하드 파라미터를 지어내지 마세요. 자료가 부족하면 현재 규칙에 따라 차단/실패로 기록하고 회신하세요.
        - 매번 대상 백엔드의 신규 글 빈 페이지로 들어가며, 초안 복원 팝업은 취소/복원 안 함을 선택하세요.
        - 제목, 분류, 본문, 태그, 소속 카테고리는 필드별로 순차 입력하고 입력 후 화면에서 다시 읽어 확인하세요.
        - cron run ok 는 글 게시 성공이 아닙니다. 성공은 성공 표시, 성공 콜백, 또는 관리 목록의 최종 제목 확인으로만 판단합니다.

        아래 실제 목록대로 예약 작업을 설정하세요:
        """
    ),
    "en-US": dedent(
        """\
        Please set up scheduled article publishing tasks.

        Task batch:
        This request contains several scheduled publishing tasks, usually 5 articles, but it may be fewer or more. Create tasks only for the actual entries listed below. Do not auto-fill to 5 and do not skip any entry.

        Execution rules:
        - Each time point is an independent single-article publishing task. Do not merge them into a batch queue.
        - Each article must run, validate, record, finalize, and send a Feishu single-article receipt independently.
        - Follow the current target publishing platform workflow, account state, and submit rules.
        - Use cron for scheduling. Use browser profile=user and perform warmup before starting.
        - Before starting, check whether a publishing/browser task is already running.
        - Do not validate a fixed account, company name, article source, or region. Continue with the current browser account.
        - For each article, sync/query the SQLite products table first, then read product material from products.product_doc_path.
        - Do not invent hard parameters. If source material is insufficient, follow the current rules to block/fail, record, and send a receipt.
        - Enter a fresh blank article page in the target backend for each task. If a draft recovery dialog appears, cancel/do not restore.
        - Fill title, category, body, tags, and owned category sequentially by field, and read each field back from the page after filling.
        - The body must be written into the visible body editor. Do not rely only on hidden fields or editor internals.
        - Before publishing, pass the pre-submit gate. If any critical evidence is missing, do not click publish.
        - cron run ok only means the scheduled task was triggered, not that publishing succeeded. Success must be based on a success message, success callback, or final-title verification in the management list.
        - Whether success, failure, unknown submit result, or pre-submit gate block occurs, write the corresponding publishing record, verify it by final title, run finalization, and send a Feishu single-article receipt.

        Set the scheduled tasks according to the actual list below:
        """
    ),
    "fr-FR": dedent(
        """\
        Veuillez configurer les tâches de publication programmée.

        Cette demande contient plusieurs tâches de publication, généralement 5 articles, mais il peut y en avoir plus ou moins. Créez uniquement les tâches listées ci-dessous, sans compléter automatiquement et sans ignorer d'entrée.

        Règles d'exécution :
        - Chaque horaire est une tâche de publication indépendante pour un seul article.
        - Chaque article doit être exécuté, vérifié, enregistré, finalisé et faire l'objet d'un reçu Feishu individuel.
        - Respectez le flux de publication, l'état du compte et les règles de soumission de la plateforme cible.
        - Utilisez cron pour le déclenchement. Utilisez browser profile=user et effectuez warmup avant de commencer.
        - Vérifiez si une tâche publishing/browser est déjà en cours avant chaque démarrage.
        - Ne vérifiez pas de compte, société, source d'article ou région fixes. Continuez avec le compte actuellement ouvert dans le navigateur.
        - Synchronisez/interrogez la table SQLite products, puis lisez les sources produit via products.product_doc_path.
        - N'inventez pas de paramètres durs. Si les sources sont insuffisantes, bloquez/échouez, enregistrez et envoyez le reçu selon les règles actuelles.
        - Ouvrez une page vierge de nouvel article dans le back-office cible pour chaque tâche.
        - cron run ok signifie seulement que la tâche a été déclenchée, pas que la publication a réussi.

        Configurez les tâches selon la liste réelle ci-dessous :
        """
    ),
    "it-IT": dedent(
        """\
        Configura le attività programmate di pubblicazione.

        Questa richiesta contiene diverse attività di pubblicazione, di solito 5 articoli, ma possono essere meno o più. Crea solo le attività elencate sotto, senza completare automaticamente e senza saltare alcuna voce.

        Regole di esecuzione:
        - Ogni orario è una singola attività di pubblicazione indipendente.
        - Ogni articolo deve essere eseguito, verificato, registrato, finalizzato e notificato con ricevuta Feishu individuale.
        - Segui il flusso di pubblicazione, lo stato account e le regole di invio della piattaforma target.
        - Usa cron per la pianificazione. Usa browser profile=user ed esegui warmup prima di iniziare.
        - Prima di iniziare, verifica se è già in esecuzione un'attività publishing/browser.
        - Non verificare account, azienda, fonte articolo o area fissi. Continua con l'account attualmente aperto nel browser.
        - Sincronizza/interroga la tabella SQLite products, poi leggi il materiale prodotto tramite products.product_doc_path.
        - Non inventare parametri rigidi. Se le fonti sono insufficienti, blocca/fallisci, registra e invia ricevuta secondo le regole correnti.
        - Entra ogni volta in una nuova pagina articolo vuota nel backend target.
        - cron run ok significa solo che l'attività è stata attivata, non che la pubblicazione è riuscita.

        Configura le attività secondo l'elenco reale qui sotto:
        """
    ),
}


def normalize_locale(locale: str | None = None) -> str:
    if locale in SUPPORTED_LOCALES:
        return str(locale)
    return DEFAULT_LOCALE


def get_template_body(locale: str | None = None) -> str:
    return LOCALIZED_TEMPLATE_BODIES[normalize_locale(locale)]


def current_template_hash(locale: str | None = None) -> str:
    return sha256(get_template_body(locale).encode("utf-8")).hexdigest()


def render_schedule_text(items: Sequence[ScheduleItem], locale: str | None = None) -> str:
    if not items:
        raise ValueError("至少需要一个任务才能生成文案。")

    language = normalize_locale(locale)
    lines = [get_template_body(language).rstrip(), ""]
    for item in items:
        if language == "zh-CN":
            task_label, product_label, time_label = "任务", "产品", "时间"
            task_text = "发布一篇文章"
            separator = "："
        elif language == "zh-TW":
            task_label, product_label, time_label = "任務", "產品", "時間"
            task_text = "發布一篇文章"
            separator = "："
        else:
            task_label, product_label, time_label = "Task", "Product", "Time"
            task_text = "Publish one article"
            separator = ": "
        lines.extend(
            [
                f"{item.index}.",
                f"{time_label}{separator}{item.time_text}",
                f"{task_label}{separator}{task_text}",
                f"{product_label}{separator}{item.product_name}",
                "",
            ]
        )
    return "\n".join(lines).strip()
