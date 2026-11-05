#!/usr/bin/env bash
# Creates ./work/<fixture> as fresh one-commit git repos from the plain files in ./fixtures.
# f5-interop-revenue and f6-rename-v10 are copies of f1-revenue and f6-rename (each case needs its own folder).
# Re-run to reset: it deletes ./work first.
set -euo pipefail
cd "$(dirname "$0")"
rm -rf work && mkdir work
make() { # src dest
  cp -r "fixtures/$1" "work/$2"
  ( cd "work/$2" && git init -q && git config user.email t@example.com && git config user.name tester && git add -A && git commit -qm init )
}
make f1-revenue f1-revenue
make f1-revenue f5-interop-revenue
make f2-email f2-email
make f3-tests f3-tests
make f4-board f4-board
make f6-rename f6-rename
make f6-rename f6-rename-v10
echo "fixtures ready in ./work"
