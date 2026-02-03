SKILLS_DIR := $(HOME)/.cursor/skills
SKILL_FOLDERS := analyze app export-chat-history image-to-svg research website workflow

.PHONY: all install clean

all: install

install: $(SKILLS_DIR)
	@for folder in $(SKILL_FOLDERS); do \
		if [ -d "$$folder" ]; then \
			dest_path="$(SKILLS_DIR)/$$folder"; \
			if [ -e "$$dest_path" ]; then \
				echo "Removing existing $$dest_path"; \
				rm -rf "$$dest_path"; \
			fi; \
			echo "Copying $$folder to $$dest_path"; \
			cp -r "$$folder" "$$dest_path"; \
		fi; \
	done
	@echo "Skills copied successfully!"

$(SKILLS_DIR):
	@mkdir -p $(SKILLS_DIR)
	@echo "Created directory: $(SKILLS_DIR)"

clean:
	@for folder in $(SKILL_FOLDERS); do \
		dest_path="$(SKILLS_DIR)/$$folder"; \
		if [ -e "$$dest_path" ]; then \
			echo "Removing $$dest_path"; \
			rm -rf "$$dest_path"; \
		fi; \
	done
	@echo "Cleanup complete!"
