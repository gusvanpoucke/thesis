eval "$(ssh-agent -s)"

ssh-add ~/.ssh/thesis_key

ssh -T git@github.com