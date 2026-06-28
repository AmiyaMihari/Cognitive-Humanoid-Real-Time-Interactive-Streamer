# Auto-activate a Python virtualenv when you cd into a project that has one.
# (bash version; mirrors scripts/auto_venv.fish for the fish shell.)
#
# Installed by setup.sh, which adds a line to ~/.bashrc that sources this file.
# Looks for `venv/` or `.venv/` in the current directory or any parent. When
# found, it activates the venv; when you leave that project tree, it deactivates
# again. It only ever deactivates a venv it activated itself, so a manually
# activated environment is left untouched.

__auto_venv() {
    # Search the current directory and its parents for a venv.
    local dir="$PWD" found="" name
    while true; do
        for name in venv .venv; do
            if [ -f "$dir/$name/bin/activate" ]; then
                found="$dir/$name"
                break
            fi
        done
        [ -n "$found" ] && break
        [ "$dir" = "/" ] && break
        dir="$(dirname "$dir")"
    done

    if [ -n "$found" ]; then
        # Activate it unless it is already the active environment.
        if [ "$VIRTUAL_ENV" != "$found" ]; then
            type deactivate >/dev/null 2>&1 && deactivate
            # shellcheck disable=SC1091
            source "$found/bin/activate"
            __AUTO_VENV_ACTIVE=1
        fi
    elif [ -n "${__AUTO_VENV_ACTIVE:-}" ]; then
        # We auto-activated earlier and have now left the project tree.
        type deactivate >/dev/null 2>&1 && deactivate
        unset __AUTO_VENV_ACTIVE
    fi
}

# Run __auto_venv before every prompt, without clobbering an existing
# PROMPT_COMMAND and without adding itself twice.
case ";${PROMPT_COMMAND:-};" in
    *";__auto_venv;"*) ;;  # already registered
    *) PROMPT_COMMAND="__auto_venv${PROMPT_COMMAND:+;$PROMPT_COMMAND}" ;;
esac
