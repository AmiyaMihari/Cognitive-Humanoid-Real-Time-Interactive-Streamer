# Auto-activate a Python virtualenv when you cd into a project that has one.
#
# Installed by setup.sh to ~/.config/fish/conf.d/auto_venv.fish. Looks for
# `venv/` or `.venv/` in the current directory or any parent. When found, it
# sources the venv; when you leave that project tree, it deactivates again. It
# only ever deactivates a venv it activated itself, so manually activated
# environments are left untouched.

function __auto_venv --on-variable PWD --description "Auto (de)activate project venv"
    status is-command-substitution; and return

    # Search the current directory and its parents for a venv.
    set -l dir $PWD
    set -l found ""
    while true
        for name in venv .venv
            if test -f "$dir/$name/bin/activate.fish"
                set found "$dir/$name"
                break
            end
        end
        test -n "$found"; and break
        test "$dir" = "/"; and break
        set dir (path dirname $dir)
    end

    if test -n "$found"
        # Activate it unless it is already the active environment.
        if test "$VIRTUAL_ENV" != "$found"
            functions -q deactivate; and deactivate
            source "$found/bin/activate.fish"
            set -g __auto_venv_active 1
        end
    else if set -q __auto_venv_active
        # We auto-activated earlier and have now left the project tree.
        functions -q deactivate; and deactivate
        set -e __auto_venv_active
    end
end

# Run once for the directory the shell starts in.
__auto_venv
