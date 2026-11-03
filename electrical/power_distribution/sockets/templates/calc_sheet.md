# ELECTRICAL DESIGN CALCULATION NOTE
## SMALL POWER BRANCH CIRCUITS & APPLIANCE FEEDS

---

### 1. General Design Parameters
- **Active Code**: {{code_used}}
- **Nominal System Voltage**: {{voltage_v}} V (1-Phase / 3-Phase)
- **Standard Branch Circuit Breaker**: {{std_breaker}} A
- **Standard Branch Conductor**: {{std_cable}} mm$^2$ Cu/XLPE
- **Maximum Outlets per General Circuit**: {{max_outlets}} Sockets
- **Total Branch Circuits**: **{{total_circuits}} Circuits**
- **Total Connected Load**: **{{total_kw}} kW ({{total_kva}} kVA)**

---

### 2. Branch Circuit Schedule
| Circuit Tag | Description | Outlets | Connected Load (W) | Breaker (A) | Cable (mm$^2$) | Voltage Drop (%) | Status |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{circuit_table_rows}}

---

### 3. Cross-Discipline Coordination Notices (MEP Interfaces)
*The following requirements from Mechanical / Plumbing have been integrated into this electrical design:*
{{coordination_notices_list}}

---

### 4. Overall Design Verification
- **Voltage Drop Compliance**: All branch circuits $\le 3.0\%$ $\longrightarrow$ **[PASS]**
- **Overcurrent Protection**: All circuit breakers $\ge$ design current ($I_n \ge I_b$) $\longrightarrow$ **[PASS]**
- **Overall Status**: **{{overall_status}}**
