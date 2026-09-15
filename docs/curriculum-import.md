# AI Engineering Curriculum Import

The Guides tab includes lesson markdown from [AI Engineering from
Scratch](https://github.com/rohitg00/ai-engineering-from-scratch), imported
from its `phases/*/*/docs/en.md` files. The source repository is distributed
under the MIT License, copyright (c) 2026 Rohit Ghumare. The license permits
redistribution; this attribution and the MIT permission notice must remain
with redistributed copies.

## Refreshing the content

The importer clones the source repository when no checkout is supplied:

```bash
python3 scripts/import_ai_eng_curriculum.py
```

For an offline or repeatable refresh, point it at an existing checkout:

```bash
python3 scripts/import_ai_eng_curriculum.py --source-dir /path/to/ai-engineering-from-scratch
```

The script regenerates `content/lessons/phases/` and reports phase, lesson,
skipped-entry, file, and byte counts. It imports lesson documentation only;
source `code/` and `outputs/` directories are intentionally left out.

## Scope

AI Engineering lessons are a read-only reference library for now. They are
not included in Practice, quiz generation, study-plan topic validation, or
mastery scoring, so their status remains `not_started`. Adding practice for
this curriculum requires generalized lesson-topic validation and exercise
flows rather than hundreds of fixed schema literals.