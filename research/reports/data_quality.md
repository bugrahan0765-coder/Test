# Data quality report

Source: HistData M1 (bid + assumed spread/2), store `/home/user/Test/data/bars`.

## US100

|   time |   bars |   median_close |   session_days |   median_session_coverage |   days_cov<90% |   days_with_open_bar |
|-------:|-------:|---------------:|---------------:|--------------------------:|---------------:|---------------------:|
|   2015 | 335257 |         4436.7 |            259 |                         1 |             11 |                  257 |
|   2016 | 341629 |         4530.2 |            258 |                         1 |              7 |                  258 |
|   2017 | 330380 |         5804   |            252 |                         1 |              7 |                  252 |
|   2018 | 348607 |         6966   |            258 |                         1 |             10 |                  258 |
|   2019 | 341335 |         7672.3 |            258 |                         1 |              9 |                  258 |
|   2020 | 339962 |        10364.5 |            258 |                         1 |              8 |                  256 |
|   2021 | 342946 |        14562.8 |            258 |                         1 |              7 |                  258 |
|   2022 | 342711 |        12417.9 |            258 |                         1 |              8 |                  258 |
|   2023 | 299289 |        14766.1 |            256 |                         1 |            117 |                  194 |
|   2024 | 340926 |        19016.5 |            259 |                         1 |             13 |                  259 |
|   2025 | 340493 |        22654.8 |            257 |                         1 |             10 |                  257 |

Intra-session gaps > 5 min: 308 (largest: 2020-03-09 13:35 0 days 05:05:00, 2023-03-15 18:00 0 days 05:01:00, 2023-02-28 17:00 0 days 03:01:00)

1-min |return| > 2%: 18 bars

Timezone check vs Dukascopy: best lag 0 min (corr of 1-min returns 1.000, n=29123); median HistData - Dukascopy mid = 0.43

## US500

|   time |   bars |   median_close |   session_days |   median_session_coverage |   days_cov<90% |   days_with_open_bar |
|-------:|-------:|---------------:|---------------:|--------------------------:|---------------:|---------------------:|
|   2015 | 281125 |         2067.1 |            259 |                     0.987 |             22 |                  248 |
|   2016 | 282913 |         2088.1 |            258 |                     0.982 |             31 |                  249 |
|   2017 | 222026 |         2434.3 |            252 |                     0.915 |            103 |                  225 |
|   2018 | 310381 |         2737.6 |            258 |                     0.992 |             23 |                  248 |
|   2019 | 308298 |         2911.8 |            258 |                     0.995 |             13 |                  257 |
|   2020 | 334202 |         3276   |            258 |                     1     |              8 |                  256 |
|   2021 | 333528 |         4295.8 |            258 |                     1     |              7 |                  256 |
|   2022 | 341611 |         4037.9 |            258 |                     1     |              8 |                  258 |
|   2023 | 291380 |         4311.7 |            256 |                     1     |            116 |                  205 |
|   2024 | 334338 |         5442.7 |            259 |                     1     |             12 |                  258 |
|   2025 | 339076 |         6210.9 |            257 |                     1     |             10 |                  257 |

Intra-session gaps > 5 min: 602 (largest: 2020-03-09 13:49 0 days 05:53:00, 2023-02-24 17:00 0 days 03:01:00, 2023-03-09 20:00 0 days 03:01:00)

1-min |return| > 2%: 17 bars

Timezone check vs Dukascopy: no Dukascopy reference

## GER40

|   time |   bars |   median_close |   session_days |   median_session_coverage |   days_cov<90% |   days_with_open_bar |
|-------:|-------:|---------------:|---------------:|--------------------------:|---------------:|---------------------:|
|   2015 | 211996 |        10981.2 |            253 |                     1     |              1 |                  234 |
|   2016 | 213764 |        10214.2 |            255 |                     1     |              1 |                  217 |
|   2017 | 206648 |        12477   |            247 |                     1     |              0 |                  170 |
|   2018 | 213273 |        12372.8 |            251 |                     1     |              1 |                  165 |
|   2019 | 325977 |        12113.7 |            258 |                     1     |              6 |                  255 |
|   2020 | 259840 |         9952.3 |            259 |                     1     |             37 |                  257 |
|   2021 | 187516 |         4087.3 |            258 |                     0.962 |             97 |                  256 |
|   2022 | 205728 |         3747.3 |            258 |                     0.977 |             33 |                  257 |
|   2023 | 159626 |         4274.1 |            255 |                     0.8   |            164 |                  245 |
|   2024 | 332439 |        18447.4 |            259 |                     1     |              1 |                  258 |
|   2025 | 335844 |        23713.9 |            258 |                     1     |              1 |                  258 |

Intra-session gaps > 5 min: 974 (largest: 2023-06-28 07:04 0 days 11:06:00, 2023-05-12 07:01 0 days 11:03:00, 2023-05-23 07:02 0 days 11:03:00)

1-min |return| > 2%: 29 bars

Timezone check vs Dukascopy: no Dukascopy reference

## XAUUSD

|   time |   bars |   median_close |   session_days |   median_session_coverage |   days_cov<90% |   days_with_open_bar |
|-------:|-------:|---------------:|---------------:|--------------------------:|---------------:|---------------------:|
|   2015 | 351666 |         1167.7 |            259 |                         1 |              2 |                  258 |
|   2016 | 353415 |         1256.9 |            258 |                         1 |              0 |                  258 |
|   2017 | 352360 |         1261.1 |            257 |                         1 |              0 |                  257 |
|   2018 | 353778 |         1263.4 |            258 |                         1 |              0 |                  258 |
|   2019 | 352628 |         1406.6 |            258 |                         1 |              1 |                  258 |
|   2020 | 354291 |         1774.2 |            258 |                         1 |              1 |                  258 |
|   2021 | 353386 |         1793.7 |            257 |                         1 |              0 |                  257 |
|   2022 | 354568 |         1804.6 |            258 |                         1 |              0 |                  258 |
|   2023 | 308752 |         1941.4 |            257 |                         1 |            115 |                  201 |
|   2024 | 355592 |         2381.1 |            259 |                         1 |              0 |                  259 |
|   2025 | 353951 |         3344.7 |            258 |                         1 |              1 |                  258 |

Intra-session gaps > 5 min: 250 (largest: 2023-03-10 14:00 0 days 03:01:00, 2023-05-17 16:00 0 days 03:01:00, 2023-07-13 16:00 0 days 03:01:00)

1-min |return| > 2%: 3 bars

Timezone check vs Dukascopy: no Dukascopy reference

## Findings and decisions (2026-10-06)

- **Timezone conversion verified** for US100: HistData vs Dukascopy 1-minute returns correlate 1.000 at lag 0
  (Dec 2025). Price level differs by ~0.4 points (spread assumption).
- **2023-03 .. 2023-07 incomplete** for US100, US500, XAUUSD (about half of each cash session missing).
  Excluded from all research via `harness.EXCLUDED_MONTHS`. To be refilled from another source if possible.
- **US500** 2016-08 and five months of 2017 have poor coverage: excluded.
- **GER40 is unreliable**: 2021-2023 prices (~4,000) are not the DAX (likely Euro Stoxx 50); 2015-2018 misses
  the Xetra open bar on a third of days. Only 2019-01..2020-11 and 2024+ are kept, so GER40 cannot be tested
  properly from this source. GER40 is dropped from the A1/A2 sister-instrument checks (US100 <-> US500 only).
- Spread is an assumed constant (US100 2.0, US500 0.6, GER40 1.5, XAUUSD 0.30) until FTMO calibration.
