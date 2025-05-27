eval "$(ssh-agent -s)" && ssh-add ssh_key && ssh -T git@github.com
