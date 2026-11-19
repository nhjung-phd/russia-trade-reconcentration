# Final Full All-in-One v3.0 실행 가이드

## 가장 간단한 실행

1. Google Colab을 엽니다.
2. `notebooks/Russia_Trade_Full_AllInOne.ipynb`를 업로드합니다.
3. Colab Files에 아래 둘 중 하나를 업로드합니다.
   - `Russia_BACI_Lite_Dataset.zip` (권장)
   - `BACI_HS12_V202601.zip` (원자료)
4. `런타임 → 모두 실행(Run all)`을 누릅니다.
5. 마지막 셀에서 `Russia_Trade_Full_AllInOne_Outputs.zip`이 다운로드됩니다.

Google Drive에 데이터가 있으면 `/content/drive/MyDrive/BACI`도 자동 탐색합니다.

## 한 번에 생성되는 결과

### 기존 구조분석
- T1–T8 계열 결과
- HS6 통계검정
- R1–R8 강건성 결과
- 기존 구조분석 PNG 그래프
- `Russia_Trade_Master_Final_Results.xlsx`
- `Russia_Trade_Master_Robustness_Results.xlsx`

### 추가 패널분석
- P1 FE/RE
- P2 Hausman
- P3 HS6 product-FE event profile
- P4 PPML-HDFE
- FE/RE/PPML 논문용 계수 그래프
- balanced pre/post 그래프
- event-profile 그래프
- `Russia_Trade_Panel_Robustness_Results.xlsx`
- `publication/Russia_Trade_Panel_Publication_Tables.xlsx`

### 최종 감사
- `FULL_OUTPUT_INVENTORY.csv`
- `FULL_ANALYSIS_METADATA.json`

## 출력 폴더

```text
outputs/
├── tables/              # 기존 + P1~P4 전체 CSV
├── figures/             # 기존 + event-profile PNG
├── publication/
│   ├── tables/          # 패널 논문용 요약표
│   ├── figures/         # 패널 논문용 그림
│   ├── all_tables/      # 기존 + 패널 CSV 전체 모음
│   └── all_figures/     # 기존 + 패널 PNG 전체 모음
├── Russia_Trade_Master_Final_Results.xlsx
├── Russia_Trade_Master_Robustness_Results.xlsx
├── Russia_Trade_Panel_Robustness_Results.xlsx
├── FULL_OUTPUT_INVENTORY.csv
└── FULL_ANALYSIS_METADATA.json
```

## 해석 주의
패널모형은 구조적 변화의 강건성 검증입니다. 2022년에는 전쟁·제재·기업철수·에너지·결제·물류 변화가 동시 발생하므로 FE/RE/PPML 결과를 제재의 순수 인과효과로 해석하지 않습니다.
