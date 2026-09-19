# Master graph schema

## Node classes
Person, EmailAddress, PhoneNumber, Organization, Address, Location, Flight, Airport, Document, Event, Claim, Citation.

## Evidence rule
Every non-derived relationship must retain enough provenance to identify the upstream repository/file/record.

## Semantics
Do not collapse semantically different relationships:
- HAS_EMAIL is ownership/association of an address with a person in a source.
- SENT_EMAIL_TO is an observed communication-metadata relation.
- CO_MENTIONED_WITH is textual co-occurrence only.
- TRAVELED_WITH is co-presence in a flight record.
- ASSOCIATED_WITH is reserved for sources that explicitly assert an association.

No relationship type alone implies wrongdoing.

## Identity resolution
Deterministic exact normalization is applied first. Fuzzy person merges must be written to an explicit review mapping and must never silently overwrite source identities.
