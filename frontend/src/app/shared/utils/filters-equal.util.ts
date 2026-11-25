export function filtersEqual<T extends object>(a: T, b: T): boolean {
  if (a === b) {
    return true;
  }

  const keysA = Object.keys(a) as (keyof T)[];

  if (keysA.length !== Object.keys(b).length) {
    return false;
  }

  return keysA.every((key) => valueEqual(a[key], b[key]));
}

function valueEqual(a: unknown, b: unknown): boolean {
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((item, index) => item === b[index]);
  }

  return a === b;
}
