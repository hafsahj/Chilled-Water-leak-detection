# Data

Raw data files are **not** included in this repo. Place your own copies here (or point `CW_DATA_DIR` at wherever they live) with this schema — all at 2-hourly resolution for calendar year 2024:

| File | Columns | Notes |
|---|---|---|
| `weather_data_2024.csv` | `Timestamp`, `values` | Heat index; `values` gets renamed to `heatIndex` on load. |
| `makeup_flow_2024.csv` | `Timestamp`, `values` | Instantaneous makeup-water flow; renamed to `makeupFlow`. Used in Approach 2. |
| `makeup_data_2024.csv` | `Timestamp`, `values` | Daily makeup-flow totalizer (MFDT); renamed to `MFDT` in Approach 2. Approach 1 merges this same file in as `makeupFlow` — see the note in that notebook's load cell before assuming the two notebooks are using an equivalent signal under that name. |
| `summary_data_2024.csv` | `Building, Meter, Timestamp, Flow, DeltaT, MixTemp, StationCO` (no header row) | Per-building meter readings. |

None of the above are checked into git — see the top-level README for why.
