# Python + Playwright ロケーター自己修復支援ツール

本プロジェクトは Playwright 実行失敗時の証跡収集、ロケーター修正案の提示、Claude Code Hook/Skill との連携、および承認後の最小限の修正を実装します。**完全自律型の自己修復システムではありません**。デフォルトではコードを自動変更しません。

## インストール

Python 3.10 以上を推奨します。

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## 実行例

```bash
python tools/heal_runner.py examples/passing.py
python tools/heal_runner.py examples/failing_locator.py
python tools/heal_runner.py examples/failing_assertion.py
python tools/repair_locator.py examples/_healing/failing_locator/bundle.json
pytest -q
```

`passing.py` は成功例です。`failing_locator.py` はボタン名を意図的に間違えた失敗例で、`bundle.json`、ARIA スナップショット、スクリーンショット、トレースバックを保存します。`failing_assertion.py` はロケーター以外の失敗例なので、ロケーター修復を試みてはいけません。

`repair_locator.py` は修正案だけを表示します。対象要素が一意でテスト意図に合致していることを実ブラウザーで確認してください。提案 JSON を `proposal.json` に保存後、承認する場合のみ次を実行します。

```bash
python tools/apply_repair.py examples/failing_locator.py proposal.json --approve
```

## Claude Code 連携

`.claude/settings.json` の PostToolUse Hook がテスト失敗を検出し、`.claude/skills/heal-locators/SKILL.md` の手順を案内します。Phase 0–8 は、実行、診断、ライブ検証、修正、横展開の調査、再検証、記録、Git 作業、継続改善です。

## 制限と安全

- ブラウザーが閉じた後は証跡が取得できないため、失敗例では終了前に `capture_in_context` を呼び出します。
- CDP のポート 9222 を自動公開せず、Playwright の内部実装を無条件で書き換えません。
- 単一行の単純なボタンロケーターのみ修正案を生成します。複雑なケースは人間が判断してください。
- テストデータ、期待値、URL、待機時間を自動変更しません。main に自動 push しません。
- `_healing/` は Git の対象外です。認証情報や機密スクリーンショットをアップロードしないでください。

## 統合修復フロー（標準はドライラン）

```bash
python tools/heal_pipeline.py examples/failing_locator.py
# 修正候補が本来の操作対象であることを確認してから明示的に許可します。
python tools/heal_pipeline.py examples/failing_locator.py --apply
python -m pytest -q
```

通常は証跡と修正候補を出力するだけです。`--apply` を付けた場合のみ、サポート対象の一行 `get_by_role('button', name=...)` に対して最小限の変更を行い、再実行で失敗した場合は元のコードに戻します。意図的な失敗例を残すため、先にサンプルを複製することを推奨します。複雑なページや実際の業務要件の妥当性まで自動保証する仕組みではありません。[改善内容と理由](docs/IMPROVEMENTS.md) を参照してください。
