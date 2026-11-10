---
name: api-and-interface-design
description: Guides stable API and interface design. Use when designing APIs, module boundaries, or any public interface. Use when creating REST or GraphQL endpoints, defining type contracts between modules, or establishing boundaries between frontend and backend.
---

# API and Interface Design

## Overview

Design stable, well-documented interfaces that are hard to misuse. Good interfaces make the right thing easy and the wrong thing hard. This applies to REST APIs, GraphQL schemas, module boundaries, component props, and any surface where one piece of code talks to another.

## When to Use

- Designing new API endpoints
- Defining module boundaries or contracts between teams
- Creating component prop interfaces
- Establishing database schema that informs API shape
- Changing existing public interfaces

## Core Principles

### Hyrum's Law

> With a sufficient number of users of an API, all observable behaviors of your system will be depended on by somebody, regardless of what you promise in the contract.

This means: every public behavior — including undocumented quirks, error message text, timing, and ordering — becomes a de facto contract once users depend on it. Design implications:

- **Be intentional about what you expose.** Every observable behavior is a potential commitment.
- **Don't leak implementation details.** If users can observe it, they will depend on it.
- **Plan for deprecation at design time.** See `deprecation-and-migration` for how to safely remove things users depend on.
- **Tests are not enough.** Even with perfect contract tests, Hyrum's Law means "safe" changes can break real users who depend on undocumented behavior.

### The One-Version Rule

Avoid forcing consumers to choose between multiple versions of the same dependency or API. Diamond dependency problems arise when different consumers need different versions of the same thing. Design for a world where only one version exists at a time — extend rather than fork.

### Pure Production APIs & Inversion of Control (The Anti-Backdoor Principle)

Never pollute production interfaces with test-only backdoors, bypass methods, or conditional compilation switches (`#[cfg(test)]`, `#ifdef`, `@VisibleForTesting`, or feature-gated shortcuts).

- **The Smell of Test Backdoors**: Introducing test-only methods (e.g. `new_for_test()`, `set_internal_state()`, or `mock_backend()`) directly into production modules breaks encapsulation, bloats production binaries, creates untested production branches, and risks accidental invocation in production environments.
- **Inversion of Control (IoC) Seams**: When a component requires swappable collaborators, simulated clock/time, or alternative backends for testing:
  - Expose a clean, first-class dependency injection seam (such as accepting an interface/trait, factory, strategy struct, or closure).
  - Design the standard production entry points (e.g. `new()`, `default()`, `runtime_from_configuration()`) as thin delegates that provide the canonical production collaborator to the configurable seam.
  - Both production and test paths exercise the exact same orchestration code.
- **Visibility Bounded by Signature**: An interface method's visibility must never exceed the visibility of the types in its signature. For example, a method accepting a crate-private or package-private configuration/trait must be crate-private (`pub(crate)`), never public (`pub`). Leaking private types across public boundaries triggers compiler warnings and destabilizes the public API contract.
- **Capability Colocation Principle (Anti-Dislocation Rule)**: Define an abstraction, trait, port, or strategy interface in the **domain capability module** that it governs, *never* in the consumer/caller module that happens to trigger the need for it. The consumer should import or re-export it. Defining a persistence strategy inside the dispatcher or client creates feature envy and splits domain cohesion.
- **Zero Phantom Seams**: Every newly added seam or factory must be wired to its live production caller from inception. Do not introduce configurable seams without connecting the canonical production path.
- **Zero Broken Windows for Touched Files**: When refactoring or adding functionality to a file that contains legacy `#[cfg(not(test))]` guards or test backdoors, builders must identify and purge those legacy guards if existing test fixtures (e.g. mock singletons or temporary filesystems) already support pure execution.
- **Dead Code Suppression Policy**: `#[allow(dead_code)]` must never be used to silence warnings on test-only helpers, abandoned code, or orphaned seams. The sole permitted usage is temporary scaffolding in intermediate slices of an approved stacked PR stack per the *Stacked PR Scaffolding Exception* (`pub(crate)` encapsulation, explicit `// Scaffolding: consumed in Slice <N> (PR #<ID>)`, authentic unit test coverage, and mandatory removal in the terminal PR).


