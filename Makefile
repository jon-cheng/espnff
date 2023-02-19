# Data Science Repo Makefile

# Define variables
PROJECT_NAME := espnff
CONDA_ENV_NAME := espnff_env
PYTHON_VERSION := 3.10
PYTHON_INTERPRETER := python$(PYTHON_VERSION)

# Define file paths
SRC := src
DATA_DIR := data
NOTEBOOKS_DIR := notebooks
MODELS_DIR := models
REPORTS_DIR := reports

# Define commands
CONDA_CREATE_ENV := conda create --name $(CONDA_ENV_NAME) python=$(PYTHON_VERSION) -y
CONDA_ACTIVATE_ENV := conda activate $(CONDA_ENV_NAME)
CONDA_DEACTIVATE_ENV := conda deactivate
INSTALL_REQUIREMENTS := pip install -r requirements.txt
RUN_NOTEBOOKS := jupyter nbconvert --execute --to notebook --inplace $(NOTEBOOKS_DIR)/*.ipynb
MKDIR := mkdir -p

.PHONY: help create_environment activate_environment deactivate_environment install_requirements run_notebooks create_folders

help:
	@echo "Available commands:"
	@echo "  make create_environment"
	@echo "  make activate_environment"
	@echo "  make deactivate_environment"
	@echo "  make install_requirements"
	@echo "  make run_notebooks"
	@echo "  make create_folders"

create_environment:
	$(CONDA_CREATE_ENV)
	$(CONDA_ACTIVATE_ENV)
	$(INSTALL_REQUIREMENTS)
	$(CONDA_DEACTIVATE_ENV)

activate_environment:
	$(CONDA_ACTIVATE_ENV)

deactivate_environment:
	$(CONDA_DEACTIVATE_ENV)

install_requirements:
	$(CONDA_ACTIVATE_ENV)
	$(INSTALL_REQUIREMENTS)
	$(CONDA_DEACTIVATE_ENV)

run_notebooks:
	$(CONDA_ACTIVATE_ENV)
	$(RUN_NOTEBOOKS)
	$(CONDA_DEACTIVATE_ENV)

create_folders:
	$(MKDIR) $(DATA_DIR)
	$(MKDIR) $(NOTEBOOKS_DIR)
	$(MKDIR) $(MODELS_DIR)
	$(MKDIR) $(REPORTS_DIR)
	$(MKDIR) $(SRC)

