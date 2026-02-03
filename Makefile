SKILLS_DIR := $(HOME)/.cursor/skills
SKILL_FOLDERS := analyze app export-chat-history image-to-svg research website workflow

.PHONY: all install clean

all: install

install: $(SKILLS_DIR)
	@for folder in $(SKILL_FOLDERS); do \
		if [ -d "$$folder" ]; then \
			link_path="$(SKILLS_DIR)/$$folder"; \
			if [ -L "$$link_path" ] || [ -e "$$link_path" ]; then \
				echo "Removing existing $$link_path"; \
				rm -rf "$$link_path"; \
			fi; \
			echo "Creating symlink: $$link_path -> $(PWD)/$$folder"; \
			ln -s "$(PWD)/$$folder" "$$link_path"; \
		fi; \
	done
	@echo "Symlinks created successfully!"

$(SKILLS_DIR):
	@mkdir -p $(SKILLS_DIR)
	@echo "Created directory: $(SKILLS_DIR)"

clean:
	@for folder in $(SKILL_FOLDERS); do \
		link_path="$(SKILLS_DIR)/$$folder"; \
		if [ -L "$$link_path" ]; then \
			echo "Removing symlink: $$link_path"; \
			rm "$$link_path"; \
		fi; \
	done
	@echo "Cleanup complete!"
