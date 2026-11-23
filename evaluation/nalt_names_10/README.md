# Foodscan naming slice10, local evidence, November22,2026

Local stack on unpublished slice9: four new ingredient/category heads and five exact names. These are canonical/category-name counts, not disjoint foods or a coverage percentage. Candidate541canonical/294aliases; combined above pinned main1513332 is23heads/45aliases. No source publication or deployment.

## Scope

New heads: root vegetables, citrus fruits, leafy vegetables and inflorescence vegetables. Names: fresh greens, leafy greens, leafy green vegetables, green leafy vegetables and salad greens. Each is a current NALT Product term or explicit synonym, with the current NOVA fruit/vegetable class independently supporting the plain category. Class-instance, not exact-named food evidence, and not a strong marker. No prior CSV row, classifier, browser engine or marker changes.

## Validation

- Scoped suite9214passed, same two baseline failures, two skips, one deselected, five expected failures. Restricted reference module excluded, not validated.
- Build14805/14805full-field analyses identical,7785OCR-text-path/7020paste-path. Not photo-capture evidence.
- Wider26026full-field Python/browser analyses and8115alias-parent comparisons, zero mismatch. No unsupported new-category powder answer under any tested parent, including misleading outer100%.
- All826existing local names retain identical full results, not only non-provenance fields. Frozen66identical.
- Original32frozen OOS ingredient texts reused, hashes/manifest unchanged,64full-field before/after source-path results identical and128Python/browser cross-engine analyses match. Targeted regression evidence, not an accuracy estimate. Raw OFF contents remain outside the repository.

## Rejected proposals and remaining gaps

Initial green-leafy canonical plus shorter leafy-vegetables alias repeated the green modifier. Using the explicit leafy-vegetables synonym as canonical and the preferred term as an alias fixes it without a guard change. Dried/dehydrated vegetables are excluded after affected-form controls. Both fungi proposals are excluded after wide unsupported-powder controls, even though their plain identities and NOVA class were source-backed. Do not restore them based on the smaller passing set or treat alias-parent equality alone as sufficient. Other holds remain; no held singular is bypassed with a plural. Original photographs are not newly validated.

Actual local pixels inspected: Green Leafy Vegetables1, Salted Root Vegetables3, Root Vegetables Extract abstains, Edible Fungi remains held.

## Release gate

Local candidate only. Slice9 remains independently preserved and its delivered patch is unchanged. A fresh main reconciliation and supported source-write route are required before publishing. No account/security setting, secret-collection request, deployment retry or spending action.
