# Foundations & Substructure Index (Level 2 Sub-Branch)

This node serves as the sub-branch router for all **Foundations and Geotechnical Concrete Elements**.
Shared foundation parameters (soil bearing capacity, minimum cover against earth, blinding concrete) are inherited from [`rules.json`](file:///d:/programming/construction%20design/structural/foundations/rules.json).

---

## Foundation Skills Navigation & Dispatch Table

| Skill / Element | Directory | Scope | Trigger Keywords |
| :--- | :--- | :--- | :--- |
| **Isolated Footing** | [`isolated_footing/`](file:///d:/programming/construction%20design/structural/foundations/isolated_footing/SKILL.md) | Pad footing under single concentric/eccentric column | `isolated footing`, `pad footing`, `single column footing`, `spread footing` |
| **Combined Footing** | [`combined_footing/`](file:///d:/programming/construction%20design/structural/foundations/combined_footing/SKILL.md) | Footing supporting two or more adjacent columns | `combined footing`, `two columns footing`, `rectangular combined` |
| **Strap / Cantilever Footing** | [`strap_footing/`](file:///d:/programming/construction%20design/structural/foundations/strap_footing/SKILL.md) | Property line / boundary column with strap beam to interior footing | `strap footing`, `property line footing`, `cantilever footing`, `strap beam` |
| **Raft / Mat Foundation** | [`raft_foundation/`](file:///d:/programming/construction%20design/structural/foundations/raft_foundation/SKILL.md) | Continuous slab foundation under entire building | `raft`, `mat foundation`, `flat plate raft`, `raft with beams` |
| **[Specialized] Machine Foundation** | [`machine_foundation/`](file:///d:/programming/construction%20design/structural/foundations/machine_foundation/SKILL.md) | Dynamic machine foundation under heavy rotating/reciprocating equipment | `machine foundation`, `factory`, `vibration`, `generator base`, `turbine base`, `dynamic analysis` |
| **Piles & Pile Caps** | [`piles/`](file:///d:/programming/construction%20design/structural/foundations/piles/INDEX.md) | Driven/bored piles, skin friction, pile caps using strut-and-tie | `pile`, `pile cap`, `bored pile`, `deep foundation`, `drilled shaft` |

---

## Shared Rules Summary
- **Geotechnical**: Default allowable soil bearing capacity $q_{\text{all}} = 150 - 200\text{ kPa}$.
- **Durability**: Minimum concrete cover cast against earth $= 75\text{ mm}$ (SBC/ACI) or $70\text{ mm}$ (ECP).
- **Inheritance**: Subordinate leaf skills inherit foundation rules automatically.
