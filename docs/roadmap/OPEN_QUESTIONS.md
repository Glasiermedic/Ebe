# Ebe Open Questions

These questions are not approved decisions.

## Retrieval and query

1. Should `RetrievalResult` contain serialized dictionaries, ORM objects, or internal evidence records?
2. Should unresolved phrases reject a query or allow a partial result with warnings?
3. What HTTP behavior should replace the current multi-entity 501?
4. Should retrieval-planning intent and language-understanding intent be represented by the same model?
5. How should possessives be parsed, such as `Laura's first date`?
6. How should ambiguous aliases be presented to a client for disambiguation?
7. What is the first supported graph intersection: person-person, person-place, or generic entity sets?
8. When should constrained semantic search begin: after no exact result or after too few exact results?
9. What minimum semantic score is acceptable for fallback?
10. Should the API expose every fallback attempt or only the successful strategy?

## Ranking

1. How should importance interact with exact graph matches?
2. Should recency influence personal-memory recall or only explicitly temporal requests?
3. How should user-confirmed memories rank against automatically extracted memories?
4. How should contradictions and duplicate candidates be penalized?

## Time

1. Which timestamp is authoritative when `remembered_at` is absent?
2. How should uncertain dates be stored and queried?
3. Which timezone applies to a memory without an explicit location?
4. How should recurring events be represented?

## Privacy and family use

1. Who owns a memory involving several family members?
2. Can a person restrict a memory that another user created?
3. How are private, shared, and family-visible memories separated?
4. How are embeddings filtered so authorization cannot be bypassed?
5. What deletion behavior applies to derived embeddings and extracted entities?

## Biblical context

1. Is biblical enrichment enabled per user, per query, or per memory?
2. Which translations are permitted?
3. Should Ebe retrieve passages from a curated corpus?
4. How should differing theological interpretations be represented?
5. What contexts should suppress biblical enrichment for safety or appropriateness?

## Documentation

1. Confirm whether EBE-008 should remain approved or be rewritten as a proposed historical interpretation.
2. Confirm the canonical location of `project_snapshot.sh`.
3. Add real Git hashes and original completion dates where available.
