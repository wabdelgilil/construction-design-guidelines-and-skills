# Mechanical Plumbing Drainage & Water Supply Calculation Sheet

## 1. Project & Governing Codes
- **Discipline**: Mechanical Engineering (Plumbing & Sanitation)
- **Governing Codes**: {{code_used}} (SBC 701 / IPC)
- **Facility / Building Tag**: {{building_tag}}

---

## 2. Sanitary Drainage Sizing (DFU)
| Drainage Parameter | Sized Value | Design Basis | Status |
| :--- | :--- | :--- | :--- |
| Total Drainage Fixture Units ($DFU$) | {{total_dfu}} DFU | Fixture count load summation | **CALCULATED** |
| Vertical Soil & Waste Stack | **{{soil_stack_in}}" ({{soil_stack_mm}} mm)** | Capacity up to 500 DFU | **SAFE** |
| Horizontal Main Building Drain | **{{drain_in}}" ({{drain_mm}} mm)** | Gravity outflow capacity | **SAFE** |
| Minimum Invert Slope Required | {{drain_slope}}% ({{drain_fall}} mm/m) | Self-cleansing velocity $\ge 0.6$ m/s | **COMPLIANT** |

---

## 3. Water Supply Demand & Booster Pump Sizing
| Parameter | Sized Value | Unit | Engineering Reference |
| :--- | :--- | :--- | :--- |
| Water Supply Fixture Units ($WSFU$) | {{total_wsfu}} | WSFU | Hunter's Curve Loading |
| Peak Simultaneous Flow Rate | {{flow_gpm}} GPM ({{flow_lps}} L/s) | Flow | Standard Flush-Tank System |
| Static Suction & Lift Head | {{static_head}} | m | Geometric elevation difference |
| Estimated Pipe & Fitting Friction | {{friction_head}} | m | Equivalent length resistance |
| Required Minimum Residual Pressure | {{residual_pressure}} | m | 1.5 bar at highest outlet |
| **Total Pump Design Head** | **{{total_head_m}} m ({{total_head_bar}} bar)** | Head | Delivery gauge pressure |
| **Selected Booster Motor Power** | **{{pump_kw}} kW (Duty)** | Power | Standard Twin Set (1D + 1S) |

---

## 4. Multi-Discipline Coordination Interface
| Interface Target | Engineering Specification | Responsible Discipline |
| :--- | :--- | :--- |
| **Electrical Power** | Dedicated Feeder: {{pump_voltage}}V, FLC = {{pump_current}}A, MCB = {{pump_mcb}}A | Electrical |
| **Dry-Run Interlock** | Float switch in water tank connected to pump controller | Electrical & Controls |
| **Water Heater Isolation** | 20A DP Switch with Neon @ +1600mm AFF outside shower zone | Electrical & Architecture |
| **Main Drain Sleeve** | {{sleeve_drain}} through Grade Beam (mid-depth, >200mm from C1) | Civil / Structural |
| **Potable Supply Sleeve** | {{sleeve_potable}} through Basement Retaining Wall with Link-Seal | Civil / Structural |

---

## 5. Mandatory Interdisciplinary Action Items
{{coordination_checklist}}
