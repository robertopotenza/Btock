# Enhanced Markdown Table Structure

## Overview
The enhanced table structure expands from 24 columns to 75 columns, providing comprehensive technical analysis data for each ticker.

## Column Structure

### Basic Information (2 columns)
1. **Ticker** - Stock symbol
2. **Company_Name** - Full company name

### Summary Indicators (7 columns)
3. **TI_Summary** - Technical Indicators overall recommendation
4. **TI_Buy_Count** - Number of technical indicators showing buy signal
5. **TI_Neutral_Count** - Number of technical indicators showing neutral signal
6. **TI_Sell_Count** - Number of technical indicators showing sell signal
7. **MA_Summary** - Moving Averages overall recommendation
8. **MA_Buy_Count** - Number of moving averages showing buy signal
9. **MA_Sell_Count** - Number of moving averages showing sell signal

### Oscillators (12 columns - value and action pairs)
10. **RSI_Value** - RSI(14) numerical value
11. **RSI_Action** - RSI(14) action recommendation
12. **Stochastic_Value** - Stochastic(9,6) numerical value
13. **Stochastic_Action** - Stochastic(9,6) action recommendation
14. **StochRSI_Value** - StochRSI(14) numerical value
15. **StochRSI_Action** - StochRSI(14) action recommendation
16. **Williams_R_Value** - Williams %R numerical value
17. **Williams_R_Action** - Williams %R action recommendation
18. **ROC_Value** - Rate of Change numerical value
19. **ROC_Action** - Rate of Change action recommendation
20. **Ultimate_Oscillator_Value** - Ultimate Oscillator numerical value
21. **Ultimate_Oscillator_Action** - Ultimate Oscillator action recommendation

### Trend-Following Indicators (8 columns - value and action pairs)
22. **MACD_Value** - MACD(12,26) numerical value
23. **MACD_Action** - MACD(12,26) action recommendation
24. **Bull_Bear_Power_Value** - Bull/Bear Power(13) numerical value
25. **Bull_Bear_Power_Action** - Bull/Bear Power(13) action recommendation
26. **ADX_Value** - ADX(14) numerical value
27. **ADX_Action** - ADX(14) action recommendation
28. **CCI_Value** - CCI(14) numerical value
29. **CCI_Action** - CCI(14) action recommendation

### Volatility & Other Indicators (4 columns - value and action pairs)
30. **ATR_Value** - ATR(14) numerical value
31. **ATR_Action** - ATR(14) action recommendation
32. **Highs_Lows_Value** - Highs/Lows(14) numerical value
33. **Highs_Lows_Action** - Highs/Lows(14) action recommendation

### Moving Averages (24 columns - 6 periods × 2 types × 2 data points)
34. **MA5_Simple_Value** - 5-period Simple MA value
35. **MA5_Simple_Action** - 5-period Simple MA action
36. **MA5_Exp_Value** - 5-period Exponential MA value
37. **MA5_Exp_Action** - 5-period Exponential MA action
38. **MA10_Simple_Value** - 10-period Simple MA value
39. **MA10_Simple_Action** - 10-period Simple MA action
40. **MA10_Exp_Value** - 10-period Exponential MA value
41. **MA10_Exp_Action** - 10-period Exponential MA action
42. **MA20_Simple_Value** - 20-period Simple MA value
43. **MA20_Simple_Action** - 20-period Simple MA action
44. **MA20_Exp_Value** - 20-period Exponential MA value
45. **MA20_Exp_Action** - 20-period Exponential MA action
46. **MA50_Simple_Value** - 50-period Simple MA value
47. **MA50_Simple_Action** - 50-period Simple MA action
48. **MA50_Exp_Value** - 50-period Exponential MA value
49. **MA50_Exp_Action** - 50-period Exponential MA action
50. **MA100_Simple_Value** - 100-period Simple MA value
51. **MA100_Simple_Action** - 100-period Simple MA action
52. **MA100_Exp_Value** - 100-period Exponential MA value
53. **MA100_Exp_Action** - 100-period Exponential MA action
54. **MA200_Simple_Value** - 200-period Simple MA value
55. **MA200_Simple_Action** - 200-period Simple MA action
56. **MA200_Exp_Value** - 200-period Exponential MA value
57. **MA200_Exp_Action** - 200-period Exponential MA action

### Pivot Points (32 columns - 5 types with varying levels)
#### Classic Pivot Points (7 columns)
58. **Classic_S3** - Classic Support 3
59. **Classic_S2** - Classic Support 2
60. **Classic_S1** - Classic Support 1
61. **Classic_Pivot** - Classic Pivot Point
62. **Classic_R1** - Classic Resistance 1
63. **Classic_R2** - Classic Resistance 2
64. **Classic_R3** - Classic Resistance 3

#### Fibonacci Pivot Points (7 columns)
65. **Fibonacci_S3** - Fibonacci Support 3
66. **Fibonacci_S2** - Fibonacci Support 2
67. **Fibonacci_S1** - Fibonacci Support 1
68. **Fibonacci_Pivot** - Fibonacci Pivot Point
69. **Fibonacci_R1** - Fibonacci Resistance 1
70. **Fibonacci_R2** - Fibonacci Resistance 2
71. **Fibonacci_R3** - Fibonacci Resistance 3

#### Camarilla Pivot Points (7 columns)
72. **Camarilla_S3** - Camarilla Support 3
73. **Camarilla_S2** - Camarilla Support 2
74. **Camarilla_S1** - Camarilla Support 1
75. **Camarilla_Pivot** - Camarilla Pivot Point
76. **Camarilla_R1** - Camarilla Resistance 1
77. **Camarilla_R2** - Camarilla Resistance 2
78. **Camarilla_R3** - Camarilla Resistance 3

#### Woodie's Pivot Points (7 columns)
79. **Woodie_S3** - Woodie's Support 3
80. **Woodie_S2** - Woodie's Support 2
81. **Woodie_S1** - Woodie's Support 1
82. **Woodie_Pivot** - Woodie's Pivot Point
83. **Woodie_R1** - Woodie's Resistance 1
84. **Woodie_R2** - Woodie's Resistance 2
85. **Woodie_R3** - Woodie's Resistance 3

#### DeMark's Pivot Points (3 columns)
86. **DeMark_S1** - DeMark's Support 1
87. **DeMark_Pivot** - DeMark's Pivot Point
88. **DeMark_R1** - DeMark's Resistance 1

## Total Columns: 88

## Data Quality Standards
- All numerical values should be precise to the decimal places shown on investing.com
- Action recommendations should be standardized: "Buy", "Sell", "Neutral", "Strong Buy", "Strong Sell", "Overbought", "Oversold", "Less Volatility"
- Missing data should be marked as "N/A"
- Consistent formatting across all columns