### 1. Contract First

Define the interface before implementing it. The contract is the spec — implementation follows.

**For HTTP APIs**: Define the OpenAPI/JSON schema before writing handlers.
**For TypeScript**: Define types/interfaces before writing functions.
**For components**: Define the Props interface before writing JSX.

```typescript
// Good: Contract defined first, clear and minimal
interface CreateUserRequest {
  email: string;
  name: string;
  // Don't expose internal fields like role, permissions, etc.
}

interface UserResponse {
  id: string;
  email: string;
  name: string;
  createdAt: string; // ISO 8601 string, not Date object
}
```

### 2. Information Hiding (Parnas's Principle)

A module should hide:
- **How** it stores data (database schema, in-memory structures)
- **How** it computes results (algorithms, third-party libraries)
- **Which** external services it calls

A module should expose only:
- **What** operations it supports
- **What** inputs it requires
- **What** guarantees it makes

If changing an internal implementation detail requires changing the caller, the interface leaked.

### 3. Make Illegal States Unrepresentable

Use the type system to prevent callers from passing invalid combinations of arguments.

```typescript
// Bad: Boolean flags allow contradictory states
interface FetchOptions {
  includeDeleted?: boolean;
  onlyDeleted?: boolean; // What if both are true?
}

// Good: Union type makes invalid states impossible
type DeletionFilter = 'active-only' | 'including-deleted' | 'deleted-only';
```

### 4. Idempotency

State-changing endpoints must be safe to retry. Network failures, client timeouts, and user double-clicks mean operations will be re-sent.

- **`GET`, `HEAD`, `OPTIONS`**: Naturally safe and idempotent (RFC 9110 §9.2.1-2).
- **`PUT`, `DELETE`**: Naturally idempotent (repeating achieves the same final state).
- **`POST`, `PATCH`**: NOT naturally idempotent. Implement explicit idempotency keys for any non-idempotent operation that creates records or triggers side effects (payments, orders, messages).

#### Idempotency Key Design

1. Require an `Idempotency-Key` HTTP header (or parameter) on critical `POST` endpoints.
2. Store the key, request hash, status (`processing` / `completed`), and the cached response atomically.
3. If the same key arrives with the **same** request payload while `processing`: return `409 Conflict` or poll/wait.
4. If the same key arrives with the **same** request payload after `completed`: return the **cached response** without re-executing.
5. If the same key arrives with a **different** request payload: return `422 Unprocessable Entity` (key reuse with mismatched intent).
6. Set a TTL on idempotency keys (typically 24–72 hours).

```typescript
// Good: Explicit idempotency key on side-effecting operations
interface ChargeRequest {
  idempotencyKey: string; // Client-generated UUID v4
  amountCents: number;
  currency: string;
  customerId: string;
}
```

### 5. Tolerant Reader (Postel's Law)

> Be conservative in what you send, be liberal in what you accept.

