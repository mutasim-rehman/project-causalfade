import { z } from "zod";

const cache = new Map<string, unknown>();

export async function loadDataset<T>(
  path: string,
  schema?: z.ZodType<T>
): Promise<T> {
  if (cache.has(path)) {
    return cache.get(path) as T;
  }
  const res = await fetch(path);
  if (!res.ok) {
    throw new Error(`Failed to fetch dataset ${path}: ${res.status}`);
  }
  const raw = await res.json();
  const parsed = schema ? schema.parse(raw) : (raw as T);
  cache.set(path, parsed);
  return parsed;
}
