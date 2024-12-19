#target_url="https://www.ai.gov/ai-use-case-inventories/"
#output_md5file="data/ai_gov_md5hash.csv"

compute:
	python src/P0_compute_checksums.py
	python src/P1_clean_inventory.py
	python src/P2_compute_summary.py
	python src/P3_compute_embeddings.py
	python src/P4_precompute_viz_data.py

streamlit:
	streamlit run streamlit_app.py

lint:
	black . data
