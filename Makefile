SRC_DIR := .cursor/skills
SKILLS_DIR := $(HOME)/.cursor/skills
SKILL_FOLDERS := $(patsubst $(SRC_DIR)/%/SKILL.md,%,$(wildcard $(SRC_DIR)/*/SKILL.md))

.PHONY: all install clean

all: install

install: $(SKILLS_DIR)
	@count=0; for folder in $(SKILL_FOLDERS); do \
		[ -d "$(SRC_DIR)/$$folder" ] && rm -rf "$(SKILLS_DIR)/$$folder" && cp -r "$(SRC_DIR)/$$folder" "$(SKILLS_DIR)/$$folder" && \
		printf "  + %s\n" "$$folder" && count=$$((count+1)); \
	done; echo "Installed $$count skills to $(SKILLS_DIR)"

$(SKILLS_DIR):
	@mkdir -p $(SKILLS_DIR)

clean:
	@count=0; for folder in $(SKILL_FOLDERS); do \
		[ -e "$(SKILLS_DIR)/$$folder" ] && rm -rf "$(SKILLS_DIR)/$$folder" && \
		printf "  - %s\n" "$$folder" && count=$$((count+1)); \
	done; echo "Removed $$count skills"
