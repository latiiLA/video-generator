/** Turn API/FastAPI error payloads into a readable string. */
export function formatError(value: unknown, fallback = "Something went wrong"): string {
  if (value == null || value === "") return fallback;
  if (typeof value === "string") return value;
  if (value instanceof Error) return value.message || fallback;
  if (Array.isArray(value)) {
    return value.map((item) => formatError(item, "")).filter(Boolean).join("; ") || fallback;
  }
  if (typeof value === "object") {
    const obj = value as Record<string, unknown>;
    if (typeof obj.message === "string") return obj.message;
    if (typeof obj.error === "string") return obj.error;
    if (obj.detail != null) return formatError(obj.detail, fallback);
    if (typeof obj.msg === "string") {
      const loc = Array.isArray(obj.loc) ? obj.loc.join(".") : "";
      return loc ? `${loc}: ${obj.msg}` : obj.msg;
    }
    try {
      return JSON.stringify(value);
    } catch {
      return fallback;
    }
  }
  return String(value);
}
