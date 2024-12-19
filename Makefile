#target_url="https://www.ai.gov/ai-use-case-inventories/"
#output_md5file="data/ai_gov_md5hash.csv"

compute:
	python src/P0_compute_checksums.py
	python src/P1_clean_inventory.py

streamlit:
	streamlit run streamlit_app.py

lint:
	black . data
