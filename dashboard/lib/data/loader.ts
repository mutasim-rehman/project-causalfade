import { z } from "zod";

const cache = new Map<string, Promise<unknown>>();

export async function loadDataset<T>(
  path: string,
  schema?: z.ZodType<T>
): Promise<T> {
  let request = cache.get(path);
  if (!request) {
    request = fetch(path).then((response) => {
      if (!response.ok) throw new Error(`Failed to fetch dataset ${path}: ${response.status}`);
      return response.json();
    }).catch((error) => {
      cache.delete(path);
      throw error;
    });
    cache.set(path, request);
  }
  const raw = await request;
  return schema ? schema.parse(raw) : (raw as T);
}
