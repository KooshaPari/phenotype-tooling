# Modern Frontend Architecture Best Practices Reference

## 1. Component Architecture Patterns

### Atomic Design

Components organized hierarchically:
- **Atoms**: Basic units (buttons, inputs, labels)
- **Molecules**: Simple combinations (search box = input + button)
- **Organisms**: Complex components (header, card, form)
- **Templates**: Page layouts
- **Pages**: Specific instances

**Benefit**: Reusability, cognitive clarity, design system alignment

### Compound Components Pattern

Parent manages state, children consume via context:

```tsx
// Parent manages state
<Select>
  <Select.Trigger>Choose option</Select.Trigger>
  <Select.Content>
    <Select.Item value="1">Option 1</Select.Item>
    <Select.Item value="2">Option 2</Select.Item>
  </Select.Content>
</Select>
```

**Benefits**: Flexibility, no prop drilling, composable

---

## 2. State Management Strategy

### Hybrid Approach (2026 Standard)

| Layer | Tool | Purpose |
|-------|------|---------|
| **Server State** | React Query / TanStack Query | API caching, refetch, offline |
| **Local State** | useState | Component-level UI state |
| **Shared Client State** | Zustand / Jotai | Global app state (lightweight) |
| **UI State** | URL / Router | Navigation, filter state, search |

**Recommendation**: React Query + Zustand (minimal boilerplate, excellent DX)

### State Management Decision Tree

```
Do you need server data?
├─ Yes → React Query (handles caching, sync)
└─ No → Is it global? (needed by multiple pages)
    ├─ Yes → Zustand (simple) or Jotai (fine-grained)
    └─ No → useState (local to component)
```

---

## 3. Data Fetching Patterns

### React Query (TanStack Query)

```tsx
// Automatic refetch, caching, retries
const { data, isLoading, error } = useQuery({
  queryKey: ['users', userId],
  queryFn: () => api.getUser(userId),
  staleTime: 5 * 60 * 1000, // 5 min
});
```

**Handles**: Retries, background refetch, cache invalidation, DevTools

### SWR (Stale-While-Revalidate)

Lighter weight; uses stale data while fetching fresh:
```tsx
const { data } = useSWR('/api/users', fetcher);
```

### Apollo Client (GraphQL)

Full-featured for graph APIs:
```tsx
const { data, loading } = useQuery(GET_USER_QUERY);
```

---

## 4. Form Management

### React Hook Form (Winner, 2026)

```tsx
const { register, handleSubmit, errors } = useForm();

<input {...register("email", {
  required: "Email required",
  pattern: { value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i }
})} />
```

**Advantages**: <8KB, minimal re-renders, uncontrolled components

**Why not Formik**: Unmaintained (12+ months no commits), heavier bundle

---

## 5. Routing Architecture

| Framework | Paradigm | Best For |
|-----------|----------|----------|
| **Next.js** | App Router (RSC-first) | Full-stack, Vercel-optimized |
| **TanStack Router** | Type-safe, loaders | Type safety first, complex params |
| **React Router v7** | Web standards | Progressive enhancement, accessibility |

### App Routers (2026 Default)

Routing now handles data fetching + rendering automatically:

```tsx
// Next.js App Router
export default async function Page({ params }) {
  const data = await fetch(`/api/users/${params.id}`);
  return <UserProfile user={data} />;
}
```

**Benefits**: SSR + streaming, no loading states, type-safe routes

---

## 6. Performance Optimization

### Code Splitting

```tsx
// Route-based splitting (automatic in Next.js/Remix)
const AdminPage = lazy(() => import('./pages/Admin'));

// Dynamic imports
const HeavyChart = lazy(() => import('./charts/CanvasChart'));
```

### Lazy Loading

```tsx
// Images with IntersectionObserver
<img loading="lazy" src="..." />

// Components
<Suspense fallback={<Spinner />}>
  <HeavyComponent />
</Suspense>
```

### Memoization

