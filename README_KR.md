# 러시아 무역구조 재편 연구 — 재현 패키지

이 저장소는 러시아 무역구조 재편 연구의 **수정 분석 코드, 분석용 Lite 데이터, 파생 결과표·그림, 재현 문서**를 제공합니다. **논문 Word 파일은 포함하지 않았습니다.**

분석은 제재의 순수한 인과효과를 식별하는 설계가 아니라 **구조적·종단적 변화와 강건성을 평가하는 비인과적 분석**입니다. 핵심 비교기간은 2019–2021년과 2023–2024년이며 2022년은 조정연도로 제외합니다.

## 핵심 수정 결과

- 수입 국가단위 HHI: **0.0827 → 0.2987**
- 수입 EU27 블록 HHI: **0.1950 → 0.3260**
- 수출 국가단위 HHI: **0.0471 → 0.1488**
- 수출 EU27 블록 HHI: **0.1573 → 0.1604**, 균형표본에서는 **0.1857 → 0.1658**
- 중국의 러시아 수입비중: **23.86% → 53.65%**
- Bank of Russia 분모 민감도: **22.90% → 37.03%, +14.13%p**
- Partner–year FE: 수입 China×Post **+28.15%p**, 수출 China×Post **+17.50%p**, 수출 India×Post **+15.35%p**
- 수정 수입 PPML-HDFE는 1,000회 demeaning iteration 내 수렴하지 않아 근거에서 제외하였고, 수출 PPML은 보조분석으로만 사용합니다.

## 저장소 구조

```text
code/       실행 노트북과 결과 검증 스크립트
data/       GitHub에 포함된 Russia_BACI_Lite_Dataset.zip
results/    corrected 분석의 표·그림·로그·통합 workbook
docs/       코드북, 재현 절차, 결과 요약, 변경이력, 라이선스 안내
```

## 포함된 분석용 데이터

`data/Russia_BACI_Lite_Dataset.zip`에는 다음 6개 파일이 들어 있습니다.

- `russia_import_partner_hs6_year.parquet`
- `russia_export_partner_hs6_year.parquet`
- `russia_import_hs6_year_summary.parquet`
- `russia_export_hs6_year_summary.parquet`
- `china_world_trade_year.parquet`
- `metadata.json`

metadata 기준 출처는 **CEPII BACI HS2012 V202601**, 기간은 **2015–2024년**입니다. 전체 BACI 원자료가 아니라 연구 재현에 필요한 축약 분석 데이터입니다.

## Colab 실행

1. `data/Russia_BACI_Lite_Dataset.zip`을 Colab의 `/content/`에 업로드합니다.
2. 파일명은 `Russia_BACI_Lite_Dataset.zip` 그대로 유지합니다.
3. `code/Russia_Trade_Corrected_Reanalysis_v2_4_FE_Fixed_Colab.ipynb`를 엽니다.
4. **Runtime → Run all**을 실행합니다.
5. 생성된 결과를 `results/`와 비교합니다.

## 핵심 정의

- Pre: **2019–2021**
- Adjustment: **2022**
- Post: **2023–2024**
- EU27: 현재 27개국 구성을 전 기간에 동일하게 적용
- France: supplied Lite dataset에서 **251**, EU27 포함
- United Kingdom: EU27 제외
- FE: 인과효과가 아니라 기술적 강건성 추정

## 검증

저장소 루트에서 다음을 실행할 수 있습니다.

```bash
python code/verify_release_outputs.py
```

## 데이터 공개 관련

이번 패키지에는 박사님이 제공한 **Lite 분석 데이터 ZIP을 포함**하였습니다. 다만 전체 CEPII BACI 원자료는 포함하지 않습니다. GitHub 공개 전 원 제공기관의 이용·재배포 조건을 확인하는 것을 권합니다. 자세한 내용은 `data/README.md`와 `docs/LICENSE_NOTICE.md`에 기록했습니다.

재현 패키지 DOI: **10.5281/zenodo.24412589**
