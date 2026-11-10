# Relationship choices

The relationship patterns describe different concerns and can coexist. Upstream/downstream describes dependency and influence, not necessarily network request direction. A team that serves an API is not automatically a cooperative supplier.

| Pattern | Evidence favoring it | Obligation or cost | Source pages |
|---|---|---|---|
| Shared Kernel | Teams benefit from a small shared model and can jointly maintain it | Define the shared model and code/schema subset; consult on changes and run both teams' tests | 251 |
| Customer/Supplier Development Teams | Upstream has a real incentive and planning mechanism to serve downstream needs | Negotiate commitments; put jointly developed downstream acceptance checks in upstream integration | 252–254 |
| Conformist | Upstream will not accommodate downstream, and adopting its model is acceptable | Accept dependence and constraints on local evolution rather than pretending to negotiate control | 255–256 |
| Anticorruption Layer | Integration is necessary but the local model must retain its own meaning | Maintain a semantic translation boundary and its tests; budget its complexity | 257–260 |
| Separate Ways | Integration adds less value than its cost | Keep independent solutions; colocated UI does not require shared domain logic | 261–262 |
| Open Host Service | Many consumers need a coherent, reusable access protocol | Maintain a stable service protocol; keep exceptional consumer needs from distorting it | 263 |
| Published Language | Parties need a documented interchange vocabulary | Specify shared meaning and translate to/from local models; syntax alone is insufficient | 264–265 |

An Open Host Service can expose a Published Language, while a consumer uses an ACL to protect its own model. A shared library with no joint model ownership is not automatically a Shared Kernel. Open Host Service does not imply public internet access, open source, or unauthenticated endpoints.

## Design a semantic translation

Original example: a warehouse calls an item “available” when it exists on a shelf; a rental application calls it “available” only when it is not reserved and has passed inspection. Copying the availability boolean imports a false promise. Specify which source facts can establish the local condition, what is unknown, and when the answer must be refreshed.

An ACL can combine a facade over foreign capabilities, an adapter for the desired interface, and translators for domain meaning. Keep foreign rules from becoming accidental local rules. Decide what to do when identities cannot be matched or a foreign status has no valid local equivalent. Translation need not be lossless, but any information loss that affects behavior must be explicit. (pp. 257–260.)

## Make the map truthful

Record context name, purpose, model vocabulary, concrete code/data scope, and actual owner. Record each connection's purpose, information, influence, ownership, and translation. When no established pattern fits, describe the observed relationship plainly. Include unknown or contradictory regions instead of assigning attractive names to them. Establish an accurate map before undertaking broad reorganization. (pp. 238–250.)

Within a context, continuous integration includes bringing concepts together through language and collaboration as well as merging implementation artifacts and running tests. Across contexts, choose the integration cadence that their contract requires rather than forcing one unified model. (pp. 242–243.)
