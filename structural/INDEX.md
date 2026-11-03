# Structural Engineering Index (Level 1 Parent)

This node serves as the parent index and router for all **Structural Engineering** design skills.
Shared structural rules (materials, load combinations, unit weights) are inherited from [`rules.json`](file:///d:/programming/construction%20design/structural/rules.json).

---

## Sub-Branch Navigation & Dispatch Table

| Sub-Branch | Directory | Primary Scope | Trigger Keywords |
| :--- | :--- | :--- | :--- |
| **Foundations & Substructure** | [`foundations/`](file:///d:/programming/construction%20design/structural/foundations/INDEX.md) | Isolated footings, combined footings, strap footings, raft foundations, piles | `footing`, `foundation`, `isolated`, `combined`, `strap`, `raft`, `mat`, `pile`, `soil` |
| **Vertical Elements** | [`vertical_elements/`](file:///d:/programming/construction%20design/structural/vertical_elements/INDEX.md) | Short columns, slender columns, biaxial columns, shear walls, retaining walls | `column`, `slender`, `buckling`, `shear wall`, `core wall`, `retaining wall` |
| **Horizontal Elements** | [`horizontal_elements/`](file:///d:/programming/construction%20design/structural/horizontal_elements/INDEX.md) | Solid slabs, flat slabs, ribbed slabs (hollow core), continuous beams | `slab`, `solid slab`, `flat slab`, `hollow block`, `ribbed`, `beam`, `drop beam`, `hidden beam` |

---

## Shared Rules Summary
- **Materials**: $f'_c$ / $f_{cu}$, $f_y$, density, and elasticity modulus.
- **Inheritance**: Sub-branches inherit material strengths and load factors automatically from [`rules.json`](file:///d:/programming/construction%20design/structural/rules.json).
