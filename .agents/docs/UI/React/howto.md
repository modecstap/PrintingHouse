# How to Apply React Rules

Steps for common React tasks. The rules behind them: [reference guide](reference.md).

## Load Data in a Component

1. Keep the request in one state value with a `status` field: `loading`, `error`, or `success`. See [Request States](reference.md#request-states).
2. Start the request in an effect, with its parameters in the dependency array.
3. Create an `AbortController` in the effect and pass its `signal` to the request.
4. Return a cleanup function that calls `controller.abort()`.
5. Ignore `AbortError`. Put any other error into state.
6. Render a separate branch for each status.
7. If the request function does not accept a `signal`, use an `ignore` flag instead of steps 3–5.
8. If several components need the same data, or the data must refresh, use a library instead. See [Decide on a Server-State Library](#decide-on-a-server-state-library).

```jsx
function Product({ id }) {
  const [state, setState] = useState({ status: 'loading' });

  useEffect(() => {
    const controller = new AbortController();
    setState({ status: 'loading' });

    fetchProduct(id, { signal: controller.signal })
      .then((data) => setState({ status: 'success', data }))
      .catch((error) => {
        if (error.name !== 'AbortError') setState({ status: 'error', error });
      });

    return () => controller.abort();
  }, [id]);

  if (state.status === 'loading') return <Spinner />;
  if (state.status === 'error') return <ErrorMessage error={state.error} />;
  return <ProductCard product={state.data} />;
}
```

With an `ignore` flag:

```jsx
useEffect(() => {
  let ignore = false;
  fetchProduct(id)
    .then((data) => {
      if (!ignore) setState({ status: 'success', data });
    })
    .catch((error) => {
      if (!ignore) setState({ status: 'error', error });
    });
  return () => {
    ignore = true;
  };
}, [id]);
```

## Replace an Effect with a Computed Value

Signs: an effect only reads props or state and calls a state setter with the result.

1. Delete the effect and the state variable it sets.
2. Compute the value in the component body.
3. If the computation is slow (measure it first), wrap it in `useMemo`.
4. If the effect resets state when a prop changes, use `key` instead. See [Reset Component State on Purpose](#reset-component-state-on-purpose).
5. If the effect runs code in response to a user action, move the code into the event handler.

```jsx
// before
const [visibleTodos, setVisibleTodos] = useState([]);
useEffect(() => {
  setVisibleTodos(todos.filter((todo) => todo.status === filter));
}, [todos, filter]);

// after
const visibleTodos = todos.filter((todo) => todo.status === filter);
```

## Subscribe to an External System

1. Put the subscription in `useEffect`.
2. Define handler functions inside the effect, so they do not become dependencies.
3. Return a cleanup function that removes exactly what the setup added.
4. Add every prop and state value used inside the effect to the dependency array.
5. In development, run the component in Strict Mode and check that only one subscription is active after mount.
6. If the component only reads a value from an external store, use `useSyncExternalStore` instead of steps 1–4.

```jsx
useEffect(() => {
  function handleOnline() {
    setIsOnline(true);
  }
  function handleOffline() {
    setIsOnline(false);
  }
  window.addEventListener('online', handleOnline);
  window.addEventListener('offline', handleOffline);
  return () => {
    window.removeEventListener('online', handleOnline);
    window.removeEventListener('offline', handleOffline);
  };
}, []);
```

## Build a Form

1. Choose the source of truth:
   * Validation only on submit: uncontrolled fields, read values with `FormData`.
   * Instant validation, dependent fields, or formatting while typing: controlled fields with state.
2. Write validation as a pure function `validate(values)` that returns `{ [field]: message }`.
3. In the submit handler, prevent the default action, read and validate the values, and store the errors. Stop if there are any.
4. Show each error next to its field. Link them with `aria-describedby` and set `aria-invalid`.
5. Disable the submit button while the request runs.
6. Send the request. Put server field errors into the same errors object. Show other server errors as a form-level error.
7. Keep server validation even if the client validates everything.

```jsx
function SubscribeForm() {
  const [errors, setErrors] = useState({});
  const [isSending, setIsSending] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();
    const values = Object.fromEntries(new FormData(event.currentTarget));
    const nextErrors = validate(values);
    setErrors(nextErrors);
    if (Object.keys(nextErrors).length > 0) return;

    setIsSending(true);
    try {
      await subscribe(values);
    } catch (error) {
      setErrors(error.fieldErrors ?? { form: 'Could not subscribe. Try again.' });
    } finally {
      setIsSending(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      <input
        name="email"
        type="email"
        aria-invalid={Boolean(errors.email)}
        aria-describedby="email-error"
      />
      {errors.email && <p id="email-error">{errors.email}</p>}
      {errors.form && <p role="alert">{errors.form}</p>}
      <button disabled={isSending}>Subscribe</button>
    </form>
  );
}
```

## Isolate Errors in a User Flow

1. Find the parts of the page that work independently: a page route, a widget, a sidebar.
2. Wrap each part in an Error Boundary. React has no built-in function component for this: use a class component or the `react-error-boundary` library.
3. Give each boundary a fallback that says what failed and offers a retry.
4. Report the error from the boundary.
5. In event handlers and async code, catch errors with `try`/`catch` and put them into state. An Error Boundary does not catch them.

```jsx
import { ErrorBoundary } from 'react-error-boundary';

<ErrorBoundary
  fallbackRender={({ resetErrorBoundary }) => <WidgetError onRetry={resetErrorBoundary} />}
  onError={reportError}
>
  <Recommendations />
</ErrorBoundary>
```

## Share Data Through Context

1. If data goes down only one or two levels, pass props or use `children`. Stop here.
2. Create a separate context for each independent piece of data: `UserContext`, `ThemeContext`, not `AppContext`.
3. Place the provider in the lowest common parent of the consumers.
4. Memoize an object or function value with `useMemo` or `useCallback`. Otherwise every provider render re-renders all consumers.
5. If many components read parts of large, often-changing data, use a state library with selectors instead.

```jsx
function CartProvider({ children }) {
  const [items, setItems] = useState([]);
  const value = useMemo(() => ({ items, setItems }), [items]);
  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
}
```

## Reset Component State on Purpose

1. Find the component whose state must reset when an entity changes: for example, a form that edits another user.
2. Pass the entity ID as `key` to this component.
3. Remove effects that reset the state manually.

```jsx
// before
function EditUserForm({ user }) {
  const [name, setName] = useState(user.name);
  useEffect(() => {
    setName(user.name);
  }, [user]);
  // ...
}

// after
<EditUserForm key={user.id} user={user} />
```

## Render User-Provided HTML

1. If plain text is enough, render it as `{text}` in JSX. Stop here.
2. If markup is needed, prefer a structured format: for example, Markdown rendered without raw HTML.
3. If you must insert HTML, sanitize it with a library such as DOMPurify right before insertion.
4. Put sanitization in one component and insert HTML only through it.
5. Allow only `http:` and `https:` in user-provided URLs.

```jsx
import DOMPurify from 'dompurify';

export function SafeHtml({ html }) {
  return <div dangerouslySetInnerHTML={{ __html: DOMPurify.sanitize(html) }} />;
}
```

```js
function toSafeUrl(url) {
  const { protocol } = new URL(url, window.location.origin);
  return protocol === 'http:' || protocol === 'https:' ? url : undefined;
}
```

## Model Request State in TypeScript

1. List the states the component can be in.
2. For each state, list the data that exists only in it.
3. Write a discriminated union with a `status` field. See [Mutually Exclusive States](reference.md#mutually-exclusive-states).
4. Replace boolean flags (`isLoading`, `isError`) with this union.
5. Narrow by `status` before reading state-specific fields.
6. Validate API data at runtime before putting it into the `success` state. See [Runtime Validation](reference.md#runtime-validation).

```tsx
type ProductState =
  | { status: 'loading' }
  | { status: 'error'; error: Error }
  | { status: 'success'; data: Product };

function ProductView({ state }: { state: ProductState }) {
  switch (state.status) {
    case 'loading':
      return <Spinner />;
    case 'error':
      return <ErrorMessage error={state.error} />;
    case 'success':
      return <ProductCard product={state.data} />;
  }
}
```

## Choose a Test Level

1. Pure logic (validation, formatting, calculations): write a unit test that calls the function.
2. A component or several interacting components: write an integration test with Testing Library. Render, act like the user with `userEvent`, check what is on screen.
3. A key user path across pages (sign-in, checkout): write an E2E test.
4. Do not repeat a check on every level. Cover validation edge cases in a unit test and one invalid case in an integration test.
5. Find elements by role and accessible name: `getByRole('button', { name: 'Save' })`. Use a test ID only when an element has no role or text.
6. Do not check internal state, hook calls, or component names.

## Decide on a Server-State Library

1. A library such as TanStack Query is needed if at least one is true:
   * Several components use the same data.
   * Data must refresh: on window focus, on an interval, or after a mutation.
   * A mutation must update or invalidate lists.
   * You need a cache between pages, pagination, or optimistic updates.
2. If none is true, load the data without a library. See [Load Data in a Component](#load-data-in-a-component). Stop here.
3. If the project already has a server-state library, use it.
4. Build query keys from the entity name and parameters: `['products', id]`.
5. After a mutation, invalidate the keys of the changed data. See [Server Data](reference.md#server-data).
