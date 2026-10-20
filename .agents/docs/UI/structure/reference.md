# Reference Guide: web-ui Structure

The target structure of `src/`. The rules are mandatory for new code. How to achieve it: [instructions](howto.md).

## `src/` Layout

```text
src/
├── components/
│   ├── <domain>/       # business component: product, checkout-flow, ...
│   └── generic/        # UI without business logic
├── lib/                # utilities and wrappers over third-party libraries
└── test-utils/         # shared test helpers
```

| Directory                | Contents                                                     |
| ------------------------ | ------------------------------------------------------------ |
| `components/<domain>/`   | A business component and everything that belongs only to it  |
| `components/generic/`    | Reusable UI that knows nothing about the business domain     |
| `lib/`                   | Utilities and the only entry point to third-party libraries  |
| `test-utils/`            | Test setup used by more than one test                        |

## Component

A significant component lives in its own directory. Helper components, the test, and styles lie next to it, without subdirectories:

```text
components/product/
├── product.jsx
├── product.module.css
├── product.test.jsx
└── product-price.jsx
```

A component that has grown or mixes unrelated logic is split into subdirectories:

| Subdirectory  | Contents                                                                   |
| ------------- | -------------------------------------------------------------------------- |
| `api/`        | Calls to the backend and third-party services, hidden behind functions     |
| `models/`     | Data models of the component: validation and transformation                |
| `handlers/`   | Component logic: reactions to input, clicks, and other events              |
| `components/` | React subcomponents                                                        |

```text
components/product/
├── api/
├── models/
├── handlers/
├── components/
│   └── product-price.jsx
├── product.jsx
├── product.module.css
└── product.test.jsx
```

Only the subdirectories that have contents exist.

Bad:

```text
components/product/
├── api/            # empty
├── models/         # empty
├── handlers/       # empty
├── components/     # empty
└── product.jsx
```

Good:

```text
components/product/
├── product.jsx
└── product.test.jsx
```

## Generic Components

UI without business logic (buttons, tables, input fields, modal windows) lives in `components/generic/<name>/`. A generic component receives everything through props and does not call the API or use domain models.

Bad:

```text
components/generic/
└── product-card/       # knows about products: belongs to a domain
```

Good:

```text
components/generic/
├── button/
├── card/
└── modal/
components/product/
└── product-card.jsx    # uses generic/card
```

## `lib/`

All utilities live in `lib/` as a flat list of modules. Each module is named after its purpose. `lib/` is not divided into `utils`, `helpers`, or `services`.

Bad:

```text
lib/
├── utils/
│   └── helpers.js      # dates, prices, and validation together
└── services/
    └── sentry.js
```

Good:

```text
lib/
├── date.js
├── error-reporting.js
├── format-price.js
└── validation.js
```

## Third-Party Libraries

A third-party library is imported in exactly one `lib/` module. The rest of the code calls the API of that module.

```js
// lib/error-reporting.js
import * as Sentry from '@sentry/react';

export function reportError(error) {
  Sentry.captureException(error);
}
```

Bad:

```js
// components/checkout-flow/checkout-flow.jsx
import * as Sentry from '@sentry/react';

Sentry.captureException(error);
```

Good:

```js
// components/checkout-flow/checkout-flow.jsx
import { reportError } from '../../lib/error-reporting';

reportError(error);
```

## Data Contracts

PropTypes are not used: React 19 ignores them. Data from the API is validated in `models/` when it is received. A component receives an already validated model.

```js
// components/product/models/product.js
export function toProduct(raw) {
  if (typeof raw?.id !== 'number') throw new Error('product: id must be a number');
  if (typeof raw?.title !== 'string') throw new Error('product: title must be a string');
  return { id: raw.id, title: raw.title };
}
```

```js
// components/product/api/product.js
import { toProduct } from '../models/product';

export async function fetchProduct(id) {
  const response = await fetch(`/api/products/${id}`);
  return toProduct(await response.json());
}
```

Bad:

```jsx
// components/product/product.jsx
function Product({ raw }) {
  if (typeof raw?.title !== 'string') return null;
  return <h1>{raw.title}</h1>;
}
```

Good:

```jsx
// components/product/product.jsx
function Product({ product }) {
  return <h1>{product.title}</h1>;
}
```

## Tests

* A test lies next to the code it tests: `auth.js` and `auth.test.js`.
* Environment setup repeated in several tests lives in `test-utils/`.

```jsx
// test-utils/render-with-auth.jsx
import { render } from '@testing-library/react';
import { UserAuth } from '../components/auth/auth';

export function renderWithAuth(ui, user) {
  return render(<UserAuth.Provider value={user}>{ui}</UserAuth.Provider>);
}
```

```jsx
renderWithAuth(<ComponentUnderTest />, { name: 'Jack', userId: 1 });
```

Bad:

```text
src/
├── __tests__/
│   └── product.test.jsx
└── components/product/
    └── product.jsx
```

Good:

```text
components/product/
├── product.jsx
└── product.test.jsx
```

## Dependencies

A new library is added only if Hooks and the Context API do not solve the task. Redux and similar libraries are acceptable when there is a real need.

## Naming

* Files and directories use kebab-case: `format-price.js`, `checkout-flow/`.
* The main file of a component is named after its directory: `product/product.jsx`.
* Tests use the `.test` suffix: `product.test.jsx`.
* Styles use CSS modules: `product.module.css`.

| Bad                          | Good                         |
| ---------------------------- | ---------------------------- |
| `FormatPrice.js`             | `format-price.js`            |
| `checkoutFlow/`              | `checkout-flow/`             |
| `product/index.jsx`          | `product/product.jsx`        |
| `product.spec.jsx`           | `product.test.jsx`           |
| `product.css`                | `product.module.css`         |