Applied to API evolution:
- **Accept extra fields** without erroring (allows clients to send new data to old servers).
- **Send only agreed-upon fields** (don't leak internal state).
- **Never change the type** of an existing field.
- **Never remove a field** without a deprecation cycle.
- **Make new fields optional** on input, with sensible defaults.

### 6. Semantic Versioning for APIs

Follow semver rules:
- **MAJOR**: Incompatible API changes (removing fields, changing types, new required parameters).
- **MINOR**: Backward-compatible new functionality (new endpoints, new optional fields).
- **PATCH**: Backward-compatible bug fixes (fixing calculation, performance improvement).

Prefer **evolution over versioning**: add optional fields, deprecate old ones, avoid URL-path version bumps (`/v2/`) unless the entire domain model has changed fundamentally.

---

## API Design Workflow

### Step 1: Identify Consumers and Use Cases
Answer before writing any types:
- Who calls this? (Frontend, mobile, third party, internal service)
- What is the user goal? (Not "what database table does this map to")
- What is the expected call frequency and volume?
- What happens when this fails?

### Step 2: Draft the Contract
Write the type definitions or schema first:

```typescript
// Define inputs
interface UpdateProfileInput {
  displayName?: string;
  bio?: string;
}

// Define outputs
interface UpdateProfileResult {
  success: boolean;
  user: PublicUser;
}

// Define errors explicitly
type UpdateProfileError =
  | { code: 'NOT_FOUND'; message: string }
  | { code: 'VALIDATION_ERROR'; fields: Record<string, string> }
  | { code: 'UNAUTHORIZED'; message: string };
```

### Step 3: Check for Anti-Patterns
Review the contract against common mistakes (see table below).

### Step 4: Implement Behind the Interface
Write the implementation. If the implementation requires changing the interface, go back to Step 2 and assess whether the change makes the interface worse.

### Step 5: Document with Examples
Every endpoint/interface must have:
- At least one realistic example of inputs and outputs
- Clear descriptions of error cases and their HTTP status codes
- Preconditions and postconditions

---

## REST API Conventions

### URL Structure
```
GET    /api/resources          # List (paginated)
POST   /api/resources          # Create
GET    /api/resources/:id      # Read single
PATCH  /api/resources/:id      # Partial update
PUT    /api/resources/:id      # Full replacement (rarely what you want)
DELETE /api/resources/:id      # Delete
```

- Use plural nouns for collections: `/api/users`, not `/api/user`
- Use kebab-case for multi-word paths: `/api/order-items`, not `/api/orderItems`
- Nest resources only for true parent-child relationships, max 2 levels deep:
  ```
  GET /api/posts/:postId/comments       # OK: comments belong to a post
  GET /api/users/:id/orders/:id/items   # Too deep: use /api/orders/:id/items instead
  ```

### Query Parameters
- **Pagination**: `?page=1&limit=20` or cursor-based: `?after=cursor_abc&limit=20`
- **Filtering**: `?status=active&role=admin`
- **Sorting**: `?sort=-createdAt` (minus prefix for descending)
- **Field selection**: `?fields=id,name,email` (when payloads are large)

### Status Codes
| Code | Meaning | When to Use |
|------|---------|-------------|
| 200 | OK | Successful GET, PATCH, PUT, or DELETE returning a body |
| 201 | Created | Successful POST that created a resource (include `Location` header) |
| 204 | No Content | Successful operation returning no body (often DELETE) |
| 400 | Bad Request | Malformed request syntax (invalid JSON, missing required headers) |
| 401 | Unauthorized | Authentication missing or invalid (caller is anonymous) |
| 403 | Forbidden | Authenticated caller lacks permission for this action |
| 404 | Not Found | Resource does not exist (or caller shouldn't know it exists) |
| 409 | Conflict | State conflict (duplicate key, concurrent modification) |
| 422 | Unprocessable | Well-formed JSON but semantically invalid (validation failure) |
| 429 | Too Many Requests | Rate limit exceeded (include `Retry-After` header) |
| 500 | Internal Error | Server bug — never deliberately returned for client errors |

### Error Response Format
Always return structured errors, never plain strings:

```json
{
  "error": {
    "code": "VALIDATION_FAILED",
    "message": "The request body failed validation",
    "details": [
      {
        "field": "email",
        "issue": "INVALID_FORMAT",
        "message": "Must be a valid email address"
      }
    ]
  }
}
```

---

## Function and Module Boundary Conventions

### Keep Argument Counts Low
Functions with more than 3 arguments should take a configuration object:

```typescript
// Bad: Position-dependent, easy to swap arguments of same type
function createUser(name: string, email: string, role: string, sendEmail: boolean, tenantId: string) { ... }

// Good: Named properties, order-independent, self-documenting
interface CreateUserInput {
  name: string;
  email: string;
  role: Role;
  sendWelcomeEmail?: boolean; // Sensible default: true
  tenantId: string;
}
function createUser(input: CreateUserInput) { ... }
```

### Return Values: Explicit Over Implicit

```typescript
// Bad: null could mean "not found" or "error occurred"
function getTask(id: TaskId): Promise<Task | null> { ... }

// Good: Result type distinguishes "not found" from errors
type Result<T, E> = { ok: true; data: T } | { ok: false; error: E };

function getTask(id: TaskId): Promise<Result<Task, 'NOT_FOUND' | 'DATABASE_ERROR'>> { ... }
```

---

## Rationales to Challenge

| What you might hear | Why it's wrong / what to consider |
|---------------------|-----------------------------------|
| "We'll add validation later" | Unvalidated inputs become dependencies. Callers rely on permissive behavior. Validate from day one. |
| "Nobody uses that undocumented behavior" | Hyrum's Law: if it's observable, somebody depends on it. Treat every public behavior as a commitment. |
| "We can just maintain two versions" | Multiple versions multiply maintenance cost and create diamond dependency problems. Prefer the One-Version Rule. |
| "Internal APIs don't need contracts" | Internal consumers are still consumers. Contracts prevent coupling and enable parallel work. |
| "It's just a test helper on the production class" | Test backdoors leak into production, pollute binaries, and tempt production callers into breaking encapsulation. Use DI seams instead. |
| "We can make it `pub` so tests can see it" | Leaking visibility causes compiler warnings and exposes internal implementation details. Keep visibility aligned with the least visible type in the signature. |
| "Accepting the Idempotency-Key header is enough" | The header is the contract; storing the key against the result is the implementation. A key you accept but don't honour tells the client retrying is safe when it isn't. |
| "Our queue guarantees exactly-once delivery" | No queue does across a consumer crash — the broker's ack and your side effect are not in one transaction. Design for at-least-once with idempotent processing. |
| "Duplicate requests are rare" | They're *correlated*. Retries spike exactly when a dependency is degraded — the moment duplicates are most likely and most expensive. |

---

## Common Anti-Patterns

- Returning database rows directly from API handlers (leaks internal schema)
- Using the same type for create requests and response objects (IDs don't exist on create)
- `boolean` arguments that control function behavior (split into two functions instead)
- Breaking changes to existing fields (type changes, removals)
- List endpoints without pagination
- Verbs in REST URLs (`/api/createTask`, `/api/getUsers`)
- Test-only backdoor methods, conditional compilation flags (`#[cfg(test)]`, `#ifdef`), or test hooks embedded in production structs or classes
- Visibility mismatches (e.g. `pub` method exposing crate-private types in its parameter or return types)
- Newly introduced dependency injection seams with no active production caller (phantom seams)
- Third-party API responses used without validation or sanitization
- A `SELECT` for an idempotency key followed by an `INSERT` — that's a race, not a guard
- An idempotency key derived from a UUID, timestamp, or anything else regenerated per attempt

---

## Verification Checklist

After designing an API:
- [ ] Contract is defined before implementation begins
- [ ] Observable behavior is intentional (nothing accidental exposed)
- [ ] Illegal states are unrepresentable in the type system
- [ ] Error cases return structured responses with machine-readable codes
- [ ] List endpoints support pagination
- [ ] New fields are additive and optional (backward compatible)
- [ ] Naming follows consistent conventions across all endpoints
- [ ] Production interfaces are 100% pure (zero test-only backdoor methods, test hooks, or `#[cfg(test)]` shortcuts)
- [ ] Method visibility matches the least visible type in its signature (no visibility leaks or compiler warnings)
- [ ] Configurable DI seams are wired into live production callers (zero phantom seams)
- [ ] API documentation or types are committed alongside the implementation
- [ ] State-changing endpoints either honour an idempotency key or are documented as unsafe to retry
- [ ] The key is claimed in one atomic operation, guarded by a unique constraint
- [ ] The key cache stores the completed response, including headers and status code
- [ ] Retried requests return the cached response without re-executing side effects
- [ ] A concurrent retry while the first is in-flight returns `409 Conflict` (or waits), not a second execution
- [ ] Key reuse with mismatched parameters returns `422 Unprocessable Entity`
- [ ] Idempotency keys expire after a documented TTL (typically 24–72 hours)
