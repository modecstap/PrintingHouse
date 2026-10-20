# Reference Guide: React Rules

Rules for React components, mandatory for new code. How to apply them: [instructions](howto.md).

## State

### Minimal State

Store only state that cannot be computed from props or other state. Compute derived values during rendering.

**Why:** No duplicated data to get out of sync.

**Exceptions:** Store a copy when it is a snapshot (for example, a form's initial value) or has a lifecycle independent of its source.

Bad:

```jsx
const [items, setItems] = useState([]);
const [selectedItem, setSelectedItem] = useState(null); // stale copy after items change
```

Good:

```jsx
const [items, setItems] = useState([]);
const [selectedId, setSelectedId] = useState(null);
const selectedItem = items.find((item) => item.id === selectedId);
```

### Immutability

Do not mutate objects and arrays in state. Create new ones.

**Why:** React compares state by reference: a mutated object keeps its reference, so React may skip the render, and memoization breaks.

**Exceptions:** Mutating a local object not yet in state is fine. Immer allows mutation-style code with an immutable result.

Bad:

```jsx
function addItem(item) {
  items.push(item);
  setItems(items);
}
```

Good:

```jsx
function addItem(item) {
  setItems((prev) => [...prev, item]);
}
```

### Context

Do not put all state into Context. Keep each context small and its provider as close to its consumers as possible.

**Why:** A context value change re-renders every consumer of that context.

**Exceptions:** Context fits theme, locale, the current user, and dependencies such as API clients. Large, often-changing data fits a dedicated state library better.

Bad:

```jsx
<AppContext.Provider value={{ user, theme, cart, setCart }}>
  {children}
</AppContext.Provider>
```

Good:

```jsx
<UserContext.Provider value={user}>
  <ThemeContext.Provider value={theme}>
    {children}
  </ThemeContext.Provider>
</UserContext.Provider>
```

### Server Data

Treat server data as a cache: decide when it goes stale, when to refetch it, and what to invalidate after a mutation.

**Why:** Fewer requests and no outdated data on screen.

**Exceptions:** Complex server state fits TanStack Query or a similar library. A simple one-off request needs no library.

Bad:

```jsx
async function rename(id, title) {
  await renameProduct(id, title);
  // the product list still shows the old title
}
```

Good:

```jsx
const queryClient = useQueryClient();
const { mutate: rename } = useMutation({
  mutationFn: ({ id, title }) => renameProduct(id, title),
  onSuccess: () => queryClient.invalidateQueries({ queryKey: ['products'] }),
});
```

## Hooks and Effects

### Rules of Hooks

Call hooks only at the top level of a component or custom hook, in the same order on every render.

**Why:** React matches state to hooks by call order.

**Exceptions:** Only `use` can be called inside conditions and loops.

Bad:

```jsx
function Profile({ userId }) {
  if (!userId) return null;
  const [user, setUser] = useState(null);
  // ...
}
```

Good:

```jsx
function Profile({ userId }) {
  const [user, setUser] = useState(null);
  if (!userId) return null;
  // ...
}
```

### Effects

Use `useEffect` to synchronize with external systems, not to compute derived state or respond to user events.

**Why:** Fewer extra renders, no update loops, no hidden dependencies.

**Exceptions:** Effects fit subscriptions, timers, DOM integrations, and external APIs. Cleanup undoes what setup started: unsubscribe, clear the timer, close the connection.

Bad:

```jsx
useEffect(() => {
  if (submitted) sendForm(form);
}, [submitted]);
```

Good:

```jsx
function handleSubmit() {
  sendForm(form);
}
```

Good:

```jsx
useEffect(() => {
  const connection = createConnection(roomId);
  connection.connect();
  return () => connection.disconnect();
}, [roomId]);
```

### Refs and DOM

Use `ref` for DOM access and for values that must not trigger a render: timer IDs, third-party library instances.

**Why:** Displayed state stays separate from imperative operations.

**Exceptions:** If the UI shows the value, use state. Direct DOM manipulation is fine for focus, measurements, and third-party library integration.

Bad:

```jsx
const clicks = useRef(0);
return <button onClick={() => clicks.current++}>Clicked {clicks.current}</button>;
```

Good:

```jsx
const [clicks, setClicks] = useState(0);
return <button onClick={() => setClicks((c) => c + 1)}>Clicked {clicks}</button>;
```

Good:

```jsx
const inputRef = useRef(null);

function handleEdit() {
  inputRef.current.focus();
}

return <input ref={inputRef} />;
```

### Repeated Rendering and Effects

Components and effects must tolerate repeated calls without incorrect side effects: setup, cleanup, and setup again must equal one setup.

**Why:** React may render more than once and checks effects by running them twice, including in Strict Mode.

**Exceptions:** Behavior varies by React version and mode. Never rely on a single render or effect call where React does not guarantee it. Run one-time application setup at module level.

Bad:

```jsx
useEffect(() => {
  analytics.init(); // runs twice in Strict Mode
  window.addEventListener('resize', handleResize); // never removed
}, []);
```

Good:

```jsx
useEffect(() => {
  function handleResize() {
    setWidth(window.innerWidth);
  }
  window.addEventListener('resize', handleResize);
  return () => window.removeEventListener('resize', handleResize);
}, []);
```

## Async Operations

### Request States

Handle loading, success, and error states explicitly, and show each in the UI.

**Why:** No blank screen, no endless spinner, no lost errors.

Bad:

```jsx
const [data, setData] = useState(null);

useEffect(() => {
  fetchProduct(id).then(setData);
}, [id]);

if (!data) return <Spinner />; // spins forever if the request fails
```

Good:

```jsx
if (state.status === 'loading') return <Spinner />;
if (state.status === 'error') return <ErrorMessage error={state.error} />;
return <ProductCard product={state.data} />;
```

Full example: [Load Data in a Component](howto.md#load-data-in-a-component).

### Cancellation and Stale Results

Cancel or ignore a request whose result is no longer needed: its parameters changed or the component unmounted.

**Why:** No race where an older response overwrites a newer one, no UI updates from outdated data.

**Exceptions:** Not every request needs cancellation. Cancelling a mutation on the client may not stop it on the server: it may still succeed.

Bad:

```jsx
useEffect(() => {
  fetchResults(query).then(setResults); // an old query may resolve last
}, [query]);
```

Good:

```jsx
useEffect(() => {
  const controller = new AbortController();
  fetchResults(query, { signal: controller.signal })
    .then(setResults)
    .catch((error) => {
      if (error.name !== 'AbortError') setError(error);
    });
  return () => controller.abort();
}, [query]);
```

## Components

### Composition

Prefer composition through `children`, props, and small components over one over-generalized component.

**Why:** Fewer conditional branches and interdependent props.

**Exceptions:** A generalized component is justified when behavior or structure repeats, or real variation appears.

Bad:

```jsx
<Card
  title="Order"
  showIcon
  iconType="cart"
  showFooter
  footerButtonText="Pay"
  onFooterButtonClick={pay}
/>
```

Good:

```jsx
<Card>
  <CardHeader icon={<CartIcon />}>Order</CardHeader>
  <CardFooter>
    <Button onClick={pay}>Pay</Button>
  </CardFooter>
</Card>
```

### Explicit Dependencies

Make dependencies and state transitions explicit. Avoid hidden side effects.

**Why:** Code is easier to analyze, debug, and change.

**Exceptions:** Do not split simple logic into many functions and abstractions just to satisfy the rule.

Bad:

```jsx
function formatPrice(price) {
  analytics.track('price_shown'); // hidden side effect
  return `${price.toFixed(2)} ${window.currency}`; // hidden dependency
}
```

Good:

```jsx
function formatPrice(price, currency) {
  return `${price.toFixed(2)} ${currency}`;
}
```

### Anti-Patterns

Avoid these constructs: they cause extra renders, unexpected state resets, and complex logic.

**Syncing state through an effect.** Compute the value instead: see [Replace an Effect with a Computed Value](howto.md#replace-an-effect-with-a-computed-value).

**Unstable `key`.** Use a stable ID from the data. An index is acceptable only for a static list that is never reordered, filtered, or edited. Changing `key` to reset state on purpose is fine: see [Reset Component State on Purpose](howto.md#reset-component-state-on-purpose).

Bad:

```jsx
{items.map((item) => <Row key={Math.random()} item={item} />)}
```

Good:

```jsx
{items.map((item) => <Row key={item.id} item={item} />)}
```

**A component defined inside another component.** Each render creates a new component type, so React remounts it and loses its state and focus. Define it at module level. A nested function returning JSX is fine when called as a function, `{renderRow(item)}`, not rendered as a component, `<Row />`.

Bad:

```jsx
function ProductList({ products }) {
  function Row({ product }) {
    return <li>{product.title}</li>;
  }
  return <ul>{products.map((p) => <Row key={p.id} product={p} />)}</ul>;
}
```

**Redundant state.** See [Minimal State](#minimal-state).

## Forms

Give each field one source of truth: React state (controlled field) or the DOM (uncontrolled field). Keep validation, error display, and submission separate.

**Why:** Predictable behavior and clear feedback to the user.

**Exceptions:** Controlled fields suit complex interactivity: instant validation, dependent fields, formatting while typing. Uncontrolled fields are simpler for ordinary forms. Always validate on the server too.

Bad:

```jsx
async function handleSubmit(event) {
  event.preventDefault();
  if (!email.includes('@')) {
    alert('Invalid email'); // validation, display, and submission in one place
    return;
  }
  await subscribe(email);
}
```

Good:

```jsx
function validate(values) {
  const errors = {};
  if (!values.email.includes('@')) errors.email = 'Enter a valid email';
  return errors;
}
```

```jsx
<input name="email" aria-invalid={Boolean(errors.email)} aria-describedby="email-error" />
{errors.email && <p id="email-error">{errors.email}</p>}
```

Full example: [Build a Form](howto.md#build-a-form).

## Error Handling

Handle errors at user-flow boundaries.

**Why:** One error must not break the rest of the working UI.

**Exceptions:** An Error Boundary catches errors thrown while rendering its children. Errors in event handlers, promises, and server requests need their own handling.

Bad:

```jsx
<ErrorBoundary fallback={<SaveError />}>
  <button onClick={() => saveOrder(order)}>Save</button> {/* rejected promise is not caught */}
</ErrorBoundary>
```

Good:

```jsx
async function handleSave() {
  try {
    await saveOrder(order);
  } catch (error) {
    setSaveError(error);
  }
}
```

Good:

```jsx
<Page>
  <ErrorBoundary fallback={<WidgetError />}>
    <Recommendations />
  </ErrorBoundary>
  <Cart />
</Page>
```

## Security

Do not trust user data. Avoid unsafe HTML insertion. In user-provided URLs, allow only `http:` and `https:`.

**Why:** Prevents XSS and execution of untrusted code.

**Exceptions:** JSX escapes text values. `dangerouslySetInnerHTML` requires reliable HTML sanitization.

Bad:

```jsx
<div dangerouslySetInnerHTML={{ __html: comment.body }} />
```

Good:

```jsx
<p>{comment.body}</p>
```

Good, when markup is required:

```jsx
<div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(comment.html) }} />
```

Full example: [Render User-Provided HTML](howto.md#render-user-provided-html).

## Testing

Test observable behavior and critical scenarios first: what the user sees and does.

**Why:** Tests catch regressions without coupling to the implementation.

**Exceptions:** Unit tests suit pure logic, integration tests suit interactions, E2E tests suit key user paths. Not everything needs a test on every level: see [Choose a Test Level](howto.md#choose-a-test-level).

Bad:

```jsx
const setOpen = jest.fn();
jest.spyOn(React, 'useState').mockReturnValue([false, setOpen]);
render(<Menu />);
fireEvent.click(screen.getByText('Menu'));
expect(setOpen).toHaveBeenCalledWith(true);
```

Good:

```jsx
const user = userEvent.setup();
render(<Menu />);
await user.click(screen.getByRole('button', { name: 'Menu' }));
expect(screen.getByRole('menu')).toBeVisible();
```

## TypeScript

### Component Contracts

Type public contracts: props of exported components and arguments of exported hooks.

**Why:** Errors surface before runtime, and the type shows valid usage.

**Exceptions:** Do not complicate types to cover every theoretical case. Let TypeScript infer local types.

Bad:

```tsx
export function Button(props: any) {
  // ...
}
```

Good:

```tsx
type ButtonProps = {
  variant?: 'primary' | 'secondary';
  onClick: () => void;
  children: React.ReactNode;
};

export function Button({ variant = 'primary', onClick, children }: ButtonProps) {
  // ...
}
```

### Mutually Exclusive States

Model mutually exclusive states as a discriminated union, not independent flags.

**Why:** Impossible combinations, such as loading and error at once, do not compile.

Bad:

```tsx
type ProductState = {
  isLoading: boolean;
  error?: Error;
  data?: Product;
};
```

Good:

```tsx
type ProductState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: Product };
```

### Runtime Validation

Types do not check data at runtime. Validate external input at runtime: API responses, `localStorage`, URL parameters, messages.

**Why:** A type assertion on unchecked data hides the error until the data is used.

Bad:

```tsx
const product = (await response.json()) as Product;
```

Good:

```tsx
function toProduct(raw: unknown): Product {
  // check each field, throw an Error if a check fails
}

const product = toProduct(await response.json());
```
