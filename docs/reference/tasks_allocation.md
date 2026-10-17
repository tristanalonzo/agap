# Task allocation (copied from the team Drive)

**Team A: Model Training & Delivery (FEUDO & MANIMTIM)**

\- Train the classification model in Google Colab on the .h5 IR dataset.

\- Verify input tensor specs: shape \[1, 3, 128, 128\], pixel values
normalized to \[0.0,1.0\].

\- Export and deliver agap_tc_classifier.onnx to the repository under
/backend/models/.

\- Provide a benchmark test script (test_inference.py) verifying
predicted labels and probabilities.

**Team B: Frontend & Backend Development (ALONZO, RANESES, MARCAIDA)**

**- Backend:** Build the FastAPI service implementing the schema above
with mock outputs for cyclone_inference until the ONNX file is ready.

**- Backend:** Implement the scraping function for PAGASA NCR-PRSD
rainfall warnings.

**- Backend:** Host qc_shelters.geojson and integrate the Haversine
distance formula to resolve the nearest shelter.

**- Frontend:** Adapt the single-page prototype mockup into the
production client shell.

**- Frontend:** Implement MapLibre/Leaflet with the PMTiles protocol to
stream NOAH flood polygons bounded to Quezon City.

**- Frontend:** Connect client state to the /api/v1/telemetry/assess
endpoint with pull-to-refresh and 60-second auto-polling.

**Final: Model Integration (MANIMTIM & ALONZO)**