```tsx
// Memoize expensive computations
const memoizedData = useMemo(() =>
  complexCalculation(data), [data]);

// Prevent unnecessary renders
const MemoButton = React.memo(Button);
```

---

## 7. React Server Components (RSC)

### Use Server Components For

- Static content (no state needed)
- Database queries (direct access, no API layer)
- Authentication checks (secrets secure)
- Streaming UI (progressive rendering)

### Use Client Components For

- Interactivity (onClick, onChange, hooks)
- Real-time data (WebSocket subscriptions)
- Forms
- Local state management

```tsx
// Server Component (automatic)
export default async function Page() {
  const users = await db.query("SELECT * FROM users");
  return <UserList users={users} />;
}

// Client Component (opt-in)
'use client'
export default function SearchBox() {
  const [query, setQuery] = useState('');
  return <input onChange={(e) => setQuery(e.target.value)} />;
}
```

---

## 8. Design System & Token-Driven Design

### Figma Variables + Token Export (2026 Standard)

**Collections**:
- Base: colors, spacing, typography
- Aliases: buttons, headings, semantic
- Typography: font families, weights, sizes

**Token-to-Component Mapping**:

```tsx
// buttons.tsx
const buttonStyles = {
  primary: {
    backgroundColor: tokens.colors.semantic.primary,
    color: tokens.colors.semantic.primary_text,
    padding: `${tokens.spacing.m} ${tokens.spacing.lg}`,
    fontSize: tokens.typography.button.size,
  }
};
```

**Export**: Figma → Tailwind config, CSS variables, JSON

---

## 9. Testing Strategy (Multi-Layer)

### Pyramid Targets

- Unit: 70% (isolated function tests)
- Integration: 20% (multi-component flows + API mocking)
- E2E: 10% (critical user journeys)

### Tools by Layer

| Layer | Tool | Speed |
|-------|------|-------|
| Unit | Vitest | 10-20× faster than Jest |
| Component | Vitest + React Testing Library | Fast |
| Integration | Supertest + MSW | Medium |
| E2E | Playwright | Slow |

### CI Strategy

- Fast job: Vitest + RTL + MSW (must pass)
- Slow job: Playwright (only if fast passes)

---

## 10. Framework Comparison (2026)

| Criterion | React | Vue | Svelte | Solid |
|-----------|-------|-----|--------|-------|
| Performance | Good (RSC helps) | Good | Best | Best |
| Bundle Size | Largest | Medium | Smallest | Small |
| Ecosystem | Massive | Good | Growing | Minimal |
| Job Market | Dominant | Growing | Niche | Emerging |
| Learning Curve | Moderate | Gentle | Moderate | Moderate |

**Recommendation**: React (jobs + ecosystem), Vue (balance), Svelte (performance)

---

## 11. Emerging Trends (2026)

1. **App Routers**: Data fetching + routing unified (default now)
2. **TypeScript Everywhere**: End-to-end type safety (tRPC, OpenAPI)
3. **Fine-Grained Reactivity**: Signals replacing VDOM (SolidJS, Vue Vapor)
4. **Micro-Frontends**: Module federation for large teams
5. **AI-Driven UI**: Generative UIs + AI understanding of design tokens

---

## 12. Production Readiness Checklist

- [ ] Code splitting enabled (route-based minimum)
- [ ] Lazy loading for images (loading="lazy")
- [ ] Memoization tuned (no over-memoization)
- [ ] Performance metrics tracked (FCP, LCP, CLS)
- [ ] Testing strategy in place (unit + integration + E2E)
- [ ] Design tokens exported from Figma
- [ ] Accessibility tested (axe DevTools, keyboard nav)
- [ ] Dark mode support (CSS custom properties or tailwind)
- [ ] SEO optimized (meta tags, structured data)
- [ ] Error boundaries configured

---

## References

- React Docs: https://react.dev
- Vue Docs: https://vuejs.org
- TanStack Query: https://tanstack.com/query
- React Hook Form: https://react-hook-form.com
- Playwright: https://playwright.dev
- Figma Tokens: https://tokens.studio
