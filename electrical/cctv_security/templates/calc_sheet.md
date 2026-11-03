# CCTV Video Surveillance & NVR Storage Sizing Calculation Note

## 1. Project & Governing Standards
- **Discipline**: Electrical Engineering (Low Current / ELV - Security Systems)
- **Governing Standards**: {{standard_used}}
- **Project Designation**: {{project_name}}
- **Retention Period Mandate**: {{recording_days}} Days Continuous Recording

---

## 2. Camera Optical Selection & DORI Coverage Schedule
| Tag | Location | Model / Type | Resolution | Target DORI | Distance (m) | Lens Focal ($f$) | HFOV ($^\circ$) | ID Reach (m) | Bandwidth (Mbps) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{{camera_table_rows}}

---

## 3. Bandwidth & NVR Storage Sizing Analysis
| Parameter | Sized Value | Engineering Basis | Status |
| :--- | :--- | :--- | :--- |
| Total Camera Quantities | {{total_cameras}} Cameras | IP Surveillance Grid | Verified |
| Video Compression Standard | H.265 / Smart Stream | 20 FPS Main Stream | High Efficiency |
| Cumulative Incoming Bandwidth | {{total_bandwidth}} Mbps | Network Throughput | **OK** |
| Net Raw Video Storage | {{net_storage_tb}} TB | Sized for {{recording_days}} days | Calculated |
| **Gross Storage with Redundancy** | **{{gross_storage_tb}} TB** | **{{raid_config}} Configuration** | **SECURE** |
| Hard Drive Specification | {{hdd_count}}x {{hdd_capacity}} TB SATA | Enterprise 24/7 Surveillance | **SIZED** |
| **Specified NVR System** | **{{nvr_channels}}-Channel NVR ({{nvr_bays}} Bays)** | 4K Embedded Linux NVR | **COMPLIANT** |

---

## 4. PoE Network Switch Power Budget
| Parameter | Value | Standard Requirement | Compliance |
| :--- | :--- | :--- | :--- |
| Total Connected Camera PoE Load | {{poe_raw}} W | Sum of IEEE 802.3af/at loads | Calculated |
| Safety Headroom Multiplier | 1.25 | Continuous switch loading margin | NFPA / IEEE |
| **Minimum Required Switch PoE Budget** | **{{poe_budget}} Watts** | Dedicated Managed PoE+ Switch | **VERIFIED** |

---

## 5. Mandatory Interdisciplinary Coordination Checklist
{{coordination_checklist}}
